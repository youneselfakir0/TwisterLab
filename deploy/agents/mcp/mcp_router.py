"""
MCP Router - Isolated communication router for TwisterLab agents.

This module provides secure, isolated communication between agents
and MCP (Model Context Protocol) servers. All agent communication
MUST go through this router to maintain security and auditability.

MCP Isolation Tiers:
- TIER 1: TwisterLab Agent MCPs (172.25.0.0/16)
- TIER 2: Claude Desktop MCPs (172.26.0.0/16)
- TIER 3: Docker System MCPs (172.27.0.0/16)
- TIER 4: Copilot MCPs (172.28.0.0/16)

NO cross-tier communication is allowed.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

import aiohttp

logger = logging.getLogger(__name__)


class MCPRouter:
    """
    Isolated MCP communication router.

    Ensures all agent communication goes through secure, audited channels.
    Maintains MCP isolation and prevents unauthorized access.
    """

    def __init__(self):
        """Initialize MCP router with tier isolation."""
        self.tier_isolation = {
            "tier_1": {
                "network": "172.25.0.0/16",
                "ports": range(9000, 9100),
                "allowed_agents": [
                    "MonitoringAgent",
                    "BackupAgent",
                    "SyncAgent",
                    "ResolverAgent",
                    "Desktop-CommanderAgent",
                    "MaestroOrchestratorAgent",
                    "ClassifierAgent",
                ],
            },
            "tier_2": {
                "network": "172.26.0.0/16",
                "ports": range(9200, 9300),
                "allowed_agents": [],  # Claude Desktop only
            },
            "tier_3": {
                "network": "172.27.0.0/16",
                "ports": range(9400, 9500),
                "allowed_agents": ["MaestroOrchestratorAgent"],  # Docker daemon + Maestro
            },
            "tier_4": {
                "network": "172.28.0.0/16",
                "ports": range(9600, 9700),
                "allowed_agents": [],  # Copilot only
            },
        }

        # MCP endpoint registry
        self.mcp_endpoints = {
            # Tier 1 - TwisterLab Agent MCPs
            "monitoring_mcp": {
                "endpoint": "http://172.25.0.11:9001",
                "tier": "tier_1",
                "allowed_agents": ["MonitoringAgent", "MaestroOrchestratorAgent"],
            },
            "sync_mcp": {
                "endpoint": "http://172.25.0.12:9002",
                "tier": "tier_1",
                "allowed_agents": ["BackupAgent", "SyncAgent", "MonitoringAgent"],
            },
            "backup_mcp": {
                "endpoint": "http://172.25.0.13:9003",
                "tier": "tier_1",
                "allowed_agents": ["BackupAgent"],
            },
            "maestro_mcp": {
                "endpoint": "http://172.25.0.14:9004",
                "tier": "tier_1",
                "allowed_agents": ["all"],  # Maestro can coordinate all
            },
            # Tier 2 - Claude Desktop MCPs (isolated)
            "claude_filesystem_mcp": {
                "endpoint": "http://172.26.0.11:9201",
                "tier": "tier_2",
                "allowed_agents": [],
            },
            # Tier 3 - Docker System MCPs
            "docker_monitoring_mcp": {
                "endpoint": "http://172.27.0.11:9401",
                "tier": "tier_3",
                "allowed_agents": ["MaestroOrchestratorAgent"],
            },
            # Tier 4 - Copilot MCPs (isolated)
            "copilot_code_completion_mcp": {
                "endpoint": "http://172.28.0.11:9601",
                "tier": "tier_4",
                "allowed_agents": [],
            },
        }

        # Communication audit log
        self.audit_log = []

        # HTTP client session
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def route_to_mcp(
        self, agent_name: str, mcp_name: str, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route operation to specified MCP with isolation enforcement.

        Args:
            agent_name: Name of calling agent
            mcp_name: Target MCP name
            operation: Operation to perform
            params: Operation parameters

        Returns:
            MCP response

        Raises:
            PermissionError: If agent not allowed to access MCP
            ValueError: If MCP not found
            RuntimeError: If communication fails
        """
        # Validate access permissions
        await self._validate_access(agent_name, mcp_name)

        # Get MCP endpoint
        mcp_config = self.mcp_endpoints.get(mcp_name)
        if not mcp_config:
            raise ValueError(f"MCP '{mcp_name}' not found")

        endpoint = mcp_config["endpoint"]

        # Audit the communication
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "mcp": mcp_name,
            "operation": operation,
            "tier": mcp_config["tier"],
        }
        self.audit_log.append(audit_entry)

        logger.info(f"MCP Route: {agent_name} -> {mcp_name}:{operation}")

        try:
            # For testing/development, return mock responses
            # In production, this would make actual HTTP calls
            return await self._mock_mcp_call(agent_name, mcp_name, operation, params)

        except Exception as e:
            logger.error(f"MCP communication failed: {agent_name} -> {mcp_name}: {str(e)}")
            raise RuntimeError(f"MCP communication failed: {str(e)}")

    async def _validate_access(self, agent_name: str, mcp_name: str) -> None:
        """
        Validate agent has permission to access MCP.

        Args:
            agent_name: Calling agent name
            mcp_name: Target MCP name

        Raises:
            PermissionError: If access not allowed
        """
        mcp_config = self.mcp_endpoints.get(mcp_name)
        if not mcp_config:
            raise ValueError(f"MCP '{mcp_name}' not found")

        allowed_agents = mcp_config["allowed_agents"]

        # Check if agent is allowed
        if "all" not in allowed_agents and agent_name not in allowed_agents:
            raise PermissionError(
                f"Agent '{agent_name}' not allowed to access MCP '{mcp_name}'. "
                f"Allowed agents: {allowed_agents}"
            )

        # Additional tier validation could be added here
        tier = mcp_config["tier"]
        tier_config = self.tier_isolation[tier]

        if agent_name not in tier_config["allowed_agents"] and "all" not in allowed_agents:
            raise PermissionError(
                f"Agent '{agent_name}' not allowed in {tier}. "
                f"Allowed agents: {tier_config['allowed_agents']}"
            )

    async def _mock_mcp_call(
        self, agent_name: str, mcp_name: str, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mock MCP call for testing/development.

        In production, this would make actual HTTP requests to MCP servers.
        """
        # Simulate network delay
        await asyncio.sleep(0.01)

        # Return mock responses based on operation
        if mcp_name == "monitoring_mcp":
            if operation == "health_check":
                return {
                    "status": "healthy",
                    "services": ["api", "database", "cache"],
                    "response_time_ms": 150,
                }
            elif operation == "get_diagnostics":
                return {"issues_found": 0, "issues": [], "diagnostic_duration_ms": 500}

        elif mcp_name == "sync_mcp":
            if operation == "backup_database":
                return {
                    "status": "success",
                    "backup_size": "2.1GB",
                    "duration_ms": 8500,
                }
            elif operation == "sync_cache_database":
                return {
                    "status": "synced",
                    "records_synced": 250,
                    "sync_duration_ms": 1500,
                }

        elif mcp_name == "backup_mcp":
            if operation == "verify_database_integrity":
                return {"integrity_ok": True, "verification_duration_ms": 3200}

        elif mcp_name == "maestro_mcp":
            if operation == "get_all_agent_states":
                return {
                    "agents": ["MonitoringAgent", "BackupAgent", "SyncAgent"],
                    "states": {"healthy": True, "active": True},
                }

        # Default mock response
        return {
            "status": "success",
            "operation": operation,
            "mock_response": True,
            "timestamp": datetime.now().isoformat(),
        }

    def get_audit_log(self) -> list:
        """
        Get communication audit log.

        Returns:
            List of audit entries
        """
        return self.audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear audit log."""
        self.audit_log.clear()

    def get_mcp_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """
        Get registered MCP endpoints.

        Returns:
            Dict of MCP configurations
        """
        return self.mcp_endpoints.copy()
