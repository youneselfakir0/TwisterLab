"""
Ollama LLM Client for TwisterLab Agents
Provides async HTTP client for Ollama API with fallback mechanisms.
"""
import httpx
import logging
from typing import Optional, Dict, Any
from agents.config import (
    OLLAMA_URL,
    OLLAMA_TIMEOUT,
    OLLAMA_MODELS,
    OLLAMA_OPTIONS,
    LLM_TIMEOUTS,
    LLM_MAX_RETRIES,
    LLM_RETRY_DELAY,
    LOG_LLM_METRICS
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

    def __init__(self):
        self.base_url = OLLAMA_URL
        self.timeout = OLLAMA_TIMEOUT
        self.models = OLLAMA_MODELS
        self.options = OLLAMA_OPTIONS

    async def generate(
        self,
        prompt: str,
        agent_type: str = "general",
        custom_options: Optional[Dict] = None,
        custom_timeout: Optional[int] = None
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
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }

        # Log request
        if LOG_LLM_METRICS:
            logger.info(
                f"Ollama request started",
                extra={
                    "agent_type": agent_type,
                    "model": model,
                    "prompt_length": len(prompt),
                    "timeout": timeout
                }
            )

        # Retry loop
        last_error = None
        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload
                    )
                    response.raise_for_status()

                    result = response.json()

                    # Extract metrics
                    duration_ns = result.get("total_duration", 0)
                    duration_s = duration_ns / 1e9 if duration_ns > 0 else 0
                    tokens = result.get("eval_count", 0)

                    # Log success
                    if LOG_LLM_METRICS:
                        logger.info(
                            f"Ollama response received",
                            extra={
                                "agent_type": agent_type,
                                "model": model,
                                "duration_seconds": duration_s,
                                "tokens": tokens,
                                "attempt": attempt
                            }
                        )

                    return {
                        "response": result["response"].strip(),
                        "model": model,
                        "duration_seconds": duration_s,
                        "tokens": tokens,
                        "success": True
                    }

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    f"Ollama timeout (attempt {attempt}/{LLM_MAX_RETRIES})",
                    extra={
                        "agent_type": agent_type,
                        "model": model,
                        "timeout": timeout
                    }
                )
                if attempt < LLM_MAX_RETRIES:
                    await self._sleep(LLM_RETRY_DELAY)

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.error(
                    f"Ollama HTTP error {e.response.status_code} (attempt {attempt}/{LLM_MAX_RETRIES})",
                    extra={
                        "agent_type": agent_type,
                        "model": model,
                        "status_code": e.response.status_code
                    }
                )
                if attempt < LLM_MAX_RETRIES:
                    await self._sleep(LLM_RETRY_DELAY)

            except httpx.RequestError as e:
                last_error = e
                logger.error(
                    f"Ollama connection error (attempt {attempt}/{LLM_MAX_RETRIES}): {e}",
                    extra={
                        "agent_type": agent_type,
                        "model": model,
                        "url": self.base_url
                    }
                )
                if attempt < LLM_MAX_RETRIES:
                    await self._sleep(LLM_RETRY_DELAY)

        # All retries failed
        logger.error(
            f"Ollama request failed after {LLM_MAX_RETRIES} attempts",
            extra={
                "agent_type": agent_type,
                "model": model,
                "error": str(last_error)
            }
        )
        raise last_error

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
                    f"Ollama health check passed",
                    extra={
                        "url": self.base_url,
                        "models_count": len(available_models)
                    }
                )

                return {
                    "healthy": True,
                    "models": available_models,
                    "url": self.base_url
                }

        except Exception as e:
            logger.warning(
                f"Ollama health check failed: {e}",
                extra={"url": self.base_url}
            )
            return {
                "healthy": False,
                "models": [],
                "url": self.base_url,
                "error": str(e)
            }

    async def _sleep(self, seconds: int):
        """Sleep for retry delay (async)."""
        import asyncio
        await asyncio.sleep(seconds)


# Singleton instance
ollama_client = OllamaClient()
