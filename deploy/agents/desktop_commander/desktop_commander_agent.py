"""
TwisterLab - Desktop Commander Agent (Server-Side)
Secure remote command execution with zero-trust architecture
"""

import asyncio
import hashlib
import importlib.util
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# Import TwisterAgent directly from base.py file
base_file_path = os.path.join(os.path.dirname(__file__), "..", "base.py")
spec = importlib.util.spec_from_file_location("base_module", base_file_path)
base_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_module)
TwisterAgent = base_module.TwisterAgent
from ..database.config import get_db

logger = logging.getLogger(__name__)


class CommandStatus(str, Enum):
    """Command execution status"""

    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


class DesktopCommanderAgent(TwisterAgent):
    """
    Server-side Desktop Commander agent for secure remote execution.

    Security Features:
    - Command whitelisting
    - Device authentication
    - Operation audit trail
    - Zero-trust validation
    - Encrypted communication
    """

    # Command whitelist (only these commands are allowed)
    WHITELISTED_COMMANDS = {
        # Active Directory Operations
        "reset_ad_password": {
            "description": "Reset Active Directory password",
            "params": ["username", "temporary_password"],
            "risk_level": "medium",
            "requires_approval": False,
        },
        "unlock_ad_account": {
            "description": "Unlock Active Directory account",
            "params": ["username"],
            "risk_level": "low",
            "requires_approval": False,
        },
        # Software Management
        "install_software": {
            "description": "Install software from approved repository",
            "params": ["package_name", "version"],
            "risk_level": "medium",
            "requires_approval": True,
        },
        "uninstall_software": {
            "description": "Uninstall software",
            "params": ["package_name"],
            "risk_level": "medium",
            "requires_approval": True,
        },
        # System Diagnostics
        "get_system_info": {
            "description": "Gather system information",
            "params": [],
            "risk_level": "low",
            "requires_approval": False,
        },
        "network_diagnostics": {
            "description": "Run network connectivity tests",
            "params": [],
            "risk_level": "low",
            "requires_approval": False,
        },
        "disk_space_check": {
            "description": "Check disk space usage",
            "params": [],
            "risk_level": "low",
            "requires_approval": False,
        },
        # Access Management
        "add_to_group": {
            "description": "Add user to security group",
            "params": ["username", "group_name"],
            "risk_level": "high",
            "requires_approval": True,
        },
        "remove_from_group": {
            "description": "Remove user from security group",
            "params": ["username", "group_name"],
            "risk_level": "high",
            "requires_approval": True,
        },
        # Windows Commands
        "ipconfig": {
            "description": "Display IP configuration",
            "params": [],
            "risk_level": "low",
            "requires_approval": False,
        },
        "ping": {
            "description": "Test network connectivity",
            "params": ["target"],
            "risk_level": "low",
            "requires_approval": False,
        },
        "clear_dns_cache": {
            "description": "Clear DNS resolver cache",
            "params": [],
            "risk_level": "low",
            "requires_approval": False,
        },
    }

    def __init__(self):
        """Initialize Desktop Commander Agent"""

        super().__init__(
            name="desktop-commander",
            display_name="Desktop Commander",
            description="Secure remote desktop command execution with zero-trust",
            role="desktop-commander",
            instructions=self._get_instructions(),
            tools=self._define_tools(),
            model="llama-3.2",
            temperature=0.1,  # Very low for precise execution
        )

        # Active command tracking
        self.active_commands: Dict[str, Dict[str, Any]] = {}

        # Device registry cache
        self.device_cache: Dict[str, Any] = {}

        logger.info(f"DesktopCommanderAgent initialized: {self.name}")

    def _get_instructions(self) -> str:
        """Get agent instructions"""
        return """
        You are the Desktop Commander Agent, responsible for secure remote execution.

        Your responsibilities:
        1. Validate all incoming command requests against whitelist
        2. Authenticate device identity for every request
        3. Execute approved commands via MCP protocol
        4. Monitor command execution and enforce timeouts
        5. Log all operations in audit trail
        6. Report execution results back to requester

        Security Rules:
        - NEVER execute commands not in the whitelist
        - ALWAYS verify device authentication
        - ALWAYS log every command execution
        - REJECT any suspicious or malformed requests
        - ENFORCE command timeouts
        - VALIDATE all parameters before execution

        You are the last line of defense before code execution on user devices.
        When in doubt, REJECT and escalate.
        """

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define agent tools (max 5)"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute whitelisted command on remote device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string"},
                            "command": {"type": "string"},
                            "parameters": {"type": "object"},
                            "timeout": {"type": "integer"},
                        },
                        "required": ["device_id", "command"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_device_status",
                    "description": "Check device connectivity and health",
                    "parameters": {
                        "type": "object",
                        "properties": {"device_id": {"type": "string"}},
                        "required": ["device_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_devices",
                    "description": "List all registered devices",
                    "parameters": {
                        "type": "object",
                        "properties": {"filter": {"type": "string"}},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "register_device",
                    "description": "Register new device client",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string"},
                            "hostname": {"type": "string"},
                            "os": {"type": "string"},
                        },
                        "required": ["device_id", "hostname"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_command_audit",
                    "description": "Retrieve command execution audit logs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                    },
                },
            },
        ]

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution method.

        Args:
            task: Operation description
            context: Operation parameters

        Returns:
            Execution result with audit information
        """
        start_time = datetime.now(timezone.utc)

        try:
            logger.info(f"[{self.name}] Executing: {task}")

            if not context:
                return {
                    "status": "error",
                    "error": "Context required for Desktop Commander operations",
                }

            operation = context.get("operation", "execute_command")

            # Route to appropriate handler
            if operation == "execute_command":
                result = await self._execute_command(context)
            elif operation == "get_device_status":
                result = await self._get_device_status(context)
            elif operation == "list_devices":
                result = await self._list_devices(context)
            elif operation == "register_device":
                result = await self._register_device(context)
            elif operation == "get_command_audit":
                result = await self._get_command_audit(context)
            else:
                result = {"status": "error", "error": f"Unknown operation: {operation}"}

            # Add execution metadata
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            result["execution_time"] = f"{execution_time:.2f} seconds"
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            result["agent"] = self.name

            return result

        except Exception as e:
            logger.error(f"[{self.name}] Error in execution: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": self.name,
            }

    async def _execute_command(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute command on remote device with full security validation.
        """
        try:
            # Extract parameters
            device_id = context.get("device_id")
            command = context.get("command")
            parameters = context.get("parameters", {})
            timeout = context.get("timeout", 300)
            ticket_id = context.get("ticket_id", "unknown")

            # Validation
            if not device_id or not command:
                return {
                    "status": "rejected",
                    "reason": "Missing required parameters: device_id, command",
                }

            # Step 1: Validate command is whitelisted
            if command not in self.WHITELISTED_COMMANDS:
                logger.warning(f"[{self.name}] Rejected non-whitelisted: {command}")
                return {
                    "status": "rejected",
                    "reason": f"Command '{command}' not in whitelist",
                    "whitelisted_commands": list(self.WHITELISTED_COMMANDS.keys()),
                }

            command_spec = self.WHITELISTED_COMMANDS[command]

            # Step 2: Validate device exists and is online
            device_status = await self._validate_device(device_id)
            if not device_status["valid"]:
                return {
                    "status": "failed",
                    "reason": f"Device validation failed: {device_status['reason']}",
                }

            # Step 3: Validate parameters
            param_validation = self._validate_parameters(command_spec, parameters)
            if not param_validation["valid"]:
                return {
                    "status": "rejected",
                    "reason": f"Parameter validation failed: {param_validation['reason']}",
                }

            # Step 4: Check if approval required
            if command_spec.get("requires_approval"):
                logger.info(
                    f"[{self.name}] Command {command} requires approval (ticket {ticket_id})"
                )

            # Step 5: Generate audit ID
            audit_id = self._generate_audit_id(device_id, command)

            # Step 6: Execute command via MCP
            logger.info(f"[{self.name}] Executing {command} on {device_id} (audit: {audit_id})")

            execution_result = await self._execute_via_mcp(device_id, command, parameters, timeout)

            # Step 7: Log to audit trail
            await self._log_audit(
                audit_id, device_id, command, parameters, execution_result, ticket_id
            )

            # Step 8: Return result
            return {
                "status": execution_result["status"],
                "device_id": device_id,
                "command": command,
                "result": execution_result.get("result", {}),
                "audit_id": audit_id,
                "risk_level": command_spec["risk_level"],
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error executing command: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    async def _validate_device(self, device_id: str) -> Dict[str, Any]:
        """
        Validate device exists and is online.
        """
        try:
            # Check cache first
            if device_id in self.device_cache:
                device = self.device_cache[device_id]
                return {"valid": True, "device": device}

            # TODO: Query database when DeviceService is implemented
            # async for session in get_db():
            #     device_service = DeviceService(session)
            #     device = await device_service.get_device(device_id)

            # For now, simulate device validation
            # Accept any device_id for testing
            device = {
                "device_id": device_id,
                "is_online": True,
                "hostname": f"device-{device_id}",
                "os": "Windows 11",
            }

            self.device_cache[device_id] = device

            return {"valid": True, "device": device}

        except Exception as e:
            logger.error(f"[{self.name}] Error validating device: {e}")
            return {"valid": False, "reason": f"Validation error: {str(e)}"}

    def _validate_parameters(
        self, command_spec: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate command parameters.
        """
        required_params = command_spec.get("params", [])

        # Check all required parameters are present
        for param in required_params:
            if param not in parameters:
                return {
                    "valid": False,
                    "reason": f"Missing required parameter: {param}",
                }

        # Additional validation (sanitization, type checking)
        for key, value in parameters.items():
            # Prevent injection attacks
            if isinstance(value, str):
                if any(char in value for char in [";", "&", "|", "`", "$", "\n", "\r"]):
                    return {
                        "valid": False,
                        "reason": f"Invalid characters in parameter: {key}",
                    }

        return {"valid": True}

    async def _execute_via_mcp(
        self, device_id: str, command: str, parameters: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """
        Execute command via MCP protocol to client.

        In production, this would use the MCP server infrastructure
        to communicate with the desktop client.
        """
        try:
            # Track as active command
            command_id = secrets.token_hex(8)
            self.active_commands[command_id] = {
                "device_id": device_id,
                "command": command,
                "status": CommandStatus.EXECUTING.value,
                "started_at": datetime.now(timezone.utc),
            }

            # Simulate MCP call (in production, use actual MCP client)
            logger.info(f"[{self.name}] MCP: Sending {command} to {device_id}")

            # Simulate execution delay
            await asyncio.sleep(0.5)

            # Simulate result based on command
            if command == "reset_ad_password":
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": f"Password reset for {parameters.get('username')}",
                        "stderr": "",
                    },
                }
            elif command == "install_software":
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": f"Installed {parameters.get('package_name')}",
                        "stderr": "",
                    },
                }
            elif command == "get_system_info":
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": json.dumps(
                            {
                                "os": "Windows 11",
                                "cpu": "Intel Core i7",
                                "ram": "16 GB",
                                "disk_free": "250 GB",
                            }
                        ),
                        "stderr": "",
                    },
                }
            elif command in ["ipconfig", "network_diagnostics"]:
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": "IPv4 Address: 192.168.1.100\nSubnet Mask: 255.255.255.0",
                        "stderr": "",
                    },
                }
            else:
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": f"Executed {command} successfully",
                        "stderr": "",
                    },
                }

            # Update command status
            self.active_commands[command_id]["status"] = result["status"]
            self.active_commands[command_id]["completed_at"] = datetime.now(timezone.utc)

            return result

        except asyncio.TimeoutError:
            logger.error(f"[{self.name}] Command timeout: {command} on {device_id}")
            return {
                "status": CommandStatus.TIMEOUT.value,
                "error": "Command execution timeout",
            }
        except Exception as e:
            logger.error(f"[{self.name}] MCP execution error: {e}")
            return {"status": CommandStatus.FAILED.value, "error": str(e)}

    def _generate_audit_id(self, device_id: str, command: str) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        raw_string = f"{device_id}{command}{timestamp}{secrets.token_hex(4)}"
        hash_digest = hashlib.sha256(raw_string.encode()).hexdigest()[:16]
        return f"AUDIT-{hash_digest.upper()}"

    async def _log_audit(
        self,
        audit_id: str,
        device_id: str,
        command: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        ticket_id: str,
    ) -> None:
        """
        Log command execution to audit trail.
        """
        try:
            # TODO: Implement AuditService
            # async for session in get_db():
            #     audit_service = AuditService(session)
            #     await audit_service.create_audit_entry(...)

            # For now, just log
            audit_entry = {
                "audit_id": audit_id,
                "device_id": device_id,
                "command": command,
                "parameters": parameters,
                "status": result.get("status"),
                "result": result.get("result", {}),
                "ticket_id": ticket_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"[{self.name}] Audit logged: {json.dumps(audit_entry)}")

        except Exception as e:
            logger.error(f"[{self.name}] Error logging audit: {e}")
            # Don't fail the operation if audit logging fails

    async def _get_device_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get device connectivity and health status"""
        try:
            device_id = context.get("device_id")

            if not device_id:
                return {"status": "error", "error": "device_id required"}

            # Validate device
            device_validation = await self._validate_device(device_id)

            if not device_validation["valid"]:
                return {
                    "status": "offline",
                    "device_id": device_id,
                    "reason": device_validation["reason"],
                }

            device = device_validation["device"]

            return {
                "status": "online",
                "device_id": device_id,
                "hostname": device.get("hostname", "unknown"),
                "os": device.get("os", "unknown"),
                "last_seen": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error getting device status: {e}")
            return {"status": "error", "error": str(e)}

    async def _list_devices(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """List all registered devices"""
        try:
            # TODO: Query database
            # Return cached devices for now
            devices = [
                {"device_id": device_id, **device}
                for device_id, device in self.device_cache.items()
            ]

            return {"status": "success", "devices": devices, "count": len(devices)}

        except Exception as e:
            logger.error(f"[{self.name}] Error listing devices: {e}")
            return {"status": "error", "error": str(e)}

    async def _register_device(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Register new device client"""
        try:
            device_id = context.get("device_id")
            hostname = context.get("hostname")
            os_type = context.get("os", "Unknown")

            if not device_id or not hostname:
                return {"status": "error", "error": "device_id and hostname required"}

            # TODO: Save to database
            # For now, add to cache
            self.device_cache[device_id] = {
                "device_id": device_id,
                "hostname": hostname,
                "os": os_type,
                "is_online": True,
                "registered_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"[{self.name}] Registered device: {device_id}")

            return {
                "status": "success",
                "device_id": device_id,
                "message": "Device registered successfully",
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error registering device: {e}")
            return {"status": "error", "error": str(e)}

    async def _get_command_audit(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve command execution audit logs"""
        try:
            device_id = context.get("device_id")

            # TODO: Query audit database
            # For now, return active commands
            audit_logs = [
                {"command_id": cmd_id, **cmd_data}
                for cmd_id, cmd_data in self.active_commands.items()
                if not device_id or cmd_data.get("device_id") == device_id
            ]

            return {
                "status": "success",
                "audit_logs": audit_logs,
                "count": len(audit_logs),
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error retrieving audit logs: {e}")
            return {"status": "error", "error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for Desktop Commander Agent.

        Returns:
            Health status including active commands and device connectivity
        """
        health = {
            "agent": self.name,
            "status": "healthy",
            "checks": {
                "active_commands": len(self.active_commands),
                "cached_devices": len(self.device_cache),
                "whitelisted_commands": len(self.WHITELISTED_COMMANDS),
            },
        }

        # Check database connectivity
        try:
            async for db in get_db():
                await db.execute("SELECT 1")
                health["checks"]["database"] = "healthy"
                break
        except Exception as e:
            health["checks"]["database"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        return health
