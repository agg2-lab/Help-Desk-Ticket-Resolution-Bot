from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="University identifier, e.g., NetID")
    issue_text: str = Field(..., min_length=5, description="User's IT issue")
    context: Optional[str] = Field(None, description="Optional extra context")


class ChatResponse(BaseModel):
    category: str
    priority: str
    solved: bool
    response_text: str
    ticket_created: bool
    ticket_id: Optional[int] = None
    confidence: float
    escalated_to_human: bool
    servicenow_incident_number: Optional[str] = None
    recommended_steps: List[str] = Field(default_factory=list)


class TicketCreate(BaseModel):
    user_id: str
    category: str
    summary: str
    details: str
    priority: str = "medium"


class Ticket(BaseModel):
    id: int
    user_id: str
    category: str
    summary: str
    details: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., description="Ticket status: open, in_progress, resolved, closed")


class KBDocument(BaseModel):
    title: str
    text: str = Field(..., min_length=5)
    source: str = "manual"


class KBIngestRequest(BaseModel):
    documents: List[KBDocument]
