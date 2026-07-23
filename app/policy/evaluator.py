from __future__ import annotations

import re
from typing import Any

from app.models.action import ActionRequest
from app.models.decision import Decision
from app.policy.loader import PolicyPack

_OPS = {
    "gt":  lambda a, b: a > b,
    "gte": lambda a, b: a >= b,
    "lt":  lambda a, b: a < b,
    "lte": lambda a, b: a <= b,
    "eq":  lambda a, b: a == b,
    "ne":  lambda a, b: a != b,
}


def _matches(action: ActionRequest, condition: dict[str, Any]) -> bool:
    if "action_type" in condition:
        if action.action_type != condition["action_type"]:
            return False

    if "action_type_in" in condition:
        if action.action_type not in condition["action_type_in"]:
            return False

    if "action_type_not_in" in condition:
        if action.action_type in condition["action_type_not_in"]:
            return False

    if "param" in condition:
        param_val = action.params.get(condition["param"])
        if param_val is None:
            return False
        op_fn = _OPS.get(condition.get("op", "eq"))
        if op_fn is None:
            return False
        if not op_fn(param_val, condition["value"]):
            return False

    if "param_contains_word" in condition:
        spec = condition["param_contains_word"]
        param_val = str(action.params.get(spec["param"], "")).upper()
        words = [w.upper() for w in spec.get("words", [])]
        if not any(re.search(rf'\b{word}\b', param_val) for word in words):
            return False

    return True


def evaluate(
    action: ActionRequest, policy: PolicyPack
) -> tuple[Decision, str, str] | None:
    """Return (decision, rule_id, reason) for the first matching rule, or None."""
    for rule in policy.rules:
        if _matches(action, rule.condition):
            return Decision(rule.decision), rule.id, rule.reason
    return None
