"""
REST API wrapper for MCP Server (Mode 1).

Provides HTTP/REST interface to MCP operations for universal interoperability.
Clients: Python, Node.js, Bash (curl), any HTTP-capable language.

Endpoint: POST /v1/mcp/message
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from agents.mcp.mcp_server import MCPServer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1/mcp", tags=["MCP"])

# Global MCP server instance
mcp_server = MCPServer()


# Request/Response models
class MCPRequest(BaseModel):
    """REST request wrapping MCP JSON-RPC call."""

    method: str = Field(
        ...,
        description="MCP method (initialize, tools/list, tools/call, resources/read, etc.)",
        examples=["tools/list", "tools/call", "resources/read"],
    )
    params: Optional[Dict[str, Any]] = Field(
        default={},
        description="Method parameters",
    )
    id: Optional[str] = Field(
        default=None,
        description="Request ID (auto-generated if not provided)",
    )


class MCPResponse(BaseModel):
    """REST response wrapping MCP JSON-RPC response."""

    jsonrpc: str = Field(default="2.0")
    id: Optional[str] = Field(default=None)
    result: Optional[Dict[str, Any]] = Field(default=None)
    error: Optional[Dict[str, Any]] = Field(default=None)


class MCPToolCallRequest(BaseModel):
    """Simplified tool call request (alternative to raw JSON-RPC)."""

    tool: str = Field(
        ...,
        description="Tool name",
        examples=["monitor_system_health", "classify_ticket"],
    )
    arguments: Dict[str, Any] = Field(
        default={},
        description="Tool arguments",
    )


class MCPResourceReadRequest(BaseModel):
    """Simplified resource read request."""

    uri: str = Field(
        ...,
        description="Resource URI",
        examples=[
            "twisterlab://system/health",
            "twisterlab://agents/status",
            "twisterlab://audit/mcp-log",
        ],
    )


# Endpoints

@router.post("/message", response_model=MCPResponse)
async def mcp_message(request: MCPRequest) -> MCPResponse:
    """
    Universal MCP endpoint - accepts any MCP JSON-RPC method.

    Supports all MCP protocol methods:
    - initialize
    - tools/list, tools/call
    - resources/list, resources/read
    - prompts/list, prompts/get

    **Example: List available tools**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/message \\
      -H "Content-Type: application/json" \\
      -d '{
        "method": "tools/list",
        "params": {}
      }'
    ```

    **Example: Call a tool**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/message \\
      -H "Content-Type: application/json" \\
      -d '{
        "method": "tools/call",
        "params": {
          "name": "monitor_system_health",
          "arguments": {"include_docker": true}
        }
      }'
    ```

    **Example: Read a resource**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/message \\
      -H "Content-Type: application/json" \\
      -d '{
        "method": "resources/read",
        "params": {
          "uri": "twisterlab://system/health"
        }
      }'
    ```
    """
    try:
        # Generate request ID if not provided
        request_id = request.id or f"rest-{datetime.now().timestamp()}"

        # Build JSON-RPC request
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": request.method,
            "params": request.params,
        }

        logger.info(f"MCP REST Request: {request.method}")

        # Route to MCP server handler
        response = await mcp_server.handle_request(jsonrpc_request)

        return MCPResponse(**response)

    except Exception as e:
        logger.error(f"MCP REST error: {e}", exc_info=True)
        return MCPResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}",
            },
        )


@router.post("/tools/call")
async def call_tool(request: MCPToolCallRequest) -> Dict[str, Any]:
    """
    Simplified tool call endpoint (no JSON-RPC wrapping).

    **Example: Monitor system health**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \\
      -H "Content-Type: application/json" \\
      -d '{
        "tool": "monitor_system_health",
        "arguments": {"include_docker": true}
      }'
    ```

    **Example: Classify ticket**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/tools/call \\
      -H "Content-Type: application/json" \\
      -d '{
        "tool": "classify_ticket",
        "arguments": {
          "ticket_text": "Cannot connect to WiFi network"
        }
      }'
    ```
    """
    try:
        # Call tool via MCP server
        result = await mcp_server.handle_tools_call({
            "name": request.tool,
            "arguments": request.arguments,
        })

        # Check for errors
        if result.get("isError"):
            raise HTTPException(
                status_code=500,
                detail=result["content"][0]["text"],
            )

        return {
            "status": "success",
            "tool": request.tool,
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool call error: {request.tool}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}",
        )


@router.post("/resources/read")
async def read_resource(request: MCPResourceReadRequest) -> Dict[str, Any]:
    """
    Simplified resource read endpoint.

    **Example: Read system health**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \\
      -H "Content-Type: application/json" \\
      -d '{
        "uri": "twisterlab://system/health"
      }'
    ```

    **Example: Read agent statuses**
    ```bash
    curl -X POST http://192.168.0.30:8000/v1/mcp/resources/read \\
      -H "Content-Type: application/json" \\
      -d '{
        "uri": "twisterlab://agents/status"
      }'
    ```
    """
    try:
        # Read resource via MCP server
        result = await mcp_server.handle_resources_read({
            "uri": request.uri,
        })

        # Check for errors
        if result.get("isError"):
            raise HTTPException(
                status_code=404,
                detail=result["contents"][0]["text"],
            )

        return {
            "status": "success",
            "uri": request.uri,
            "contents": result["contents"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resource read error: {request.uri}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Resource read failed: {str(e)}",
        )


@router.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """
    List all available MCP tools.

    **Example**
    ```bash
    curl http://192.168.0.30:8000/v1/mcp/tools
    ```
    """
    try:
        result = await mcp_server.handle_tools_list()
        return {
            "status": "success",
            "tools": result["tools"],
        }
    except Exception as e:
        logger.error(f"List tools error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tools: {str(e)}",
        )


@router.get("/resources")
async def list_resources() -> Dict[str, Any]:
    """
    List all available MCP resources.

    **Example**
    ```bash
    curl http://192.168.0.30:8000/v1/mcp/resources
    ```
    """
    try:
        result = await mcp_server.handle_resources_list()
        return {
            "status": "success",
            "resources": result["resources"],
        }
    except Exception as e:
        logger.error(f"List resources error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list resources: {str(e)}",
        )


@router.get("/prompts")
async def list_prompts() -> Dict[str, Any]:
    """
    List all available MCP prompt templates.

    **Example**
    ```bash
    curl http://192.168.0.30:8000/v1/mcp/prompts
    ```
    """
    try:
        result = await mcp_server.handle_prompts_list()
        return {
            "status": "success",
            "prompts": result["prompts"],
        }
    except Exception as e:
        logger.error(f"List prompts error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list prompts: {str(e)}",
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    MCP REST API health check.

    **Example**
    ```bash
    curl http://192.168.0.30:8000/v1/mcp/health
    ```
    """
    return {
        "status": "healthy",
        "service": "twisterlab-mcp-rest",
        "version": "1.0.0",
        "transport": "http",
        "timestamp": datetime.now().isoformat(),
    }
