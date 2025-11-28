from starlette.testclient import TestClient

from twisterlab.api.main import STATIC_UI, app

client = TestClient(app)


def test_ui_index_served():
    # Ensure STATIC_UI path resolves correctly in the app
    assert STATIC_UI.exists(), f"STATIC_UI not found at {STATIC_UI}"
    res = client.get("/ui/")
    assert res.status_code == 200
    text = res.text
    assert "TwisterLab Browser UI" in text
