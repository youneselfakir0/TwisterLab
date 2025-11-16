# =============================================================================
# CONTINUE IDE CUSTOM COMMANDS FOR TWISTERLAB ORCHESTRATION
# Configuration for .continue/config.json
# =============================================================================

# Custom Slash Commands to add to Continue IDE config.json

```json
{
  "slashCommands": [
    {
      "name": "dashboard",
      "description": "Show TwisterLab infrastructure dashboard",
      "prompt": "Using the twisterlab-dashboard MCP server, get the complete infrastructure status including API health, agents status, Prometheus targets, Traefik services, and Docker services. Format the output as a clean, organized dashboard with emojis and status indicators."
    },
    {
      "name": "monitor",
      "description": "Monitor specific TwisterLab component",
      "prompt": "Using the twisterlab-dashboard MCP server, check the status of {{{input}}}. Provide detailed health metrics, recent activity, and any issues. Use the appropriate MCP tool (check_api_health, get_agents_status, get_prometheus_targets, or get_traefik_services)."
    },
    {
      "name": "deploy",
      "description": "Deploy or update TwisterLab services",
      "prompt": "Guide me through deploying or updating TwisterLab service: {{{input}}}. Check current status via dashboard MCP, review docker-compose configuration, and provide deployment command. Ask for confirmation before executing."
    },
    {
      "name": "backup",
      "description": "Trigger backup operation via RealBackupAgent",
      "prompt": "Using the twisterlab-agents MCP server, execute a backup operation with type: {{{input}}} (full, incremental, or differential). Show backup status and verification results."
    },
    {
      "name": "health",
      "description": "Complete system health check",
      "prompt": "Perform a comprehensive health check of all TwisterLab components: 1) API health via dashboard MCP, 2) System metrics via RealMonitoringAgent, 3) Prometheus targets, 4) Traefik services, 5) Docker Swarm services. Summarize overall system status with recommendations."
    },
    {
      "name": "classify",
      "description": "Classify a ticket using RealClassifierAgent",
      "prompt": "Using the twisterlab-agents MCP server, classify the following ticket: {{{input}}}. Return the category, priority, assigned agent, and suggested SOP."
    },
    {
      "name": "resolve",
      "description": "Resolve a ticket using RealResolverAgent",
      "prompt": "Using the twisterlab-agents MCP server, resolve ticket ID: {{{input}}}. Execute appropriate SOP and return resolution steps and status."
    },
    {
      "name": "sync",
      "description": "Synchronize cache and database",
      "prompt": "Using the twisterlab-agents MCP server, execute RealSyncAgent to synchronize cache and database. Show sync statistics and any conflicts resolved."
    },
    {
      "name": "sso",
      "description": "Manage SSO/LDAP authentication",
      "prompt": "Using the TwisterLab API auth endpoints, show SSO status and help with: {{{input}}}. Available operations: check health, list sessions (admin), revoke session (admin), test authentication."
    },
    {
      "name": "gateway",
      "description": "Manage Traefik API Gateway",
      "prompt": "Using the twisterlab-dashboard MCP, show Traefik API Gateway status for: {{{input}}}. Include routing rules, services, middlewares, and health checks."
    },
    {
      "name": "agents",
      "description": "List all TwisterLab agents",
      "prompt": "Using the twisterlab-agents MCP server, list all 7 Real agents with their current status, capabilities, and recent activity. Format as a clean table."
    },
    {
      "name": "restart",
      "description": "Restart a Docker service",
      "prompt": "Using the twisterlab-dashboard MCP server restart_service tool, restart the service: {{{input}}}. First show current status, then execute restart, and verify new status after 30 seconds."
    }
  ],

  "customCommands": [
    {
      "name": "Infrastructure Status",
      "prompt": "Get complete TwisterLab infrastructure status via dashboard MCP and present it in a visually appealing format with status indicators, metrics, and recommendations.",
      "description": "Complete infrastructure overview"
    },
    {
      "name": "Deploy Stack",
      "prompt": "Help me deploy the complete TwisterLab stack. Check infrastructure/docker/docker-compose.unified.yml, verify prerequisites, and guide deployment steps with safety checks.",
      "description": "Deploy full TwisterLab stack"
    },
    {
      "name": "Security Audit",
      "prompt": "Perform a security audit of TwisterLab: 1) Check SSO/LDAP configuration, 2) Review Traefik security headers, 3) Verify Docker secrets, 4) Check API authentication, 5) Review network policies. Provide security score and recommendations.",
      "description": "Complete security audit"
    },
    {
      "name": "Performance Analysis",
      "prompt": "Analyze TwisterLab performance: 1) Get Prometheus metrics, 2) Check Docker resource usage, 3) Review API response times, 4) Analyze agent execution times, 5) Check database query performance. Provide optimization recommendations.",
      "description": "Performance analysis and optimization"
    },
    {
      "name": "Disaster Recovery",
      "prompt": "Guide disaster recovery process: 1) Check backup status via RealBackupAgent, 2) List available backups, 3) Verify backup integrity, 4) Provide recovery steps for: {{{input}}}.",
      "description": "Disaster recovery guidance"
    },
    {
      "name": "Network Troubleshooting",
      "prompt": "Troubleshoot network issues: 1) Check Traefik routes and services, 2) Verify Docker network connectivity, 3) Test API endpoints, 4) Check Prometheus targets, 5) Analyze recent access logs. Focus on: {{{input}}}.",
      "description": "Network troubleshooting"
    }
  ],

  "contextProviders": [
    {
      "name": "twisterlab-dashboard",
      "description": "Current infrastructure status from dashboard MCP",
      "query": "dashboard://status"
    },
    {
      "name": "prometheus",
      "description": "Prometheus metrics and targets",
      "query": "dashboard://prometheus"
    },
    {
      "name": "agents",
      "description": "TwisterLab agents status",
      "query": "dashboard://agents"
    }
  ]
}
```

---

# Installation Instructions

## 1. Update Continue IDE Configuration

Open `C:\Users\Administrator\.continue\config.json` and add the above slash commands and custom commands to the existing configuration.

## 2. Restart Continue IDE

Close and reopen VS Code to reload the configuration.

## 3. Test Commands

Try the following commands in Continue IDE chat:

```
/dashboard
/health
/agents
/monitor api
/gateway
/sso check health
```

## 4. Available MCP Tools

### twisterlab-dashboard MCP:
- `get_dashboard` - Complete infrastructure dashboard
- `check_api_health` - TwisterLab API health
- `get_agents_status` - All 7 Real agents status
- `get_prometheus_targets` - Prometheus scrape targets
- `get_traefik_services` - Traefik services and routes
- `restart_service(service_name)` - Restart Docker service

### twisterlab-agents MCP:
- `monitor_system_health` - System metrics (CPU, RAM, Disk)
- `create_backup(type)` - Create backup
- `sync_cache_db` - Sync cache and database
- `classify_ticket(description)` - Classify ticket
- `resolve_ticket(id, category)` - Resolve ticket
- `execute_desktop_command(command)` - Execute remote command
- `orchestrate_workflow(type)` - Multi-agent workflow

---

# Usage Examples

## Monitor Infrastructure

```
/dashboard
```
Shows: API, Agents, Prometheus, Traefik, Docker services with health status.

## Check Specific Component

```
/monitor prometheus
```
Shows: Prometheus targets, scrape status, metrics availability.

## Deploy Service

```
/deploy twisterlab_api
```
Guides through: Current status → Review config → Deploy command → Verification.

## Create Backup

```
/backup full
```
Executes: RealBackupAgent full backup → Shows progress → Verifies integrity.

## Classify Ticket

```
/classify Server API returns 500 error on /health endpoint
```
Returns: Category, Priority, Assigned Agent, Suggested SOP.

## Restart Service

```
/restart twisterlab_api
```
Executes: Check current → Restart → Wait → Verify new status.

---

# Advanced Orchestration

## Multi-Step Workflow

```
Custom Command: "Infrastructure Status"
```
Executes:
1. Dashboard MCP → Get all component status
2. Format with emojis and indicators
3. Calculate overall health score
4. Provide recommendations

## Security Audit

```
Custom Command: "Security Audit"
```
Executes:
1. Check SSO/LDAP config
2. Review Traefik security headers
3. Verify Docker secrets
4. Check API authentication
5. Review network policies
6. Generate security score

## Performance Analysis

```
Custom Command: "Performance Analysis"
```
Executes:
1. Get Prometheus metrics
2. Check Docker resources
3. Review API response times
4. Analyze agent execution
5. Provide optimization recommendations

---

**Continue IDE est maintenant configuré pour orchestrer complètement TwisterLab !** 🎉
