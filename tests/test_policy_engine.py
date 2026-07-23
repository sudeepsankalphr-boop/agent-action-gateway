import pytest
from app.models.action import ActionRequest
from app.models.decision import Decision
from app.policy.engine import evaluate_action


def _action(**kwargs) -> ActionRequest:
    defaults = dict(agent_id="agent-test", action_type="send_email", target="x", params={})
    return ActionRequest(**{**defaults, **kwargs})


def test_approved_known_safe_action():
    result = evaluate_action(_action(action_type="send_email", params={"to": "user@example.com"}))
    assert result.verdict == Decision.APPROVED
    assert result.evaluated_rule == "none"


def test_approved_budget_below_threshold():
    result = evaluate_action(_action(action_type="set_budget", params={"amount": 5000}))
    assert result.verdict == Decision.APPROVED


def test_rejected_budget_above_hard_limit():
    result = evaluate_action(_action(action_type="set_budget", params={"amount": 75000}))
    assert result.verdict == Decision.REJECTED
    assert result.evaluated_rule == "reject-extreme-budget"
    assert result.policy_version == "1.0.0"


def test_rejected_unknown_action_type():
    result = evaluate_action(_action(action_type="fly_rocket", params={}))
    assert result.verdict == Decision.REJECTED
    assert result.evaluated_rule == "reject-unknown-action"


def test_needs_approval_budget_mid_range():
    result = evaluate_action(_action(action_type="set_budget", params={"amount": 25000}))
    assert result.verdict == Decision.NEEDS_APPROVAL
    assert result.evaluated_rule == "review-high-budget"


def test_needs_approval_destructive_action():
    result = evaluate_action(_action(action_type="delete_campaign", params={}))
    assert result.verdict == Decision.NEEDS_APPROVAL
    assert result.evaluated_rule == "review-destructive-action"


def test_rejected_takes_priority_over_needs_approval():
    # set_budget at extreme amount: budget policy fires REJECTED;
    # permissions policy sees set_budget as allowed → no rule; overall = REJECTED
    result = evaluate_action(_action(action_type="set_budget", params={"amount": 99999}))
    assert result.verdict == Decision.REJECTED


def test_stub_policies_do_not_raise():
    # brand, marketing, privacy stubs have empty rule sets — should be silent
    result = evaluate_action(_action(action_type="create_campaign", params={}))
    assert result.verdict == Decision.APPROVED


def test_latency_is_populated():
    result = evaluate_action(_action(action_type="send_email", params={}))
    assert result.latency_ms >= 0


def test_missing_param_does_not_match_budget_rule():
    # set_budget without 'amount' in params — no budget rule should fire
    result = evaluate_action(_action(action_type="set_budget", params={}))
    assert result.verdict == Decision.APPROVED
