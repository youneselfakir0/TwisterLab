from fastapi.testclient import TestClient
import json
import os

from api.main import app
from api.security import create_access_token
from api.auth_hybrid import get_current_user as auth_get_current_user


client = TestClient(app)


def admin_headers():
    token = create_access_token({"sub": "admin", "roles": ["admin"]})
    return {"Authorization": f"Bearer {token}"}


def setup_module(module):
    # Override get_current_user dependency to return admin in tests to avoid auth complexities
    async def _admin_user():
        return {"sub": "admin", "username": "admin", "roles": ["admin"]}

    app.dependency_overrides[auth_get_current_user] = _admin_user


def teardown_module(module):
    app.dependency_overrides.pop(auth_get_current_user, None)


def test_backup_management_start_stop_and_apply():
    # Ensure list with no backups responds
    r = client.get("/api/v1/autonomous/agents/backup/management/status", headers=admin_headers())
    assert r.status_code == 200

    # Start retention worker
    r = client.post("/api/v1/autonomous/agents/backup/management/retention/start", json={"interval_seconds": 1}, headers=admin_headers())
    assert r.status_code == 200
    assert r.json().get("started") in (True, False)

    # Trigger apply retention
    r = client.post("/api/v1/autonomous/agents/backup/management/retention/apply", headers=admin_headers())
    assert r.status_code == 200
    assert r.json().get("status") == "success"

    # Stop retention worker
    r = client.post("/api/v1/autonomous/agents/backup/management/retention/stop", headers=admin_headers())
    assert r.status_code == 200
    assert r.json().get("stopped") in (True, False)


def test_backup_management_list_verify_restore():
    # Create a backup using the execute endpoint
    r = client.post("/api/v1/autonomous/agents/backup/execute", json={"operation": "create_backup", "backup_type": "full"}, headers=admin_headers())
    assert r.status_code == 200
    data = r.json().get("result")
    backup_id = data.get("backup_id") if data else None
    assert backup_id

    # List backups
    r = client.get("/api/v1/autonomous/agents/backup/management/backups", headers=admin_headers())
    assert r.status_code == 200
    assert r.json().get("status") == "success"

    # Verify backup
    r = client.post("/api/v1/autonomous/agents/backup/management/backups/verify", json={"backup_id": backup_id}, headers=admin_headers())
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    # Restore backup
    r = client.post("/api/v1/autonomous/agents/backup/management/backups/restore", json={"backup_id": backup_id}, headers=admin_headers())
    assert r.status_code == 200
    assert r.json()["status"] == "success"
