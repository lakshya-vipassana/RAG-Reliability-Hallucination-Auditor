# app/rag/metrics.py
import statistics
from typing import List, Dict

def compute_metrics(claim_evaluations: List[Dict]) -> Dict:
    total = len(claim_evaluations)

    if total == 0:
        return {
            "faithfulness": None,
            "hallucination_rate": None,
            "evidence_coverage": None,
            "severity_score": None
        }

    strict_supported = 0
    weak_supported = 0
    unsupported = 0
    contradicted = 0
    with_evidence = 0

    for c in claim_evaluations:
        status = c["status"]

        if status == "Supported":
            strict_supported += 1
        elif status == "Weakly supported":
            weak_supported += 1
        elif status == "Unsupported":
            unsupported += 1
        elif status == "Contradicted":
            contradicted += 1

        if c.get("evidence"):
            with_evidence += 1

    faithfulness = (strict_supported + 0.5 * weak_supported) / total
    hallucination_rate = (unsupported + contradicted) / total

    # Contradictions weighted heavier
    severity_score = (unsupported + 2 * contradicted) / total

    return {
        "faithfulness": round(faithfulness, 3),
        "hallucination_rate": round(hallucination_rate, 3),
        "evidence_coverage": round(with_evidence / total, 3),
        "severity_score": round(severity_score, 3)
    }
