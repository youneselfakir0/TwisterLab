"""
BackupAgent - Automated Backup and Disaster Recovery
=====================================================

Provides automated backup capabilities for TwisterLab's data assets with
integrity verification and retention management.

Author: Claude + Copilot Collaborative Development
Version: 1.0.0-alpha.1
License: Apache 2.0
"""

import asyncio
import hashlib
import json
import logging
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.base import TwisterAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("backup_agent")


# ============================================================================
# BACKUP TYPES AND STATUS
# ============================================================================


class BackupType:
    """Backup type constants"""

    FULL = "full"
    INCREMENTAL = "incremental"
    ON_DEMAND = "on_demand"


class BackupStatus:
    """Backup operation status constants"""

    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


# ============================================================================
# BACKUP AGENT
# ============================================================================


class BackupAgent(TwisterAgent):
    """
    Agent for automated backup and disaster recovery.

    Features:
    - Automated scheduled backups (full/incremental)
    - Backup integrity verification with checksums
    - Retention policy management
    - Point-in-time recovery support
    - Disaster recovery capabilities

    Backup Schedule:
    - Full backup: Daily at 00:00 UTC
    - Incremental backup: Every 6 hours
    - Retention: 30 days (full), 7 days (incremental)
    """

    def __init__(self, backup_dir: Optional[str] = None):
        super().__init__(
            name="backup-agent",
            display_name="Backup & Recovery Agent",
            description="Automated backup and disaster recovery for TwisterLab data",
            model="llama-3.2",
            temperature=0.1,
            tools=self._define_tools(),
        )

        # Backup configuration
        self.backup_dir = Path(backup_dir or "backups/twisterlab")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Retention policy (days)
        self.retention_policy = {
            BackupType.FULL: 30,
            BackupType.INCREMENTAL: 7,
        }

        # Backup statistics
        self.backup_stats = {
            "total_backups": 0,
            "successful_backups": 0,
            "failed_backups": 0,
            "last_backup": None,
            "total_size_bytes": 0,
        }

        # In-memory backup history
        self.backup_history = []

        logger.info(f"BackupAgent initialized (backup_dir={self.backup_dir})")

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define MCP tools for backup operations"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_backup",
                    "description": "Create a new backup (full or incremental)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backup_type": {
                                "type": "string",
                                "enum": ["full", "incremental", "on_demand"],
                                "description": "Type of backup to create",
                            }
                        },
                        "required": ["backup_type"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_backups",
                    "description": "List all available backups",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_backup",
                    "description": "Verify backup integrity using checksum",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backup_id": {"type": "string", "description": "Backup ID to verify"}
                        },
                        "required": ["backup_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "restore_backup",
                    "description": "Restore from backup (disaster recovery)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backup_id": {"type": "string", "description": "Backup ID to restore"}
                        },
                        "required": ["backup_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_retention",
                    "description": "Apply retention policy and cleanup old backups",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute backup operation.

        Args:
            task: Task description
            context: Operation context with parameters

        Returns:
            Operation result
        """
        try:
            logger.info(f"BackupAgent executing: {task}")

            context = context or {}
            operation = context.get("operation", "create_backup")

            # Route to appropriate handler
            if operation == "create_backup":
                backup_type = context.get("backup_type", BackupType.FULL)
                result = await self._create_backup(backup_type)
            elif operation == "list_backups":
                result = await self._list_backups()
            elif operation == "verify_backup":
                backup_id = context.get("backup_id")
                result = await self._verify_backup(backup_id)
            elif operation == "restore_backup":
                backup_id = context.get("backup_id")
                result = await self._restore_backup(backup_id)
            elif operation == "apply_retention":
                result = await self._apply_retention()
            else:
                result = {"status": BackupStatus.FAILED, "error": f"Unknown operation: {operation}"}

            return result

        except Exception as e:
            logger.error(f"Error in backup execution: {e}", exc_info=True)
            return {
                "status": BackupStatus.FAILED,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _create_backup(self, backup_type: str) -> Dict[str, Any]:
        """
        Create a new backup.

        Steps:
        1. Generate backup ID
        2. Backup PostgreSQL database
        3. Backup Redis snapshot
        4. Backup configuration files
        5. Create compressed archive
        6. Calculate checksum
        7. Save metadata
        """
        try:
            backup_id = self._generate_backup_id(backup_type)
            logger.info(f"Creating {backup_type} backup: {backup_id}")

            start_time = datetime.now(timezone.utc)

            # Create backup directory
            backup_path = self.backup_dir / backup_type / f"{backup_id}.tar.gz"
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Backup components
            logger.info("Backing up database")
            db_file = await self._backup_database(backup_id)

            logger.info("Backing up Redis")
            redis_file = await self._backup_redis(backup_id)

            logger.info("Backing up configuration")
            config_file = await self._backup_config(backup_id)

            # Create archive
            logger.info("Creating compressed archive")
            await self._create_archive(backup_path, [db_file, redis_file, config_file])

            # Calculate checksum
            checksum = await self._calculate_checksum(backup_path)

            # Cleanup temporary files
            await self._cleanup_temp_files([db_file, redis_file, config_file])

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            size_bytes = backup_path.stat().st_size

            # Save metadata
            metadata = {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "timestamp": start_time.isoformat(),
                "size_bytes": size_bytes,
                "checksum": checksum,
                "status": BackupStatus.SUCCESS,
                "execution_time": execution_time,
                "components": ["database", "redis", "config"],
            }

            await self._save_backup_metadata(metadata)

            # Update statistics
            self.backup_stats["total_backups"] += 1
            self.backup_stats["successful_backups"] += 1
            self.backup_stats["last_backup"] = start_time.isoformat()
            self.backup_stats["total_size_bytes"] += size_bytes

            self.backup_history.append(metadata)

            logger.info(
                f"Backup {backup_id} completed: " f"{size_bytes} bytes, {execution_time:.2f}s"
            )

            return {
                "status": BackupStatus.SUCCESS,
                "backup_id": backup_id,
                "backup_type": backup_type,
                "size_bytes": size_bytes,
                "checksum": checksum,
                "execution_time": round(execution_time, 3),
                "timestamp": start_time.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating backup: {e}", exc_info=True)
            self.backup_stats["failed_backups"] += 1
            return {"status": BackupStatus.FAILED, "error": str(e)}

    async def _backup_database(self, backup_id: str) -> str:
        """Mock database backup (PostgreSQL)"""
        temp_dir = self.backup_dir / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        db_file = temp_dir / f"{backup_id}_database.sql"

        # Mock database backup
        mock_data = f"""-- TwisterLab Database Backup
-- Backup ID: {backup_id}
-- Timestamp: {datetime.now(timezone.utc).isoformat()}

-- Tables: tickets, sops, devices, audit_logs
-- Mock data for testing
"""
        db_file.write_text(mock_data)

        logger.debug(f"Database backup created: {db_file}")
        return str(db_file)

    async def _backup_redis(self, backup_id: str) -> str:
        """Mock Redis snapshot backup"""
        temp_dir = self.backup_dir / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        redis_file = temp_dir / f"{backup_id}_redis.rdb"

        # Mock Redis RDB file header
        mock_data = b"REDIS0009\xfa\x09redis-ver\x053.2.0\x00"
        redis_file.write_bytes(mock_data)

        logger.debug(f"Redis backup created: {redis_file}")
        return str(redis_file)

    async def _backup_config(self, backup_id: str) -> str:
        """Mock configuration backup"""
        temp_dir = self.backup_dir / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        config_file = temp_dir / f"{backup_id}_config.json"

        # Mock config data
        mock_config = {
            "backup_id": backup_id,
            "config_files": [".env", "docker-compose.yml", "alembic.ini"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        config_file.write_text(json.dumps(mock_config, indent=2))

        logger.debug(f"Config backup created: {config_file}")
        return str(config_file)

    async def _create_archive(self, output_path: Path, files_to_archive: List[str]):
        """Create compressed tar.gz archive"""
        with tarfile.open(output_path, "w:gz") as tar:
            for file_path in files_to_archive:
                file_p = Path(file_path)
                if file_p.exists():
                    tar.add(file_path, arcname=file_p.name)

        logger.debug(f"Archive created: {output_path}")

    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum"""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        checksum = sha256_hash.hexdigest()
        logger.debug(f"Checksum: {checksum}")
        return checksum

    async def _cleanup_temp_files(self, files: List[str]):
        """Delete temporary files"""
        for file_path in files:
            file_p = Path(file_path)
            if file_p.exists():
                file_p.unlink()

    async def _save_backup_metadata(self, metadata: Dict[str, Any]):
        """Save backup metadata to manifest"""
        manifest_file = self.backup_dir / "metadata" / "backup_manifest.json"
        manifest_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing manifest
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
        else:
            manifest = {"backups": []}

        # Add new backup
        manifest["backups"].append(metadata)

        # Save manifest
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.debug("Backup metadata saved")

    def _generate_backup_id(self, backup_type: str) -> str:
        """Generate unique backup ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        return f"twisterlab_{backup_type}_{timestamp}"

    async def _list_backups(self) -> Dict[str, Any]:
        """List all available backups"""
        try:
            manifest_file = self.backup_dir / "metadata" / "backup_manifest.json"

            if not manifest_file.exists():
                return {"status": "success", "backups": [], "total_backups": 0}

            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            backups = manifest.get("backups", [])

            return {
                "status": "success",
                "backups": backups,
                "total_backups": len(backups),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return {"status": "error", "error": str(e)}

    async def _verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity using checksum"""
        try:
            if not backup_id:
                return {"status": "error", "error": "backup_id is required"}

            logger.info(f"Verifying backup: {backup_id}")

            # Find backup in manifest
            backups_list = await self._list_backups()
            backup_metadata = None

            for backup in backups_list.get("backups", []):
                if backup["backup_id"] == backup_id:
                    backup_metadata = backup
                    break

            if not backup_metadata:
                return {"status": "error", "error": f"Backup {backup_id} not found in manifest"}

            # Find backup file
            backup_type = backup_metadata["backup_type"]
            backup_path = self.backup_dir / backup_type / f"{backup_id}.tar.gz"

            if not backup_path.exists():
                return {"status": "error", "error": f"Backup file not found: {backup_path}"}

            # Verify checksum
            stored_checksum = backup_metadata["checksum"]
            calculated_checksum = await self._calculate_checksum(backup_path)

            if stored_checksum == calculated_checksum:
                logger.info(f"Backup {backup_id} verified successfully")
                return {
                    "status": BackupStatus.VERIFIED,
                    "backup_id": backup_id,
                    "checksum_match": True,
                    "checksum": stored_checksum,
                }
            else:
                logger.error(f"Backup {backup_id} is corrupted!")
                return {
                    "status": BackupStatus.CORRUPTED,
                    "backup_id": backup_id,
                    "checksum_match": False,
                    "stored_checksum": stored_checksum,
                    "calculated_checksum": calculated_checksum,
                }

        except Exception as e:
            logger.error(f"Error verifying backup: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def _restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup (disaster recovery)"""
        try:
            if not backup_id:
                return {"status": "error", "error": "backup_id is required"}

            logger.warning(f"Initiating restore from backup: {backup_id}")

            # Verify backup exists and is valid
            verify_result = await self._verify_backup(backup_id)

            if verify_result["status"] != BackupStatus.VERIFIED:
                return {
                    "status": "error",
                    "error": f"Cannot restore: {verify_result.get('error', 'Backup verification failed')}",
                }

            # In production, this would:
            # 1. Stop all agents
            # 2. Restore PostgreSQL database
            # 3. Restore Redis data
            # 4. Restore configuration files
            # 5. Restart agents

            logger.info(f"Restore simulation completed for {backup_id}")

            return {
                "status": "success",
                "backup_id": backup_id,
                "message": "Restore simulation (actual restore not performed in demo)",
                "note": "In production: stop agents → restore DB → restore Redis → restore config → restart",
            }

        except Exception as e:
            logger.error(f"Error restoring backup: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def _apply_retention(self) -> Dict[str, Any]:
        """Apply retention policy and delete old backups"""
        try:
            logger.info("Applying retention policy")

            deleted_count = 0
            deleted_backups = []

            # Calculate cutoff dates
            cutoffs = {
                BackupType.FULL: datetime.now(timezone.utc)
                - timedelta(days=self.retention_policy[BackupType.FULL]),
                BackupType.INCREMENTAL: datetime.now(timezone.utc)
                - timedelta(days=self.retention_policy[BackupType.INCREMENTAL]),
            }

            # Get all backups
            backups_list = await self._list_backups()

            for backup in backups_list.get("backups", []):
                backup_date = datetime.fromisoformat(backup["timestamp"].replace("Z", "+00:00"))
                backup_type = backup["backup_type"]
                backup_id = backup["backup_id"]

                # Check if backup should be deleted
                cutoff = cutoffs.get(backup_type)
                if cutoff and backup_date < cutoff:
                    # Delete backup file
                    backup_path = self.backup_dir / backup_type / f"{backup_id}.tar.gz"
                    if backup_path.exists():
                        backup_path.unlink()
                        deleted_count += 1
                        deleted_backups.append(backup_id)
                        logger.info(f"Deleted old backup: {backup_id}")

            logger.info(f"Retention policy applied: {deleted_count} backups deleted")

            return {
                "status": "success",
                "deleted_count": deleted_count,
                "deleted_backups": deleted_backups,
                "retention_policy": self.retention_policy,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error applying retention: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        return {**self.backup_stats, "retention_policy": self.retention_policy}

    def health_check(self) -> Dict[str, Any]:
        """Agent health check"""
        return {
            "status": "healthy",
            "agent": self.name,
            "backup_dir": str(self.backup_dir),
            "backup_stats": self.backup_stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":

    async def main():
        backup_agent = BackupAgent(backup_dir="test_backups")

        # Test full backup
        print("\n=== Creating Full Backup ===")
        result = await backup_agent.execute(
            "Create backup", {"operation": "create_backup", "backup_type": BackupType.FULL}
        )
        print(json.dumps(result, indent=2))

        backup_id = result.get("backup_id")

        # Test backup verification
        if backup_id:
            print("\n=== Verifying Backup ===")
            verify_result = await backup_agent.execute(
                "Verify backup", {"operation": "verify_backup", "backup_id": backup_id}
            )
            print(json.dumps(verify_result, indent=2))

        # Test listing backups
        print("\n=== Listing Backups ===")
        list_result = await backup_agent.execute("List backups", {"operation": "list_backups"})
        print(json.dumps(list_result, indent=2))

        # Test statistics
        print("\n=== Backup Statistics ===")
        print(json.dumps(backup_agent.get_backup_stats(), indent=2))

    asyncio.run(main())
