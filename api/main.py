import logging
import sys
from pathlib import Path
from fastapi import FastAPI

# Add project root to Python path to allow importing agents package
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import routers from the new modular structure
from api.routes import system, agents

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create the main FastAPI app instance
app = FastAPI(
    title="TwisterLab Autonomous Agents API v2",
    description="API for the TwisterLab v2 'Living IT System' ecosystem.",
    version="2.0.0",
)

# Include the routers from the separate modules
app.include_router(system.router)
app.include_router(agents.router)

logger.info("FastAPI application created and routers included.")
logger.info("System router loaded with endpoints: /health, /token, /metrics")
logger.info("Agents router loaded with endpoints: /api/v1/autonomous/agents/*")


# Main entry point for running the server directly
if __name__ == "__main__":
    import uvicorn

    try:
        logger.info("Starting TwisterLab API v2 server...")
        
        # The agent registry is automatically initialized on first import,
        # which happens when the routers are imported.
        
        uvicorn.run(app, host="0.0.0.0", port=8000)

    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
