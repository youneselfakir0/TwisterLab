#!/usr/bin/env python3
"""
TwisterLab API Server Launcher
"""

import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting TwisterLab API Server...")

try:
    from agents.api.main import app
    import uvicorn

    logger.info("Application imported successfully")
    logger.info("Starting uvicorn server...")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

except Exception as e:
    logger.error(f"Failed to start server: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)