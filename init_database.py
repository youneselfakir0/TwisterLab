#!/usr/bin/env python3
"""
Initialize TwisterLab Database
Creates all tables defined in agents/core/models.py
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.core.database import close_db, init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """Initialize database tables"""
    try:
        logger.info("🚀 Starting database initialization...")
        logger.info("📊 Creating tables: tickets, agent_logs, system_metrics")

        await init_db()

        logger.info("✅ Database initialization complete!")
        logger.info("📋 Tables created successfully:")
        logger.info("   - tickets (IT support tickets)")
        logger.info("   - agent_logs (agent execution audit)")
        logger.info("   - system_metrics (system health monitoring)")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
