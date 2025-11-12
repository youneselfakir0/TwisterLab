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
        async def route_to_mcp(self, *args, **kwargs):
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
        self.mcp_router = MCPRouter()

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

    async def update_health_status(
        self, healthy: bool, details: Dict[str, Any] = None
    ) -> None:
        """
        Update agent health status.

        Args:
            healthy: Whether agent is healthy
            details: Additional health details
        """
        self.is_healthy = healthy
        if details:
            self.health_status_details.update(details)

        await self.audit_log(
            "health_status_update", {"healthy": healthy, "details": details}
        )

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
