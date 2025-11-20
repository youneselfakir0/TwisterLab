"""
Azure AD OAuth2 Authentication for TwisterLab

Provides secure authentication using Microsoft Azure Active Directory.
Supports both user authentication (OAuth2 flow) and application-level access.
"""

import logging
import os
from typing import Any, Dict, Optional

from fastapi import HTTPException
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class AzureADAuth:
    """
    Azure AD authentication handler for TwisterLab.

    Manages OAuth2 flows for user authentication and application-level
    token acquisition for Microsoft Graph API access.

    Environment Variables Required:
        AZURE_TENANT_ID: Azure AD tenant ID
        AZURE_CLIENT_ID: Application (client) ID
        AZURE_CLIENT_SECRET: Client secret value

    Example:
        >>> auth = AzureADAuth()
        >>> token = await auth.get_app_token()
        >>> print(f"Access token: {token[:20]}...")
    """

    def __init__(self):
        """Initialize Azure AD authentication handler."""
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")

        if not all([self.client_id, self.tenant_id, self.client_secret]):
            raise ValueError(
                "Missing Azure AD credentials in environment. "
                "Required: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET"
            )

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]

        self.app = ConfidentialClientApplication(
            self.client_id, authority=self.authority, client_credential=self.client_secret
        )

        logger.info(
            "AzureADAuth initialized successfully",
            extra={
                "tenant_id": self.tenant_id,
                "client_id": self.client_id,
                "authority": self.authority,
            },
        )

    async def get_app_token(self) -> str:
        """
        Get application-level access token for Microsoft Graph API.

        Returns:
            str: Access token for API requests

        Raises:
            HTTPException: If token acquisition fails

        Example:
            >>> token = await auth.get_app_token()
        """
        try:
            result = self.app.acquire_token_for_client(scopes=self.scopes)

            if "access_token" in result:
                logger.info("Application token acquired successfully")
                return result["access_token"]

            error = result.get("error_description", result.get("error", "Unknown error"))
            logger.error(f"Token acquisition failed: {error}")
            raise HTTPException(status_code=500, detail=f"Azure AD authentication failed: {error}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token acquisition: {e}")
            raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

    def get_authorization_url(
        self, redirect_uri: str, state: Optional[str] = None, scopes: Optional[list[str]] = None
    ) -> str:
        """
        Generate OAuth2 authorization URL for user login.

        Args:
            redirect_uri: URL to redirect after authentication
            state: Optional state parameter for CSRF protection
            scopes: Optional list of scopes (default: ["User.Read"])

        Returns:
            str: Authorization URL to redirect user to

        Example:
            >>> url = auth.get_authorization_url("http://localhost:8000/auth/callback")
            >>> print(url)
            https://login.microsoftonline.com/.../authorize?...
        """
        scopes = scopes or ["User.Read"]

        return self.app.get_authorization_request_url(
            scopes=scopes, redirect_uri=redirect_uri, state=state
        )

    async def acquire_token_by_code(
        self, code: str, redirect_uri: str, scopes: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Called in the OAuth2 callback after user authenticates.

        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization request
            scopes: Optional list of scopes (default: ["User.Read"])

        Returns:
            dict: Token response containing access_token, refresh_token, etc.

        Raises:
            HTTPException: If token exchange fails

        Example:
            >>> result = await auth.acquire_token_by_code(code, redirect_uri)
            >>> access_token = result["access_token"]
        """
        scopes = scopes or ["User.Read"]

        try:
            result = self.app.acquire_token_by_authorization_code(
                code=code, scopes=scopes, redirect_uri=redirect_uri
            )

            if "access_token" in result:
                logger.info("User token acquired via authorization code")
                return result

            error = result.get("error_description", result.get("error", "Unknown error"))
            logger.error(f"Token exchange failed: {error}")
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {error}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            raise HTTPException(status_code=500, detail=f"Token exchange error: {str(e)}")

    def validate_token_structure(self, token: str) -> bool:
        """
        Validate token structure (basic check, not signature verification).

        Args:
            token: JWT token to validate

        Returns:
            bool: True if token structure is valid (3 parts separated by dots)
        """
        try:
            parts = token.split(".")
            return len(parts) == 3 and all(len(part) > 0 for part in parts)
        except Exception:
            return False
