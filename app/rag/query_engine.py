# app/rag/query_engine.py
import logging
import os
from typing import Any, Dict, List
import requests

from app.rag.retriever import retrieve_chunks
from app.rag.claim_extractor import ClaimExtractor
from app.rag.evidence_matching import EvidenceMatcher
from app.rag.metrics import compute_metrics

# OLLAMA CONFIG
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT_SEC = float(os.getenv("OLLAMA_TIMEOUT_SEC", "60"))

MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "20"))

logger = logging.getLogger(__name__)
claim_extractor = ClaimExtractor()
evidence_matcher = EvidenceMatcher()

def call_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=OLLAMA_TIMEOUT_SEC
    )
    response.raise_for_status()
    data = response.json()
    if "response" not in data:
        raise ValueError("OLLAMA response missing 'response' field")
    return data["response"].strip()

def _safe_chunk_text(chunk: Dict[str, Any]) -> str:
    chunk_id = chunk.get("chunk_id", "unknown")
    text = chunk.get("text", "")
    return f"[{chunk_id}] {text}"

def _convert_to_evidence_objects(claim_evaluations: List[Dict]) -> List[Dict]:
    status_mapping = {
        "Supported": "supported",
        "Weakly supported": "weak",
        "Unsupported": "unsupported",
        "Contradicted": "contradicted",
    }

    evidence_objects = []

    for c in claim_evaluations:
        evidence_objects.append({
            "claim_id": c["claim_id"],
            "chunk_ids": c.get("evidence", []),
            "support_level": status_mapping.get(c["status"], "unsupported"),
            "rationale": c.get("rationale", ""),
            "confidence": float(c.get("confidence", 0.0)),
        })

    return evidence_objects


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

def answer_query(query: str, answer: str) -> Dict[str, Any]:
    # 1️⃣ Retrieve relevant chunks
    retrieved_chunks = retrieve_chunks(query)

    if not retrieved_chunks:
        return {
            "query": query,
            "answer": answer,
            "claims": [],
            "claim_evaluations": [],
            "retrieved_chunks": [],
            "sources": [],
        }

    retrieved_chunks = _limit_context(retrieved_chunks)

    # 2️⃣ Extract claims from USER-PROVIDED answer
    claim_data = claim_extractor.extract(answer)
    claims = claim_data.get("claims", [])

    # 3️⃣ Match evidence
    claim_evaluations = []
    for claim in claims:
        eval_res = evidence_matcher.match(claim, retrieved_chunks)
        claim_evaluations.append(eval_res)

    # 4️⃣ Compute metrics
    metrics = compute_metrics(claim_evaluations)

    hallucination_rate = metrics.get("hallucination_rate")
    faithfulness = metrics.get("faithfulness")

    evidence_objects = _convert_to_evidence_objects(claim_evaluations)

    # 5️⃣ Verdict logic
    if not claim_evaluations:
        verdict = "UNSAFE"
    elif hallucination_rate is not None and hallucination_rate > 0.5:
        verdict = "UNSAFE"
    elif faithfulness is not None and faithfulness < 0.7:
        verdict = "PARTIALLY_SUPPORTED"
    else:
        verdict = "SAFE"

    return {
        "query": query,
        "answer": answer,
        "claims": claims,
        "claim_evaluations": claim_evaluations,
        "evidence": evidence_objects,
        "metrics": metrics,
        "verdict": verdict,
        "retrieved_chunks": retrieved_chunks,
        "sources": list({(c.get("metadata") or {}).get("file_name", "unknown") for c in retrieved_chunks}),
    }
