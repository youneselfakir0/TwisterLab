"""API package for TwisterLab.
This file intentionally avoids importing many of the optional dependencies at package import
time; instead, route modules should import optional functionality lazily inside function calls.
"""

from . import main  # Expose main on package import

__all__ = ["main"]
