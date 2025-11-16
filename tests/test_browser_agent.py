import os

import pytest

try:
    from agents.real.BrowserAgent import BrowserAgent
except Exception:
    BrowserAgent = None


@pytest.mark.asyncio
async def test_browser_agent_open_and_close():
    # Skip test if playwright isn't installed (or browsers not present)
    import importlib

    if (
        BrowserAgent is None
        or importlib.util.find_spec("playwright") is None
        or os.getenv("PLAYWRIGHT_SKIP", "0") == "1"
    ):
        pytest.skip("Playwright browsers not installed; skipping browser integration test")

    agent = BrowserAgent()
    # Open browser in headless mode, navigate to about:blank
    result = await agent.execute("open_browser", {"headless": True, "target_url": "about:blank"})
    assert result["status"] == "success"

    # Get page source
    res = await agent.execute("get_page_source", {})
    assert res["status"] == "success"
    assert "<html" in res["data"].lower()

    # Close browser
    result_close = await agent.execute("close_browser", {})
    assert result_close["status"] == "success"
