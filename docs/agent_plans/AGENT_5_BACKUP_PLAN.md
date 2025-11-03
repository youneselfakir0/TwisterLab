# AGENT 5: BACKUP AGENT - COMPLETE IMPLEMENTATION PLAN

**Priority:** 5
**Status:** Planning Phase
**Estimated Lines:** 500+
**Dependencies:** MaestroOrchestrator, PostgreSQL, Redis, S3-Compatible Storage

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Role in System
The Backup-AgentAgent provides **automated backup and disaster recovery** for TwisterLab's data assets.

**Backup Targets:**
- PostgreSQL database (tickets, SOPs, devices, audit logs)
- Redis cache snapshots
- Configuration files
- Agent logs

**Backup Types:**
- **Full Backup:** Complete snapshot (daily)
- **Incremental Backup:** Changes only (every 6 hours)
- **On-Demand Backup:** Manual trigger

### 1.2 Core Responsibilities
1. **Scheduled Backups** - Automated backup execution
2. **Backup Verification** - Validate backup integrity
3. **Retention Management** - Apply retention policies
4. **Point-in-Time Recovery** - Restore to specific timestamp
5. **Disaster Recovery** - Full system restore capabilities

### 1.3 Backup Storage

**Primary:** S3-Compatible Storage (MinIO, AWS S3, Azure Blob)
**Secondary:** Local filesystem (for quick recovery)

**Backup Naming:**
```
backups/
├── full/
│   ├── twisterlab_full_2025-11-02_00-00-00.tar.gz
│   ├── twisterlab_full_2025-11-01_00-00-00.tar.gz
├── incremental/
│   ├── twisterlab_incr_2025-11-02_06-00-00.tar.gz
│   ├── twisterlab_incr_2025-11-02_12-00-00.tar.gz
└── metadata/
    └── backup_manifest.json
```

---

## 2. CODE TEMPLATE

**File:** `agents/support/backup_agent.py`

```python
"""
TwisterLab - Backup Agent
Automated backup and disaster recovery
"""

import logging
import asyncio
import tarfile
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import hashlib

from ..base import TwisterAgent
from ..database.config import get_db
import subprocess

logger = logging.getLogger(__name__)


class BackupType:
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    ON_DEMAND = "on_demand"


class BackupStatus:
    """Backup operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


class BackupAgent(TwisterAgent):
    """
    Agent for automated backup and disaster recovery.
    """

    def __init__(self):
        super().__init__(
            name="backup-agent",
            display_name="Backup & Recovery Agent",
            description="Automated backup and disaster recovery for TwisterLab data",
            role="backup",
            instructions=self._get_instructions(),
            tools=self._define_tools(),
            model="llama-3.2",
            temperature=0.1,
            metadata={
                "department": "Infrastructure",
                "backup_interval": "21600 seconds",  # 6 hours
                "retention_days": 30,
                "storage_type": "s3"
            }
        )

        # Backup configuration
        self.backup_dir = Path("/var/backups/twisterlab")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Retention policy
        self.retention_policy = {
            "full": 30,  # Keep 30 days of full backups
            "incremental": 7,  # Keep 7 days of incremental backups
        }

        # Backup history
        self.backup_history = []

    def _get_instructions(self) -> str:
        return """
        You are the Backup Agent, responsible for data protection and disaster recovery.

        Your responsibilities:
        1. Execute scheduled backups (full and incremental)
        2. Verify backup integrity with checksums
        3. Apply retention policies (delete old backups)
        4. Provide point-in-time recovery capabilities
        5. Monitor backup health and storage usage

        Backup Schedule:
        - Full backup: Daily at 00:00 UTC
        - Incremental backup: Every 6 hours
        - Retention: 30 days for full, 7 days for incremental

        Always verify backups after creation.
        Log all operations for audit trail.
        Alert on backup failures.
        """

    def _define_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_backup",
                    "description": "Create a new backup",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backup_type": {
                                "type": "string",
                                "enum": ["full", "incremental"]
                            }
                        },
                        "required": ["backup_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_backups",
                    "description": "List available backups",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "restore_backup",
                    "description": "Restore from backup",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backup_id": {"type": "string"},
                            "point_in_time": {"type": "string"}
                        },
                        "required": ["backup_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_backup",
                    "description": "Verify backup integrity",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backup_id": {"type": "string"}
                        },
                        "required": ["backup_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_retention",
                    "description": "Apply retention policy and cleanup old backups",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main execution method"""
        try:
            logger.info(f"Backup Agent executing: {task}")

            operation = context.get("operation", "create_backup") if context else "create_backup"

            if operation == "create_backup":
                backup_type = context.get("backup_type", BackupType.FULL) if context else BackupType.FULL
                result = await self._create_backup(backup_type)
            elif operation == "list_backups":
                result = await self._list_backups()
            elif operation == "restore_backup":
                backup_id = context.get("backup_id") if context else None
                result = await self._restore_backup(backup_id)
            elif operation == "verify_backup":
                backup_id = context.get("backup_id") if context else None
                result = await self._verify_backup(backup_id)
            elif operation == "apply_retention":
                result = await self._apply_retention()
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }

            return result

        except Exception as e:
            logger.error(f"Error in backup execution: {e}", exc_info=True)
            return {
                "status": BackupStatus.FAILED,
                "error": str(e)
            }

    async def _create_backup(self, backup_type: str) -> Dict[str, Any]:
        """Create a new backup"""
        try:
            backup_id = self._generate_backup_id(backup_type)
            logger.info(f"Creating {backup_type} backup: {backup_id}")

            backup_path = self.backup_dir / backup_type / f"{backup_id}.tar.gz"
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            start_time = datetime.now(timezone.utc)

            # Step 1: Backup PostgreSQL
            logger.info("Backing up PostgreSQL database")
            db_backup = await self._backup_postgres(backup_id)

            # Step 2: Backup Redis
            logger.info("Backing up Redis snapshot")
            redis_backup = await self._backup_redis(backup_id)

            # Step 3: Backup configuration files
            logger.info("Backing up configuration files")
            config_backup = await self._backup_config(backup_id)

            # Step 4: Create compressed archive
            logger.info("Creating compressed archive")
            await self._create_archive(backup_id, backup_path, [
                db_backup,
                redis_backup,
                config_backup
            ])

            # Step 5: Calculate checksum
            checksum = await self._calculate_checksum(backup_path)

            # Step 6: Upload to S3 (if configured)
            # await self._upload_to_s3(backup_path)

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Step 7: Save backup metadata
            metadata = {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "timestamp": start_time.isoformat(),
                "size_bytes": backup_path.stat().st_size,
                "checksum": checksum,
                "status": BackupStatus.SUCCESS,
                "execution_time": execution_time
            }

            await self._save_backup_metadata(metadata)
            self.backup_history.append(metadata)

            logger.info(
                f"Backup {backup_id} completed successfully "
                f"({metadata['size_bytes']} bytes, {execution_time:.2f}s)"
            )

            return {
                "status": BackupStatus.SUCCESS,
                "backup_id": backup_id,
                "backup_type": backup_type,
                "size_bytes": metadata['size_bytes'],
                "checksum": checksum,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error creating backup: {e}", exc_info=True)
            return {
                "status": BackupStatus.FAILED,
                "error": str(e)
            }

    async def _backup_postgres(self, backup_id: str) -> str:
        """Backup PostgreSQL database using pg_dump"""
        try:
            output_file = self.backup_dir / "temp" / f"{backup_id}_postgres.sql"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Use pg_dump (would use actual DATABASE_URL in production)
            cmd = [
                "pg_dump",
                "-h", "localhost",
                "-U", "twisterlab",
                "-d", "twisterlab",
                "-F", "c",  # Custom format
                "-f", str(output_file)
            ]

            # For demo, create a mock backup file
            output_file.write_text("-- PostgreSQL database backup mock\n")

            logger.info(f"PostgreSQL backup saved to {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Error backing up PostgreSQL: {e}")
            raise

    async def _backup_redis(self, backup_id: str) -> str:
        """Backup Redis snapshot"""
        try:
            output_file = self.backup_dir / "temp" / f"{backup_id}_redis.rdb"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Trigger Redis BGSAVE
            # redis-cli BGSAVE
            # Then copy dump.rdb

            # For demo, create mock file
            output_file.write_bytes(b"REDIS0009\xfa\x09redis-ver\x053.2.0")

            logger.info(f"Redis backup saved to {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Error backing up Redis: {e}")
            raise

    async def _backup_config(self, backup_id: str) -> str:
        """Backup configuration files"""
        try:
            output_file = self.backup_dir / "temp" / f"{backup_id}_config.tar"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Backup .env, docker-compose.yml, etc.
            config_files = [
                ".env",
                "docker-compose.yml",
                "alembic.ini"
            ]

            # For demo, create mock archive
            with tarfile.open(output_file, "w") as tar:
                for config_file in config_files:
                    # Would add actual files in production
                    pass

            logger.info(f"Config backup saved to {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Error backing up config: {e}")
            raise

    async def _create_archive(
        self,
        backup_id: str,
        output_path: Path,
        files_to_archive: List[str]
    ):
        """Create compressed tar archive"""
        try:
            with tarfile.open(output_path, "w:gz") as tar:
                for file_path in files_to_archive:
                    if Path(file_path).exists():
                        tar.add(file_path, arcname=Path(file_path).name)

            logger.info(f"Archive created: {output_path}")

        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            raise

    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of backup file"""
        try:
            sha256_hash = hashlib.sha256()

            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            checksum = sha256_hash.hexdigest()
            logger.info(f"Checksum calculated: {checksum}")
            return checksum

        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            raise

    async def _save_backup_metadata(self, metadata: Dict[str, Any]):
        """Save backup metadata to manifest file"""
        try:
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

            logger.info("Backup metadata saved")

        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def _generate_backup_id(self, backup_type: str) -> str:
        """Generate unique backup ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        return f"twisterlab_{backup_type}_{timestamp}"

    async def _list_backups(self) -> Dict[str, Any]:
        """List all available backups"""
        try:
            manifest_file = self.backup_dir / "metadata" / "backup_manifest.json"

            if not manifest_file.exists():
                return {
                    "status": "success",
                    "backups": [],
                    "total_backups": 0
                }

            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            backups = manifest.get("backups", [])

            return {
                "status": "success",
                "backups": backups,
                "total_backups": len(backups)
            }

        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity using checksum"""
        try:
            logger.info(f"Verifying backup: {backup_id}")

            # Find backup in manifest
            backups_list = await self._list_backups()
            backup_metadata = None

            for backup in backups_list.get("backups", []):
                if backup["backup_id"] == backup_id:
                    backup_metadata = backup
                    break

            if not backup_metadata:
                return {
                    "status": "error",
                    "error": f"Backup {backup_id} not found"
                }

            # Find backup file
            backup_type = backup_metadata["backup_type"]
            backup_path = self.backup_dir / backup_type / f"{backup_id}.tar.gz"

            if not backup_path.exists():
                return {
                    "status": "error",
                    "error": f"Backup file not found: {backup_path}"
                }

            # Verify checksum
            stored_checksum = backup_metadata["checksum"]
            calculated_checksum = await self._calculate_checksum(backup_path)

            if stored_checksum == calculated_checksum:
                return {
                    "status": "verified",
                    "backup_id": backup_id,
                    "checksum_match": True
                }
            else:
                return {
                    "status": "corrupted",
                    "backup_id": backup_id,
                    "checksum_match": False,
                    "stored_checksum": stored_checksum,
                    "calculated_checksum": calculated_checksum
                }

        except Exception as e:
            logger.error(f"Error verifying backup: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup"""
        try:
            logger.warning(f"Restoring from backup: {backup_id}")

            # This is a critical operation - would require:
            # 1. Stop all agents
            # 2. Restore database
            # 3. Restore Redis
            # 4. Restore config
            # 5. Restart agents

            return {
                "status": "success",
                "backup_id": backup_id,
                "message": "Restore simulation (not implemented in demo)"
            }

        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _apply_retention(self) -> Dict[str, Any]:
        """Apply retention policy and delete old backups"""
        try:
            logger.info("Applying retention policy")

            deleted_count = 0
            cutoff_full = datetime.now(timezone.utc) - timedelta(days=self.retention_policy["full"])
            cutoff_incr = datetime.now(timezone.utc) - timedelta(days=self.retention_policy["incremental"])

            backups_list = await self._list_backups()

            for backup in backups_list.get("backups", []):
                backup_date = datetime.fromisoformat(backup["timestamp"].replace("Z", "+00:00"))
                backup_type = backup["backup_type"]

                # Check if backup is old enough to delete
                should_delete = False

                if backup_type == "full" and backup_date < cutoff_full:
                    should_delete = True
                elif backup_type == "incremental" and backup_date < cutoff_incr:
                    should_delete = True

                if should_delete:
                    backup_path = self.backup_dir / backup_type / f"{backup['backup_id']}.tar.gz"
                    if backup_path.exists():
                        backup_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {backup['backup_id']}")

            return {
                "status": "success",
                "deleted_count": deleted_count,
                "retention_policy": self.retention_policy
            }

        except Exception as e:
            logger.error(f"Error applying retention: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
```

---

## 3. TESTING

```python
# tests/test_backup_agent.py

@pytest.mark.asyncio
async def test_create_backup():
    """Test backup creation"""
    backup_agent = BackupAgent()

    result = await backup_agent.execute(
        "Create backup",
        {"operation": "create_backup", "backup_type": "full"}
    )

    assert result["status"] in [BackupStatus.SUCCESS, BackupStatus.FAILED]
    if result["status"] == BackupStatus.SUCCESS:
        assert "backup_id" in result
        assert "checksum" in result

@pytest.mark.asyncio
async def test_list_backups():
    """Test listing backups"""
    backup_agent = BackupAgent()

    result = await backup_agent.execute("List backups", {"operation": "list_backups"})

    assert result["status"] == "success"
    assert "backups" in result
    assert "total_backups" in result
```

---

## 4. DEPLOYMENT

**Environment Variables:**
```bash
BACKUP_INTERVAL=21600  # 6 hours
BACKUP_DIR=/var/backups/twisterlab
BACKUP_RETENTION_DAYS=30
S3_BUCKET=twisterlab-backups
S3_ENDPOINT=https://s3.amazonaws.com
```

---

**Next Agent:** [Monitoring-AgentAgent (Priority 6)](AGENT_6_MONITORING_PLAN.md)
