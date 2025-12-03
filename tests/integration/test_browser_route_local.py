import importlib.util
from pathlib import Path

from fastapi import FastAPI
from starlette.testclient import TestClient

spec_agent = importlib.util.spec_from_file_location(
    "browser_agent_mod",
    Path(__file__).resolve().parents[2]
    / "src"
    / "twisterlab"
    / "agents"
    / "real"
    / "browser_screenshot_agent.py",
)
agent_mod = importlib.util.module_from_spec(spec_agent)
spec_agent.loader.exec_module(agent_mod)
BrowserScreenshotAgent = agent_mod.BrowserScreenshotAgent


def test_browser_visit_local():
    app = FastAPI()

    @app.post("/api/v1/browser/visit")
    async def visit_endpoint(req: dict):
        url = req.get("url")
        agent = BrowserScreenshotAgent()
        # Prefer the async API when calling from an async endpoint
        try:
            screenshot = await agent.visit_async(url)
        except AttributeError:
            # Fallback to sync API running in a thread
            import anyio

            screenshot = await anyio.to_thread.run_sync(agent.visit, url)
        return {"screenshot": screenshot}

    client = TestClient(app)

    res = client.post("/api/v1/browser/visit", json={"url": "https://example.com"})
    assert res.status_code == 200
    data = res.json()
    assert data["screenshot"].startswith("data:image/png;base64,")
