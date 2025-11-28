"""
TwisterLab Authentication Module

Provides multiple authentication strategies:
- Azure AD OAuth2 (azure_ad_auth.py)
- Local JWT authentication (local_auth.py)
- Hybrid auto-detection (hybrid_auth.py) - RECOMMENDED

Use HybridAuth for automatic fallback behavior.
"""

from twisterlab.agents.auth.azure_ad_auth import AzureADAuth
from twisterlab.agents.auth.hybrid_auth import HybridAuth
from twisterlab.agents.auth.local_auth import LocalAuth

__all__ = ["AzureADAuth", "LocalAuth", "HybridAuth"]
