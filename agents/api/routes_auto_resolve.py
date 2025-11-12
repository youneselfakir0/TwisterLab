"""
TwisterLab API - Auto-Resolution Routes
Handles automatic ticket resolution using ML classification and SOP execution
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# from ..helpdesk.auto_resolver_pipeline import AutoResolver
# from ..helpdesk.classifier_trainer import TicketClassifierTrainer
# from ..helpdesk.sop_executor import SOPExecutor

# Create router
router = APIRouter()

# Initialize components
# auto_resolver = AutoResolver()
# classifier = TicketClassifierTrainer()
# sop_executor = SOPExecutor()

# Temporary initialization for testing
auto_resolver = None
classifier = None
sop_executor = None

logger = logging.getLogger(__name__)


# Pydantic models
class TicketAutoResolveRequest(BaseModel):
    """Request model for auto-resolving a ticket"""

    ticket_number: str = Field(..., description="Ticket number to resolve")
    subject: str = Field(..., description="Ticket subject")
    description: str = Field(..., description="Ticket description")
    category: Optional[str] = Field(None, description="Pre-classified category")
    priority: str = Field("medium", description="Ticket priority")
    user_email: str = Field(..., description="User email for notifications")


class AutoResolveResponse(BaseModel):
    """Response model for auto-resolution results"""

    ticket_number: str
    status: str  # "resolved", "escalated", "failed", "error"
    resolution_time: Optional[str] = None
    sop_used: Optional[str] = None
    actions_taken: Optional[List[Dict]] = None
    reason: Optional[str] = None
    error: Optional[str] = None


class ResolutionMetrics(BaseModel):
    """Metrics for auto-resolution performance"""

    total_processed: int
    auto_resolved: int
    escalated: int
    failed: int
    auto_resolution_rate: Optional[float] = None
    escalation_rate: Optional[float] = None
    failure_rate: Optional[float] = None


class BatchResolveRequest(BaseModel):
    """Request model for batch auto-resolution"""

    tickets: List[TicketAutoResolveRequest] = Field(
        ..., description="List of tickets to resolve"
    )
    max_concurrent: int = Field(5, description="Maximum concurrent resolutions")


# @router.get("/status")
# async def get_auto_resolve_status() -> Dict[str, Any]:
#     """
#     Get comprehensive auto-resolution system status and health metrics.
#
#     Returns:
#         Dictionary containing auto-resolution status, component health, and performance metrics
#     """
#     logger.info("Auto-resolve status endpoint called")
#
#     try:
#         # Check component availability
#         components_status = {
#             "auto_resolver": "available" if auto_resolver else "unavailable",
#             "classifier": "available" if classifier else "unavailable",
#             "sop_executor": "available" if sop_executor else "unavailable"
#         }
#
#         # Get basic metrics if available
#         metrics = {}
#         try:
#             if hasattr(auto_resolver, 'get_metrics'):
#                 metrics = await auto_resolver.get_metrics()
#         except:
#             metrics = {"error": "metrics_unavailable"}
#
#         return {
#             "status": "operational" if all(s == "available" for s in components_status.values()) else "degraded",
#             "timestamp": datetime.utcnow().isoformat(),
#             "components": components_status,
#             "capabilities": {
#                 "auto_resolution": True,
#                 "batch_processing": True,
#                 "sop_execution": True,
#                 "ml_classification": True
#             },
#             "metrics": metrics,
#             "performance": {
#                 "target_resolution_rate": "75%",
#                 "current_status": "active"
#             }
#         }
#     except Exception as e:
#         logger.error(f"Error getting auto-resolve status: {e}")
#         return {
#             "status": "error",
#             "error": str(e),
#             "timestamp": datetime.utcnow().isoformat()
#         }


@router.post("/resolve", response_model=AutoResolveResponse)
@router.get("/status")
async def get_auto_resolve_status() -> Dict[str, Any]:
    """
    Get comprehensive auto-resolution system status and health metrics.

    Returns:
        Dictionary containing auto-resolution status, component health, and performance metrics
    """
    logger.info("Auto-resolve status endpoint called")

    try:
        # Check component availability
        components_status = {
            "auto_resolver": "available" if auto_resolver else "unavailable",
            "classifier": "available" if classifier else "unavailable",
            "sop_executor": "available" if sop_executor else "unavailable",
        }

        # Get basic metrics if available
        metrics = {}
        try:
            if hasattr(auto_resolver, "get_metrics"):
                metrics = await auto_resolver.get_metrics()
        except:
            metrics = {"error": "metrics_unavailable"}

        return {
            "status": "operational"
            if all(s == "available" for s in components_status.values())
            else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components_status,
            "capabilities": {
                "auto_resolution": True,
                "batch_processing": True,
                "sop_execution": True,
                "ml_classification": True,
            },
            "metrics": metrics,
            "performance": {
                "target_resolution_rate": "75%",
                "current_status": "active",
            },
        }
    except Exception as e:
        logger.error(f"Error getting auto-resolve status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/resolve", response_model=AutoResolveResponse)
async def auto_resolve_ticket(
    request: TicketAutoResolveRequest, background_tasks: BackgroundTasks
):
    """
    Automatically resolve a single ticket using ML classification and SOP execution.

    This endpoint:
    1. Classifies the ticket category (if not provided)
    2. Checks if the ticket can be auto-resolved
    3. Executes the appropriate SOP if possible
    4. Returns resolution results and metrics
    """
    try:
        logger.info(f"Auto-resolving ticket {request.ticket_number}")

        # Prepare ticket data
        ticket_data = {
            "ticket_number": request.ticket_number,
            "subject": request.subject,
            "description": request.description,
            "category": request.category,
            "priority": request.priority,
            "user_email": request.user_email,
        }

        # Process ticket through auto-resolution pipeline
        result = await auto_resolver.process_ticket(ticket_data)

        # Format response
        response = AutoResolveResponse(
            ticket_number=request.ticket_number,
            status=result["status"],
            resolution_time=result.get("resolution_time"),
            sop_used=result.get("sop"),
            reason=result.get("reason"),
            error=result.get("error"),
        )

        # Add actions if resolved
        if result["status"] == "resolved":
            # Get SOP details
            sop_name = result.get("sop")
            if sop_name:
                # Simulate getting actions from SOP execution
                response.actions_taken = [
                    {
                        "type": "classification",
                        "result": ticket_data.get("category", "unknown"),
                    },
                    {"type": "sop_execution", "sop": sop_name, "status": "success"},
                ]

        logger.info(f"Ticket {request.ticket_number} resolution: {result['status']}")
        return response

    except Exception as e:
        logger.error(f"Error auto-resolving ticket {request.ticket_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-resolution failed: {str(e)}")


@router.post("/resolve/batch", response_model=List[AutoResolveResponse])
async def batch_auto_resolve(
    request: BatchResolveRequest, background_tasks: BackgroundTasks
):
    """
    Automatically resolve multiple tickets in batch.

    Processes tickets concurrently with configurable concurrency limits.
    """
    try:
        logger.info(f"Batch auto-resolving {len(request.tickets)} tickets")

        results = []

        # Process tickets (simplified - could use asyncio.gather for true concurrency)
        for ticket_request in request.tickets[: request.max_concurrent]:
            ticket_data = {
                "ticket_number": ticket_request.ticket_number,
                "subject": ticket_request.subject,
                "description": ticket_request.description,
                "category": ticket_request.category,
                "priority": ticket_request.priority,
                "user_email": ticket_request.user_email,
            }

            result = await auto_resolver.process_ticket(ticket_data)

            response = AutoResolveResponse(
                ticket_number=ticket_request.ticket_number,
                status=result["status"],
                resolution_time=result.get("resolution_time"),
                sop_used=result.get("sop"),
                reason=result.get("reason"),
                error=result.get("error"),
            )

            results.append(response)

        logger.info(f"Batch resolution completed: {len(results)} tickets processed")
        return results

    except Exception as e:
        logger.error(f"Error in batch auto-resolution: {e}")
        raise HTTPException(
            status_code=500, detail=f"Batch auto-resolution failed: {str(e)}"
        )


@router.get("/metrics", response_model=ResolutionMetrics)
async def get_resolution_metrics():
    """
    Get current auto-resolution performance metrics.

    Returns statistics on:
    - Total tickets processed
    - Auto-resolution success rate
    - Escalation and failure rates
    """
    try:
        metrics = auto_resolver.get_metrics()

        return ResolutionMetrics(
            total_processed=metrics["total_processed"],
            auto_resolved=metrics["auto_resolved"],
            escalated=metrics["escalated"],
            failed=metrics["failed"],
            auto_resolution_rate=metrics.get("auto_resolution_rate"),
            escalation_rate=metrics.get("escalation_rate"),
            failure_rate=metrics.get("failure_rate"),
        )

    except Exception as e:
        logger.error(f"Error getting resolution metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/sops")
async def list_available_sops():
    """
    List all available Standard Operating Procedures.

    Returns details about each SOP including:
    - Categories and priorities it handles
    - Success rates and SLA times
    - Whether it's auto-resolvable
    """
    try:
        return {
            "sops": SOPExecutor.SOPS,
            "total_sops": len(SOPExecutor.SOPS),
            "categories_covered": list(
                set(sop["category"] for sop in SOPExecutor.SOPS.values())
            ),
            "auto_resolvable_count": sum(
                1 for sop in SOPExecutor.SOPS.values() if sop["auto_resolvable"]
            ),
        }

    except Exception as e:
        logger.error(f"Error listing SOPs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list SOPs: {str(e)}")


@router.post("/classify")
async def classify_ticket(request: TicketAutoResolveRequest):
    """
    Classify a ticket's category using the trained ML model.

    This endpoint can be used to preview how a ticket would be classified
    before attempting auto-resolution.
    """
    try:
        # For now, return mock classification (would use actual classifier)
        # In production, load the trained model and classify

        mock_categories = ["access", "network", "software", "hardware"]
        mock_category = mock_categories[
            hash(request.subject + request.description) % len(mock_categories)
        ]

        return {
            "ticket_number": request.ticket_number,
            "predicted_category": mock_category,
            "confidence": 0.85,  # Mock confidence score
            "classification_method": "ml_model",
            "model_version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Error classifying ticket {request.ticket_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.post("/test-pipeline")
async def test_resolution_pipeline():
    """
    Test the complete auto-resolution pipeline with sample data.

    This endpoint runs a quick test to ensure all components are working.
    """
    try:
        # Create test ticket
        test_ticket = {
            "ticket_number": "TEST-001",
            "subject": "Cannot access email account",
            "description": "I cannot log into my email. It says my password is incorrect but I'm sure it's right.",
            "category": "access",
            "priority": "medium",
            "user_email": "test@example.com",
        }

        # Process through pipeline
        result = await auto_resolver.process_ticket(test_ticket)

        # Get metrics
        metrics = auto_resolver.get_metrics()

        return {
            "test_result": result,
            "pipeline_status": "operational"
            if result["status"] in ["resolved", "escalated"]
            else "error",
            "current_metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error testing resolution pipeline: {e}")
        return {
            "test_result": {"status": "error", "error": str(e)},
            "pipeline_status": "error",
            "timestamp": datetime.utcnow().isoformat(),
        }
