# TwisterLab - API Reference
### 1. User Management
- **GET /api/users**
  - **Description**: Retrieve a list of users.
  - **Authentication**: JWT (required)
  - **Response**: JSON array of user objects.

### 2. Agent Management
- **POST /api/agents**
  - **Description**: Create a new AI agent.
  - **Authentication**: JWT (required)
  - **Request Body**: Agent configuration details.
  - **Response**: Created agent details.

### 3. Monitoring
- **GET /api/metrics**
  - **Description**: Retrieve system metrics.
  - **Authentication**: JWT (required)
  - **Response**: JSON object containing metrics.

## Request/Response Examples
### Example Request:
```http
GET /api/users HTTP/1.1
Host: localhost:3000
Authorization: Bearer <JWT_TOKEN>
```

### Example Response:
# TwisterLab - API Reference

## Overview

TwisterLab provides a comprehensive REST API for interacting with AI agents, managing workflows, and monitoring system health. The API supports both standard REST operations and Model Context Protocol (MCP) for advanced agent interactions.

## Base URL

```
Production: https://api.twisterlab.local/v1/
Development: http://localhost:8000/v1/
```

## Authentication

### JWT Token Authentication

```bash
# Get access token
curl -X POST https://api.twisterlab.local/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.twisterlab.local/v1/agents/
```

### API Key Authentication (Service-to-Service)

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  https://api.twisterlab.local/v1/agents/
```

## Core Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-15T10:00:00Z",
  "services": {
    "database": "up",
    "redis": "up",
    "ollama": "up"
  }
}
```

### Agent Management

#### List Agents

```http
GET /agents/
```

**Response:**

```json
{
  "agents": [
    {
      "name": "monitoring",
      "display_name": "Monitoring Agent",
      "description": "System health monitoring",
      "status": "active",
      "capabilities": ["cpu", "memory", "disk"]
    }
  ]
}
```

#### Get Agent Details

```http
GET /agents/{agent_name}
```

**Response:**

```json
{
  "name": "monitoring",
  "display_name": "Monitoring Agent",
  "description": "System health monitoring",
  "tools": [
    {
      "name": "check_system_health",
      "description": "Check overall system health",
      "parameters": {
        "type": "object",
        "properties": {
          "detailed": {"type": "boolean", "default": false}
        }
      }
    }
  ]
}
```

#### Execute Agent Task

```http
POST /agents/{agent_name}/execute
```

**Request:**

```json
{
  "task": "check_system_health",
  "context": {
    "detailed": true,
    "target_hosts": ["server1", "server2"]
  },
  "async": false
}
```

**Response:**

```json
{
  "task_id": "task_12345",
  "status": "completed",
  "result": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  },
  "execution_time": 2.34
}
```

### Ticket Management

#### Create Ticket

```http
POST /tickets/
```

**Request:**

```json
{
  "title": "Server CPU high",
  "description": "CPU usage is consistently above 90%",
  "priority": "high",
  "category": "performance",
  "requester": "john.doe@company.com"
}
```

**Response:**

```json
{
  "ticket_id": "TICK-001",
  "status": "created",
  "assigned_agent": "monitoring",
  "estimated_resolution": "2025-11-15T11:00:00Z"
}
```

#### Get Ticket Status

```http
GET /tickets/{ticket_id}
```

**Response:**

```json
{
  "ticket_id": "TICK-001",
  "status": "in_progress",
  "progress": 75,
  "current_step": "Analyzing system metrics",
  "assigned_agent": "resolver",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

#### List Tickets

```http
GET /tickets/?status=open&priority=high
```

**Response:**

```json
{
  "tickets": [
    {
      "ticket_id": "TICK-001",
      "title": "Server CPU high",
      "status": "in_progress",
      "priority": "high",
      "created_at": "2025-11-15T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### Workflow Management

#### Create Workflow

```http
POST /workflows/
```

**Request:**

```json
{
  "name": "incident_response",
  "description": "Automated incident response workflow",
  "steps": [
    {
      "agent": "monitoring",
      "task": "check_system_health",
      "conditions": {"cpu_threshold": 90}
    },
    {
      "agent": "resolver",
      "task": "execute_sop",
      "parameters": {"sop_id": "cpu_high"}
    }
  ],
  "triggers": {
    "type": "alert",
    "source": "prometheus",
    "condition": "cpu_usage > 90"
  }
}
```

#### Execute Workflow

```http
POST /workflows/{workflow_id}/execute
```

**Request:**

```json
{
  "context": {
    "alert_source": "prometheus",
    "cpu_usage": 95,
    "affected_hosts": ["web-server-01"]
  }
}
```

### MCP (Model Context Protocol)

#### List Available Tools

```http
GET /mcp/tools/
```

**Response:**

```json
{
  "tools": [
    {
      "name": "monitoring.check_system_health",
      "description": "Check overall system health metrics",
      "input_schema": {
        "type": "object",
        "properties": {
          "detailed": {"type": "boolean"},
          "target_hosts": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  ]
}
```

#### Execute MCP Tool

```http
POST /mcp/tools/execute
```

**Request:**

```json
{
  "tool": "monitoring.check_system_health",
  "arguments": {
    "detailed": true,
    "target_hosts": ["server1", "server2"]
  }
}
```

**Response:**

```json
{
  "result": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1,
    "services": [
      {"name": "nginx", "status": "running"},
      {"name": "postgres", "status": "running"}
    ]
  }
}
```

### Monitoring & Metrics

#### System Metrics

```http
GET /metrics
```

Returns Prometheus-compatible metrics:

```
# HELP twisterlab_api_requests_total Total number of API requests
# TYPE twisterlab_api_requests_total counter
twisterlab_api_requests_total{method="GET",endpoint="/health",status="200"} 12543

# HELP twisterlab_agent_execution_duration_seconds Agent execution duration
# TYPE twisterlab_agent_execution_duration_seconds histogram
twisterlab_agent_execution_duration_seconds_bucket{agent="monitoring",le="1.0"} 45
```

#### Health Status

```http
GET /health/detailed
```

**Response:**

```json
{
  "overall_status": "healthy",
  "components": {
    "api": {"status": "healthy", "response_time": 45},
    "database": {"status": "healthy", "connections": 12},
    "redis": {"status": "healthy", "memory_usage": 234567},
    "ollama": {"status": "healthy", "models_loaded": 2},
    "agents": {
      "monitoring": "healthy",
      "backup": "healthy",
      "resolver": "healthy"
    }
  }
}
```

### Audit & Logging

#### Get Audit Logs

```http
GET /audit/logs/?agent=monitoring&start_date=2025-11-15&end_date=2025-11-15
```

**Response:**

```json
{
  "logs": [
    {
      "timestamp": "2025-11-15T10:00:00Z",
      "agent": "monitoring",
      "action": "check_system_health",
      "result": "success",
      "duration": 2.34,
      "details": {"cpu": 45.2, "memory": 67.8}
    }
  ]
}
```

#### Export Audit Data

```http
GET /audit/export/?format=json&start_date=2025-11-01&end_date=2025-11-15
```

## WebSocket Endpoints

### Real-time Agent Communication

```javascript
const ws = new WebSocket('ws://api.twisterlab.local/ws/agents/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent update:', data);
};

// Send message to agent
ws.send(JSON.stringify({
  type: 'execute',
  agent: 'monitoring',
  task: 'check_health'
}));
```

### Workflow Progress

```javascript
const ws = new WebSocket('ws://api.twisterlab.local/ws/workflows/');

ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  updateProgressBar(progress.percentage);
};
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent 'unknown_agent' not found",
    "details": {
      "available_agents": ["monitoring", "backup", "resolver"]
    }
  },
  "timestamp": "2025-11-15T10:00:00Z",
  "request_id": "req_12345"
}
```

### Common Error Codes

- `AGENT_NOT_FOUND`: Specified agent doesn't exist
- `INVALID_PARAMETERS`: Request parameters are invalid
- `AGENT_BUSY`: Agent is currently executing another task
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `AUTHENTICATION_FAILED`: Invalid credentials
- `PERMISSION_DENIED`: Insufficient permissions

## Rate Limiting

### Default Limits

- **Authenticated users**: 1000 requests/hour
- **API keys**: 5000 requests/hour
- **Anonymous**: 100 requests/hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1636972800
X-RateLimit-Retry-After: 3600
```

## SDK Examples

### Python Client

```python
import requests

class TwisterLabClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def execute_agent(self, agent: str, task: str, context: dict = None):
        response = requests.post(
            f"{self.base_url}/agents/{agent}/execute",
            json={"task": task, "context": context or {}},
            headers=self.headers
        )
        return response.json()

# Usage
client = TwisterLabClient("https://api.twisterlab.local/v1/", "your_api_key")
result = client.execute_agent("monitoring", "check_system_health")
```

### JavaScript Client

```javascript
class TwisterLabAPI {
    constructor(baseURL, apiKey) {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
        };
    }

    async executeAgent(agent, task, context = {}) {
        const response = await fetch(`${this.baseURL}/agents/${agent}/execute`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ task, context })
        });
        return await response.json();
    }
}

// Usage
const api = new TwisterLabAPI('https://api.twisterlab.local/v1/', 'your_api_key');
const result = await api.executeAgent('monitoring', 'check_system_health');
```

## API Versioning

- **v1**: Current stable version
- **v0**: Deprecated (use v1)

All endpoints support the `Accept-Version` header:

```http
Accept-Version: v1
```

## Support

For API support:

- **Documentation**: https://api.twisterlab.local/docs
- **Status Page**: https://status.twisterlab.local
- **Issues**: Create GitHub issues with API logs

---

**Version**: 1.0.0 | **Last Updated**: 2025-11-15
```