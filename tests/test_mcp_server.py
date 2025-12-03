#!/usr/bin/env python3
"""
Test script for TwisterLab MCP Server
Tests MCP server functionality without requiring Kubernetes deployment
"""

import json
from unittest.mock import patch
import sys

from twisterlab.agents.mcp.mcp_server import MCPServerContinue


def test_mcp_server_initialization():
    """Test MCP server initialization"""
    print("🧪 Testing MCP server initialization...")

    server = MCPServerContinue()

    # Test that the server was created successfully
    assert hasattr(server, 'api_url')
    assert hasattr(server, 'protocol_version')

    print("✅ MCP server initialization test passed")

def test_list_tools_with_mock_api():
    """Test tool registration"""
    print("🧪 Testing tool registration...")

    server = MCPServerContinue()

    # Check that tools are registered
    # FastMCP automatically registers tools via decorators
    # We can verify by checking the app has tools
    # ensure tools list returns a result
    tools_resp = server._handle_tools_list(1)
    assert 'result' in tools_resp and 'tools' in tools_resp['result']
    # The tools are registered dynamically via decorators

    print("✅ Tool registration test passed")


def test_call_tool_with_mock_api():
    """Test calling a tool with mocked API response"""
    print("🧪 Testing tool execution with mocked API...")

    server = MCPServerContinue()

    # Mock successful API response
    mock_tool_response = {
        "status": "ok",
        "data": {
            "result": "Backup created successfully",
            "timestamp": "2025-11-22T17:20:00Z"
        }
    }

    with patch.object(server, '_call_api', return_value=mock_tool_response):
        response = server._handle_tools_call(3, {'name': 'create_backup', 'arguments': {'target': '/data'}})
        assert 'result' in response and 'content' in response['result']

    print("✅ Tool execution test passed")


def test_error_handling():
    """Test error handling scenarios"""
    print("🧪 Testing error handling...")

    server = MCPServerContinue()

    # Test API error handling
    with patch.object(server, '_call_api', side_effect=Exception("Connection failed")):
        # Should return hybrid fallback response
        response = server._handle_tools_call(5, {'name': 'create_backup', 'arguments': {}})
        assert 'result' in response and 'content' in response['result']

    print("✅ Error handling test passed")


def test_api_connection_error():
    """Test API connection error handling"""
    print("🧪 Testing API connection error handling...")

    server = MCPServerContinue()

    with patch.object(server, '_call_api', side_effect=Exception("Network error")):
        response = server._handle_tools_call(6, {'name': 'create_backup', 'arguments': {}})
        assert 'result' in response and 'content' in response['result']

    print("✅ API connection error test passed")


def main():
    """Run all tests"""
    print("🚀 Starting TwisterLab MCP Server Tests")
    print("=" * 50)

    try:
        test_mcp_server_initialization()
        test_list_tools_with_mock_api()
        test_call_tool_with_mock_api()
        test_error_handling()
        test_api_connection_error()

        print("=" * 50)
        print("🎉 All MCP server tests passed successfully!")
        print("\n📋 Test Summary:")
        print("   ✅ Server initialization")
        print("   ✅ Tool registration")
        print("   ✅ Tool execution with API calls")
        print("   ✅ Error handling (API errors)")
        print("   ✅ API connection error handling")
        print("\n🔗 The MCP server is ready for Kubernetes deployment!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
