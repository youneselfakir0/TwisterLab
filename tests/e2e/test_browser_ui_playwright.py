import os
import time

import pytest

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.skipif(
        os.environ.get("E2E") != "1",
        reason="E2E tests require E2E=1 environment variable",
    ),
    pytest.mark.e2e,
]

BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def _wait_for_server(base, timeout=30):
    import requests

    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(base + "/")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def test_ui_go_button_loads_screenshot(browser_page):
    page = browser_page
    assert _wait_for_server(BASE), "API did not start in time"
    page.goto(f"{BASE}/ui/", wait_until="networkidle")
    assert page.title() == "TwisterLab Browser UI"
    # ensure the input and button exist
    page.fill("#addr", "https://example.com")
    page.click("#go")
    # Wait for an image to appear in the display area
    img = page.wait_for_selector("#display img", timeout=15000)
    assert img is not None
    src = img.get_attribute("src")
    assert src and src.startswith("data:image/png;base64,")
