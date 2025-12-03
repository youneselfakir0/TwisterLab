import inspect
from typing import Any

import anyio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from twisterlab.agents.real.browser_screenshot_agent import BrowserScreenshotAgent

router = APIRouter(tags=["browser"])


class VisitRequest(BaseModel):
    url: str


@router.post("/visit")
async def visit_endpoint(req: VisitRequest) -> Any:
    url = req.url
    if not url:
        raise HTTPException(status_code=400, detail="Missing url")
    agent = BrowserScreenshotAgent()
    # Prefer async screenshotting if the agent provides an async API, otherwise run sync code in a thread
    try:
        if hasattr(agent, "visit_async") and inspect.iscoroutinefunction(
            agent.visit_async
        ):
            screenshot = await agent.visit_async(url)
        else:
            screenshot = await anyio.to_thread.run_sync(agent.visit, url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"screenshot": screenshot}
