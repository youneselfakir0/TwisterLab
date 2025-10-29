# TwisterLab AI Agent Development Guide

## Project Overview

TwisterLab is an AI-powered IT Helpdesk automation platform using a multi-agent architecture with MCP protocol integration. The system automates 60-70% of repetitive helpdesk tickets through specialized agents.

## Core Architecture Patterns

### Agent System (`agents/base.py`)

- **Base Class**: All agents inherit from `TwisterAgent(ABC)`
- **Multi-Framework Export**: Agents export to Microsoft Agent Framework, LangChain, Semantic Kernel, OpenAI formats
- **Tool Pattern**: MCP-style function tools with OpenAPI parameter schemas
- **Naming Convention**: Kebab-case agent names (`helpdesk-resolver`, `classifier`, `desktop-commander`)

**Agent Structure**:

```python
class CustomAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="agent-name",           # kebab-case identifier
            display_name="Display Name", # human-readable
            description="Agent purpose",
            role="agent_role",           # helpdesk, classifier, etc.
            instructions="System prompt",
            tools=[{...}],               # MCP function tools
            model="llama-3.2",           # or deepseek-r1
            temperature=0.3,             # role-specific (0.1-0.7)
            metadata={"key": "value"}    # additional context
        )

    async def execute(self, task: str, context=None) -> Any:
        # Implementation
        pass
```

### API Layer (`agents/api/`)

- **Framework**: FastAPI with async endpoints
- **Router Pattern**: Modular routers in separate files (`routes_tickets.py`, `routes_agents.py`, `routes_sops.py`)
- **Models**: Pydantic v2 with field validation
- **Response Pattern**: Consistent error handling with HTTPException

**Router Structure**:

```python
router = APIRouter()

class RequestModel(BaseModel):
    field: str = Field(..., min_length=1, max_length=100)

class ResponseModel(BaseModel):
    id: str
    field: str
    created_at: datetime

@router.post("/", response_model=ResponseModel)
async def create_item(request: RequestModel):
    # Implementation
    pass
```

### CLI System (`cli/twisterlab.py`)

- **Framework**: Typer with Rich for terminal output
- **Commands**: `list-agents`, `export-agent`, `show-agent`, `version`
- **Agent Registry**: Dictionary mapping agent names to classes
- **Export Formats**: Microsoft (production), LangChain/SK/OpenAI (stubs)

**CLI Command Pattern**:

```python
@app.command("command-name")
def command_name(
    param: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--option", help="Description")
):
    # Implementation with Rich console output
    pass
```

## Development Workflow

### Environment Setup

```bash
# Always use virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# For development
pip install -e .  # Editable install
```

### Running the System

```bash
# Full stack with Docker
docker-compose up -d

# API server only
uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload

# CLI commands
python -m cli.twisterlab list-agents
python -m cli.twisterlab export-agent helpdesk-resolver
```

### Testing

```bash
# Run all tests
pytest -v

# With coverage
pytest --cov=agents --cov-report=html

# Async tests
pytest -k "test_async" --asyncio-mode=auto
```

## Key Conventions

### Code Quality

- **Type Hints**: Full typing with `typing` module
- **Docstrings**: Google-style with Args/Returns/Raises
- **Formatting**: Black with 88 char line length
- **Imports**: isort with standard library first
- **Linting**: flake8 with strict rules

### Agent Design

- **Temperature Settings**:
  - `0.1`: Precise operations (Desktop Commander)
  - `0.2`: Consistent classification (Classifier)
  - `0.3`: IT operations (Helpdesk)
  - `0.7`: Creative tasks
- **Tool Schemas**: OpenAPI 3.0 format with required/optional fields
- **Error Handling**: Async context managers, proper exception chaining

### API Design

- **URL Structure**: `/api/v1/{resource}/`
- **HTTP Methods**: RESTful with proper status codes
- **Validation**: Pydantic models with Field constraints
- **Pagination**: Cursor-based for large datasets
- **CORS**: Configured for frontend integration

### Database Patterns

- **ORM**: SQLAlchemy 2.0 async
- **Migrations**: Alembic for schema changes
- **Connections**: Connection pooling with health checks
- **Models**: Declarative base with relationships

## Integration Points

### MCP Protocol

- **Transport**: SSE/WebSocket for remote servers, stdio for local
- **Tools**: Function calling with JSON-RPC 2.0
- **Security**: Zero-trust with JWT authentication

### External Services

- **Ollama**: Local LLM inference (DeepSeek-R1, Llama 3.2)
- **PostgreSQL**: Persistent data storage
- **Redis**: Caching and session state
- **OpenWebUI**: Chat-based frontend

### Azure Integration (Optional)

- **AD Auth**: JWT with Azure AD B2C
- **Key Vault**: Secrets management
- **Cosmos DB**: Agent state storage
- **Functions**: Serverless task processing

## Common Patterns

### Agent Registration

```python
# In cli/twisterlab.py
AGENTS = {
    "agent-name": AgentClass,
}

# Export formats
SUPPORTED_FORMATS = ["microsoft", "langchain", "semantic-kernel", "openai"]
```

### Tool Definition

```python
tools = [{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Param description"}
            },
            "required": ["param"]
        }
    }
}]
```

### Async Error Handling

```python
try:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()
except aiohttp.ClientError as e:
    logger.error(f"API call failed: {e}")
    raise HTTPException(502, "External service unavailable")
```

## Deployment Architecture

### Docker Services

- **postgres**: Data persistence
- **redis**: Caching/state
- **ollama**: AI inference
- **api**: FastAPI application
- **openwebui**: Frontend (optional)

### Configuration

- **Environment Variables**: `.env` file
- **Agent Configs**: `config/agent_schemas/` (JSON exports)
- **Routing Rules**: `config/routing_rules.yaml`

## Testing Strategy

### Unit Tests

- **Framework**: pytest-asyncio
- **Coverage**: >80% target
- **Mocks**: External API calls and database operations

### Integration Tests

- **API Endpoints**: Full request/response cycles
- **Agent Workflows**: End-to-end task execution
- **MCP Tools**: Tool calling and response handling

### Performance Tests

- **Load Testing**: Concurrent agent execution
- **Latency**: <500ms API response target
- **Throughput**: 100+ RPS capacity

## Security Considerations

### Authentication

- **JWT Tokens**: 30min access, 7-day refresh
- **Azure AD**: Optional enterprise integration
- **API Keys**: Service-to-service communication

### Authorization

- **RBAC**: Role-based access control
- **Tool Guards**: Risk-based validation
- **Rate Limiting**: Sliding window limits

### Data Protection

- **Encryption**: AES-256 for sensitive data
- **Audit Trail**: Immutable operation logs
- **Compliance**: GDPR-ready architecture

## Key Files Reference

| File | Purpose | Key Patterns |
|------|---------|--------------|
| `agents/base.py` | Agent base classes | TwisterAgent, schema export |
| `agents/api/main.py` | FastAPI app | Router inclusion, logging |
| `agents/api/routes_*.py` | API endpoints | Pydantic models, async handlers |
| `cli/twisterlab.py` | CLI interface | Typer commands, Rich output |
| `config/agent_schemas/*.json` | Agent exports | Microsoft Agent Framework format |
| `docker-compose.yml` | Services | Multi-container setup |
| `pyproject.toml` | Project config | Dependencies, scripts |
| `requirements.txt` | Dependencies | Pinned versions |

## Getting Started

1. **Setup Environment**: `python -m venv .venv && .venv\Scripts\activate`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Start Services**: `docker-compose up -d`
4. **Run API**: `uvicorn agents.api.main:app --reload`
5. **Test CLI**: `python -m cli.twisterlab list-agents`

## Development Guidelines

- **Agent-First**: Design agents before APIs
- **MCP-Compliant**: Follow Model Context Protocol standards
- **Test-Driven**: Write tests before implementation
- **Type-Safe**: Use full type hints throughout
- **Async-Native**: All I/O operations are async
- **Zero-Cost**: No permanent cloud costs for portfolio use
