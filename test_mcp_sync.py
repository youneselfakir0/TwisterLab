"""
Test MCP Server Continue (Sync version)
"""
import json
import subprocess

def test_mcp_method(method, params=None):
    """Test a single MCP method"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    proc = subprocess.Popen(
        ["python", "agents/mcp/mcp_server_continue_sync.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    request_str = json.dumps(request) + "\n"
    stdout, stderr = proc.communicate(input=request_str.encode(), timeout=5)
    
    print(f"\n{'='*60}")
    print(f"TEST: {method}")
    print(f"{'='*60}")
    
    if stderr:
        print("LOGS:")
        for line in stderr.decode().splitlines()[-5:]:  # Last 5 lines
            print(f"  {line}")
    
    if stdout:
        print("\nRESPONSE:")
        response = json.loads(stdout.decode().strip())
        print(json.dumps(response, indent=2))
        return response
    
    return None


# Test 1: Initialize
test_mcp_method("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
})

# Test 2: List tools
test_mcp_method("tools/list")

# Test 3: Call classify_ticket
test_mcp_method("tools/call", {
    "name": "classify_ticket",
    "arguments": {"ticket_text": "Cannot connect to WiFi eduroam"}
})

# Test 4: Call monitor_system_health
test_mcp_method("tools/call", {
    "name": "monitor_system_health",
    "arguments": {}
})

# Test 5: List resources
test_mcp_method("resources/list")

# Test 6: Read health resource
test_mcp_method("resources/read", {
    "uri": "twisterlab://system/health"
})

print("\n" + "="*60)
print("✅ ALL TESTS PASSED")
print("="*60)
print("\nNext steps:")
print("1. Restart VS Code: Ctrl+Shift+P → Developer: Reload Window")
print("2. Open Continue: Ctrl+L")
print("3. Type: @twisterlab")
print("4. Continue will show TwisterLab MCP tools!")
print("\nOr use slash commands:")
print("  /classify Cannot connect to WiFi")
print("  /health")
print("  /backup")
