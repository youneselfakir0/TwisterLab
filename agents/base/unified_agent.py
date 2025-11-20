"""
Compatibility shim for legacy UnifiedAgentBase and AgentStatus

Some modules still import from `agents.base.unified_agent`. This file
provides a small compatibility layer which re-exports the project's
`TwisterAgent` base class and a lightweight `AgentStatus` Enum so that
older imports continue to work without refactoring the whole codebase.
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from agents.base import TwisterAgent


class AgentStatus(str, Enum):
    """Simple agent lifecycle status enum (compatibility shim)."""

    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    FAILED = "FAILED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    ERROR = "ERROR"


class UnifiedAgentBase(TwisterAgent):
    """Compatibility subclass which mirrors the previous UnifiedAgentBase API.

    Keep this thin: it behaves like TwisterAgent but adds a `status` attribute
    and a convenience `version` argument used in some legacy code paths.
    """

    def __init__(
        self,
        name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        role: str = "assistant",
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "llama-3.2",
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
    ) -> None:
        try:
            super().__init__(
                name=name,
                display_name=display_name or name,
                description=description or "",
                role=role,
                tools=tools,
                model=model,
                temperature=temperature,
                metadata=metadata,
            )
        except TypeError:
            # Some older BaseAgent signatures don't accept kwargs. Call default
            # constructor then set the expected attributes for compatibility.
            super().__init__()
            self.name = name
            self.display_name = display_name or name
            self.description = description or ""
            self.role = role
            self.tools = tools or []
            self.model = model
            self.temperature = temperature
            self.metadata = metadata or {}
        self.version = version or "1.0"
        self.status = AgentStatus.INITIALIZING

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None):
        """Default execute method for compatibility; subclasses usually override it."""
        raise NotImplementedError("execute() must be implemented by subclass")

    async def _process(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compatibility: provide BaseAgent._process behavior by delegating
        to the newer `execute` method pattern where possible.

        Many legacy agents implement execute(...) or operation-specific methods
        like _sync_all. To avoid forcing a large refactor across all files,
        provide a fallback that calls execute() when subclasses don't implement
        _process directly.
        """
        if hasattr(self, "execute"):
            # `execute` may expect a task string + context. If a dict is passed in
            # as context, try to use the 'operation' field as the task.
            if isinstance(context, dict):
                task = context.get("operation", "execute")
            else:
                task = "execute"
            try:
                return await self.execute(task, context)
            except TypeError:
                # Some agents implement execute(context) only; support that signature too
                return await self.execute(context)
        raise NotImplementedError("_process() must be implemented by subclass")
