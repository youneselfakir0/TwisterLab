"""
Hybrid Authentication System for TwisterLab

Automatically detects and uses:
1. Azure AD OAuth2 (if credentials available)
2. Local JWT authentication (fallback)

This allows TwisterLab to work with or without Azure AD, providing
maximum flexibility for different deployment scenarios.

Usage:
    hybrid_auth = HybridAuth()
    print(f"Auth mode: {hybrid_auth.mode}")  # "azure" or "local"
    
    # Authenticate (method depends on mode)
    if hybrid_auth.mode == "azure":
        auth_url = hybrid_auth.get_authorization_url()
    else:
        user = await hybrid_auth.authenticate("admin", "password")
"""

import logging
import os
from typing import Any, Dict, Optional

from agents.auth.azure_ad_auth import AzureADAuth
from agents.auth.local_auth import LocalAuth

logger = logging.getLogger(__name__)


class HybridAuth:
    """
    Hybrid authentication system that auto-detects Azure AD availability.
    
    Modes:
        - "azure": Azure AD OAuth2 (requires AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
        - "local": Local JWT authentication (fallback)
    
    The system automatically chooses the best mode based on:
    1. Environment variables presence
    2. Azure AD initialization success
    
    Attributes:
        mode (str): Current auth mode ("azure" or "local")
        azure_auth (AzureADAuth): Azure AD instance (if mode="azure")
        local_auth (LocalAuth): Local auth instance (if mode="local")
    """
    
    def __init__(self):
        """
        Initialize hybrid auth system.
        
        Tries to initialize Azure AD first, falls back to local auth if:
        - Azure credentials are missing
        - Azure AD initialization fails
        - Any exception occurs
        """
        self.mode: str = "local"  # Default to local
        self.azure_auth: Optional[AzureADAuth] = None
        self.local_auth: Optional[LocalAuth] = None
        
        # Check if Azure AD credentials are present
        azure_credentials_present = all([
            os.getenv("AZURE_TENANT_ID"),
            os.getenv("AZURE_CLIENT_ID"),
            os.getenv("AZURE_CLIENT_SECRET"),
        ])
        
        if azure_credentials_present:
            try:
                # Try to initialize Azure AD
                self.azure_auth = AzureADAuth()
                self.mode = "azure"
                logger.info("✅ Hybrid Auth: Azure AD mode enabled")
                logger.info(
                    f"   Tenant: {os.getenv('AZURE_TENANT_ID')[:8]}..., "
                    f"Client: {os.getenv('AZURE_CLIENT_ID')[:8]}..."
                )
            except Exception as e:
                logger.warning(f"⚠️ Azure AD initialization failed: {e}")
                logger.info("   Falling back to local authentication...")
                self._initialize_local_auth()
        else:
            logger.info("ℹ️ Azure AD credentials not found, using local authentication")
            self._initialize_local_auth()
    
    def _initialize_local_auth(self):
        """Initialize local authentication system."""
        try:
            self.local_auth = LocalAuth()
            self.mode = "local"
            logger.info("✅ Hybrid Auth: Local JWT mode enabled")
        except Exception as e:
            logger.error(f"❌ Local auth initialization failed: {e}")
            raise RuntimeError("Failed to initialize any authentication system") from e
    
    # =========================================================================
    # Azure AD Methods (only available in "azure" mode)
    # =========================================================================
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get Azure AD authorization URL (Azure mode only).
        
        Args:
            state: Optional state parameter for OAuth2 flow
            
        Returns:
            Authorization URL to redirect user
            
        Raises:
            RuntimeError: If not in Azure mode
        """
        if self.mode != "azure" or not self.azure_auth:
            raise RuntimeError(
                "get_authorization_url() only available in Azure mode. "
                f"Current mode: {self.mode}"
            )
        
        return self.azure_auth.get_authorization_url(state=state)
    
    async def acquire_token_by_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token (Azure mode only).
        
        Args:
            code: Authorization code from Azure AD callback
            
        Returns:
            Token response with access_token, expires_in, etc.
            
        Raises:
            RuntimeError: If not in Azure mode
        """
        if self.mode != "azure" or not self.azure_auth:
            raise RuntimeError(
                "acquire_token_by_code() only available in Azure mode. "
                f"Current mode: {self.mode}"
            )
        
        return await self.azure_auth.acquire_token_by_code(code)
    
    async def get_app_token(self) -> str:
        """
        Get app-level access token (Azure mode only).
        
        Returns:
            Access token for Microsoft Graph API
            
        Raises:
            RuntimeError: If not in Azure mode
        """
        if self.mode != "azure" or not self.azure_auth:
            raise RuntimeError(
                "get_app_token() only available in Azure mode. "
                f"Current mode: {self.mode}"
            )
        
        return await self.azure_auth.get_app_token()
    
    # =========================================================================
    # Local Auth Methods (only available in "local" mode)
    # =========================================================================
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate with username/password (Local mode only).
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User dict if successful, None otherwise
            
        Raises:
            RuntimeError: If not in Local mode
        """
        if self.mode != "local" or not self.local_auth:
            raise RuntimeError(
                "authenticate_user() only available in Local mode. "
                f"Current mode: {self.mode}"
            )
        
        return await self.local_auth.authenticate_user(username, password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT access token (Local mode only).
        
        Args:
            data: Payload to encode (should include "sub": username)
            
        Returns:
            JWT token string
            
        Raises:
            RuntimeError: If not in Local mode
        """
        if self.mode != "local" or not self.local_auth:
            raise RuntimeError(
                "create_access_token() only available in Local mode. "
                f"Current mode: {self.mode}"
            )
        
        return self.local_auth.create_access_token(data)
    
    # =========================================================================
    # Universal Methods (work in both modes)
    # =========================================================================
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify token (works in both modes).
        
        In Azure mode: Validates Azure AD JWT
        In Local mode: Validates local JWT
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        if self.mode == "azure" and self.azure_auth:
            # For Azure AD, we use the validate_token_structure method
            # In production, implement full JWT verification with Azure public keys
            if self.azure_auth.validate_token_structure(token):
                # Return basic validation success
                # TODO: Implement full Azure AD token verification
                return {"mode": "azure", "validated": True}
            return None
        
        elif self.mode == "local" and self.local_auth:
            return await self.local_auth.verify_token(token)
        
        return None
    
    def get_mode(self) -> str:
        """
        Get current authentication mode.
        
        Returns:
            "azure" or "local"
        """
        return self.mode
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get authentication system status.
        
        Returns:
            Status dict with mode and availability info
        """
        status = {
            "mode": self.mode,
            "provider": "AzureADAuth" if self.mode == "azure" else "LocalAuth",
            "azure_available": self.azure_auth is not None,
            "local_available": self.local_auth is not None,
            "azure_configured": all([
                os.getenv("AZURE_TENANT_ID"),
                os.getenv("AZURE_CLIENT_ID"),
                os.getenv("AZURE_CLIENT_SECRET")
            ])
        }
        
        if self.mode == "azure":
            status["azure_tenant_id"] = os.getenv("AZURE_TENANT_ID", "")[:8] + "..."
            status["azure_client_id"] = os.getenv("AZURE_CLIENT_ID", "")[:8] + "..."
        
        return status
