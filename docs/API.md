# TwisterLab API Documentation

## Overview

TwisterLab exposes a RESTful API built with FastAPI. The API provides endpoints for agent management, MCP (Model Context Protocol) operations, browser automation, and system monitoring.

**Base URL:** `http://edgeserver.twisterlab.local:30001`

## Authentication

### POST /auth/login

Authenticate and obtain an access token.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### POST /auth/logout

Invalidate the current session.

### GET /auth/me

Get the current authenticated user information.

---

## System Endpoints

### GET /system/health

Returns the health status of all system components.

**Response:**

```json
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "redis": "ok",
    "agents": "ok"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /system/status

Returns detailed system status including uptime and resource usage.

### GET /system/metrics

Prometheus-compatible metrics endpoint for monitoring.

---

## MCP (Model Context Protocol) Endpoints

### GET /mcp/list_autonomous_agents

List all registered autonomous agents.

**Response:**

```json
{
  "agents": [
    {
      "id": "browser-agent-1",
      "type": "BrowserAgent",
      "status": "active",
      "capabilities": ["navigate", "screenshot", "extract"]
    }
  ]
}
```

### POST /mcp/classify_ticket

Classify a support ticket using AI.

**Request Body:**

```json
{
  "ticket_id": "string",
  "content": "string",
  "metadata": {}
}
```

**Response:**

```json
{
  "ticket_id": "string",
  "classification": "bug|feature|support|question",
  "confidence": 0.95,
  "suggested_priority": "high|medium|low"
}
```

### POST /mcp/resolve_ticket

Attempt automatic resolution of a classified ticket.

### GET /mcp/monitor_system_health

Get real-time system health metrics for MCP operations.

### POST /mcp/create_backup

Create a system backup.

**Request Body:**

```json
{
  "backup_type": "full|incremental",
  "include_database": true,
  "include_configs": true
}
```

### POST /mcp/sync_cache_db

Synchronize cache with database.

### POST /mcp/execute_command

Execute a system command (restricted permissions).

**Request Body:**

```json
{
  "command": "string",
  "timeout": 30,
  "working_directory": "string"
}
```

---

## Browser Automation Endpoints

### POST /browser/visit

Navigate to a URL and return page information.

**Request Body:**

```json
{
  "url": "https://example.com",
  "wait_for": "networkidle",
  "timeout": 30000
}
```

**Response:**

```json
{
  "success": true,
  "title": "Example Domain",
  "url": "https://example.com",
  "screenshot_base64": "..."
}
```

### POST /browser/screenshot

Capture a screenshot of the current page.

### POST /browser/extract

Extract structured data from a web page.

---

## Agent Management Endpoints

### GET /agents

List all agents.

### POST /agents

Create a new agent.

### GET /agents/{agent_id}

Get details of a specific agent.

### PUT /agents/{agent_id}

Update an agent configuration.

### DELETE /agents/{agent_id}

Delete an agent.

### POST /agents/{agent_id}/execute

Execute a task with a specific agent.

---

## Workflow Orchestration

### POST /orchestrator/workflow

Create and execute a multi-agent workflow.

**Request Body:**

```json
{
  "name": "ticket-resolution",
  "steps": [
    {"agent": "classifier", "action": "classify"},
    {"agent": "resolver", "action": "resolve", "depends_on": [0]}
  ],
  "input": {}
}
```

### GET /orchestrator/workflow/{workflow_id}

Get workflow execution status.

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "ValidationError"
}
```

**Common Status Codes:**

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## SDK Usage Examples

### Python

```python
import httpx

client = httpx.Client(base_url="http://edgeserver.twisterlab.local:30001")

# Login
response = client.post("/auth/login", json={
    "username": "admin",
    "password": "secret"
})
token = response.json()["access_token"]
client.headers["Authorization"] = f"Bearer {token}"

# List agents
agents = client.get("/mcp/list_autonomous_agents").json()

# Classify a ticket
result = client.post("/mcp/classify_ticket", json={
    "ticket_id": "TKT-001",
    "content": "Application crashes on startup"
}).json()
```

### JavaScript/TypeScript

```typescript
const API_BASE = 'http://edgeserver.twisterlab.local:30001';

async function classifyTicket(ticketId: string, content: string) {
  const response = await fetch(`${API_BASE}/mcp/classify_ticket`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ ticket_id: ticketId, content })
  });
  return response.json();
}
```

---

## Rate Limiting

- **Default:** 100 requests per minute
- **Authenticated:** 1000 requests per minute
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Versioning

API version is included in responses via the `X-API-Version` header. Current version: `v1.0.0`
