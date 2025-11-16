#!/usr/bin/env python3
"""
TwisterLab Autonomous Agents Service

Standalone service for running autonomous agents with orchestration.
Can be run as a separate service or integrated into the main API.
"""

import asyncio
import logging
import os
import signal
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.orchestrator.autonomous_orchestrator import (
    get_orchestrator,
    start_autonomous_agents,
    stop_autonomous_agents,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/autonomous_agents.log", mode="a", encoding="utf-8"),
    ],
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

# Global shutdown event
shutdown_event = asyncio.Event()


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    shutdown_event.set()


async def run_autonomous_agents_service():
    """Run the autonomous agents service."""
    logger.info("🤖 Starting TwisterLab Autonomous Agents Service")
    logger.info("=" * 60)

    try:
        # Start autonomous agents
        await start_autonomous_agents()
        logger.info("✅ Autonomous agents started successfully")

        # Get orchestrator for status monitoring
        orchestrator = await get_orchestrator()

        # Main service loop
        while not shutdown_event.is_set():
            try:
                # Log status every 5 minutes
                status = orchestrator.get_system_status()
                logger.info(
                    f"📊 System Status: {status['status']} | "
                    f"Agents: {status['healthy_agents']}/{status['agents_count']} healthy | "
                    f"Tasks: {status['scheduled_tasks_count']} scheduled"
                )

                # Check for critical issues
                if status["healthy_agents"] < status["agents_count"]:
                    logger.warning(
                        f"⚠️  Some agents unhealthy: {status['healthy_agents']}/{status['agents_count']}"
                    )

                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Status check error: {str(e)}")
                await asyncio.sleep(60)  # Retry in 1 minute

    except Exception as e:
        logger.error(f"❌ Failed to start autonomous agents: {str(e)}")
        raise

    finally:
        # Graceful shutdown
        logger.info("🛑 Shutting down autonomous agents service...")
        try:
            await stop_autonomous_agents()
            logger.info("✅ Autonomous agents stopped successfully")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")


async def run_with_api_integration():
    """Run autonomous agents integrated with the FastAPI server."""
    logger.info("🚀 Starting autonomous agents with API integration")

    # Import here to avoid circular imports
    import uvicorn

    from agents.api.main import app

    # Start autonomous agents
    await start_autonomous_agents()
    logger.info("✅ Autonomous agents integrated with API")

    # Configure uvicorn
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, reload=False, log_level="info")

    server = uvicorn.Server(config)

    # Run both server and agents
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        await stop_autonomous_agents()


def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="TwisterLab Autonomous Agents Service")
    parser.add_argument(
        "--with-api", action="store_true", help="Run with integrated FastAPI server"
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        default=True,
        help="Run as standalone autonomous agents service",
    )

    args = parser.parse_args()

    try:
        if args.with_api:
            logger.info("Starting with API integration...")
            asyncio.run(run_with_api_integration())
        else:
            logger.info("Starting standalone autonomous agents service...")
            asyncio.run(run_autonomous_agents_service())

    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
