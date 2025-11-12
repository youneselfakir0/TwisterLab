"""
TwisterLab - Real Agents Integration
Replace mock agents with REAL working agents
"""
import sys
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.real.real_backup_agent import RealBackupAgent
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_sync_agent import RealSyncAgent
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent

# Export real agents
__all__ = [
    "RealBackupAgent",
    "RealMonitoringAgent",
    "RealSyncAgent",
    "RealClassifierAgent",
    "RealResolverAgent",
    "RealDesktopCommanderAgent",
    "RealMaestroAgent"
]
