from typing import List, Dict
from pydantic import BaseModel

class Claim(BaseModel):
    id: str
    text: str

class Evidence(BaseModel):
    claim_id: str
    chunk_ids: List[str]
    support_level: str  # supported | weak | unsupported | contradicted
    rationale: str
    confidence: float

class Metrics(BaseModel):
    faithfulness: float
    hallucination_rate: float
    evidence_coverage: float
    decision_consistency: float | None = None

class AuditResult(BaseModel):
    claims: List[Claim]
    evidence: List[Evidence]
    metrics: Metrics
    verdict: str  # SAFE | PARTIALLY_SUPPORTED | UNSAFE
