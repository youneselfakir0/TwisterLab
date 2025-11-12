"""
TwisterLab MCP API Routes - Real Agent Endpoints
Production-ready FastAPI routes for MCP tool integration
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
import time

# Import database layer
from agents.core.database import get_db_session
from agents.core.repository import TicketRepository, AgentLogRepository, SystemMetricsRepository
from agents.core.models import TicketPriority

# Import real agents
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_backup_agent import RealBackupAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router (prefix is defined in api/main.py, not here)
router = APIRouter(tags=["mcp-tools"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class MCPResponse(BaseModel):
    """Standard MCP response format."""
    status: str = Field(..., pattern="^(ok|error)$")
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# REGISTRY ENDPOINT - List All Agents
# ============================================================================

@router.post("/list_autonomous_agents", response_model=MCPResponse)
@router.get("/list_autonomous_agents", response_model=MCPResponse)
async def list_autonomous_agents() -> MCPResponse:
    """
    List all 7 real autonomous agents with metadata.
    
    Returns:
        MCPResponse with agent registry data
    """
    try:
        agents_data = {
            "version": "2.0.0",
            "total": 7,
            "base_class": "agents.base.TwisterAgent",
            "agents": [
                {
                    "name": "RealMonitoringAgent",
                    "module": "agents.real.real_monitoring_agent",
                    "file": "agents/real/real_monitoring_agent.py",
                    "mcp_tool": "monitor_system_health",
                    "description": "System health monitoring (CPU, RAM, disk, Docker services)",
                    "capabilities": ["cpu_monitoring", "ram_monitoring", "disk_monitoring", "docker_health"],
                    "status": "operational"
                },
                {
                    "name": "RealBackupAgent",
                    "module": "agents.real.real_backup_agent",
                    "file": "agents/real/real_backup_agent.py",
                    "mcp_tool": "create_backup",
                    "description": "Automated backups with disaster recovery (PostgreSQL, Redis, configs)",
                    "capabilities": ["postgres_backup", "redis_backup", "config_backup", "incremental_backup"],
                    "status": "operational"
                },
                {
                    "name": "RealSyncAgent",
                    "module": "agents.real.real_sync_agent",
                    "file": "agents/real/real_sync_agent.py",
                    "mcp_tool": "sync_cache",
                    "description": "Cache/Database synchronization (Redis ↔ PostgreSQL)",
                    "capabilities": ["redis_sync", "postgres_sync", "conflict_resolution"],
                    "status": "operational"
                },
                {
                    "name": "RealClassifierAgent",
                    "module": "agents.real.real_classifier_agent",
                    "file": "agents/real/real_classifier_agent.py",
                    "mcp_tool": "classify_ticket",
                    "description": "Ticket classification using Ollama LLM (llama3.2:1b)",
                    "capabilities": ["llm_classification", "confidence_scoring", "priority_assignment"],
                    "categories": ["network", "hardware", "software", "account", "email"],
                    "status": "operational"
                },
                {
                    "name": "RealResolverAgent",
                    "module": "agents.real.real_resolver_agent",
                    "file": "agents/real/real_resolver_agent.py",
                    "mcp_tool": "resolve_ticket",
                    "description": "SOP-based ticket resolution (network, hardware, software, account, email)",
                    "capabilities": ["sop_execution", "troubleshooting", "guided_resolution"],
                    "status": "operational"
                },
                {
                    "name": "RealDesktopCommanderAgent",
                    "module": "agents.real.real_desktop_commander_agent",
                    "file": "agents/real/real_desktop_commander_agent.py",
                    "mcp_tool": "execute_desktop_command",
                    "description": "Remote system command execution (PowerShell, Bash, SSH)",
                    "capabilities": ["powershell_execution", "bash_execution", "ssh_commands", "command_whitelisting"],
                    "status": "operational",
                    "security": "whitelisted_commands_only"
                },
                {
                    "name": "RealMaestroAgent",
                    "module": "agents.real.real_maestro_agent",
                    "file": "agents/real/real_maestro_agent.py",
                    "mcp_tool": None,
                    "description": "Workflow orchestration and load balancing (agent coordination)",
                    "capabilities": ["workflow_orchestration", "load_balancing", "state_persistence", "error_recovery"],
                    "status": "operational"
                }
            ],
            "infrastructure": {
                "database": "PostgreSQL 16",
                "cache": "Redis 7",
                "llm": "Ollama (llama3.2:1b, llama3:latest)",
                "deployment": "Docker Swarm",
                "monitoring": "Prometheus + Grafana"
            },
            "api_base": "http://192.168.0.30:8000",
            "mcp_protocol": "2024-11-05"
        }
        
        logger.info("list_autonomous_agents called - returning 7 agents")
        return MCPResponse(status="ok", data=agents_data)
    
    except Exception as e:
        logger.error(f"Error in list_autonomous_agents: {e}", exc_info=True)
        return MCPResponse(status="error", error=str(e))


# ============================================================================
# PYDANTIC MODELS - Input Validation
# ============================================================================

class ClassifyTicketRequest(BaseModel):
    """Input model for classify_ticket endpoint."""
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Ticket description (min 10 chars)"
    )
    priority: Optional[str] = Field(
        None,
        pattern="^(critical|high|medium|low)$",
        description="Optional manual priority override"
    )
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()


class ResolveTicketRequest(BaseModel):
    """Input model for resolve_ticket endpoint."""
    ticket_id: Optional[int] = Field(
        None,
        gt=0,
        description="Ticket ID (optional)"
    )
    category: str = Field(
        ...,
        pattern="^(network|software|hardware|security|performance|database)$",
        description="Ticket category"
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Ticket description for context"
    )


class MonitorSystemHealthRequest(BaseModel):
    """Input model for monitor_system_health endpoint."""
    detailed: Optional[bool] = Field(
        False,
        description="Return detailed metrics (CPU, RAM, disk, services)"
    )


class CreateBackupRequest(BaseModel):
    """Input model for create_backup endpoint."""
    backup_type: str = Field(
        "full",
        pattern="^(full|incremental|config)$",
        description="Backup type"
    )


# ============================================================================
# ENDPOINTS - MCP Tool Routes
# ============================================================================

@router.post("/classify_ticket", response_model=MCPResponse)
async def classify_ticket(
    request: ClassifyTicketRequest,
    session: Optional[AsyncSession] = Depends(get_db_session)
) -> MCPResponse:
    """
    Classify a helpdesk ticket using RealClassifierAgent.
    
    **Database Integration**: Creates ticket record and logs execution (graceful fallback if DB down).
    
    **Input**:
    - `description`: Ticket description (10-5000 chars)
    - `priority`: Optional priority override (critical|high|medium|low)
    
    **Output**:
    - `status`: "ok" or "error"
    - `data`: Classification results + ticket_id from database (if available)
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
            "method": "llm",
            "ticket_id": 123
        },
        "error": null,
        "timestamp": "2025-11-11T12:00:00.000000+00:00"
    }
    ```
    """
    ticket_id = None
    try:
        logger.info(f"🔍 Classifying ticket: {request.description[:50]}...")
        start_time = time.time()
        
        # 1. Try to save to database (with fallback if DB is down)
        if session:
            try:
                ticket_repo = TicketRepository(session)
                log_repo = AgentLogRepository(session)
                
                # Create ticket in database
                priority_enum = TicketPriority(request.priority) if request.priority else TicketPriority.MEDIUM
                ticket_db = await ticket_repo.create(
                    description=request.description,
                    priority=priority_enum
                )
                ticket_id = ticket_db.id
                logger.info(f"✅ Ticket saved to database: ticket_id={ticket_id}")
            except Exception as db_error:
                logger.warning(f"⚠️ Database unavailable, continuing without persistence: {db_error}")
                session = None  # Disable DB for rest of request
        else:
            logger.warning("⚠️ Database session not available, classification will not be persisted")
        
        # 2. Initialize agent
        agent = RealClassifierAgent()
        
        # Build ticket context
        ticket = {
            "id": ticket_id,  # Include DB ticket ID if available
            "description": request.description,
            "title": request.description[:100],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 3. Execute classification
        result = await agent.execute({
            "operation": "classify_ticket",
            "ticket": ticket
        })
        
        # Check if classification succeeded
        if result.get("status") != "success":
            error_msg = result.get("error", "Unknown error")
            logger.error(f"❌ Classification failed: {error_msg}")
            
            # Try to log failure to database
            if session and ticket_id:
                try:
                    await log_repo.log_execution(
                        agent_name="RealClassifierAgent",
                        action="classify_ticket",
                        ticket_id=ticket_id,
                        error=error_msg
                    )
                    await session.commit()
                except Exception as log_error:
                    logger.warning(f"⚠️ Failed to log error to database: {log_error}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Classification failed: {error_msg}"
            )
        
        # Extract classification data
        classification = result.get("classification", {})
        
        # Override priority if provided
        if request.priority:
            classification["priority"] = request.priority
        
        # 4. Update database (if available)
        execution_time_ms = int((time.time() - start_time) * 1000)
        if session and ticket_id:
            try:
                category = classification.get("category", "unknown")
                await ticket_repo.update_category(ticket_id, category)
                
                # Log successful execution
                await log_repo.log_execution(
                    agent_name="RealClassifierAgent",
                    action="classify_ticket",
                    ticket_id=ticket_id,
                    result=classification,
                    execution_time_ms=execution_time_ms
                )
                
                # Commit transaction
                await session.commit()
                logger.info(f"✅ Database updated: category={category}, execution_time={execution_time_ms}ms")
            except Exception as db_error:
                logger.warning(f"⚠️ Failed to update database: {db_error}")
                # Continue anyway - classification succeeded even if DB update failed
        
        logger.info(
            f"✅ Classification complete: {classification.get('category')} "
            f"(confidence: {classification.get('confidence')}) "
            f"[ticket_id={ticket_id}, {execution_time_ms}ms]"
        )
        
        return MCPResponse(
            status="ok",
            data={
                **classification,
                "ticket_id": ticket_id,  # Will be None if DB is down
                "execution_time_ms": execution_time_ms,
                "database_persisted": ticket_id is not None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ classify_ticket failed: {e}", exc_info=True)
        return MCPResponse(
            status="error",
            error=str(e)
        )


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
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Execute resolution
        result = await agent.execute({
            "operation": "resolve_ticket",
            "ticket": ticket
        })
        
        # Check if resolution succeeded
        if result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resolution failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract resolution data
        resolution = result.get("resolution", {})
        
        logger.info(
            f"✅ Resolution complete: SOP {resolution.get('sop_id')} "
            f"({len(resolution.get('steps', []))} steps)"
        )
        
        return MCPResponse(
            status="ok",
            data=resolution
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ resolve_ticket failed: {e}", exc_info=True)
        return MCPResponse(
            status="error",
            error=str(e)
        )


@router.post("/monitor_system_health", response_model=MCPResponse)
async def monitor_system_health(
    request: MonitorHealthRequest,
    session: AsyncSession = Depends(get_db_session)
) -> MCPResponse:
    """
    Monitor system health using RealMonitoringAgent.
    
    **Input**:
    - `detailed`: Return detailed metrics (default: false)
    
    **Output**:
    - `status`: "ok" or "error"
    - `data`: System health metrics (CPU, RAM, disk, services, ports)
    - `error`: Error message if status="error"
    
    **Example**:
    ```json
    POST /v1/mcp/tools/monitor_system_health
    {
        "detailed": true
    }
    
    Response:
    {
        "status": "ok",
        "data": {
            "overall_status": "healthy",
            "cpu_percent": 45.2,
            "memory_percent": 62.1,
            "disk_percent": 38.5,
            "services": {
                "twisterlab_api": "running",
                "twisterlab_postgres": "running",
                "twisterlab_redis": "running"
            },
            "alerts": [],
            "uptime_hours": 168.5
        },
        "error": null,
        "timestamp": "2025-11-11T12:00:00.000000+00:00"
    }
    ```
    """
    try:
        logger.info(f"🏥 Monitoring system health (detailed: {request.detailed})")
        start_time = time.time()
        
        # Initialize repositories
        metrics_repo = SystemMetricsRepository(session)
        log_repo = AgentLogRepository(session)
        
        # Initialize agent
        agent = RealMonitoringAgent()
        
        # Execute health check
        result = await agent.execute({
            "operation": "health_check",
            "detailed": request.detailed
        })
        
        # Check if health check succeeded
        if result.get("status") != "success":
            # Log failure
            await log_repo.log_execution(
                agent_name="RealMonitoringAgent",
                action="health_check",
                error=result.get("error", "Unknown error")
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Health check failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract health data
        health_data = result.get("health_check", {})
        health_data["overall_status"] = result.get("health_status", "unknown")
        health_data["issues"] = result.get("issues", [])
        
        # Record metrics in database
        cpu = health_data.get("cpu_percent", 0.0)
        memory = health_data.get("memory_percent", 0.0)
        disk = health_data.get("disk_percent", 0.0)
        docker_status = health_data.get("overall_status", "unknown")
        
        await metrics_repo.record_metrics(
            cpu_usage=cpu,
            memory_usage=memory,
            disk_usage=disk,
            docker_status=docker_status
        )
        
        # Log execution
        execution_time_ms = int((time.time() - start_time) * 1000)
        await log_repo.log_execution(
            agent_name="RealMonitoringAgent",
            action="health_check",
            result={"status": docker_status, "cpu": cpu, "memory": memory, "disk": disk},
            execution_time_ms=execution_time_ms
        )
        
        # Commit transaction
        await session.commit()
        
        logger.info(
            f"✅ Health check complete: {docker_status} "
            f"(CPU: {cpu}%, RAM: {memory}%, Disk: {disk}%) [{execution_time_ms}ms]"
        )
        
        return MCPResponse(
            status="ok",
            data={
                **health_data,
                "execution_time_ms": execution_time_ms
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ monitor_system_health failed: {e}", exc_info=True)
        return MCPResponse(
            status="error",
            error=str(e)
        )


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
        result = await agent.execute({
            "operation": "create_backup",
            "backup_type": request.backup_type
        })
        
        # Check if backup succeeded
        if result.get("status") not in ["success", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Backup failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract backup data
        backup = result.get("backup", result)  # Handle different response formats
        
        logger.info(
            f"✅ Backup complete: {backup.get('backup_id')} "
            f"({backup.get('size_mb', 0)}MB in {backup.get('duration_seconds', 0)}s)"
        )
        
        return MCPResponse(
            status="ok",
            data=backup
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ create_backup failed: {e}", exc_info=True)
        return MCPResponse(
            status="error",
            error=str(e)
        )


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
            "create_backup"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
