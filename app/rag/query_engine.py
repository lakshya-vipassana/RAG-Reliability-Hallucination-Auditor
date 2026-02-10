import requests
from app.rag.retriever import retrieve
from app.rag.claim_extractor import ClaimExtractor
from app.rag.evidence_matcher import EvidenceMatcher


def call_ollama(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()["response"]


claim_extractor = ClaimExtractor()
evidence_matcher = EvidenceMatcher()


def answer_query(query: str):
    retrieved_chunks = retrieve(query)

    if not retrieved_chunks:
        return {
            "query": query,
            "answer": "I don't know",
            "claims": [],
            "claim_evaluations": [],
            "retrieved_chunks": [],
            "sources": []
        }

    context = "\n\n".join(
        f"[{c['chunk_id']}]: {c['text']}" for c in retrieved_chunks
    )

    prompt = f"""
Answer the question ONLY using the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{query}
"""

    try:
        answer = call_ollama(prompt)
    except Exception as e:
        answer = f"LLM unavailable. Error: {str(e)}"

    # 🔹 PHASE 4 — CLAIM EXTRACTION
    claims = claim_extractor.extract(answer)

    # 🔹 PHASE 5 — EVIDENCE MATCHING
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
            c["metadata"].get("file_name", "unknown")
            for c in retrieved_chunks
        })
    }
