"""
BackupAgent - Automated disaster recovery and system repair.

This agent performs automated backups, detects system corruption,
and executes recovery procedures autonomously.

Responsibilities:
- Automated backup scheduling
- Corruption detection
- Data recovery procedures
- System integrity verification
- Emergency repair protocols
"""

import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from agents.base.base_agent import BaseAgent


class BackupAgent(BaseAgent):
    """
    Autonomous backup and recovery agent.

    Capabilities:
    - Automated backups
    - Integrity verification
    - Disaster recovery
    - Self-healing repairs
    """

    def __init__(self):
        super().__init__()
        self.name = "BackupAgent"
        self.priority = 2
        self.capabilities = [
            "automated_backup",
            "cloud_backup",
            "incremental_backup",
            "backup_cleanup",
            "backup_verification",
            "integrity_check",
            "disaster_recovery",
            "cloud_recovery",
            "self_repair",
            "data_restoration",
        ]

        # Backup configuration
        self.backup_schedule = {
            "database": timedelta(hours=6),
            "config": timedelta(hours=24),
            "logs": timedelta(hours=1),
        }

        # Cloud backup configuration (DISABLED until proper MCP isolation)
        self.cloud_backup_enabled = False  # Temporarily disabled
        self.cloud_provider = "azure"  # azure, aws, gcp
        self.cloud_container = "twisterlab-backups"
        self.backup_retention_days = 30
        self.max_backup_count = 10

        # Encryption configuration
        self.encryption_enabled = True
        self.encryption_key_source = "vault"  # vault, env, generated

        # Integrity check configuration
        self.integrity_checks = {
            "database": "checksum_verification",
            "config": "file_hash_verification",
            "logs": "log_integrity_check",
        }

        # Configurable paths (instead of hardcoded)
        self.config_paths = ["./config/app.yml", "./config/database.yml"]
        self.log_directory = "./logs"
        self.backup_base_path = "./backups"

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute backup and recovery operations.

        Args:
            context: Operation context (backup_type, recovery_needed, etc.)

        Returns:
            Dict with operation results
        """
        try:
            self._validate_context(context)
            await self.audit_log("backup_operation_start", context)

            # CORRECTION: Appel à _process() comme requis par BaseAgent
            result = await self._process(context)

            await self.audit_log("backup_operation_complete", result)

            return {
                "status": "success",
                "operation": context.get("operation", "backup"),
                "timestamp": datetime.now().isoformat(),
                "result": result,
            }

        except Exception as e:
            await self.audit_log("backup_operation_failed", {"error": str(e)})
            raise

    async def _process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process backup operation (agent-specific logic).

        Args:
            context: Operation context

        Returns:
            Processing results
        """
        operation_type = context.get("operation", "backup")

        if operation_type == "backup":
            return await self._perform_backup(context)
        elif operation_type == "cloud_backup":
            return await self._perform_cloud_backup(context)
        elif operation_type == "incremental_backup":
            return await self._perform_incremental_backup(context)
        elif operation_type == "backup_cleanup":
            return await self._perform_backup_cleanup(context)
        elif operation_type == "backup_verify":
            return await self._perform_backup_verification(context)
        elif operation_type == "integrity_check":
            return await self._perform_integrity_check(context)
        elif operation_type == "recovery":
            return await self._perform_recovery(context)
        elif operation_type == "cloud_recovery":
            return await self._perform_cloud_recovery(context)
        elif operation_type == "repair":
            return await self._perform_self_repair(context)
        else:
            raise ValueError(f"Unknown operation: {operation_type}")

    async def _perform_backup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated backup of system components."""
        backup_type = context.get("backup_type", "full")
        results = {}

        if backup_type in ["full", "database"]:
            results["database"] = await self._backup_database()

        if backup_type in ["full", "config"]:
            results["config"] = await self._backup_config()

        if backup_type in ["full", "logs"]:
            results["logs"] = await self._backup_logs()

        return results

    async def _perform_integrity_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check system integrity and detect corruption."""
        check_type = context.get("check_type", "full")
        issues = []

        if check_type in ["full", "database"]:
            db_issues = await self._check_database_integrity()
            issues.extend(db_issues)

        if check_type in ["full", "config"]:
            config_issues = await self._check_config_integrity()
            issues.extend(config_issues)

        if check_type in ["full", "logs"]:
            log_issues = await self._check_log_integrity()
            issues.extend(log_issues)

        return {
            "issues_found": len(issues),
            "issues": issues,
            "integrity_status": "compromised" if issues else "intact",
        }

    async def _perform_recovery(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform disaster recovery from backups."""
        recovery_type = context.get("recovery_type", "full")
        results = {}

        if recovery_type in ["full", "database"]:
            results["database"] = await self._recover_database()

        if recovery_type in ["full", "config"]:
            results["config"] = await self._recover_config()

        return results

    async def _perform_self_repair(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated self-repair operations."""
        repair_type = context.get("repair_type", "integrity")
        results = {}

        if repair_type == "integrity":
            results = await self._repair_integrity_issues()
        elif repair_type == "permissions":
            results = await self._repair_permissions()
        elif repair_type == "connections":
            results = await self._repair_connections()

        return results

    async def _perform_cloud_backup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cloud backup of system components."""
        if not self.cloud_backup_enabled:
            return {"status": "skipped", "reason": "cloud_backup_disabled"}

        backup_type = context.get("backup_type", "full")
        results = {}

        try:
            # First perform local backup
            local_result = await self._perform_backup(context)
            if local_result.get("status") != "success":
                return {
                    "status": "failed",
                    "error": "local_backup_failed",
                    "details": local_result,
                }

            # Then upload to cloud
            if backup_type in ["full", "database"]:
                results["database"] = await self._upload_to_cloud("database")

            if backup_type in ["full", "config"]:
                results["config"] = await self._upload_to_cloud("config")

            if backup_type in ["full", "logs"]:
                results["logs"] = await self._upload_to_cloud("logs")

            # Clean up old cloud backups
            cleanup_result = await self._cleanup_cloud_backups()
            results["cleanup"] = cleanup_result

            return {
                "status": "success",
                "cloud_provider": self.cloud_provider,
                "uploaded_components": list(results.keys()),
                "results": results,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _perform_incremental_backup(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform incremental backup (only changed files)."""
        component = context.get("component", "all")
        results = {}

        try:
            if component in ["all", "database"]:
                results["database"] = await self._incremental_backup_database()

            if component in ["all", "config"]:
                results["config"] = await self._incremental_backup_config()

            if component in ["all", "logs"]:
                results["logs"] = await self._incremental_backup_logs()

            return {
                "status": "success",
                "backup_type": "incremental",
                "components": list(results.keys()),
                "results": results,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _perform_backup_cleanup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old backups based on retention policy."""
        cleanup_type = context.get("cleanup_type", "both")  # local, cloud, both
        results = {}

        try:
            if cleanup_type in ["local", "both"]:
                results["local"] = await self._cleanup_local_backups()

            if cleanup_type in ["cloud", "both"]:
                results["cloud"] = await self._cleanup_cloud_backups()

            return {
                "status": "success",
                "cleanup_type": cleanup_type,
                "results": results,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _perform_backup_verification(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify backup integrity and completeness."""
        verify_type = context.get("verify_type", "all")  # local, cloud, all
        results = {}

        try:
            if verify_type in ["local", "all"]:
                results["local"] = await self._verify_local_backups()

            if verify_type in ["cloud", "all"]:
                results["cloud"] = await self._verify_cloud_backups()

            # Generate verification report
            report = self._generate_verification_report(results)

            return {
                "status": "success",
                "verify_type": verify_type,
                "results": results,
                "report": report,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _perform_cloud_recovery(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform recovery from cloud backups."""
        recovery_type = context.get("recovery_type", "full")
        backup_timestamp = context.get("backup_timestamp", "latest")
        results = {}

        try:
            if recovery_type in ["full", "database"]:
                results["database"] = await self._download_from_cloud(
                    "database", backup_timestamp
                )

            if recovery_type in ["full", "config"]:
                results["config"] = await self._download_from_cloud(
                    "config", backup_timestamp
                )

            # Then perform local recovery
            local_recovery = await self._perform_recovery(context)
            results["local_recovery"] = local_recovery

            return {
                "status": "success",
                "recovery_type": recovery_type,
                "backup_timestamp": backup_timestamp,
                "results": results,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _backup_database(self) -> Dict[str, Any]:
        """Backup database with integrity verification."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="sync_mcp",
                operation="backup_database",
                params={"verify_integrity": True},
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _backup_config(self) -> Dict[str, Any]:
        """Backup configuration files."""
        try:
            # Use Desktop-Commander to backup config files
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="copy_files",
                params={
                    "source": self.config_paths,  # Configurable path
                    "destination": f"{self.backup_base_path}/config",
                    "compress": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _backup_logs(self) -> Dict[str, Any]:
        """Backup log files."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="backup_files",
                params={
                    "source": self.log_directory,  # Configurable path
                    "destination": f"{self.backup_base_path}/logs",
                    "compress": True,
                    "rotate": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _check_database_integrity(self) -> List[Dict[str, Any]]:
        """Check database integrity and detect corruption."""
        issues = []
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="sync_mcp",
                operation="verify_database_integrity",
                params={},
            )

            if not result.get("integrity_ok", False):
                issues.append(
                    {
                        "type": "database_corruption",
                        "severity": "critical",
                        "description": "Database integrity check failed",
                        "details": result,
                    }
                )
        except Exception as e:
            issues.append(
                {
                    "type": "database_check_error",
                    "severity": "high",
                    "description": f"Failed to check database integrity: {str(e)}",
                }
            )

        return issues

    async def _check_config_integrity(self) -> List[Dict[str, Any]]:
        """Check configuration file integrity."""
        issues = []
        try:
            # Calculate current hashes
            for config_file in self.config_paths:  # Configurable paths
                if os.path.exists(config_file):
                    current_hash = self._calculate_file_hash(config_file)
                    stored_hash = await self._get_stored_hash(config_file)

                    if current_hash != stored_hash:
                        issues.append(
                            {
                                "type": "config_file_modified",
                                "severity": "medium",
                                "description": f"Config file {config_file} has been modified",
                                "file": config_file,
                            }
                        )
        except Exception as e:
            issues.append(
                {
                    "type": "config_check_error",
                    "severity": "low",
                    "description": f"Failed to check config integrity: {str(e)}",
                }
            )

        return issues

    async def _check_log_integrity(self) -> List[Dict[str, Any]]:
        """Check log file integrity."""
        issues = []
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="verify_log_integrity",
                params={"log_directory": self.log_directory},
            )

            if result.get("corrupted_logs", 0) > 0:
                issues.append(
                    {
                        "type": "log_corruption",
                        "severity": "low",
                        "description": f"{result['corrupted_logs']} log files corrupted",
                        "details": result,
                    }
                )
        except Exception as e:
            issues.append(
                {
                    "type": "log_check_error",
                    "severity": "low",
                    "description": f"Failed to check log integrity: {str(e)}",
                }
            )

        return issues

    async def _recover_database(self) -> Dict[str, Any]:
        """Recover database from backup."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="sync_mcp",
                operation="restore_database",
                params={"backup_file": "latest"},
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _recover_config(self) -> Dict[str, Any]:
        """Recover configuration files from backup."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="restore_files",
                params={
                    "source": f"{self.backup_base_path}/config/latest",
                    "destination": "./config",  # Relative path
                    "overwrite": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _repair_integrity_issues(self) -> Dict[str, Any]:
        """Repair detected integrity issues."""
        repairs = []

        # Run integrity check first
        integrity_result = await self._perform_integrity_check({"check_type": "full"})

        for issue in integrity_result["issues"]:
            if issue["type"] == "database_corruption":
                repair_result = await self._recover_database()
                repairs.append(
                    {
                        "issue": issue,
                        "repair_action": "database_recovery",
                        "result": repair_result,
                    }
                )
            elif issue["type"] == "config_file_modified":
                # For config files, we might need manual intervention
                repairs.append(
                    {
                        "issue": issue,
                        "repair_action": "manual_review_required",
                        "result": "pending_manual_review",
                    }
                )

        return {"repairs_attempted": len(repairs), "repairs": repairs}

    async def _repair_permissions(self) -> Dict[str, Any]:
        """Repair file and directory permissions."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="fix_permissions",
                params={
                    "paths": [
                        "./config",
                        self.log_directory,
                        self.backup_base_path,
                    ],  # Configurable paths
                    "recursive": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _repair_connections(self) -> Dict[str, Any]:
        """Repair broken connections."""
        repairs = []

        # Try to reconnect database
        db_repair = await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name="sync_mcp",
            operation="reconnect_database",
            params={},
        )
        repairs.append({"component": "database", "result": db_repair})

        # Try to reconnect cache
        cache_repair = await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name="sync_mcp",
            operation="reconnect_cache",
            params={},
        )
        repairs.append({"component": "cache", "result": cache_repair})

        return repairs

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    async def _get_stored_hash(self, file_path: str) -> str:
        """Get stored hash for a file."""
        # This would typically read from a secure hash store
        # For now, return empty string to force re-hash
        return ""

    def _validate_context(self, context: Dict[str, Any]) -> None:
        """Validate backup operation context."""
        valid_operations = [
            "backup",
            "cloud_backup",
            "incremental_backup",
            "backup_cleanup",
            "backup_verify",
            "integrity_check",
            "recovery",
            "cloud_recovery",
            "repair",
        ]
        operation = context.get("operation")
        if operation and operation not in valid_operations:
            raise ValueError(
                f"Invalid operation: {operation}. Must be one of {valid_operations}"
            )

    # Cloud backup methods
    async def _upload_to_cloud(self, component: str) -> Dict[str, Any]:
        """Upload backup to cloud storage."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="azure_mcp",  # or appropriate cloud MCP
                operation="upload_backup",
                params={
                    "component": component,
                    "container": self.cloud_container,
                    "encrypt": self.encryption_enabled,
                    "compression": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _download_from_cloud(
        self, component: str, timestamp: str
    ) -> Dict[str, Any]:
        """Download backup from cloud storage."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="azure_mcp",
                operation="download_backup",
                params={
                    "component": component,
                    "container": self.cloud_container,
                    "timestamp": timestamp,
                    "decrypt": self.encryption_enabled,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # Incremental backup methods
    async def _incremental_backup_database(self) -> Dict[str, Any]:
        """Perform incremental database backup."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="sync_mcp",
                operation="incremental_backup_database",
                params={"verify_changes": True},
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _incremental_backup_config(self) -> Dict[str, Any]:
        """Perform incremental config backup."""
        try:
            # Check which config files have changed since last backup
            changed_files = await self._get_changed_config_files()
            if not changed_files:
                return {"status": "skipped", "reason": "no_changes"}

            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="backup_files",
                params={
                    "files": changed_files,
                    "destination": f"{self.backup_base_path}/config/incremental",
                    "compress": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _incremental_backup_logs(self) -> Dict[str, Any]:
        """Perform incremental log backup."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="backup_files",
                params={
                    "source": self.log_directory,
                    "destination": f"{self.backup_base_path}/logs/incremental",
                    "compress": True,
                    "rotate": True,
                    "incremental": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # Cleanup methods
    async def _cleanup_local_backups(self) -> Dict[str, Any]:
        """Clean up old local backups."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="cleanup_backups",
                params={
                    "base_path": self.backup_base_path,
                    "retention_days": self.backup_retention_days,
                    "max_count": self.max_backup_count,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _cleanup_cloud_backups(self) -> Dict[str, Any]:
        """Clean up old cloud backups."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="azure_mcp",
                operation="cleanup_backups",
                params={
                    "container": self.cloud_container,
                    "retention_days": self.backup_retention_days,
                    "max_count": self.max_backup_count,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # Verification methods
    async def _verify_local_backups(self) -> Dict[str, Any]:
        """Verify local backup integrity."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="verify_backups",
                params={
                    "base_path": self.backup_base_path,
                    "check_integrity": True,
                    "check_completeness": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _verify_cloud_backups(self) -> Dict[str, Any]:
        """Verify cloud backup integrity."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="azure_mcp",
                operation="verify_backups",
                params={
                    "container": self.cloud_container,
                    "check_integrity": True,
                    "check_completeness": True,
                },
            )
            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # Helper methods
    async def _get_changed_config_files(self) -> List[str]:
        """Get list of config files that changed since last backup."""
        try:
            result = await self.mcp_router.route_to_mcp(
                agent_name=self.name,
                mcp_name="desktop_commander_mcp",
                operation="get_changed_files",
                params={"directory": self.config_paths[0], "since_last_backup": True},
            )
            return result.get("changed_files", [])
        except Exception:
            return []

    def _generate_verification_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive backup verification report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "issues": [],
            "recommendations": [],
        }

        # Analyze results
        for location, result in results.items():
            if result.get("status") != "success":
                report["overall_status"] = "issues_found"
                report["issues"].append(
                    f"{location}: {result.get('error', 'unknown_error')}"
                )

        # Add recommendations
        if len(results.get("local", {}).get("backups", [])) > self.max_backup_count:
            report["recommendations"].append("Consider reducing local backup retention")

        if len(results.get("cloud", {}).get("backups", [])) > self.max_backup_count:
            report["recommendations"].append("Consider reducing cloud backup retention")

        return report
