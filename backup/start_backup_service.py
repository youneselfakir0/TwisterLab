"""
TwisterLab Backup Service Startup Script
Starts the automated backup system as a background service
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backup.automated_backup import AutomatedBackup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/backup_service.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def start_backup_service():
    """Start the backup service."""
    logger.info("Starting TwisterLab Backup Service...")

    try:
        # Initialize backup system
        backup_system = AutomatedBackup()

        # Validate configuration
        from backup.backup_config import validate_config

        config_errors = validate_config()
        if config_errors:
            logger.error("Configuration validation failed:")
            for error in config_errors:
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Configuration validated successfully")

        # Start the scheduler
        await backup_system.start_scheduler()

    except KeyboardInterrupt:
        logger.info("Backup service stopped by user")
    except Exception as e:
        logger.error(f"Backup service failed: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point."""
    # Ensure directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # Run the backup service
    asyncio.run(start_backup_service())


if __name__ == "__main__":
    main()
