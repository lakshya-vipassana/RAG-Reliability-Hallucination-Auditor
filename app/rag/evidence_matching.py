# app/rag/evidence_matching.py

import json
import requests
import re
from typing import List, Dict

EVIDENCE_MATCH_PROMPT = """
You are an evidence verification system.

Task:
Given a claim and a set of retrieved document chunks, determine whether the 
claim is supported.

Rules:
- Use ONLY the provided chunks.
- Do NOT use outside knowledge.
- Be conservative.
- If evidence is partial, mark as Weakly supported.
- If evidence contradicts the claim, mark as Contradicted.
- If no chunk addresses the claim, mark as Unsupported.

Output JSON ONLY in this schema:
{{
  "status": "Supported | Weakly supported | Unsupported | Contradicted",
  "confidence": 0.0-1.0,
  "evidence": ["chunk_id"],
  "rationale": "One sentence explanation"
}}

Claim:
{claim}

Chunks:
{chunks}
"""


class EvidenceMatcher:
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model

    def _call_llm(self, prompt: str) -> str:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"]

    def _extract_json(self, text: str) -> Dict:
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Remove markdown fences
        text = re.sub(r"```json|```", "", text)

        # Extract JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON found in LLM output")

        cleaned = text[start:end+1]
        return json.loads(cleaned)

    def _candidate_chunks(self, claim: str, chunks: List[Dict], top_k: int = 5):
        claim_tokens = set(re.findall(r"\w+", claim.lower()))
        scored = []

        for c in chunks:
            chunk_tokens = set(re.findall(r"\w+", c["text"].lower()))
            overlap = len(claim_tokens & chunk_tokens)
            if overlap > 0:
                scored.append((overlap, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [c for _, c in scored[:top_k]]

    def match(self, claim: Dict, retrieved_chunks: List[Dict]) -> Dict:
        candidates = self._candidate_chunks(claim["text"], retrieved_chunks)

        if not candidates:
            return {
                "claim_id": claim["id"],
                "status": "Unsupported",
                "confidence": 0.0,
                "evidence": [],
                "rationale": "No retrieved chunk addresses the claim."
            }

        chunks_text = "\n\n".join(
            f"[{c['chunk_id']}]: {c['text']}" for c in candidates
        )

        prompt = EVIDENCE_MATCH_PROMPT.format(
            claim=claim["text"],
            chunks=chunks_text
        )

        try:
            raw = self._call_llm(prompt)
            print("EVIDENCE RAW OUTPUT:", raw)

            parsed = self._extract_json(raw)

            return {
                "claim_id": claim["id"],
                "status": parsed.get("status", "Unsupported"),
                "confidence": float(parsed.get("confidence", 0.0)),
                "evidence": parsed.get("evidence", []),
                "rationale": parsed.get("rationale", "")
            }

        except Exception as e:
            print("EVIDENCE MATCH ERROR:", str(e))
            return {
                "claim_id": claim["id"],
                "status": "Unsupported",
                "confidence": 0.0,
                "evidence": [],
                "rationale": "Evidence matching failed."
            }
