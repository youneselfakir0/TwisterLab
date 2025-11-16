# =============================================================================
# TWISTERLAB SSO/LDAP UNIFIED AUTHENTICATION
# Centralized authentication for all TwisterLab modules
# =============================================================================

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ldap3 import ALL, NTLM, Connection, Server
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# LDAP configuration
LDAP_SERVER = os.getenv("LDAP_SERVER", "ldap://192.168.0.10:389")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "DC=twisterlab,DC=local")
LDAP_USER_DN = os.getenv("LDAP_USER_DN", "CN=Users,DC=twisterlab,DC=local")
LDAP_BIND_USER = os.getenv("LDAP_BIND_USER", "CN=twisterlab,CN=Users,DC=twisterlab,DC=local")
LDAP_BIND_PASSWORD = os.getenv("LDAP_BIND_PASSWORD", "")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class SSOAuthManager:
    """
    Unified SSO/LDAP authentication manager for TwisterLab
    Supports:
    - LDAP/Active Directory authentication
    - JWT token generation and validation
    - Role-based access control (RBAC)
    - Session management
    """

    def __init__(self):
        self.ldap_server = Server(LDAP_SERVER, get_info=ALL)
        self.sessions = {}  # In-memory session store (use Redis in production)

    def authenticate_ldap(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user against LDAP/Active Directory

        Args:
            username: User's username or email
            password: User's password

        Returns:
            User information dict if successful, None otherwise
        """
        try:
            # Construct user DN
            user_dn = f"CN={username},{LDAP_USER_DN}"

            # Attempt LDAP bind
            conn = Connection(
                self.ldap_server, user=user_dn, password=password, authentication=NTLM
            )

            if not conn.bind():
                logger.warning(f"LDAP authentication failed for user: {username}")
                return None

            # Search for user attributes
            conn.search(
                search_base=LDAP_BASE_DN,
                search_filter=f"(cn={username})",
                attributes=["cn", "mail", "memberOf", "displayName"],
            )

            if not conn.entries:
                logger.warning(f"User not found in LDAP: {username}")
                return None

            entry = conn.entries[0]

            # Extract user info and roles
            user_info = {
                "username": str(entry.cn),
                "email": str(entry.mail) if hasattr(entry, "mail") else None,
                "display_name": (
                    str(entry.displayName) if hasattr(entry, "displayName") else username
                ),
                "groups": [str(g) for g in entry.memberOf] if hasattr(entry, "memberOf") else [],
                "roles": self._extract_roles(entry.memberOf if hasattr(entry, "memberOf") else []),
            }

            conn.unbind()
            logger.info(f"LDAP authentication successful for user: {username}")
            return user_info

        except Exception as e:
            logger.error(f"LDAP authentication error: {e}", exc_info=True)
            return None

    def _extract_roles(self, groups: list) -> list:
        """Extract TwisterLab roles from LDAP groups"""
        role_mapping = {
            "TwisterLab-Admins": "admin",
            "TwisterLab-Operators": "operator",
            "TwisterLab-Users": "user",
            "TwisterLab-Readonly": "readonly",
        }

        roles = []
        for group in groups:
            group_cn = group.split(",")[0].replace("CN=", "")
            if group_cn in role_mapping:
                roles.append(role_mapping[group_cn])

        return roles or ["user"]  # Default role

    def create_access_token(self, user_info: Dict[str, Any]) -> str:
        """
        Create JWT access token for authenticated user

        Args:
            user_info: User information from LDAP

        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": user_info["username"],
            "email": user_info.get("email"),
            "display_name": user_info.get("display_name"),
            "roles": user_info.get("roles", ["user"]),
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "twisterlab-sso",
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Store session
        self.sessions[user_info["username"]] = {
            "token": token,
            "user_info": user_info,
            "created_at": datetime.utcnow(),
            "expires_at": expire,
        }

        return token

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return user info

        Args:
            token: JWT token string

        Returns:
            User payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check if token is expired
            exp = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > exp:
                logger.warning("Token expired")
                return None

            return payload

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def logout(self, username: str) -> bool:
        """
        Logout user and invalidate session

        Args:
            username: Username to logout

        Returns:
            True if successful, False otherwise
        """
        if username in self.sessions:
            del self.sessions[username]
            logger.info(f"User logged out: {username}")
            return True
        return False

    def check_permission(self, user_info: Dict[str, Any], required_role: str) -> bool:
        """
        Check if user has required role/permission

        Args:
            user_info: User information from token
            required_role: Required role (admin, operator, user, readonly)

        Returns:
            True if user has permission, False otherwise
        """
        role_hierarchy = {"admin": 4, "operator": 3, "user": 2, "readonly": 1}

        user_roles = user_info.get("roles", ["readonly"])
        user_level = max(role_hierarchy.get(role, 0) for role in user_roles)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level


# Global SSO manager instance
sso_manager = SSOAuthManager()


# FastAPI dependency for authentication
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user

    Usage:
        @app.get("/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            return {"message": f"Hello {user['display_name']}"}
    """
    token = credentials.credentials
    user_info = sso_manager.validate_token(token)

    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_info


# FastAPI dependency for role-based access
def require_role(required_role: str):
    """
    FastAPI dependency factory for role-based access control

    Usage:
        @app.delete("/admin/service/{service_id}")
        async def delete_service(
            service_id: str,
            user: Dict = Depends(require_role("admin"))
        ):
            # Only admins can access this
    """

    async def role_checker(user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
        if not sso_manager.check_permission(user, required_role):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return user

    return role_checker


# Authentication endpoints (to be added to main API)
async def login_endpoint(username: str, password: str) -> Dict[str, Any]:
    """
    Login endpoint for SSO authentication

    Returns:
        {
            "access_token": "jwt_token_here",
            "token_type": "bearer",
            "user": {...},
            "expires_in": 3600
        }
    """
    # Authenticate against LDAP
    user_info = sso_manager.authenticate_ldap(username, password)

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    access_token = sso_manager.create_access_token(user_info)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user_info["username"],
            "email": user_info["email"],
            "display_name": user_info["display_name"],
            "roles": user_info["roles"],
        },
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def logout_endpoint(user: Dict = Depends(get_current_user)) -> Dict[str, str]:
    """
    Logout endpoint

    Returns:
        {"message": "Logged out successfully"}
    """
    sso_manager.logout(user["sub"])
    return {"message": "Logged out successfully"}


async def me_endpoint(user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user info endpoint

    Returns:
        User information from JWT token
    """
    return {
        "username": user["sub"],
        "email": user.get("email"),
        "display_name": user.get("display_name"),
        "roles": user.get("roles", []),
    }
