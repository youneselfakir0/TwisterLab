"""
Minimal RealSyncAgent implementation for the AgentRegistry.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from twisterlab.agents.base import TwisterAgent


class RealSyncAgent(TwisterAgent):
    def __init__(self) -> None:
        super().__init__(
            name="real-sync",
            display_name="Real Sync Agent",
            description="Performs sync operations across agents",
            role="sync",
            tools=[{"type": "function", "function": {"name": "sync_now"}}],
        )

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        return {"status": "ok", "task": task}


__all__ = ["RealSyncAgent"]
