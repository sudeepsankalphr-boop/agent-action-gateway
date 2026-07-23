import uuid

from app.models.action import ActionRequest, ActionDecisionResponse
from app.models.decision import DecisionResult
from app.policy.engine import evaluate_action
from app.services.audit_service import write_audit_record


def process_action(action: ActionRequest) -> ActionDecisionResponse:
    correlation_id = str(uuid.uuid4())
    result: DecisionResult = evaluate_action(action)

    write_audit_record(
        correlation_id=correlation_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        target=action.target,
        params=action.params,
        decision=result.verdict.value,
        evaluated_rule=result.evaluated_rule,
        reason=result.reason,
        policy_version=result.policy_version,
        processing_latency_ms=result.latency_ms,
    )

    return ActionDecisionResponse(
        correlation_id=correlation_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        target=action.target,
        params=action.params,
        decision=result.verdict.value,
        reason=result.reason,
    )
