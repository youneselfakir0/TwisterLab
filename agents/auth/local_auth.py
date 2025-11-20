"""
Local Authentication System for TwisterLab

Fallback authentication when Azure AD is unavailable (no credits, trial expired).
Provides:
- Username/password authentication with bcrypt
- JWT token generation and verification
- Local user database (in-memory or PostgreSQL)
- Role-based access control

Usage:
    local_auth = LocalAuth()
    user = await local_auth.authenticate_user("admin", "password123")
    token = local_auth.create_access_token({"sub": user["username"]})

    verified = await local_auth.verify_token(token)
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LocalAuth:
    """
    Local authentication system with JWT tokens.

    Features:
    - Bcrypt password hashing
    - HS256 JWT tokens
    - In-memory user database (can be replaced with PostgreSQL)
    - Role-based access control

    Environment Variables:
        JWT_SECRET_KEY: Secret key for JWT signing (min 32 chars)
        JWT_ALGORITHM: Algorithm for JWT (default: HS256)
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time (default: 60)
    """

    def __init__(self):
        """Initialize local auth system."""
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be set and at least 32 characters. "
                "Generate with: openssl rand -hex 32"
            )

        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # In-memory user database
        # TODO: Replace with PostgreSQL queries for production
        self.users_db = self._initialize_default_users()

        logger.info(
            f"LocalAuth initialized (algorithm={self.algorithm}, "
            f"token_ttl={self.access_token_expire_minutes}m)"
        )

    def _initialize_default_users(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize default users from environment or hardcoded.

        In production, load from PostgreSQL:
            SELECT username, hashed_password, roles FROM users;

        Returns:
            Dictionary of users: {username: {hashed_password, roles, ...}}
        """
        # Default admin user (CHANGE PASSWORD IN PRODUCTION!)
        # Bcrypt has 72 byte limit, so truncate if needed
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")[:72]

        return {
            "admin": {
                "username": "admin",
                "hashed_password": pwd_context.hash(admin_password),
                "email": "admin@twisterlab.local",
                "roles": ["admin", "user"],
                "enabled": True,
            },
            # Add more users here or load from database
        }

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against bcrypt hash.

        Args:
            plain_password: Plain text password from user
            hashed_password: Bcrypt hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    def hash_password(self, plain_password: str) -> str:
        """
        Hash password with bcrypt.

        Args:
            plain_password: Plain text password (will be truncated to 72 bytes if longer)

        Returns:
            Bcrypt hashed password
        """
        # Bcrypt has 72 byte limit
        return pwd_context.hash(plain_password[:72])

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            data: Payload to encode in token (should include "sub": username)
            expires_delta: Token expiration time (default: 60 minutes)

        Returns:
            JWT token string

        Example:
            token = local_auth.create_access_token(
                {"sub": "admin", "roles": ["admin"]}
            )
        """
        to_encode = data.copy()

        # Set expiration
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(timezone.utc),  # Issued at
                "iss": "twisterlab-local-auth",  # Issuer
            }
        )

        # Sign token
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User dict if authentication successful, None otherwise

        Example:
            user = await local_auth.authenticate_user("admin", "password123")
            if user:
                print(f"Welcome {user['username']}")
        """
        # Get user from database
        user = self.users_db.get(username)

        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return None

        # Check if user is enabled
        if not user.get("enabled", True):
            logger.warning(f"Authentication failed: user '{username}' is disabled")
            return None

        # Verify password
        if not self.verify_password(password, user["hashed_password"]):
            logger.warning(f"Authentication failed: invalid password for '{username}'")
            return None

        logger.info(f"User '{username}' authenticated successfully")

        # Return user without password hash
        return {
            "username": user["username"],
            "email": user.get("email"),
            "roles": user.get("roles", []),
        }

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload if valid, None otherwise

        Example:
            payload = await local_auth.verify_token(token)
            if payload:
                username = payload["sub"]
                roles = payload["roles"]
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Extract username
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Token verification failed: missing 'sub' claim")
                return None

            # Check if user still exists and is enabled
            user = self.users_db.get(username)
            if not user or not user.get("enabled", True):
                logger.warning(
                    f"Token verification failed: user '{username}' not found or disabled"
                )
                return None

            return {
                "sub": username,
                "username": username,
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
            }

        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: token expired")
            return None
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        roles: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Create new user (admin function).

        Args:
            username: Username (unique)
            password: Plain text password (will be hashed)
            email: User email
            roles: List of roles (default: ["user"])

        Returns:
            Created user dict

        Raises:
            ValueError: If username already exists

        Example:
            user = local_auth.create_user(
                "john",
                "secure_password",
                email="john@example.com",
                roles=["user"]
            )
        """
        if username in self.users_db:
            raise ValueError(f"User '{username}' already exists")

        user = {
            "username": username,
            "hashed_password": self.hash_password(password),
            "email": email,
            "roles": roles or ["user"],
            "enabled": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.users_db[username] = user
        logger.info(f"User '{username}' created successfully")

        # Return without password hash
        return {
            "username": user["username"],
            "email": user["email"],
            "roles": user["roles"],
        }

    def disable_user(self, username: str) -> bool:
        """
        Disable user account (soft delete).

        Args:
            username: Username to disable

        Returns:
            True if user was disabled, False if not found
        """
        user = self.users_db.get(username)
        if not user:
            return False

        user["enabled"] = False
        logger.info(f"User '{username}' disabled")
        return True

    def list_users(self) -> list[Dict[str, Any]]:
        """
        List all users (admin function).

        Returns:
            List of user dicts (without password hashes)
        """
        return [
            {
                "username": user["username"],
                "email": user.get("email"),
                "roles": user.get("roles", []),
                "enabled": user.get("enabled", True),
            }
            for user in self.users_db.values()
        ]
