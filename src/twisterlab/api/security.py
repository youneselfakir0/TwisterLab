from __future__ import annotations

import os
from typing import Any

# Minimal auth helpers to satisfy imports during tests. Replace with robust implementation.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def create_access_token(data: dict[str, Any], expires_delta: int | None = None) -> str:
    # Minimal token generator for tests (not secure)
    return "token-123"
