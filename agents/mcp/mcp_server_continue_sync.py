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
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

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
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MCPServerContinue:
    """MCP Server for Continue IDE - stdio transport"""

    def __init__(self):
        """Initialize MCP server"""
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "twisterlab-mcp-continue",
            "version": "2.1.0",  # Version 2.1 - Enhanced error handling & API health checks
            "description": "TwisterLab MCP Server for Continue IDE (Enhanced)",
        }

        # API configuration
        self.api_url = os.getenv("API_URL", "http://192.168.0.30:8000")
        self.api_timeout = 60.0  # 60 seconds for LLM operations
        self.mode = "REAL" if HTTPX_AVAILABLE else "MOCK"

        # Test API connectivity on startup
        self.api_available = self._test_api_connectivity()

        logger.info(
            f"Initialized: {self.server_info['name']} v{self.server_info['version']}"
        )
        logger.info(f"Mode: {self.mode}")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"API Available: {self.api_available}")

    def _test_api_connectivity(self) -> bool:
        """Test API connectivity on startup"""
        if not HTTPX_AVAILABLE:
            return False

        try:
            # Test with a simple health check endpoint
            health_url = f"{self.api_url}/health"
            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"API connectivity test failed: {e}")
            return False

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
                return self._error_response(
                    request_id, -32601, f"Method not found: {method}"
                )

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._error_response(request_id, -32700, f"Invalid JSON: {e}")
        except KeyError as e:
            logger.error(f"Missing required parameter: {e}")
            return self._error_response(request_id, -32602, f"Missing parameter: {e}")
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return self._error_response(request_id, -32602, str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")

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
                "name": "twisterlab_mcp_list_autonomous_agents",
                "description": "List all 7 production autonomous agents (RealMonitoring, RealBackup, RealSync, RealClassifier, RealResolver, RealDesktopCommander, RealMaestro)",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "monitor_system_health",
                "description": "RealMonitoringAgent - Check system health (CPU, RAM, disk, Docker services)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Include detailed metrics",
                        }
                    },
                },
            },
            {
                "name": "create_backup",
                "description": "RealBackupAgent - Create PostgreSQL/Redis/config backup with disaster recovery",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "backup_type": {
                            "type": "string",
                            "enum": ["full", "incremental", "config_only"],
                        }
                    },
                },
            },
            {
                "name": "sync_cache",
                "description": "RealSyncAgent - Synchronize Redis cache with PostgreSQL database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force": {"type": "boolean", "description": "Force full resync"}
                    },
                },
            },
            {
                "name": "classify_ticket",
                "description": "RealClassifierAgent - Classify IT helpdesk ticket using Ollama LLM",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_text": {
                            "type": "string",
                            "description": "Ticket description",
                        }
                    },
                    "required": ["ticket_text"],
                },
            },
            {
                "name": "resolve_ticket",
                "description": "RealResolverAgent - Execute SOP resolution steps for ticket category",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "network",
                                "hardware",
                                "software",
                                "account",
                                "email",
                            ],
                        },
                        "description": {"type": "string"},
                    },
                    "required": ["category", "description"],
                },
            },
            {
                "name": "execute_desktop_command",
                "description": "RealDesktopCommanderAgent - Execute system commands on remote machines (PowerShell/Bash)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute",
                        },
                        "target_host": {
                            "type": "string",
                            "description": "Target hostname/IP",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds",
                        },
                    },
                    "required": ["command", "target_host"],
                },
            },
        ]

        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    def _handle_tools_call(self, request_id: int, params: Dict) -> Dict:
        """Execute tool call - REAL API mode"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool: {tool_name} | Args: {arguments} | Mode: {self.mode}")

        # Call REAL API if available
        if self.mode == "REAL" and HTTPX_AVAILABLE and self.api_available:
            try:
                result = self._call_api(tool_name, arguments)
            except Exception as api_error:
                logger.error(f"API call failed: {api_error}, using fallback")
                result = self._get_mock_response(tool_name, arguments)
        else:
            # Fallback to MOCK if httpx not available or API not reachable
            result = self._get_mock_response(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            },
        }

    def _call_api(self, tool_name: str, arguments: Dict) -> Dict:
        """Call real TwisterLab API"""
        endpoint_map = {
            "twisterlab_mcp_list_autonomous_agents": "/v1/mcp/tools/list_autonomous_agents",
            "monitor_system_health": "/v1/mcp/tools/monitor_system_health",
            "create_backup": "/v1/mcp/tools/create_backup",
            "sync_cache": "/v1/mcp/tools/sync_cache",
            "classify_ticket": "/v1/mcp/tools/classify_ticket",
            "resolve_ticket": "/v1/mcp/tools/resolve_ticket",
            "execute_desktop_command": "/v1/mcp/tools/execute_desktop_command",
        }

        endpoint = endpoint_map.get(tool_name)
        if not endpoint:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Map arguments to API format
        if tool_name == "twisterlab_mcp_list_autonomous_agents":
            payload = {}  # No arguments needed
        elif tool_name == "classify_ticket":
            payload = {
                "description": arguments.get("ticket_text", ""),
                "priority": arguments.get("priority"),
            }
        elif tool_name == "resolve_ticket":
            payload = {
                "ticket_id": int(arguments.get("ticket_id", 0))
                if arguments.get("ticket_id")
                else None,
                "category": arguments.get("category", "network"),
                "description": arguments.get("description"),
            }
        elif tool_name == "monitor_system_health":
            payload = {"detailed": arguments.get("detailed", False)}
        elif tool_name == "create_backup":
            payload = {"backup_type": arguments.get("backup_type", "full")}
        elif tool_name == "sync_cache":
            payload = {"force": arguments.get("force", False)}
        elif tool_name == "execute_desktop_command":
            payload = {
                "command": arguments.get("command"),
                "target_host": arguments.get("target_host"),
                "timeout": arguments.get("timeout", 30),
            }
        else:
            payload = arguments

        # Call API
        url = f"{self.api_url}{endpoint}"
        logger.info(f"Calling API: POST {url}")

        try:
            with httpx.Client(timeout=self.api_timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                api_response = response.json()
        except httpx.TimeoutException as e:
            logger.error(f"API timeout: {e}")
            raise ValueError(f"API timeout after {self.api_timeout}s")
        except httpx.HTTPStatusError as e:
            logger.error(
                f"API HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise ValueError(
                f"API returned {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"API request error: {e}")
            raise ValueError(f"Failed to connect to API: {e}")
        except ValueError as e:
            logger.error(f"API JSON parsing error: {e}")
            raise ValueError(f"Invalid API response format: {e}")

        logger.info(f"API response status: {api_response.get('status')}")

        # Extract data from MCPResponse format
        if api_response.get("status") == "ok":
            return {"status": "success", "mode": "REAL", **api_response.get("data", {})}
        else:
            return {
                "status": "error",
                "mode": "REAL",
                "error": api_response.get("error", "Unknown error"),
            }

    def _get_mock_response(self, tool_name: str, arguments: Dict) -> Dict:
        """Fallback mock responses"""
        # Mock responses (used when API is unreachable)
        if tool_name == "twisterlab_mcp_list_autonomous_agents":
            result = {
                "status": "success",
                "mode": "MOCK",
                "agents": [
                    {
                        "name": "RealMonitoringAgent",
                        "module": "agents.real.real_monitoring_agent",
                        "description": "System health monitoring (CPU, RAM, disk, Docker services)",
                        "status": "operational",
                    },
                    {
                        "name": "RealBackupAgent",
                        "module": "agents.real.real_backup_agent",
                        "description": "Automated backups with disaster recovery (PostgreSQL, Redis, configs)",
                        "status": "operational",
                    },
                    {
                        "name": "RealSyncAgent",
                        "module": "agents.real.real_sync_agent",
                        "description": "Cache/Database synchronization (Redis ↔ PostgreSQL)",
                        "status": "operational",
                    },
                    {
                        "name": "RealClassifierAgent",
                        "module": "agents.real.real_classifier_agent",
                        "description": "Ticket classification using Ollama LLM (llama3.2:1b)",
                        "status": "operational",
                    },
                    {
                        "name": "RealResolverAgent",
                        "module": "agents.real.real_resolver_agent",
                        "description": "SOP-based ticket resolution (network, hardware, software, account, email)",
                        "status": "operational",
                    },
                    {
                        "name": "RealDesktopCommanderAgent",
                        "module": "agents.real.real_desktop_commander_agent",
                        "description": "Remote system command execution (PowerShell, Bash, SSH)",
                        "status": "operational",
                    },
                    {
                        "name": "RealMaestroAgent",
                        "module": "agents.real.real_maestro_agent",
                        "description": "Workflow orchestration and load balancing (agent coordination)",
                        "status": "operational",
                    },
                ],
                "total": 7,
                "note": "⚠️ Mock response - API service offline. Real agents defined in agents/real/",
            }

        elif tool_name == "classify_ticket":
            ticket_text = arguments.get("ticket_text", "")
            result = {
                "status": "success",
                "agent": "RealClassifierAgent",
                "category": "network"
                if "wifi" in ticket_text.lower() or "network" in ticket_text.lower()
                else "software",
                "confidence": 0.85,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline",
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
                    "Step 4: Escalate if unresolved",
                ],
                "estimated_time": "15-30 minutes",
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline",
            }

        elif tool_name == "monitor_system_health":
            result = {
                "status": "warning",
                "agent": "RealMonitoringAgent",
                "services": {
                    "postgres": "running",
                    "redis": "running",
                    "api": "down (0/1 replicas)",
                    "ollama": "running",
                },
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline",
            }

        elif tool_name == "create_backup":
            result = {
                "status": "success",
                "agent": "RealBackupAgent",
                "backup_location": "/backups/mock_backup.tar.gz",
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline",
            }

        elif tool_name == "sync_cache":
            result = {
                "status": "success",
                "agent": "RealSyncAgent",
                "synced_keys": 42,
                "duration_ms": 150,
                "mode": "MOCK",
                "note": "⚠️ Mock response - API service offline",
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
                "note": "⚠️ Mock response - API service offline. Real execution disabled.",
            }

        else:
            result = {
                "status": "error",
                "mode": "MOCK",
                "error": f"Unknown tool: {tool_name}",
            }

        return result

    def _handle_resources_list(self, request_id: int) -> Dict:
        """List available resources"""
        resources = [
            {
                "uri": "twisterlab://agents/registry",
                "name": "Agents Registry",
                "description": "Complete list of all 7 real autonomous agents with module paths and capabilities",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://system/health",
                "name": "System Health",
                "description": "Current TwisterLab system status",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://agents/status",
                "name": "Agent Status",
                "description": "Status of all agents",
                "mimeType": "application/json",
            },
            {
                "uri": "twisterlab://docs/quickstart",
                "name": "Quick Start Guide",
                "description": "How to use TwisterLab agents via MCP",
                "mimeType": "text/markdown",
            },
        ]

        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": resources}}

    def _handle_resources_read(self, request_id: int, params: Dict) -> Dict:
        """Read resource content"""
        uri = params.get("uri", "")

        if uri == "twisterlab://agents/registry":
            content = json.dumps(
                {
                    "version": "2.0.0",
                    "total_agents": 7,
                    "base_class": "agents.base.TwisterAgent",
                    "agents": [
                        {
                            "name": "RealMonitoringAgent",
                            "module": "agents.real.real_monitoring_agent",
                            "file": "agents/real/real_monitoring_agent.py",
                            "mcp_tool": "monitor_system_health",
                            "description": "System health monitoring (CPU, RAM, disk, Docker services)",
                            "capabilities": [
                                "cpu_monitoring",
                                "ram_monitoring",
                                "disk_monitoring",
                                "docker_health",
                            ],
                            "status": "operational",
                        },
                        {
                            "name": "RealBackupAgent",
                            "module": "agents.real.real_backup_agent",
                            "file": "agents/real/real_backup_agent.py",
                            "mcp_tool": "create_backup",
                            "description": "Automated backups with disaster recovery (PostgreSQL, Redis, configs)",
                            "capabilities": [
                                "postgres_backup",
                                "redis_backup",
                                "config_backup",
                                "incremental_backup",
                            ],
                            "status": "operational",
                        },
                        {
                            "name": "RealSyncAgent",
                            "module": "agents.real.real_sync_agent",
                            "file": "agents/real/real_sync_agent.py",
                            "mcp_tool": "sync_cache",
                            "description": "Cache/Database synchronization (Redis ↔ PostgreSQL)",
                            "capabilities": [
                                "redis_sync",
                                "postgres_sync",
                                "conflict_resolution",
                            ],
                            "status": "operational",
                        },
                        {
                            "name": "RealClassifierAgent",
                            "module": "agents.real.real_classifier_agent",
                            "file": "agents/real/real_classifier_agent.py",
                            "mcp_tool": "classify_ticket",
                            "description": "Ticket classification using Ollama LLM (llama3.2:1b)",
                            "capabilities": [
                                "llm_classification",
                                "confidence_scoring",
                                "priority_assignment",
                            ],
                            "categories": [
                                "network",
                                "hardware",
                                "software",
                                "account",
                                "email",
                            ],
                            "status": "operational",
                        },
                        {
                            "name": "RealResolverAgent",
                            "module": "agents.real.real_resolver_agent",
                            "file": "agents/real/real_resolver_agent.py",
                            "mcp_tool": "resolve_ticket",
                            "description": "SOP-based ticket resolution (network, hardware, software, account, email)",
                            "capabilities": [
                                "sop_execution",
                                "troubleshooting",
                                "guided_resolution",
                            ],
                            "status": "operational",
                        },
                        {
                            "name": "RealDesktopCommanderAgent",
                            "module": "agents.real.real_desktop_commander_agent",
                            "file": "agents/real/real_desktop_commander_agent.py",
                            "mcp_tool": "execute_desktop_command",
                            "description": "Remote system command execution (PowerShell, Bash, SSH)",
                            "capabilities": [
                                "powershell_execution",
                                "bash_execution",
                                "ssh_commands",
                                "command_whitelisting",
                            ],
                            "status": "operational",
                            "security": "whitelisted_commands_only",
                        },
                        {
                            "name": "RealMaestroAgent",
                            "module": "agents.real.real_maestro_agent",
                            "file": "agents/real/real_maestro_agent.py",
                            "mcp_tool": null,
                            "description": "Workflow orchestration and load balancing (agent coordination)",
                            "capabilities": [
                                "workflow_orchestration",
                                "load_balancing",
                                "state_persistence",
                                "error_recovery",
                            ],
                            "status": "operational",
                        },
                    ],
                    "infrastructure": {
                        "database": "PostgreSQL 16",
                        "cache": "Redis 7",
                        "llm": "Ollama (llama3.2:1b, llama3:latest)",
                        "deployment": "Docker Swarm",
                        "monitoring": "Prometheus + Grafana",
                    },
                    "api_base": "http://192.168.0.30:8000",
                    "mcp_protocol": "2024-11-05",
                },
                indent=2,
            )

        elif uri == "twisterlab://system/health":
            content = json.dumps(
                {
                    "status": "degraded",
                    "api_service": "offline",
                    "database": "online",
                    "cache": "online",
                    "llm": "online",
                },
                indent=2,
            )

        elif uri == "twisterlab://agents/status":
            content = json.dumps(
                {
                    "agents": [
                        "RealMonitoring",
                        "RealBackup",
                        "RealSync",
                        "RealClassifier",
                        "RealResolver",
                        "RealDesktopCommander",
                        "RealMaestro",
                    ],
                    "status": "mock_mode",
                    "note": "API service offline - using mock responses",
                },
                indent=2,
            )

        elif uri == "twisterlab://docs/quickstart":
            content = """# TwisterLab MCP Quick Start

## Available Tools

1. **twisterlab_mcp_list_autonomous_agents** - List all 7 agents
   ```
   @mcp twisterlab_mcp_list_autonomous_agents
   ```

2. **monitor_system_health** - Check system health
   ```
   @mcp monitor_system_health
   ```

3. **create_backup** - Create backups
   ```
   @mcp create_backup
   ```

4. **sync_cache** - Sync Redis ↔ PostgreSQL
   ```
   @mcp sync_cache
   ```

5. **classify_ticket** - Classify helpdesk tickets
   ```
   @mcp classify_ticket "WiFi not working"
   ```

6. **resolve_ticket** - Get resolution steps
   ```
   @mcp resolve_ticket --category=network --description="No internet"
   ```

7. **execute_desktop_command** - Run remote commands
   ```
   @mcp execute_desktop_command --command="Get-Service Docker" --target=192.168.0.30
   ```

## Resources

- `twisterlab://agents/registry` - Full agent documentation
- `twisterlab://system/health` - System status
- `twisterlab://agents/status` - Agent status

## Files

- Base class: `agents/base.py` (TwisterAgent)
- Real agents: `agents/real/*.py`
- MCP server: `agents/mcp/mcp_server_continue_sync.py`
"""

        else:
            return self._error_response(request_id, -32602, f"Unknown resource: {uri}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {"uri": uri, "mimeType": "application/json", "text": content}
                ]
            },
        }

    def _handle_resources_templates_list(self, request_id: int) -> Dict:
        """List available resource templates (optional MCP feature)"""
        # Return empty list - we don't use resource templates
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resourceTemplates": []}}

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
                "messages": [
                    {"role": "user", "content": {"type": "text", "text": text}}
                ],
            },
        }

    def _error_response(self, request_id: int, code: int, message: str) -> Dict:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }

    def run(self):
        """Main event loop - read stdin, write stdout"""
        logger.info("=" * 60)
        logger.info(f"MCP Server Starting: {self.server_info['name']}")
        logger.info(f"Protocol: MCP {self.protocol_version}")
        logger.info("=" * 60)

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
