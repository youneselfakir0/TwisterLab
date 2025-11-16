"""
Automated Backup System for TwisterLab Production
Schedules and executes regular backups of all components
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import httpx
import schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("backup/backup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AutomatedBackup:
    """Automated backup system for TwisterLab."""

    def __init__(self, api_base_url: str = "http://api.twisterlab.local"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout
        self.backup_schedule = {
            "database": "daily",  # Every day at 2 AM
            "config": "daily",  # Every day at 3 AM
            "logs": "hourly",  # Every hour
            "full_system": "weekly",  # Every Sunday at 4 AM
        }
        self.backup_dir = "backup"
        os.makedirs(self.backup_dir, exist_ok=True)

    async def start_scheduler(self):
        """Start the automated backup scheduler."""
        logger.info("Starting automated backup scheduler...")

        # Schedule database backups
        schedule.every().day.at("02:00").do(self._run_backup_job, "database")

        # Schedule config backups
        schedule.every().day.at("03:00").do(self._run_backup_job, "config")

        # Schedule log backups
        schedule.every().hour.do(self._run_backup_job, "logs")

        # Schedule full system backups
        schedule.every().sunday.at("04:00").do(self._run_backup_job, "full_system")

        # Keep running
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute

    async def _run_backup_job(self, backup_type: str):
        """Execute a backup job."""
        logger.info(f"Starting {backup_type} backup...")

        try:
            if backup_type == "database":
                result = await self._backup_database()
            elif backup_type == "config":
                result = await self._backup_config()
            elif backup_type == "logs":
                result = await self._backup_logs()
            elif backup_type == "full_system":
                result = await self._backup_full_system()
            else:
                logger.error(f"Unknown backup type: {backup_type}")
                return

            if result["status"] == "success":
                logger.info(f"{backup_type} backup completed successfully")
                await self._send_backup_notification(result)
                self._save_backup_metadata(result)
            else:
                logger.error(f"{backup_type} backup failed: {result.get('error', 'Unknown error')}")
                await self._send_backup_alert(result)

        except Exception as e:
            logger.error(f"Backup job failed: {str(e)}")
            await self._send_backup_alert(
                {
                    "backup_type": backup_type,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def _backup_database(self) -> Dict[str, Any]:
        """Backup database via BackupAgent."""
        return await self._call_agent(
            "backup", {"operation": "backup", "context": {"backup_type": "database"}}
        )

    async def _backup_config(self) -> Dict[str, Any]:
        """Backup configuration via BackupAgent."""
        return await self._call_agent(
            "backup", {"operation": "backup", "context": {"backup_type": "config"}}
        )

    async def _backup_logs(self) -> Dict[str, Any]:
        """Backup logs via BackupAgent."""
        return await self._call_agent(
            "backup", {"operation": "backup", "context": {"backup_type": "logs"}}
        )

    async def _backup_full_system(self) -> Dict[str, Any]:
        """Full system backup."""
        # Run integrity check first
        integrity_result = await self._call_agent(
            "backup",
            {"operation": "integrity_check", "context": {"check_type": "full"}},
        )

        if integrity_result.get("status") != "success":
            return {
                "status": "failed",
                "error": "Integrity check failed before full backup",
                "integrity_result": integrity_result,
            }

        # Proceed with full backup
        return await self._call_agent(
            "backup", {"operation": "backup", "context": {"backup_type": "full"}}
        )

    async def _call_agent(self, agent_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call an autonomous agent."""
        try:
            response = await self.client.post(
                f"{self.api_base_url}/api/v1/autonomous/agents/{agent_name}/execute",
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "agent": agent_name,
                }

        except Exception as e:
            return {"status": "error", "error": str(e), "agent": agent_name}

    async def _send_backup_notification(self, result: Dict[str, Any]):
        """Send backup success notification."""
        # In production, integrate with notification system (email, Slack, etc.)
        logger.info(f"Backup notification: {result}")

        # Save to notification log
        notification = {
            "type": "backup_success",
            "timestamp": datetime.now().isoformat(),
            "backup_type": result.get("backup_type", "unknown"),
            "details": result,
        }

        with open(f"{self.backup_dir}/notifications.log", "a") as f:
            json.dump(notification, f)
            f.write("\n")

    async def _send_backup_alert(self, result: Dict[str, Any]):
        """Send backup failure alert."""
        # In production, integrate with alerting system
        logger.error(f"Backup alert: {result}")

        # Save to alert log
        alert = {
            "type": "backup_failure",
            "timestamp": datetime.now().isoformat(),
            "backup_type": result.get("backup_type", "unknown"),
            "error": result.get("error", "Unknown error"),
            "details": result,
        }

        with open(f"{self.backup_dir}/alerts.log", "a") as f:
            json.dump(alert, f)
            f.write("\n")

    def _save_backup_metadata(self, result: Dict[str, Any]):
        """Save backup metadata for tracking."""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "backup_type": result.get("backup_type", "unknown"),
            "status": result.get("status", "unknown"),
            "size": result.get("size", 0),
            "duration": result.get("execution_time_ms", 0),
            "agent": result.get("agent", "unknown"),
        }

        with open(f"{self.backup_dir}/backup_metadata.log", "a") as f:
            json.dump(metadata, f)
            f.write("\n")

    async def manual_backup(self, backup_type: str) -> Dict[str, Any]:
        """Execute manual backup."""
        return await self._run_backup_job(backup_type)

    def get_backup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get backup history."""
        try:
            with open(f"{self.backup_dir}/backup_metadata.log", "r") as f:
                lines = f.readlines()[-limit:]
                return [json.loads(line.strip()) for line in lines if line.strip()]
        except FileNotFoundError:
            return []

    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics."""
        history = self.get_backup_history(1000)  # Last 1000 backups

        stats = {
            "total_backups": len(history),
            "successful_backups": len([h for h in history if h["status"] == "success"]),
            "failed_backups": len([h for h in history if h["status"] != "success"]),
            "average_duration": (
                sum(h.get("duration", 0) for h in history) / len(history) if history else 0
            ),
            "last_backup": history[-1] if history else None,
        }

        return stats


async def main():
    """Main function."""
    backup_system = AutomatedBackup()

    # Check command line arguments
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "manual":
            if len(sys.argv) > 2:
                backup_type = sys.argv[2]
                result = await backup_system.manual_backup(backup_type)
                print(f"Manual backup result: {result}")
            else:
                print("Usage: python automated_backup.py manual <backup_type>")
                print("Backup types: database, config, logs, full_system")

        elif command == "stats":
            stats = backup_system.get_backup_stats()
            print("Backup Statistics:")
            print(json.dumps(stats, indent=2, default=str))

        elif command == "history":
            history = backup_system.get_backup_history()
            print("Backup History:")
            for item in history[-10:]:  # Last 10
                print(f"{item['timestamp']} - {item['backup_type']} - {item['status']}")

        else:
            print("Usage: python automated_backup.py [manual <type>|stats|history]")
    else:
        # Start automated scheduler
        await backup_system.start_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
