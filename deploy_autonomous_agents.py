#!/usr/bin/env python3
"""
TwisterLab Autonomous Agents Deployment Script
Handles deployment of autonomous agents service with health checks and monitoring.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutonomousAgentsDeployer:
    """Handles deployment of autonomous agents service."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.compose_file = self.project_root / "docker-compose.yml"
        self.health_check_url = "http://localhost:8001/autonomous/health"

    async def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        try:
            # Check Docker
            result = await asyncio.create_subprocess_exec(
                "docker",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()
            if result.returncode != 0:
                logger.error("Docker is not available")
                return False

            # Check Docker Compose
            result = await asyncio.create_subprocess_exec(
                "docker-compose",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()
            if result.returncode != 0:
                logger.error("Docker Compose is not available")
                return False

            logger.info("All dependencies are available")
            return True

        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False

    async def deploy_service(self) -> bool:
        """Deploy the autonomous agents service."""
        try:
            logger.info("Starting autonomous agents deployment...")

            # Build and start the service
            cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "up",
                "-d",
                "autonomous-agents",
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Deployment failed: {stderr.decode()}")
                return False

            logger.info("Autonomous agents service deployed successfully")
            return True

        except Exception as e:
            logger.error(f"Error during deployment: {e}")
            return False

    async def wait_for_health(self, timeout: int = 300) -> bool:
        """Wait for the service to become healthy."""
        import aiohttp

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < timeout:
                try:
                    async with session.get(
                        self.health_check_url, timeout=10
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("status") == "healthy":
                                logger.info("Autonomous agents service is healthy")
                                return True
                except Exception as e:
                    logger.debug(f"Health check failed: {e}")

                await asyncio.sleep(5)

        logger.error(f"Service did not become healthy within {timeout} seconds")
        return False

    async def verify_deployment(self) -> Dict[str, Any]:
        """Verify the deployment by checking service status and logs."""
        result = {
            "service_running": False,
            "containers_healthy": False,
            "logs_clean": False,
            "api_responsive": False,
        }

        try:
            # Check if service is running
            cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "ps",
                "autonomous-agents",
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0 and b"Up" in stdout:
                result["service_running"] = True
                logger.info("Service is running")

            # Check container health
            cmd = [
                "docker",
                "ps",
                "--filter",
                "name=twisterlab-autonomous-agents",
                "--format",
                "{{.Status}}",
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if b"healthy" in stdout.lower():
                result["containers_healthy"] = True
                logger.info("Containers are healthy")

            # Check logs for errors
            cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "logs",
                "autonomous-agents",
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            logs = stdout.decode().lower()
            error_indicators = ["error", "exception", "failed", "critical"]

            if not any(indicator in logs for indicator in error_indicators):
                result["logs_clean"] = True
                logger.info("Logs are clean")

            # Check API responsiveness
            import aiohttp

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        self.health_check_url, timeout=10
                    ) as response:
                        if response.status == 200:
                            result["api_responsive"] = True
                            logger.info("API is responsive")
                except Exception as e:
                    logger.warning(f"API check failed: {e}")

        except Exception as e:
            logger.error(f"Error during verification: {e}")

        return result

    async def rollback(self) -> bool:
        """Rollback the deployment in case of failure."""
        try:
            logger.info("Rolling back autonomous agents deployment...")

            cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "down",
                "autonomous-agents",
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            await process.communicate()

            if process.returncode == 0:
                logger.info("Rollback completed successfully")
                return True
            else:
                logger.error("Rollback failed")
                return False

        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False

    async def deploy(self) -> bool:
        """Main deployment method."""
        logger.info("Starting autonomous agents deployment process...")

        # Check dependencies
        if not await self.check_dependencies():
            logger.error("Dependency check failed")
            return False

        # Deploy service
        if not await self.deploy_service():
            logger.error("Service deployment failed")
            return False

        # Wait for health
        if not await self.wait_for_health():
            logger.error("Service health check failed")
            await self.rollback()
            return False

        # Verify deployment
        verification = await self.verify_deployment()
        success_count = sum(verification.values())
        total_checks = len(verification)

        logger.info(
            f"Deployment verification: {success_count}/{total_checks} checks passed"
        )

        if success_count == total_checks:
            logger.info("Autonomous agents deployment completed successfully!")
            return True
        else:
            logger.error("Deployment verification failed")
            await self.rollback()
            return False


async def main():
    """Main entry point."""
    deployer = AutonomousAgentsDeployer()

    try:
        success = await deployer.deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        await deployer.rollback()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await deployer.rollback()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
