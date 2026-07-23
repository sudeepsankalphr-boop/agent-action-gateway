from app.models.decision import Decision


def test_action_appears_in_audit_log(client):
    payload = {
        "agent_id": "agent-1",
        "action_type": "send_email",
        "target": "user@example.com",
        "params": {"subject": "hello"},
    }
    post_resp = client.post("/actions", json=payload)
    assert post_resp.status_code == 200
    action_data = post_resp.json()
    correlation_id = action_data["correlation_id"]
    decision = action_data["decision"]

    audit_resp = client.get("/audit")
    assert audit_resp.status_code == 200
    records = audit_resp.json()
    assert len(records) >= 1

    match = next((r for r in records if r["correlation_id"] == correlation_id), None)
    assert match is not None, "audit record not found for correlation_id"
    assert match["decision"] == decision
    assert match["agent_id"] == payload["agent_id"]
    assert match["action_type"] == payload["action_type"]


def test_rejected_action_recorded(client):
    payload = {
        "agent_id": "agent-bad",
        "action_type": "fly_rocket",
        "target": "mars",
        "params": {},
    }
    post_resp = client.post("/actions", json=payload)
    assert post_resp.status_code == 200
    data = post_resp.json()
    assert data["decision"] == Decision.REJECTED.value

    records = client.get("/audit").json()
    match = next((r for r in records if r["correlation_id"] == data["correlation_id"]), None)
    assert match is not None
    assert match["decision"] == Decision.REJECTED.value


def test_audit_returns_newest_first(client):
    for action_type in ("send_email", "create_campaign"):
        client.post("/actions", json={
            "agent_id": "agent-order",
            "action_type": action_type,
            "target": "t",
            "params": {},
        })

    records = client.get("/audit").json()
    ids = [r["id"] for r in records]
    assert ids == sorted(ids, reverse=True)
