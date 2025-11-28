import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logging.warning("httpx not available - install with: pip install httpx")

logger = logging.getLogger(__name__)


class MCPServerContinue:
    """MCP Server for Continue IDE - stdio transport"""

    def __init__(self):
        """Initialize MCP server"""
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "twisterlab-mcp-continue",
            "version": "2.1.0",
            "description": "TwisterLab MCP Server for Continue IDE (Enhanced)",
        }

        # API configuration
        self.api_url = os.getenv("API_URL", "http://192.168.0.30:8000")
        self.api_timeout = 60.0

        if HTTPX_AVAILABLE:
            self.api_available = self._test_api_connectivity()
            self.mode = "REAL" if self.api_available else "HYBRID"
        else:
            self.api_available = False
            self.mode = "HYBRID"

        logger.info(
            f"Initialized: {self.server_info['name']} v{self.server_info['version']}"
        )
        logger.info(f"Mode: {self.mode}")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"API Available: {self.api_available}")

    def _test_api_connectivity(self) -> bool:
        if not HTTPX_AVAILABLE:
            return False
        try:
            health_url = f"{self.api_url}/health"
            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"API connectivity test failed: {e}")
            return False

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
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
        client = params.get("clientInfo", {}).get("name", "unknown")
        logger.info(f"Client: {client}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.protocol_version,
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "serverInfo": self.server_info,
            },
        }

    def _handle_tools_list(self, request_id: int) -> Dict:
        tools = [
            {"name": "twisterlab_mcp_list_autonomous_agents", "description": "List...", "inputSchema": {"type": "object"}},
            {"name": "monitor_system_health", "description": "RealMonitoringAgent", "inputSchema": {"type": "object"}},
        ]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    def _handle_tools_call(self, request_id: int, params: Dict) -> Dict:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        logger.info(f"Tool: {tool_name} | Args: {arguments} | Mode: {self.mode}")

        if self.mode == "REAL" and self.api_available:
            try:
                result = self._call_api(tool_name, arguments)
            except Exception:
                result = self._get_hybrid_response(tool_name, arguments)
        elif self.mode == "HYBRID":
            try:
                result = self._call_api(tool_name, arguments)
            except Exception:
                result = self._get_hybrid_response(tool_name, arguments)
        else:
            result = self._get_mock_response(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
        }

    def _get_mock_response(self, tool_name: str, arguments: Dict) -> Dict:
        return {"status": "ok", "tool": tool_name, "data": {}}

    def _get_hybrid_response(self, tool_name: str, arguments: Dict) -> Dict:
        return {"status": "success", "mode": "HYBRID", "tool": tool_name}

    def _error_response(self, request_id: int, code: int, message: str) -> Dict:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    def _call_api(self, tool_name: str, arguments: Dict) -> Dict:
        """Perform a simple POST to API endpoint and return the JSON response."""
        if not HTTPX_AVAILABLE:
            raise Exception("httpx not available")
        # Basic payload format for REST wrapper endpoint
        payload = {
            "tool": tool_name,
            "arguments": arguments,
        }
        url = f"{self.api_url}/v1/mcp/message"
        with httpx.Client(timeout=self.api_timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
