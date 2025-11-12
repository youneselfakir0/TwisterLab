"""
Test script for MCP Server Continue
Tests all MCP protocol methods
"""
import json
import subprocess
import sys

def send_request(request):
    """Send JSON-RPC request to MCP server"""
    proc = subprocess.Popen(
        ["python", "agents/mcp/mcp_server_continue.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PYTHONPATH": "C:\\TwisterLab"}
    )

    request_str = json.dumps(request) + "\n"
    stdout, stderr = proc.communicate(input=request_str.encode())

    print(f"\n{'='*60}")
    print(f"REQUEST: {request['method']}")
    print(f"{'='*60}")

    if stderr:
        print("STDERR (logs):")
        print(stderr.decode())

    if stdout:
        print("\nRESPONSE:")
        response = json.loads(stdout.decode().strip())
        print(json.dumps(response, indent=2))
        return response

    return None

# Test 1: Initialize
print("TEST 1: Initialize MCP connection")
response = send_request({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0"}
    }
})

# Test 2: List tools
print("\n\nTEST 2: List available tools")
response = send_request({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
})

# Test 3: List resources
print("\n\nTEST 3: List available resources")
response = send_request({
    "jsonrpc": "2.0",
    "id": 3,
    "method": "resources/list",
    "params": {}
})

# Test 4: List prompts
print("\n\nTEST 4: List available prompts")
response = send_request({
    "jsonrpc": "2.0",
    "id": 4,
    "method": "prompts/list",
    "params": {}
})

print("\n\n" + "="*60)
print("✅ ALL TESTS COMPLETED")
print("="*60)
print("\nNext steps:")
print("1. Restart VS Code (Ctrl+Shift+P → Developer: Reload Window)")
print("2. Open Continue chat (Ctrl+L)")
print("3. Type: @twisterlab")
print("4. Continue should show TwisterLab MCP tools!")
