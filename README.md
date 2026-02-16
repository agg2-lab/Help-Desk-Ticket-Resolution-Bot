# UArizona Database Help Desk Ticket Bot

This project is a starter **university IT help desk bot** that:

- Uses the OpenAI API to generate troubleshooting responses.
- Classifies common campus issues (login, Duo MFA, wifi, VPN/firewall, email, LMS).
- Stores tickets in a local SQLite database.
- Auto-creates tickets when issues are unresolved or high priority.
- Supports optional ServiceNow incident creation for escalated tickets.
- Supports optional MongoDB-backed retrieval to ground responses in historical KB/tickets.

## Stack

- Python + FastAPI
- OpenAI Python SDK
- SQLite (file-based database)
- Optional MongoDB for KB/ticket retrieval
- Optional ServiceNow API integration

## 1) Setup

From PowerShell in this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy env template:

```powershell
copy .env.example .env
```

Edit `.env` and set your key:

- `OPENAI_API_KEY=...`

Optional:

- `OPENAI_MODEL=gpt-4o-mini`
- `DATABASE_PATH=helpdesk_tickets.db`
- `CONFIDENCE_THRESHOLD=0.65`
- `MONGO_URI=<mongodb-connection-string>`
- `SERVICENOW_INSTANCE_URL=https://<instance>.service-now.com`
- `SERVICENOW_USERNAME=<user>`
- `SERVICENOW_PASSWORD=<password>`

## 2) Run API

```powershell
uvicorn app.main:app --reload
```

API docs:

- http://127.0.0.1:8000/docs
- Chat UI: http://127.0.0.1:8000/
- Admin dashboard: http://127.0.0.1:8000/admin

## 3) Test the Bot

### Health check

```powershell
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8000/health"
```

### Chat/help request

```powershell
$body = @{
  user_id = "jdoe1"
  issue_text = "I cannot login to my NetID and Duo push is not working"
  context = "Exam starts in 1 hour"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/chat" -ContentType "application/json" -Body $body
```

### Get ticket by ID

```powershell
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8000/tickets/1"
```

## API Endpoints

- `GET /health`
- `POST /chat`
- `POST /kb/ingest`
- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `PATCH /tickets/{ticket_id}/status`

### Example KB ingest payload

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

## Notes for University Deployment

- Replace/extend troubleshooting playbooks in `app/kb.py` with official UArizona IT policy links.
- Add authentication and role-based access before production use.
- Move from SQLite to PostgreSQL for multi-user deployment.
- Add audit logging and PII redaction for support transcripts.

## GitHub Upload Checklist

This repo is prepped for safe upload:

- `.gitignore` excludes `.env`, local DB files, virtual envs, and caches.
- `.gitattributes` and `.editorconfig` keep line endings/formatting consistent.
- GitHub Actions workflow (`.github/workflows/ci.yml`) runs syntax checks on push/PR.

### First push (PowerShell)

```powershell
git init
git add .
git commit -m "Initial commit: UArizona help desk bot"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

### Important safety check before push

```powershell
git status
git diff -- .env
```

If `.env` appears in staged files, remove it before commit:

```powershell
git restore --staged .env
```
