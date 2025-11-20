import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

# Import the agent registry, schemas, and security dependencies
from agents.registry import agent_registry
from api.schemas import AgentExecutePayload
from api.auth_hybrid import get_current_user
from typing import Any, Dict

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


@router.get("/{agent_name}/management/status")
async def agent_management_status(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return management status for an agent (backup) including retention worker status and backup stats."""
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    # Admin check if roles present
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    status = {
        "agent_name": agent.name,
        "agent_id": agent.agent_id,
        "status": agent.status.value,
    }

    # If backup agent, include backup stats and retention status if available
    try:
        if hasattr(agent, "get_backup_stats"):
            status["backup_stats"] = agent.get_backup_stats()
        if hasattr(agent, "is_retention_running"):
            status["retention_running"] = agent.is_retention_running()
    except Exception:
        pass

    return {"status": "success", "data": status}


@router.post("/{agent_name}/management/retention/start")
async def agent_management_retention_start(agent_name: str, payload: Dict[str, Any] = {}, current_user: Dict[str, Any] = Depends(get_current_user)):
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    interval = payload.get("interval_seconds", 3600)
    if hasattr(agent, "start_scheduled_retention"):
        started = await agent.start_scheduled_retention(int(interval))
        return {"status": "success", "started": bool(started)}
    return {"status": "error", "error": "Retention worker not supported for this agent"}


@router.post("/{agent_name}/management/retention/stop")
async def agent_management_retention_stop(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    if hasattr(agent, "stop_scheduled_retention"):
        stopped = await agent.stop_scheduled_retention()
        return {"status": "success", "stopped": bool(stopped)}
    return {"status": "error", "error": "Retention worker not supported for this agent"}


@router.post("/{agent_name}/management/retention/apply")
async def agent_management_retention_apply(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    # Use agent run to trigger the apply_retention operation
    try:
        result = await agent.run(context={"operation": "apply_retention"})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_name}/management/backups")
async def agent_management_list_backups(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    try:
        result = await agent.run(context={"operation": "list_backups"})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_name}/management/backups/verify")
async def agent_management_verify_backup(agent_name: str, payload: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    backup_id = payload.get("backup_id")
    if not backup_id:
        raise HTTPException(status_code=400, detail="backup_id is required")
    try:
        result = await agent.run(context={"operation": "verify_backup", "backup_id": backup_id})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_name}/management/backups/restore")
async def agent_management_restore_backup(agent_name: str, payload: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    roles = current_user.get("roles") if isinstance(current_user, dict) else []
    if roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    backup_id = payload.get("backup_id")
    if not backup_id:
        raise HTTPException(status_code=400, detail="backup_id is required")
    try:
        result = await agent.run(context={"operation": "restore_backup", "backup_id": backup_id})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _require_admin(user: Dict[str, Any]):
    roles = user.get("roles", []) if isinstance(user, dict) else []
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin privileges required")


@router.get("/{agent_name}/management/status")
async def agent_management_status(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    status = {
        "agent": agent.name,
        "agent_id": agent.agent_id,
        "retention_running": getattr(agent, "is_retention_running", lambda: False)(),
        "manifest_count": None,
    }
    # If agent exposes manifest path and load method, use it
    if hasattr(agent, "_load_manifest"):
        try:
            manifest = agent._load_manifest()
            status["manifest_count"] = len(manifest)
        except Exception:
            status["manifest_count"] = None
    return {"status": "success", "data": status}


@router.post("/{agent_name}/management/retention/start")
async def agent_management_start_retention(agent_name: str, payload: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    interval = payload.get("interval_seconds") or 3600
    # Some agents might not have start_scheduled_retention
    if not hasattr(agent, "start_scheduled_retention"):
        raise HTTPException(status_code=400, detail="Agent does not support scheduled retention")
    started = await agent.start_scheduled_retention(int(interval))
    return {"status": "success", "started": started}


@router.post("/{agent_name}/management/retention/stop")
async def agent_management_stop_retention(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    if not hasattr(agent, "stop_scheduled_retention"):
        raise HTTPException(status_code=400, detail="Agent does not support scheduled retention")
    stopped = await agent.stop_scheduled_retention()
    return {"status": "success", "stopped": stopped}


@router.post("/{agent_name}/management/retention/apply")
async def agent_management_apply_retention(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    try:
        result = await agent.run({"operation": "apply_retention"})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_name}/management/backups")
async def agent_management_list_backups(agent_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    try:
        result = await agent.run({"operation": "list_backups"})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_name}/management/backups/verify")
async def agent_management_verify_backup(agent_name: str, payload: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    backup_id = payload.get("backup_id")
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    if not backup_id:
        raise HTTPException(status_code=400, detail=f"backup_id required")
    try:
        result = await agent.run({"operation": "verify_backup", "backup_id": backup_id})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_name}/management/backups/restore")
async def agent_management_restore_backup(agent_name: str, payload: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    _require_admin(current_user)
    agent = agent_registry.get_agent(agent_name)
    backup_id = payload.get("backup_id")
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    if not backup_id:
        raise HTTPException(status_code=400, detail=f"backup_id required")
    try:
        result = await agent.run({"operation": "restore_backup", "backup_id": backup_id})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
