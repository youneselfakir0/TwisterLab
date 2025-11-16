---
name: "TwisterLab Architecture"
version: "1.0.0"
globs: "**/*"
description: TwisterLab v1.0.0 - Architecture des agents autonomes et infrastructure de production
alwaysApply: true
---

# 🏗️ TwisterLab v1.0.0 - Architecture de Production

TwisterLab est un système d'orchestration multi-agent IA pour l'automatisation autonome du helpdesk IT, déployé en production avec Docker Swarm.

## 🏛️ Architecture Core

### 🤖 Système Multi-Agent (7 Agents Réels)

Tous les agents héritent de `TwisterAgent` dans `agents/base.py` et sont déployés dans `agents/real/` :

#### **Agents de Production Opérationnels**
- **RealMonitoringAgent** - Surveillance système (CPU/RAM/Disk/Docker)
- **RealBackupAgent** - Sauvegardes PostgreSQL/Redis/configs
- **RealSyncAgent** - Synchronisation Redis ↔ PostgreSQL
- **RealClassifierAgent** - Classification tickets IT (LLM Ollama)
- **RealResolverAgent** - Résolution SOP automatisée
- **RealDesktopCommanderAgent** - Commandes système distantes
- **RealMaestroAgent** - Orchestration et load balancing

### 🛠️ Infrastructure de Production

#### **Stack Technologique**
- **Backend**: Python 3.12+, FastAPI, asyncio, asyncpg
- **Base de données**: PostgreSQL 16 (port 5432)
- **Cache/État**: Redis 7 (port 6379)
- **IA Locale**: Ollama (port 11434) avec GPU RTX 3060
- **Orchestration**: Docker Swarm sur edgeserver.twisterlab.local
- **Monitoring**: Prometheus + Grafana (ports 9090/3000)

#### **Endpoints de Production**
- **API TwisterLab**: `http://192.168.0.30:8000`
- **Ollama GPU**: `http://192.168.0.20:11434`
- **Grafana**: `http://192.168.0.30:3000`

### 🔧 MCP Integration (Continue IDE)

#### **Serveur MCP Actif**
- **Fichier**: `agents/mcp/mcp_server_continue_sync.py` (v2.1.0)
- **Protocol**: MCP 2024-11-05
- **Transport**: stdio (JSON-RPC 2.0)
- **Mode**: REAL avec fallback MOCK

#### **Outils MCP Exposés (7)**
1. `list_autonomous_agents` - Liste des 7 agents
2. `monitor_system_health` - Surveillance système
3. `create_backup` - Sauvegardes automatisées
4. `sync_cache` - Sync Redis/PostgreSQL
5. `classify_ticket` - Classification LLM
6. `resolve_ticket` - Résolution SOP
7. `execute_desktop_command` - Commandes distantes

#### **Configuration Continue**
- **Config**: `.continue/config.json`
- **6 Modèles Ollama** configurés
- **15 Règles TwisterLab** actives
- **Auto-approve** pour tous les outils MCP

### 📊 Flux de Données

```
Continue IDE → MCP Server → API TwisterLab → Agents Réels
                                      ↓
                            PostgreSQL + Redis + Ollama
```

### 🎯 Patterns de Développement

#### **TwisterAgent Base Class**
```python
from agents.base import TwisterAgent

class MyAgent(TwisterAgent):
    async def execute(self, task: str, context: Dict[str, Any]) -> Any:
        # Logique métier ici
        pass
```

#### **Gestion d'Erreurs Standard**
```python
try:
    result = await self._perform_operation()
    return {"status": "success", "data": result}
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {"status": "error", "error": str(e)}
```

#### **MCP Tool Integration**
```python
# Dans Continue IDE
@mcp monitor_system_health {"detailed": true}
@mcp classify_ticket {"ticket_text": "Problème réseau"}
@mcp resolve_ticket {"category": "network", "description": "..."}
```

### 📁 Structure du Projet

```
TwisterLab/
├── agents/
│   ├── base/           # TwisterAgent, BaseAgent
│   ├── real/           # 7 agents de production
│   ├── core/           # Agents standards (référence)
│   ├── orchestrator/   # AutonomousAgentOrchestrator
│   ├── mcp/            # Serveur MCP v2.1.0
│   └── metrics.py      # Métriques Prometheus
├── api/                # Routes FastAPI
├── tests/              # Tests pytest
├── infrastructure/     # Docker Swarm, configs
└── .continue/          # Configuration Continue IDE
```

### 🔄 Patterns de Communication

#### **Inter-Agent**
- **Orchestrateur**: `AutonomousAgentOrchestrator` gère le cycle de vie
- **MCP Protocol**: Communication avec Continue IDE (v2.1.0)
- **API REST**: Endpoints FastAPI pour intégrations externes

#### **Base de Données**
- **PostgreSQL**: Données persistantes via asyncpg
- **Redis**: Cache et état des agents via aioredis
- **Connexions**: Pool de connexions async optimisé

### 🚀 Déploiement Production

#### **Docker Swarm Stack**
```yaml
# 6 services déployés sur edgeserver.twisterlab.local
twisterlab:
  api: FastAPI (port 8000)
  postgres: PostgreSQL 16
  redis: Redis 7
  ollama: GPU inference
  openwebui: Interface chat
  traefik: Load balancer
```

#### **Commandes Déploiement**
```powershell
# Déploiement production
.\infrastructure\scripts\deploy.ps1 -Environment production

# Monitoring
docker service logs twisterlab_api
docker stats
```

### 📊 Monitoring & Observabilité

#### **Métriques Temps Réel**
- **Prometheus**: Collecte métriques agents
- **Grafana**: Dashboards de monitoring
- **Health Checks**: `/health` endpoint
- **MCP Tools**: `monitor_system_health` intégré

#### **Logs Structurés**
- **Format**: JSON avec contexte (agent, timestamp, status)
- **Niveaux**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Outil**: structlog (pas print!)

### 🔒 Sécurité & Conformité

#### **Pratiques de Sécurité**
- **Credentials**: Variables d'environnement uniquement
- **Validation**: Pydantic models pour tous les inputs
- **Audit**: Logs détaillés pour toutes les actions
- **Whitelist**: Commandes système autorisées uniquement

#### **Réseau Sécurisé**
- **Isolation**: Docker Swarm avec overlay networks
- **Authentification**: API keys pour endpoints sensibles
- **Chiffrement**: TLS pour communications externes

### 🧪 Standards de Développement

#### **Code Quality**
- **Linting**: ruff (rapide, strict)
- **Format**: black (88 caractères)
- **Types**: mypy obligatoire
- **Tests**: pytest avec asyncio, 80% coverage minimum

#### **CI/CD**
- **Tests**: Automatiques sur push
- **Build**: Docker images optimisées
- **Deploy**: Blue/green avec rollback

### 🎯 Principes Architecturaux

#### **Production-First**
- Code directement déployable
- Gestion d'erreur robuste
- Monitoring intégré
- Documentation complète

#### **Async Everywhere**
- Toutes les opérations I/O async
- FastAPI avec async routes
- asyncpg pour PostgreSQL
- aioredis pour Redis

#### **Agent-Based Design**
- Tout est agent (monitoring, backup, classification...)
- Héritage TwisterAgent obligatoire
- Interface standardisée execute(context)
- Orchestration centralisée

Quand vous travaillez avec TwisterLab, considérez toujours l'architecture de production : 7 agents réels, Docker Swarm, async partout, et monitoring intégré.


