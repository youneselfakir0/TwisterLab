# TwisterLang Core Package
"""
Core modules for TwisterLang encoding/decoding functionality and settings.
"""

from .settings import Settings, get_settings, load_environment_config

__version__ = "1.0.0"

__all__ = ["Settings", "get_settings", "load_environment_config"]
