# MCP (Model Context Protocol) Integration Guide

TwisterLab implements **dual-mode MCP architecture** for maximum interoperability:

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    TwisterLab MCP                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐              ┌────────────────┐     │
│  │   MODE 1       │              │   MODE 2       │     │
│  │  REST Wrapper  │              │ Native stdio   │     │
│  │                │              │  MCP Server    │     │
│  │ /v1/mcp/*      │              │  JSON-RPC 2.0  │     │
│  └────────────────┘              └────────────────┘     │
│         ▲                               ▲               │
│         │                               │               │
│  ┌──────┴─────────┐              ┌──────┴──────┐        │
│  │ Python/Node/   │              │   Claude    │        │
│  │ Bash/curl      │              │   Desktop   │        │
│  │ Any HTTP client│              │             │        │
│  └────────────────┘              └─────────────┘        │
│                                                          │
│              ┌──────────────────────┐                    │
│              │   MCP Router         │                    │
│              │  (Tier Isolation)    │                    │
│              └──────────────────────┘                    │
│                        ▼                                 │
│         ┌──────────────────────────────┐                 │
│         │  TwisterLab Agents           │                 │
│         │  (Monitoring, Backup, etc.)  │                 │
│         └──────────────────────────────┘                 │
└──────────────────────────────────────────────────────────┘
```

## Mode 1: REST API (Universal Interoperability)

### Quick Start

**Base URL**: `http://192.168.0.30:8000/v1/mcp`

### Health Check
```bash
curl http://192.168.0.30:8000/v1/mcp/health
```

### List Available Tools
```bash
curl http://192.168.0.30:8000/v1/mcp/tools
```

**Response:**
```json
{
  "status": "success",
  "tools": [
    {
      "name": "monitor_system_health",
      "description": "Check system health (CPU, RAM, disk, Docker services)",
      "inputSchema": {...}
    },
    {
      "name": "classify_ticket",
      "description": "Classify IT helpdesk ticket using LLM",
      "inputSchema": {...}
    }
  ]
}
```

### Call a Tool (Simplified)
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "monitor_system_health",
    "arguments": {"include_docker": true}
  }'
```

**Response:**
```json
{
  "status": "success",
  "tool": "monitor_system_health",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"status\": \"healthy\",\n  \"services\": [\"api\", \"database\", \"cache\"]\n}"
      }
    ]
  }
}
```

### Read a Resource (Simplified)
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "twisterlab://system/health"
  }'
```

### Universal Endpoint (Full MCP Protocol)

**POST `/v1/mcp/message`** - Accepts any MCP JSON-RPC method

```bash
# List tools
curl -X POST http://192.168.0.30:8000/v1/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'

# Call tool
curl -X POST http://192.168.0.30:8000/v1/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "classify_ticket",
      "arguments": {
        "ticket_text": "Cannot connect to WiFi"
      }
    }
  }'

# Read resource
curl -X POST http://192.168.0.30:8000/v1/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "method": "resources/read",
    "params": {
      "uri": "twisterlab://agents/status"
    }
  }'

# Get prompt template
curl -X POST http://192.168.0.30:8000/v1/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "method": "prompts/get",
    "params": {
      "name": "classify_it_ticket",
      "arguments": {
        "ticket_description": "Printer offline"
      }
    }
  }'
```

## Client Examples

### Python Client

```python
import requests

# Simple tool call
def call_mcp_tool(tool_name: str, arguments: dict):
    response = requests.post(
        "http://192.168.0.30:8000/v1/mcp/tools/call",
        json={
            "tool": tool_name,
            "arguments": arguments
        }
    )
    return response.json()

# Example: Monitor system health
result = call_mcp_tool(
    "monitor_system_health",
    {"include_docker": True}
)
print(result)

# Example: Classify ticket
result = call_mcp_tool(
    "classify_ticket",
    {"ticket_text": "Cannot connect to WiFi network"}
)
print(result)
```

### Node.js Client

```javascript
const axios = require('axios');

// Simple tool call
async function callMCPTool(toolName, arguments) {
  const response = await axios.post(
    'http://192.168.0.30:8000/v1/mcp/tools/call',
    {
      tool: toolName,
      arguments: arguments
    }
  );
  return response.data;
}

// Example: Monitor system
callMCPTool('monitor_system_health', { include_docker: true })
  .then(result => console.log(result))
  .catch(error => console.error(error));

// Example: Classify ticket
callMCPTool('classify_ticket', {
  ticket_text: 'Email not sending'
})
  .then(result => console.log(result));
```

### PowerShell Client

```powershell
# Simple tool call
$body = @{
    tool = "monitor_system_health"
    arguments = @{
        include_docker = $true
    }
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Method POST `
    -Uri "http://192.168.0.30:8000/v1/mcp/tools/call" `
    -Body $body `
    -ContentType "application/json"

$response | ConvertTo-Json -Depth 10
```

### Bash/Shell Client

```bash
#!/bin/bash

# Function to call MCP tool
call_mcp_tool() {
    local tool=$1
    local args=$2
    
    curl -s -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
        -H "Content-Type: application/json" \
        -d "{\"tool\":\"$tool\",\"arguments\":$args}" \
        | jq .
}

# Example: Monitor system
call_mcp_tool "monitor_system_health" '{"include_docker":true}'

# Example: Classify ticket
call_mcp_tool "classify_ticket" '{"ticket_text":"Printer not working"}'
```

## Mode 2: Native MCP Server (Claude Desktop)

### Claude Desktop Configuration

**Location**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "twisterlab": {
      "command": "python",
      "args": [
        "-m",
        "agents.mcp.mcp_server"
      ],
      "cwd": "C:\\TwisterLab",
      "env": {
        "PYTHONPATH": "C:\\TwisterLab",
        "LOG_LEVEL": "INFO"
      },
      "description": "TwisterLab Multi-Agent IT Helpdesk System",
      "capabilities": {
        "tools": true,
        "resources": true,
        "prompts": true
      }
    }
  }
}
```

### Usage in Claude Desktop

After configuration, Claude Desktop will automatically connect to TwisterLab MCP server via stdio.

**Available Tools** (visible in Claude):
- `monitor_system_health` - Check system health
- `create_backup` - Create database backup
- `sync_cache_db` - Sync Redis with PostgreSQL
- `classify_ticket` - Classify IT ticket
- `resolve_ticket` - Execute SOP for ticket

**Available Resources**:
- `twisterlab://system/health` - Current system metrics
- `twisterlab://agents/status` - Agent statuses
- `twisterlab://audit/mcp-log` - MCP communication log

**Available Prompts**:
- `classify_it_ticket` - IT ticket classification template
- `resolve_network_issue` - Network troubleshooting SOP

### Example Claude Conversation

```
User: Monitor the system health including Docker services

Claude: [Calls monitor_system_health tool with include_docker=true]
        System is healthy. All services operational:
        - API: Running
        - Database: Running
        - Cache: Running
        - Docker: 8/8 services up

User: Classify this ticket: "User cannot access shared drive"

Claude: [Calls classify_ticket tool]
        Category: access
        Confidence: 0.92
        Priority: medium
        Recommended action: Check network drive permissions
```

## Available Tools

### monitor_system_health
Check system health (CPU, RAM, disk, Docker services).

**Arguments:**
- `include_docker` (boolean, optional): Include Docker service status. Default: `true`

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "monitor_system_health",
    "arguments": {"include_docker": true}
  }'
```

### create_backup
Create PostgreSQL database backup.

**Arguments:**
- `compression` (string, optional): Compression method. Options: `gzip`, `none`. Default: `gzip`

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create_backup",
    "arguments": {"compression": "gzip"}
  }'
```

### sync_cache_db
Synchronize Redis cache with PostgreSQL database.

**Arguments:**
- `force` (boolean, optional): Force sync even if cache is fresh. Default: `false`

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "sync_cache_db",
    "arguments": {"force": false}
  }'
```

### classify_ticket
Classify IT helpdesk ticket using LLM.

**Arguments:**
- `ticket_text` (string, **required**): Ticket description text

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "classify_ticket",
    "arguments": {
      "ticket_text": "Cannot connect to WiFi network"
    }
  }'
```

### resolve_ticket
Execute SOP to resolve classified ticket.

**Arguments:**
- `ticket_id` (string, **required**): Ticket identifier
- `category` (string, **required**): Ticket category from classifier

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "resolve_ticket",
    "arguments": {
      "ticket_id": "TKT-12345",
      "category": "network"
    }
  }'
```

## Available Resources (Read-Only)

### twisterlab://system/health
Current system health metrics.

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "twisterlab://system/health"}'
```

### twisterlab://agents/status
All autonomous agent statuses.

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "twisterlab://agents/status"}'
```

### twisterlab://audit/mcp-log
Audit trail of MCP communications.

**Example:**
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "twisterlab://audit/mcp-log"}'
```

## API Reference

### REST Endpoints

#### GET `/v1/mcp/health`
Health check for MCP REST API.

#### GET `/v1/mcp/tools`
List all available tools.

#### GET `/v1/mcp/resources`
List all available resources.

#### GET `/v1/mcp/prompts`
List all available prompt templates.

#### POST `/v1/mcp/tools/call`
Call a tool (simplified endpoint).

**Request Body:**
```json
{
  "tool": "string",
  "arguments": {}
}
```

#### POST `/v1/mcp/resources/read`
Read a resource (simplified endpoint).

**Request Body:**
```json
{
  "uri": "string"
}
```

#### POST `/v1/mcp/message`
Universal MCP endpoint (full JSON-RPC protocol).

**Request Body:**
```json
{
  "method": "string",
  "params": {},
  "id": "string (optional)"
}
```

**Supported Methods:**
- `initialize` - Initialize MCP connection
- `tools/list` - List available tools
- `tools/call` - Call a tool
- `resources/list` - List available resources
- `resources/read` - Read a resource
- `prompts/list` - List available prompts
- `prompts/get` - Get a prompt template

## Testing

### Run Native MCP Tests
```bash
pytest tests/test_mcp_native.py -v
```

### Run REST API Tests
```bash
pytest tests/test_mcp_rest.py -v
```

### Integration Test (Manual)

**Test Claude Desktop:**
1. Configure `claude_desktop_config.json`
2. Restart Claude Desktop
3. Ask Claude to "List available TwisterLab tools"
4. Ask Claude to "Monitor system health"

**Test REST API:**
```bash
# Test from Windows (PowerShell)
$body = @{tool="monitor_system_health"; arguments=@{include_docker=$true}} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri "http://192.168.0.30:8000/v1/mcp/tools/call" -Body $body -ContentType "application/json"

# Test from Linux (bash)
curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool":"monitor_system_health","arguments":{"include_docker":true}}'
```

## Security & Isolation

MCP Router enforces **tier-based isolation**:

- **Tier 1** (172.25.0.0/16): TwisterLab Agent MCPs
- **Tier 2** (172.26.0.0/16): Claude Desktop MCPs
- **Tier 3** (172.27.0.0/16): Docker System MCPs
- **Tier 4** (172.28.0.0/16): Copilot MCPs

**No cross-tier communication allowed** - all access is audited and logged.

## Troubleshooting

### Claude Desktop Not Connecting

1. Verify config path: `%APPDATA%\Claude\claude_desktop_config.json`
2. Check Python is in PATH: `python --version`
3. Verify TwisterLab path in config
4. Check Claude Desktop logs

### REST API Not Responding

```bash
# Check API health
curl http://192.168.0.30:8000/health

# Check MCP health
curl http://192.168.0.30:8000/v1/mcp/health

# Check logs
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 50"
```

### Tool Execution Fails

Check MCP audit log:
```bash
curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri":"twisterlab://audit/mcp-log"}' \
  | jq .
```

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **TwisterLab Docs**: `README.md`
- **MCP Router**: `agents/mcp/mcp_router.py`
- **Native MCP Server**: `agents/mcp/mcp_server.py`
- **REST Wrapper**: `api/endpoints/mcp_rest.py`
