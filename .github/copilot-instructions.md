# TwisterLab AI Coding Instructions

## Architecture Overview
TwisterLab is a multi-agent IT helpdesk automation system using FastAPI, PostgreSQL, Redis, and MCP protocol. Core components:
- **Agents**: Specialized classes in `agents/` (Classifier, Resolver, Desktop Commander)
- **API**: FastAPI app in `agents/api/main.py` with routers for tickets, agents, SOPs
- **Database**: SQLAlchemy models in `agents/database/models.py`, migrations via Alembic
- **Orchestration**: Maestro agent coordinates task routing in `agents/orchestrator/maestro.py`

## Development Patterns

### Agent Creation
Extend `TwisterAgent` from `agents/base.py`. Always include:
- `name`: kebab-case identifier
- `tools`: MCP function definitions with OpenAPI schemas
- `execute()`: async method for task processing
- Schema export methods for Microsoft/LangChain compatibility

Example from `agents/helpdesk/classifier.py`:
```python
class TicketClassifierAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="classifier",
            display_name="Ticket Classifier",
            tools=[{"type": "function", "function": {...}}],
            model="deepseek-r1",
            temperature=0.2
        )
```

### API Endpoints
Use FastAPI routers in `agents/api/routes_*.py`. Pattern:
- Async endpoint functions
- Pydantic request/response models
- Dependency injection for database sessions
- Structured error responses

Example from `agents/api/routes_tickets.py`:
```python
@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
```

### Database Operations
Use SQLAlchemy async sessions. Pattern:
- `agents/database/config.py` for session management
- `agents/database/services.py` for business logic
- Alembic migrations in `alembic/versions/`

Example service pattern from `agents/database/services.py`:
```python
class SOPService:
    @staticmethod
    async def get_active_sops(db: AsyncSession) -> List[SOP]:
        result = await db.execute(select(SOP).where(SOP.is_active == True))
        return result.scalars().all()
```

### CLI Commands
Use Typer + Rich in `cli/twisterlab.py`. Pattern:
- Commands as decorated functions
- Rich tables for output formatting
- Agent registry dictionary for dynamic loading

Example:
```python
AGENTS = {
    "helpdesk-resolver": HelpdeskAgent,
    "classifier": ClassifierAgent,
}

@app.command("list-agents")
def list_agents():
    table = Table()
    for name, cls in AGENTS.items():
        agent = cls()
        table.add_row(name, agent.display_name, str(len(agent.tools)))
    console.print(table)
```

### Testing
Use pytest-asyncio for async tests. Pattern:
- Test files in root directory (not `tests/`)
- FastAPI TestClient for API tests
- Async database sessions in fixtures

Example from `test_api.py`:
```python
def test_create_ticket() -> Optional[str]:
    response = requests.post(f"{BASE_URL}/api/v1/tickets/", json=ticket_data)
    assert response.status_code == 201
    return response.json().get("id")
```

## Key Conventions

- **Imports**: Relative imports within `agents/` package
- **Async/Await**: All I/O operations are async
- **Error Handling**: Structured exceptions with logging
- **Configuration**: Environment variables via `python-dotenv`
- **Logging**: Structured logging with context
- **Dependencies**: Minimal, pinned versions in `pyproject.toml`

## Integration Points

- **MCP Protocol**: Tool definitions follow MCP specification
- **Ollama**: Local LLM inference at `http://localhost:11434`
- **Redis**: State management and caching
- **PostgreSQL**: Persistent data storage
- **OpenWebUI**: Frontend integration via custom connector

## Development Workflow

### Local Development
1. Activate venv: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
2. Start services: `docker-compose up -d`
3. Run API: `uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload`
4. Test CLI: `python -m cli.twisterlab list-agents`

### Database Changes
1. Modify models in `agents/database/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

### Adding New Agents
1. Create agent class in appropriate `agents/` subdirectory
2. Add to `AGENTS` dict in `cli/twisterlab.py`
3. Add API routes if needed in `agents/api/routes_agents.py`
4. Export schemas to `config/agent_schemas/`

## Reference Files
- `agents/base.py` - TwisterAgent base class
- `agents/api/main.py` - FastAPI application setup
- `cli/twisterlab.py` - CLI commands and agent registry
- `agents/database/models.py` - SQLAlchemy models
- `agents/orchestrator/maestro.py` - Central orchestrator
- `pyproject.toml` - Dependencies and configuration
- `docker-compose.yml` - Local development services

## Constraints

### What NOT to Do (v1.0)
❌ NO Multi-Vertical Agents
❌ NO Universal Agent
❌ NO Agent Auto-Creation
❌ NO Azure Premium
❌ NO Partial Code
❌ NO >5 Tools per Task

### Coding Standards
✅ Full type hints
✅ Async/await
✅ Error handling
✅ Pydantic models
✅ Docstrings
✅ Tests >80%

---

## Technical Excellence Standards

For comprehensive quality gates, operational requirements, and production-readiness criteria, refer to:

📘 **[System Prompt - Technical Excellence](../docs/SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md)**

This document defines:
- ✅ **Quality Gates**: Linting, tests (≥80% coverage), performance benchmarks, security scans
- ✅ **Observability**: Metrics exposure, monitoring integration, alert configuration
- ✅ **Robustness**: Error handling, retry logic, health checks, failure testing
- ✅ **Traceability**: Structured logging, audit trails, diagnostic context
- ✅ **Deployment**: Automated pipelines, rollback procedures, smoke tests
- ✅ **Continuous Improvement**: Post-mortems, performance optimization, permanent fixes

**All code MUST comply with these standards before merging/deploying.**

---

**Last Updated**: 2025-02-11
**Version**: 1.0.0
**License**: Apache 2.0

**This document is the SINGLE SOURCE OF TRUTH for TwisterLab v1.0 development.**
