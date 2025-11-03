# 🚀 TWISTERLAB v1.0.0 - COMPLETE COPILOT VS CODE SYSTEM PROMPT
# À coller dans .github/copilot-instructions.md ou dans VS Code Copilot Chat settings

---

## CONTEXT: PROJECT OVERVIEW

You are assisting with **TwisterLab v1.0.0** - a production-grade multi-agent AI orchestration system for autonomous IT helpdesk automation.

**Project Status**: 83% complete (10/12 milestones)
**Active Environment**: Staging validated, Production-ready
**Tech Stack**: Python 3.11+, FastAPI, PostgreSQL, Redis, Docker Swarm, Kubernetes-ready
**Repository**: https://github.com/youneselfakir0/TwisterLab

---

## PART 1: TWISTERLAB ARCHITECTURE (READ FIRST)

### System Components

**7 Production AI Agents** (all 100% tested):
1. **ClassifierAgent** - Analyzes incoming tickets, routes to appropriate agent
2. **ResolverAgent** - Executes SOPs, resolves issues autonomously
3. **Desktop-CommanderAgent** - Executes system commands securely (Windows/Linux)
4. **MaestroOrchestratorAgent** - Load balancing, workflow orchestration
5. **SyncAgent** - Cache/DB synchronization, consistency verification
6. **BackupAgent** - Disaster recovery, automated backups
7. **MonitoringAgent** - Real-time metrics, alerting, health checks

**Infrastructure**:
- PostgreSQL (high-availability)
- Redis (caching + state management)
- Prometheus (metrics collection)
- Grafana (dashboards)
- Docker Swarm (4-node production cluster)
- GitHub Actions (CI/CD pipelines)

**Deployment Models**:
- Staging: docker-compose.staging.yml (local testing)
- Production: docker-compose.production.yml (blue-green zero-downtime)
- CI/CD: Automated test → deploy → validate → rollback

---

## PART 2: MCP ISOLATION & CREDENTIAL MANAGEMENT (CRITICAL)

### 4-Tier MCP Architecture (MANDATORY ISOLATION)

```
TIER 1: TwisterLab Agent MCPs (172.25.0.0/16, ports 9000-9100)
  ├─ linkedin_mcp (9001)
  ├─ twitter_mcp (9002)
  ├─ email_mcp (9003)
  ├─ github_mcp (9004)
  └─ notion_mcp (9005)
  🔒 Access: ONLY TwisterLab agents

TIER 2: Claude Desktop MCPs (172.26.0.0/16, ports 9200-9300)
  ├─ claude_filesystem_mcp (9201)
  ├─ claude_web_search_mcp (9202)
  ├─ claude_code_analysis_mcp (9203)
  └─ claude_knowledge_base_mcp (9204)
  🔒 Access: ONLY Claude Desktop

TIER 3: Docker System MCPs (172.27.0.0/16, ports 9400-9500)
  ├─ docker_monitoring_mcp (9401)
  ├─ docker_orchestration_mcp (9402)
  └─ docker_health_check_mcp (9403)
  🔒 Access: ONLY Docker daemon + Maestro

TIER 4: Copilot MCPs (172.28.0.0/16, ports 9600-9700)
  ├─ copilot_code_completion_mcp (9601)
  ├─ copilot_github_mcp (9602)
  └─ copilot_repo_analysis_mcp (9603)
  🔒 Access: ONLY GitHub Copilot

FIREWALL RULES:
  ❌ NO cross-tier communication allowed
  ✅ Each tier completely isolated
```

### Credential Management Rules (NON-NEGOTIABLE)

**Rule 1: Encryption**
- ✅ ALL credentials encrypted with Fernet cipher
- ✅ Master password stored in secure ENV var ONLY (never in code/logs)
- ✅ Plaintext credentials destroyed after use

**Rule 2: Scoping**
- ✅ Enterprise credentials (DB, Docker, Office365) ≠ Personal credentials (LinkedIn, Twitter)
- ✅ Agents access ONLY assigned credentials
- ✅ ClassifierAgent CANNOT access LinkedIn credentials

**Rule 3: Audit Trail**
- ✅ Every credential access logged with timestamp, agent, result
- ✅ NO plaintext credentials in logs
- ✅ Failed access attempts trigger alerts

**Rule 4: Emergency Protocol**
- ✅ If credentials compromised: immediate revocation + agent stop
- ✅ Security team alert sent automatically
- ✅ Full audit trail preserved

---

## PART 3: CODING STANDARDS (MANDATORY)

### Code Quality Requirements

**Type Hints (PEP 484)**
```python
# ✅ CORRECT
async def process_ticket(ticket_id: str, priority: int) -> Dict[str, Any]:
    """Process ticket with validation."""
    pass

# ❌ WRONG
async def process_ticket(ticket_id, priority):
    pass
```

**Docstrings (Google Style)**
```python
# ✅ CORRECT
async def authenticate_service(service: str) -> Session:
    """
    Authenticate to external service using encrypted credentials.
    
    Args:
        service: Service name (e.g., 'linkedin', 'twitter')
    
    Returns:
        Authenticated session object
    
    Raises:
        CredentialNotFoundError: If credentials not configured
        AuthenticationFailedError: If authentication fails
    
    Example:
        >>> session = await authenticate_service('linkedin')
        >>> result = await session.post_content('Hello world')
    """
    pass
```

**Error Handling**
```python
# ✅ CORRECT - Specific exceptions
try:
    creds = await get_credentials('linkedin')
except CredentialNotFoundError as e:
    logger.warning(f"Credentials missing for linkedin: {e}")
    raise
except AuthenticationFailedError as e:
    logger.error(f"Authentication failed: {e}")
    await alert_operator()
    raise

# ❌ WRONG - Generic exception
try:
    creds = await get_credentials('linkedin')
except Exception:
    pass
```

**Logging (Structured, no secrets)**
```python
# ✅ CORRECT
logger.info(
    "Agent execution started",
    extra={
        'agent': 'ClassifierAgent',
        'ticket_id': 'T-001',
        'timestamp': datetime.now().isoformat()
    }
)

# ❌ WRONG - Contains sensitive data
logger.info(f"Authenticated as {password}@{service}")
```

**Testing Requirements**
- ✅ Every module MUST have unit tests (pytest)
- ✅ MINIMUM 80% code coverage (enforced by CI)
- ✅ Integration tests for end-to-end flows
- ✅ Mock external services (avoid real API calls in tests)

---

## PART 4: AGENT IMPLEMENTATION PATTERNS

### BaseAgent Pattern (MANDATORY)

All agents MUST inherit from BaseAgent:

```python
from agents.base.base_agent import BaseAgent
from typing import Dict, Any

class CustomAgent(BaseAgent):
    """
    Your agent description.
    
    Responsibilities:
    - What it does
    - How it integrates with other agents
    """
    
    def __init__(self):
        super().__init__()
        self.name = "CustomAgent"
        self.priority = 5
        self.capabilities = ['capability_1', 'capability_2']
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic.
        
        Args:
            context: Input context (ticket, data, etc)
        
        Returns:
            Result dict with status, data, errors
        """
        try:
            # 1. Validate input
            self._validate_context(context)
            
            # 2. Log start
            await self.audit_log('execute_start', context)
            
            # 3. Execute logic
            result = await self._process(context)
            
            # 4. Log success
            await self.audit_log('execute_success', result)
            
            return result
        
        except Exception as e:
            # 5. Log error (without exposing sensitive data)
            await self.audit_log('execute_failed', {'error_type': type(e).__name__})
            raise
    
    async def _process(self, context: Dict) -> Dict[str, Any]:
        """Override this method with agent-specific logic."""
        raise NotImplementedError("Subclasses must implement _process()")
    
    def _validate_context(self, context: Dict) -> None:
        """Validate input context."""
        required_fields = ['ticket_id', 'priority']
        for field in required_fields:
            if field not in context:
                raise ValueError(f"Missing required field: {field}")
```

### Agent Interaction Pattern

```python
# Agents communicate via MCP Router (never directly)
from agents.mcp.mcp_router import MCPRouter

class MyAgent(BaseAgent):
    
    async def call_other_agent(self, agent_name: str, operation: str, params: Dict) -> Dict:
        """
        Call another agent via isolated MCP (secure, audited).
        
        Args:
            agent_name: Target agent name
            operation: Operation to execute
            params: Operation parameters
        
        Returns:
            Result from target agent
        """
        return await self.mcp_router.route_to_mcp(
            agent_name=self.name,
            mcp_name=f'{agent_name}_mcp',
            operation=operation,
            params=params
        )
```

---

## PART 5: TESTING PATTERNS

### Unit Test Template

```python
import pytest
from agents.custom_agent import CustomAgent

@pytest.fixture
def agent():
    """Setup test agent."""
    return CustomAgent()

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initializes correctly."""
    assert agent.name == "CustomAgent"
    assert agent.priority >= 1
    assert len(agent.capabilities) > 0

@pytest.mark.asyncio
async def test_agent_execute_success(agent):
    """Test agent executes successfully."""
    context = {
        'ticket_id': 'T-001',
        'priority': 'high',
        'data': {'issue': 'test'}
    }
    
    result = await agent.execute(context)
    
    assert result['status'] == 'success'
    assert 'data' in result

@pytest.mark.asyncio
async def test_agent_execute_failure(agent):
    """Test agent handles errors correctly."""
    invalid_context = {}  # Missing required fields
    
    with pytest.raises(ValueError):
        await agent.execute(invalid_context)

@pytest.mark.asyncio
async def test_agent_credential_isolation(agent):
    """Test agent cannot access unauthorized credentials."""
    # This should FAIL - enterprise agent accessing personal scope
    with pytest.raises(CredentialScopeViolation):
        await agent.get_credentials('linkedin')  # Agent should only access enterprise creds
```

### Integration Test Template

```python
@pytest.mark.asyncio
async def test_full_ticket_pipeline():
    """Test complete ticket flow: Email → Classifier → Resolver → Desktop-Commander → Sync → Monitoring."""
    
    # 1. Create test ticket
    ticket = {
        'ticket_id': 'T-INT-001',
        'title': 'Cannot connect to WiFi',
        'priority': 'high'
    }
    
    # 2. Execute pipeline
    classifier = ClassifierAgent()
    classified = await classifier.execute({'ticket': ticket})
    
    assert classified['status'] == 'success'
    assert classified['routed_to_agent'] == 'resolver'
    
    # 3. Continue through chain...
    # (test each agent in sequence)
```

---

## PART 6: DEPLOYMENT WORKFLOWS

### Local Development
```bash
# 1. Start staging environment
docker-compose -f docker-compose.staging.yml up -d

# 2. Verify services
curl http://localhost:8001/health          # API
curl http://localhost:3001                 # Grafana

# 3. Run tests
pytest tests/ -v --cov=agents --cov-report=html

# 4. Check code quality
black agents/
pylint agents/
mypy agents/

# 5. Commit & push
git add .
git commit -m "feat: [agent-name] [description]"
git push origin main
```

### Production Deployment
```bash
# 1. Create production environment file
cp .env.production.example .env.production
# Edit with real values

# 2. Deploy with GitHub Actions
# Just push to main branch - CI/CD handles:
#   - Run all tests
#   - Build Docker images
#   - Deploy to staging (validate)
#   - Deploy to production (blue-green)
#   - Run smoke tests
#   - Automatic rollback if failed

# 3. Monitor
curl http://localhost:3001  # Grafana dashboards
curl http://localhost:9090  # Prometheus
```

---

## PART 7: DIRECTORY STRUCTURE (REFERENCE)

```
twisterlab/
├── agents/
│   ├── __init__.py
│   ├── base/
│   │   └── base_agent.py           # BaseAgent class (inherit from this)
│   ├── core/
│   │   ├── classifier_agent.py      # #1 - Ticket classification
│   │   ├── resolver_agent.py        # #2 - SOP execution
│   │   ├── desktop_commander_agent.py # #3 - System commands
│   │   └── maestro_agent.py         # #4 - Orchestration
│   ├── support/
│   │   ├── sync_agent.py            # #5 - Cache sync
│   │   ├── backup_agent.py          # #6 - Backup/recovery
│   │   └── monitoring_agent.py      # #7 - Monitoring
│   ├── mcp/
│   │   ├── mcp_router.py            # Route MCP calls (CRITICAL)
│   │   └── credential_manager.py    # Credential encryption (CRITICAL)
│   └── security/
│       └── credential_access.py     # Secure credential usage
├── api/
│   ├── main.py                      # FastAPI app
│   ├── routes/
│   │   ├── agents.py
│   │   ├── tickets.py
│   │   └── monitoring.py
│   └── middleware/
│       ├── auth.py
│       └── logging.py
├── tests/
│   ├── test_agents/
│   ├── test_api/
│   ├── test_integration_full_system.py
│   └── test_mcp_isolation.py
├── monitoring/
│   ├── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── prometheus.staging.yml
├── docker-compose.staging.yml
├── docker-compose.production.yml
├── docker-compose.mcp-isolation.yml
├── .github/
│   ├── copilot-instructions.md      # THIS FILE
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-staging.yml
│       └── deploy-production.yml
├── docs/
│   ├── SYSTEM_PROMPT_TECHNICAL_EXCELLENCE.md
│   ├── SECURE_CREDENTIALS_MCP_SYSTEM_PROMPT.md
│   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   └── README.md
└── vault/
    ├── linkedin_creds.enc
    ├── twitter_creds.enc
    ├── email_creds.enc
    └── github_creds.enc
```

---

## PART 8: COMMON TASKS & COMMANDS

### Add New Agent
```bash
# 1. Create agent file
touch agents/core/my_new_agent.py

# 2. Implement using BaseAgent pattern (see PART 4)

# 3. Create tests
touch tests/test_agents/test_my_new_agent.py

# 4. Add to __init__.py
# agents/__init__.py
from agents.core.my_new_agent import MyNewAgent

# 5. Register in Maestro
# agents/core/maestro_agent.py
self.agents['my_new_agent'] = MyNewAgent()

# 6. Run tests
pytest tests/test_agents/test_my_new_agent.py -v

# 7. Commit
git add agents/ tests/
git commit -m "feat: Add MyNewAgent with full test coverage"
```

### Add MCP Server (Isolated)
```bash
# 1. Create MCP container in docker-compose.mcp-isolation.yml
# (Add under appropriate TIER with isolated network)

# 2. Create credential file
touch vault/service_creds.enc

# 3. Encrypt credentials
python agents/security/credential_manager.py encrypt vault/service_creds.enc

# 4. Update MCPRouter
# agents/mcp/mcp_router.py
MCP_NETWORKS['service_mcp'] = {
    'endpoint': 'http://172.25.0.15:9006',
    'allowed_agents': ['RelevantAgent'],
    'credentials_scope': 'enterprise'  # or 'personal'
}

# 5. Test isolation
docker-compose -f docker-compose.mcp-isolation.yml up -d
docker exec agent_mcp_1 curl http://172.26.0.10:8000  # Should timeout
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_agents/test_classifier_agent.py -v

# With coverage
pytest tests/ -v --cov=agents --cov-report=html

# Integration tests only
pytest tests/test_integration_full_system.py -v -s
```

### Deploy to Staging
```bash
# 1. Verify tests pass locally
pytest tests/ -v

# 2. Verify code quality
black agents/ --check
mypy agents/

# 3. Push to main
git push origin main

# 4. GitHub Actions automatically:
#    - Runs all tests
#    - Deploys to staging
#    - Runs smoke tests
#    - Notifies on success/failure
```

---

## PART 9: DEBUGGING & TROUBLESHOOTING

### Common Issues

**Issue: Tests fail with "CredentialNotFoundError"**
```bash
# Solution: Ensure credentials encrypted in vault/
python -c "from agents.security.credential_manager import CredentialManager; \
  CredentialManager().encrypt_from_csv('passwords.csv')"
```

**Issue: MCP connection timeout**
```bash
# Solution: Verify MCP container is running and accessible
docker-compose -f docker-compose.mcp-isolation.yml ps
docker logs linkedin_mcp

# Verify network isolation
docker exec linkedin_mcp curl http://172.25.0.10:8000/health
```

**Issue: Agent cannot access credentials**
```bash
# Solution: Check credential scope assignment
# agents/mcp/mcp_router.py - verify allowed_agents list
# Make sure agent is in correct tier (enterprise vs personal)
```

**Issue: Circular imports or missing modules**
```bash
# Solution: Check __init__.py files are present
# Ensure all imports are relative
# from agents.core.classifier_agent import ClassifierAgent  # ✅
# from classifier_agent import ClassifierAgent              # ❌
```

---

## PART 10: PRODUCTION CHECKLIST

Before deploying to production:

- [ ] All 138+ tests passing
- [ ] Code coverage ≥ 80%
- [ ] No linting errors (pylint, mypy, black)
- [ ] Security scan passed (bandit, safety)
- [ ] All credentials encrypted in vault/
- [ ] Docker images built and tagged
- [ ] Staging deployment validated
- [ ] Monitoring dashboards configured
- [ ] Alerts configured with thresholds
- [ ] Rollback procedure tested
- [ ] Documentation updated
- [ ] Team trained on system

---

## SUMMARY: KEY PRINCIPLES

1. **Agents are autonomous** - They execute independently, driven by tickets/schedules
2. **MCPs are isolated** - 4-tier architecture prevents cross-contamination
3. **Credentials are encrypted** - Never plaintext, always audited
4. **Code is tested** - 138+ tests, ≥80% coverage mandatory
5. **Deployment is automated** - CI/CD handles all validation + deployment
6. **Monitoring is real-time** - Prometheus + Grafana expose all metrics
7. **Failure is graceful** - Errors logged, escalated, recovered automatically
8. **Everything is documented** - Code, tests, architecture, operations

---

## GETTING HELP

- **Architecture questions**: See PART 1
- **Security questions**: See PART 2
- **Code standards**: See PART 3
- **Agent implementation**: See PART 4
- **Testing**: See PART 5
- **Deployment**: See PART 6
- **Troubleshooting**: See PART 9

---

**Status**: PRODUCTION READY  
**Last Updated**: 2025-11-02  
**Version**: v1.0.0  
**Maintained By**: TwisterLab Team

🚀 **Happy coding! The agents are ready to work.**
