"""
Test Desktop Commander MCP Integration
"""

from unittest.mock import patch

import pytest

from agents.helpdesk.desktop_commander import DesktopCommanderAgent


class TestDesktopCommanderMCPIntegration:
    """Test MCP integration for Desktop Commander Agent."""

    @pytest.fixture
    def agent(self):
        """Create a Desktop Commander agent instance."""
        return DesktopCommanderAgent()

    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self, agent):
        """Test that MCP client is properly initialized."""
        assert hasattr(agent, "mcp_client")
        assert hasattr(agent, "_mcp_started")
        assert agent._mcp_started is False

    @pytest.mark.asyncio
    async def test_execute_command_mcp_integration(self, agent):
        """Test execute_command uses MCP client instead of simulation."""
        # Mock MCP client
        mock_result = {
            "status": "success",
            "command": "systeminfo",
            "output": "System info output",
            "execution_time": 1.5,
            "device_id": "test-device",
        }

        with patch.object(
            agent.mcp_client, "execute_command", return_value=mock_result
        ) as mock_execute:
            with patch.object(agent.mcp_client, "start") as mock_start:

                result = await agent.execute_command(
                    device_id="test-device", command="systeminfo", timeout=300
                )

                # Verify MCP client was started
                mock_start.assert_called_once()

                # Verify MCP execute_command was called
                mock_execute.assert_called_once_with("test-device", "systeminfo", 300)

                # Verify result is returned from MCP client
                assert result == mock_result

    @pytest.mark.asyncio
    async def test_deploy_package_mcp_integration(self, agent):
        """Test deploy_package uses MCP client instead of simulation."""
        mock_result = {
            "status": "success",
            "package_url": "http://example.com/package.msi",
            "install_args": "/quiet",
            "deployment_result": "Package deployed successfully",
        }

        with patch.object(
            agent.mcp_client, "deploy_package", return_value=mock_result
        ) as mock_deploy:
            with patch.object(agent.mcp_client, "start") as mock_start:

                result = await agent.deploy_package(
                    device_id="test-device",
                    package_url="http://example.com/package.msi",
                    install_args="/quiet",
                )

                # Verify MCP client was started
                mock_start.assert_called_once()

                # Verify MCP deploy_package was called
                mock_deploy.assert_called_once_with(
                    "test-device", "http://example.com/package.msi", "/quiet"
                )

                # Verify result is returned from MCP client
                assert result == mock_result

    @pytest.mark.asyncio
    async def test_get_system_info_mcp_integration(self, agent):
        """Test get_system_info uses MCP client instead of simulation."""
        mock_result = {
            "status": "success",
            "info_type": "hardware",
            "system_info": {
                "cpu": "Intel i7",
                "memory": "16GB",
                "disk": "512GB SSD",
            },
        }

        with patch.object(
            agent.mcp_client, "get_system_info", return_value=mock_result
        ) as mock_get_info:
            with patch.object(agent.mcp_client, "start") as mock_start:

                result = await agent.get_system_info(device_id="test-device", info_type="hardware")

                # Verify MCP client was started
                mock_start.assert_called_once()

                # Verify MCP get_system_info was called
                mock_get_info.assert_called_once_with("test-device", "hardware")

                # Verify result is returned from MCP client
                assert result == mock_result

    @pytest.mark.asyncio
    async def test_mcp_client_started_only_once(self, agent):
        """Test MCP client started only once across operations."""
        mock_result = {"status": "success"}

        with patch.object(
            agent.mcp_client, "execute_command", return_value=mock_result
        ) as mock_execute:
            with patch.object(agent.mcp_client, "start") as mock_start:

                # First call
                await agent.execute_command("device1", "systeminfo")
                # Second call
                await agent.execute_command("device2", "ipconfig")

                # Verify start was called only once
                mock_start.assert_called_once()

                # Verify execute_command was called twice
                assert mock_execute.call_count == 2

    def test_command_validation_still_works(self, agent):
        """Test that command validation still works with MCP integration."""
        # Test allowed command
        assert agent._is_command_allowed("systeminfo") is True

        # Test disallowed command
        assert agent._is_command_allowed("format c:") is False

    @pytest.mark.asyncio
    async def test_execute_method_routes_to_mcp(self, agent):
        """Test that the main execute method routes to MCP methods."""
        context = {
            "command_type": "execute_command",
            "device_id": "test-device",
            "command": "systeminfo",
            "timeout": 300,
        }

        mock_result = {
            "status": "success",
            "command": "systeminfo",
            "output": "Mock output",
        }

        with patch.object(agent, "execute_command", return_value=mock_result) as mock_execute_cmd:

            result = await agent.execute("Execute systeminfo on test-device", context)

            mock_execute_cmd.assert_called_once_with(
                device_id="test-device", command="systeminfo", timeout=300
            )

            # The execute method adds extra fields to the result
            # Check that the core result is included
            for key, value in mock_result.items():
                assert result[key] == value
