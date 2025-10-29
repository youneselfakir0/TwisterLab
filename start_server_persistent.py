#!/usr/bin/env python3
"""
TwisterLab API Server - Persistent version
"""

import logging
import sys
import threading
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging (without Unicode characters)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('api_server.log')
    ]
)
logger = logging.getLogger(__name__)

def keep_alive():
    """Keep the main thread alive"""
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")

def main():
    """Main function"""
    logger.info("Starting TwisterLab API Server...")

    try:
        # Import the app
        from agents.api.main import app
        logger.info("Application imported successfully")

        # Start server in a separate thread
        import uvicorn
        from uvicorn import Config, Server

        config = Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True
        )

        server = Server(config)

        # Start server in background thread
        server_thread = threading.Thread(target=server.run)
        server_thread.daemon = True
        server_thread.start()

        logger.info("Server started successfully on http://127.0.0.1:8000")
        logger.info("Press Ctrl+C to stop")

        # Keep main thread alive
        keep_alive()

    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        if 'server' in locals():
            server.should_exit = True
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()