"""
MCP Server for Desktop Commander
Allows agents to execute commands on remote desktop clients

Protocol: MCP 2024-11-05
Security: Zero-Trust Architecture with command whitelist
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    """Status des devices clients"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BUSY = "busy"
    ERROR = "error"


class CommandStatus(Enum):
    """Status d'exécution des commandes"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


class DesktopCommanderMCPServer:
    """
    Serveur MCP pour la gestion des clients Desktop Commander

    Responsabilités:
    - Enregistrement des clients distants
    - Exécution de commandes sécurisées
    - Monitoring de l'état des clients
    - Gestion des sessions
    """

    def __init__(self):
        """Initialise le serveur MCP"""
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.command_history: List[Dict[str, Any]] = []

        # Whitelist des commandes autorisées (Zero-Trust)
        self.command_whitelist = {
            # Windows System Commands
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
            # PowerShell Commands (Safe)
            "Get-Service": "Get Windows services",
            "Get-Process": "Get running processes",
            "Get-EventLog": "Get event logs",
            "Test-Connection": "Test network connection",
            # File Operations (Read-only)
            "dir": "List directory contents",
            "type": "Display file contents",
            # Network Diagnostics
            "arp": "Display ARP cache",
            "route": "Display routing table",
        }

    async def register_client(
        self,
        device_id: str,
        hostname: str,
        ip_address: str,
        os_info: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Enregistre un nouveau client Desktop Commander

        Args:
            device_id: Identifiant unique du device
            hostname: Nom du poste
            ip_address: Adresse IP
            os_info: Informations OS (name, version, build)
            metadata: Métadonnées additionnelles

        Returns:
            Registration result
        """
        try:
            self.connected_clients[device_id] = {
                "device_id": device_id,
                "hostname": hostname,
                "ip_address": ip_address,
                "os_info": os_info,
                "status": DeviceStatus.CONNECTED.value,
                "last_seen": datetime.now().isoformat(),
                "registered_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "commands_executed": 0,
                "last_command": None,
            }

            logger.info(f"Client registered: {device_id} ({hostname} @ {ip_address})")

            return {
                "status": "success",
                "device_id": device_id,
                "message": f"Client {hostname} registered successfully",
                "server_time": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error registering client {device_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def unregister_client(self, device_id: str) -> Dict[str, Any]:
        """Désenregistre un client"""
        if device_id in self.connected_clients:
            client_info = self.connected_clients.pop(device_id)
            logger.info(f"Client unregistered: {device_id}")
            return {
                "status": "success",
                "device_id": device_id,
                "message": f"Client {client_info['hostname']} unregistered",
            }
        else:
            return {"status": "error", "error": f"Client {device_id} not found"}

    async def execute_command(
        self, device_id: str, command: str, timeout: int = 300, user_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exécute une commande sur un client distant

        Args:
            device_id: ID du device cible
            command: Commande à exécuter
            timeout: Timeout en secondes (max 600)
            user_context: Contexte utilisateur (pour audit)

        Returns:
            Command execution result
        """
        try:
            # Vérifier que le client est connecté
            if device_id not in self.connected_clients:
                return {
                    "status": CommandStatus.FAILED.value,
                    "error": f"Client {device_id} not connected",
                    "device_id": device_id,
                }

            client = self.connected_clients[device_id]

            # Vérifier le statut du client
            if client["status"] != DeviceStatus.CONNECTED.value:
                return {
                    "status": CommandStatus.FAILED.value,
                    "error": f"Client {device_id} is {client['status']}",
                    "device_id": device_id,
                }

            # Valider la commande contre la whitelist
            if not self._is_command_allowed(command):
                logger.warning(f"Command denied on {device_id}: {command}")
                self._log_command(device_id, command, CommandStatus.DENIED, user_context)

                return {
                    "status": CommandStatus.DENIED.value,
                    "error": f"Command not in whitelist: {command.split()[0]}",
                    "allowed_commands": list(self.command_whitelist.keys()),
                    "device_id": device_id,
                }

            # Valider le timeout
            if timeout > 600:
                timeout = 600  # Max 10 minutes

            # Marquer le client comme occupé
            client["status"] = DeviceStatus.BUSY.value

            logger.info(f"Executing command on {device_id}: {command}")

            # TODO: Implémentation réelle via protocole MCP
            # Pour l'instant, simulation
            execution_result = await self._simulate_command_execution(device_id, command, timeout)

            # Mettre à jour le client
            client["status"] = DeviceStatus.CONNECTED.value
            client["last_seen"] = datetime.now().isoformat()
            client["commands_executed"] += 1
            client["last_command"] = {
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "status": execution_result["status"],
            }

            # Logger la commande
            self._log_command(
                device_id,
                command,
                (
                    CommandStatus.SUCCESS
                    if execution_result["status"] == "success"
                    else CommandStatus.FAILED
                ),
                user_context,
            )

            return execution_result

        except Exception as e:
            logger.error(f"Error executing command on {device_id}: {e}")

            # Restaurer le statut du client
            if device_id in self.connected_clients:
                self.connected_clients[device_id]["status"] = DeviceStatus.ERROR.value

            return {"status": CommandStatus.FAILED.value, "error": str(e), "device_id": device_id}

    def _is_command_allowed(self, command: str) -> bool:
        """
        Vérifie si la commande est dans la whitelist

        Args:
            command: Commande complète

        Returns:
            True si autorisée, False sinon
        """
        # Extraire la commande de base (premier mot)
        command_base = command.strip().split()[0].lower()

        # Vérifier contre la whitelist (case-insensitive)
        for allowed_cmd in self.command_whitelist.keys():
            if command_base == allowed_cmd.lower():
                return True

        return False

    async def _simulate_command_execution(
        self, device_id: str, command: str, timeout: int
    ) -> Dict[str, Any]:
        """
        Simulation de l'exécution d'une commande
        (Remplacé par vraie implémentation MCP en production)
        """
        # Simuler un délai d'exécution
        await asyncio.sleep(0.5)

        command_lower = command.lower()

        # Simuler différents outputs selon la commande
        if "systeminfo" in command_lower:
            output = """
Host Name:                 DESKTOP-CLIENT01
OS Name:                   Microsoft Windows 11 Pro
OS Version:                10.0.22621 N/A Build 22621
System Manufacturer:       Dell Inc.
System Model:              Latitude 5420
Processor:                 Intel Core i7-1185G7 @ 3.00GHz
Total Physical Memory:     16,384 MB
"""
        elif "ipconfig" in command_lower:
            output = """
Windows IP Configuration

Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1
"""
        elif "ping" in command_lower:
            output = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=15ms TTL=118

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
"""
        else:
            output = f"Command '{command}' executed successfully"

        return {
            "status": "success",
            "device_id": device_id,
            "command": command,
            "output": output.strip(),
            "execution_time": 2.5,
            "timeout": timeout,
            "timestamp": datetime.now().isoformat(),
        }

    def _log_command(
        self, device_id: str, command: str, status: CommandStatus, user_context: Optional[str]
    ):
        """Enregistre une commande dans l'historique"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "command": command,
            "status": status.value,
            "user_context": user_context,
        }

        self.command_history.append(log_entry)

        # Garder seulement les 1000 dernières commandes
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]

    async def get_client_status(self, device_id: str) -> Dict[str, Any]:
        """Récupère le statut d'un client"""
        if device_id not in self.connected_clients:
            return {"status": "not_found", "device_id": device_id}

        client = self.connected_clients[device_id]
        return {"status": "success", "client": client}

    async def list_clients(self) -> Dict[str, Any]:
        """Liste tous les clients connectés"""
        return {
            "status": "success",
            "total_clients": len(self.connected_clients),
            "clients": list(self.connected_clients.values()),
        }

    async def get_command_history(
        self, device_id: Optional[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Récupère l'historique des commandes"""
        history = self.command_history

        # Filtrer par device_id si spécifié
        if device_id:
            history = [cmd for cmd in history if cmd["device_id"] == device_id]

        # Limiter le nombre de résultats
        history = history[-limit:]

        return {"status": "success", "total_commands": len(history), "commands": history}

    async def healthcheck(self) -> Dict[str, Any]:
        """Vérification de santé du serveur"""
        connected_count = sum(
            1
            for client in self.connected_clients.values()
            if client["status"] == DeviceStatus.CONNECTED.value
        )

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "total_clients": len(self.connected_clients),
            "connected_clients": connected_count,
            "command_history_size": len(self.command_history),
            "whitelist_commands": len(self.command_whitelist),
        }


# Instance globale du serveur MCP
_mcp_server_instance: Optional[DesktopCommanderMCPServer] = None


def get_mcp_server() -> DesktopCommanderMCPServer:
    """Retourne l'instance singleton du serveur MCP"""
    global _mcp_server_instance

    if _mcp_server_instance is None:
        _mcp_server_instance = DesktopCommanderMCPServer()

    return _mcp_server_instance
