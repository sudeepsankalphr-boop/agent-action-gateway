from pydantic import BaseModel


class AuditRecord(BaseModel):
    id: int
    correlation_id: str
    timestamp: str
    agent_id: str
    action_type: str
    target: str
    params: str
    decision: str
    evaluated_rule: str | None
    reason: str | None
    policy_version: str | None
    processing_latency_ms: float | None
