#!/usr/bin/env python3
"""
TwisterLab API Server with detailed error handling
"""

import logging
import os
import sys
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("api_debug.log")],
)
logger = logging.getLogger(__name__)


def main():
    """Main function with comprehensive error handling"""
    logger.info("🚀 Starting TwisterLab API Server with debug logging...")

    try:
        # Test imports first
        logger.info("📦 Testing imports...")
        from agents.api.main import app

        logger.info("✅ Application imported successfully")

        # Test database connection
        logger.info("🗄️ Testing database connection...")
        import asyncio

        from agents.database.config import async_session

        async def test_db():
            async with async_session() as session:
                from sqlalchemy import text

                result = await session.execute(text("SELECT 1"))
                return result.scalar()

        result = asyncio.run(test_db())
        logger.info(f"✅ Database connection successful: {result}")

        # Start server
        logger.info("🌐 Starting uvicorn server...")
        import uvicorn

        # Configure uvicorn with more detailed logging
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="debug",
            access_log=True,
            server_header=False,
            date_header=False,
        )

    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
