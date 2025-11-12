"""
Native MCP Server for TwisterLab Agents (Mode 2).

Standard Model Context Protocol server using stdio transport.
Designed for Claude Desktop and other native MCP clients.

Protocol: https://modelcontextprotocol.io/
Transport: stdio (JSON-RPC 2.0)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.mcp.mcp_router import MCPRouter

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Native MCP Server implementing the Model Context Protocol.

    Supports:
    - tools/* - Callable agent operations
    - resources/* - Read-only data access
    - prompts/* - Template prompts

    Transport: stdio (JSON-RPC 2.0)
    """

    def __init__(self):
        """Initialize MCP server."""
        self.router = MCPRouter()
        self.capabilities = {
            "tools": True,
            "resources": True,
            "prompts": True,
        }

        # Available tools (exposed agent operations)
        self.tools = [
            {
                "name": "monitor_system_health",
                "description": "Check system health (CPU, RAM, disk, Docker services)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_docker": {
                            "type": "boolean",
                            "description": "Include Docker service status",
                            "default": True,
                        },
                    },
                },
            },
            {
                "name": "create_backup",
                "description": "Create PostgreSQL database backup",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "compression": {
                            "type": "string",
                            "enum": ["gzip", "none"],
                            "default": "gzip",
                        },
                    },
                },
            },
            {
                "name": "sync_cache_db",
                "description": "Synchronize Redis cache with PostgreSQL database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force": {
                            "type": "boolean",
                            "description": "Force sync even if cache is fresh",
                            "default": False,
                        },
                    },
                },
            },
            {
                "name": "classify_ticket",
                "description": "Classify IT helpdesk ticket using LLM",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_text": {
                            "type": "string",
                            "description": "Ticket description text",
                        },
                    },
                    "required": ["ticket_text"],
                },
            },
            {
                "name": "resolve_ticket",
                "description": "Execute SOP to resolve classified ticket",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier",
                        },
                        "category": {
                            "type": "string",
                            "description": "Ticket category from classifier",
                        },
                    },
                    "required": ["ticket_id", "category"],
                },
            },
        ]

        # Available resources (read-only data)
        self.resources = [
            {
                "uri": "twisterlab://system/health",
                "name": "System Health Status",
                "description": "Current system health metrics",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://agents/status",
                "name": "Agent Status",
                "description": "All autonomous agent statuses",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://audit/mcp-log",
                "name": "MCP Communication Audit Log",
                "description": "Audit trail of MCP communications",
                "mimeType": "application/json",
            },
        ]

        # Available prompts (templates)
        self.prompts = [
            {
                "name": "classify_it_ticket",
                "description": "Template for IT ticket classification",
                "arguments": [
                    {
                        "name": "ticket_description",
                        "description": "The IT issue description",
                        "required": True,
                    },
                ],
            },
            {
                "name": "resolve_network_issue",
                "description": "SOP prompt for network troubleshooting",
                "arguments": [
                    {
                        "name": "error_message",
                        "description": "Network error details",
                        "required": True,
                    },
                ],
            },
        ]

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle initialize request (JSON-RPC method: initialize).

        Returns server capabilities and metadata.
        """
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "twisterlab-mcp",
                "version": "1.0.0",
            },
            "capabilities": self.capabilities,
        }

    async def handle_tools_list(self) -> Dict[str, Any]:
        """
        Handle tools/list request.

        Returns available agent operations as tools.
        """
        return {"tools": self.tools}

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request.

        Execute agent operation via MCP router.
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"MCP Tool Call: {tool_name} with args {arguments}")

        # Map tool calls to agent operations
        try:
            if tool_name == "monitor_system_health":
                result = await self.router.route_to_mcp(
                    agent_name="MCP-Client",
                    mcp_name="monitoring_mcp",
                    operation="health_check",
                    params=arguments,
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2),
                        }
                    ],
                }

            elif tool_name == "create_backup":
                result = await self.router.route_to_mcp(
                    agent_name="MCP-Client",
                    mcp_name="backup_mcp",
                    operation="backup_database",
                    params=arguments,
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Backup created: {result.get('backup_size')}",
                        }
                    ],
                }

            elif tool_name == "sync_cache_db":
                result = await self.router.route_to_mcp(
                    agent_name="MCP-Client",
                    mcp_name="sync_mcp",
                    operation="sync_cache_database",
                    params=arguments,
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Synced {result.get('records_synced')} records",
                        }
                    ],
                }

            elif tool_name == "classify_ticket":
                # Route to classifier agent (placeholder)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "category": "network",
                                "confidence": 0.95,
                                "ticket": arguments.get("ticket_text"),
                            }, indent=2),
                        }
                    ],
                }

            elif tool_name == "resolve_ticket":
                # Route to resolver agent (placeholder)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "resolved",
                                "ticket_id": arguments.get("ticket_id"),
                                "sop_executed": "network_diagnostic_v1",
                            }, indent=2),
                        }
                    ],
                }

            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {tool_name}",
                        }
                    ],
                    "isError": True,
                }

        except Exception as e:
            logger.error(f"Tool call failed: {tool_name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool execution error: {str(e)}",
                    }
                ],
                "isError": True,
            }

    async def handle_resources_list(self) -> Dict[str, Any]:
        """
        Handle resources/list request.

        Returns available read-only resources.
        """
        return {"resources": self.resources}

    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resources/read request.

        Return resource data.
        """
        uri = params.get("uri")

        logger.info(f"MCP Resource Read: {uri}")

        if uri == "twisterlab://system/health":
            # Get current system health
            health_data = await self.router.route_to_mcp(
                agent_name="MCP-Client",
                mcp_name="monitoring_mcp",
                operation="health_check",
                params={},
            )
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(health_data, indent=2),
                    }
                ],
            }

        elif uri == "twisterlab://agents/status":
            # Get agent statuses
            status_data = await self.router.route_to_mcp(
                agent_name="MCP-Client",
                mcp_name="maestro_mcp",
                operation="get_all_agent_states",
                params={},
            )
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(status_data, indent=2),
                    }
                ],
            }

        elif uri == "twisterlab://audit/mcp-log":
            # Get MCP audit log
            audit_log = self.router.get_audit_log()
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(audit_log, indent=2),
                    }
                ],
            }

        else:
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": f"Resource not found: {uri}",
                    }
                ],
                "isError": True,
            }

    async def handle_prompts_list(self) -> Dict[str, Any]:
        """
        Handle prompts/list request.

        Returns available prompt templates.
        """
        return {"prompts": self.prompts}

    async def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle prompts/get request.

        Return rendered prompt template.
        """
        name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"MCP Prompt Get: {name}")

        if name == "classify_it_ticket":
            ticket_desc = arguments.get("ticket_description", "")
            prompt = f"""Classify this IT helpdesk ticket into one of these categories:
- network (connectivity, WiFi, VPN issues)
- hardware (PC, printer, monitor problems)
- software (application crashes, installation issues)
- access (password reset, permissions)
- email (Outlook, mail delivery issues)

Ticket: {ticket_desc}

Provide:
1. Category (one of the above)
2. Confidence score (0-1)
3. Suggested priority (low/medium/high)
4. Recommended first action
"""
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": prompt,
                        },
                    }
                ],
            }

        elif name == "resolve_network_issue":
            error_msg = arguments.get("error_message", "")
            prompt = f"""Network Troubleshooting SOP

Error: {error_msg}

Execute these diagnostic steps:
1. Check physical connections (cable, WiFi signal)
2. Verify IP configuration (ipconfig /all)
3. Test connectivity (ping 8.8.8.8, ping gateway)
4. Check DNS resolution (nslookup google.com)
5. Verify firewall rules
6. Test with alternative network (mobile hotspot)

Document findings and recommend solution.
"""
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": prompt,
                        },
                    }
                ],
            }

        else:
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Prompt not found: {name}",
                        },
                    }
                ],
                "isError": True,
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle JSON-RPC request.

        Routes to appropriate handler based on method.
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            # Route to handlers
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list()
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list()
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "prompts/list":
                result = await self.handle_prompts_list()
            elif method == "prompts/get":
                result = await self.handle_prompts_get(params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                }

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Request handler error: {method}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            }

    async def run_stdio(self):
        """
        Run MCP server with stdio transport.

        Reads JSON-RPC requests from stdin, writes responses to stdout.
        """
        logger.info("TwisterLab MCP Server starting (stdio transport)")

        async with self.router:
            while True:
                try:
                    # Read line from stdin
                    line = await asyncio.get_event_loop().run_in_executor(
                        None, sys.stdin.readline
                    )

                    if not line:
                        # EOF reached
                        break

                    # Parse JSON-RPC request
                    request = json.loads(line.strip())

                    # Handle request
                    response = await self.handle_request(request)

                    # Write response to stdout
                    print(json.dumps(response), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                        },
                    }
                    print(json.dumps(error_response), flush=True)

                except Exception as e:
                    logger.error(f"Server error: {e}", exc_info=True)
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal server error: {str(e)}",
                        },
                    }
                    print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point for MCP server."""
    # Configure logging to stderr (stdout is for JSON-RPC)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    server = MCPServer()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
