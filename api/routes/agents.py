import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

# Import the agent registry, schemas, and security dependencies
from agents.registry import agent_registry
from api.schemas import AgentExecutePayload
from api.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/autonomous/agents",
    tags=["Agents"],
)


@router.get("/")
async def list_agents():
    """Lists all active agents from the Agent Registry, providing real-time data."""
    real_agents = agent_registry.list_agents()
    return {"agents": list(real_agents.values()), "total": len(real_agents)}


@router.get("/{agent_name}")
async def get_agent(agent_name: str):
    """Gets a specific agent's real-time status from the Agent Registry."""
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")

    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "version": agent.version,
        "description": agent.description,
        "status": agent.status.value,
    }


@router.post("/{agent_name}/execute")
async def execute_agent_operation(
    agent_name: str,
    payload: AgentExecutePayload,
    current_user: str = Depends(get_current_user),  # This endpoint is protected
):
    """
    Executes a specific agent's operation via the Agent Registry.
    Requires a valid JWT token for access.
    """
    logger.info(f"User '{current_user}' executing agent '{agent_name}'")

    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")

    context = payload.dict()

    try:
        result = await agent.run(context=context)
        return {
            "agent_name": agent.name,
            "agent_id": agent.agent_id,
            "status": agent.status.value,
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }
    except Exception as e:
        logger.error(
            f"Unhandled error during agent execution for '{agent_name}': {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred while executing agent '{agent_name}'.",
        )
