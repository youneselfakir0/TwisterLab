"""
TwisterLab API - Agent Management Routes
Handles agent registration, status monitoring, and orchestration
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Create router
router = APIRouter()

# In-memory storage (replace with database in production)
agents_db: dict[str, dict] = {}


# Pydantic models
class AgentCreate(BaseModel):
    """Request model for creating a new agent."""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    display_name: str = Field(..., min_length=1, max_length=200, description="Display name")
    role: str = Field(
        ..., pattern="^(classifier|resolver|commander|orchestrator)$", description="Agent role"
    )
    model: str = Field("llama-3.2", description="LLM model to use")
    description: Optional[str] = Field(None, description="Agent description")


class AgentUpdate(BaseModel):
    """Request model for updating an agent."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    model: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    status: Optional[str] = Field(None, pattern="^(active|inactive|error)$")


class AgentResponse(BaseModel):
    """Response model for agent data."""

    id: str
    name: str
    display_name: str
    role: str
    model: str
    status: str
    description: Optional[str]
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string
    last_active: Optional[str] = None


@router.get("/hello")
def hello():
    """Test endpoint for agents router."""
    return {"hello": "agents"}


@router.post("/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """
    Create a new agent.

    This endpoint registers a new agent in the system.
    """
    agent_id = str(uuid.uuid4())
    now = datetime.utcnow()

    agent_data = {
        "id": agent_id,
        "name": agent.name,
        "display_name": agent.display_name,
        "role": agent.role,
        "model": agent.model,
        "status": "active",
        "description": agent.description,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "last_active": now.isoformat(),
    }

    agents_db[agent_id] = agent_data

    return AgentResponse.model_validate(agent_data)


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    role: Optional[str] = Query(None, pattern="^(classifier|resolver|commander|orchestrator)$"),
    status: Optional[str] = Query(None, pattern="^(active|inactive|error)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[AgentResponse]:
    """
    List agents with optional filtering.

    Returns a list of agents matching the specified criteria.
    """
    agents = list(agents_db.values())

    # Apply filters
    if role:
        agents = [a for a in agents if a["role"] == role]
    if status:
        agents = [a for a in agents if a["status"] == status]

    # Apply pagination
    agents = agents[offset : offset + limit]

    return [AgentResponse.model_validate(agent) for agent in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """
    Get a specific agent by ID.

    Returns detailed information about a single agent.
    """
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponse.model_validate(agents_db[agent_id])


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentUpdate) -> AgentResponse:
    """
    Update an existing agent.

    Modifies agent properties and returns the updated agent.
    """
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent_data = agents_db[agent_id]
    now = datetime.utcnow()

    # Update fields
    update_data = agent.model_dump(exclude_unset=True)
    agent_data.update(update_data)
    agent_data["updated_at"] = now.isoformat()

    if "status" in update_data and update_data["status"] == "active":
        agent_data["last_active"] = now.isoformat()

    return AgentResponse.model_validate(agent_data)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """
    Delete an agent.

    Removes an agent from the system.
    """
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    del agents_db[agent_id]
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task: dict):
    """
    Execute a task with the specified agent.

    This endpoint triggers task execution by the specified agent.
    """
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents_db[agent_id]
    if agent["status"] != "active":
        raise HTTPException(status_code=400, detail="Agent is not active")

    # For now, return a mock response
    # In production, this would trigger actual agent execution
    return {
        "agent_id": agent_id,
        "task": task,
        "status": "executed",
        "result": "Task completed successfully",
    }
