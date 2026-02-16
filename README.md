# UArizona IT Help Desk Bot

Production-style starter for a university help desk assistant that combines OpenAI responses, retrieval grounding, ticket lifecycle tracking, and optional ServiceNow escalation.

## Problems This Project Solves

University IT teams repeatedly face high-volume, repetitive issues that require fast triage:

- **Login/identity access failures**: NetID lockouts, password resets, Duo MFA failures.
- **Network access blockers**: campus wifi, VPN connectivity, firewall/client conflicts.
- **Service disruption confusion**: email and LMS access issues with unclear root cause.
- **Slow ticket triage**: analysts spending time rewriting summaries and first-response steps.
- **Inconsistent support quality**: variable troubleshooting responses across staff and shifts.
- **Escalation gaps**: low-confidence AI answers needing reliable handoff to human support.

This bot addresses those problems by classifying incidents, generating actionable responses, grounding recommendations in prior KB/ticket history, and escalating uncertain cases.

## Key Capabilities

- OpenAI-powered troubleshooting responses and recommended next steps.
- Category and priority detection for common university support scenarios.
- Confidence-based guardrails with explicit human escalation behavior.
- Local ticket management in SQLite with status workflow (`open`, `in_progress`, `resolved`, `closed`).
- Audit logging for request/response and escalation events.
- ServiceNow incident creation for escalated or unresolved tickets.
- MongoDB-based retrieval to ground responses in historical resolutions.

## Architecture

- **API/UI**: FastAPI + Jinja templates
- **LLM**: OpenAI Chat Completions API
- **RAG**: MongoDB document store + OpenAI embeddings
- **Ticket storage**: SQLite
- **ITSM integration**: ServiceNow Table API

## Tech Stack

- Python
- FastAPI
- OpenAI Python SDK
- SQLite
- MongoDB (optional)
- ServiceNow REST API (optional)


## Configuration

Core:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `DATABASE_PATH` (default: `helpdesk_tickets.db`)
- `CONFIDENCE_THRESHOLD` (default: `0.65`)
- `EMBEDDING_MODEL` (default: `text-embedding-3-small`)

MongoDB retrieval (optional):

- `MONGO_URI`
- `MONGO_DB_NAME` (default: `helpdesk`)
- `MONGO_KB_COLLECTION` (default: `kb_documents`)

ServiceNow integration (optional):

- `SERVICENOW_INSTANCE_URL` (example: `https://<instance>.service-now.com`)
- `SERVICENOW_USERNAME`
- `SERVICENOW_PASSWORD`
- `SERVICENOW_INCIDENT_TABLE` (default: `incident`)

## API Endpoints

- `GET /health`
- `POST /chat`
- `POST /kb/ingest`
- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}/status`

### Example: Chat Request

```json
{
  "user_id": "jdoe1",
  "issue_text": "Cannot login to NetID and Duo push is failing",
  "context": "Exam starts in 1 hour"
}
```

### Example: KB Ingest Request

```json
{
  "documents": [
    {
      "title": "Duo push delayed",
      "text": "If Duo push is delayed, confirm mobile data is available and device time is synced.",
      "source": "uarizona-kb"
    }
  ]
}
```

## Deployment Notes

- Replace sample troubleshooting logic with official UArizona IT policy and runbooks.
- Add authentication/authorization before production exposure.
- Prefer PostgreSQL over SQLite for concurrent multi-user deployment.

- Add PII redaction and retention policy controls for compliance.
