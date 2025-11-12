# TwisterLab Autonomous Agents Registry
## Real Production Agents (agents/real/)

### Overview
7 production-ready autonomous agents for IT helpdesk automation

---

## 1. RealMonitoringAgent
**File**: `agents/real/real_monitoring_agent.py`  
**MCP Tool**: `monitor_system_health`  
**Purpose**: System health monitoring and alerting

**Capabilities**:
- CPU usage monitoring (psutil)
- RAM usage tracking
- Disk space monitoring
- Docker service health checks
- Real-time metrics collection

**Usage**:
```python
from agents.real.real_monitoring_agent import RealMonitoringAgent

agent = RealMonitoringAgent()
result = await agent.execute({"detailed": True})
# Returns: CPU%, RAM usage, disk space, Docker services status
```

**MCP Call**:
```
@mcp monitor_system_health
```

---

## 2. RealBackupAgent
**File**: `agents/real/real_backup_agent.py`  
**MCP Tool**: `create_backup`  
**Purpose**: Automated backups with disaster recovery

**Capabilities**:
- PostgreSQL database backups
- Redis cache backups
- Configuration file backups
- Incremental and full backups
- Backup rotation and retention

**Usage**:
```python
from agents.real.real_backup_agent import RealBackupAgent

agent = RealBackupAgent()
result = await agent.execute({"backup_type": "full"})
# Returns: backup location, size, timestamp
```

**MCP Call**:
```
@mcp create_backup
```

---

## 3. RealSyncAgent
**File**: `agents/real/real_sync_agent.py`  
**MCP Tool**: `sync_cache`  
**Purpose**: Cache and database synchronization

**Capabilities**:
- Redis ↔ PostgreSQL sync
- Cache invalidation
- Data consistency checks
- Conflict resolution
- Performance optimization

**Usage**:
```python
from agents.real.real_sync_agent import RealSyncAgent

agent = RealSyncAgent()
result = await agent.execute({"force": False})
# Returns: synced keys count, duration
```

**MCP Call**:
```
@mcp sync_cache
```

---

## 4. RealClassifierAgent
**File**: `agents/real/real_classifier_agent.py`  
**MCP Tool**: `classify_ticket`  
**Purpose**: AI-powered ticket classification

**Capabilities**:
- LLM-based classification (Ollama llama3.2:1b)
- 5 categories: network, hardware, software, account, email
- Confidence scoring
- Priority assignment
- Auto-escalation triggers

**Usage**:
```python
from agents.real.real_classifier_agent import RealClassifierAgent

agent = RealClassifierAgent()
result = await agent.execute({
    "ticket_text": "WiFi keeps dropping connection"
})
# Returns: category="network", confidence=0.92, priority="high"
```

**MCP Call**:
```
@mcp classify_ticket "WiFi keeps dropping connection"
```

---

## 5. RealResolverAgent
**File**: `agents/real/real_resolver_agent.py`  
**MCP Tool**: `resolve_ticket`  
**Purpose**: SOP-based automatic ticket resolution

**Capabilities**:
- Standard Operating Procedures execution
- Network troubleshooting (ping, traceroute, DNS)
- Hardware diagnostics
- Software reinstallation guides
- Account unlocking
- Email configuration fixes

**Usage**:
```python
from agents.real.real_resolver_agent import RealResolverAgent

agent = RealResolverAgent()
result = await agent.execute({
    "category": "network",
    "description": "No internet access"
})
# Returns: resolution_steps[], estimated_time, success_rate
```

**MCP Call**:
```
@mcp resolve_ticket --category=network --description="No internet"
```

---

## 6. RealDesktopCommanderAgent
**File**: `agents/real/real_desktop_commander_agent.py`  
**MCP Tool**: `execute_desktop_command`  
**Purpose**: Remote system command execution

**Capabilities**:
- PowerShell command execution (Windows)
- Bash command execution (Linux)
- SSH remote execution
- Command whitelisting (security)
- Output capture and logging
- Timeout management

**Usage**:
```python
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent

agent = RealDesktopCommanderAgent()
result = await agent.execute({
    "command": "Get-Service Docker",
    "target_host": "192.168.0.30",
    "timeout": 30
})
# Returns: output, exit_code, execution_time
```

**MCP Call**:
```
@mcp execute_desktop_command --command="systemctl status docker" --target=192.168.0.30
```

**⚠️ Security**: Commands are whitelisted, validated, and audited

---

## 7. RealMaestroAgent
**File**: `agents/real/real_maestro_agent.py`  
**MCP Tool**: N/A (internal orchestration)  
**Purpose**: Workflow orchestration and load balancing

**Capabilities**:
- Multi-agent workflow coordination
- Load balancing across agents
- State persistence (Redis)
- Error recovery
- Performance optimization
- Agent health monitoring

**Usage**:
```python
from agents.real.real_maestro_agent import RealMaestroAgent

agent = RealMaestroAgent()
result = await agent.execute({
    "workflow": "ticket_processing",
    "ticket_id": 123
})
# Returns: workflow_status, agents_used[], total_time
```

**Orchestration Example**:
```
1. Ticket arrives → RealClassifierAgent (classify)
2. Category identified → RealResolverAgent (resolve)
3. Requires system access → RealDesktopCommanderAgent (execute)
4. Monitor progress → RealMonitoringAgent (check)
5. Complete → RealBackupAgent (backup state)
```

---

## Base Class: TwisterAgent

**File**: `agents/base.py`  
**Lines**: 565

All 7 real agents inherit from `TwisterAgent` base class:

```python
from agents.base import TwisterAgent

class RealMyAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            display_name="My Agent",
            description="What it does",
            role="assistant",
            model="llama-3.2",
            temperature=0.7,
            tools=[...]
        )
    
    async def execute(self, context: Dict) -> Dict:
        # Implementation
        pass
```

**Multi-Framework Export**:
- `agent.to_schema("microsoft")` → Microsoft Agent Framework
- `agent.to_schema("langchain")` → LangChain
- `agent.to_schema("openai")` → OpenAI Assistants API
- `agent.to_schema("semantic-kernel")` → Semantic Kernel

---

## MCP Server Integration

**File**: `agents/mcp/mcp_server_continue_sync.py`  
**Version**: 2.0.0  
**Protocol**: MCP 2024-11-05  
**Transport**: stdio (JSON-RPC 2.0)

**Endpoints** (API: http://192.168.0.30:8000):
```
POST /v1/mcp/tools/list_autonomous_agents
POST /v1/mcp/tools/monitor_system_health
POST /v1/mcp/tools/create_backup
POST /v1/mcp/tools/sync_cache
POST /v1/mcp/tools/classify_ticket
POST /v1/mcp/tools/resolve_ticket
POST /v1/mcp/tools/execute_desktop_command
```

**Modes**:
- **REAL**: Calls actual TwisterLab API (requires httpx)
- **MOCK**: Fallback responses (offline mode)

---

## Quick Reference

| Agent | File | MCP Tool | Primary Function |
|-------|------|----------|------------------|
| RealMonitoringAgent | real_monitoring_agent.py | monitor_system_health | System health checks |
| RealBackupAgent | real_backup_agent.py | create_backup | Disaster recovery |
| RealSyncAgent | real_sync_agent.py | sync_cache | Cache synchronization |
| RealClassifierAgent | real_classifier_agent.py | classify_ticket | AI ticket classification |
| RealResolverAgent | real_resolver_agent.py | resolve_ticket | SOP execution |
| RealDesktopCommanderAgent | real_desktop_commander_agent.py | execute_desktop_command | Remote commands |
| RealMaestroAgent | real_maestro_agent.py | (internal) | Workflow orchestration |

---

## Dependencies

- **Python**: 3.12+
- **AsyncIO**: All agents use async/await
- **Database**: PostgreSQL 16, Redis 7
- **LLM**: Ollama (llama3.2:1b, llama3:latest)
- **Infrastructure**: Docker Swarm
- **Monitoring**: Prometheus + Grafana

---

## Testing

```powershell
# Test individual agent
python -m pytest tests/test_monitoring_agent.py -v

# Test all real agents
python -m pytest tests/test_integration_real_agents.py -v

# Test MCP server
python test_mcp_list_agents.py
```

---

## Documentation

- **Setup Guide**: `.continue/SETUP_GUIDE_v1.0.1.md`
- **MCP Upgrade**: `.continue/MCP_UPGRADE_v2.0.0.md`
- **API Docs**: `API_DOCUMENTATION.md`
- **Copilot Instructions**: `copilot-instructions.md`
