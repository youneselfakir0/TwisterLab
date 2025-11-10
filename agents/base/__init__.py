"""
TwisterLab Base Agent Module.

This module provides the foundation classes for all autonomous agents
in the TwisterLab system.
"""

from .base_agent import BaseAgent

# Alias for backward compatibility
TwisterAgent = BaseAgent

__all__ = ["BaseAgent", "TwisterAgent"]
