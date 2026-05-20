# response_schema.py — must match orchestrator return exactly

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class RecommendationItem(BaseModel):
    reason: str
    action: str


class ClaimResponse(BaseModel):
    claim_id:          str
    prediction:        str
    risk_level:        str
    risk_score:        float
    approve_threshold: float
    deny_threshold:    float
    top_reasons:       List[Dict[str, Any]]         = []
    policy_summary: Optional[str] = None
    recommendations:   List[RecommendationItem]     = []
    next_action:       Optional[str]                = None