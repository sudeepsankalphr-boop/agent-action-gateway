from pydantic import BaseModel, field_validator


class ActionRequest(BaseModel):
    agent_id: str
    action_type: str
    target: str
    params: dict

    @field_validator("agent_id", "action_type", "target")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must be a non-empty string")
        return v


class ActionResponse(BaseModel):
    agent_id: str
    action_type: str
    target: str
    params: dict
    status: str


class ActionDecisionResponse(BaseModel):
    correlation_id: str
    agent_id: str
    action_type: str
    target: str
    params: dict
    decision: str
    reason: str
