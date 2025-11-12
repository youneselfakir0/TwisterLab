"""
MCP Server for Continue IDE integration (Synchronous version)
Windows-compatible version without asyncio

Usage:
    python agents/mcp/mcp_server_continue_sync.py

Protocol: MCP 2024-11-05 (Model Context Protocol)
Transport: stdio (JSON-RPC 2.0)
"""
import json
import logging
import sys
import os
from typing import Any, Dict
from datetime import datetime, timezone

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
            "version": "1.0.0",
            "description": "TwisterLab MCP Server for Continue IDE"
        }
        logger.info(f"Initialized: {self.server_info['name']} v{self.server_info['version']}")
        
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
        """List available tools"""
        tools = [
            {
                "name": "classify_ticket",
                "description": "Classify IT helpdesk ticket (network, hardware, software, account, email)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_text": {"type": "string", "description": "Ticket text"}
                    },
                    "required": ["ticket_text"]
                }
            },
            {
                "name": "resolve_ticket",
                "description": "Get resolution steps from SOP database",
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
                "name": "monitor_system_health",
                "description": "Check TwisterLab system health (CPU, RAM, disk, Docker)",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "create_backup",
                "description": "Create database/config backup",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "backup_type": {"type": "string", "enum": ["full", "incremental"]}
                    }
                }
            },
        ]
        
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}
    
    def _handle_tools_call(self, request_id: int, params: Dict) -> Dict:
        """Execute tool call (mock implementation)"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool: {tool_name} | Args: {arguments}")
        
        # Mock responses (replace with real agent calls when API is ready)
        if tool_name == "classify_ticket":
            ticket_text = arguments.get("ticket_text", "")
            result = {
                "status": "success",
                "agent": "RealClassifierAgent",
                "category": "network" if "wifi" in ticket_text.lower() or "network" in ticket_text.lower() else "software",
                "confidence": 0.85,
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
                "note": "⚠️ Mock response - API service offline"
            }
            
        elif tool_name == "create_backup":
            result = {
                "status": "success",
                "agent": "RealBackupAgent",
                "backup_location": "/backups/mock_backup.tar.gz",
                "note": "⚠️ Mock response - API service offline"
            }
            
        else:
            return self._error_response(request_id, -32602, f"Unknown tool: {tool_name}")
        
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
    
    def _handle_prompts_list(self, request_id: int) -> Dict:
        """List available prompts"""
        prompts = [
            {
                "name": "classify_it_ticket",
                "description": "Classify an IT helpdesk ticket",
                "arguments": [{"name": "ticket", "description": "Ticket text", "required": True}]
            },
            {
                "name": "resolve_network_issue",
                "description": "Get network troubleshooting steps",
                "arguments": [{"name": "issue", "description": "Network issue", "required": True}]
            }
        ]
        
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
