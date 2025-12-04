"""
Minimal RealBackupAgent for registry completeness.

Provides a lightweight agent that returns a simple 'backup' response when
executed. Not intended to be feature-complete.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from twisterlab.agents.base import TwisterAgent


class RealBackupAgent(TwisterAgent):
    def __init__(self) -> None:
        super().__init__(
            name="real-backup",
            display_name="Real Backup Agent",
            description="Performs backups and return status",
            role="backup",
            instructions="Triggers backup operations for demo purposes",
            tools=[{"type": "function", "function": {"name": "backup_now"}}],
            model="llama-3.2",
        )

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        return {"status": "ok", "task": task}


__all__ = ["RealBackupAgent"]
