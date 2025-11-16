import asyncio

from fastapi.testclient import TestClient

from api.main import app


def test_mcp_endpoints():
    client = TestClient(app)

    print("🧪 Testing MCP endpoints...")

    # Test health endpoint
    print("\n1. Testing /v1/mcp/tools/health")
    response = client.get("/v1/mcp/tools/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check: {data['status']}, {data['tools']} tools available")
        print(f"   Tools: {', '.join(data['tools_available'])}")
    else:
        print(f"❌ Health check failed: {response.status_code}")

    # Test list agents endpoint
    print("\n2. Testing /v1/mcp/tools/list_autonomous_agents")
    response = client.post("/v1/mcp/tools/list_autonomous_agents")
    if response.status_code == 200:
        data = response.json()
        if "data" in data and isinstance(data["data"], dict) and "agents" in data["data"]:
            agents = data["data"]["agents"]
            print(f"✅ Found {len(agents)} agents:")
            for agent in agents:
                if isinstance(agent, dict):
                    mcp_tool = agent.get("mcp_tool", "None")
                    print(f"   - {agent.get('name', 'Unknown')}: {mcp_tool}")
        else:
            print(f"❌ Unexpected response format: {data}")
    else:
        print(f"❌ List agents failed: {response.status_code} - {response.text}")

    # Test sync endpoint
    print("\n3. Testing /v1/mcp/tools/sync_cache_db")
    response = client.post(
        "/v1/mcp/tools/sync_cache_db", json={"operation": "verify_consistency", "force": False}
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok":
            print("✅ Sync endpoint working")
        else:
            print(f"⚠️ Sync endpoint returned error: {data.get('error')}")
    else:
        print(f"❌ Sync endpoint failed: {response.status_code}")

    # Test execute command endpoint
    print("\n4. Testing /v1/mcp/tools/execute_command")
    response = client.post("/v1/mcp/tools/execute_command", json={"command": "hostname"})
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok":
            print("✅ Execute command endpoint working")
        else:
            print(f"⚠️ Execute command returned error: {data.get('error')}")
    else:
        print(f"❌ Execute command failed: {response.status_code}")


async def test_mcp_router():
    """Test MCP router isolation."""
    print("\n5. Testing MCP router isolation")
    from agents.mcp.mcp_router import MCPRouter

    router = MCPRouter()

    # Test valid access (MonitoringAgent -> monitoring_mcp)
    try:
        async with router:
            await router.route_to_mcp("MonitoringAgent", "monitoring_mcp", "health_check", {})
        print("✅ Valid access allowed: MonitoringAgent -> monitoring_mcp")
    except Exception as e:
        print(f"❌ Valid access blocked: {e}")

    # Test invalid access (should be blocked)
    try:
        async with router:
            await router.route_to_mcp("ClassifierAgent", "backup_mcp", "create_backup", {})
        print("❌ Invalid access allowed (should be blocked)")
    except PermissionError as e:
        print("✅ Invalid access correctly blocked:", str(e)[:50] + "...")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")


def test_mcp_endpoints():
    # ... existing code ...
    asyncio.run(test_mcp_router())


if __name__ == "__main__":
    test_mcp_endpoints()
