"""
TwisterLab API - FastAPI Application
AI-powered IT Helpdesk automation platform
"""

import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from .routes_tickets import router as tickets_router
from .routes_agents import router as agents_router
from .routes_sops import router as sops_router
from .routes_orchestrator import router as orchestrator_router
from .routes_mcp_real import router as mcp_real_router
from .monitoring import setup_logging, MetricsMiddleware, create_health_endpoint
from .security import (
    setup_security_middleware,
    create_access_token,
    create_default_admin,
    UserCredentials,
    TokenResponse,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from fastapi import HTTPException, status

# Configure structured logging for production
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/twisterlab.log")
logger = setup_logging(log_level=log_level, log_file=log_file)

logger.info("Creating FastAPI application...")

# Create FastAPI application
app = FastAPI(
    title="TwisterLab API",
    description="AI-powered IT Helpdesk automation platform",
    version="1.0.0-alpha.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add monitoring middleware
logger.info("Adding monitoring middleware...")
app.add_middleware(MetricsMiddleware, logger=logger)
logger.info("Monitoring middleware added")

# Add security middleware
logger.info("Adding security middleware...")
setup_security_middleware(app)
logger.info("Security middleware added")

logger.info("FastAPI application created successfully")

# Include routers
logger.info("Including routers...")
app.include_router(tickets_router, prefix="/api/v1/tickets", tags=["tickets"])
logger.info("Tickets router included")
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
logger.info("Agents router included")
app.include_router(sops_router, prefix="/api/v1/sops", tags=["sops"])
logger.info("SOPs router included")
app.include_router(orchestrator_router, prefix="/api/v1/orchestrator", tags=["orchestrator"])
logger.info("Orchestrator router included")
app.include_router(mcp_real_router)  # MCP tools router (already has /v1/mcp/tools prefix)
logger.info("MCP tools router included")


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    logger.info("Root endpoint called")
    return {
        "name": "TwisterLab API",
        "description": "AI-powered IT Helpdesk automation platform",
        "version": "1.0.0-alpha.1",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    logger.info("Health check endpoint called")
    return await create_health_endpoint()()
@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserCredentials):
    """Authenticate user and return access token."""
    logger.info(f"Login attempt for user: {credentials.username}")

    # For development, use default admin credentials
    admin_data = create_default_admin()

    if (credentials.username == admin_data["username"] and
        verify_password(credentials.password, admin_data["password_hash"])):

        token_data = {
            "sub": credentials.username,
            "roles": admin_data["roles"],
            "permissions": admin_data["permissions"]
        }

        access_token = create_access_token(data=token_data)
        logger.info(f"Login successful for user: {credentials.username}")

        return TokenResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    else:
        logger.warning(f"Login failed for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

logger.info("Routes registered successfully")

# Prometheus metrics endpoint
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY

    @app.get("/metrics", response_class=PlainTextResponse)
    async def metrics() -> PlainTextResponse:
        """Prometheus metrics endpoint."""
        logger.info("Metrics endpoint called")
        data = generate_latest(REGISTRY)
        return PlainTextResponse(content=data, media_type=CONTENT_TYPE_LATEST)
except Exception:
    logger.warning("prometheus_client not available; /metrics endpoint not enabled")

if __name__ == "__main__":
    logger.info("Starting server with uvicorn...")
    import uvicorn
    uvicorn.run(
        "agents.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
