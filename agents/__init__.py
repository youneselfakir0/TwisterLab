"""
TwisterLab Agents Package.

This package contains all autonomous agents for the TwisterLab helpdesk automation system.
All agents follow the BaseAgent pattern and implement MCP isolation for security.
"""

from agents.core.backup_agent import BackupAgent
from agents.core.maestro_orchestrator_agent import MaestroOrchestratorAgent
from agents.core.monitoring_agent import MonitoringAgent
from agents.core.sync_agent import SyncAgent
# from agents.desktop_commander.desktop_commander_agent import DesktopCommanderAgent  # DISABLED - imports database/config.py with psycopg2
# from agents.helpdesk.classifier import TicketClassifierAgent  # DISABLED - imports database/config.py with psycopg2
# from agents.resolver.resolver_agent import ResolverAgent  # DISABLED - imports database/config.py with psycopg2

__all__ = [
    "MaestroOrchestratorAgent",
    # "TicketClassifierAgent",  # DISABLED
    # "ResolverAgent",  # DISABLED
    # "DesktopCommanderAgent",  # DISABLED
    "SyncAgent",
    "BackupAgent",
    "MonitoringAgent",
]
