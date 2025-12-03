#!/usr/bin/env python3
"""
Cross-platform pinning of dependencies using pip-tools.
This script creates a requirements.in and compiles a pinned requirements.txt with hashes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    print("+ ", " ".join(cmd))
    result = subprocess.run(cmd)
    return result.returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    req_in = root / "requirements.in"
    req_out = root / "requirements.txt"

    requirements_in = """
# Core Framework
fastapi>=0.115.0
pydantic>=2.9.0
uvicorn[standard]>=0.32.0
starlette>=0.41.0

# Database
asyncpg>=0.29.0
sqlalchemy[asyncio]>=2.0.0
alembic>=1.13.0

# Communication
httpx>=0.27.0
websockets>=13.1
msgpack>=1.1.0

# AI/LLM
openai>=1.54.0
anthropic>=0.39.0

# Monitoring
prometheus-client>=0.21.0
opentelemetry-api>=1.27.0
opentelemetry-sdk>=1.27.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.0
pydantic-settings>=2.6.0
"""

    req_in.write_text(requirements_in)
    print(f"Wrote {req_in}")

    # Ensure pip-tools installed
    rc = run([sys.executable, "-m", "pip", "install", "pip-tools"])
    if rc != 0:
        return rc

    # Run pip-compile
    rc = run(
        [
            sys.executable,
            "-m",
            "piptools",
            "compile",
            "--generate-hashes",
            "--output-file",
            str(req_out),
            str(req_in),
        ]
    )
    if rc != 0:
        return rc

    print(f"Pinned dependencies to {req_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
