from enum import Enum
from pydantic import BaseModel


class Decision(str, Enum):
    APPROVED = "APPROVED"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    REJECTED = "REJECTED"


class DecisionResult(BaseModel):
    verdict: Decision
    reason: str
    evaluated_rule: str
    policy_version: str
    latency_ms: float
