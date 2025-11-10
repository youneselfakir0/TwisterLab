# 🚀 TwisterLab v1.0.0

## Multi-Agent AI Orchestration System for Autonomous IT Helpdesk Automation with Swarm Intelligence

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **🎉 NEW in v1.0.0**: Complete infrastructure reorganization! See [REORGANISATION_COMPLETE.md](REORGANISATION_COMPLETE.md) and [CHANGELOG.md](CHANGELOG.md) for details.
>
> **Quick Start**: All deployment files are now in `infrastructure/` directory. Use `.\infrastructure\scripts\deploy.ps1` for production deployment.

## 📋 Project Status

- **Status**: ✅ **PRODUCTION READY** - All 6/6 services operational
- **Version**: v1.0.0 (Released 2025-11-10)
- **Infrastructure**: Unified deployment system (`infrastructure/` directory)
- **Environment**: Production on Docker Swarm (edgeserver.twisterlab.local)
- **Repository**: [https://github.com/youneselfakir0/TwisterLab](https://github.com/youneselfakir0/TwisterLab)

## 🏗️ Architecture Overview

TwisterLab is a production-grade multi-agent AI orchestration system designed for autonomous IT helpdesk automation with advanced swarm intelligence capabilities.

### Core Components

**🤖 AI Agents (TwisterAgent-based with Swarm Extensions)**:

- **TicketClassifierAgent** - Analyzes and categorizes incoming tickets
- **AutoResolverAgent** - Executes SOPs for automated ticket resolution
- **DesktopCommanderAgent** - Remote system management and command execution
- **SwarmMaestroOrchestratorAgent** - Coordinates workflows with swarm intelligence
- **HumanInterfaceAgent** - Manages human-AI interactions

**🐝 Swarm IA Components**:

- **SwarmMessenger** - Redis-based pub/sub for inter-agent communication
- **TwisterLangueParser** - DSL for token-efficient agent communication
- **MCP Server** - Model Context Protocol for standardized tool integration

### Tech Stack

- **Backend**: Python 3.12+, FastAPI, PostgreSQL/asyncpg, Redis
- **AI/ML**: Ollama, LangChain, Hugging Face Evaluate, MongoDB/Cosmos DB
- **Infrastructure**: Docker Swarm, OpenTelemetry, Prometheus + Grafana
- **CI/CD**: GitHub Actions with ruff/black/mypy quality gates

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Git

### Development Setup

```bash
# Clone repository
git clone https://github.com/youneselfakir0/TwisterLab.git
cd TwisterLab

# Start full development stack
docker-compose up -d

# Run tests
pytest tests/ -v --cov=agents

# Start API server locally
python -m uvicorn agents.api.main:app --reload --host 0.0.0.0 --port 8001
```

### Production Deployment

Pour un déploiement complet en production avec haute disponibilité, monitoring avancé et sécurité enterprise :

```bash
# Guide complet automatisé
# Voir: docs/PRODUCTION_DEPLOYMENT_COMPLETE_GUIDE.md

# Configuration infrastructure (3+ managers, N workers)
./setup-production.sh

# Déploiement automatisé avec monitoring
./deploy-production.sh --build

# Validation complète
./validate-production.sh
```

**Fonctionnalités production** :

- 🐳 **Docker Swarm** : Orchestration multi-noeuds haute disponibilité
- 🔐 **SSL/TLS** : Certificats Let's Encrypt automatiques
- 📊 **Monitoring** : Prometheus + Grafana + AlertManager
- 🚨 **Alertes** : Notifications automatiques (email, Slack)
- 💾 **Backup** : Sauvegarde automatique avec rotation
- 🔄 **CI/CD** : Pipeline GitHub Actions complet
- 🧪 **Tests** : Charge, sécurité, validation automatisés

## 📚 Essential Documentation & Resources

### 🔗 FastAPI Documentation & Latest Release Notes

- **Official FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **FastAPI Release Notes**: [https://fastapi.tiangolo.com/release-notes/](https://fastapi.tiangolo.com/release-notes/)
- **FastAPI DevDocs**: [https://devdocs.io/fastapi/](https://devdocs.io/fastapi/)

### 🔗 Async/Await & Concurrency Python (Best Practices 2025)

- **FastAPI Async Guide**: [https://fastapi.tiangolo.com/async/](https://fastapi.tiangolo.com/async/)
- **AsyncIO in Python 2025**: [https://linkedin.com/pulse/asyncio-in-python-writing-fast-and-efficient-asynchronous-code-2025/](https://linkedin.com/pulse/asyncio-in-python-writing-fast-and-efficient-asynchronous-code-2025/)

### 🔗 Pydantic V2 (Validation & Schemas)

- **Pydantic Latest Documentation**: [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)
- **Pydantic PyPI**: [https://pypi.org/project/pydantic/](https://pypi.org/project/pydantic/)

### 🔗 Docker Compose 2025 – Multi-container Apps & Scaling

- **Docker Compose Official Docs**: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
- **Docker Compose Deployment 2025**: [https://dokploy.com/how-to-deploy-apps-with-docker-compose-in-2025/](https://dokploy.com/how-to-deploy-apps-with-docker-compose-in-2025/)

### 🔗 GitHub Actions — Setup & Workflow CI/CD

- **GitHub Actions Documentation**: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)
- **GitHub Actions Setup Guide**: [https://freecodecamp.org/news/github-actions-setup-guide/](https://freecodecamp.org/news/github-actions-setup-guide/)

### 🔗 React – Build Production Frontend

- **Create React App Production**: [https://create-react-app.dev/docs/production-build/](https://create-react-app.dev/docs/production-build/)

### 🔗 Audit Logging Python — Best Practices

- **Python Logging Documentation**: [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)
- **Real Python Logging Guide**: [https://realpython.com/python-logging/](https://realpython.com/python-logging/)

### 🔗 Monitoring avec Prometheus/Grafana pour Python/FastAPI

- **Grafana Getting Started**: [https://grafana.com/docs/grafana/latest/getting-started/](https://grafana.com/docs/grafana/latest/getting-started/)
- **Prometheus Overview**: [https://prometheus.io/docs/introduction/overview/](https://prometheus.io/docs/introduction/overview/)
- **Python Apps Monitoring**: [https://towardsdatascience.com/monitoring-your-python-apps-with-prometheus-9e5ae0880887](https://towardsdatascience.com/monitoring-your-python-apps-with-prometheus-9e5ae0880887)

### 🔗 CI/CD Microservices — Modern Patterns 2025

- **Microservices Testing**: [https://martinfowler.com/articles/microservices-testing/](https://martinfowler.com/articles/microservices-testing/)
- **CI/CD for Microservices 2025**: [https://jalr.dev/posts/2025-ci-cd-for-microservices/](https://jalr.dev/posts/2025-ci-cd-for-microservices/)

### 🔗 AI Integration & MCP Protocol

- **TwisterLab MCP Protocol**: [https://github.com/youneselfakir0/TwisterLab](https://github.com/youneselfakir0/TwisterLab) (Internal MCP implementation)
- **Model Context Protocol Standards**: Reference TwisterLab's MCP server implementation in `agents/mcp/server.py`

## 📖 API Documentation

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
