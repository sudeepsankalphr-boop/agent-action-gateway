# Agent Action Gateway

A FastAPI service that acts as a policy enforcement gateway for AI agent actions. Before an agent executes an action (send email, set budget, delete a campaign, etc.), it submits a request here. The gateway evaluates the request against a set of YAML-defined policies, returns a decision, and writes an immutable audit record.

## Architecture

```
POST /actions
    └── policy engine (YAML rules)
            └── audit log (SQLite, append-only)
                    └── decision + correlation_id returned to caller

GET /audit      — JSON list of all audit records, newest first
GET /dashboard  — server-rendered HTML table of audit records
GET /health     — liveness check
```

## Quickstart

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/dashboard to see the audit dashboard.

## Submitting an action

```bash
curl -X POST http://localhost:8000/actions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-1",
    "action_type": "set_budget",
    "target": "campaign-42",
    "params": {"amount": 75000}
  }'
```

Response:

```json
{
  "correlation_id": "...",
  "decision": "REJECTED",
  "reason": "Budget amount exceeds hard rejection limit of $50,000",
  "agent_id": "agent-1",
  "action_type": "set_budget",
  "target": "campaign-42",
  "params": {"amount": 75000}
}
```

## Policy files

Policies live in `policies/*.yaml`. Each file declares a version and a list of rules:

```yaml
name: budget-policy
version: "1.0.0"
rules:
  - id: reject-extreme-budget
    condition:
      action_type: set_budget
      param: amount
      op: gt
      value: 50000
    decision: REJECTED
    reason: "Budget amount exceeds hard rejection limit of $50,000"
```

Supported decisions: `APPROVED`, `NEEDS_APPROVAL`, `REJECTED`.  
The engine takes the most severe verdict across all matching rules.

## Integration: HyperMindZ NL-to-SQL

This gateway is live-integrated with [HyperMindZ](https://github.com/sudeepsankalphr-boop/Hyper-Mindz-Solution), an NL-to-SQL query service. Before every AI-generated SQL query is executed against user data, HyperMindZ submits it to this gateway for policy evaluation. Queries containing destructive keywords are blocked before they reach the database.

Request shape sent from HyperMindZ (`backend/gateway.py`):

```json
{
  "agent_id": "hypermindz-nl-sql",
  "action_type": "execute_query",
  "target": "data",
  "params": { "sql": "SELECT category, SUM(revenue) FROM data GROUP BY category" }
}
```

`APPROVED` → query executes. `REJECTED` / `NEEDS_APPROVAL` → 403 returned to the user with the policy reason and correlation_id. If the gateway is unreachable, queries are blocked (fail-closed).

## Running tests

```bash
pytest tests/ -v
```

## Project structure

```
app/
  api/          — FastAPI routers (actions, audit, health)
  core/         — database connection, config
  dashboard/    — Jinja2 HTML dashboard
  models/       — Pydantic schemas
  policy/       — YAML loader + rule evaluator + engine
  services/     — action_service (orchestrator), audit_service (append-only writes)
policies/       — YAML policy definitions
tests/          — pytest suite
```
