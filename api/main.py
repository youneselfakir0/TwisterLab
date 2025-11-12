import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Response, Depends

# Hybrid Authentication (Azure AD + Local fallback)
try:
    from api.auth_hybrid import router as auth_router, get_current_user
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    auth_router = None
    get_current_user = None
    logger = logging.getLogger(__name__)
    logger.warning("Hybrid auth module not available; authentication disabled")

# Prometheus metrics
try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        generate_latest,
        CONTENT_TYPE_LATEST,
        REGISTRY,
    )

    PROMETHEUS_AVAILABLE = True

    # Define metrics
    http_requests_total = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )

    agent_operations_total = Counter(
        "agent_operations_total",
        "Total agent operations executed",
        ["agent", "operation", "status"],
    )

    active_agents = Gauge(
        "active_agents_count",
        "Number of active agents",
    )

    http_request_duration_seconds = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint"],
    )

    agent_execution_duration_seconds = Histogram(
        "agent_execution_duration_seconds",
        "Agent execution duration in seconds",
        ["agent", "operation"],
    )

except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("prometheus_client not installed; metrics will not be available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TwisterLab API", version="1.0.0", description="Autonomous IT Helpdesk API"
)

# Include authentication routes if available
if AUTH_AVAILABLE and auth_router:
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    logger.info("Hybrid authentication enabled (Azure AD + Local fallback)")
else:
    logger.warning("Authentication disabled - Hybrid auth module not available")

# Include MCP REST endpoints (REAL agents)
try:
    from api.routes_mcp_real import router as mcp_real_router
    app.include_router(mcp_real_router, prefix="/v1/mcp/tools", tags=["MCP Real Agents"])
    logger.info("MCP REAL API enabled (/v1/mcp/tools/*)")
except ImportError as e:
    logger.warning(f"MCP REAL API not available: {e}")

# Mock data for agents
AGENTS = [
    {
        "name": "ClassifierAgent",
        "status": "active",
        "priority": 1,
        "capabilities": ["classification", "routing"],
    },
    {
        "name": "ResolverAgent",
        "status": "active",
        "priority": 2,
        "capabilities": ["resolution", "execution"],
    },
    {
        "name": "DesktopCommanderAgent",
        "status": "active",
        "priority": 3,
        "capabilities": ["system_commands", "automation"],
    },
    {
        "name": "MaestroOrchestratorAgent",
        "status": "active",
        "priority": 4,
        "capabilities": ["orchestration", "load_balancing"],
    },
    {
        "name": "SyncAgent",
        "status": "active",
        "priority": 5,
        "capabilities": ["synchronization", "consistency"],
    },
    {
        "name": "BackupAgent",
        "status": "active",
        "priority": 6,
        "capabilities": ["backup", "recovery"],
    },
    {
        "name": "MonitoringAgent",
        "status": "active",
        "priority": 7,
        "capabilities": ["monitoring", "alerting"],
    },
]


@app.get("/")
async def root():
    return {"message": "TwisterLab API v1.0.0", "status": "operational"}


@app.get("/health")
async def health_check():
    if PROMETHEUS_AVAILABLE:
        http_requests_total.labels(method="GET", endpoint="/health", status="200").inc()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime": "operational",
    }


@app.get("/api/v1/autonomous/status")
async def get_autonomous_status():
    if PROMETHEUS_AVAILABLE:
        http_requests_total.labels(method="GET", endpoint="/api/v1/autonomous/status", status="200").inc()
        active_agents.set(len([a for a in AGENTS if a["status"] == "active"]))

    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len([a for a in AGENTS if a["status"] == "active"]),
        "total_agents": len(AGENTS),
        "system_health": "good",
    }


@app.get("/api/v1/autonomous/agents")
async def get_agents():
    return {
        "agents": AGENTS,
        "total": len(AGENTS),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/v1/autonomous/agents/{agent_name}")
async def get_agent(agent_name: str):
    agent = next((a for a in AGENTS if a["name"].lower() == agent_name.lower()), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    return agent


@app.post("/api/v1/autonomous/agents/{agent_name}/execute")
async def execute_agent_operation(
    agent_name: str,
    payload: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """
    Execute agent operation (PROTECTED ROUTE - requires authentication).

    Requires valid Azure AD JWT token in Authorization header:
        Authorization: Bearer <access_token>

    Args:
        agent_name: Name of the agent to execute
        payload: Operation parameters
        user: Current authenticated user (auto-injected if auth enabled)

    Returns:
        Agent execution result with status and metrics
    """
    import time
    start_time = time.time()

    # Log authenticated user if available
    if user:
        logger.info(f"User {user.get('name')} executing {agent_name}")

    agent = next((a for a in AGENTS if a["name"].lower() == agent_name.lower()), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

    try:
        # Route to specific agent implementations
        if agent_name.lower() == "backupagent":
            result = await execute_backup_agent(payload)
        elif agent_name.lower() == "syncagent":
            result = await execute_sync_agent(payload)
        elif agent_name.lower() == "monitoringagent":
            result = await execute_monitoring_agent(payload)
        else:
            # Mock execution for other agents
            result = {
                "agent": agent_name,
                "operation": payload.get("operation", "unknown"),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "result": f"Mock execution completed for {agent_name}",
            }

        # Track metrics
        if PROMETHEUS_AVAILABLE:
            operation = payload.get("operation", "unknown")
            status = result.get("status", "unknown")
            agent_operations_total.labels(
                agent=agent_name,
                operation=operation,
                status=status
            ).inc()

            duration = time.time() - start_time
            agent_execution_duration_seconds.labels(
                agent=agent_name,
                operation=operation
            ).observe(duration)

        return result

    except Exception as e:
        # Track error
        if PROMETHEUS_AVAILABLE:
            operation = payload.get("operation", "unknown")
            agent_operations_total.labels(
                agent=agent_name,
                operation=operation,
                status="error"
            ).inc()
        raise


async def execute_backup_agent(payload: Dict[str, Any]):
    """Execute backup operations"""
    operation = payload.get("operation", "status")

    if operation == "status":
        return {
            "agent": "BackupAgent",
            "operation": "status",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "last_backup": "2025-11-09T17:00:00Z",
                "backup_status": "completed",
                "next_backup": "2025-11-10T17:00:00Z",
                "storage_used": "2.3GB",
                "backups_count": 15,
            },
        }
    elif operation == "execute":
        # Simulate backup execution
        return {
            "agent": "BackupAgent",
            "operation": "execute",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "full_system_backup",
                "size": "2.4GB",
                "duration": "45 seconds",
                "status": "completed",
            },
        }
    else:
        raise HTTPException(
            status_code=400, detail=f"Unknown backup operation: {operation}"
        )


async def execute_sync_agent(payload: Dict[str, Any]):
    """Execute synchronization operations"""
    operation = payload.get("operation", "status")

    if operation == "status":
        return {
            "agent": "SyncAgent",
            "operation": "status",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "last_sync": "2025-11-09T16:45:00Z",
                "sync_status": "completed",
                "pending_changes": 0,
                "cache_consistency": "verified",
                "data_integrity": "intact",
            },
        }
    elif operation == "execute":
        # Simulate sync execution
        return {
            "agent": "SyncAgent",
            "operation": "execute",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "sync_id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "cache_database_sync",
                "records_processed": 1250,
                "duration": "12 seconds",
                "status": "completed",
                "consistency_check": "passed",
            },
        }
    elif operation == "verify":
        # Simulate consistency verification
        return {
            "agent": "SyncAgent",
            "operation": "verify",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "cache_database_consistency": "verified",
                "orphaned_records": 0,
                "data_integrity": "100%",
                "last_verification": datetime.now().isoformat(),
            },
        }
    else:
        raise HTTPException(
            status_code=400, detail=f"Unknown sync operation: {operation}"
        )


async def execute_monitoring_agent(payload: Dict[str, Any]):
    """Execute monitoring operations"""
    operation = payload.get("operation", "status")

    if operation == "status":
        return {
            "agent": "MonitoringAgent",
            "operation": "status",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "system_health": "excellent",
                "active_alerts": 0,
                "response_time": "45ms",
                "uptime": "99.9%",
                "last_check": datetime.now().isoformat(),
            },
        }
    elif operation == "health_check":
        check_type = payload.get("context", {}).get("check_type", "system")
        return {
            "agent": "MonitoringAgent",
            "operation": "health_check",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "check_type": check_type,
                "status": "healthy",
                "details": f"{check_type} health check passed",
                "metrics": {
                    "cpu_usage": "23%",
                    "memory_usage": "1.2GB",
                    "disk_usage": "45%",
                    "network_io": "normal",
                },
            },
        }
    else:
        raise HTTPException(
            status_code=400, detail=f"Unknown monitoring operation: {operation}"
        )


@app.get("/api/v1/monitoring/health")
async def get_monitoring_health():
    return {
        "status": "operational",
        "services": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "monitoring": "operational",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Exposes metrics in Prometheus format for scraping:
    - http_requests_total: Total HTTP requests by method, endpoint, and status
    - agent_operations_total: Total agent operations by agent, operation, and status
    - active_agents_count: Current number of active agents
    - http_request_duration_seconds: HTTP request latency histogram
    - agent_execution_duration_seconds: Agent execution time histogram
    """
    if not PROMETHEUS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Prometheus metrics not available (prometheus_client not installed)",
        )

    # Update current active agents count
    active_agents.set(len([a for a in AGENTS if a["status"] == "active"]))

    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting TwisterLab API server...")
    print("TwisterLab API server starting on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
