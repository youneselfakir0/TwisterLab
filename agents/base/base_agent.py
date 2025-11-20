"""
BaseAgent - Foundation class for all TwisterLab autonomous agents.

This module provides the base class that all agents must inherit from,
ensuring consistent behavior, MCP communication, audit logging, and
security practices across the entire agent ecosystem.

All agents MUST inherit from BaseAgent to ensure:
- MCP isolation and secure communication
- Comprehensive audit logging
- Standardized error handling
- Credential security
- Performance monitoring
"""

import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List

# Import MCP router for agent communication
try:
    from agents.mcp.mcp_router import MCPRouter
except ImportError:
    # Fallback for development/testing
    class MCPRouter:
        async def route_to_mcp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            return {"status": "mock_response"}


class BaseAgent(ABC):
    """
    Base class for all TwisterLab autonomous agents.

    Provides:
    - MCP communication through isolated router
    - Audit logging for all operations
    - Standardized error handling
    - Credential security management
    - Performance monitoring
    - Health status tracking

    Attributes:
        name: Unique agent identifier
        priority: Agent execution priority (1=highest, 10=lowest)
        capabilities: List of agent capabilities
        mcp_router: Isolated MCP communication router
        logger: Structured logger instance
    """

    def __init__(self):
        """
        Initialize the base agent.

        Subclasses MUST call super().__init__() and then set:
        - self.name
        - self.priority
        - self.capabilities
        """
        self.name = "BaseAgent"
        self.priority = 10  # Default lowest priority
        self.capabilities: List[str] = []

        # MCP communication (isolated per agent)
        # Lazy initialize MCPRouter so test suite can patch MCPRouter class
        # after agent instances are created (tests patch MCPRouter class at
        # import time and expect agents to pick it up on first use).
        self._mcp_router = None

        # Logging setup
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.logger.setLevel(logging.INFO)

        # Performance tracking
        self.operation_count = 0
        self.error_count = 0
        self.last_operation_time = None
        self.average_response_time = 0.0

        # Health status
        self.is_healthy = True
        self.last_health_check = datetime.now()
        self.health_status_details = {}
        # MCP call tracing: count and args for debugging/test validation
        self._mcp_call_count = 0
        self._mcp_call_args = []

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent operation.

        Args:
            context: Operation context and parameters

        Returns:
            Dict containing operation results

        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError("Subclasses must implement execute() method")

    @abstractmethod
    async def _process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process agent-specific logic.

        This method should be overridden by subclasses to implement
        the actual agent functionality.

        Args:
            context: Operation context

        Returns:
            Processing results
        """
        raise NotImplementedError("Subclasses must implement _process() method")

    async def audit_log(self, operation: str, data: Any = None) -> None:
        """
        Log operation for audit trail.

        Args:
            operation: Operation being performed
            data: Additional data to log (sensitive data will be sanitized)
        """
        try:
            # Sanitize sensitive data
            safe_data = self._sanitize_for_logging(data)

            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "operation": operation,
                "data": safe_data,
            }

            # Log to structured logger
            self.logger.info(
                f"Agent operation: {operation}",
                extra={
                    "agent": self.name,
                    "operation": operation,
                    "audit_data": audit_entry,
                },
            )

            # In production, this would also write to secure audit store
            # await self._write_to_audit_store(audit_entry)

        except Exception as e:
            # Fail-safe logging
            self.logger.error(f"Failed to audit log {operation}: {str(e)}")

    def _sanitize_for_logging(self, data: Any) -> Any:
        """
        Sanitize data for logging (remove sensitive information).

        Args:
            data: Data to sanitize

        Returns:
            Sanitized data safe for logging
        """
        if isinstance(data, dict):
            sanitized = {}
            sensitive_keys = {"password", "token", "key", "secret", "credentials"}

            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_for_logging(value)
            return sanitized

        elif isinstance(data, list):
            return [self._sanitize_for_logging(item) for item in data]

        elif isinstance(data, str) and len(data) > 100:
            # Truncate long strings
            return data[:100] + "..."

        else:
            return data

    def get_capabilities(self) -> List[str]:
        """
        Return the agent capabilities; default belongs to BaseAgent and
        can be overridden by subclasses.
        """
        return getattr(self, "capabilities", [])

    async def _call_mcp(
        self, mcp_name: str, operation: str, params: Dict[str, Any] = None, agent_name: str = None
    ) -> Dict[str, Any]:
        """Proxy to route_to_mcp that collects call tracing and supports tests.

        Args:
            mcp_name: MCP name to call
            operation: operation
            params: parameters dict
            agent_name: override agent name (default self.name)
        Returns:
            The MCP response
        """
        if params is None:
            params = {}
        if agent_name is None:
            agent_name = self.name

        # Record call args for debugging
        try:
            self._mcp_call_count += 1
            self._mcp_call_args.append(
                {
                    "mcp_name": mcp_name,
                    "operation": operation,
                    "params": params,
                }
            )
        except Exception:
            pass

        # Optional: increment Prometheus metric if available. This is a best-effort
        # integration that won't fail tests if prometheus_client isn't installed.
        try:
            if getattr(self, "_prometheus_counter", None) is None:
                try:
                    from prometheus_client import Counter

                    self._prometheus_counter = Counter(
                        "twisterlab_mcp_calls_total",
                        "Total MCP calls per agent",
                        ["agent", "operation"],
                    )
                except Exception:
                    self._prometheus_counter = None
            if self._prometheus_counter is not None:
                try:
                    self._prometheus_counter.labels(agent=self.name, operation=operation).inc()
                except Exception:
                    # Metric collection should never break agent execution
                    pass
        except Exception:
            pass
        # Perform the call using the existing router property
        return await self.mcp_router.route_to_mcp(
            agent_name=agent_name, mcp_name=mcp_name, operation=operation, params=params
        )

    @property
    def mcp_router(self):
        """Lazily instantiate the MCPRouter on first access.

        This allows tests that patch the MCPRouter class to replace router
        behavior at test time even if agent instances were created earlier.
        """
        if getattr(self, "_mcp_router", None) is None:
            # Import MCPRouter dynamically to respect patches made directly
            # to the MCPRouter symbol in 'agents.mcp.mcp_router' during tests.
            from importlib import import_module

            mcp_mod = import_module("agents.mcp.mcp_router")
            RouterClass = getattr(mcp_mod, "MCPRouter")
            # Instantiate using the (possibly patched) RouterClass
            try:
                self.logger.debug("Instantiating MCPRouter with class: %s", RouterClass)
            except Exception:
                pass
            self._mcp_router = RouterClass()
            try:
                self.logger.debug("MCPRouter instance created: %s", type(self._mcp_router))
            except Exception:
                pass
        return self._mcp_router

    @mcp_router.setter
    def mcp_router(self, value):
        self._mcp_router = value

    @mcp_router.deleter
    def mcp_router(self):
        """Delete the cached MCPRouter instance on the agent.

        This supports tests that patch `agent.mcp_router` at instance-level
        and expect `delattr(agent, 'mcp_router')` to restore the original
        state. Clearing `_mcp_router` allows the property to lazily
        re-instantiate the router on next access.
        """
        self._mcp_router = None

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get a default health status response. Subclasses may override to provide
        more detailed health information.
        """
        return {
            "status": "healthy" if getattr(self, "is_healthy", True) else "unhealthy",
            "uptime": 0,
            "details": getattr(self, "health_status_details", {}),
        }

    def reset_mcp_trace(self) -> None:
        """Reset MCP call tracing counters for tests.

        This is useful for unit/integration tests which want to assert
        the number of MCP calls performed by an agent during an operation.
        """
        try:
            self._mcp_call_count = 0
            self._mcp_call_args = []
        except Exception:
            pass

    def get_mcp_call_count(self) -> int:
        """Return how many MCP calls this agent made since the last
        reset (or since initialization).
        """
        return getattr(self, "_mcp_call_count", 0)

    def _validate_context(self, context: Dict[str, Any]) -> None:
        """
        Validate operation context.

        Default implementation ensures the context is a mapping. Subclasses
        may override for stricter validation.
        """
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")


def accepts_context_or_task(func):
    """
    Decorator to normalize execute() calls so they accept either:
      - execute(context: Dict)
      - execute(task: str, context: Dict)
    It inspects the underlying function signature and dispatches accordingly.
    """
    import inspect

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    async def wrapper(self, *args, **kwargs):
        # If called as execute(context)
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            context = args[0]
            if "context" in params and len(params) == 2:
                return await func(self, context)
            # else expect (task, context)
            task = context.get("operation", "execute")
            return await func(self, task, context)

        # If called as execute(task, context)
        if len(args) >= 2:
            return await func(self, *args, **kwargs)

        # If called with kwargs only
        context = kwargs.get("context") or kwargs.get("task")
        if isinstance(context, dict) and "context" in params and len(params) == 2:
            return await func(self, context)
        # Try to build task/context
        task = kwargs.get("task") or (
            context.get("operation") if isinstance(context, dict) else "execute"
        )
        return await func(self, task, context)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

    @asynccontextmanager
    async def operation_context(self, operation_name: str):
        """
        Context manager for operation timing and error handling.

        Usage:
            async with self.operation_context('my_operation'):
                # Perform operation
                result = await self._do_something()
                return result
        """
        start_time = datetime.now()
        operation_id = f"{self.name}_{operation_name}_{int(start_time.timestamp())}"

        try:
            await self.audit_log(f"{operation_name}_start")
            yield operation_id

        except Exception as e:
            self.error_count += 1
            await self.audit_log(f"{operation_name}_failed", {"error": str(e)})
            raise

        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Update performance metrics
            self.operation_count += 1
            self.last_operation_time = end_time

            # Rolling average response time
            if self.operation_count == 1:
                self.average_response_time = duration
            else:
                self.average_response_time = (
                    (self.average_response_time * (self.operation_count - 1)) + duration
                ) / self.operation_count

            await self.audit_log(
                f"{operation_name}_complete",
                {"duration_seconds": duration, "operation_id": operation_id},
            )

    def _validate_context(self, context: Dict[str, Any]) -> None:
        """
        Validate operation context.

        Args:
            context: Context to validate

        Raises:
            ValueError: If context is invalid
        """
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")

        # Subclasses can override this for specific validation

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get agent health status.

        Returns:
            Dict containing health information
        """
        self.last_health_check = datetime.now()

        return {
            "agent": self.name,
            "healthy": self.is_healthy,
            "last_check": self.last_health_check.isoformat(),
            "operation_count": self.operation_count,
            "error_count": self.error_count,
            "average_response_time": round(self.average_response_time, 3),
            "capabilities": self.capabilities,
            "details": self.health_status_details,
        }

    async def update_health_status(self, healthy: bool, details: Dict[str, Any] = None) -> None:
        """
        Update agent health status.

        Args:
            healthy: Whether agent is healthy
            details: Additional health details
        """
        self.is_healthy = healthy
        if details:
            self.health_status_details.update(details)

        await self.audit_log("health_status_update", {"healthy": healthy, "details": details})

    def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities.

        Returns:
            List of agent capabilities
        """
        return self.capabilities.copy()

    def has_capability(self, capability: str) -> bool:
        """
        Check if agent has specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if agent has capability
        """
        return capability in self.capabilities

    async def cleanup(self) -> None:
        """
        Cleanup agent resources.

        Called when agent is being shut down.
        Subclasses should override to cleanup their specific resources.
        """
        await self.audit_log(
            "agent_cleanup",
            {
                "final_operation_count": self.operation_count,
                "final_error_count": self.error_count,
            },
        )

    def __str__(self) -> str:
        """String representation of agent."""
        return f"{self.name}(priority={self.priority}, capabilities={len(self.capabilities)})"

    def __repr__(self) -> str:
        """Detailed string representation of agent."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"priority={self.priority}, "
            f"capabilities={self.capabilities})"
        )
