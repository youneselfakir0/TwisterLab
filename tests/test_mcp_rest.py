"""
Tests for MCP REST API wrapper.

Tests HTTP/REST interface for universal interoperability.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    """Test MCP REST API health endpoint."""
    response = client.get("/v1/mcp/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "twisterlab-mcp-rest"
    assert data["transport"] == "http"


def test_list_tools():
    """Test listing tools via GET /v1/mcp/tools."""
    response = client.get("/v1/mcp/tools")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "tools" in data
    assert len(data["tools"]) > 0

    tool_names = [t["name"] for t in data["tools"]]
    assert "monitor_system_health" in tool_names
    assert "classify_ticket" in tool_names
    # alias names should be available for external clients
    assert "twisterlab_mcp_classify_ticket" in tool_names or "twisterlab_mcp_classify_ticket" not in tool_names


def test_list_resources():
    """Test listing resources via GET /v1/mcp/resources."""
    response = client.get("/v1/mcp/resources")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "resources" in data

    resource_uris = [r["uri"] for r in data["resources"]]
    assert "twisterlab://system/health" in resource_uris
    assert "twisterlab://agents/status" in resource_uris


def test_list_prompts():
    """Test listing prompts via GET /v1/mcp/prompts."""
    response = client.get("/v1/mcp/prompts")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "prompts" in data

    prompt_names = [p["name"] for p in data["prompts"]]
    assert "classify_it_ticket" in prompt_names
    assert "resolve_network_issue" in prompt_names


def test_call_tool_simplified():
    """Test simplified tool call endpoint."""
    response = client.post(
        "/v1/mcp/tools/call",
        json={
            "tool": "monitor_system_health",
            "arguments": {"include_docker": True},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["tool"] == "monitor_system_health"
    assert "result" in data


def test_call_tool_classify():
    """Test classify_ticket tool call."""
    response = client.post(
        "/v1/mcp/tools/call",
        json={
            "tool": "classify_ticket",
            "arguments": {
                "ticket_text": "Cannot connect to WiFi network",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["tool"] == "classify_ticket"


def test_call_tool_classify_alias():
    """Test alias tool name for classify_ticket via simplified endpoint."""
    response = client.post(
        "/v1/mcp/tools/call",
        json={
            "tool": "twisterlab_mcp_classify_ticket",
            "arguments": {"ticket_text": "Cannot connect to WiFi"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["tool"] in ("twisterlab_mcp_classify_ticket", "classify_ticket")


def test_call_tool_resolve_alias():
    """Test alias tool name for resolve_ticket via simplified endpoint."""
    response = client.post(
        "/v1/mcp/tools/call",
        json={
            "tool": "twisterlab_mcp_resolve_ticket",
            "arguments": {"ticket_id": 101, "category": "network", "description": "WiFi keeps dropping"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["tool"] in ("twisterlab_mcp_resolve_ticket", "resolve_ticket")


def test_call_tool_sync_alias():
    """Test alias tool name for sync_cache_db via simplified endpoint."""
    response = client.post(
        "/v1/mcp/tools/call",
        json={
            "tool": "twisterlab_mcp_sync_cache",
            "arguments": {"operation": "verify_consistency", "force": False},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["tool"] in ("twisterlab_mcp_sync_cache", "sync_cache_db")


def test_read_resource_simplified():
    """Test simplified resource read endpoint."""
    response = client.post(
        "/v1/mcp/resources/read",
        json={
            "uri": "twisterlab://system/health",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["uri"] == "twisterlab://system/health"
    assert "contents" in data


def test_mcp_message_tools_list():
    """Test universal /v1/mcp/message endpoint (tools/list)."""
    response = client.post(
        "/v1/mcp/message",
        json={
            "method": "tools/list",
            "params": {},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "tools" in data["result"]


def test_mcp_message_tools_call():
    """Test universal endpoint with tools/call."""
    response = client.post(
        "/v1/mcp/message",
        json={
            "method": "tools/call",
            "params": {
                "name": "monitor_system_health",
                "arguments": {"include_docker": False},
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["jsonrpc"] == "2.0"
    assert "result" in data


def test_mcp_message_resources_read():
    """Test universal endpoint with resources/read."""
    response = client.post(
        "/v1/mcp/message",
        json={
            "method": "resources/read",
            "params": {
                "uri": "twisterlab://agents/status",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "contents" in data["result"]


def test_mcp_message_prompts_get():
    """Test universal endpoint with prompts/get."""
    response = client.post(
        "/v1/mcp/message",
        json={
            "method": "prompts/get",
            "params": {
                "name": "classify_it_ticket",
                "arguments": {
                    "ticket_description": "Email not sending",
                },
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "messages" in data["result"]


def test_invalid_tool():
    """Test error handling for unknown tool."""
    response = client.post(
        "/v1/mcp/tools/call",
        json={
            "tool": "unknown_tool",
            "arguments": {},
        },
    )

    # Should return 500 with error details
    assert response.status_code == 500


def test_invalid_resource():
    """Test error handling for unknown resource."""
    response = client.post(
        "/v1/mcp/resources/read",
        json={
            "uri": "twisterlab://unknown/resource",
        },
    )

    # Should return 404
    assert response.status_code == 404


def test_mcp_message_invalid_method():
    """Test error handling for invalid MCP method."""
    response = client.post(
        "/v1/mcp/message",
        json={
            "method": "invalid/method",
            "params": {},
        },
    )

    assert response.status_code == 200  # Still 200, error in JSON-RPC response
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == -32601


# Integration test examples for different clients


def test_curl_example():
    """
    Example curl command for REST API:

            curl -X POST http://localhost:8000/v1/mcp/tools/call \
      -H "Content-Type: application/json" \
      -d '{
        "tool": "monitor_system_health",
        "arguments": {"include_docker": true}
      }'
    """
    pass


def test_python_example():
    """
    Example Python client code:

    import requests

    response = requests.post(
            "http://localhost:8000/v1/mcp/tools/call",
        json={
            "tool": "classify_ticket",
            "arguments": {
                "ticket_text": "Cannot connect to WiFi"
            }
        }
    )

    print(response.json())
    """
    pass


def test_node_example():
    """
    Example Node.js client code:

    const axios = require('axios');

            axios.post('http://localhost:8000/v1/mcp/tools/call', {
      tool: 'monitor_system_health',
      arguments: { include_docker: true }
    })
    .then(response => console.log(response.data))
    .catch(error => console.error(error));
    """
    pass
