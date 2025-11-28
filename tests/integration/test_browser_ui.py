import base64

from starlette.testclient import TestClient

from twisterlab.api.main import app

client = TestClient(app)


def test_visit_basic():
    res = client.post("/api/v1/browser/visit", json={"url": "https://example.com"})
    assert res.status_code == 200
    data = res.json()
    assert "screenshot" in data
    assert data["screenshot"].startswith("data:image/png;base64,")
    b64 = data["screenshot"].split(",", 1)[1]
    decoded = base64.b64decode(b64)
    assert len(decoded) > 0
