"""
TwisterLab API - Ticket Management Routes (Minimal for debugging)
"""

from fastapi import APIRouter
import uuid
from datetime import datetime

# Create router
router = APIRouter()

# In-memory storage
tickets_db: dict[str, dict] = {}

@router.post("/")
async def create_ticket(ticket: dict):
    ticket_id = str(uuid.uuid4())
    ticket_data = {
        "id": ticket_id,
        "subject": ticket.get("subject", "No subject"),
        "description": ticket.get("description", "No description"),
        "requestor_email": ticket.get("requestor_email", "unknown@example.com"),
        "created_at": datetime.utcnow().isoformat()
    }
    tickets_db[ticket_id] = ticket_data
    return ticket_data

@router.get("/")
async def list_tickets():
    return list(tickets_db.values())