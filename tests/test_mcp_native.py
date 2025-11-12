"""
Tests for Native MCP Server (stdio transport).

Tests Claude Desktop integration and MCP protocol compliance.
"""

import asyncio
import json
import pytest
from agents.mcp.mcp_server import MCPServer


@pytest.fixture
async def mcp_server():
    """Create MCP server instance."""
    server = MCPServer()
    async with server.router:
        yield server


@pytest.mark.asyncio
async def test_initialize(mcp_server):
    """Test initialize handshake."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "test-client",
                "version": "1.0",
            },
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == "test-1"
    assert "result" in response
    assert response["result"]["protocolVersion"] == "2024-11-05"
    assert response["result"]["serverInfo"]["name"] == "twisterlab-mcp"
    assert response["result"]["capabilities"]["tools"] is True
    assert response["result"]["capabilities"]["resources"] is True
    assert response["result"]["capabilities"]["prompts"] is True


@pytest.mark.asyncio
async def test_tools_list(mcp_server):
    """Test listing available tools."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-2",
        "method": "tools/list",
        "params": {},
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "tools" in response["result"]

    tools = response["result"]["tools"]
    tool_names = [t["name"] for t in tools]

    assert "monitor_system_health" in tool_names
    assert "create_backup" in tool_names
    assert "sync_cache_db" in tool_names
    assert "classify_ticket" in tool_names
    assert "resolve_ticket" in tool_names


@pytest.mark.asyncio
async def test_tools_call_monitor(mcp_server):
    """Test calling monitor_system_health tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-3",
        "method": "tools/call",
        "params": {
            "name": "monitor_system_health",
            "arguments": {
                "include_docker": True,
            },
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "content" in response["result"]
    assert len(response["result"]["content"]) > 0
    assert response["result"]["content"][0]["type"] == "text"


@pytest.mark.asyncio
async def test_tools_call_classify(mcp_server):
    """Test calling classify_ticket tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-4",
        "method": "tools/call",
        "params": {
            "name": "classify_ticket",
            "arguments": {
                "ticket_text": "Cannot connect to WiFi network",
            },
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "content" in response["result"]

    content_text = response["result"]["content"][0]["text"]
    result_data = json.loads(content_text)

    assert "category" in result_data
    assert "confidence" in result_data


@pytest.mark.asyncio
async def test_resources_list(mcp_server):
    """Test listing available resources."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-5",
        "method": "resources/list",
        "params": {},
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "resources" in response["result"]

    resources = response["result"]["resources"]
    resource_uris = [r["uri"] for r in resources]

    assert "twisterlab://system/health" in resource_uris
    assert "twisterlab://agents/status" in resource_uris
    assert "twisterlab://audit/mcp-log" in resource_uris


@pytest.mark.asyncio
async def test_resources_read_health(mcp_server):
    """Test reading system health resource."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-6",
        "method": "resources/read",
        "params": {
            "uri": "twisterlab://system/health",
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "contents" in response["result"]
    assert len(response["result"]["contents"]) > 0

    content = response["result"]["contents"][0]
    assert content["uri"] == "twisterlab://system/health"
    assert content["mimeType"] == "application/json"


@pytest.mark.asyncio
async def test_prompts_list(mcp_server):
    """Test listing available prompts."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-7",
        "method": "prompts/list",
        "params": {},
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "prompts" in response["result"]

    prompts = response["result"]["prompts"]
    prompt_names = [p["name"] for p in prompts]

    assert "classify_it_ticket" in prompt_names
    assert "resolve_network_issue" in prompt_names


@pytest.mark.asyncio
async def test_prompts_get(mcp_server):
    """Test getting a prompt template."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-8",
        "method": "prompts/get",
        "params": {
            "name": "classify_it_ticket",
            "arguments": {
                "ticket_description": "Printer offline error",
            },
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "messages" in response["result"]
    assert len(response["result"]["messages"]) > 0

    message = response["result"]["messages"][0]
    assert message["role"] == "user"
    assert "Printer offline error" in message["content"]["text"]


@pytest.mark.asyncio
async def test_invalid_method(mcp_server):
    """Test error handling for invalid method."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-9",
        "method": "invalid/method",
        "params": {},
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "error" in response
    assert response["error"]["code"] == -32601
    assert "Method not found" in response["error"]["message"]


@pytest.mark.asyncio
async def test_tool_not_found(mcp_server):
    """Test error handling for unknown tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-10",
        "method": "tools/call",
        "params": {
            "name": "unknown_tool",
            "arguments": {},
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert response["result"].get("isError") is True


@pytest.mark.asyncio
async def test_resource_not_found(mcp_server):
    """Test error handling for unknown resource."""
    request = {
        "jsonrpc": "2.0",
        "id": "test-11",
        "method": "resources/read",
        "params": {
            "uri": "twisterlab://unknown/resource",
        },
    }

    response = await mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    # Error is embedded in result, not as JSON-RPC error
    assert response["result"].get("isError") is True
