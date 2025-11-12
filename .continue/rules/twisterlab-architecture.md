---
globs: "**/*"
description: TwisterLab project architecture and component structure for AI agent development
alwaysApply: true
---

# TwisterLab Project Architecture

TwisterLab is a multi-agent AI orchestration system for autonomous IT helpdesk automation with swarm intelligence.

## Core Architecture

### Agent-Based Design

- All agents inherit from `TwisterAgent` in `agents/base.py`
- Agents implement async `execute()` method with task/context parameters
- Use swarm intelligence via `SwarmMessenger` for inter-agent communication

### Key Components

- **AI Agents**: `agents/` - Core agent implementations (TicketClassifierAgent, AutoResolverAgent, etc.)
- **API Layer**: `agents/api/` - FastAPI routes and middleware at `/docs`
- **Swarm IA**: `agents/swarm/` - Swarm intelligence components and messaging
- **Database**: Async SQLAlchemy with PostgreSQL via `agents/database/services.py`
- **MCP Integration**: `agents/mcp/server.py` for Model Context Protocol

### Tech Stack

- **Backend**: Python 3.12+, FastAPI, PostgreSQL/asyncpg, Redis
- **AI/ML**: Ollama, LangChain, Hugging Face Evaluate
- **Infrastructure**: Docker Swarm, OpenTelemetry, Prometheus + Grafana
- **Development**: pytest, ruff, mypy, black

### File Organization

- `agents/` - Core agent implementations
- `agents/api/` - FastAPI routes and middleware
- `agents/swarm/` - Swarm intelligence components
- `tests/` - pytest test suite with fixtures in `conftest.py`
- `scripts/` - Deployment and utility scripts

### Communication Patterns

- Redis pub/sub via `SwarmMessenger` for inter-agent messaging
- `TwisterLangueParser` DSL for efficient agent communication
- Async operations throughout for scalability

When working with TwisterLab code, always consider the swarm intelligence architecture and agent-based design patterns.


