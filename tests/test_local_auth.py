"""
Unit tests for LocalAuth - Local JWT Authentication System

Tests:
- Password hashing and verification
- JWT token creation and verification
- User authentication
- Token expiration
- User management (create, disable, list)
"""

import pytest
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

# Set required env vars before importing
os.environ["JWT_SECRET_KEY"] = "test_secret_key_min_32_chars_for_testing_purposes_12345"
os.environ["ADMIN_PASSWORD"] = "admin123"  # Short password for testing

from agents.auth.local_auth import LocalAuth


@pytest.fixture
def local_auth():
    """LocalAuth instance for testing."""
    return LocalAuth()


@pytest.mark.unit
def test_local_auth_initialization(local_auth):
    """Test LocalAuth initializes correctly."""
    assert local_auth.secret_key == "test_secret_key_min_32_chars_for_testing_purposes_12345"
    assert local_auth.algorithm == "HS256"
    assert local_auth.access_token_expire_minutes == 60
    assert "admin" in local_auth.users_db


@pytest.mark.unit
def test_local_auth_missing_secret_key():
    """Test LocalAuth raises error if JWT_SECRET_KEY missing or too short."""
    with patch.dict(os.environ, {"JWT_SECRET_KEY": "tooshort"}):
        with pytest.raises(ValueError, match="at least 32 characters"):
            LocalAuth()


@pytest.mark.unit
def test_password_hashing(local_auth):
    """Test password hashing and verification."""
    password = "secure_password_123"
    hashed = local_auth.hash_password(password)
    
    assert hashed != password  # Should be hashed
    assert hashed.startswith("$2b$")  # Bcrypt format
    assert local_auth.verify_password(password, hashed) is True
    assert local_auth.verify_password("wrong_password", hashed) is False


@pytest.mark.unit
def test_create_access_token(local_auth):
    """Test JWT token creation."""
    token = local_auth.create_access_token(
        {"sub": "testuser", "roles": ["user"]}
    )
    
    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long
    
    # Token should contain 3 parts (header.payload.signature)
    parts = token.split(".")
    assert len(parts) == 3


@pytest.mark.unit
def test_create_access_token_with_custom_expiry(local_auth):
    """Test JWT token with custom expiration time."""
    token = local_auth.create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(minutes=30)
    )
    
    assert isinstance(token, str)
    # Verify token is valid
    from jose import jwt
    decoded = jwt.decode(
        token,
        local_auth.secret_key,
        algorithms=[local_auth.algorithm]
    )
    assert "exp" in decoded


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authenticate_user_success(local_auth):
    """Test successful user authentication."""
    user = await local_auth.authenticate_user("admin", "admin123")
    
    assert user is not None
    assert user["username"] == "admin"
    assert user["email"] == "admin@twisterlab.local"
    assert "admin" in user["roles"]
    assert "hashed_password" not in user  # Should not return password hash


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(local_auth):
    """Test authentication fails with wrong password."""
    user = await local_auth.authenticate_user("admin", "wrong_password")
    
    assert user is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authenticate_user_not_found(local_auth):
    """Test authentication fails for non-existent user."""
    user = await local_auth.authenticate_user("nonexistent", "password")
    
    assert user is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authenticate_disabled_user(local_auth):
    """Test authentication fails for disabled user."""
    # Disable admin user
    local_auth.users_db["admin"]["enabled"] = False
    
    user = await local_auth.authenticate_user("admin", "admin123")
    
    assert user is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_token_success(local_auth):
    """Test successful token verification."""
    # Create token
    token = local_auth.create_access_token({
        "sub": "testuser",
        "email": "test@example.com",
        "roles": ["user"]
    })
    
    # Verify token
    payload = await local_auth.verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["username"] == "testuser"
    assert payload["email"] == "test@example.com"
    assert "user" in payload["roles"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_token_expired(local_auth):
    """Test token verification fails for expired token."""
    # Create token that expires immediately
    token = local_auth.create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    
    # Verify token
    payload = await local_auth.verify_token(token)
    
    assert payload is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_token_invalid(local_auth):
    """Test token verification fails for invalid token."""
    payload = await local_auth.verify_token("invalid.token.here")
    
    assert payload is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_token_disabled_user(local_auth):
    """Test token verification fails if user is disabled."""
    # Create token for admin
    token = local_auth.create_access_token({"sub": "admin"})
    
    # Disable admin user
    local_auth.users_db["admin"]["enabled"] = False
    
    # Verify token
    payload = await local_auth.verify_token(token)
    
    assert payload is None


@pytest.mark.unit
def test_create_user(local_auth):
    """Test creating new user."""
    user = local_auth.create_user(
        "newuser",
        "password123",
        email="newuser@example.com",
        roles=["user", "viewer"]
    )
    
    assert user["username"] == "newuser"
    assert user["email"] == "newuser@example.com"
    assert "user" in user["roles"]
    assert "viewer" in user["roles"]
    
    # Check user is in database
    assert "newuser" in local_auth.users_db
    assert local_auth.users_db["newuser"]["enabled"] is True


@pytest.mark.unit
def test_create_user_duplicate(local_auth):
    """Test creating duplicate user raises error."""
    with pytest.raises(ValueError, match="already exists"):
        local_auth.create_user("admin", "password")


@pytest.mark.unit
def test_disable_user(local_auth):
    """Test disabling user."""
    # Create test user
    local_auth.create_user("testuser", "password123")
    
    # Disable user
    result = local_auth.disable_user("testuser")
    
    assert result is True
    assert local_auth.users_db["testuser"]["enabled"] is False


@pytest.mark.unit
def test_disable_nonexistent_user(local_auth):
    """Test disabling non-existent user returns False."""
    result = local_auth.disable_user("nonexistent")
    
    assert result is False


@pytest.mark.unit
def test_list_users(local_auth):
    """Test listing all users."""
    # Create additional test user
    local_auth.create_user("testuser", "password123", email="test@example.com")
    
    users = local_auth.list_users()
    
    assert len(users) >= 2  # At least admin and testuser
    assert any(u["username"] == "admin" for u in users)
    assert any(u["username"] == "testuser" for u in users)
    
    # Check password hashes are not included
    for user in users:
        assert "hashed_password" not in user
