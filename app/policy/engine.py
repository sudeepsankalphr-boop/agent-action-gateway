from __future__ import annotations

import time

from app.models.action import ActionRequest
from app.models.decision import Decision, DecisionResult
from app.policy.evaluator import evaluate
from app.policy.loader import load_all_policies

_SEVERITY: dict[Decision, int] = {
    Decision.APPROVED: 0,
    Decision.NEEDS_APPROVAL: 1,
    Decision.REJECTED: 2,
}


def evaluate_action(
    action: ActionRequest, policies_dir: str | None = None
) -> DecisionResult:
    t0 = time.perf_counter()
    policies = load_all_policies(policies_dir)

    verdict = Decision.APPROVED
    reason = "All policies passed"
    evaluated_rule = "none"
    policy_version = "N/A"

    for policy in policies:
        result = evaluate(action, policy)
        if result is None:
            continue
        rule_decision, rule_id, rule_reason = result
        if _SEVERITY[rule_decision] > _SEVERITY[verdict]:
            verdict = rule_decision
            reason = rule_reason
            evaluated_rule = rule_id
            policy_version = policy.version
        if verdict == Decision.REJECTED:
            break

    latency_ms = (time.perf_counter() - t0) * 1000
    return DecisionResult(
        verdict=verdict,
        reason=reason,
        evaluated_rule=evaluated_rule,
        policy_version=policy_version,
        latency_ms=latency_ms,
    )
