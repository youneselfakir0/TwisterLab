#!/usr/bin/env python3
"""
TwisterLab API Server - Production Ready
"""

import logging
import signal
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global flag for shutdown
shutdown_event = False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown_event
    logger.info(f"Received signal {signum}, shutting down...")
    shutdown_event = True


def main():
    """Main function"""
    global shutdown_event

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting TwisterLab API Server...")

    try:
        # Import the app
        from agents.api.main import app

        logger.info("Application imported successfully")

        # Start server
        import uvicorn

        config = uvicorn.Config(
            app=app, host="0.0.0.0", port=8000, log_level="info", access_log=True, reload=False
        )
        server = uvicorn.Server(config)

        logger.info("Server starting on http://0.0.0.0:8000")
        logger.info("Press Ctrl+C to stop")

        # Start server (this will block until shutdown)
        server.run()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
