import statistics
from typing import List, Dict


def compute_metrics(claim_evaluations: List[Dict]) -> Dict:
    total = len(claim_evaluations)

    if total == 0:
        return {
            "faithfulness": None,
            "hallucination_rate": None,
            "evidence_coverage": None
        }

    supported = 0
    hallucinated = 0
    with_evidence = 0

    for c in claim_evaluations:
        status = c["status"]

        if status in ("Supported", "Weakly supported"):
            supported += 1
        if status in ("Unsupported", "Contradicted"):
            hallucinated += 1
        if c.get("evidence"):
            with_evidence += 1

    return {
        "faithfulness": round(supported / total, 3),
        "hallucination_rate": round(hallucinated / total, 3),
        "evidence_coverage": round(with_evidence / total, 3)
    }


def decision_consistency(runs: List[Dict]) -> float:
    """
    runs = list of metrics dicts from multiple executions
    """
    scores = [r["faithfulness"] for r in runs if r["faithfulness"] is not None]

    if len(scores) < 2:
        return None

    return round(statistics.variance(scores), 4)
