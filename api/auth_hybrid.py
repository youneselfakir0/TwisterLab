"""
Hybrid Authentication for TwisterLab API

Auto-detects and uses:
- Azure AD OAuth2 (if credentials available)
- Local JWT authentication (fallback)

Endpoints:
- /auth/login - Azure AD redirect OR return login form info
- /auth/token - Local username/password auth (POST)
- /auth/callback - Azure AD OAuth2 callback
- /auth/logout - Logout (both modes)
- /auth/me - Get current user
- /auth/status - Get auth mode info

Usage:
    from api.auth_hybrid import get_current_user, router as auth_router
    
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    
    @app.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"message": f"Hello {user['username']}"}
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
import redis.asyncio as aioredis

from agents.auth.hybrid_auth import HybridAuth

logger = logging.getLogger(__name__)

# Router for auth endpoints
router = APIRouter()

# Security scheme for JWT bearer token
security = HTTPBearer()

# Hybrid auth instance (initialized on first request)
_hybrid_auth: Optional[HybridAuth] = None

# Redis client for session management
_redis_client: Optional[aioredis.Redis] = None


def get_hybrid_auth() -> HybridAuth:
    """Get or initialize Hybrid auth instance."""
    global _hybrid_auth
    if _hybrid_auth is None:
        _hybrid_auth = HybridAuth()
        logger.info(f"Hybrid Auth initialized in '{_hybrid_auth.mode}' mode")
    return _hybrid_auth


async def get_redis_client() -> aioredis.Redis:
    """Get or initialize Redis client for session management."""
    global _redis_client
    if _redis_client is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_password = os.getenv("REDIS_PASSWORD")
        
        try:
            _redis_client = await aioredis.from_url(
                f"redis://{redis_host}:{redis_port}",
                password=redis_password,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Session caching disabled.")
            _redis_client = None
    return _redis_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Works in both Azure and Local modes by verifying JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User claims dictionary
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    hybrid_auth = get_hybrid_auth()
    token = credentials.credentials
    
    # Verify token (works in both modes)
    user_claims = await hybrid_auth.verify_token(token)
    
    if not user_claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cache user info in Redis if available
    try:
        redis = await get_redis_client()
        if redis:
            user_id = user_claims.get("sub") or user_claims.get("username")
            cache_key = f"user:{user_id}"
            await redis.setex(cache_key, 3600, str(user_claims))
    except Exception as e:
        logger.warning(f"Failed to cache user in Redis: {e}")
    
    return user_claims


# ==============================================================================
# HYBRID ENDPOINTS (work in both modes)
# ==============================================================================

@router.get("/status")
async def get_auth_status():
    """
    Get authentication system status.
    
    Returns mode (azure/local) and availability info.
    """
    hybrid_auth = get_hybrid_auth()
    return hybrid_auth.get_status()


@router.get("/me")
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Works in both Azure and Local modes.
    """
    return {
        "username": user.get("username") or user.get("sub"),
        "email": user.get("email") or user.get("preferred_username"),
        "roles": user.get("roles", []),
        "auth_mode": get_hybrid_auth().mode,
        "authenticated_at": datetime.now().isoformat()
    }


@router.post("/logout")
async def logout(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout current user (clear session from Redis).
    
    Works in both modes.
    """
    try:
        redis = await get_redis_client()
        if redis:
            user_id = user.get("sub") or user.get("username")
            cache_key = f"user:{user_id}"
            await redis.delete(cache_key)
        
        logger.info(f"User {user.get('username')} logged out successfully")
        
        return {
            "status": "success",
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


# ==============================================================================
# LOCAL MODE ENDPOINTS
# ==============================================================================

@router.post("/token")
async def login_local(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Local authentication with username/password.
    
    Only available in LOCAL mode.
    
    Args:
        form_data: OAuth2 form with username and password
        
    Returns:
        {"access_token": "...", "token_type": "bearer"}
        
    Example:
        curl -X POST http://localhost:8000/auth/token \
          -d "username=admin&password=changeme_admin_2024!"
    """
    hybrid_auth = get_hybrid_auth()
    
    if hybrid_auth.mode != "local":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Local authentication not available in '{hybrid_auth.mode}' mode. Use /auth/login for Azure AD."
        )
    
    # Authenticate user
    user = await hybrid_auth.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = hybrid_auth.create_access_token(
        data={
            "sub": user["username"],
            "username": user["username"],
            "email": user.get("email"),
            "roles": user.get("roles", [])
        }
    )
    
    logger.info(f"User '{user['username']}' authenticated successfully (local mode)")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,  # 1 hour
        "username": user["username"],
        "roles": user.get("roles", [])
    }


# ==============================================================================
# AZURE MODE ENDPOINTS
# ==============================================================================

@router.get("/login")
async def login_azure(request: Request):
    """
    Initiate authentication flow.
    
    - AZURE mode: Redirect to Azure AD
    - LOCAL mode: Return info about /auth/token endpoint
    
    Query params (Azure mode only):
        redirect_uri (optional): URL to redirect after login
    """
    hybrid_auth = get_hybrid_auth()
    
    if hybrid_auth.mode == "azure":
        # Azure AD OAuth2 flow
        redirect_after_login = request.query_params.get("redirect_uri", "/")
        state = f"redirect={redirect_after_login}"
        auth_url = hybrid_auth.get_authorization_url(state=state)
        
        logger.info(f"Redirecting to Azure AD login: {auth_url}")
        return RedirectResponse(url=auth_url)
    
    else:
        # Local mode - return instructions
        return {
            "mode": "local",
            "message": "Use POST /auth/token with username and password",
            "endpoint": "/auth/token",
            "method": "POST",
            "content_type": "application/x-www-form-urlencoded",
            "example": {
                "username": "admin",
                "password": "your_password"
            },
            "curl_example": 'curl -X POST http://localhost:8000/auth/token -d "username=admin&password=your_password"'
        }


@router.get("/callback")
async def callback_azure(request: Request):
    """
    Azure AD OAuth2 callback endpoint.
    
    Only available in AZURE mode.
    
    Query params:
        code: Authorization code from Azure AD
        state: State parameter with redirect URI
        error (optional): Error code if auth failed
        error_description (optional): Error details
    """
    hybrid_auth = get_hybrid_auth()
    
    if hybrid_auth.mode != "azure":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Azure AD callback not available in '{hybrid_auth.mode}' mode"
        )
    
    # Check for errors
    error = request.query_params.get("error")
    if error:
        error_desc = request.query_params.get("error_description", "Unknown error")
        logger.error(f"Azure AD auth error: {error} - {error_desc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {error_desc}"
        )
    
    # Get authorization code
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code"
        )
    
    # Exchange code for token
    token_response = await hybrid_auth.acquire_token_by_code(code)
    
    # Extract redirect URI from state
    state = request.query_params.get("state", "")
    redirect_uri = "/"
    if state.startswith("redirect="):
        redirect_uri = state.split("=", 1)[1]
    
    access_token = token_response.get("access_token")
    
    logger.info(f"Successfully authenticated user via Azure AD, redirecting to {redirect_uri}")
    
    # TODO: In production, use httponly cookies instead of returning token
    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": token_response.get("expires_in", 3600),
        "redirect_uri": redirect_uri,
        "message": "Include this token in Authorization header: Bearer <access_token>"
    }
