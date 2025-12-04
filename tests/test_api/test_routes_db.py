from fastapi.testclient import TestClient

from twisterlab.api.main import app
from twisterlab.storage.db_repo import DatabaseAgentRepo
from twisterlab.api.dependencies import get_agent_repo


def _override_get_agent_repo():
    return DatabaseAgentRepo()


app.dependency_overrides[get_agent_repo] = _override_get_agent_repo
client = TestClient(app)


def test_create_agent_db_repo():
    response = client.post("/api/v1/agents/", json={"name": "DB Agent"})
    assert response.status_code == 201
    assert "id" in response.json()
    assert isinstance(response.json()["id"], str)


def test_update_agent_db_repo():
    # Ensure we can update the agent we just created; the DB repo returns string id
    response = client.post("/api/v1/agents/", json={"name": "DB Agent 2"})
    assert response.status_code == 201
    agent_id = response.json()["id"]
    upd = client.put(f"/api/v1/agents/{agent_id}", json={"name": "DB Agent Updated"})
    assert upd.status_code == 200
    assert upd.json()["name"] == "DB Agent Updated"
    assert isinstance(upd.json()["id"], str)


def test_delete_agent_db_repo():
    response = client.post("/api/v1/agents/", json={"name": "DB Agent To Delete"})
    assert response.status_code == 201
    agent_id = response.json()["id"]
    d = client.delete(f"/api/v1/agents/{agent_id}")
    assert d.status_code == 204
