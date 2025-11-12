
@app.post("/api/v1/tickets/process")
async def process_ticket_workflow(payload: Dict[str, Any]):
    """
    Process a ticket through complete workflow:
    ClassifierAgent -> ResolverAgent/DesktopCommanderAgent

    Payload should contain ticket data:
    {
        "ticket_id": "T-001",
        "title": "Cannot connect to WiFi",
        "description": "WiFi connection keeps dropping",
        "category": "network" (optional - will be auto-detected),
        "priority": "high" (optional - will be auto-detected)
    }
    """
    import time
    start_time = time.time()

    try:
        # Get orchestrator instance
        orchestrator = await get_orchestrator()

        # Extract ticket data
        ticket = payload.get("ticket", payload)  # Support both formats

        logger.info(f"🎫 Processing ticket workflow for: {ticket.get('ticket_id', 'Unknown')}")

        # Execute complete workflow
        result = await orchestrator.process_ticket_workflow(ticket)

        duration = time.time() - start_time

        # Record metrics if available
        if PROMETHEUS_AVAILABLE:
            http_requests_total.labels(
                method="POST",
                endpoint="/api/v1/tickets/process",
                status="success" if result.get("status") == "success" else "error"
            ).inc()

            http_request_duration_seconds.labels(
                method="POST",
                endpoint="/api/v1/tickets/process"
            ).observe(duration)

        logger.info(f"✅ Workflow completed in {duration:.2f}s: {result.get('status')}")

        return {
            "status": result.get("status"),
            "ticket_id": result.get("ticket_id"),
            "workflow_results": result,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Workflow processing failed: {e}", exc_info=True)

        if PROMETHEUS_AVAILABLE:
            http_requests_total.labels(
                method="POST",
                endpoint="/api/v1/tickets/process",
                status="error"
            ).inc()

        raise HTTPException(
            status_code=500,
            detail=f"Workflow processing failed: {str(e)}"
        )
