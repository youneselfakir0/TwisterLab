# TwisterLab: Personal AI Agent Orchestration Platform# TwisterLab: Personal AI Agent Orchestration Platform



![Version](https://img.shields.io/badge/version-1.0.0-blue)![Version](https://img.shields.io/badge/version-1.0.0-blue)

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)

![License](https://img.shields.io/badge/license-MIT-green)![License](https://img.shields.io/badge/license-MIT-green)

![Python](https://img.shields.io/badge/python-3.12+-blue)![Python](https://img.shields.io/badge/python-3.12+-blue)

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)



## 🚀 What is TwisterLab?## 🚀 What is TwisterLab?



TwisterLab is a **production-grade multi-agent AI infrastructure** designed to provide autonomous IT operations management through a unified architecture. Control 7 autonomous agents directly from your IDE (Continue, Claude Desktop, Ollama) via MCP (Model Context Protocol).TwisterLab is a **production-grade multi-agent AI infrastructure** designed to provide autonomous IT operations management through a unified architecture. Control 7 autonomous agents directly from your IDE (Continue, Claude Desktop, Ollama) via MCP (Model Context Protocol).



### Key Features### Key Features

- ✅ **7 Autonomous Agents** (Classifier, Resolver, Monitor, Backup, Sync, Commander, Maestro)- ✅ **7 Autonomous Agents** (Classifier, Resolver, Monitor, Backup, Sync, Commander, Maestro)

- ✅ **IDE-Native Control** (Continue IDE, Claude Desktop, Ollama Desktop)- ✅ **IDE-Native Control** (Continue IDE, Claude Desktop, Ollama Desktop)

- ✅ **MCP Integration** (Hybrid native + REST modes)- ✅ **MCP Integration** (Hybrid native + REST modes)

- ✅ **GPU Accelerated** (Ollama + RTX 3060)- ✅ **GPU Accelerated** (Ollama + RTX 3060)

- ✅ **Production Ready** (Docker Swarm, PostgreSQL, async-native)- ✅ **Production Ready** (Docker Swarm, PostgreSQL, async-native)

- ✅ **Type-Safe** (100% type hints)- ✅ **Type-Safe** (100% type hints)

- ✅ **Fully Documented** (40+ pages, comprehensive guides)- ✅ **Fully Documented** (40+ pages, comprehensive guides)



## 🏗️ Architecture## 🏗️ Architecture



``````

Continue IDE → MCP Tools → Real Agents → Ollama GPUContinue IDE → MCP Tools → Real Agents → Ollama GPU

     ↓             ↓            ↓            ↓     ↓             ↓            ↓            ↓

  Copilot    4 Endpoints   7 Autonomous  RTX 3060  Copilot    4 Endpoints   7 Autonomous  RTX 3060

              (REST API)     Agents       (3x faster)              (REST API)     Agents       (3x faster)

                             + DB                             + DB

``````



### 7 Autonomous Agents### 7 Autonomous Agents



| Agent | Purpose | Status || Agent | Purpose | Status |

|-------|---------|--------||-------|---------|--------|

| **RealMonitoringAgent** | System health (CPU/RAM/Disk/Docker) | ✅ Operational || **RealMonitoringAgent** | System health (CPU/RAM/Disk/Docker) | ✅ Operational |

| **RealClassifierAgent** | Ticket classification (Ollama LLM) | ✅ Operational || **RealClassifierAgent** | Ticket classification (Ollama LLM) | ✅ Operational |

| **RealResolverAgent** | SOP-based resolution | ✅ Operational || **RealResolverAgent** | SOP-based resolution | ✅ Operational |

| **RealBackupAgent** | Automated backups (PostgreSQL/Redis) | ✅ Operational || **RealBackupAgent** | Automated backups (PostgreSQL/Redis) | ✅ Operational |

| **RealSyncAgent** | Cache/DB synchronization | ✅ Operational || **RealSyncAgent** | Cache/DB synchronization | ✅ Operational |

| **RealDesktopCommanderAgent** | Remote command execution | ✅ Operational || **RealDesktopCommanderAgent** | Remote command execution | ✅ Operational |

| **RealMaestroAgent** | Workflow orchestration | ✅ Operational || **RealMaestroAgent** | Workflow orchestration | ✅ Operational |



## 📦 Installation## � Installation



### Prerequisites### Prerequisites

- Python 3.12+- Python 3.12+

- Docker & Docker Compose- Docker & Docker Compose

- PostgreSQL 16- PostgreSQL 16

- Ollama with GPU support (optional but recommended)- Ollama with GPU support (optional but recommended)



### Quick Start### Quick Start



**1. Clone Repository****1. Clone Repository**

```bash```bash

git clone https://github.com/youneselfakir0/TwisterLab.gitgit clone https://github.com/youneselfakir0/TwisterLab.git

cd TwisterLabcd TwisterLab

``````



**2. Create Environment****2. Create Environment**

```bash```bash

cp .env.example .envcp .env.example .env

# Edit .env with your settings (PostgreSQL credentials, API keys)# Edit .env with your settings (PostgreSQL credentials, API keys)

``````



**3. Deploy Infrastructure****3. Deploy Infrastructure**

```bash```bash

docker-compose -f infrastructure/docker/docker-compose.unified.yml up -ddocker-compose -f infrastructure/docker/docker-compose.unified.yml up -d

``````



**4. Initialize Database****4. Initialize Database**

```bash```bash

python -c "import asyncio; from agents.core.database import init_db; asyncio.run(init_db())"python -c "import asyncio; from agents.core.database import init_db; asyncio.run(init_db())"

# Or use schema.sql:# Or use schema.sql:

# docker exec twisterlab_postgres.1.xxx psql -U twisterlab -d twisterlab -f /tmp/schema.sql# docker exec twisterlab_postgres.1.xxx psql -U twisterlab -d twisterlab -f /tmp/schema.sql

``````



**5. Configure Continue IDE****5. Configure Continue IDE**

```bash```bash

cp .continue/config.json ~/.continue/config.jsoncp .continue/config.json ~/.continue/config.json

# Update IP addresses (192.168.0.30 → your server IP)# Update IP addresses (192.168.0.30 → your server IP)

``````



**6. Test****6. Test**

```bash```bash

curl -X POST http://192.168.0.30:8000/v1/mcp/tools/classify_ticket \curl -X POST http://192.168.0.30:8000/v1/mcp/tools/classify_ticket \

  -H "Content-Type: application/json" \  -H "Content-Type: application/json" \

  -d '{"description":"WiFi broken","priority":"high"}'  -d '{"description":"WiFi broken","priority":"high"}'

``````



## 📊 System Status### Prerequisites



| Component | Status | Location |- Docker & Docker Compose

|-----------|--------|----------|- Python 3.12+

| API Server | ✅ Running | 192.168.0.30:8000 |- Git

| PostgreSQL | ✅ Running | 192.168.0.30:5432 |

| Redis Cache | ✅ Running | 192.168.0.30:6379 |### Development Setup

| Ollama GPU | ✅ Running | 192.168.0.20:11434 |

| Monitoring | ✅ Running | 192.168.0.30:3000 (Grafana) |```bash

# Clone repository

## 🎯 Usagegit clone https://github.com/youneselfakir0/TwisterLab.git

cd TwisterLab

### Via Continue IDE

```# Start full development stack

Ctrl+L → /classify "WiFi not working"docker-compose up -d

Ctrl+L → /resolve network

Ctrl+L → /monitor# Run tests

Ctrl+L → /backup fullpytest tests/ -v --cov=agents

```

# Start API server locally

### Via APIpython -m uvicorn agents.api.main:app --reload --host 0.0.0.0 --port 8001

```bash```

# List all agents

curl -X POST http://192.168.0.30:8000/v1/mcp/tools/list_autonomous_agents### Production Deployment



# Classify ticketPour un déploiement complet en production avec haute disponibilité, monitoring avancé et sécurité enterprise :

curl -X POST http://192.168.0.30:8000/v1/mcp/tools/classify_ticket \

  -H "Content-Type: application/json" \```bash

  -d '{"description":"Cannot access shared folder","priority":"high"}'# Guide complet automatisé

# Voir: docs/PRODUCTION_DEPLOYMENT_COMPLETE_GUIDE.md

# Monitor system health

curl -X POST http://192.168.0.30:8000/v1/mcp/tools/monitor_system_health \# Configuration infrastructure (3+ managers, N workers)

  -H "Content-Type: application/json" \./setup-production.sh

  -d '{"detailed":true}'

```# Déploiement automatisé avec monitoring

./deploy-production.sh --build

## 📚 Documentation

# Validation complète

- **[Architecture Guide](docs/ARCHITECTURE_GUIDE.md)** - System design and agent interactions./validate-production.sh

- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions```

- **[API Reference](API_DOCUMENTATION.md)** - Complete API documentation

- **[Troubleshooting](.continue/VERIFICATION_MCP.md)** - Common issues and solutions**Fonctionnalités production** :



## 🧪 Testing- 🐳 **Docker Swarm** : Orchestration multi-noeuds haute disponibilité

- 🔐 **SSL/TLS** : Certificats Let's Encrypt automatiques

```bash- 📊 **Monitoring** : Prometheus + Grafana + AlertManager

# Run all tests- 🚨 **Alertes** : Notifications automatiques (email, Slack)

pytest tests/ -v- 💾 **Backup** : Sauvegarde automatique avec rotation

- 🔄 **CI/CD** : Pipeline GitHub Actions complet

# Run with coverage- 🧪 **Tests** : Charge, sécurité, validation automatisés

pytest tests/ --cov=agents --cov-report=html

## 📚 Essential Documentation & Resources

# Integration tests

pytest tests/ -m integration### 🔗 FastAPI Documentation & Latest Release Notes

```

- **Official FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

## 🔧 Development- **FastAPI Release Notes**: [https://fastapi.tiangolo.com/release-notes/](https://fastapi.tiangolo.com/release-notes/)

- **FastAPI DevDocs**: [https://devdocs.io/fastapi/](https://devdocs.io/fastapi/)

```bash

# Install dev dependencies### 🔗 Async/Await & Concurrency Python (Best Practices 2025)

pip install -r requirements.txt

- **FastAPI Async Guide**: [https://fastapi.tiangolo.com/async/](https://fastapi.tiangolo.com/async/)

# Format code- **AsyncIO in Python 2025**: [https://linkedin.com/pulse/asyncio-in-python-writing-fast-and-efficient-asynchronous-code-2025/](https://linkedin.com/pulse/asyncio-in-python-writing-fast-and-efficient-asynchronous-code-2025/)

black agents/ api/

### 🔗 Pydantic V2 (Validation & Schemas)

# Type checking

mypy agents/ api/- **Pydantic Latest Documentation**: [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)

- **Pydantic PyPI**: [https://pypi.org/project/pydantic/](https://pypi.org/project/pydantic/)

# Lint

ruff check agents/ api/### 🔗 Docker Compose 2025 – Multi-container Apps & Scaling

```

- **Docker Compose Official Docs**: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)

## 📈 Performance- **Docker Compose Deployment 2025**: [https://dokploy.com/how-to-deploy-apps-with-docker-compose-in-2025/](https://dokploy.com/how-to-deploy-apps-with-docker-compose-in-2025/)



| Operation | Latency | Status |### 🔗 GitHub Actions — Setup & Workflow CI/CD

|-----------|---------|--------|

| Classify Ticket | 150ms | ✅ |- **GitHub Actions Documentation**: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)

| Resolve Ticket | 200ms | ✅ |- **GitHub Actions Setup Guide**: [https://freecodecamp.org/news/github-actions-setup-guide/](https://freecodecamp.org/news/github-actions-setup-guide/)

| Monitor Health | 50ms | ✅ |

| Create Backup | 1300ms | ✅ |### 🔗 React – Build Production Frontend



*Measured on edgeserver.twisterlab.local with Ollama GPU acceleration (RTX 3060)*- **Create React App Production**: [https://create-react-app.dev/docs/production-build/](https://create-react-app.dev/docs/production-build/)



## 🔐 Security### 🔗 Audit Logging Python — Best Practices



- ✅ Type-safe Python (100% type hints)- **Python Logging Documentation**: [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)

- ✅ No hardcoded credentials (env-based configuration)- **Real Python Logging Guide**: [https://realpython.com/python-logging/](https://realpython.com/python-logging/)

- ✅ Audit logging (all operations logged to `agent_logs` table)

- ✅ PostgreSQL prepared statements (SQL injection prevention)### 🔗 Monitoring avec Prometheus/Grafana pour Python/FastAPI

- ✅ Docker Swarm secrets management ready

- **Grafana Getting Started**: [https://grafana.com/docs/grafana/latest/getting-started/](https://grafana.com/docs/grafana/latest/getting-started/)

## 📝 Changelog- **Prometheus Overview**: [https://prometheus.io/docs/introduction/overview/](https://prometheus.io/docs/introduction/overview/)

- **Python Apps Monitoring**: [https://towardsdatascience.com/monitoring-your-python-apps-with-prometheus-9e5ae0880887](https://towardsdatascience.com/monitoring-your-python-apps-with-prometheus-9e5ae0880887)

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### 🔗 CI/CD Microservices — Modern Patterns 2025

## 👨‍💻 Author

- **Microservices Testing**: [https://martinfowler.com/articles/microservices-testing/](https://martinfowler.com/articles/microservices-testing/)

**Younes El Fakir** - Founder & Lead Architect- **CI/CD for Microservices 2025**: [https://jalr.dev/posts/2025-ci-cd-for-microservices/](https://jalr.dev/posts/2025-ci-cd-for-microservices/)



## 📄 License### 🔗 AI Integration & MCP Protocol



MIT License - see [LICENSE](LICENSE) file for details.- **TwisterLab MCP Protocol**: [https://github.com/youneselfakir0/TwisterLab](https://github.com/youneselfakir0/TwisterLab) (Internal MCP implementation)

- **Model Context Protocol Standards**: Reference TwisterLab's MCP server implementation in `agents/mcp/server.py`

---

## 📖 API Documentation

**Built with ⚡ Warrior Mode Energy**

Once the API is running, visit:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=agents --cov-report=html

# Run specific test categories
pytest tests/unit/ -v      # Unit tests
pytest tests/integration/ -v  # Integration tests
```

## 📊 Monitoring & Observability

- **Grafana Dashboards**: [http://localhost:3000](http://localhost:3000)
- **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)
- **Jaeger Tracing**: [http://localhost:16686](http://localhost:16686)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write comprehensive docstrings (Google style)
- Add unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI framework and community
- Ollama for local LLM inference
- Docker and containerization technologies
- Open source AI and machine learning communities

## 📞 Support

- **Issues**: [https://github.com/youneselfakir0/TwisterLab/issues](https://github.com/youneselfakir0/TwisterLab/issues)
- **Discussions**: [https://github.com/youneselfakir0/TwisterLab/discussions](https://github.com/youneselfakir0/TwisterLab/discussions)
- **Documentation**: See documentation files below for detailed guidelines

## 📖 Documentation

### Guides essentiels

- **[INSTRUCTIONS.md](INSTRUCTIONS.md)** - Instructions complètes (installation, développement, déploiement)
- **[QUICK_START.md](QUICK_START.md)** - Guide de démarrage rapide (5 minutes)
- **[AI_ASSISTANT_INSTRUCTIONS.md](AI_ASSISTANT_INSTRUCTIONS.md)** - Instructions pour assistants IA
- **[LAUNCH_GUIDE.md](LAUNCH_GUIDE.md)** - Guide de lancement détaillé
- **[copilot-instructions.md](copilot-instructions.md)** - Instructions pour GitHub Copilot

### Documentation technique

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentation API complète
- **[PRODUCTION_DEPLOYMENT_COMPLETE_GUIDE.md](docs/PRODUCTION_DEPLOYMENT_COMPLETE_GUIDE.md)** - Guide complet de déploiement production automatisé
- **[MCP_INTEGRATION_README.md](MCP_INTEGRATION_README.md)** - Guide d'intégration MCP
- **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** - Rapport d'audit de sécurité

### 🏗️ Infrastructure & Déploiement

- **[INFRASTRUCTURE_GUIDES_OVERVIEW.md](docs/INFRASTRUCTURE_GUIDES_OVERVIEW.md)** - Vue d'ensemble de tous les guides d'infrastructure
- **[DOCKER_SWARM_COMPLETE_GUIDE.md](docs/DOCKER_SWARM_COMPLETE_GUIDE.md)** - Guide complet Docker Swarm (architecture, sécurité, monitoring)
- **[DOCKER_COMPLETE_GUIDE.md](docs/DOCKER_COMPLETE_GUIDE.md)** - Guide complet Docker (conteneurisation, multi-disques, performance)
- **[LDAP_SSO_COMPLETE_GUIDE.md](docs/LDAP_SSO_COMPLETE_GUIDE.md)** - Guide complet LDAP & SSO (authentification entreprise)
- **[JWT_COMPLETE_GUIDE.md](docs/JWT_COMPLETE_GUIDE.md)** - Guide complet JWT (tokens d'authentification)
- **[CONTRIBUTING_INFRASTRUCTURE.md](docs/CONTRIBUTING_INFRASTRUCTURE.md)** - Guide de contribution à la documentation infrastructure

**🚀 Happy coding! The agents are ready to work.**

---

## 🏭 PRODUCTION DEPLOYMENT

### Final Deployment Status

✅ **PRODUCTION READY** - All services operational on Linux node (edgeserver.twisterlab.local)

**Last Deployment**: November 9, 2025
**Environment**: Docker Swarm with Linux manager + Windows workers
**Status**: Fully operational with documented workarounds

### Quick Deploy

```bash
# Deploy final production stack
docker stack deploy -c docker-compose.production.yml twisterlab

# Check status
.\check_status.ps1
```

### Access Points

| Service | Direct Access | Traefik Route | Status |
|---------|---------------|---------------|---------|
| **API** | `http://192.168.0.30:8000` | `http://192.168.0.30/api/health` ⚠️ | ✅ Operational |
| **Traefik Dashboard** | `http://192.168.0.30:8080` | - | ✅ Operational |
| **WebUI** | - | `http://webui.twisterlab.local` ⚠️ | ⚠️ DNS required |
| **PostgreSQL** | `192.168.0.30:5432` | - | ✅ Operational |
| **Redis** | `192.168.0.30:6379` | - | ✅ Operational |
| **Ollama** | `192.168.0.30:11434` | - | ✅ Operational |

### Known Issues & Workarounds

⚠️ **Traefik API Routing**: `/api/*` routes timeout due to overlay network issues

- **Workaround**: Use direct API access at `http://192.168.0.30:8000`
- **Impact**: API fully functional, routing cosmetic issue

⚠️ **WebUI Host Routing**: Requires DNS resolution for `webui.twisterlab.local`

- **Workaround**: Add to hosts file or use direct container access
- **Impact**: Interface accessible via alternative methods

### Service Architecture

```text
┌─────────────────┐    ┌─────────────────┐
│   Traefik       │    │   OpenWebUI     │
│   (Load Balancer│◄──►│   (Interface)   │
│   :80, :8080)   │    │                 │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   TwisterLab    │    │   PostgreSQL    │
│   API (:8000)   │◄──►│   Database      │
│   FastAPI       │    │   :5432         │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Redis Cache   │    │   Ollama AI     │
│   :6379         │    │   Inference     │
│   Messaging     │    │   :11434        │
└─────────────────┘    └─────────────────┘
```

### 🔍 Monitoring & Observability

**Traefik Dashboard**: `http://192.168.0.30:8080`
- Configuration visualization
- Real-time routing status
- Service health monitoring

**Prometheus Metrics**: `http://192.168.0.30:8080/metrics`
- HTTP request metrics (count, duration, status codes)
- Entry point statistics
- Service performance data
- Go runtime metrics

**Access Logs**: JSON format in `traefik_logs` volume
- Structured logging for all requests
- Request/response details
- Performance timing data

**Test Monitoring**: `.\test_traefik_monitoring.ps1`
- Automated monitoring verification
- Metrics validation
- Logs volume inspection

### Deployment Scripts

- **`deploy_final.ps1`** - Complete deployment with verification
- **`check_status.ps1`** - Quick status check
- **`docker-compose.production.yml`** - Production configuration

### Node Constraints

All services constrained to Linux node (`edgeserver.twisterlab.local`) for compatibility:

- Python/FastAPI services
- PostgreSQL database
- Redis cache
- Ollama AI inference
- Traefik load balancer
- OpenWebUI interface

### Volumes

External volumes for data persistence:

- `redis_prod_data` - Redis cache data
- `webui_prod_data` - WebUI configuration
- `postgres_prod_data` - Database (currently disabled)
- `ollama_data` - AI models

### Monitoring & Logs

```bash
# View service logs
docker stack logs twisterlab

# Monitor services
docker stack services twisterlab

# Check node status
docker node ls
```

### Backup Strategy

1. **Database**: Export PostgreSQL dumps regularly
2. **Redis**: Backup RDB files from volume
3. **Models**: Backup Ollama models volume
4. **Config**: Version control all configurations

### Scaling

Current setup: 1 replica per service
For production scaling:
```bash
docker service scale twisterlab_api=3
docker service scale twisterlab_ollama=2
```

---

Built with ❤️ by the TwisterLab Team
