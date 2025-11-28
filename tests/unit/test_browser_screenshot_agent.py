import base64
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "browser_screenshot_agent",
    Path(__file__).resolve().parents[2]
    / "src"
    / "twisterlab"
    / "agents"
    / "real"
    / "browser_screenshot_agent.py",
)
module = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(module)  # type: ignore
BrowserScreenshotAgent = module.BrowserScreenshotAgent


def test_agent_returns_dataurl():
    agent = BrowserScreenshotAgent()
    result = agent.visit("https://example.com")
    assert isinstance(result, str)
    assert result.startswith("data:image/png;base64,")
    b64 = result.split(",", 1)[1]
    decoded = base64.b64decode(b64)
    assert len(decoded) > 0
