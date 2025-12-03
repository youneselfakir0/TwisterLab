from starlette.testclient import TestClient

from twisterlab.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_agents():
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_agent():
    response = client.post("/api/v1/agents/", json={"name": "Test Agent"})
    assert response.status_code == 201
    assert "id" in response.json()


def test_update_agent():
    response = client.put("/api/v1/agents/1", json={"name": "Updated Agent"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Agent"


def test_delete_agent():
    response = client.delete("/api/v1/agents/1")
    assert response.status_code == 204


def test_mcp_endpoint():
    response = client.post(
        "/api/v1/mcp/execute",
        json={
            "tool_name": "create_browser_tool",
            "args": {"target_url": "https://example.com"},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] in ["success", "error"]
