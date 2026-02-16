# UArizona IT Help Desk Bot (OpenAI + RAG + ServiceNow)

FastAPI-based help desk bot for university IT support use cases (NetID login, Duo MFA, VPN/firewall, wifi, email, LMS).  
The app classifies issues, generates troubleshooting steps with OpenAI, grounds responses with historical KB/ticket context from MongoDB, and escalates low-confidence cases to human support with optional ServiceNow incident creation.

## What This Project Does

- Handles support chat requests through `POST /chat` and the web UI at `/`.
- Classifies issue category and urgency (priority).
- Generates response summaries and recommended remediation steps via OpenAI.
- Uses retrieval-augmented context from MongoDB (`/kb/ingest` + semantic retrieval).
- Applies guardrails:
  - confidence threshold
  - explicit human escalation
  - audit logging
- Opens local tickets in SQLite and optionally creates incidents in ServiceNow.

## Architecture

- **API/UI**: FastAPI + Jinja templates (`/` chat UI, `/admin` dashboard)
- **LLM**: OpenAI Chat Completions API
- **RAG Store**: MongoDB (`kb_documents` collection with embeddings)
- **Ticket Store**: SQLite (`tickets` + `audit_logs`)
- **ITSM Integration**: ServiceNow Table API (`incident` table by default)

## Quick Start (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set at least:

- `OPENAI_API_KEY`

Run:

```powershell
uvicorn app.main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Chat UI: `http://127.0.0.1:8000/`
- Admin UI: `http://127.0.0.1:8000/admin`

## Environment Variables

Required for LLM responses:

- `OPENAI_API_KEY`

Common settings:

- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `DATABASE_PATH` (default: `helpdesk_tickets.db`)
- `CONFIDENCE_THRESHOLD` (default: `0.65`)
- `EMBEDDING_MODEL` (default: `text-embedding-3-small`)

MongoDB (RAG):

- `MONGO_URI`
- `MONGO_DB_NAME` (default: `helpdesk`)
- `MONGO_KB_COLLECTION` (default: `kb_documents`)

ServiceNow (incident creation):

- `SERVICENOW_INSTANCE_URL` (e.g. `https://<instance>.service-now.com`)
- `SERVICENOW_USERNAME`
- `SERVICENOW_PASSWORD`
- `SERVICENOW_INCIDENT_TABLE` (default: `incident`)

## Core API Endpoints

- `GET /health`
- `POST /chat`
- `POST /kb/ingest`
- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}/status`

### Example Chat Request

```json
{
  "user_id": "jdoe1",
  "issue_text": "Cannot login to NetID and Duo push is failing",
  "context": "Exam starts in 1 hour"
}
```

### Example KB Ingest Request

```json
{
  "documents": [
    {
      "title": "Duo Push Delay",
      "text": "If Duo push fails, verify phone time sync, notifications, and alternate MFA method.",
      "source": "uarizona-kb"
    }
  ]
}
```

## Resume-Bullet Mapping

This build supports the core claims:

- **Python + ServiceNow + OpenAI triage**: implemented via chat pipeline + `app/servicenow.py`
- **MongoDB + embeddings retrieval**: implemented via `app/retrieval.py` and `/kb/ingest`
- **Guardrails**: confidence threshold, escalate-to-human behavior, and audit logging

## Git Upload Notes

Commit these:

- `app/`, `templates/`, `static/`
- `.github/workflows/ci.yml`
- `requirements.txt`, `.env.example`, `README.md`
- `.gitignore`, `.gitattributes`, `.editorconfig`

Do not commit:

- `.env`
- `.venv/`
- `*.db`, `*.sqlite*`
- `__pycache__/` and local cache artifacts
