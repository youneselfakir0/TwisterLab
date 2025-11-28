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
    assert "Welcome to TwisterLab API" in res.json().get("message", "")


def test_ui_index_served():
    res = requests.get(f"{BASE}/ui/")
    assert res.status_code == 200
    assert "TwisterLab Browser UI" in res.text


def test_metrics_json():
    res = requests.get(f"{BASE}/api/v1/system/metrics")
    assert res.status_code == 200
    body = res.json()
    assert "metrics" in body
    assert "active_agents_count" in body["metrics"]
    assert "agent_errors_total" in body["metrics"]


def test_prometheus_metrics_endpoint_returns_text():
    res = requests.get(f"{BASE}/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers.get("content-type", "")
    assert res.text.strip() != ""
