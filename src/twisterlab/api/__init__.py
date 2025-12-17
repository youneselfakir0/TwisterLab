"""API package for TwisterLab.
This file intentionally avoids importing many of the optional dependencies at package import
time; instead, route modules should import optional functionality lazily inside function calls.
"""

import sys

# CRITICAL: Add /app to sys.path BEFORE any imports to ensure twisterlab package is found
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from . import main  # Expose main on package import

__all__ = ["main"]
