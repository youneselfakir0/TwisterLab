# TwisterLab API Documentation v1.0.0

## Overview

TwisterLab provides a comprehensive REST API for autonomous IT helpdesk automation. The API exposes endpoints for all 7 production agents and system monitoring.

**Base URL:** `http://localhost:8001`
**Authentication:** None required (internal system)
**Content-Type:** `application/json`

## API Endpoints

### Health Check
- **GET** `/health`
- **Description:** System health status
- **Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T17:40:25Z",
  "version": "1.0.0"
}
```

### Agent Operations

#### Classifier Agent
- **POST** `/agents/classifier/execute`
- **Description:** Classify incoming tickets and route to appropriate agents
- **Request Body:**
```json
{
  "ticket_id": "T-001",
  "title": "Cannot connect to WiFi",
  "description": "User reports WiFi connection issues",
  "priority": "high",
  "category": "network"
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "ClassifierAgent",
  "result": {
    "classification": "network_issue",
    "routed_to_agent": "resolver",
    "confidence": 0.95,
    "estimated_resolution_time": "15 minutes"
  }
}
```

#### Resolver Agent
- **POST** `/agents/resolver/execute`
- **Description:** Execute SOPs and resolve issues autonomously
- **Request Body:**
```json
{
  "ticket_id": "T-001",
  "issue_type": "network_issue",
  "context": {
    "user_id": "user123",
    "device_info": "Windows 11 Pro",
    "error_logs": "..."
  }
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "ResolverAgent",
  "result": {
    "resolution_applied": "network_reset",
    "steps_executed": [
      "Diagnosed network adapter",
      "Reset TCP/IP stack",
      "Renewed DHCP lease"
    ],
    "resolution_status": "resolved",
    "follow_up_required": false
  }
}
```

#### Desktop Commander Agent
- **POST** `/agents/desktop_commander/execute`
- **Description:** Execute system commands securely on Windows/Linux
- **Request Body:**
```json
{
  "ticket_id": "T-001",
  "command_type": "system_diagnostic",
  "commands": [
    "ipconfig /all",
    "netsh wlan show interfaces",
    "ping 8.8.8.8"
  ],
  "timeout_seconds": 30
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "DesktopCommanderAgent",
  "result": {
    "commands_executed": 3,
    "output": {
      "ipconfig": "...",
      "netsh": "...",
      "ping": "..."
    },
    "execution_time": "2.3 seconds",
    "security_check_passed": true
  }
}
```

#### Maestro Orchestrator Agent
- **POST** `/agents/maestro/execute`
- **Description:** Load balancing and workflow orchestration
- **Request Body:**
```json
{
  "workflow_id": "wf-001",
  "agents_required": ["resolver", "desktop_commander"],
  "load_distribution": "balanced",
  "priority": "high"
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "MaestroOrchestratorAgent",
  "result": {
    "workflow_status": "orchestrated",
    "agents_assigned": ["resolver", "desktop_commander"],
    "load_balance_achieved": true,
    "estimated_completion": "10 minutes"
  }
}
```

#### Sync Agent
- **POST** `/agents/sync/execute`
- **Description:** Cache/DB synchronization and consistency verification
- **Request Body:**
```json
{
  "operation": "sync",
  "scope": "full_system",
  "verify_consistency": true
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "SyncAgent",
  "result": {
    "operation": "sync_completed",
    "records_synced": 1250,
    "consistency_check": "passed",
    "sync_duration": "45 seconds"
  }
}
```

#### Backup Agent
- **POST** `/agents/backup/execute`
- **Description:** Disaster recovery and automated backups
- **Request Body:**
```json
{
  "operation": "backup",
  "type": "full_system",
  "destination": "local"
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "BackupAgent",
  "result": {
    "operation": "backup_completed",
    "backup_size": "2.3 GB",
    "files_backed_up": 15420,
    "backup_duration": "8 minutes",
    "integrity_check": "passed"
  }
}
```

#### Monitoring Agent
- **POST** `/agents/monitoring/execute`
- **Description:** Real-time metrics, alerting, and health checks
- **Request Body:**
```json
{
  "operation": "health_check",
  "components": ["api", "database", "agents", "docker"],
  "alert_thresholds": {
    "cpu_usage": 80,
    "memory_usage": 85,
    "disk_usage": 90
  }
}
```
- **Response:**
```json
{
  "status": "success",
  "agent": "MonitoringAgent",
  "result": {
    "overall_health": "healthy",
    "component_status": {
      "api": "healthy",
      "database": "healthy",
      "agents": "healthy",
      "docker": "healthy"
    },
    "metrics": {
      "cpu_usage": 45,
      "memory_usage": 62,
      "disk_usage": 78
    },
    "alerts_triggered": 0
  }
}
```

### System Operations

#### Get System Status
- **GET** `/status`
- **Description:** Complete system status overview
- **Response:**
```json
{
  "status": "operational",
  "uptime": "17h 25m",
  "agents": {
    "classifier": "active",
    "resolver": "active",
    "desktop_commander": "active",
    "maestro": "active",
    "sync": "active",
    "backup": "active",
    "monitoring": "active"
  },
  "infrastructure": {
    "docker_swarm": "healthy",
    "database": "connected",
    "cache": "operational"
  },
  "last_backup": "2025-11-09T02:00:00Z",
  "active_tickets": 3
}
```

#### Get Agent Status
- **GET** `/agents/{agent_name}/status`
- **Description:** Individual agent status
- **Parameters:**
  - `agent_name`: Name of the agent (classifier, resolver, desktop_commander, maestro, sync, backup, monitoring)
- **Response:**
```json
{
  "agent": "resolver",
  "status": "active",
  "uptime": "17h 25m",
  "processed_tickets": 147,
  "success_rate": 94.5,
  "average_resolution_time": "12 minutes",
  "current_load": "medium"
}
```

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "status": "error",
  "error": {
    "code": "AGENT_UNAVAILABLE",
    "message": "Requested agent is currently unavailable",
    "details": "Agent is undergoing maintenance",
    "timestamp": "2025-11-09T17:40:25Z"
  }
}
```

### Common Error Codes
- `AGENT_UNAVAILABLE`: Agent is down or maintenance
- `INVALID_REQUEST`: Malformed request data
- `OPERATION_FAILED`: Agent operation failed
- `SYSTEM_OVERLOAD`: System at capacity
- `AUTHENTICATION_FAILED`: Authentication required but failed

## Rate Limiting

- **Global Limit:** 100 requests per minute
- **Per Agent:** 20 requests per minute
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time until reset (Unix timestamp)

## Usage Examples

### Python Client
```python
import requests

# Health check
response = requests.get("http://localhost:8001/health")
print(response.json())

# Execute resolver agent
ticket_data = {
    "ticket_id": "T-001",
    "issue_type": "network_issue",
    "context": {"user_id": "user123"}
}

response = requests.post(
    "http://localhost:8001/agents/resolver/execute",
    json=ticket_data
)
result = response.json()
print(f"Resolution status: {result['result']['resolution_status']}")
```

### PowerShell Client
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8001/health" -Method GET

# Execute backup agent
$backupRequest = @{
    operation = "backup"
    type = "full_system"
    destination = "local"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/agents/backup/execute" -Method POST -Body $backupRequest -ContentType "application/json"
```

### cURL Examples
```bash
# Health check
curl -X GET http://localhost:8001/health

# Execute monitoring agent
curl -X POST http://localhost:8001/agents/monitoring/execute \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "health_check",
    "components": ["api", "database", "agents"]
  }'
```

## Monitoring & Logging

- All API requests are logged with timestamps, client info, and response codes
- Performance metrics are collected for all endpoints
- Failed requests trigger alerts to system administrators
- Logs are retained for 30 days and automatically archived

## Version History

- **v1.0.0** (2025-11-09): Initial production release
  - All 7 agents operational
  - Complete REST API
  - Health monitoring
  - Error handling
  - Rate limiting

## Support

For API support or issues:
- Check system logs: `C:\TwisterLab\logs\api.log`
- Run diagnostics: `.\debug_complete_system.ps1`
- Contact: System automatically alerts administrators for critical issues
