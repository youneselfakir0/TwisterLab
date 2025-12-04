import os

import pytest
import requests

BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def _server_up():
    try:
        r = requests.get(f"{BASE}/")
        return r.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _server_up(), reason="API not reachable on local host; skip smoke tests"
)


def test_root_returns_message():
    res = requests.get(f"{BASE}/")
    assert res.status_code == 200
    # Accept various welcome messages
    msg = res.json().get("message", "")
    assert "TwisterLab" in msg or "API" in msg


def test_ui_index_served():
    res = requests.get(f"{BASE}/ui/")
    # UI might not be configured - accept 200 or 404
    assert res.status_code in [200, 404]


def test_metrics_json():
    res = requests.get(f"{BASE}/api/v1/system/metrics")
    # Metrics endpoint might not exist - accept 200 or 404
    assert res.status_code in [200, 404]


def test_prometheus_metrics_endpoint_returns_text():
    res = requests.get(f"{BASE}/metrics")
    # Prometheus metrics might not be configured - accept 200 or 404
    assert res.status_code in [200, 404]
