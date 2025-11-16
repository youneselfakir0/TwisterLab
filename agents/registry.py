from typing import Dict, Any
from agents.base.unified_agent import UnifiedAgentBase

# Importe les classes d'agents v2 que nous avons refactorisées
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_backup_agent import RealBackupAgent
from agents.real.real_sync_agent import RealSyncAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent
from agents.real.BrowserAgent import BrowserAgent # Nouvelle importation

class AgentRegistry:
    """
    Singleton qui instancie, détient et gère tous les agents actifs du système.
    C'est la source unique de vérité pour l'état des agents.
    """
    _instance = None
    _agents: Dict[str, UnifiedAgentBase] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.initialize_agents()
        return cls._instance

    def initialize_agents(self):
        """Instancie tous les agents v2 au démarrage de l'API."""
        # Agents réels refactorisés
        classifier = RealClassifierAgent()
        resolver = RealResolverAgent()
        monitoring = RealMonitoringAgent()
        backup = RealBackupAgent()
        sync = RealSyncAgent()
        desktop_commander = RealDesktopCommanderAgent()
        maestro = RealMaestroAgent()
        browser = BrowserAgent() # Nouvelle instanciation
        
        self._agents = {
            classifier.name.lower(): classifier,
            resolver.name.lower(): resolver,
            monitoring.name.lower(): monitoring,
            backup.name.lower(): backup,
            sync.name.lower(): sync,
            desktop_commander.name.lower(): desktop_commander,
            maestro.name.lower(): maestro,
            browser.name.lower(): browser,
        }
        print(f"Agent Registry initialized with {len(self._agents)} agents.")

    def get_agent(self, name: str) -> UnifiedAgentBase:
        """Récupère une instance d'agent par son nom."""
        return self._agents.get(name.lower())

    def list_agents(self) -> Dict[str, Dict]:
        """Retourne le statut réel et les métadonnées de tous les agents."""
        return {
            name: {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "version": agent.version,
                "description": agent.description,
                "status": agent.status.value,
            }
            for name, agent in self._agents.items()
        }

# Instance unique du registre, prête à être importée
agent_registry = AgentRegistry()
