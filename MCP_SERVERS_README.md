# TwisterLab MCP Server Configuration

This document explains how to configure TwisterLab's MCP (Model Context Protocol) servers for different IDE integrations.

## Overview

TwisterLab provides unified MCP servers that give IDEs access to all agent capabilities through a single, comprehensive interface.

## Available MCP Servers

### 1. Continue IDE Server
- **File**: `agents/mcp/mcp_server_continue.py`
- **Capabilities**: 15 tools, 10 resources
- **Protocol**: MCP 2024-11-05
- **Transport**: stdio (JSON-RPC 2.0)

### 2. Claude Desktop Server
- **File**: `agents/mcp/mcp_server.py`
- **Capabilities**: 15 tools, 10 resources
- **Protocol**: MCP 2024-11-05
- **Transport**: stdio (JSON-RPC 2.0)

## Configuration

### Continue IDE Setup

1. **Locate Continue configuration**:
   - Open Continue settings in VS Code
   - Go to MCP Servers section

2. **Add server configuration**:
   ```json
   {
     "mcpServers": {
       "twisterlab-unified": {
         "command": "python",
         "args": ["agents/mcp/mcp_server_continue.py"],
         "env": {
           "PYTHONPATH": "."
         }
       }
     }
   }
   ```

3. **Restart Continue** to load the new server

### Claude Desktop Setup

1. **Locate Claude Desktop configuration**:
   - Open Claude Desktop settings
   - Find the MCP servers configuration file

2. **Add server configuration**:
   ```json
   {
     "mcpServers": {
       "twisterlab-unified": {
         "command": "python",
         "args": ["agents/mcp/mcp_server.py"],
         "env": {
           "PYTHONPATH": "."
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** to load the new server

## Available Tools

The unified MCP servers provide access to:

### Agent Operations
- `execute_agent_task` - Execute tasks on specific agents
- `create_workflow` - Create multi-agent workflows
- `get_agent_status` - Check agent health and status

### Monitoring & Observability
- `get_system_metrics` - Real-time system metrics
- `get_agent_metrics` - Agent performance metrics
- `subscribe_to_events` - Real-time event streaming

### Search & Knowledge
- `semantic_search` - Search across agent knowledge bases
- `get_workflow_history` - Workflow execution history

### Learning & Adaptation
- `analyze_performance` - AI-powered performance analysis
- `optimize_workflow` - Workflow optimization suggestions

## Available Resources

- `agent://{agent_name}` - Agent-specific information
- `workflow://{workflow_id}` - Workflow definitions and status
- `metric://{metric_name}` - System and agent metrics
- `knowledge://{domain}` - Domain-specific knowledge bases

## Testing

Test your MCP server configuration:

```bash
# Test Continue IDE server
python -c "
from agents.mcp.mcp_server_continue import MCPServerContinue
server = MCPServerContinue()
print(f'Server initialized with {len(server.unified_server.tools)} tools')
"

# Test Claude Desktop server
python -c "
from agents.mcp.mcp_server import MCPServer
server = MCPServer()
print(f'Server initialized with {len(server.unified_server.tools)} tools')
"
```

## Troubleshooting

### Server Won't Start
- Ensure Python path includes the project root
- Check that all dependencies are installed
- Verify agent registry is accessible

### Tools Not Available
- Check server logs for initialization errors
- Ensure unified MCP server initializes correctly
- Verify agent registration in communication system

### Connection Issues
- Confirm MCP protocol version compatibility
- Check stdio transport configuration
- Verify environment variables are set correctly

## Security Notes

- MCP servers run with the same permissions as the IDE
- All agent operations go through the secure MCP router
- Communication is isolated by tier-based security
- Credentials are managed through Docker secrets
