"""
Production monitoring and observability configuration
"""

import json
import logging
import logging.handlers
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        return json.dumps(log_entry, default=str)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP metrics"""

    def __init__(self, app, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_endpoint": {},
            "response_times": [],
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Increment request counter
        self.metrics["requests_total"] += 1

        # Track endpoint
        endpoint = f"{request.method} {request.url.path}"
        if endpoint not in self.metrics["requests_by_endpoint"]:
            self.metrics["requests_by_endpoint"][endpoint] = 0
        self.metrics["requests_by_endpoint"][endpoint] += 1

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Track response time
            self.metrics["response_times"].append(process_time)

            # Track status codes
            status = str(response.status_code)
            if status not in self.metrics["requests_by_status"]:
                self.metrics["requests_by_status"][status] = 0
            self.metrics["requests_by_status"][status] += 1

            # Log request details
            self.logger.info(
                f"Request completed: {endpoint}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(process_time * 1000, 2),
                    "user_agent": request.headers.get("user-agent", ""),
                    "client_ip": request.client.host if request.client else "",
                },
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(
                f"Request failed: {endpoint}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": round(process_time * 1000, 2),
                },
                exc_info=True,
            )
            raise


def setup_logging(log_level: str = "INFO", log_file: str = "logs/twisterlab.log") -> logging.Logger:
    """Setup structured logging for production"""

    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)

    # Get log level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("twisterlab")
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # JSON formatter
    json_formatter = JSONFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    return logger


def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0-alpha.1",
        "services": {
            "api": "up",
            "database": "up",  # TODO: Add actual DB health check
            "redis": "up",  # TODO: Add actual Redis health check
            "ollama": "up",  # TODO: Add actual Ollama health check
        },
        "uptime": time.time(),  # TODO: Track actual uptime
    }


def create_health_endpoint():
    """Create health check endpoint"""

    async def health_check():
        return JSONResponse(content=get_health_status(), status_code=200)

    return health_check
