import logging
import os
from typing import Any, Dict, List

import requests

from app.rag.retriever import retrieve_chunks
from app.rag.claim_extractor import ClaimExtractor
from app.rag.evidence_matching import EvidenceMatcher

# ------------------------
# OLLAMA CONFIG
# ------------------------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT_SEC = float(os.getenv("OLLAMA_TIMEOUT_SEC", "60"))

MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "20"))

logger = logging.getLogger(__name__)

# ------------------------
# LLM CALL
# ------------------------
def call_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=OLLAMA_TIMEOUT_SEC
    )
    response.raise_for_status()
    data = response.json()

    if "response" not in data:
        raise ValueError("OLLAMA response missing 'response' field")

    return data["response"].strip()

# ------------------------
# INITIALIZE AUDIT COMPONENTS
# ------------------------
claim_extractor = ClaimExtractor()
evidence_matcher = EvidenceMatcher()

# ------------------------
# HELPERS
# ------------------------
def _safe_chunk_text(chunk: Dict[str, Any]) -> str:
    chunk_id = chunk.get("chunk_id", "unknown")
    text = chunk.get("text", "")
    return f"[{chunk_id}] {text}"

def _limit_context(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    limited = []
    total = 0

    for chunk in chunks[:MAX_CHUNKS]:
        text = chunk.get("text", "")
        if not isinstance(text, str):
            continue

        if total + len(text) > MAX_CONTEXT_CHARS:
            break

        limited.append(chunk)
        total += len(text)

    return limited

# ------------------------
# MAIN ENTRY POINT
# ------------------------
def answer_query(query: str) -> Dict[str, Any]:
    # 🔹 RETRIEVAL
    retrieved_chunks = retrieve_chunks(query)

    if not retrieved_chunks:
        return {
            "query": query,
            "answer": "I don't know",
            "claims": [],
            "claim_evaluations": [],
            "retrieved_chunks": [],
            "sources": []
        }

    retrieved_chunks = _limit_context(retrieved_chunks)

    context = "\n\n".join(
        _safe_chunk_text(c) for c in retrieved_chunks
    )

    prompt = f"""
Answer the question ONLY using the context below.
If the answer is not explicitly stated, say "I don't know".

Context:
{context}

Question:
{query}
"""

    # 🔹 LLM CALL
    try:
        answer = call_ollama(prompt)
    except Exception as e:
        logger.exception("LLM call failed")
        return {
            "query": query,
            "answer": "I don't know",
            "error": f"LLM unavailable: {str(e)}",
            "claims": [],
            "claim_evaluations": [],
            "retrieved_chunks": retrieved_chunks,
            "sources": list({
                (c.get("metadata") or {}).get("file_name", "unknown")
                for c in retrieved_chunks
            })
        }

    # 🔹 CLAIM EXTRACTION
    claims = claim_extractor.extract(answer)

    # 🔹 EVIDENCE MATCHING
    claim_evaluations = [
        evidence_matcher.match(claim, retrieved_chunks)
        for claim in claims
    ]

    return {
        "query": query,
        "answer": answer,
        "claims": claims,
        "claim_evaluations": claim_evaluations,
        "retrieved_chunks": retrieved_chunks,
        "sources": list({
            (c.get("metadata") or {}).get("file_name", "unknown")
            for c in retrieved_chunks
        })
    }
