import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Response

# Add /app to Python path to allow importing agents package
sys.path.insert(0, str(Path(__file__).parent.parent))

# NOTE: Orchestrator import is LAZY (in function) to avoid database connection at startup

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

    # Agent-specific metrics
    agent_requests_total = Counter(
        "agent_requests_total",
        "Total agent requests",
        ["agent_name", "status"],
    )

    agent_execution_time_seconds = Histogram(
        "agent_execution_time_seconds",
        "Agent execution time in seconds",
        ["agent_name"],
    )

    tickets_processed_total = Counter(
        "tickets_processed_total",
        "Total tickets processed",
        ["status"],
    )

    tickets_failed_total = Counter(
        "tickets_failed_total",
        "Total tickets failed",
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

except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available, metrics disabled")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TwisterLab Autonomous Agents API",
    description="API for TwisterLab autonomous agent orchestration system",
    version="1.0.0",
)

# Mock data for agents list
AGENTS = [
    {
        "name": "ClassifierAgent",
        "description": "Classifies incoming tickets and routes them appropriately",
        "status": "active",
        "priority": 1,
        "capabilities": ["ticket_classification", "routing", "priority_assignment"],
    },
    {
        "name": "ResolverAgent",
        "description": "Resolves tickets based on SOPs and knowledge base",
        "status": "active",
        "priority": 2,
        "capabilities": ["sop_execution", "ticket_resolution", "knowledge_search"],
    },
    {
        "name": "DesktopCommanderAgent",
        "description": "Executes system commands on Windows/Linux desktops",
        "status": "active",
        "priority": 3,
        "capabilities": ["command_execution", "system_management", "process_control"],
    },
    {
        "name": "MaestroOrchestratorAgent",
        "description": "Orchestrates multi-agent workflows",
        "status": "active",
        "priority": 4,
        "capabilities": [
            "workflow_orchestration",
            "load_balancing",
            "agent_coordination",
        ],
    },
    {
        "name": "SyncAgent",
        "description": "Synchronizes cache and database, ensures data consistency",
        "status": "active",
        "priority": 5,
        "capabilities": ["cache_sync", "database_sync", "consistency_verification"],
    },
    {
        "name": "BackupAgent",
        "description": "Manages backup and disaster recovery operations",
        "status": "active",
        "priority": 6,
        "capabilities": [
            "backup_creation",
            "backup_verification",
            "disaster_recovery",
        ],
    },
    {
        "name": "MonitoringAgent",
        "description": "Monitors system health and performance",
        "status": "active",
        "priority": 7,
        "capabilities": ["health_monitoring", "metrics_collection", "alerting"],
    },
]


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.now().isoformat()}


@app.get("/api/v1/autonomous/agents")
async def list_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}


@app.get("/api/v1/autonomous/agents/{agent_name}")
async def get_agent(agent_name: str):
    agent = next((a for a in AGENTS if a["name"].lower() == agent_name.lower()), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    return agent


@app.post("/api/v1/autonomous/agents/{agent_name}/execute")
async def execute_agent_operation(agent_name: str, payload: Dict[str, Any]):
    """Execute an agent operation using the real orchestrator."""
    import time
    start_time = time.time()

    agent = next((a for a in AGENTS if a["name"].lower() == agent_name.lower()), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

    try:
        # Lazy import to avoid database connection at startup
        from agents.orchestrator.autonomous_orchestrator import get_orchestrator

        # Get orchestrator instance
        orchestrator = await get_orchestrator()

        # Map API agent names to orchestrator agent names
        agent_mapping = {
            "monitoringagent": "monitoring",
            "backupagent": "backup",
            "syncagent": "sync",
            "classifieragent": "classifier",
            "resolveragent": "resolver",
            "desktopcommanderagent": "desktop_commander",
            "maestroorchestratoragent": "maestro",
        }

        orchestrator_agent_name = agent_mapping.get(agent_name.lower())
        if not orchestrator_agent_name:
            return {
                "agent": agent_name,
                "status": "error",
                "error": f"Unknown agent mapping: {agent_name}",
                "timestamp": datetime.now().isoformat()
            }

        # Extract operation and context from payload
        operation = payload.get("operation", "health_check")
        context = payload.get("context", {})

        # Execute REAL agent operation via orchestrator
        result = await orchestrator.execute_agent_operation(
            orchestrator_agent_name,
            operation,
            context
        )

        # Track metrics
        if PROMETHEUS_AVAILABLE:
            status = "success" if result.get("status") == "success" else "error"
            agent_requests_total.labels(
                agent_name=agent_name,
                status=status
            ).inc()

            duration = time.time() - start_time
            agent_execution_time_seconds.labels(
                agent_name=agent_name
            ).observe(duration)

            # Track tickets if this is a ticket-related operation
            if operation in ["classify_ticket", "resolve_ticket", "execute_desktop_command"]:
                if status == "success":
                    tickets_processed_total.labels(status="success").inc()
                else:
                    tickets_failed_total.inc()

        return {
            "agent": agent_name,
            "operation": operation,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

    except Exception as e:
        # Track error
        if PROMETHEUS_AVAILABLE:
            agent_requests_total.labels(
                agent_name=agent_name,
                status="error"
            ).inc()

            # Track failed tickets
            operation = payload.get("operation", "unknown")
            if operation in ["classify_ticket", "resolve_ticket", "execute_desktop_command"]:
                tickets_failed_total.inc()

        logger.error(f"Error executing {agent_name}: {str(e)}")
        return {
            "agent": agent_name,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


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
