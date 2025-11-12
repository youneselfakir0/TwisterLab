"""
Test MCP server list_autonomous_agents tool
Simulates Continue IDE calling the MCP server
"""
import json
import subprocess
import sys

def test_mcp_list_agents():
    """Test list_autonomous_agents via stdio"""
    
    # MCP requests to send
    requests = [
        # 1. Initialize
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        },
        # 2. List tools
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        # 3. Call list_autonomous_agents
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_autonomous_agents",
                "arguments": {}
            }
        }
    ]
    
    # Start MCP server
    proc = subprocess.Popen(
        [sys.executable, "agents/mcp/mcp_server_continue_sync.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    print("🧪 Testing MCP Server - list_autonomous_agents")
    print("=" * 60)
    
    try:
        for i, request in enumerate(requests, 1):
            # Send request
            request_json = json.dumps(request) + "\n"
            print(f"\n📤 Request {i}: {request['method']}")
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            # Read response
            response_line = proc.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                print(f"📥 Response {i}:")
                
                if request['method'] == 'tools/list':
                    tools = response.get('result', {}).get('tools', [])
                    print(f"   ✅ {len(tools)} tools found:")
                    for tool in tools:
                        print(f"      - {tool['name']}: {tool['description'][:80]}...")
                
                elif request['method'] == 'tools/call' and request['params']['name'] == 'list_autonomous_agents':
                    content = response.get('result', {}).get('content', [])
                    if content:
                        data = json.loads(content[0]['text'])
                        print(f"   ✅ Status: {data.get('status')}")
                        print(f"   ✅ Mode: {data.get('mode')}")
                        print(f"   ✅ Total agents: {data.get('total')}")
                        print(f"\n   📋 Agents list:")
                        for agent in data.get('agents', []):
                            print(f"      {agent['name']:30} | {agent['description']}")
                else:
                    print(f"   {json.dumps(response, indent=2)[:200]}...")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == "__main__":
    test_mcp_list_agents()
