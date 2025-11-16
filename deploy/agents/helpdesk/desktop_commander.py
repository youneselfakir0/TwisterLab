"""
TwisterLab - Desktop Commander Agent
Distributed agent system for remote desktop management and command execution
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from mcp.client import MCPClient

logger = logging.getLogger(__name__)


class DesktopCommanderAgent(BaseAgent):
    """
    Agent spécialisé dans la gestion à distance des postes de travail.

    Permet l'exécution de commandes, le déploiement de logiciels,
    et la collecte d'informations système sur les machines clientes.
    """

    def __init__(self) -> None:
        super().__init__(
            name="desktop-commander",
            display_name="Desktop Commander",
            description="Remote desktop management agent",
            role="desktop-commander",
            instructions="""
            Desktop Commander Agent for remote desktop management.
            Execute commands, deploy software, gather system info, and perform
            remote diagnostics on registered client machines.
            All operations are logged and secured with zero-trust architecture.

            Only execute commands from the approved whitelist.
            Always validate device permissions before execution.
            Report all actions with detailed logging.
            """,
            model="llama-3.2",
            temperature=0.1,  # Haute précision pour les commandes système
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "execute_command",
                        "description": "Execute command on remote desktop",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "device_id": {
                                    "type": "string",
                                    "description": "Target device identifier",
                                },
                                "command": {
                                    "type": "string",
                                    "description": "Command to execute",
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds",
                                },
                            },
                            "required": ["device_id", "command"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "deploy_package",
                        "description": "Deploy software package",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "device_id": {
                                    "type": "string",
                                    "description": "Target device identifier",
                                },
                                "package_url": {
                                    "type": "string",
                                    "description": "Package download URL",
                                },
                                "install_args": {
                                    "type": "string",
                                    "description": "Installation arguments",
                                },
                            },
                            "required": ["device_id", "package_url"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_system_info",
                        "description": "Gather system info from remote device",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "device_id": {
                                    "type": "string",
                                    "description": "Target device identifier",
                                },
                                "info_type": {
                                    "type": "string",
                                    "enum": [
                                        "hardware",
                                        "software",
                                        "network",
                                        "all",
                                    ],
                                    "description": "Type of info to gather",
                                },
                            },
                            "required": ["device_id"],
                        },
                    },
                },
            ],
        )

        # Liste blanche des commandes autorisées
        self.allowed_commands = {
            "systeminfo": "Get system information",
            "ipconfig": "Get network configuration",
            "netstat": "Get network connections",
            "tasklist": "List running processes",
            "ping": "Test network connectivity",
            "tracert": "Trace network route",
            "nslookup": "DNS lookup",
            "gpupdate": "Update group policies",
            "whoami": "Get current user",
            "hostname": "Get computer name",
            "ver": "Get Windows version",
        }

        # Client MCP pour la communication avec les devices
        self.mcp_client = MCPClient()
        self._mcp_started = False

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Exécute une commande de gestion à distance.

        Args:
            task: Description de la tâche (contient les détails de la commande)
            context: Contexte additionnel (device_id, command, etc.)

        Returns:
            Dict avec le résultat de l'exécution
        """
        try:
            logger.info(f"Desktop commander executing task: {task}")

            # Extraire les paramètres depuis le contexte
            device_id = context.get("device_id") if context else None
            command = context.get("command") if context else None
            timeout = context.get("timeout", 300) if context else 300
            command_type = (
                context.get("command_type", "execute_command") if context else "execute_command"
            )

            if not device_id:
                return {
                    "status": "error",
                    "error": "device_id is required",
                    "timestamp": datetime.now().isoformat(),
                }

            # Router vers la fonction appropriée
            if command_type == "execute_command":
                if not command:
                    return {
                        "status": "error",
                        "error": "command is required for execute_command",
                        "timestamp": datetime.now().isoformat(),
                    }
                result = await self.execute_command(
                    device_id=device_id, command=command, timeout=timeout
                )
            elif command_type == "deploy_package":
                package_url = context.get("package_url") if context else None
                install_args = context.get("install_args") if context else None
                if not package_url:
                    return {
                        "status": "error",
                        "error": "package_url is required for deploy_package",
                        "timestamp": datetime.now().isoformat(),
                    }
                result = await self.deploy_package(device_id, package_url, install_args)
            elif command_type == "get_system_info":
                info_type = context.get("info_type", "all") if context else "all"
                result = await self.get_system_info(device_id, info_type)
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown command type: {command_type}",
                }

            logger.info(f"Desktop command result for device {device_id}: {result['status']}")

            return {
                "device_id": device_id,
                "command_type": command_type,
                "timestamp": datetime.now().isoformat(),
                **result,
            }

        except Exception as e:
            logger.error(f"Error in desktop commander execution: {e}")
            return {
                "status": "error",
                "error": str(e),
                "device_id": (context.get("device_id", "unknown") if context else "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

    async def execute_command(
        self, device_id: str, command: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Exécute une commande sur un device distant.
        """
        try:
            # Valider la commande
            if not self._is_command_allowed(command):
                return {
                    "status": "denied",
                    "error": f"Command not in whitelist: {command}",
                    "allowed_commands": list(self.allowed_commands.keys()),
                }

            # Démarrer le client MCP si nécessaire
            if not self._mcp_started:
                await self.mcp_client.start()
                self._mcp_started = True

            # Exécuter la commande via MCP
            result = await self.mcp_client.execute_command(device_id, command, timeout)

            return result

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"status": "error", "error": str(e)}

    async def deploy_package(
        self,
        device_id: str,
        package_url: str,
        install_args: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Déploie un package logiciel sur un device distant.
        """
        try:
            logger.info(f"Deploying package {package_url} to device {device_id}")

            # Démarrer le client MCP si nécessaire
            if not self._mcp_started:
                await self.mcp_client.start()
                self._mcp_started = True

            # Déployer le package via MCP
            result = await self.mcp_client.deploy_package(device_id, package_url, install_args)

            return result

        except Exception as e:
            logger.error(f"Error deploying package: {e}")
            return {"status": "error", "error": str(e)}

    async def get_system_info(self, device_id: str, info_type: str = "all") -> Dict[str, Any]:
        """
        Récupère les informations système d'un device distant.
        """
        try:
            logger.info(f"Gathering {info_type} info from device {device_id}")

            # Démarrer le client MCP si nécessaire
            if not self._mcp_started:
                await self.mcp_client.start()
                self._mcp_started = True

            # Récupérer les informations système via MCP
            result = await self.mcp_client.get_system_info(device_id, info_type)

            return result

        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"status": "error", "error": str(e)}

    def _is_command_allowed(self, command: str) -> bool:
        """
        Vérifie si la commande est dans la liste blanche.
        """
        command_base = command.split()[0].lower()
        return command_base in self.allowed_commands

    async def _simulate_command_execution(self, command: str) -> str:
        """
        Simulation de l'exécution d'une commande.
        """
        # Simuler différents outputs selon la commande
        command_lower = command.lower()

        if "systeminfo" in command_lower:
            return r"""
Host Name:                 DESKTOP-EXAMPLE
OS Name:                   Microsoft Windows 11 Pro
OS Version:                10.0.22621 N/A Build 22621
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Workstation
OS Build Type:             Multiprocessor Free
Registered Owner:          User
Registered Organization:
Product ID:                XXXXX-XXXXX-XXXXX-XXXXX
Original Install Date:     15/10/2023, 10:30:15
System Boot Time:          28/10/2025, 09:00:00
System Manufacturer:       Dell Inc.
System Model:              Latitude 5420
System Type:               x64-based PC
Processor(s):              1 Processor(s) Installed.
                           [01]: Intel64 Family 6 Model 141 Stepping 1
                           GenuineIntel ~2400 Mhz
BIOS Version:              Dell Inc. 1.20.0, 15/08/2023
Windows Directory:         C:\WINDOWS
System Directory:          C:\WINDOWS\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             fr;French (France)
Input Locale:             fr;French (France)
Time Zone:                 (UTC+01:00) Brussels, Copenhagen, Madrid, Paris
Total Physical Memory:     16,384 MB
Available Physical Memory: 12,345 MB
Virtual Memory: Max Size:  18,896 MB
Virtual Memory: Available: 14,567 MB
Virtual Memory: In Use:    4,329 MB
"""
        elif "ipconfig" in command_lower:
            return """
Windows IP Configuration

Ethernet adapter Ethernet:
   Connection-specific DNS Suffix  . : local
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1

Wireless LAN adapter Wi-Fi:
   Media State . . . . . . . . . . . : Media disconnected
   Connection-specific DNS Suffix  . :
"""
        elif "ping" in command_lower:
            return """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=15ms TTL=118
Reply from 8.8.8.8: bytes=32 time=14ms TTL=118
Reply from 8.8.8.8: bytes=32 time=16ms TTL=118
Reply from 8.8.8.8: bytes=32 time=15ms TTL=118

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 14ms, Maximum = 16ms, Average = 15ms
"""
        else:
            return f"Command '{command}' executed successfully at " f"{datetime.now().isoformat()}"

    async def _simulate_package_deployment(
        self, package_url: str, install_args: Optional[str]
    ) -> Dict[str, Any]:
        """
        Simulation du déploiement d'un package.
        """
        return {
            "download_status": "completed",
            "install_status": "in_progress",
            "progress": "75%",
            "estimated_time_remaining": "2 minutes",
            "install_args": install_args or "default",
        }

    async def _simulate_system_info(self, info_type: str) -> Dict[str, Any]:
        """
        Simulation des informations système.
        """
        base_info = {
            "hostname": "DESKTOP-EXAMPLE",
            "os": "Windows 11 Pro",
            "os_version": "10.0.22621",
            "architecture": "x64",
            "cpu": "Intel Core i7-1185G7 @ 3.00GHz",
            "memory_total": "16 GB",
            "memory_available": "12 GB",
        }

        if info_type == "hardware":
            return {
                **base_info,
                "disk_total": "512 GB SSD",
                "disk_free": "256 GB",
                "gpu": "Intel Iris Xe Graphics",
            }
        elif info_type == "software":
            return {
                "installed_software": [
                    "Microsoft Office 365",
                    "Google Chrome",
                    "Zoom",
                    "Slack",
                    "Adobe Acrobat Reader",
                ],
                "running_processes": 87,
                "startup_programs": 12,
            }
        elif info_type == "network":
            return {
                "ip_address": "192.168.1.100",
                "subnet": "255.255.255.0",
                "gateway": "192.168.1.1",
                "dns_servers": ["8.8.8.8", "8.8.4.4"],
                "mac_address": "00:1B:44:11:3A:B7",
                "wifi_connected": False,
                "ethernet_connected": True,
            }
        else:  # all
            return {
                **base_info,
                "network": {
                    "ip_address": "192.168.1.100",
                    "dns_servers": ["8.8.8.8", "8.8.4.4"],
                },
                "software": {
                    "office_installed": True,
                    "antivirus_active": True,
                },
            }
