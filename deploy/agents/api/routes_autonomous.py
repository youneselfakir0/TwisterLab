"""
TwisterLab API - Autonomous Agents Routes

REST API endpoints for autonomous agent management, monitoring,
and orchestration integration.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from agents.orchestrator.autonomous_orchestrator import (
    get_orchestrator,
    start_autonomous_agents,
    stop_autonomous_agents,
)

# Create router
router = APIRouter(
    prefix="/autonomous",
    tags=["autonomous-agents"],
    responses={404: {"description": "Agent or operation not found"}},
)


# Pydantic models
class AgentOperationRequest(BaseModel):
    """Request model for agent operations."""

    operation: str = Field(..., description="Operation to execute")
    context: Optional[Dict[str, Any]] = Field(None, description="Operation context")
    async_execution: bool = Field(False, description="Execute asynchronously")


class AgentOperationResponse(BaseModel):
    """Response model for agent operations."""

    agent: str
    operation: str
    status: str
    timestamp: str
    result: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None


class SystemStatusResponse(BaseModel):
    """Response model for system status."""

    status: str
    agents_count: int
    scheduled_tasks_count: int
    healthy_agents: int
    last_coordination: Optional[str] = None
    uptime: Optional[str] = None


class AgentStatusResponse(BaseModel):
    """Response model for individual agent status."""

    agent: str
    status: str
    health: Dict[str, Any]
    capabilities: List[str]
    orchestrator_status: Dict[str, Any]


class AgentsListResponse(BaseModel):
    """Response model for list of all agents."""

    agents: Dict[str, Dict[str, Any]]


class EmergencyResponseRequest(BaseModel):
    """Request model for emergency response."""

    issue_type: str = Field(..., description="Type of issue detected")
    severity: str = Field(
        ..., pattern="^(low|medium|high|critical)$", description="Issue severity"
    )
    description: Optional[str] = Field(None, description="Issue description")


class EmergencyResponseResponse(BaseModel):
    """Response model for emergency response."""

    emergency_triggered: bool
    issue_type: str
    severity: str
    responses: List[Dict[str, Any]]
    timestamp: str


@router.on_event("startup")
async def startup_event():
    """Start autonomous agents on API startup."""
    try:
        await start_autonomous_agents()
    except Exception as e:
        # Log error but don't crash API
        print(f"Warning: Failed to start autonomous agents: {str(e)}")


@router.on_event("shutdown")
async def shutdown_event():
    """Stop autonomous agents on API shutdown."""
    try:
        await stop_autonomous_agents()
    except Exception as e:
        print(f"Warning: Failed to stop autonomous agents: {str(e)}")


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get overall autonomous agent system status.

    Returns comprehensive status of all agents and orchestration system.
    """
    try:
        orchestrator = await get_orchestrator()
        return orchestrator.get_system_status()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get system status: {str(e)}"
        )


@router.get("/agents", response_model=AgentsListResponse)
async def get_agents_status():
    """
    Get status of all autonomous agents.

    Returns status information for all registered agents.
    """
    try:
        orchestrator = await get_orchestrator()
        status = await orchestrator.get_agent_status()
        return {"agents": status.get("agents", {})}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get agents status: {str(e)}"
        )


@router.get("/agents/{agent_name}", response_model=AgentStatusResponse)
async def get_agent_status(agent_name: str):
    """
    Get status of a specific autonomous agent.

    Parameters:
    - agent_name: Name of the agent (monitoring, backup, sync)
    """
    try:
        orchestrator = await get_orchestrator()
        return await orchestrator.get_agent_status(agent_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/agents/{agent_name}/execute", response_model=AgentOperationResponse)
async def execute_agent_operation(
    agent_name: str, request: AgentOperationRequest, background_tasks: BackgroundTasks
):
    """
    Execute an operation on a specific autonomous agent.

    Parameters:
    - agent_name: Name of the agent (monitoring, backup, sync)
    - operation: Operation to execute
    - context: Optional operation context
    - async_execution: Execute asynchronously (default: false)
    """
    try:
        orchestrator = await get_orchestrator()

        if request.async_execution:
            # Execute in background
            background_tasks.add_task(
                _execute_agent_operation_background,
                agent_name,
                request.operation,
                request.context,
            )
            return AgentOperationResponse(
                agent=agent_name,
                operation=request.operation,
                status="scheduled",
                timestamp=datetime.now().isoformat(),
                result={"message": "Operation scheduled for background execution"},
            )

        else:
            # Execute synchronously
            start_time = datetime.now()
            result = await orchestrator.execute_agent_operation(
                agent_name, request.operation, request.context
            )
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return AgentOperationResponse(
                agent=agent_name,
                operation=request.operation,
                status="completed",
                timestamp=datetime.now().isoformat(),
                result=result,
                execution_time_ms=execution_time,
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")


@router.post("/emergency", response_model=EmergencyResponseResponse)
async def trigger_emergency_response(request: EmergencyResponseRequest):
    """
    Trigger emergency response for critical system issues.

    This endpoint should be called when critical issues are detected
    that require immediate autonomous agent intervention.
    """
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.trigger_emergency_response(
            request.issue_type, request.severity
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Emergency response failed: {str(e)}"
        )


@router.post("/start")
async def start_agents():
    """Manually start the autonomous agent system."""
    try:
        await start_autonomous_agents()
        return {"message": "Autonomous agents started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agents: {str(e)}")


@router.post("/stop")
async def stop_agents():
    """Manually stop the autonomous agent system."""
    try:
        await stop_autonomous_agents()
        return {"message": "Autonomous agents stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agents: {str(e)}")


@router.get("/capabilities")
async def get_system_capabilities():
    """
    Get all capabilities available across autonomous agents.

    Returns a comprehensive list of all operations and features
    provided by the autonomous agent system.
    """
    try:
        orchestrator = await get_orchestrator()

        capabilities = {}
        for agent_name, agent in orchestrator.agents.items():
            capabilities[agent_name] = {
                "capabilities": agent.get_capabilities(),
                "priority": agent.priority,
                "name": agent.name,
            }

        return {
            "system_capabilities": capabilities,
            "total_agents": len(capabilities),
            "available_operations": [
                "health_check",
                "diagnostic",
                "repair",
                "backup",
                "integrity_check",
                "recovery",
                "sync",
                "consistency_check",
                "reconciliation",
                "performance_check",
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get capabilities: {str(e)}"
        )


# Background task helper
async def _execute_agent_operation_background(
    agent_name: str, operation: str, context: Dict[str, Any]
):
    """Execute agent operation in background."""
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.execute_agent_operation(
            agent_name, operation, context
        )

        # Log completion (in production, this could send notifications)
        print(
            f"Background operation completed: {agent_name}:{operation} - Result: {result}"
        )

    except Exception as e:
        # Log error (in production, this could trigger alerts)
        print(f"Background operation failed: {agent_name}:{operation} - {str(e)}")


# Health check endpoint for autonomous agents
@router.get("/health")
async def autonomous_agents_health():
    """Health check endpoint for autonomous agents."""
    try:
        orchestrator = await get_orchestrator()
        status = orchestrator.get_system_status()

        if status["status"] == "running":
            return {
                "status": "healthy",
                "agents": status["agents_count"],
                "healthy_agents": status["healthy_agents"],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "status": "unhealthy",
                "message": f"System status: {status['status']}",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }
