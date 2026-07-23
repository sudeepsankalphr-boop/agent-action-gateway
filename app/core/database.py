import sqlite3
from contextlib import contextmanager
from app.core.config import settings


@contextmanager
def get_db():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                correlation_id        TEXT    NOT NULL,
                timestamp             TEXT    NOT NULL,
                agent_id              TEXT    NOT NULL,
                action_type           TEXT    NOT NULL,
                target                TEXT    NOT NULL,
                params                TEXT    NOT NULL,
                decision              TEXT    NOT NULL,
                evaluated_rule        TEXT,
                reason                TEXT,
                policy_version        TEXT,
                processing_latency_ms REAL
            )
        """)
