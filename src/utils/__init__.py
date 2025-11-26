"""Compatibility shim for `utils` top-level package imports.

This package re-exports conveniences from `twisterlab.utils` where possible. It's a
temporary compatibility shim to avoid import errors in tests when modules use the
older `utils.*` import style.
"""

from .secret_manager import read_secret_file

__all__ = ["read_secret_file"]
