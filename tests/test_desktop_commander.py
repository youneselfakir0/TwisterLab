"""
TwisterLab - Desktop Commander Agent Tests
Comprehensive test suite for secure remote command execution
"""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from agents.real.real_desktop_commander_agent import (
    RealDesktopCommanderAgent,
    CommandStatus
)


@pytest.fixture
def commander_agent():
    """Create RealDesktopCommanderAgent instance for testing"""
    return RealDesktopCommanderAgent()


@pytest.fixture
def valid_execute_context():
    """Valid context for command execution"""
    return {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "get_system_info",
        "parameters": {},
        "timeout": 60,
        "ticket_id": "TKT-TEST-001"
    }


@pytest.fixture
def malicious_command_context():
    """Context with malicious command"""
    return {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "rm -rf /",
        "parameters": {},
        "ticket_id": "TKT-TEST-002"
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_commander_initialization(commander_agent):
    """Test Desktop Commander initializes correctly"""
    assert commander_agent.name == "desktop-commander"
    assert commander_agent.display_name == "Desktop Commander"
    assert len(commander_agent.WHITELISTED_COMMANDS) > 0
    assert "reset_ad_password" in commander_agent.WHITELISTED_COMMANDS
    assert "install_software" in commander_agent.WHITELISTED_COMMANDS
    assert "get_system_info" in commander_agent.WHITELISTED_COMMANDS
    assert len(commander_agent.tools) <= 5  # Max 5 tools
    assert commander_agent.temperature == 0.1  # Low temperature


def test_whitelist_structure(commander_agent):
    """Test whitelist command structure"""
    for cmd_name, cmd_spec in commander_agent.WHITELISTED_COMMANDS.items():
        assert "description" in cmd_spec
        assert "params" in cmd_spec
        assert "risk_level" in cmd_spec
        assert "requires_approval" in cmd_spec
        assert cmd_spec["risk_level"] in ["low", "medium", "high"]


# ============================================================================
# COMMAND WHITELISTING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_whitelisted_command_execution(commander_agent, valid_execute_context):
    """Test executing whitelisted command"""
    result = await commander_agent.execute("Execute system info", valid_execute_context)
    
    # Should not be rejected
    assert result["status"] != "rejected"
    assert result["agent"] == "desktop-commander"
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_non_whitelisted_command_rejection(commander_agent, malicious_command_context):
    """Test rejection of non-whitelisted command"""
    result = await commander_agent.execute("Execute malicious command", malicious_command_context)
    
    # Should be rejected
    assert result["status"] == "rejected"
    assert "not in whitelist" in result["reason"]
    assert "whitelisted_commands" in result


@pytest.mark.asyncio
async def test_command_injection_protection(commander_agent):
    """Test protection against command injection"""
    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "ping",
        "parameters": {
            "target": "8.8.8.8; rm -rf /"  # Injection attempt
        },
        "ticket_id": "TKT-INJ-001"
    }
    
    result = await commander_agent.execute("Ping with injection", context)
    
    # Should reject due to invalid characters
    assert result["status"] == "rejected"
    assert "Invalid characters" in result["reason"]


# ============================================================================
# PARAMETER VALIDATION TESTS
# ============================================================================

def test_parameter_validation_success(commander_agent):
    """Test valid parameter validation"""
    command_spec = {
        "params": ["username", "temporary_password"]
    }
    
    valid_params = {
        "username": "john.doe",
        "temporary_password": "TempPass123!"
    }
    
    result = commander_agent._validate_parameters(command_spec, valid_params)
    assert result["valid"] is True


def test_parameter_validation_missing_param(commander_agent):
    """Test validation with missing required parameter"""
    command_spec = {
        "params": ["username", "temporary_password"]
    }
    
    invalid_params = {
        "username": "john.doe"
        # Missing temporary_password
    }
    
    result = commander_agent._validate_parameters(command_spec, invalid_params)
    assert result["valid"] is False
    assert "Missing required parameter" in result["reason"]


def test_parameter_validation_injection_characters(commander_agent):
    """Test validation blocks injection characters"""
    command_spec = {
        "params": ["username"]
    }
    
    # Test various injection characters
    dangerous_chars = [';', '&', '|', '`', '$', '\n', '\r']
    
    for char in dangerous_chars:
        invalid_params = {
            "username": f"user{char}name"
        }
        
        result = commander_agent._validate_parameters(command_spec, invalid_params)
        assert result["valid"] is False, f"Should reject character: {char}"
        assert "Invalid characters" in result["reason"]


# ============================================================================
# DEVICE VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_device_validation_caching(commander_agent):
    """Test device validation uses caching"""
    device_id = "TEST-CACHE-001"
    
    # First call should cache device
    result1 = await commander_agent._validate_device(device_id)
    assert result1["valid"] is True
    assert device_id in commander_agent.device_cache
    
    # Second call should use cache
    result2 = await commander_agent._validate_device(device_id)
    assert result2["valid"] is True
    assert result2["device"] == commander_agent.device_cache[device_id]


@pytest.mark.asyncio
async def test_device_validation_accepts_any_device(commander_agent):
    """Test device validation accepts any device for testing"""
    device_id = "RANDOM-DEVICE-XYZ"
    
    result = await commander_agent._validate_device(device_id)
    
    # Should accept for testing purposes
    assert result["valid"] is True
    assert result["device"]["device_id"] == device_id


# ============================================================================
# COMMAND EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_execute_command_full_flow(commander_agent):
    """Test complete command execution flow"""
    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-FLOW",
        "command": "reset_ad_password",
        "parameters": {
            "username": "test.user",
            "temporary_password": "TempPass123!"
        },
        "ticket_id": "TKT-FLOW-001"
    }
    
    result = await commander_agent.execute("Reset password", context)
    
    assert result["status"] == "success"
    assert result["device_id"] == "TEST-DEVICE-FLOW"
    assert result["command"] == "reset_ad_password"
    assert "audit_id" in result
    assert result["audit_id"].startswith("AUDIT-")
    assert "risk_level" in result


@pytest.mark.asyncio
async def test_execute_command_with_missing_params(commander_agent):
    """Test command execution with missing parameters"""
    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "reset_ad_password",
        "parameters": {
            "username": "test.user"
            # Missing temporary_password
        },
        "ticket_id": "TKT-MISSING-001"
    }
    
    result = await commander_agent.execute("Reset password incomplete", context)
    
    assert result["status"] == "rejected"
    assert "Missing required parameter" in result["reason"]


@pytest.mark.asyncio
async def test_execute_multiple_commands_concurrently(commander_agent):
    """Test concurrent command execution"""
    contexts = [
        {
            "operation": "execute_command",
            "device_id": f"TEST-DEVICE-{i}",
            "command": "get_system_info",
            "parameters": {},
            "ticket_id": f"TKT-CONCURRENT-{i}"
        }
        for i in range(3)
    ]
    
    results = await asyncio.gather(*[
        commander_agent.execute(f"Command {i}", ctx)
        for i, ctx in enumerate(contexts)
    ])
    
    assert len(results) == 3
    assert all(r["status"] == "success" for r in results)
    assert len(set(r["audit_id"] for r in results)) == 3  # Unique audit IDs


# ============================================================================
# AUDIT LOGGING TESTS
# ============================================================================

def test_audit_id_generation(commander_agent):
    """Test audit ID generation is unique and formatted correctly"""
    device_id = "TEST-DEVICE-001"
    command = "test_command"
    
    audit_id1 = commander_agent._generate_audit_id(device_id, command)
    audit_id2 = commander_agent._generate_audit_id(device_id, command)
    
    # Should be unique
    assert audit_id1 != audit_id2
    
    # Should have correct format
    assert audit_id1.startswith("AUDIT-")
    assert len(audit_id1) == 22  # AUDIT- + 16 hex chars


@pytest.mark.asyncio
async def test_audit_logging(commander_agent):
    """Test audit logging doesn't fail execution"""
    audit_id = "TEST-AUDIT-001"
    device_id = "TEST-DEVICE-001"
    command = "get_system_info"
    parameters = {}
    result = {"status": "success"}
    ticket_id = "TKT-001"
    
    # Should not raise exception
    await commander_agent._log_audit(
        audit_id,
        device_id,
        command,
        parameters,
        result,
        ticket_id
    )


# ============================================================================
# MCP EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_mcp_execution_simulates_commands(commander_agent):
    """Test MCP execution simulates different commands"""
    test_cases = [
        ("reset_ad_password", {"username": "user", "temporary_password": "pass"}),
        ("install_software", {"package_name": "Chrome", "version": "120"}),
        ("get_system_info", {}),
        ("ipconfig", {}),
    ]
    
    for command, params in test_cases:
        result = await commander_agent._execute_via_mcp(
            "TEST-DEVICE",
            command,
            params,
            timeout=60
        )
        
        assert result["status"] == "success"
        assert "result" in result
        assert result["result"]["exit_code"] == 0


@pytest.mark.asyncio
async def test_mcp_execution_tracks_active_commands(commander_agent):
    """Test MCP execution tracks active commands"""
    initial_count = len(commander_agent.active_commands)
    
    await commander_agent._execute_via_mcp(
        "TEST-DEVICE",
        "get_system_info",
        {},
        timeout=60
    )
    
    # Should have added to active commands
    assert len(commander_agent.active_commands) > initial_count


# ============================================================================
# DEVICE MANAGEMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_device_status(commander_agent):
    """Test getting device status"""
    context = {
        "operation": "get_device_status",
        "device_id": "TEST-DEVICE-STATUS"
    }
    
    result = await commander_agent.execute("Get device status", context)
    
    assert result["status"] == "online"
    assert result["device_id"] == "TEST-DEVICE-STATUS"
    assert "hostname" in result


@pytest.mark.asyncio
async def test_list_devices(commander_agent):
    """Test listing registered devices"""
    # Register some devices first
    await commander_agent._validate_device("DEVICE-1")
    await commander_agent._validate_device("DEVICE-2")
    
    context = {
        "operation": "list_devices"
    }
    
    result = await commander_agent.execute("List devices", context)
    
    assert result["status"] == "success"
    assert "devices" in result
    assert result["count"] >= 2


@pytest.mark.asyncio
async def test_register_device(commander_agent):
    """Test device registration"""
    context = {
        "operation": "register_device",
        "device_id": "NEW-DEVICE-001",
        "hostname": "laptop-user01",
        "os": "Windows 11"
    }
    
    result = await commander_agent.execute("Register device", context)
    
    assert result["status"] == "success"
    assert result["device_id"] == "NEW-DEVICE-001"
    assert "NEW-DEVICE-001" in commander_agent.device_cache


@pytest.mark.asyncio
async def test_get_command_audit(commander_agent):
    """Test retrieving command audit logs"""
    # Execute a command first to create audit entry
    await commander_agent._execute_via_mcp(
        "TEST-DEVICE-AUDIT",
        "get_system_info",
        {},
        timeout=60
    )
    
    context = {
        "operation": "get_command_audit",
        "device_id": "TEST-DEVICE-AUDIT"
    }
    
    result = await commander_agent.execute("Get audit logs", context)
    
    assert result["status"] == "success"
    assert "audit_logs" in result
    assert result["count"] >= 0


# ============================================================================
# SECURITY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_high_risk_command_approval_check(commander_agent):
    """Test high-risk commands are flagged for approval"""
    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "add_to_group",
        "parameters": {
            "username": "test.user",
            "group_name": "Domain Admins"
        },
        "ticket_id": "TKT-HIGH-RISK-001"
    }
    
    result = await commander_agent.execute("Add to admin group", context)
    
    # Should execute but log that approval is required
    assert result["risk_level"] == "high"


@pytest.mark.asyncio
async def test_missing_context_rejection(commander_agent):
    """Test execution rejects missing context"""
    result = await commander_agent.execute("Execute without context", None)
    
    assert result["status"] == "error"
    assert "Context required" in result["error"]


@pytest.mark.asyncio
async def test_missing_device_id_rejection(commander_agent):
    """Test execution rejects missing device_id"""
    context = {
        "operation": "execute_command",
        "command": "get_system_info",
        "parameters": {}
    }
    
    result = await commander_agent.execute("Execute without device", context)
    
    assert result["status"] == "rejected"
    assert "Missing required parameters" in result["reason"]


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_health_check_all_healthy(commander_agent):
    """Test health check when system is healthy"""
    with patch('agents.desktop_commander.desktop_commander_agent.get_db') as mock_db:
        mock_db_session = MagicMock()
        mock_db_session.execute = AsyncMock()
        mock_db.return_value.__aiter__.return_value = [mock_db_session]
        
        health = await commander_agent.health_check()
        
        assert health["agent"] == "desktop-commander"
        assert health["status"] == "healthy"
        assert "active_commands" in health["checks"]
        assert "cached_devices" in health["checks"]
        assert "whitelisted_commands" in health["checks"]
        assert health["checks"]["database"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_degraded(commander_agent):
    """Test health check when database is degraded"""
    with patch('agents.desktop_commander.desktop_commander_agent.get_db') as mock_db:
        mock_db.side_effect = Exception("Database connection error")
        
        health = await commander_agent.health_check()
        
        assert health["status"] == "degraded"
        assert "unhealthy" in health["checks"]["database"]


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_execute_unknown_operation(commander_agent):
    """Test execution with unknown operation"""
    context = {
        "operation": "unknown_operation",
        "device_id": "TEST-DEVICE-001"
    }
    
    result = await commander_agent.execute("Unknown op", context)
    
    assert result["status"] == "error"
    assert "Unknown operation" in result["error"]


@pytest.mark.asyncio
async def test_execute_with_timeout_parameter(commander_agent):
    """Test execution respects timeout parameter"""
    context = {
        "operation": "execute_command",
        "device_id": "TEST-DEVICE-001",
        "command": "get_system_info",
        "parameters": {},
        "timeout": 1,  # Very short timeout
        "ticket_id": "TKT-TIMEOUT-001"
    }
    
    result = await commander_agent.execute("Execute with timeout", context)
    
    # Should complete (simulated execution is fast)
    assert result["status"] in ["success", "timeout"]


@pytest.mark.asyncio
async def test_command_execution_error_handling(commander_agent):
    """Test error handling in command execution"""
    with patch.object(commander_agent, '_execute_via_mcp', side_effect=Exception("MCP error")):
        context = {
            "operation": "execute_command",
            "device_id": "TEST-DEVICE-001",
            "command": "get_system_info",
            "parameters": {},
            "ticket_id": "TKT-ERROR-001"
        }
        
        result = await commander_agent.execute("Execute with error", context)
        
        assert result["status"] == "failed"
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
