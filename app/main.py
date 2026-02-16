from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .ai_service import generate_help_response
from .config import settings
from .database import create_ticket, get_ticket, init_db, list_tickets, log_audit_event, update_ticket_status
from .models import ChatRequest, ChatResponse, KBIngestRequest, Ticket, TicketCreate, TicketStatusUpdate
from .retrieval import ingest_kb_documents
from .servicenow import create_servicenow_incident

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/", response_class=HTMLResponse)
def chat_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.app_name})


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("admin.html", {"request": request, "app_name": settings.app_name})


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    log_audit_event(
        "chat_request_received",
        {"user_id": request.user_id, "issue_text": request.issue_text, "context": request.context},
    )
    ai_result = generate_help_response(
        user_id=request.user_id,
        issue_text=request.issue_text,
        context=request.context,
    )

    ticket_created = False
    ticket_id = None
    incident_number = None
    solved = ai_result["solved"]
    priority = ai_result["priority"]
    category = ai_result["category"]
    escalated_to_human = ai_result["escalated_to_human"]

    # Auto-open ticket for unresolved, high-priority, or low-confidence issues.
    if (not solved) or priority == "high" or escalated_to_human:
        payload = TicketCreate(
            user_id=request.user_id,
            category=category,
            summary=f"{category} issue for {request.user_id}",
            details=request.issue_text if not request.context else f"{request.issue_text}\nContext: {request.context}",
            priority=priority,
        )
        ticket_id = create_ticket(payload)
        ticket_created = True

        sn = create_servicenow_incident(
            short_description=payload.summary,
            description=payload.details,
            category=category,
            priority=priority,
            caller_id=request.user_id,
        )
        incident_number = sn.get("incident_number")
        log_audit_event(
            "servicenow_incident_attempt",
            {"ticket_id": ticket_id, "created": sn.get("created", False), "result": sn},
        )

    log_audit_event(
        "chat_response_generated",
        {
            "user_id": request.user_id,
            "category": category,
            "priority": priority,
            "solved": solved,
            "confidence": ai_result["confidence"],
            "escalated_to_human": escalated_to_human,
            "ticket_created": ticket_created,
            "ticket_id": ticket_id,
        },
    )

    return ChatResponse(
        category=category,
        priority=priority,
        solved=solved,
        response_text=ai_result["response_text"],
        ticket_created=ticket_created,
        ticket_id=ticket_id,
        confidence=ai_result["confidence"],
        escalated_to_human=escalated_to_human,
        servicenow_incident_number=incident_number,
        recommended_steps=ai_result["recommended_steps"],
    )


@app.post("/kb/ingest", response_model=dict)
def ingest_kb(payload: KBIngestRequest) -> dict:
    inserted_count = ingest_kb_documents([d.model_dump() for d in payload.documents])
    log_audit_event(
        "kb_ingest_completed",
        {"documents_received": len(payload.documents), "documents_inserted": inserted_count},
    )
    return {"inserted_count": inserted_count}


@app.post("/tickets", response_model=dict)
def create_ticket_endpoint(payload: TicketCreate) -> dict:
    ticket_id = create_ticket(payload)
    return {"ticket_id": ticket_id, "status": "open"}


@app.get("/tickets", response_model=list[Ticket])
def list_tickets_endpoint(limit: int = 100) -> list[Ticket]:
    clamped_limit = max(1, min(500, limit))
    return list_tickets(limit=clamped_limit)


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket_endpoint(ticket_id: int) -> Ticket:
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}/status", response_model=dict)
def update_ticket_status_endpoint(ticket_id: int, payload: TicketStatusUpdate) -> dict:
    allowed = {"open", "in_progress", "resolved", "closed"}
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(sorted(allowed))}")

    ok = update_ticket_status(ticket_id=ticket_id, status=payload.status)
    if not ok:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {"ticket_id": ticket_id, "status": payload.status}
