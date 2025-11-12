"""
MCP Server for Continue IDE integration (Synchronous version)
Windows-compatible version without asyncio

Usage:
    python agents/mcp/mcp_server_continue_sync.py

Protocol: MCP 2024-11-05 (Model Context Protocol)
Transport: stdio (JSON-RPC 2.0)

Mode: REAL (calls actual TwisterLab API)
"""
import json
import logging
import sys
import os
from typing import Any, Dict
from datetime import datetime, timezone

# Import httpx for API calls
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logging.warning("httpx not available - install with: pip install httpx")

# Configure logging to stderr (stdout is for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServerContinue:
    """MCP Server for Continue IDE - stdio transport"""

    def __init__(self):
        """Initialize MCP server"""
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "twisterlab-mcp-continue",
            "version": "2.0.0",  # Version 2.0 - REAL mode
            "description": "TwisterLab MCP Server for Continue IDE (REAL mode)"
        }
        
        # API configuration
        self.api_url = os.getenv("API_URL", "http://192.168.0.30:8000")
        self.api_timeout = 60.0  # 60 seconds for LLM operations
        self.mode = "REAL" if HTTPX_AVAILABLE else "MOCK"
        
        logger.info(f"Initialized: {self.server_info['name']} v{self.server_info['version']}")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"API URL: {self.api_url}")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC 2.0 request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        logger.info(f"Request: {method} (id={request_id})")

        try:
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request_id, params)
            elif method == "resources/list":
                return self._handle_resources_list(request_id)
            elif method == "resources/read":
                return self._handle_resources_read(request_id, params)
            elif method == "resources/templates/list":
                return self._handle_resources_templates_list(request_id)
            elif method == "prompts/list":
                return self._handle_prompts_list(request_id)
            elif method == "prompts/get":
                return self._handle_prompts_get(request_id, params)
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return self._error_response(request_id, -32603, str(e))

    def _handle_initialize(self, request_id: int, params: Dict) -> Dict:
        """Initialize MCP connection"""
        client = params.get("clientInfo", {}).get("name", "unknown")
        logger.info(f"Client: {client}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.protocol_version,
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
                "serverInfo": self.server_info,
            },
        }

    def _handle_tools_list(self, request_id: int) -> Dict:
        """List available tools - ALL 7 REAL TwisterLab agents"""
        tools = [
            {
                "name": "list_autonomous_agents",
                "description": "List all 7 production autonomous agents (RealMonitoring, RealBackup, RealSync, RealClassifier, RealResolver, RealDesktopCommander, RealMaestro)",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "monitor_system_health",
                "description": "RealMonitoringAgent - Check system health (CPU, RAM, disk, Docker services)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "detailed": {"type": "boolean", "description": "Include detailed metrics"}
                    }
                }
            },
            {
                "name": "create_backup",
                "description": "RealBackupAgent - Create PostgreSQL/Redis/config backup with disaster recovery",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "backup_type": {"type": "string", "enum": ["full", "incremental", "config_only"]}
                    }
                }
            },
            {
                "name": "sync_cache",
                "description": "RealSyncAgent - Synchronize Redis cache with PostgreSQL database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force": {"type": "boolean", "description": "Force full resync"}
                    }
                }
            },
            {
                "name": "classify_ticket",
                "description": "RealClassifierAgent - Classify IT helpdesk ticket using Ollama LLM",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_text": {"type": "string", "description": "Ticket description"}
                    },
                    "required": ["ticket_text"]
                }
            },
            {
                "name": "resolve_ticket",
                "description": "RealResolverAgent - Execute SOP resolution steps for ticket category",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "category": {"type": "string", "enum": ["network", "hardware", "software", "account", "email"]},
                        "description": {"type": "string"}
                    },
                    "required": ["category", "description"]
                }
            },
            {
                "name": "execute_desktop_command",
                "description": "RealDesktopCommanderAgent - Execute system commands on remote machines (PowerShell/Bash)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"},
                        "target_host": {"type": "string", "description": "Target hostname/IP"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds"}
                    },
                    "required": ["command", "target_host"]
                }
            }
        ]

        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    def _handle_tools_call(self, request_id: int, params: Dict) -> Dict:
        """Execute tool call - REAL API mode"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool: {tool_name} | Args: {arguments} | Mode: {self.mode}")

        # Call REAL API if available
        if self.mode == "REAL" and HTTPX_AVAILABLE:
            try:
                result = self._call_api(tool_name, arguments)
            except Exception as api_error:
                logger.error(f"API call failed: {api_error}, using fallback")
                result = self._get_mock_response(tool_name, arguments)
        else:
            # Fallback to MOCK if httpx not available
            result = self._get_mock_response(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }
        }
    
    def _call_api(self, tool_name: str, arguments: Dict) -> Dict:
        """Call real TwisterLab API"""
        endpoint_map = {
            "list_autonomous_agents": "/v1/mcp/tools/list_autonomous_agents",
            "monitor_system_health": "/v1/mcp/tools/monitor_system_health",
            "create_backup": "/v1/mcp/tools/create_backup",
            "sync_cache": "/v1/mcp/tools/sync_cache",
            "classify_ticket": "/v1/mcp/tools/classify_ticket",
            "resolve_ticket": "/v1/mcp/tools/resolve_ticket",
            "execute_desktop_command": "/v1/mcp/tools/execute_desktop_command"
        }
        
        endpoint = endpoint_map.get(tool_name)
        if not endpoint:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Map arguments to API format
        if tool_name == "list_autonomous_agents":
            payload = {}  # No arguments needed
        elif tool_name == "classify_ticket":
            payload = {
                "description": arguments.get("ticket_text", ""),
                "priority": arguments.get("priority")
            }
        elif tool_name == "resolve_ticket":
            payload = {
                "ticket_id": int(arguments.get("ticket_id", 0)) if arguments.get("ticket_id") else None,
                "category": arguments.get("category", "network"),
                "description": arguments.get("description")
            }
        elif tool_name == "monitor_system_health":
            payload = {
                "detailed": arguments.get("detailed", False)
            }
        elif tool_name == "create_backup":
            payload = {
                "backup_type": arguments.get("backup_type", "full")
            }
        elif tool_name == "sync_cache":
            payload = {
                "force": arguments.get("force", False)
            }
        elif tool_name == "execute_desktop_command":
            payload = {
                "command": arguments.get("command"),
                "target_host": arguments.get("target_host"),
                "timeout": arguments.get("timeout", 30)
            }
        else:
            payload = arguments
        
        # Call API
        url = f"{self.api_url}{endpoint}"
        logger.info(f"Calling API: POST {url}")
        
        with httpx.Client(timeout=self.api_timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            api_response = response.json()
        
        logger.info(f"API response status: {api_response.get('status')}")
        
        # Extract data from MCPResponse format
        if api_response.get("status") == "ok":
            return {
                "status": "success",
                "mode": "REAL",
                **api_response.get("data", {})
            }
        else:
            return {
                "status": "error",
                "mode": "REAL",
                "error": api_response.get("error", "Unknown error")
            }
    
    def _get_mock_response(self, tool_name: str, arguments: Dict) -> Dict:
        """Fallback mock responses"""
        # Mock responses (used when API is unreachable)
        if tool_name == "list_autonomous_agents":
            result = {
                "status": "success",
                "mode": "MOCK",
                "agents": [
                    {
                        "name": "RealMonitoringAgent",
                        "module": "agents.real.real_monitoring_agent",
                        "description": "System health monitoring (CPU, RAM, disk, Docker services)",
                        "status": "operational"
                    },
                    {
                        "name": "RealBackupAgent",
                        "module": "agents.real.real_backup_agent",
                        "description": "Automated backups with disaster recovery (PostgreSQL, Redis, configs)",
                        "status": "operational"
                    },
                    {
                        "name": "RealSyncAgent",
                        "module": "agents.real.real_sync_agent",
                        "description": "Cache/Database synchronization (Redis ↔ PostgreSQL)",
                        "status": "operational"
                    },
                    {
                        "name": "RealClassifierAgent",
                        "module": "agents.real.real_classifier_agent",
                        "description": "Ticket classification using Ollama LLM (llama3.2:1b)",
                        "status": "operational"
                    },
                    {
                        "name": "RealResolverAgent",
                        "module": "agents.real.real_resolver_agent",
                        "description": "SOP-based ticket resolution (network, hardware, software, account, email)",
                        "status": "operational"
                    },
                    {
                        "name": "RealDesktopCommanderAgent",
                        "module": "agents.real.real_desktop_commander_agent",
                        "description": "Remote system command execution (PowerShell, Bash, SSH)",
                        "status": "operational"
                    },
                    {
                        "name": "RealMaestroAgent",
                        "module": "agents.real.real_maestro_agent",
                        "description": "Workflow orchestration and load balancing (agent coordination)",
                        "status": "operational"
                    }
                ],
                "total": 7,
                "note": "⚠️ Mock response - API service offline. Real agents defined in agents/real/"
            }
        
        elif tool_name == "classify_ticket":
            ticket_text = arguments.get("ticket_text", "")
            result = {
                "status": "success",
                "agent": "RealClassifierAgent",
                "category": "network" if "wifi" in ticket_text.lower() or "network" in ticket_text.lower() else "software",
                "confidence": 0.85,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline"
            }

        elif tool_name == "resolve_ticket":
            category = arguments.get("category", "unknown")
            result = {
                "status": "success",
                "agent": "RealResolverAgent",
                "resolution_steps": [
                    f"Step 1: Verify {category} issue symptoms",
                    f"Step 2: Check {category} configuration",
                    f"Step 3: Apply standard {category} troubleshooting",
                    f"Step 4: Escalate if unresolved"
                ],
                "estimated_time": "15-30 minutes",
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline"
            }

        elif tool_name == "monitor_system_health":
            result = {
                "status": "warning",
                "agent": "RealMonitoringAgent",
                "services": {
                    "postgres": "running",
                    "redis": "running",
                    "api": "down (0/1 replicas)",
                    "ollama": "running"
                },
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline"
            }

        elif tool_name == "create_backup":
            result = {
                "status": "success",
                "agent": "RealBackupAgent",
                "backup_location": "/backups/mock_backup.tar.gz",
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline"
            }
        
        elif tool_name == "sync_cache":
            result = {
                "status": "success",
                "agent": "RealSyncAgent",
                "synced_keys": 42,
                "duration_ms": 150,
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline"
            }
        
        elif tool_name == "execute_desktop_command":
            command = arguments.get("command", "unknown")
            target = arguments.get("target_host", "unknown")
            result = {
                "status": "success",
                "agent": "RealDesktopCommanderAgent",
                "command": command,
                "target_host": target,
                "output": f"Mock output for: {command}",
                "exit_code": 0,
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline. Real execution disabled."
            }

        else:
            result = {
                "status": "error",
                "mode": "MOCK",
                "error": f"Unknown tool: {tool_name}"
            }
        
        return result

    def _handle_resources_list(self, request_id: int) -> Dict:
        """List available resources"""
        resources = [
            {
                "uri": "twisterlab://system/health",
                "name": "System Health",
                "description": "Current TwisterLab system status",
                "mimeType": "application/json"
            },
            {
                "uri": "twisterlab://agents/status",
                "name": "Agent Status",
                "description": "Status of all agents",
                "mimeType": "application/json"
            }
        ]

        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": resources}}

    def _handle_resources_read(self, request_id: int, params: Dict) -> Dict:
        """Read resource content"""
        uri = params.get("uri", "")

        if uri == "twisterlab://system/health":
            content = json.dumps({
                "status": "degraded",
                "api_service": "offline",
                "database": "online",
                "cache": "online",
                "llm": "online"
            }, indent=2)

        elif uri == "twisterlab://agents/status":
            content = json.dumps({
                "agents": ["classifier", "resolver", "monitoring", "backup", "sync"],
                "status": "mock_mode",
                "note": "API service offline - using mock responses"
            }, indent=2)

        else:
            return self._error_response(request_id, -32602, f"Unknown resource: {uri}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": content
                }]
            }
        }

    def _handle_resources_templates_list(self, request_id: int) -> Dict:
        """List available resource templates (optional MCP feature)"""
        # Return empty list - we don't use resource templates
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resourceTemplates": []
            }
        }

    def _handle_prompts_list(self, request_id: int) -> Dict:
        """List available prompts (disabled - use tools instead)"""
        # Return empty list to force Continue to use tools, not prompts
        prompts = []

        return {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": prompts}}

    def _handle_prompts_get(self, request_id: int, params: Dict) -> Dict:
        """Get prompt content"""
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name == "classify_it_ticket":
            ticket = args.get("ticket", "")
            text = f"Classify this IT ticket:\n\n{ticket}\n\nCategories: network, hardware, software, account, email"
        elif name == "resolve_network_issue":
            issue = args.get("issue", "")
            text = f"Troubleshooting steps for:\n\n{issue}\n\n1. Diagnosis\n2. Quick fixes\n3. Advanced steps"
        else:
            return self._error_response(request_id, -32602, f"Unknown prompt: {name}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "description": f"Prompt: {name}",
                "messages": [{"role": "user", "content": {"type": "text", "text": text}}]
            }
        }

    def _error_response(self, request_id: int, code: int, message: str) -> Dict:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message}
        }

    def run(self):
        """Main event loop - read stdin, write stdout"""
        logger.info("="*60)
        logger.info(f"MCP Server Starting: {self.server_info['name']}")
        logger.info(f"Protocol: MCP {self.protocol_version}")
        logger.info("="*60)

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    logger.info("EOF - shutting down")
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)
                response = self.handle_request(request)

                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error = self._error_response(None, -32700, "Parse error")
                sys.stdout.write(json.dumps(error) + "\n")
                sys.stdout.flush()

            except KeyboardInterrupt:
                logger.info("Interrupted")
                break

            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                error = self._error_response(None, -32603, str(e))
                sys.stdout.write(json.dumps(error) + "\n")
                sys.stdout.flush()


def main():
    """Entry point"""
    try:
        server = MCPServerContinue()
        server.run()
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


