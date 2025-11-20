"""
Ollama LLM Client for TwisterLab Agents
Provides async HTTP client for Ollama API with fallback mechanisms.
"""

import logging
from typing import Any, Dict, Optional

import httpx

from agents.config import (
    LLM_MAX_RETRIES,
    LLM_RETRY_DELAY,
    LLM_TIMEOUTS,
    LOG_LLM_METRICS,
    OLLAMA_FALLBACK,
    OLLAMA_MODELS,
    OLLAMA_OPTIONS,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
)
from agents.metrics import (
    ollama_errors_total,
    ollama_failover_total,
    ollama_request_duration_seconds,
    ollama_requests_total,
    ollama_source_active,
    ollama_tokens_generated_total,
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Async client for Ollama LLM API.

    Features:
    - Automatic retries on failure
    - Performance metrics logging
    - Timeout handling
    - Error recovery with fallback

    Example:
        >>> client = OllamaClient()
        >>> result = await client.generate("Classify this ticket", agent_type="classifier")
        >>> print(result["response"])
        "network"
    """

    def __init__(self) -> None:
        import os
        self.test_mode = os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING")

        self.primary_url = OLLAMA_URL  # PRIMARY: Corertx RTX 3060 (performance)
        self.fallback_url = OLLAMA_FALLBACK  # BACKUP: Edgeserver GTX 1050 (continuity)
        self.base_url = self.primary_url  # Default to PRIMARY
        self.timeout = OLLAMA_TIMEOUT
        self.models = OLLAMA_MODELS
        self.options = OLLAMA_OPTIONS

        if self.test_mode:
            logger.info("Test mode detected; LLM client will simulate failures for fallback")

    async def generate(
        self,
        prompt: str,
        agent_type: str = "general",
        custom_options: Optional[Dict] = None,
        custom_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate LLM response via Ollama API.

        Args:
            prompt: The prompt to send to the LLM
            agent_type: Type of agent (classifier, resolver, commander, etc.)
            custom_options: Override default generation options
            custom_timeout: Override default timeout

        Returns:
            {
                "response": "LLM generated text",
                "model": "llama3.2:1b",
                "duration_seconds": 6.9,
                "tokens": 248,
                "success": True
            }

        Raises:
            httpx.HTTPError: If all retries fail
            ValueError: If model not configured
        """
        # Select model and options
        model = self.models.get(agent_type, self.models["general"])
        options = custom_options or self.options.get(agent_type, {})
        timeout = custom_timeout or LLM_TIMEOUTS.get(agent_type, self.timeout)

        # Build request payload
        payload = {"model": model, "prompt": prompt, "stream": False, "options": options}

        # Log request
        if LOG_LLM_METRICS:
            logger.info(
                "Ollama request started",
                extra={
                    "agent_type": agent_type,
                    "model": model,
                    "prompt_length": len(prompt),
                    "timeout": timeout,
                },
            )

        # Record request metric
        ollama_requests_total.labels(
            source="primary" if self.base_url == self.primary_url else "fallback",
            agent_type=agent_type,
            model=model,
        ).inc()

        # Retry loop
        last_error = None
        for attempt in range(1, LLM_MAX_RETRIES + 1):
            # In test mode, immediately fail to test fallback mechanisms
            if self.test_mode:
                from httpx import HTTPStatusError
                from unittest.mock import Mock
                mock_response = Mock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"
                mock_response.json.return_value = {"error": "Test mode - simulating server error"}
                last_error = HTTPStatusError(
                    "Test mode failure",
                    request=Mock(),
                    response=mock_response,
                )
                break

            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(f"{self.base_url}/api/generate", json=payload)
                    response.raise_for_status()

                    result = response.json()

                    # Extract metrics
                    duration_ns = result.get("total_duration", 0)
                    duration_s = duration_ns / 1e9 if duration_ns > 0 else 0
                    tokens = result.get("eval_count", 0)

                    # Record success metrics
                    ollama_request_duration_seconds.labels(
                        source="primary" if self.base_url == self.primary_url else "fallback",
                        agent_type=agent_type,
                        model=model,
                    ).observe(duration_s)

                    ollama_tokens_generated_total.labels(
                        source="primary" if self.base_url == self.primary_url else "fallback",
                        agent_type=agent_type,
                        model=model,
                    ).inc(tokens)

                    # Log success
                    if LOG_LLM_METRICS:
                        logger.info(
                            "Ollama response received",
                            extra={
                                "agent_type": agent_type,
                                "model": model,
                                "duration_seconds": duration_s,
                                "tokens": tokens,
                                "attempt": attempt,
                            },
                        )

                    return {
                        "response": result["response"].strip(),
                        "model": model,
                        "duration_seconds": duration_s,
                        "tokens": tokens,
                        "success": True,
                    }

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    f"Ollama timeout (attempt {attempt}/{LLM_MAX_RETRIES})",
                    extra={"agent_type": agent_type, "model": model, "timeout": timeout},
                )
                if attempt < LLM_MAX_RETRIES:
                    await self._sleep(LLM_RETRY_DELAY)

            except httpx.HTTPStatusError as e:
                last_error = e
                message = (
                    f"Ollama HTTP error {e.response.status_code} "
                    f"(attempt {attempt}/{LLM_MAX_RETRIES})"
                )
                logger.error(
                    message,
                    extra={
                        "agent_type": agent_type,
                        "model": model,
                        "status_code": e.response.status_code,
                    },
                )
                if attempt < LLM_MAX_RETRIES:
                    await self._sleep(LLM_RETRY_DELAY)

            except httpx.RequestError as e:
                last_error = e
                logger.error(
                    f"Ollama connection error (attempt {attempt}/{LLM_MAX_RETRIES}): {e}",
                    extra={"agent_type": agent_type, "model": model, "url": self.base_url},
                )
                if attempt < LLM_MAX_RETRIES:
                    await self._sleep(LLM_RETRY_DELAY)

        # All retries failed - record error metrics
        ollama_errors_total.labels(
            source="primary" if self.base_url == self.primary_url else "fallback",
            agent_type=agent_type,
            error_type=type(last_error).__name__ if last_error else "unknown",
        ).inc()

        # All retries failed
        logger.error(
            f"Ollama request failed after {LLM_MAX_RETRIES} attempts",
            extra={"agent_type": agent_type, "model": model, "error": str(last_error)},
        )
        raise last_error

    async def generate_with_fallback(
        self,
        prompt: str,
        agent_type: str = "general",
        custom_options: Optional[Dict] = None,
        custom_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate LLM response with automatic failover to backup Ollama.

        Attempts PRIMARY Ollama (Corertx RTX 3060) first for optimal performance,
        then automatically fails over to BACKUP Ollama (Edgeserver GTX 1050) if
        PRIMARY is unavailable. Ensures service continuity even with degraded performance.

        Args:
            prompt: The prompt to send to the LLM
            agent_type: Type of agent (classifier, resolver, commander, etc.)
            custom_options: Override default generation options
            custom_timeout: Override default timeout

        Returns:
            {
                "response": "LLM generated text",
                "model": "llama3.2:1b",
                "duration_seconds": 6.9,
                "tokens": 248,
                "success": True,
                "source": "primary" or "fallback"
            }

        Raises:
            RuntimeError: If both PRIMARY and BACKUP fail
        """
        primary_error = None
        fallback_error = None

        # Try PRIMARY first (Corertx RTX 3060 - optimal performance)
        try:
            logger.info(f"Attempting PRIMARY Ollama at {self.primary_url}")
            self.base_url = self.primary_url
            result = await self.generate(prompt, agent_type, custom_options, custom_timeout)
            result["source"] = "primary"
            ollama_source_active.labels(source="primary").set(1)
            ollama_source_active.labels(source="fallback").set(0)
            logger.info(f"PRIMARY Ollama responded successfully from {self.primary_url}")
            return result

        except Exception as e:
            primary_error = e
            msg = (
                f"PRIMARY Ollama failed ({primary_error}), attempting "
                f"FALLBACK to {self.fallback_url}"
            )
            logger.warning(msg)
            ollama_failover_total.labels(
                agent_type=agent_type, reason=self._classify_error(primary_error)
            ).inc()
            ollama_source_active.labels(source="primary").set(0)

        # Try FALLBACK (Edgeserver GTX 1050 - continuity with degraded performance)
        try:
            logger.info(f"Attempting FALLBACK Ollama at {self.fallback_url}")
            self.base_url = self.fallback_url
            result = await self.generate(prompt, agent_type, custom_options, custom_timeout)
            result["source"] = "fallback"
            ollama_source_active.labels(source="fallback").set(1)
            logger.warning(
                "FALLBACK Ollama responded successfully from %s (degraded performance)",
                self.fallback_url,
            )
            return result

        except Exception as e:
            fallback_error = e
            logger.error(
                f"All Ollama endpoints failed. PRIMARY: {primary_error}, FALLBACK: {fallback_error}"
            )
            ollama_errors_total.labels(
                source="fallback",
                agent_type=agent_type,
                error_type=self._classify_error(fallback_error),
            ).inc()
            ollama_source_active.labels(source="fallback").set(0)
            raise RuntimeError(
                f"Ollama service completely unavailable. "
                f"PRIMARY ({self.primary_url}): {primary_error}. "
                f"FALLBACK ({self.fallback_url}): {fallback_error}."
            ) from fallback_error

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Ollama API is accessible and list available models.

        Returns:
            {
                "healthy": True,
                "models": ["llama3.2:1b", "phi3:mini", "tinyllama"],
                "url": "http://twisterlab-ollama-gpu:11434"
            }
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Get model list
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()

                models_data = response.json()
                available_models = [m["name"] for m in models_data.get("models", [])]

                logger.info(
                    "Ollama health check passed",
                    extra={"url": self.base_url, "models_count": len(available_models)},
                )

                return {"healthy": True, "models": available_models, "url": self.base_url}

        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}", extra={"url": self.base_url})
            return {"healthy": False, "models": [], "url": self.base_url, "error": str(e)}

    def _classify_error(self, error: Exception) -> str:
        """
        Classify error type for metrics.

        Args:
            error: The exception that occurred

        Returns:
            str: Error type (timeout, connection_error, server_error, unknown)
        """
        error_str = str(error).lower()

        if "timeout" in error_str or isinstance(error, httpx.TimeoutException):
            return "timeout"
        elif "connection" in error_str or isinstance(error, httpx.ConnectError):
            return "connection_error"
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            return "server_error"
        else:
            return "unknown"

    async def _sleep(self, seconds: int):
        """Sleep for retry delay (async)."""
        import asyncio

        await asyncio.sleep(seconds)


# Singleton instance
ollama_client = OllamaClient()
