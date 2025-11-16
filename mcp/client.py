"""
TwisterLab MCP Client
Client for Model Context Protocol communication with Desktop Commander agents
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import websockets
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPMessage(BaseModel):
    """MCP protocol message structure"""

    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class DeviceInfo(BaseModel):
    """Device registration information"""

    device_id: str
    hostname: str
    ip_address: str
    os_version: str
    agent_version: str
    last_seen: datetime
    status: str  # "online", "offline", "maintenance"


class MCPClient:
    """
    MCP Client for communicating with Desktop Commander agents.

    Handles WebSocket connections, device registration, and command execution.
    """

    def __init__(self, registry_url: str = "ws://localhost:8080/mcp"):
        self.registry_url = registry_url
        self.devices: Dict[str, DeviceInfo] = {}
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.command_history: List[Dict[str, Any]] = []
        self._running = False

    async def start(self):
        """Start the MCP client and connect to registry"""
        self._running = True
        logger.info("Starting MCP client...")

        # Connect to device registry
        try:
            async with websockets.connect(self.registry_url) as websocket:
                await self._handle_registry_connection(websocket)
        except Exception as e:
            logger.error(f"Failed to connect to MCP registry: {e}")
            # Continue with cached device information

    async def stop(self):
        """Stop the MCP client"""
        self._running = False
        logger.info("Stopping MCP client...")

        # Close all connections
        for device_id, connection in self.connections.items():
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing connection to {device_id}: {e}")

        self.connections.clear()

    async def _handle_registry_connection(self, websocket):
        """Handle connection to device registry"""
        try:
            # Send registration request
            register_msg = MCPMessage(
                method="register_server",
                params={
                    "server_name": "twisterlab_desktop_commander",
                    "capabilities": ["command_execution", "package_deployment", "system_info"],
                },
            )

            await websocket.send(register_msg.json())

            # Listen for device registrations and commands
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg = MCPMessage(**data)

                    if msg.method == "device_registered":
                        await self._handle_device_registration(msg.params)
                    elif msg.method == "device_unregistered":
                        await self._handle_device_unregistration(msg.params)
                    elif msg.method == "execute_command":
                        await self._handle_command_execution(msg)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON message: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("Registry connection closed")
        except Exception as e:
            logger.error(f"Error in registry connection: {e}")

    async def _handle_device_registration(self, params: Dict[str, Any]):
        """Handle device registration"""
        device_info = DeviceInfo(**params)
        self.devices[device_info.device_id] = device_info

        logger.info(f"Device registered: {device_info.device_id} " f"({device_info.hostname})")

        # Attempt to establish direct connection
        await self._connect_to_device(device_info.device_id)

    async def _handle_device_unregistration(self, params: Dict[str, Any]):
        """Handle device unregistration"""
        device_id = params.get("device_id")
        if device_id in self.devices:
            del self.devices[device_id]

        if device_id in self.connections:
            try:
                await self.connections[device_id].close()
            except Exception as e:
                logger.error(f"Error closing connection to {device_id}: {e}")
            del self.connections[device_id]

        logger.info(f"Device unregistered: {device_id}")

    async def _connect_to_device(self, device_id: str):
        """Establish direct WebSocket connection to device"""
        if device_id not in self.devices:
            logger.error(f"Device {device_id} not registered")
            return

        device = self.devices[device_id]
        device_ws_url = f"ws://{device.ip_address}:8081/mcp"

        try:
            websocket = await websockets.connect(device_ws_url)
            self.connections[device_id] = websocket

            # Start device message handler
            asyncio.create_task(self._handle_device_messages(device_id, websocket))

            logger.info(f"Connected to device {device_id}")

        except Exception as e:
            logger.error(f"Failed to connect to device {device_id}: {e}")

    async def _handle_device_messages(self, device_id: str, websocket):
        """Handle messages from device"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg = MCPMessage(**data)

                    # Handle device responses
                    if msg.id and msg.result:
                        # This is a response to a command
                        logger.info(f"Command result from {device_id}: " f"{msg.result}")

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from device {device_id}: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Connection to device {device_id} closed")
            if device_id in self.connections:
                del self.connections[device_id]
        except Exception as e:
            logger.error(f"Error handling device {device_id} messages: {e}")

    async def execute_command(
        self, device_id: str, command: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute command on remote device via MCP

        Args:
            device_id: Target device identifier
            command: Command to execute
            timeout: Command timeout in seconds

        Returns:
            Command execution result
        """
        if device_id not in self.connections:
            return {
                "status": "error",
                "error": f"Device {device_id} not connected",
                "available_devices": list(self.devices.keys()),
            }

        try:
            websocket = self.connections[device_id]

            # Create command message
            cmd_msg = MCPMessage(
                id=self._generate_message_id(),
                method="execute_command",
                params={
                    "command": command,
                    "timeout": timeout,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Send command
            await websocket.send(cmd_msg.json())

            # Wait for response with timeout
            response = await asyncio.wait_for(
                self._wait_for_response(websocket, cmd_msg.id), timeout=timeout
            )

            # Log command execution
            self.command_history.append(
                {
                    "device_id": device_id,
                    "command": command,
                    "timestamp": datetime.now().isoformat(),
                    "result": response,
                }
            )

            return response

        except asyncio.TimeoutError:
            return {"status": "timeout", "error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            logger.error(f"Error executing command on {device_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def _wait_for_response(self, websocket, message_id: int) -> Dict[str, Any]:
        """Wait for response to specific message"""
        # This is a simplified implementation
        # In a real implementation, you'd maintain a response queue
        try:
            message = await websocket.recv()
            data = json.loads(message)
            msg = MCPMessage(**data)

            if msg.id == message_id:
                if msg.error:
                    return {"status": "error", "error": msg.error}
                else:
                    return {"status": "success", "result": msg.result}

        except Exception as e:
            raise Exception(f"Failed to receive response: {e}")

    async def deploy_package(
        self, device_id: str, package_url: str, install_args: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy software package to remote device

        Args:
            device_id: Target device identifier
            package_url: Package download URL
            install_args: Installation arguments

        Returns:
            Deployment result
        """
        if device_id not in self.connections:
            return {"status": "error", "error": f"Device {device_id} not connected"}

        try:
            websocket = self.connections[device_id]

            deploy_msg = MCPMessage(
                id=self._generate_message_id(),
                method="deploy_package",
                params={
                    "package_url": package_url,
                    "install_args": install_args,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            await websocket.send(deploy_msg.json())

            # Wait for deployment result
            response = await asyncio.wait_for(
                self._wait_for_response(websocket, deploy_msg.id),
                timeout=600,  # 10 minutes for deployment
            )

            return response

        except Exception as e:
            logger.error(f"Error deploying package to {device_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def get_system_info(self, device_id: str, info_type: str = "all") -> Dict[str, Any]:
        """
        Get system information from remote device

        Args:
            device_id: Target device identifier
            info_type: Type of information ("hardware", "software",
                     "network", "all")

        Returns:
            System information
        """
        if device_id not in self.connections:
            return {"status": "error", "error": f"Device {device_id} not connected"}

        try:
            websocket = self.connections[device_id]

            info_msg = MCPMessage(
                id=self._generate_message_id(),
                method="get_system_info",
                params={"info_type": info_type, "timestamp": datetime.now().isoformat()},
            )

            await websocket.send(info_msg.json())

            # Wait for system info response
            response = await asyncio.wait_for(
                self._wait_for_response(websocket, info_msg.id),
                timeout=60,  # 1 minute for system info
            )

            return response

        except Exception as e:
            logger.error(f"Error getting system info from {device_id}: {e}")
            return {"status": "error", "error": str(e)}

    def get_registered_devices(self) -> List[DeviceInfo]:
        """Get list of registered devices"""
        return list(self.devices.values())

    def get_connected_devices(self) -> List[str]:
        """Get list of currently connected device IDs"""
        return list(self.connections.keys())

    def _generate_message_id(self) -> int:
        """Generate unique message ID"""
        return int(datetime.now().timestamp() * 1000000)

    async def health_check(self, device_id: str) -> bool:
        """Check if device is healthy and responding"""
        try:
            result = await self.execute_command(device_id, "echo health_check", timeout=10)
            return result.get("status") == "success"
        except Exception:
            return False
