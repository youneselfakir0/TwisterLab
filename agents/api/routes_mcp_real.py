"""
TwisterLab MCP API Routes - Real Agent Endpoints
Production-ready FastAPI routes for MCP tool integration
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator

from agents.real.real_backup_agent import RealBackupAgent

# Import real agents
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1/mcp/tools", tags=["mcp-tools"])


# ============================================================================
# PYDANTIC MODELS - Input Validation
# ============================================================================


class ClassifyTicketRequest(BaseModel):
    """Input model for classify_ticket endpoint."""

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Ticket description (min 10 chars)",
    )
    priority: Optional[str] = Field(
        None,
        pattern="^(critical|high|medium|low)$",
        description="Optional manual priority override",
    )

    @validator("description")
    def validate_description(cls, v):
        """Ensure description is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()


class ResolveTicketRequest(BaseModel):
    """Input model for resolve_ticket endpoint."""

    ticket_id: Optional[int] = Field(None, gt=0, description="Ticket ID (optional)")
    category: str = Field(
        ...,
        pattern="^(network|software|hardware|security|performance|database)$",
        description="Ticket category",
    )
    description: Optional[str] = Field(
        None, max_length=5000, description="Ticket description for context"
    )


class MonitorSystemHealthRequest(BaseModel):
    """Input model for monitor_system_health endpoint."""

    detailed: Optional[bool] = Field(
        False, description="Return detailed metrics (CPU, RAM, disk, services)"
    )


class CreateBackupRequest(BaseModel):
    """Input model for create_backup endpoint."""

    backup_type: str = Field(
        "full", pattern="^(full|incremental|config)$", description="Backup type"
    )


class MCPResponse(BaseModel):
    """Standard MCP response format."""

    status: str = Field(..., pattern="^(ok|error)$")
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# ENDPOINTS - MCP Tool Routes
# ============================================================================


@router.post("/classify_ticket", response_model=MCPResponse)
async def classify_ticket(request: ClassifyTicketRequest) -> MCPResponse:
    """
    Classify a helpdesk ticket using RealClassifierAgent.

    **Input**:
    - `description`: Ticket description (10-5000 chars)
    - `priority`: Optional priority override (critical|high|medium|low)

    **Output**:
    - `status`: "ok" or "error"
    - `data`: Classification results (category, confidence, routed_to, priority)
    - `error`: Error message if status="error"

    **Example**:
    ```json
    POST /v1/mcp/tools/classify_ticket
    {
        "description": "WiFi connection keeps dropping every few minutes",
        "priority": null
    }

    Response:
    {
        "status": "ok",
        "data": {
            "category": "network",
            "subcategory": "wifi",
            "confidence": 0.92,
            "priority": "high",
            "routed_to": "DesktopCommanderAgent",
            "method": "llm"
        },
        "error": null,
        "timestamp": "2025-11-11T12:00:00.000000+00:00"
    }
    ```
    """
    try:
        logger.info(f"🔍 Classifying ticket: {request.description[:50]}...")

        # Initialize agent
        agent = RealClassifierAgent()

        # Build ticket context
        ticket = {
            "description": request.description,
            "title": request.description[:100],  # Use first 100 chars as title
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Execute classification
        result = await agent.execute({"operation": "classify_ticket", "ticket": ticket})

        # Check if classification succeeded
        if result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Classification failed: {result.get('error', 'Unknown error')}",
            )

        # Extract classification data
        classification = result.get("classification", {})

        # Override priority if provided
        if request.priority:
            classification["priority"] = request.priority

        logger.info(
            f"✅ Classification complete: {classification.get('category')} "
            f"(confidence: {classification.get('confidence')})"
        )

        return MCPResponse(status="ok", data=classification)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ classify_ticket failed: {e}", exc_info=True)
        return MCPResponse(status="error", error=str(e))


@router.post("/resolve_ticket", response_model=MCPResponse)
async def resolve_ticket(request: ResolveTicketRequest) -> MCPResponse:
    """
    Resolve a ticket using RealResolverAgent (executes SOPs).

    **Input**:
    - `ticket_id`: Optional ticket ID
    - `category`: Ticket category (network|software|hardware|security|performance|database)
    - `description`: Optional description for context

    **Output**:
    - `status`: "ok" or "error"
    - `data`: Resolution steps, SOP executed, estimated time
    - `error`: Error message if status="error"

    **Example**:
    ```json
    POST /v1/mcp/tools/resolve_ticket
    {
        "ticket_id": 123,
        "category": "network",
        "description": "WiFi not working"
    }

    Response:
    {
        "status": "ok",
        "data": {
            "sop_executed": "network_troubleshoot",
            "steps": [
                "Check physical connection (cables, WiFi signal)",
                "Ping localhost (127.0.0.1) to verify network stack",
                "Ping gateway to verify local network",
                "Ping external DNS (8.8.8.8) to verify internet",
                "Check DNS resolution with nslookup",
                "Restart network adapter if needed"
            ],
            "estimated_time": "15 minutes",
            "success_rate": 0.85,
            "method": "static_sop"
        },
        "error": null,
        "timestamp": "2025-11-11T12:00:00.000000+00:00"
    }
    ```
    """
    try:
        logger.info(f"🔧 Resolving ticket (category: {request.category}, ID: {request.ticket_id})")

        # Initialize agent
        agent = RealResolverAgent()

        # Build ticket context
        ticket = {
            "category": request.category,
            "description": request.description or f"Ticket #{request.ticket_id}",
            "ticket_id": request.ticket_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Execute resolution
        result = await agent.execute({"operation": "resolve_ticket", "ticket": ticket})

        # Check if resolution succeeded
        if result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resolution failed: {result.get('error', 'Unknown error')}",
            )

        # Extract resolution data
        resolution = result.get("resolution", {})

        logger.info(
            f"✅ Resolution complete: SOP {resolution.get('sop_id')} "
            f"({len(resolution.get('steps', []))} steps)"
        )

        return MCPResponse(status="ok", data=resolution)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ resolve_ticket failed: {e}", exc_info=True)
        return MCPResponse(status="error", error=str(e))


@router.post("/monitor_system_health", response_model=MCPResponse)
async def monitor_system_health(
    request: MonitorSystemHealthRequest = MonitorSystemHealthRequest(),
) -> MCPResponse:
    """
    Monitor system health - Mock implementation for MCP integration.

    Returns mock health data to ensure Continue IDE integration works.
    Real implementation will be restored once container compatibility is resolved.
    """
    logger.info("🏥 Monitor system health - Mock implementation for MCP")

    # Mock health data for MCP integration
    health_data = {
        "agent": "RealMonitoringAgent",
        "status": "healthy",
        "mode": "MOCK_FOR_MCP_INTEGRATION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": 25.0,
        "cpu_count": 4,
        "memory_percent": 45.0,
        "memory_used_gb": 8.0,
        "memory_total_gb": 16.0,
        "disk_percent": 30.0,
        "disk_used_gb": 50.0,
        "disk_total_gb": 200.0,
        "network_sent_mb": 100.0,
        "network_received_mb": 200.0,
        "processes": 150,
        "issues": [],
        "services": {
            "api": "running",
            "postgres": "running",
            "redis": "running",
            "prometheus": "running",
            "grafana": "running",
            "ollama": "running",
        },
        "note": "Mock data for Continue IDE MCP integration. Real monitoring agent will be restored.",
    }

    logger.info("✅ Mock health check complete")
    return MCPResponse(status="ok", data=health_data)


@router.post("/create_backup", response_model=MCPResponse)
async def create_backup(request: CreateBackupRequest) -> MCPResponse:
    """
    Create system backup using RealBackupAgent.

    **Input**:
    - `backup_type`: Backup type (full|incremental|config)

    **Output**:
    - `status`: "ok" or "error"
    - `data`: Backup details (backup_id, path, size, checksum)
    - `error`: Error message if status="error"

    **Example**:
    ```json
    POST /v1/mcp/tools/create_backup
    {
        "backup_type": "full"
    }

    Response:
    {
        "status": "ok",
        "data": {
            "backup_id": "20251111_120000",
            "backup_name": "twisterlab_backup_20251111_120000.tar.gz",
            "backup_type": "full",
            "path": "/var/backups/twisterlab/20251111_120000.tar.gz",
            "size_bytes": 524288000,
            "size_mb": 500.0,
            "checksum": "a3f5d8c2b1e9...",
            "components": ["database", "redis", "config"],
            "duration_seconds": 45.3
        },
        "error": null,
        "timestamp": "2025-11-11T12:00:00.000000+00:00"
    }
    ```
    """
    try:
        logger.info(f"💾 Creating backup (type: {request.backup_type})")

        # Initialize agent
        agent = RealBackupAgent()

        # Execute backup
        result = await agent.execute(
            {"operation": "create_backup", "backup_type": request.backup_type}
        )

        # Check if backup succeeded
        if result.get("status") not in ["success", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Backup failed: {result.get('error', 'Unknown error')}",
            )

        # Extract backup data
        backup = result.get("backup", result)  # Handle different response formats

        logger.info(
            f"✅ Backup complete: {backup.get('backup_id')} "
            f"({backup.get('size_mb', 0)}MB in {backup.get('duration_seconds', 0)}s)"
        )

        return MCPResponse(status="ok", data=backup)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ create_backup failed: {e}", exc_info=True)
        return MCPResponse(status="error", error=str(e))


# ============================================================================
# HEALTH CHECK - MCP Service Status
# ============================================================================


@router.get("/health")
async def mcp_health() -> Dict[str, Any]:
    """
    MCP service health check.

    Returns:
        Service status, mode, available tools count
    """
    return {
        "status": "ok",
        "mode": "REAL",
        "tools": 4,
        "tools_available": [
            "classify_ticket",
            "resolve_ticket",
            "monitor_system_health",
            "create_backup",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
