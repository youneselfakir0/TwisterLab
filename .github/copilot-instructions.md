# TwisterLab v1.0.0 - AI Agent Development Guide

**Production-ready multi-agent AI orchestration system for autonomous IT helpdesk automation**

## AI Assistant Interaction Guidelines

When working with TwisterLab, AI assistants should:

**Core Principles**:
- **Production-First**: All solutions must be production-ready, not PoC/throwaway code
- **Real Infrastructure**: Only use technologies actually deployed (Docker Swarm, PostgreSQL, Redis, Ollama, Prometheus, Grafana)
- **Security-Conscious**: Never expose credentials, always validate inputs, audit all actions
- **Documentation-Driven**: Every change includes clear docs, type hints, and tests
- **Proactive Problem-Solving**: Identify weaknesses, suggest improvements, provide alternatives

**Response Style**:
- Concise, precise explanations with well-indented code
- Multi-step tasks get numbered checklists or plans
- Include rationale for technical decisions
- Suggest tests and monitoring approaches
- Point out trade-offs and edge cases

**Technology Stack** (only use these):
- **Backend**: Python 3.12+, FastAPI, asyncio, asyncpg
- **Infrastructure**: Docker Swarm, PostgreSQL 16, Redis 7
- **AI/LLM**: Ollama (llama3.2:1b), Open WebUI
- **Monitoring**: Prometheus, Grafana
- **Scripting**: PowerShell, Bash
- **Config**: YAML, TOML, .env files

**Common Tasks**:
- Agent implementation (inherit from `TwisterAgent` or create `Real*Agent`)
- Deployment automation (use `infrastructure/scripts/deploy.ps1`)
- Monitoring setup (Prometheus metrics + Grafana dashboards)
- Testing (pytest with asyncio, integration tests)
- LLM integration (Ollama API at `http://192.168.0.30:11434`)

**Forbidden**:
- Cloud-only services (AWS/Azure-specific without local alternatives)
- Unvetted dependencies not in `requirements.txt`
- Hardcoded credentials or secrets
- Code without type hints or docstrings
- Changes without corresponding tests

## Project Architecture

### Core Agent System (7 Agents)

All agents inherit from `TwisterAgent` (in `agents/base.py`) - a multi-framework base class supporting export to Microsoft, LangChain, Semantic Kernel, and OpenAI formats.

**Production Agents** (in `agents/real/`):
- `RealMonitoringAgent` - System health checks (CPU/RAM/disk/Docker)
- `RealBackupAgent` - Automated backups with disaster recovery
- `RealSyncAgent` - Cache/DB synchronization
- `RealClassifierAgent` - Ticket classification and routing
- `RealResolverAgent` - SOP execution for issue resolution
- `RealDesktopCommanderAgent` - Remote system command execution
- `RealMaestroAgent` - Workflow orchestration and load balancing

**Standard Agents** (in `agents/core/`, `agents/helpdesk/`, `agents/resolver/`, `agents/desktop_commander/`):
- Abstract implementations following BaseAgent pattern
- Reference implementations for new agent development

### Infrastructure Stack

**Current Deployment** (Docker Swarm on edgeserver.twisterlab.local):
- FastAPI (port 8000) - Main API
- PostgreSQL 16 (port 5432) - Primary database  
- Redis 7 (port 6379) - Cache + state management
- Ollama (port 11434) - Local LLM inference (llama3.2:1b)
- Open WebUI (port 8083) - Chat interface
- Traefik (ports 80/443/8080) - Load balancer
- Prometheus + Grafana (ports 9090/3000) - Monitoring

**Reorganized Structure** (as of v1.0.0 - 2025-11-10):
```
infrastructure/
├── docker/docker-compose.unified.yml    # Single compose file for all envs
├── configs/.env.production              # Production config
├── configs/.env.staging                 # Staging config
└── scripts/deploy.ps1                   # Unified deployment script
```

**Previous chaos**: 26+ docker-compose files, 18 Dockerfiles, 90+ PowerShell scripts → **Now**: 1 compose file, 2 configs, 1 deploy script

## MCP Communication Architecture

**Current Status**: MCP Router exists in `agents/mcp/mcp_router.py` with tier-based isolation design, but MCP servers are not yet deployed.

The MCP Router defines 4 isolation tiers for future implementation:
- **Tier 1** (172.25.0.0/16): TwisterLab agent MCPs
- **Tier 2** (172.26.0.0/16): Claude Desktop MCPs  
- **Tier 3** (172.27.0.0/16): Docker system MCPs
- **Tier 4** (172.28.0.0/16): Copilot MCPs

**Current Agent Communication**: Agents currently communicate via direct Python calls in `AutonomousAgentOrchestrator` rather than through deployed MCP servers. The MCP Router provides the foundation for future secure, isolated inter-agent communication.

## Agent Development Patterns

### 1. TwisterAgent Base Class

All agents MUST inherit from `TwisterAgent` in `agents/base.py`:

```python
from agents.base import TwisterAgent
from typing import Dict, Any, Optional

class MyNewAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="my-new-agent",
            display_name="My New Agent",
            description="What this agent does",
            role="assistant",
            model="llama-3.2",          # or "gpt-4", etc.
            temperature=0.7,
            tools=[self._define_tools()],  # Max 5 tools per agent
            metadata={"version": "1.0"}
        )
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute agent task - MUST be implemented"""
        # Your logic here
        pass
    
    def _define_tools(self) -> list:
        """Define agent tools in OpenAI function calling format"""
        return [{
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "What it does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "..."}
                    },
                    "required": ["param1"]
                }
            }
        }]
```

### 2. Real Agent Pattern (Production)

For production-ready agents in `agents/real/`:

```python
class RealMyAgent:
    """Real working agent with actual implementation"""
    
    def __init__(self):
        self.name = "RealMyAgent"
        # No inheritance - direct implementation
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real operation"""
        try:
            result = await self._perform_actual_work(context)
            return {
                "status": "success",
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": result
            }
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            return {"status": "error", "error": str(e)}
```

### 3. Multi-Framework Export

TwisterAgent supports exporting to multiple frameworks:

```python
agent = MyAgent()

# Export to Microsoft Agent Framework
microsoft_schema = agent.to_schema("microsoft")

# Export to LangChain
langchain_schema = agent.to_schema("langchain")

# Export to OpenAI Assistants API
openai_schema = agent.to_schema("openai")

# Export to Semantic Kernel
sk_schema = agent.to_schema("semantic-kernel")
```

## Deployment Workflows

### Local Development

```powershell
# 1. Start staging environment
.\infrastructure\scripts\deploy.ps1 -Environment staging

# 2. Verify services
curl http://localhost:8000/health
curl http://localhost:3000  # Grafana

# 3. Run tests
pytest tests/ -v --cov=agents

# 4. Code quality
ruff check agents/
mypy agents/
```

### Production Deployment

**Current method** (unified deployment script):
```powershell
# Deploy to production (edgeserver.twisterlab.local)
.\infrastructure\scripts\deploy.ps1 -Environment production

# Force redeployment
.\infrastructure\scripts\deploy.ps1 -Environment production -Force

# Deploy manually via SSH
ssh twister@192.168.0.30
cd /home/twister
export $(cat .env.production | xargs)
docker stack deploy -c docker-compose.yml twisterlab
```

**What happens**:
1. Validates prerequisites (Docker, Swarm, files)
2. Loads environment config (`.env.production` or `.env.staging`)
3. Deploys stack to Docker Swarm (6 services)
4. Runs health checks (30s timeout per service)
5. Reports status for all services

**Production endpoint**: http://192.168.0.30:8000
**Monitoring**: http://192.168.0.30:3000 (Grafana)

### Agent Registration

**Understanding the Architecture**:
- **`AutonomousAgentOrchestrator`** (`agents/orchestrator/autonomous_orchestrator.py`): Manages scheduled background tasks for autonomous agents (monitoring, backup, sync)
- **`MaestroOrchestratorAgent`** (`agents/core/maestro_orchestrator_agent.py`): Handles workflow coordination and load balancing for ticket processing
- **`RealMaestroAgent`** (`agents/real/real_maestro_agent.py`): Production implementation of workflow orchestration

To add a new agent to the autonomous system:

```python
# In agents/orchestrator/autonomous_orchestrator.py
from agents.real.real_my_agent import RealMyAgent

async def initialize_agents(self):
    self.agents = {
        "monitoring": MonitoringAgent(),
        "backup": BackupAgent(),
## Testing Requirements

**Current Test Status**: 22 test files in `tests/` directory (as of 2025-11-11)

**Pytest configuration** (in `pyproject.toml`):
```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "slow: Slow running tests",
    "azure: Tests requiring Azure resources"
]
```

**Test structure**:
```
tests/
├── test_agents/                    # Agent-specific tests
│   ├── test_maestro_orchestrator_agent.py
│   └── test_maestro_orchestrator_agent_simple.py
├── integration/                    # Cross-component tests
│   └── test_mcp_integration.py
├── unit/                           # Unit tests
│   └── test_maestro.py
├── test_monitoring_agent.py        # Individual agent tests
├── test_backup_agent.py
├── test_sync_agent.py
├── test_resolver.py
├── test_classifier_llm.py
└── test_integration_real_agents.py # Full system tests
```

**Coverage**: No recent coverage data available. Run `pytest tests/ -v --cov=agents --cov-report=html` to generate.
**Test structure**:
```
tests/
├── test_agents/           # Agent-specific tests
├── integration/           # Cross-component tests
├── unit/                  # Unit tests
└── test_*_agent.py       # Individual agent tests
```

**Writing tests**:
```python
import pytest
from agents.real.real_my_agent import RealMyAgent

@pytest.mark.asyncio
async def test_my_agent_execution():
    agent = RealMyAgent()
    result = await agent.execute({"test": "data"})
    assert result["status"] == "success"
    assert "data" in result
```

**Run tests**:
```powershell
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_my_agent.py -v

# With coverage report
pytest tests/ -v --cov=agents --cov-report=html

# Async tests only
pytest tests/ -v -m asyncio
```

## Key Conventions

### Import Paths
```python
# ✅ CORRECT - Absolute imports from project root
from agents.base import TwisterAgent
from agents.real.real_monitoring_agent import RealMonitoringAgent

# ❌ WRONG - Relative imports
from ..base import TwisterAgent
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# ✅ Structured logging
logger.info(f"{self.name}: Task completed", extra={
    "agent": self.name,
    "duration_ms": duration,
    "status": "success"
})

# ❌ Don't log sensitive data
logger.info(f"Password: {password}")  # NEVER DO THIS
```

### Async/Await
```python
# ✅ All agent execute() methods must be async
async def execute(self, context: Dict) -> Dict:
    result = await self._perform_work()
    return result

# ✅ Use asyncio for concurrent operations
import asyncio
results = await asyncio.gather(
    self.check_cpu(),
    self.check_memory(),
    self.check_disk()
)
```

### Type Hints (MANDATORY)
```python
# ✅ All functions must have type hints
async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    pass

# ❌ No type hints
async def execute(self, context):
    pass
```

## Common Operations

### Access Ollama LLM
```python
import aiohttp

async def query_llm(self, prompt: str) -> str:
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "llama3.2:1b",
            "prompt": prompt,
            "stream": False
        }
        async with session.post(
            "http://192.168.0.30:11434/api/generate",
            json=payload
        ) as resp:
            data = await resp.json()
            return data.get("response", "")
```

### Database Access
```python
import asyncpg

async def query_database(self, query: str):
### Redis Cache
```python
import aioredis

async def cache_data(self, key: str, value: Any):
    redis = await aioredis.create_redis_pool(
        f"redis://:{os.getenv('REDIS_PASSWORD')}@192.168.0.30:6379"
    )
    try:
        await redis.set(key, json.dumps(value))
        await redis.expire(key, 3600)  # 1 hour TTL
    finally:
        redis.close()
        await redis.wait_closed()
```

## Security & Credentials

**Current Status**: Basic encryption references exist in `BackupAgent` (mentions "vault" for encryption keys), but full credential management system with Fernet encryption is not yet implemented.

**Planned Features** (referenced in code but not fully deployed):
- Encrypted credential storage
- Tier-based credential scoping (enterprise vs personal)
- Audit logging for credential access

**Current Best Practice**: Store sensitive credentials in environment variables (`.env.production`, `.env.staging`) and access via `os.getenv()`. Never commit credentials to version control. Redis Cache
```python
import aioredis

async def cache_data(self, key: str, value: Any):
    redis = await aioredis.create_redis_pool(
        f"redis://:{os.getenv('REDIS_PASSWORD')}@192.168.0.30:6379"
    )
    try:
        await redis.set(key, json.dumps(value))
        await redis.expire(key, 3600)  # 1 hour TTL
    finally:
        redis.close()
        await redis.wait_closed()
```

## Troubleshooting

### Agent Not Loading
```powershell
# Check if agent is registered in orchestrator
ssh twister@192.168.0.30 "docker exec twisterlab_api.1.* python -c 'from agents.orchestrator.autonomous_orchestrator import orchestrator; print(orchestrator.agents.keys())'"

# Check logs
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 100"
```

### Service Not Starting
```powershell
# Check service status
ssh twister@192.168.0.30 "docker service ls"

# Inspect specific service
ssh twister@192.168.0.30 "docker service ps twisterlab_api --no-trunc"

# View logs
ssh twister@192.168.0.30 "docker service logs twisterlab_postgres --tail 50"
```

### Database Connection Failed
```powershell
# Verify PostgreSQL is running
ssh twister@192.168.0.30 "docker exec twisterlab_postgres.1.* pg_isready -U twisterlab"

# Test connection
ssh twister@192.168.0.30 "docker exec twisterlab_postgres.1.* psql -U twisterlab -c 'SELECT version();'"
```

## References

- **Main README**: `README.md` - Project overview
- **Reorganization Guide**: `REORGANISATION_COMPLETE.md` - v1.0 migration
- **Changelog**: `CHANGELOG.md` - Version history
- **Infrastructure**: `infrastructure/README.md` - Deployment docs
- **Agent Examples**: `agents/real/` - Production implementations
- **Base Classes**: `agents/base.py` - TwisterAgent foundation

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-11  
**Production Status**: ✅ Operational (6/6 services running)
