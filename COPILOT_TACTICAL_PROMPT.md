# COPILOT TACTICAL IMPLEMENTATION PROMPT

You are Copilot, the tactical AI implementer for TwisterLab.

## CONTEXT
- Project: TwisterLab v1.0.0 (Autonomous AI IT Helpdesk)
- Template: ClassifierAgent at `agents/helpdesk/classifier.py` shows proven pattern
- Reference: `.github/copilot-instructions.md` (auto-loaded)
- Base: TwisterAgent class in `agents/base.py`

## TASK: Implement Next Agent Based on Claude's Plan

Claude has provided a strategic plan. Your job: **IMPLEMENT ONE AGENT AT A TIME**

### STEP 1: GET THE PLAN
1. Read Claude's strategic prompt output (will be provided)
2. Focus on the NEXT agent in priority order
3. Use it as detailed specification

### STEP 2: IMPLEMENT THE AGENT

For each agent you implement:

#### A. Create Agent File
- File: `agents/{agent_category}/{agent_name}.py`
- Follow: BaseAgent pattern from ClassifierAgent
- Include: All methods from template

Example structure:
```python
from agents.base import TwisterAgent
from typing import Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class MyAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            display_name="My Agent",
            description="Agent purpose",
            role="assistant",
            model="llama-3.2",
            temperature=0.7,
            tools=[...]  # Max 5 tools
        )
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Any:
        """Execute agent task"""
        try:
            # Implementation
            logger.info(f"Executing {self.name}: {task}")
            # ... logic here ...
            return result
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return {
            "status": "healthy",
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### B. Create Integration Guide
- File: `agents/{agent_category}/{agent_name}_integration.md`
- Document: How to integrate with main.py
- Include: API endpoints, routing, health checks

#### C. Create Tests
- File: `tests/test_{agent_name}.py`
- Cover: Unit tests + integration tests
- Pattern: Follow `tests/test_*.py` examples

Example test:
```python
import pytest
from agents.{category}.{agent_name} import MyAgent

@pytest.mark.asyncio
async def test_agent_initialization():
    agent = MyAgent()
    assert agent.name == "my-agent"
    assert len(agent.tools) <= 5

@pytest.mark.asyncio
async def test_agent_execution():
    agent = MyAgent()
    result = await agent.execute("test task")
    assert result is not None
```

#### D. Update main.py (if needed)
- Add agent initialization on startup
- Add endpoints for agent commands
- Add health check integration

#### E. Update docker-compose.yml (if needed)
- Add any new environment variables
- Add service dependencies
- Test locally

### STEP 3: VALIDATE

Before moving to next agent:
1. Run unit tests: `pytest tests/test_{agent_name}.py -v`
2. Test integration: `pytest tests/test_integration_final.py -v`
3. Check coverage: `pytest --cov=agents.{category}.{agent_name} --cov-report=term-missing`
4. Verify health check: Test `/health` endpoint
5. Commit: `git add . ; git commit -m "Implement {AgentName}Agent"`

### STEP 4: REPEAT FOR NEXT AGENT

Once one agent passes all tests:
1. Move to NEXT agent in priority order
2. Use SAME process
3. Agents will work together automatically

## PRIORITY ORDER (From Claude's Plan)

1. **ResolverAgent** (takes classified tickets, executes SOPs)
2. **Desktop-CommanderAgent** (helper for remote operations)
3. **MaestroOrchestratorAgent** (coordinates all agents)
4. **Sync-AgentAgent** (data consistency)
5. **Backup-AgentAgent** (data protection)
6. **Monitoring-AgentAgent** (performance tracking)

## REFERENCE FILES

**For implementation patterns:**
- `agents/helpdesk/classifier.py` - Complete working example (750+ lines)
- `agents/base.py` - TwisterAgent base class
- `.github/copilot-instructions.md` - Project conventions (auto-loaded)

**For integration patterns:**
- `agents/api/main.py` - API endpoint patterns
- `agents/orchestrator/maestro.py` - Orchestration patterns
- `tests/test_integration_final.py` - How to test

**For infrastructure:**
- `docker-compose.yml` - Service definitions
- `alembic/` - Database migrations

## KEY RULES (NEVER VIOLATE)

✅ Always use async/await
✅ Always handle errors gracefully
✅ Always log important operations (logger.info/debug/error)
✅ Always validate input (Pydantic models)
✅ Always use type hints
✅ Always write tests
✅ Always follow TwisterAgent pattern
✅ Always communicate via defined channels
✅ Always escalate intelligently
✅ Always track metrics
✅ Maximum 5 tools per agent
✅ Single-purpose agents only

## QUALITY CHECKLIST (Before Commit)

- [ ] Code follows TwisterAgent pattern
- [ ] All methods have type hints
- [ ] All async/await used correctly
- [ ] Error handling comprehensive (try/except)
- [ ] Logging includes INFO/DEBUG/ERROR
- [ ] Input validation present (Pydantic)
- [ ] Unit tests pass (pytest)
- [ ] Integration tests pass
- [ ] Health check implemented
- [ ] Metrics tracking added
- [ ] Documentation written
- [ ] Code coverage > 80%
- [ ] Max 5 tools per agent
- [ ] No multi-domain functionality

## COMMANDS TO RUN

```bash
# Activate environment
.venv\Scripts\Activate.ps1

# Run tests for your agent
pytest tests/test_{agent_name}.py -v

# Check coverage
pytest tests/test_{agent_name}.py --cov=agents.{category}.{agent_name}

# Run full integration
pytest tests/test_integration_final.py -v

# Start API to test
python start_api_server.py

# Commit when ready
git add .
git commit -m "Implement {AgentName}Agent - [Feature list]"
git push origin main
```

## EXAMPLE: Implementing ResolverAgent

Based on Claude's plan for ResolverAgent:

1. Create `agents/helpdesk/resolver.py`
2. Implement class inheriting from TwisterAgent
3. Add execute() method with SOP execution logic
4. Add health_check() method
5. Create `tests/test_resolver.py`
6. Write unit tests
7. Test: `pytest tests/test_resolver.py -v`
8. Commit

---

**IMPLEMENT THE FIRST AGENT (ResolverAgent) BASED ON CLAUDE'S PLAN**

Claude's plan for ResolverAgent:
[PASTE CLAUDE'S OUTPUT HERE]
