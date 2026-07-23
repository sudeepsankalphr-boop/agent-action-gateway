import json
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.audit import AuditRecord


def write_audit_record(
    *,
    correlation_id: str,
    agent_id: str,
    action_type: str,
    target: str,
    params: dict,
    decision: str,
    evaluated_rule: str | None,
    reason: str | None,
    policy_version: str | None,
    processing_latency_ms: float | None,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO audit_log (
                correlation_id, timestamp, agent_id, action_type, target, params,
                decision, evaluated_rule, reason, policy_version, processing_latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                correlation_id,
                timestamp,
                agent_id,
                action_type,
                target,
                json.dumps(params),
                decision,
                evaluated_rule,
                reason,
                policy_version,
                processing_latency_ms,
            ),
        )


def read_audit_records() -> list[AuditRecord]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC"
        ).fetchall()
    return [AuditRecord(**dict(row)) for row in rows]
