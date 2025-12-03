from __future__ import annotations

import os

try:
    # Prefer the internal twisterlab implementation if present
    from twisterlab.utils.secret_manager import (
        read_secret_file as _read_secret_file,  # type: ignore
    )
except Exception:

    def _read_secret_file(name: str, default: str | None = None) -> str | None:
        return os.environ.get(name, default)


def read_secret_file(name: str, default: str | None = None) -> str | None:
    return _read_secret_file(name, default)
