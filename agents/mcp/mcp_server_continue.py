"""
MCP Server for Continue IDE integration
Updated to use Unified MCP Server for comprehensive agent access

Usage:
    python agents/mcp/mcp_server_continue.py

Protocol: MCP 2024-11-05 (Model Context Protocol)
Transport: stdio (JSON-RPC 2.0)
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
import asyncio
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.mcp.unified_mcp_server import UnifiedMCPServer

# Configure logging to stderr (stdout is for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MCPServerContinue:
    """MCP Server for Continue IDE - using Unified MCP Server"""
    def __init__(self):
        """Initialize MCP server with unified capabilities"""
        self.unified_server = UnifiedMCPServer()

        # Override server info for Continue IDE
        self.unified_server.server_info = {
            "name": "twisterlab-mcp-continue",
            "version": "2.0.0",
            "description": "TwisterLab Unified MCP Server for Continue IDE",
        }

        # Create convenient aliases so the class exposes expected attributes
        # Use sensible defaults if UnifiedMCPServer doesn't define them
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle JSON-RPC 2.0 request

        Args:
            request: JSON-RPC request object

        Returns:
            JSON-RPC response object
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        logger.info(f"Handling request: {method} (id={request_id})")

        try:
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return await self._handle_tools_list(request_id)
            elif method == "tools/call":
                return await self._handle_tools_call(request_id, params)
            elif method == "resources/list":
                return await self._handle_resources_list(request_id)
            elif method == "resources/read":
                return await self._handle_resources_read(request_id, params)
            elif method == "prompts/list":
                return await self._handle_prompts_list(request_id)
            elif method == "prompts/get":
                return await self._handle_prompts_get(request_id, params)
            else:
                logger.warning(f"Unknown method: {method}")
                return self._error_response(request_id, -32601, f"Method not found: {method}")

        except Exception as e:
            logger.error(f"Error handling {method}: {e}", exc_info=True)
            return self._error_response(request_id, -32603, str(e))
        except Exception as e:
            logger.error(f"Error handling {method}: {e}", exc_info=True)
            return self._error_response(request_id, -32603, str(e))

    def _handle_initialize(self, request_id: int, params: Dict) -> Dict:
        """Initialize MCP connection"""
        client_info = params.get("clientInfo", {})
        logger.info(f"Initialize from client: {client_info.get('name', 'unknown')}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.protocol_version,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                },
                "serverInfo": self.server_info,
            },
        }

    async def _handle_tools_list(self, request_id: int) -> Dict:
        """List available tools"""
        tools = [
            {
                "name": "classify_ticket",
                "description": "Classify IT helpdesk ticket into category (network, hardware, software, account, email)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_text": {
                            "type": "string",
                            "description": "Full text of the ticket to classify",
                        }
                    },
                    "required": ["ticket_text"],
                },
            },
            {
                "name": "twisterlab_mcp_classify_ticket",
                "description": "(alias) Classify IT helpdesk ticket into category (network, hardware, software, account, email)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_text": {"type": "string", "description": "Full text of the ticket to classify"},
                    },
                    "required": ["ticket_text"],
                },
            },
            {
                "name": "resolve_ticket",
                "description": "Get resolution steps for a ticket based on category and SOP database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string", "description": "Unique ticket ID"},
                        "category": {
                            "type": "string",
                            "enum": ["network", "hardware", "software", "account", "email"],
                            "description": "Ticket category from classifier",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed ticket description",
                        },
                    },
                    "required": ["ticket_id", "category", "description"],
                },
            },
            {
                "name": "twisterlab_mcp_resolve_ticket",
                "description": "(alias) Get resolution steps for a ticket based on category and SOP database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string", "description": "Unique ticket ID"},
                        "category": {"type": "string", "enum": ["network", "hardware", "software", "account", "email"]},
                        "description": {"type": "string", "description": "Detailed ticket description"},
                    },
                    "required": ["ticket_id", "category", "description"],
                },
            },
            {
                "name": "monitor_system_health",
                "description": "Check TwisterLab system health (CPU, RAM, disk, Docker services)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Include detailed metrics (default: false)",
                        }
                    },
                },
            },
            {
                "name": "create_backup",
                "description": "Create backup of database and configuration files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "backup_type": {
                            "type": "string",
                            "enum": ["full", "incremental", "database_only", "config_only"],
                            "description": "Type of backup to create",
                        }
                    },
                    "required": ["backup_type"],
                },
            },
            {
                "name": "sync_cache_db",
                "description": "Synchronize Redis cache with PostgreSQL database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": ["cache_to_db", "db_to_cache", "bidirectional"],
                            "description": "Sync direction",
                        }
                    },
                },
            },
            {
                "name": "twisterlab_mcp_sync_cache",
                "description": "(alias) Synchronize Redis cache with PostgreSQL database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": ["cache_to_db", "db_to_cache", "bidirectional"],
                            "description": "Sync direction",
                        }
                    },
                },
            },
        ]

        logger.info(f"Listing {len(tools)} tools")
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    async def _handle_tools_call(self, request_id: int, params: Dict) -> Dict:
        """Execute tool call via TwisterLab agents"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call: {tool_name} | Args: {arguments}")

        try:
            # Route to appropriate agent
            if tool_name == "classify_ticket" or tool_name == "twisterlab_mcp_classify_ticket":
                result = await self.agents["classifier"].execute(
                    {"ticket_text": arguments.get("ticket_text", "")}
                )

            elif tool_name == "resolve_ticket" or tool_name == "twisterlab_mcp_resolve_ticket":
                result = await self.agents["resolver"].execute(
                    {
                        "ticket_id": arguments.get("ticket_id", ""),
                        "category": arguments.get("category", ""),
                        "description": arguments.get("description", ""),
                    }
                )

            elif tool_name == "monitor_system_health":
                result = await self.agents["monitoring"].execute(
                    {"detailed": arguments.get("detailed", False)}
                )

            elif tool_name == "create_backup":
                result = await self.agents["backup"].execute(
                    {"backup_type": arguments.get("backup_type", "full")}
                )

            elif tool_name == "sync_cache_db" or tool_name == "twisterlab_mcp_sync_cache":
                result = await self.agents["sync"].execute(
                    {"direction": arguments.get("direction", "bidirectional")}
                )

            else:
                logger.warning(f"Unknown tool: {tool_name}")
                return self._error_response(request_id, -32602, f"Unknown tool: {tool_name}")

            # Format result for MCP
            result_text = json.dumps(result, indent=2, ensure_ascii=False)
            logger.info(f"Tool {tool_name} executed successfully")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": result_text}],
                    "isError": result.get("status") == "error",
                },
            }

        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return self._error_response(request_id, -32603, f"Tool execution failed: {str(e)}")

    async def _handle_resources_list(self, request_id: int) -> Dict:
        """List available resources"""
        resources = [
            {
                "uri": "twisterlab://system/health",
                "name": "System Health",
                "description": "Real-time TwisterLab system health metrics",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://agents/status",
                "name": "Agent Status",
                "description": "Status of all TwisterLab agents",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://config",
                "name": "Configuration",
                "description": "Current TwisterLab configuration",
                "mimeType": "application/json",
            },
        ]

        logger.info(f"Listing {len(resources)} resources")
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": resources}}

    async def _handle_resources_read(self, request_id: int, params: Dict) -> Dict:
        """Read resource content"""
        uri = params.get("uri", "")
        logger.info(f"Reading resource: {uri}")

        try:
            if uri == "twisterlab://system/health":
                health = await self.agents["monitoring"].execute({})
                content = json.dumps(health, indent=2)

            elif uri == "twisterlab://agents/status":
                status = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agents": {
                        name: {"name": agent.name, "status": "operational"}
                        for name, agent in self.agents.items()
                    },
                    "total_agents": len(self.agents),
                }
                content = json.dumps(status, indent=2)

            elif uri == "twisterlab://config":
                config = {
                    "server": self.server_info,
                    "protocol": self.protocol_version,
                    "agents_loaded": list(self.agents.keys()),
                    "capabilities": ["tools", "resources", "prompts"],
                }
                content = json.dumps(config, indent=2)

            else:
                logger.warning(f"Unknown resource: {uri}")
                return self._error_response(request_id, -32602, f"Unknown resource: {uri}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [{"uri": uri, "mimeType": "application/json", "text": content}]
                },
            }

        except Exception as e:
            logger.error(f"Resource read failed: {e}", exc_info=True)
            return self._error_response(request_id, -32603, f"Resource read failed: {str(e)}")

    async def _handle_prompts_list(self, request_id: int) -> Dict:
        """List available prompts"""
        prompts = [
            {
                "name": "classify_it_ticket",
                "description": "Classify an IT helpdesk ticket",
                "arguments": [
                    {
                        "name": "ticket",
                        "description": "The ticket text to classify",
                        "required": True,
                    }
                ],
            },
            {
                "name": "resolve_network_issue",
                "description": "Get steps to resolve common network issues",
                "arguments": [
                    {
                        "name": "issue_description",
                        "description": "Description of the network issue",
                        "required": True,
                    }
                ],
            },
        ]

        logger.info(f"Listing {len(prompts)} prompts")
        return {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": prompts}}

    async def _handle_prompts_get(self, request_id: int, params: Dict) -> Dict:
        """Get prompt content"""
        prompt_name = params.get("name", "")
        arguments = params.get("arguments", {})

        logger.info(f"Getting prompt: {prompt_name}")

        if prompt_name == "classify_it_ticket":
            ticket = arguments.get("ticket", "")
            prompt_text = f"""Classify the following IT helpdesk ticket into one of these categories:
- network: WiFi, VPN, connectivity issues
- hardware: PC, printer, monitor, peripherals
- software: Application crashes, installations, updates
- account: Passwords, permissions, access issues
- email: Outlook, delivery, spam issues

Ticket: {ticket}

Provide the category and confidence score (0-1)."""

        elif prompt_name == "resolve_network_issue":
            issue = arguments.get("issue_description", "")
            prompt_text = f"""Provide troubleshooting steps for this network issue:

Issue: {issue}

Steps should be:
1. Quick diagnosis
2. Common fixes
3. Advanced troubleshooting
4. Escalation criteria"""

        else:
            return self._error_response(request_id, -32602, f"Unknown prompt: {prompt_name}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "description": f"Prompt for {prompt_name}",
                "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}],
            },
        }

    def _error_response(self, request_id: int, code: int, message: str) -> Dict:
        """Create JSON-RPC error response"""
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    async def run(self):
        """Main event loop - read from stdin, write to stdout"""
        logger.info("=" * 60)
        logger.info("MCP Server for Continue IDE starting...")
        logger.info(f"Server: {self.server_info['name']} v{self.server_info['version']}")
        logger.info(f"Protocol: MCP {self.protocol_version}")
        logger.info(f"Agents loaded: {', '.join(self.agents.keys())}")
        logger.info("=" * 60)

        while True:
            try:
                # Read JSON-RPC request from stdin (one line = one request)
                line = sys.stdin.readline()
                if not line:
                    logger.info("EOF received, shutting down...")
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)

                # Handle request
                response = await self.handle_request(request)

                # Write response to stdout (must be one line)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                error_response = self._error_response(None, -32700, "Parse error")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt, shutting down...")
                break

            except Exception as e:
                logger.error(f"Server error: {e}", exc_info=True)
                error_response = self._error_response(None, -32603, f"Internal error: {str(e)}")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()


async def main():
    """Entry point"""
    try:
        server = MCPServerContinue()
        await server.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
