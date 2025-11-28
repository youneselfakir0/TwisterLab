from starlette.testclient import TestClient

from twisterlab.api.main import app

client = TestClient(app)


def test_metrics_json():
    res = client.get("/api/v1/system/metrics")
    assert res.status_code == 200
    body = res.json()
    assert "metrics" in body
    metrics = body["metrics"]
    assert "active_agents_count" in metrics
    assert "agent_errors_total" in metrics
    # Values should be numeric or null (None)
    for k, v in metrics.items():
        assert v is None or isinstance(v, (int, float))


def test_prometheus_metrics_endpoint_returns_text():
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    text = res.text
    # It should contain some Prometheus metric lines or at least not be empty
    assert text.strip() != ""
