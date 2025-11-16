"""
TwisterLab API - Ticket Management Routes
Handles ticket creation, retrieval, updates, and status management
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Create router
router = APIRouter()

# In-memory storage (replace with database in production)
tickets_db: dict[str, dict] = {}


# Pydantic models
class TicketCreate(BaseModel):
    """Request model for creating a new ticket."""

    subject: str = Field(..., min_length=1, max_length=200, description="Ticket subject")
    description: str = Field(..., min_length=1, max_length=2000, description="Ticket description")
    priority: str = Field(
        "medium", pattern="^(low|medium|high|urgent)$", description="Ticket priority"
    )
    category: str = Field("general", description="Ticket category")
    requestor_email: Optional[str] = Field(None, description="Requestor email address")
    user_email: Optional[str] = Field(
        None, description="User email address (alias for requestor_email)"
    )
    ticket_number: Optional[str] = Field(None, description="Custom ticket number")


class TicketUpdate(BaseModel):
    """Request model for updating a ticket."""

    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    category: Optional[str] = Field(None)
    status: Optional[str] = Field(None, pattern="^(new|classified|assigned|resolved|closed)$")


class TicketResponse(BaseModel):
    """Response model for ticket data."""

    id: str
    subject: str
    description: str
    priority: str
    category: str
    status: str
    requestor_email: str
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string
    assigned_agent: Optional[str] = None
    resolution: Optional[str] = None


@router.get("/hello")
def hello():
    return {"hello": "world"}


@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate) -> TicketResponse:
    """
    Create a new helpdesk ticket.

    This endpoint accepts ticket creation requests and returns
    the created ticket. The ticket will be automatically classified
    and assigned by the system.
    """
    ticket_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # Use requestor_email or user_email (for compatibility with Night Shift)
    email = ticket.requestor_email or ticket.user_email
    if not email:
        raise HTTPException(
            status_code=400, detail="Either requestor_email or user_email is required"
        )

    ticket_data = {
        "id": ticket_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "priority": ticket.priority,
        "category": ticket.category,
        "status": "new",
        "requestor_email": email,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "assigned_agent": None,
        "resolution": None,
    }

    tickets_db[ticket_id] = ticket_data

    return TicketResponse.model_validate(ticket_data)


@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[str] = Query(None, pattern="^(new|classified|assigned|resolved|closed)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|urgent)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[TicketResponse]:
    """
    List tickets with optional filtering.

    Returns a paginated list of tickets. Supports filtering by status
    and priority, with configurable pagination.
    """
    tickets = list(tickets_db.values())

    # Apply filters
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]

    # Apply pagination
    tickets = tickets[offset : offset + limit]

    return [TicketResponse.model_validate(ticket) for ticket in tickets]


@router.get("/count")
async def get_tickets_count() -> dict:
    """
    Get the total count of tickets.

    Returns the total number of tickets in the system.
    """
    return {"count": len(tickets_db)}


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str) -> TicketResponse:
    """
    Get a specific ticket by ID.

    Returns detailed information about a single ticket.
    """
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse.model_validate(tickets_db[ticket_id])


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, updates: TicketUpdate) -> TicketResponse:
    """
    Update a ticket.

    Allows updating ticket fields. Only non-None values will be updated.
    """
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = tickets_db[ticket_id].copy()

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    ticket.update(update_data)
    ticket["updated_at"] = datetime.now(timezone.utc)

    tickets_db[ticket_id] = ticket

    return TicketResponse.model_validate(ticket)


@router.delete("/{ticket_id}")
async def delete_ticket(ticket_id: str) -> dict:
    """
    Delete a ticket.

    Permanently removes a ticket from the system.
    """
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    del tickets_db[ticket_id]
    return {"message": "Ticket deleted successfully"}


@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket(
    ticket_id: str, resolution: str = Query(..., min_length=1, max_length=1000)
) -> TicketResponse:
    """
    Mark a ticket as resolved.

    Updates the ticket status to 'resolved' and records the resolution.
    """
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = tickets_db[ticket_id].copy()

    if ticket["status"] not in ["assigned", "new"]:
        raise HTTPException(status_code=400, detail="Ticket must be assigned or new to be resolved")

    ticket["status"] = "resolved"
    ticket["resolution"] = resolution
    ticket["updated_at"] = datetime.now(timezone.utc)

    tickets_db[ticket_id] = ticket

    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(ticket_id: str) -> TicketResponse:
    """
    Close a resolved ticket.

    Changes ticket status from 'resolved' to 'closed'.
    """
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = tickets_db[ticket_id].copy()

    if ticket["status"] != "resolved":
        raise HTTPException(status_code=400, detail="Only resolved tickets can be closed")

    ticket["status"] = "closed"
    ticket["updated_at"] = datetime.now(timezone.utc)

    tickets_db[ticket_id] = ticket

    return TicketResponse.model_validate(ticket)
