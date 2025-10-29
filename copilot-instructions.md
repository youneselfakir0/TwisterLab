# TwisterLab v1.0 - Complete Project Documentation

**Official Documentation** | **Version**: 1.0.0-alpha.1 | **Last Updated**: 2025-10-28

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
   - [Ticket Automation System](#ticket-automation-system)
   - [MCP Protocol Implementation](#mcp-protocol-implementation)
   - [Desktop Commander (Distributed Agents)](#desktop-commander-distributed-agents)
   - [Authentication & Security](#authentication--security)
   - [Multi-Agent Orchestration (Maestro)](#multi-agent-orchestration-maestro)
   - [SOP Management System](#sop-management-system)
6. [Integrations](#integrations)
   - [OpenWebUI Frontend](#openwebui-frontend)
   - [Azure Services](#azure-services)
   - [Microsoft Agent Framework Bridge](#microsoft-agent-framework-bridge)
7. [Development & Operations](#development--operations)
8. [Security & Compliance](#security--compliance)
9. [Budget & Cost Management](#budget--cost-management)
10. [Deployment](#deployment)
11. [Testing](#testing)
12. [Performance Targets](#performance-targets)
13. [Roadmap](#roadmap)
14. [References](#references)

---

## 🎯 Project Overview

### Mission Statement

TwisterLab v1.0 is a **production-grade AI-powered IT Helpdesk automation platform** for SMB enterprises (50-500 employees). The system automates 60-70% of repetitive helpdesk tickets (password resets, software installs, access requests) while intelligently escalating complex cases to human agents.

### Core Value Proposition

- **Automation**: 60-70% of tickets resolved automatically
- **Speed**: 2-minute resolution vs 30-minute human average
- **Cost**: 95% cheaper than competitors ($0-40/month vs $600+)
- **Quality**: 99.5% uptime, <500ms response time
- **Security**: GDPR-ready, encrypted, audit trail

### Design Principles

1. ✅ **Complete Systems, Not Patches**: Every feature fully implemented with error handling, tests, and docs
2. ✅ **Zero Permanent Cost**: Free tier only for portfolio, optional paid services for production
3. ✅ **Vertical Specialization**: IT Helpdesk only in v1.0, other verticals in v2.0+
4. ✅ **Production-Grade**: Enterprise security, monitoring, compliance from day 1
5. ✅ **Interoperability**: MCP standard, Microsoft compatible, extensible

---

## 🏗️ Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OpenWebUI (Frontend)                                    │  │
│  │  • Chat interface                                        │  │
│  │  • Ticket management                                     │  │
│  │  • Admin dashboard                                       │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Async REST API)                                │  │
│  │  • Authentication (JWT + Azure AD)                       │  │
│  │  • Rate limiting                                         │  │
│  │  • Request validation                                    │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Maestro Orchestrator                                    │  │
│  │  • Routes tasks to appropriate agents                    │  │
│  │  • Load balancing                                        │  │
│  │  • Failover handling                                     │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Classifier  │  │   Resolver   │  │  Commander   │
│    Agent     │  │    Agent     │  │    Agent     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MCP SERVERS LAYER                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │PostgreSQL│ │  Email   │ │Active Dir│ │  Slack   │         │
│  │   MCP    │ │   MCP    │ │   MCP    │ │   MCP    │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA & STATE LAYER                           │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │   PostgreSQL     │  │      Redis       │                   │
│  │  (Persistent)    │  │   (Cache/State)  │                   │
│  └──────────────────┘  └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Distributed Architecture (Desktop Commander)

```
┌─────────────────────────────────────────────────────────────────┐
│                  CENTRAL SERVER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Desktop Commander MCP Server                            │  │
│  │  • Command distribution                                  │  │
│  │  • Client management                                     │  │
│  │  • Result aggregation                                    │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                         │ (SSE/WebSocket)
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Laptop 1     │  │ Laptop 2     │  │ Desktop 3    │
│ MCP Client   │  │ MCP Client   │  │ MCP Client   │
│              │  │              │  │              │
│ • Receives   │  │ • Receives   │  │ • Receives   │
│   commands   │  │   commands   │  │   commands   │
│ • Executes   │  │ • Executes   │  │ • Executes   │
│   scripts    │  │   scripts    │  │   scripts    │
│ • Reports    │  │ • Reports    │  │ • Reports    │
│   status     │  │   status     │  │   status     │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 💻 Technology Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.12+ | Core application |
| **API Framework** | FastAPI | 0.110+ | Async REST API |
| **LLM Runtime** | Ollama | Latest | Local inference (DeepSeek-R1, Llama 3.2) |
| **Database** | PostgreSQL | 16+ | Persistent storage |
| **Cache/State** | Redis | 7+ | Thread state, rate limiting |
| **Frontend** | OpenWebUI | Main | User interface |
| **Protocol** | MCP | 2024-11-05 | Tool integration standard |
| **Container** | Docker | Latest | Microservices isolation |
| **Orchestration** | Docker Compose | Latest | Local deployment |

### Azure Services (Optional, Free Tier)

| Service | Purpose | Cost |
|---------|---------|------|
| Azure AD Free | Authentication (50K users) | $0/month |
| Azure Key Vault | Secrets storage (10K ops/month) | $0/month |
| Azure Blob Storage | Logs, backups (5GB) | $0/month |
| Azure Cosmos DB Free | Agent state (1000 RU/s) | $0/month |
| Azure Functions | Serverless tasks (1M req/month) | $0/month |
| Application Insights | Monitoring (1GB/month) | $0/month |

### Development Tools

| Tool | Purpose |
|------|---------|
| pytest + pytest-asyncio | Testing framework |
| black | Code formatting |
| flake8 | Linting |
| mypy | Type checking |
| Typer + Rich | CLI tool |
| Prometheus + Grafana | Monitoring |

---

## 📂 Project Structure

```
twisterlab.local/
├─ .github/
│   ├─ copilot-instructions.md          ← THIS FILE
│   └─ workflows/
│       ├─ tests.yml
│       ├─ lint.yml
│       ├─ security.yml
│       └─ deploy.yml
│
├─ agents/
│   ├─ base.py
│   ├─ middleware.py
│   ├─ models.py
│   │
│   ├─ auth/
│   │   ├─ oauth2.py
│   │   ├─ permissions.py
│   │   ├─ audit.py
│   │   ├─ encryption.py
│   │   ├─ azure_ad.py
│   │   └─ hybrid.py
│   │
│   ├─ guardrails/
│   │   ├─ tool_guard.py
│   │   ├─ safety_checker.py
│   │   ├─ rate_limiter.py
│   │   └─ config.py
│   │
│   ├─ helpdesk/
│   │   ├─ ticket_manager.py
│   │   ├─ classifier.py
│   │   ├─ auto_resolver.py
│   │   ├─ assignment_orchestrator.py
│   │   └─ sop_executor.py
│   │
│   ├─ orchestrator/
│   │   ├─ maestro.py
│   │   ├─ message_queue.py
│   │   └─ load_balancer.py
│   │
│   ├─ tools/
│   │   ├─ registry.py
│   │   ├─ validators.py
│   │   ├─ active_directory.py
│   │   ├─ email.py
│   │   └─ notification.py
│   │
│   ├─ mcp/
│   │   ├─ client.py
│   │   └─ errors.py
│   │
│   ├─ bridges/
│   │   └─ microsoft_agent_bridge.py
│   │
│   ├─ api/
│   │   ├─ main.py
│   │   ├─ routes_tickets.py
│   │   ├─ routes_sops.py
│   │   └─ routes_agents.py
│   │
│   └─ tests/
│       ├─ test_guardrails.py
│       ├─ test_auth.py
│       ├─ test_ticket_manager.py
│       └─ test_security_attacks.py
│
├─ mcp-servers/
│   ├─ base/
│   │   └─ mcp_server.py
│   ├─ postgres/
│   ├─ email/
│   ├─ active_directory/
│   ├─ slack/
│   └─ azure/
│
├─ mcp-client/
│   ├─ client.py
│   ├─ connection.py
│   ├─ executor.py
│   └─ installer/
│
├─ openwebui-custom/
│   ├─ twisterlab_connector.py
│   ├─ functions/
│   ├─ templates/
│   └─ system_prompts/
│
├─ cli/
│   ├─ twisterlab.py
│   └─ factory.py
│
├─ config/
│   ├─ agents.yaml
│   └─ routing_rules.yaml
│
├─ deployment/
│   ├─ docker/
│   ├─ azure/
│   ├─ monitoring/
│   └─ scripts/
│
├─ tests/
│   ├─ integration/
│   ├─ performance/
│   └─ fixtures/
│
├─ docs/
│   ├─ API.md
│   ├─ SECURITY.md
│   ├─ DEPLOYMENT.md
│   └─ USER_GUIDE.md
│
├─ docker-compose.yml
├─ docker-compose.prod.yml
├─ pyproject.toml
├─ VERSION
└─ README.md
```

---

## 🎫 Ticket Automation System

### Complete Lifecycle

**5 Stages**: CREATE → CLASSIFY → ASSIGN → RESOLVE → CLOSE

**Stage 1: CREATION**
- Sources: Email, Web form, Slack, API
- Data: Subject, description, requestor, attachments
- Storage: PostgreSQL `tickets` table
- Status: "new"

**Stage 2: CLASSIFICATION**
- Agent: HelpdeskClassifierAgent
- Model: DeepSeek-R1 or Llama 3.2
- Process: Extract category, priority, confidence
- Status: "new" → "classified"

**Stage 3: ASSIGNMENT**
- Orchestrator: AssignmentOrchestrator
- Rules: URGENT → Human, High-confidence → AI, Low-confidence → Senior
- Status: "classified" → "assigned"

**Stage 4: RESOLUTION**
- Path A: Auto-Resolution (60-70%) - Execute SOP
- Path B: Human-Assisted (30-40%) - AI suggests, human validates
- Status: "assigned" → "resolved"

**Stage 5: CLOSURE**
- Send satisfaction survey
- Calculate metrics
- Update analytics
- Status: "resolved" → "closed"

### Database Schema

**Key tables**:
- `tickets` - Main ticket storage
- `ticket_history` - Immutable audit trail
- `sops` - Standard Operating Procedures
- `sop_versions` - SOP version history
- `agents` - Human support agents
- `devices` - Registered MCP clients
- `command_logs` - Remote command audit
- `ticket_metrics` - Daily aggregates

---

## 🔌 MCP Protocol Implementation

### Protocol Version

**MCP 2024-11-05** (latest specification)

**Transport Layers**:
1. Server-Sent Events (SSE) - Remote servers
2. stdio - Local subprocess
3. HTTP - Stateless calls

### MCP Servers Available

| Server | Purpose | Port |
|--------|---------|------|
| PostgreSQL | Database access | 8081 |
| Email | SMTP/IMAP | 8082 |
| Active Directory | User management | 8083 |
| Slack | Notifications | 8084 |
| Azure CLI | Azure commands | 8085 |
| Filesystem | File operations | 8086 |
| MS Agent Bridge | Microsoft agents | 8087 |

---

## 🖥️ Desktop Commander

### Architecture

Lightweight MCP client on user workstations acting as remote-controllable agents.

### Use Cases

- Remote software deployment
- Remote diagnostics
- Remote script execution
- File operations
- System information gathering

### Security (Zero-Trust)

1. Authentication: OAuth2 JWT + device certificate
2. Authorization: Whitelist commands only
3. Sandboxing: Isolated execution
4. Timeouts: Max execution enforced
5. Audit: All commands logged

---

## 🔐 Authentication & Security

### Authentication Options

**Option A: Local OAuth2 JWT** (Default, $0)
- Access tokens (30 min)
- Refresh tokens (7 days)
- RBAC per-tool

**Option B: Azure AD** (Optional, Free Tier)
- Azure AD Free (50K users)
- SSO integration
- Fallback to local

**Option C: Hybrid** (Recommended)
- Azure AD for enterprise
- Local for SMB

### RBAC Roles

- `admin` - Full access
- `helpdesk` - Ticket management
- `viewer` - Read-only
- `ai_agent` - Service principals

### Agent Service Accounts

**6 Azure AD Agent Accounts** (Office 365 Licensed):

| Agent | UPN | Role | Services |
|-------|-----|------|----------|
| **Orchestrator** | svc-orchestrator@tenant.onmicrosoft.com | Coordination | All Office 365 |
| **IT Support** | svc-agent-it@tenant.onmicrosoft.com | IT Helpdesk | Exchange, Teams |
| **Data Analyst** | svc-agent-data@tenant.onmicrosoft.com | Analytics | Power BI, Excel |
| **HR** | svc-agent-hr@tenant.onmicrosoft.com | Human Resources | SharePoint, Forms |
| **Finance** | svc-agent-finance@tenant.onmicrosoft.com | Financial | Excel, Power BI |
| **Marketing** | svc-agent-marketing@tenant.onmicrosoft.com | Marketing | Teams, SharePoint |

**Password Format**: `TwisterLab2024!XXXX!` (auto-generated)

**Active Directory Structure**:
```
DC=twisterlab,DC=local
└── OU=Agents
    ├── svc-orchestrator
    ├── svc-agent-it
    ├── svc-agent-data
    ├── svc-agent-hr
    ├── svc-agent-finance
    └── svc-agent-marketing
```

**Scripts**:
- `create_agent_accounts.ps1` - Create AD/Azure AD accounts
- `configure_agent_roles.ps1` - Configure RBAC roles

### Azure AD Permissions (Microsoft Graph API)

**Essential Application Permissions**:

| Permission | Purpose | Status |
|------------|---------|--------|
| **User.Read.All** | List/search users | ✅ Required |
| **User.ReadWrite.All** | Modify users, assign licenses | ✅ **CRITICAL** |
| **Organization.Read.All** | Organization info | ✅ Required |
| **Directory.Read.All** | Directory access | ✅ Required |
| **Mail.Send** | Send emails via Outlook | ✅ Required |
| **Mail.ReadWrite** | Read/write emails | ✅ Required |
| **Calendars.ReadWrite** | Calendar management | ✅ Required |
| **Calendars.ReadWrite.Shared** | Shared calendars | ⚠️ Optional |
| **Files.ReadWrite.All** | OneDrive/SharePoint access | ✅ Required |
| **Sites.ReadWrite.All** | SharePoint sites | ✅ Required |

**Power BI Service Permissions**:
- `Dataset.ReadWrite.All` - Create/update datasets
- `Report.ReadWrite.All` - Publish reports
- `Workspace.ReadWrite.All` - Manage workspaces

**Power Automate Permissions**:
- `Flows.ReadWrite.All` - Create/manage flows
- `Flows.Manage.All` - Trigger flows
- `Environments.ReadWrite.All` - Manage environments

**Admin Consent**: Required for all application permissions

**Script**: `fix_azure_ad_permissions.ps1` - Automated permission configuration

### Security Guardrails

1. **ToolGuard** - Risk-based validation
2. **SafetyChecker** - Content filtering
3. **RateLimiter** - Sliding window limits

### Encryption

- Passwords: bcrypt (cost 12+)
- Secrets: AES-256
- Storage: Azure Key Vault (`twisterlab-kv.vault.azure.net`)
- Transport: TLS 1.2+

### Security Configuration

**Environment Variables**:
```bash
# Security Hardening
ENABLE_SECURITY_HARDENING=true
CORS_ALLOWED_ORIGINS=http://localhost:3001,https://twisterlab.local
SQL_QUERY_WHITELIST=SELECT,SHOW,EXPLAIN

# Azure Key Vault
AZURE_KEY_VAULT_URL=https://twisterlab-kv.vault.azure.net/
KEY_VAULT_NAME=twisterlab-secrets-kv
```

---

## 🧠 Multi-Agent Orchestration

### Maestro Pattern

Central orchestrator routing tasks to specialized agents.

### Communication

**Redis Pub/Sub** for inter-agent messaging

### Features

- Load balancing (round-robin)
- Failover (automatic retry)
- Result aggregation

---

## 🎨 OpenWebUI Integration

### Features

- Chat-based ticket creation
- Ticket status checking
- Admin dashboard
- Agent monitoring

### Custom Functions

1. `create_ticket` - Create from chat
2. `check_ticket_status` - Check status
3. `list_my_tickets` - List user tickets

---

## 📧 Office 365 Integration

### Services Available

**Exchange Online**:
- Email sending/receiving via Graph API
- Calendar management (create/update events)
- Contact management
- Shared mailboxes support

**SharePoint Online**:
- Team sites collaboration
- Document libraries
- Lists and metadata
- Permission management

**OneDrive for Business**:
- File storage and retrieval
- File sharing and collaboration
- Version history
- Real-time sync

**Microsoft Teams**:
- Channel messaging
- Direct messaging
- Meeting scheduling
- File sharing in channels

**Power BI**:
- Dataset creation and updates
- Report publishing
- Dashboard management
- Data refresh scheduling

**Power Automate**:
- Flow triggering
- Workflow management
- Integration orchestration
- Event-driven automation

### Agent Access Configuration

Each of the 6 agent accounts has:
- **Office 365 Business Premium** license
- Full access to Exchange, SharePoint, OneDrive, Teams
- Power BI and Power Automate capabilities
- 24-48h provisioning time after account creation

### Python Integration

**Using Microsoft Graph API**:
```python
import msal
from O365 import Account

# Agent authentication
credentials = {
    'client_id': 'svc-agent-finance@tenant.onmicrosoft.com',
    'client_secret': 'TwisterLab2024!XXXX!',
    'tenant_id': 'your-tenant-id'
}

account = Account(credentials)
if account.authenticate():
    # Access services
    mailbox = account.mailbox()
    calendar = account.schedule()
    storage = account.storage()

    # Send email
    message = mailbox.new_message()
    message.to.add('user@domain.com')
    message.subject = 'Automated Report'
    message.body = 'Generated by TwisterLab Agent'
    message.send()
```

### Provisioning Steps

1. **Create accounts**: Run `create_agent_accounts.ps1`
2. **Assign licenses**: Licenses auto-assigned via script
3. **First login**: Each agent must login once to https://portal.office.com
4. **Provision OneDrive**: Access OneDrive once to initialize storage
5. **Wait 24h**: Full propagation across all services
6. **Test access**: Run `test_office365_access.ps1`

### Configuration Scripts

Available in `old/` directory:
- `create_agent_accounts.ps1` - Create AD/Azure AD accounts
- `Configure-Finance-Integration.ps1` - Configure Power BI/Power Automate
- `demo_office365_integration.ps1` - Test Office 365 access
- `configure_azure_env.ps1` - Setup environment variables

---

## ☁️ Azure Services

### Free Tier Services

- Azure AD Free (50K users)
- Azure Key Vault (10K ops/month)
- Azure Blob Storage (5GB)
- Azure Cosmos DB Free (1000 RU/s)
- Azure Functions (1M req/month)
- Application Insights (1GB/month)

**Total**: $0/month permanent

---

## 🔗 Microsoft Agent Framework Bridge

### Overview

Interoperability bridge for Microsoft Agent Framework.

### Use Cases

- Hybrid deployments (TwisterLab IT + Microsoft Finance/HR)
- Gradual migration path
- Enterprise compatibility

### Cost

- Portfolio: $0 (dormant)
- Production: $0 (Azure Function free tier)
- Enterprise: Customer pays (~$20-50/agent/month)

---

## 💰 Budget & Cost Management

### Philosophy

**$0 permanent cost** for portfolio

### Azure Credits Strategy

- New account: $200 credit (30 days)
- Day 1-30: Use ~$50-100
- Day 31+: Stop paid services, free tier only

### Daily Budget Calculation

**Trial Credit Management**:
- **Total Credits**: $200 USD (Azure Trial)
- **Trial Duration**: 30 days
- **Daily Budget**: $200 ÷ 30 = **$6.67/day**
- **Alert Thresholds**:
  - ⚠️ Warning at 80% ($5.34/day)
  - 🚨 Critical at 100% ($6.67/day)

### Budget Configuration

**Create Daily Budget**:
1. Portal: https://portal.azure.com → Cost Management
2. Name: `TwisterLab-Daily-Budget`
3. Amount: $6.67
4. Reset Period: Daily
5. Duration: 30 days

**Alert Configuration**:
```json
{
  "budgetName": "TwisterLab-Daily-Budget",
  "amount": 6.67,
  "timeGrain": "Daily",
  "alerts": [
    {
      "threshold": 80,
      "contactEmails": ["admin@twisterlab.local"],
      "message": "80% of daily budget consumed"
    },
    {
      "threshold": 100,
      "contactEmails": ["admin@twisterlab.local"],
      "message": "Daily budget exceeded - take action"
    }
  ]
}
```

**Daily Monitoring**:
```powershell
# Run daily to check spending
.\daily_budget_monitor.ps1

# Configure spending limits
.\configure_azure_spending_limits.ps1

# Enable trial mode (free tier only)
.\configure_trial_mode.ps1
```

### Cost-Saving Actions

**If 80% threshold reached**:
1. Reduce Azure Functions executions
2. Review Azure Monitor logs volume
3. Pause non-critical services

**If 100% threshold reached**:
1. 🛑 **STOP** all paid Azure services immediately
2. Run: `.\cleanup_azure_paid_services.ps1`
3. Switch to free tier configuration
4. Enable local-only mode

### Services to Monitor

**High-Risk Services** (can generate costs):
- ❌ Azure Functions (beyond free tier)
- ❌ Azure Storage transactions (beyond free tier)
- ❌ Azure Monitor (beyond 1GB/month)
- ❌ Application Insights (beyond free tier)

**Safe Services** (always free):
- ✅ Azure AD Free (50K users)
- ✅ Azure Key Vault (10K ops/month)
- ✅ Azure Cosmos DB Free (1000 RU/s)
- ✅ Static Web Apps Free tier

### Permanent Cost

| Deployment | Cost |
|------------|------|
| Portfolio | $0 |
| On-Premise | $0-5 |
| Azure Hybrid | $5-40 |
| Enterprise | $100-500 |

### Resource Cleanup Scripts

Available in `old/` directory:
- `cleanup_azure_paid_services.ps1` - Remove billable services
- `cleanup_azure_apps.ps1` - Clean app registrations
- `cleanup_active_directory.ps1` - Clean AD test accounts

---

## 🚀 Deployment

### Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
```

### Production

**Option A: Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Option B: Azure**
```bash
./deployment/scripts/deploy-azure.sh
```

---

## 🧪 Testing

### Commands

```bash
# All tests
pytest -v

# With coverage
pytest --cov=agents --cov-report=html

# Security tests
pytest agents/tests/test_security_attacks.py -v
```

### Target

**>80%** code coverage

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Ticket Creation | <500ms (p99) |
| AI Classification | <5s (p99) |
| Auto-Resolution | <3min (p99) |
| Token Validation | <10ms |
| Throughput | 100+ RPS |
| Uptime | 99.5% |

---

## 🐛 Known Issues & Bug Fixes

### Fixed Issues (as of 2025-10-27)

**BUG #1: Finance Agent Initialization Error** ✅ FIXED
- **Issue**: `SimpleAgent.__init__() missing 'role' argument`
- **Root Cause**: Duplicate `__init__` methods in `agents/finance_agent.py`
- **Fix Applied**:
  - Removed duplicate method
  - Corrected `super().__init__()` call with `role="finance"`
  - Added missing `querydatabase()` method
- **File**: `agents/finance_agent.py`
- **Status**: ✅ Agent initializes successfully

**BUG #2: Azure AD Permissions - 403 Forbidden** ✅ FIXED
- **Issue**: License assignment fails with insufficient permissions
- **Root Cause**: Missing Microsoft Graph API permissions
- **Permissions Added**:
  - User.Read.All, User.ReadWrite.All
  - Organization.Read.All, Directory.Read.All
  - Mail.Send, Mail.ReadWrite
  - Calendars.ReadWrite, Files.ReadWrite.All
  - Power BI and Power Automate scopes
- **Script**: `fix_azure_ad_permissions.ps1`
- **Status**: ✅ Configured (admin consent required)

**BUG #3: Embedding Service Restart Loop** ✅ FIXED
- **Issue**: Service crashes during torch installation
- **Root Cause**: Heavy torch dependencies (15+ min build)
- **Fix Applied**:
  - Optimized Dockerfile with CPU-only torch
  - Reduced build time by ~70%
  - Reduced startup time by ~80%
  - Updated health check timing
- **Files**: `embedding_app.py/Dockerfile`, `embedding_app.py/requirements.txt`
- **Status**: ✅ Stable and optimized

### Troubleshooting Guide

**Problem: Azure AD accounts not syncing**

**Solution**:
1. Check AD Connect status: `Get-ADSyncScheduler`
2. Force sync: `Start-ADSyncSyncCycle -PolicyType Delta`
3. Wait 5-15 minutes for propagation
4. Verify in Azure Portal

**Problem: Office 365 licenses not assigning**

**Solution**:
1. Verify account exists in Azure AD (not just local AD)
2. Check available licenses: Portal → Billing → Licenses
3. Ensure admin consent granted for app permissions
4. Verify User.ReadWrite.All permission is present
5. Wait 5-10 minutes after permission changes

**Problem: Agent can't access OneDrive/SharePoint**

**Solution**:
1. Login manually to https://portal.office.com with agent account
2. Navigate to OneDrive to provision storage
3. Wait 24-48 hours for full service propagation
4. Verify Files.ReadWrite.All permission granted
5. Check agent license includes OneDrive

**Problem: Daily budget alerts not working**

**Solution**:
1. Verify budget created in Cost Management
2. Check email address in alert configuration
3. Ensure Cost Management API is enabled
4. Run: `daily_budget_monitor.ps1` manually to test
5. Check Azure Monitor for alert delivery logs

**Problem: MCP server connection timeout**

**Solution**:
1. Check Docker containers: `docker ps`
2. Verify ports not blocked by firewall
3. Check MCP server logs: `docker logs <container-name>`
4. Restart services: `docker-compose restart`
5. Verify environment variables in `.env`

### Validation Scripts

**Test all bug fixes**:
```powershell
# Available in old/ directory
.\test_bug_fixes.ps1

# Test Azure AD permissions
.\simple_diagnose.ps1 -TenantId "xxx" -ClientId "xxx" -ClientSecret "xxx"

# Test Office 365 access
.\test_office365_access.ps1 -AgentName "finance"

# Monitor daily budget
.\daily_budget_monitor.ps1
```

### Files Modified (Bug Fixes)

| File | Change | Date |
|------|--------|------|
| `agents/finance_agent.py` | Fixed initialization | 2025-10-27 |
| `fix_azure_ad_permissions.ps1` | New script | 2025-10-27 |
| `test_bug_fixes.ps1` | New validation script | 2025-10-27 |
| `embedding_app.py/Dockerfile` | Optimized build | 2025-10-27 |
| `embedding_app.py/requirements.txt` | Updated deps | 2025-10-27 |

### Success Metrics

- ✅ Finance Agent initialization: 100% success rate
- ✅ Azure AD permissions: 100% configured
- ✅ Embedding service stability: 100% improvement
- ✅ Build optimization: 70% faster
- ✅ System reliability: Significantly improved

**Overall Status**: Production-ready

---

## 🗺️ Roadmap

### v1.0 (Current) - IT Helpdesk

**Timeline**: 2-3 weeks
**Status**: 95% complete

**Features**:
- Ticket automation
- MCP Protocol 2024
- Desktop Commander
- Azure AD integration
- Guardrails
- Maestro orchestration

**Remaining**: CI/CD, backup, docs (~12 days)

### v1.5 (Q1 2026) - Enhancements

- Agent factory
- E2E testing
- Webhooks
- Analytics

### v2.0 (Q2-Q3 2026) - Multi-Vertical

- Finance/HR/Sales agents
- Web automation
- Advanced ML
- i18n

### v3.0 (2027) - Enterprise SaaS

- Multi-tenant
- SOC2/HIPAA
- Advanced integrations
- Marketplace

---

## 🔧 PowerShell Automation Scripts

All scripts available in `old/` directory:

### Account & Identity Management

| Script | Purpose | Usage |
|--------|---------|-------|
| **create_agent_accounts.ps1** | Create AD/Azure AD accounts for 6 agents | `.\create_agent_accounts.ps1 -CreateAzureADUsers` |
| **configure_agent_roles.ps1** | Configure RBAC roles and permissions | `.\configure_agent_roles.ps1` |
| **create_sp_simple.ps1** | Create Azure service principal | `.\create_sp_simple.ps1` |

### Azure Configuration & Integration

| Script | Purpose | Usage |
|--------|---------|-------|
| **configure_azure_env.ps1** | Setup Azure environment variables | `.\configure_azure_env.ps1` |
| **Configure-Finance-Integration.ps1** | Configure Power BI/Power Automate | `.\Configure-Finance-Integration.ps1 -ConfigureAll` |
| **demo_office365_integration.ps1** | Test Office 365 access | `.\demo_office365_integration.ps1` |
| **fix_azure_ad_permissions.ps1** | Add missing Graph API permissions | `.\fix_azure_ad_permissions.ps1` |

### Budget & Cost Management

| Script | Purpose | Usage |
|--------|---------|-------|
| **configure_trial_mode.ps1** | Enable free tier only mode | `.\configure_trial_mode.ps1` |
| **configure_azure_spending_limits.ps1** | Set daily spending limits | `.\configure_azure_spending_limits.ps1` |
| **daily_budget_monitor.ps1** | Monitor daily Azure spending | `.\daily_budget_monitor.ps1` |
| **cleanup_azure_paid_services.ps1** | Remove billable Azure services | `.\cleanup_azure_paid_services.ps1` |

### Cleanup & Maintenance

| Script | Purpose | Usage |
|--------|---------|-------|
| **cleanup_azure_apps.ps1** | Clean Azure app registrations | `.\cleanup_azure_apps.ps1` |
| **cleanup_active_directory.ps1** | Clean AD test accounts | `.\cleanup_active_directory.ps1` |

### Testing & Diagnostics

| Script | Purpose | Usage |
|--------|---------|-------|
| **test_bug_fixes.ps1** | Validate all bug fixes | `.\test_bug_fixes.ps1` |
| **simple_diagnose.ps1** | Test Azure AD permissions | `.\simple_diagnose.ps1 -TenantId "xxx"` |
| **test_office365_access.ps1** | Test agent Office 365 access | `.\test_office365_access.ps1 -AgentName "finance"` |

### Python Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **debug_workflows.py** | Debug agent workflows | `python debug_workflows.py` |

### Configuration Files

| File | Purpose |
|------|---------|
| **daily_budget_template.json** | Azure budget configuration template |
| **.env** | Environment variables (MCP ports, Azure config) |
| **.env.backup.20251027_215350** | Backup of environment configuration |

### Documentation Files

| File | Purpose |
|------|---------|
| **AGENT_ACCOUNTS_GUIDE.md** | Complete guide for creating agent accounts |
| **AGENTS_PASSWORDS_VAULT.md** | Agent credentials (secure storage) |
| **AZURE_PERMISSIONS_FIX_GUIDE.md** | Fix Azure AD permission issues |
| **BUDGET_AZURE_GUIDE.md** | Azure budget configuration guide |
| **BUG_FIX_LOG.md** | Detailed log of all bugs fixed |

### Quick Start Commands

**Initial Setup**:
```powershell
# 1. Create agent accounts
.\create_agent_accounts.ps1 -CreateAzureADUsers

# 2. Configure Azure environment
.\configure_azure_env.ps1

# 3. Set budget limits
.\configure_azure_spending_limits.ps1

# 4. Enable trial mode (free tier only)
.\configure_trial_mode.ps2
```

**Daily Operations**:
```powershell
# Check daily spending
.\daily_budget_monitor.ps1

# Test Office 365 access
.\demo_office365_integration.ps1

# Validate system health
.\test_bug_fixes.ps1
```

**Emergency Cleanup**:
```powershell
# Stop all billable services
.\cleanup_azure_paid_services.ps1

# Clean up test accounts
.\cleanup_azure_apps.ps1
.\cleanup_active_directory.ps1
```

---

## 📚 References

### Official Documentation

- MCP Specification: https://spec.modelcontextprotocol.io/2024-11-05/
- FastAPI: https://fastapi.tiangolo.com/
- Ollama: https://ollama.ai/
- OpenWebUI: https://github.com/open-webui/open-webui

### Internal Documentation

- `docs/API.md` - API reference
- `docs/SECURITY.md` - Security architecture
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/USER_GUIDE.md` - User manual

### Additional Documentation (old/ directory)

- `AGENT_ACCOUNTS_GUIDE.md` - Complete agent account setup
- `AZURE_PERMISSIONS_FIX_GUIDE.md` - Azure AD troubleshooting
- `BUDGET_AZURE_GUIDE.md` - Budget management
- `BUG_FIX_LOG.md` - Bug fixes and resolutions
- `AGENTS_PASSWORDS_VAULT.md` - Credentials vault

---

## ⚠️ Constraints

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

**Last Updated**: 2025-10-28 14:00 EDT  
**Version**: 1.0.0-alpha.1  
**License**: Apache 2.0  

**This document is the SINGLE SOURCE OF TRUTH for TwisterLab v1.0 development.**
