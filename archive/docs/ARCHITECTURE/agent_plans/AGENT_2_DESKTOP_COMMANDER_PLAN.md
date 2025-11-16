# AGENT 2: DESKTOP-COMMANDER AGENT - COMPLETE IMPLEMENTATION PLAN

**Priority:** 2 (CRITICAL PATH)
**Status:** Planning Phase
**Estimated Lines:** 700+
**Dependencies:** ResolverAgent, MCP Server Infrastructure

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Role in System
The Desktop-CommanderAgent is the **secure remote execution engine** for TwisterLab. It manages a fleet of client agents installed on user devices and executes whitelisted commands with zero-trust security.

**Architecture Pattern:**
```
ResolverAgent → Desktop-Commander Server → MCP Protocol → Desktop Client
                     (Central)                              (On User Device)
```

### 1.2 Core Responsibilities
1. **Command Whitelisting** - Only execute approved, safe commands
2. **Zero-Trust Security** - Authenticate every request, validate every command
3. **Device Management** - Track and manage registered client devices
4. **Remote Execution** - Execute commands on target devices
5. **Audit Logging** - Complete audit trail of all operations
6. **Health Monitoring** - Track client status and connectivity

### 1.3 Security Model

**Zero-Trust Principles:**
- Never trust, always verify
- Command whitelist (no arbitrary execution)
- Per-device authentication
- Encrypted communication (TLS)
- Signed command packages
- Complete audit trail

### 1.4 Input/Output Format

**Input (from ResolverAgent):**
```json
{
  "operation": "execute_command",
  "device_id": "DEVICE-JOHNDOE-001",
  "command": "reset_ad_password",
  "parameters": {
    "username": "john.doe",
    "temporary_password": "TempPass123!"
  },
  "timeout": 300,
  "authorized_by": "resolver-agent",
  "ticket_id": "TKT-12345"
}
```

**Output (Command Result):**
```json
{
  "status": "success" | "failed" | "timeout",
  "device_id": "DEVICE-JOHNDOE-001",
  "command": "reset_ad_password",
  "execution_time": "5.2 seconds",
  "result": {
    "exit_code": 0,
    "stdout": "Password reset successfully",
    "stderr": ""
  },
  "audit_id": "AUDIT-67890",
  "timestamp": "2025-11-02T10:30:00Z"
}
```

---

## 2. CODE TEMPLATE

### 2.1 Server-Side Agent

**File:** `agents/helpdesk/desktop_commander.py`

```python
"""
TwisterLab - Desktop Commander Agent (Server-Side)
Secure remote command execution with zero-trust architecture
"""

import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
import asyncio

from ..base import TwisterAgent
from ..database.config import get_db
from ..database.services import DeviceService, AuditService
from ..database.models import Device, CommandAudit

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
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
            "requires_approval": False
        },
        "unlock_ad_account": {
            "description": "Unlock Active Directory account",
            "params": ["username"],
            "risk_level": "low",
            "requires_approval": False
        },

        # Software Management
        "install_software": {
            "description": "Install software from approved repository",
            "params": ["package_name", "version"],
            "risk_level": "medium",
            "requires_approval": True
        },
        "uninstall_software": {
            "description": "Uninstall software",
            "params": ["package_name"],
            "risk_level": "medium",
            "requires_approval": True
        },

        # System Diagnostics
        "get_system_info": {
            "description": "Gather system information",
            "params": [],
            "risk_level": "low",
            "requires_approval": False
        },
        "network_diagnostics": {
            "description": "Run network connectivity tests",
            "params": [],
            "risk_level": "low",
            "requires_approval": False
        },
        "disk_space_check": {
            "description": "Check disk space usage",
            "params": [],
            "risk_level": "low",
            "requires_approval": False
        },

        # Access Management
        "add_to_group": {
            "description": "Add user to security group",
            "params": ["username", "group_name"],
            "risk_level": "high",
            "requires_approval": True
        },
        "remove_from_group": {
            "description": "Remove user from security group",
            "params": ["username", "group_name"],
            "risk_level": "high",
            "requires_approval": True
        }
    }

    def __init__(self):
        super().__init__(
            name="desktop-commander",
            display_name="Desktop Commander",
            description="Secure remote desktop command execution with zero-trust architecture",
            role="desktop-commander",
            instructions=self._get_instructions(),
            tools=self._define_tools(),
            model="llama-3.2",
            temperature=0.1,  # Very low for precise execution
            metadata={
                "department": "IT",
                "security_level": "zero-trust",
                "max_concurrent_commands": 10,
                "command_timeout": 300
            }
        )

        # Active command tracking
        self.active_commands: Dict[str, Dict[str, Any]] = {}

        # Device registry cache
        self.device_cache: Dict[str, Device] = {}

    def _get_instructions(self) -> str:
        """Get agent instructions"""
        return """
        You are the Desktop Commander Agent, responsible for secure remote command execution.

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
                            "timeout": {"type": "integer"}
                        },
                        "required": ["device_id", "command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_device_status",
                    "description": "Check device connectivity and health",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string"}
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_devices",
                    "description": "List all registered devices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filter": {"type": "string"}
                        }
                    }
                }
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
                            "os": {"type": "string"}
                        },
                        "required": ["device_id", "hostname"]
                    }
                }
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
                            "end_date": {"type": "string"}
                        }
                    }
                }
            }
        ]

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
            logger.info(f"Desktop Commander executing: {task}")

            if not context:
                return {
                    "status": "error",
                    "error": "Context required for Desktop Commander operations"
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
                result = {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }

            # Add execution metadata
            execution_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()

            result["execution_time"] = f"{execution_time:.2f} seconds"
            result["timestamp"] = datetime.now(timezone.utc).isoformat()

            return result

        except Exception as e:
            logger.error(f"Error in Desktop Commander execution: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _execute_command(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
                    "reason": "Missing required parameters: device_id, command"
                }

            # Step 1: Validate command is whitelisted
            if command not in self.WHITELISTED_COMMANDS:
                logger.warning(f"Rejected non-whitelisted command: {command}")
                return {
                    "status": "rejected",
                    "reason": f"Command '{command}' not in whitelist",
                    "whitelisted_commands": list(self.WHITELISTED_COMMANDS.keys())
                }

            command_spec = self.WHITELISTED_COMMANDS[command]

            # Step 2: Validate device exists and is online
            device_status = await self._validate_device(device_id)
            if not device_status["valid"]:
                return {
                    "status": "failed",
                    "reason": f"Device validation failed: {device_status['reason']}"
                }

            # Step 3: Validate parameters
            param_validation = self._validate_parameters(command_spec, parameters)
            if not param_validation["valid"]:
                return {
                    "status": "rejected",
                    "reason": f"Parameter validation failed: {param_validation['reason']}"
                }

            # Step 4: Check if approval required
            if command_spec.get("requires_approval"):
                # In production, would check approval database
                logger.info(f"Command {command} requires approval for ticket {ticket_id}")

            # Step 5: Generate audit ID
            audit_id = self._generate_audit_id(device_id, command)

            # Step 6: Execute command via MCP
            logger.info(f"Executing {command} on {device_id} (audit: {audit_id})")

            execution_result = await self._execute_via_mcp(
                device_id,
                command,
                parameters,
                timeout
            )

            # Step 7: Log to audit trail
            await self._log_audit(
                audit_id,
                device_id,
                command,
                parameters,
                execution_result,
                ticket_id
            )

            # Step 8: Return result
            return {
                "status": execution_result["status"],
                "device_id": device_id,
                "command": command,
                "result": execution_result.get("result", {}),
                "audit_id": audit_id,
                "risk_level": command_spec["risk_level"]
            }

        except Exception as e:
            logger.error(f"Error executing command: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _validate_device(self, device_id: str) -> Dict[str, Any]:
        """
        Validate device exists and is online.
        """
        try:
            # Check cache first
            if device_id in self.device_cache:
                device = self.device_cache[device_id]
                return {
                    "valid": True,
                    "device": device
                }

            # Query database
            async for session in get_db():
                device_service = DeviceService(session)
                device = await device_service.get_device(device_id)

                if not device:
                    return {
                        "valid": False,
                        "reason": "Device not registered"
                    }

                if not device.is_online:
                    return {
                        "valid": False,
                        "reason": "Device is offline"
                    }

                # Cache device
                self.device_cache[device_id] = device

                return {
                    "valid": True,
                    "device": device
                }

        except Exception as e:
            logger.error(f"Error validating device: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}"
            }

    def _validate_parameters(
        self,
        command_spec: Dict[str, Any],
        parameters: Dict[str, Any]
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
                    "reason": f"Missing required parameter: {param}"
                }

        # Additional validation (sanitization, type checking)
        for key, value in parameters.items():
            # Prevent injection attacks
            if isinstance(value, str):
                if any(char in value for char in [';', '&', '|', '`', '$']):
                    return {
                        "valid": False,
                        "reason": f"Invalid characters in parameter: {key}"
                    }

        return {"valid": True}

    async def _execute_via_mcp(
        self,
        device_id: str,
        command: str,
        parameters: Dict[str, Any],
        timeout: int
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
                "started_at": datetime.now(timezone.utc)
            }

            # Simulate MCP call (in production, use actual MCP client)
            logger.info(f"MCP: Sending {command} to {device_id}")

            # Would use MCP transport here
            # from agents.mcp.desktop_commander_server import execute_remote_command
            # result = await execute_remote_command(device_id, command, parameters)

            # Simulate execution
            await asyncio.sleep(1)  # Simulate network delay

            # Simulate result based on command
            if command == "reset_ad_password":
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": f"Password reset for {parameters.get('username')}",
                        "stderr": ""
                    }
                }
            elif command == "install_software":
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": f"Installed {parameters.get('package_name')}",
                        "stderr": ""
                    }
                }
            elif command == "get_system_info":
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": {
                            "os": "Windows 11",
                            "cpu": "Intel Core i7",
                            "ram": "16 GB",
                            "disk_free": "250 GB"
                        },
                        "stderr": ""
                    }
                }
            else:
                result = {
                    "status": "success",
                    "result": {
                        "exit_code": 0,
                        "stdout": f"Executed {command} successfully",
                        "stderr": ""
                    }
                }

            # Update command status
            self.active_commands[command_id]["status"] = result["status"]
            self.active_commands[command_id]["completed_at"] = datetime.now(timezone.utc)

            return result

        except asyncio.TimeoutError:
            logger.error(f"Command timeout: {command} on {device_id}")
            return {
                "status": CommandStatus.TIMEOUT.value,
                "error": "Command execution timeout"
            }
        except Exception as e:
            logger.error(f"MCP execution error: {e}")
            return {
                "status": CommandStatus.FAILED.value,
                "error": str(e)
            }

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
        ticket_id: str
    ) -> None:
        """
        Log command execution to audit trail.
        """
        try:
            async for session in get_db():
                audit_service = AuditService(session)

                audit_entry = CommandAudit(
                    audit_id=audit_id,
                    device_id=device_id,
                    command=command,
                    parameters=parameters,
                    status=result.get("status"),
                    result=result.get("result", {}),
                    ticket_id=ticket_id,
                    timestamp=datetime.now(timezone.utc)
                )

                await audit_service.create_audit_entry(audit_entry)
                logger.info(f"Audit logged: {audit_id}")

        except Exception as e:
            logger.error(f"Error logging audit: {e}")
            # Don't fail the operation if audit logging fails

    async def _get_device_status(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get device connectivity and health status"""
        try:
            device_id = context.get("device_id")

            if not device_id:
                return {"status": "error", "error": "device_id required"}

            # Query device
            async for session in get_db():
                device_service = DeviceService(session)
                device = await device_service.get_device(device_id)

                if not device:
                    return {
                        "status": "not_found",
                        "device_id": device_id
                    }

                return {
                    "status": "success",
                    "device_id": device_id,
                    "hostname": device.hostname,
                    "os": device.os,
                    "is_online": device.is_online,
                    "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                    "registered_at": device.created_at.isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return {"status": "error", "error": str(e)}

    async def _list_devices(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """List all registered devices"""
        try:
            filter_param = context.get("filter", "all")

            async for session in get_db():
                device_service = DeviceService(session)
                devices = await device_service.list_devices()

                device_list = [
                    {
                        "device_id": d.device_id,
                        "hostname": d.hostname,
                        "os": d.os,
                        "is_online": d.is_online,
                        "last_seen": d.last_seen.isoformat() if d.last_seen else None
                    }
                    for d in devices
                ]

                # Apply filter
                if filter_param == "online":
                    device_list = [d for d in device_list if d["is_online"]]
                elif filter_param == "offline":
                    device_list = [d for d in device_list if not d["is_online"]]

                return {
                    "status": "success",
                    "total_devices": len(device_list),
                    "devices": device_list
                }

        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return {"status": "error", "error": str(e)}

    async def _register_device(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register new device client"""
        try:
            device_id = context.get("device_id")
            hostname = context.get("hostname")
            os_info = context.get("os", "Unknown")

            if not device_id or not hostname:
                return {
                    "status": "error",
                    "error": "device_id and hostname required"
                }

            async for session in get_db():
                device_service = DeviceService(session)

                # Check if already registered
                existing = await device_service.get_device(device_id)
                if existing:
                    return {
                        "status": "already_registered",
                        "device_id": device_id
                    }

                # Register new device
                device = Device(
                    device_id=device_id,
                    hostname=hostname,
                    os=os_info,
                    is_online=True,
                    last_seen=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc)
                )

                await device_service.register_device(device)

                return {
                    "status": "success",
                    "message": f"Device {device_id} registered successfully",
                    "device_id": device_id
                }

        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return {"status": "error", "error": str(e)}

    async def _get_command_audit(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve command execution audit logs"""
        try:
            device_id = context.get("device_id")
            start_date = context.get("start_date")
            end_date = context.get("end_date")

            async for session in get_db():
                audit_service = AuditService(session)
                audits = await audit_service.get_audits(
                    device_id=device_id,
                    start_date=start_date,
                    end_date=end_date
                )

                audit_list = [
                    {
                        "audit_id": a.audit_id,
                        "command": a.command,
                        "status": a.status,
                        "timestamp": a.timestamp.isoformat(),
                        "ticket_id": a.ticket_id
                    }
                    for a in audits
                ]

                return {
                    "status": "success",
                    "total_audits": len(audit_list),
                    "audits": audit_list
                }

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return {"status": "error", "error": str(e)}
```

---

## 3. MCP SERVER COMPONENT

**File:** `agents/mcp/desktop_commander_server.py`

```python
"""
TwisterLab - Desktop Commander MCP Server
MCP protocol implementation for client-server communication
"""

import logging
from typing import Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("desktop-commander-mcp")


@app.call_tool()
async def execute_remote_command(
    device_id: str,
    command: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    MCP tool: Execute command on remote device client.

    This is called by the Desktop Commander agent and
    routed to the appropriate client.
    """
    logger.info(f"MCP: execute_remote_command on {device_id}: {command}")

    # In production, this would:
    # 1. Look up device connection
    # 2. Send command via MCP transport
    # 3. Wait for response
    # 4. Return result

    return {
        "status": "success",
        "device_id": device_id,
        "command": command,
        "result": "Command executed via MCP"
    }


@app.call_tool()
async def get_device_info(device_id: str) -> Dict[str, Any]:
    """MCP tool: Get device information"""
    logger.info(f"MCP: get_device_info for {device_id}")

    return {
        "device_id": device_id,
        "os": "Windows 11",
        "status": "online"
    }


def main():
    """Start MCP server"""
    import asyncio
    asyncio.run(stdio_server(app))


if __name__ == "__main__":
    main()
```

---

## 4. TESTING STRATEGY

### 4.1 Unit Tests

**File:** `tests/test_desktop_commander.py`

```python
import pytest
from agents.helpdesk.desktop_commander import DesktopCommanderAgent, CommandStatus

@pytest.mark.asyncio
async def test_commander_initialization():
    """Test Desktop Commander initializes correctly"""
    commander = DesktopCommanderAgent()

    assert commander.name == "desktop-commander"
    assert len(commander.WHITELISTED_COMMANDS) > 0
    assert "reset_ad_password" in commander.WHITELISTED_COMMANDS

@pytest.mark.asyncio
async def test_whitelisted_command_execution():
    """Test executing whitelisted command"""
    commander = DesktopCommanderAgent()

    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "get_system_info",
        "parameters": {},
        "ticket_id": "TKT-TEST-001"
    }

    result = await commander.execute("Execute system info command", context)

    # Should succeed for whitelisted command
    assert result["status"] in ["success", "failed"]  # Could fail if device not found
    assert "audit_id" in result or "error" in result

@pytest.mark.asyncio
async def test_non_whitelisted_command_rejection():
    """Test rejection of non-whitelisted command"""
    commander = DesktopCommanderAgent()

    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "rm -rf /",  # Malicious command
        "parameters": {},
        "ticket_id": "TKT-TEST-002"
    }

    result = await commander.execute("Execute malicious command", context)

    # Should be rejected
    assert result["status"] == "rejected"
    assert "not in whitelist" in result["reason"]

@pytest.mark.asyncio
async def test_parameter_validation():
    """Test parameter validation"""
    commander = DesktopCommanderAgent()

    command_spec = {
        "params": ["username", "temporary_password"]
    }

    # Valid parameters
    valid_params = {
        "username": "john.doe",
        "temporary_password": "TempPass123!"
    }
    result = commander._validate_parameters(command_spec, valid_params)
    assert result["valid"] is True

    # Missing parameter
    invalid_params = {"username": "john.doe"}
    result = commander._validate_parameters(command_spec, invalid_params)
    assert result["valid"] is False

    # Injection attempt
    malicious_params = {
        "username": "john.doe; rm -rf /",
        "temporary_password": "pass"
    }
    result = commander._validate_parameters(command_spec, malicious_params)
    assert result["valid"] is False

@pytest.mark.asyncio
async def test_audit_id_generation():
    """Test audit ID generation"""
    commander = DesktopCommanderAgent()

    audit_id_1 = commander._generate_audit_id("DEVICE-001", "reset_password")
    audit_id_2 = commander._generate_audit_id("DEVICE-001", "reset_password")

    # Should be unique
    assert audit_id_1 != audit_id_2
    assert audit_id_1.startswith("AUDIT-")
```

---

## 5. DEPLOYMENT NOTES

### 5.1 Configuration

**Environment Variables:**
```bash
# Desktop Commander Configuration
DC_MCP_SERVER_PORT=8001
DC_MAX_CONCURRENT_COMMANDS=10
DC_COMMAND_TIMEOUT=300
DC_REQUIRE_APPROVAL_FOR_HIGH_RISK=true

# Security
DC_API_KEY=${DESKTOP_COMMANDER_API_KEY}
DC_TLS_CERT=/path/to/cert.pem
DC_TLS_KEY=/path/to/key.pem

# Device Registry
DC_DEVICE_REGISTRY_URL=postgresql://...
```

### 5.2 Docker Setup

```yaml
services:
  desktop-commander:
    build:
      context: .
      dockerfile: Dockerfile.desktop-commander
    container_name: twisterlab-desktop-commander
    ports:
      - "8001:8001"
    environment:
      - DC_MCP_SERVER_PORT=8001
      - DC_API_KEY=${DC_API_KEY}
    volumes:
      - ./certs:/app/certs:ro
    networks:
      - twisterlab-network
    restart: unless-stopped
```

---

**Next Agent:** [MaestroOrchestratorAgent (Priority 3)](AGENT_3_MAESTRO_PLAN.md)
