# TwisterLab v1.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TwisterLang](https://img.shields.io/badge/protocol-TwisterLang-green.svg)](https://github.com/youneselfakir0/twisterlab)

**TwisterLab** is an open-source multi-agent IT helpdesk automation system using FastAPI, PostgreSQL, Redis, and the MCP protocol. It features the **TwisterLang protocol** for optimized inter-agent communication with 50-70% token reduction.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/youneselfakir0/twisterlab.git
cd twisterlab

# Install dependencies
pip install -r requirements.txt

# Run the demo
python agents/demo_multi_agent.py
```

## 📋 Features

### Core System
- **Multi-Agent Architecture**: Classifier, Resolver, Desktop Commander agents
- **FastAPI Backend**: Async REST API with Pydantic models
- **Database**: SQLAlchemy with PostgreSQL, audit trails, UUID PKs
- **Orchestration**: Maestro agent coordinates task routing with load balancing

### TwisterLang Protocol
- **50-70% Token Reduction**: Compact communication format
- **SHA256 Validation**: Secure message integrity
- **Multi-Agent Sync**: Push/pull strategies with conflict resolution
- **Auto-Learning**: Vocabulary expansion from usage patterns

### Integration Points
- **MCP Protocol**: Remote tools (PostgreSQL, Email, AD, Slack, Azure CLI)
- **Ollama**: Local AI inference (llama3.2, deepseek-r1 models)
- **Redis**: Cache and state management
- **LDAP**: Dev/test authentication
- **OpenWebUI**: Chat-based user interface
- **Rocket.Chat**: Team communication

## 🏗️ Architecture

```
TwisterLab v1.0.0
├── agents/                 # Agent implementations
│   ├── base.py            # TwisterAgent base class
│   ├── api/main.py        # FastAPI application
│   ├── database/          # SQLAlchemy models & services
│   └── orchestrator/      # Maestro coordination
├── core/                  # TwisterLang protocol
│   ├── twisterlang_encoder.py
│   ├── twisterlang_decoder.py
│   ├── twisterlang_sync.py
│   └── twisterlang_vocab.json
├── tests/                 # Test suites
├── docs/                  # Documentation
└── docker-compose.yml     # Full stack deployment
```

## 📚 Documentation

- **[TwisterLang Guide](docs/TWISTERLANG_GUIDE.md)**: Protocol specification
- **[Agent Integration](docs/AGENT_INTEGRATION_GUIDE.md)**: How to adopt TwisterLang
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Architecture](docs/ARCHITECTURE.md)**: System design overview
- **[Deployment](docs/DEPLOYMENT.md)**: Production setup guide

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=agents --cov=core --cov-report=html

# Run TwisterLang tests specifically
pytest tests/test_twisterlang*.py
```

## 🐳 Docker Deployment

```bash
# Full stack deployment
docker-compose up -d

# Monitor logs
docker-compose logs -f api
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/twisterlab.git
cd twisterlab

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Supervisor**: Younes El Fakir
- **AI Team**: Autonomous execution agents
- **Community**: Open-source contributors

## 📞 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/youneselfakir0/twisterlab/issues)
- **Discussions**: [Community Q&A](https://github.com/youneselfakir0/twisterlab/discussions)
- **Email**: youneselfakir@outlook.com

---

**TwisterLab v1.0.0** - Ethical AI Infrastructure for IT Helpdesk Automation 🎯