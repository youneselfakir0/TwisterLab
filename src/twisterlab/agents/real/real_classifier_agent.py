"""
Minimal RealClassifierAgent for demo/testing.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from twisterlab.agents.base import TwisterAgent


class RealClassifierAgent(TwisterAgent):
    def __init__(self) -> None:
        super().__init__(
            name="real-classifier",
            display_name="Real Classifier Agent",
            description="Performs classification tasks (e.g., ticket categories)",
            role="classifier",
            tools=[{"type": "function", "function": {"name": "classify_text"}}],
        )

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        return {"status": "classified", "task": task}


__all__ = ["RealClassifierAgent"]
