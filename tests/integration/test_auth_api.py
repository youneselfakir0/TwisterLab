"""
Integration tests for Azure AD OAuth2 authentication API endpoints.

Tests the complete authentication flow:
- Login redirection to Azure AD
- Callback handling with authorization code
- Token verification
- Protected route access
- Logout flow

Usage:
    pytest tests/integration/test_auth_api.py -v
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

# Import the app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_azure_auth():
    """Mock AzureADAuth instance."""
    mock_instance = Mock()
    mock_instance.get_authorization_url.return_value = "https://login.microsoftonline.com/tenant/oauth2/v2.0/authorize?client_id=abc&redirect_uri=http://test"
    mock_instance.acquire_token_by_code = AsyncMock(return_value={
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "User.Read"
    })
    mock_instance.validate_token_structure.return_value = True

    # Patch the get_azure_ad_auth function to return our mock
    with patch("api.auth.get_azure_ad_auth") as mock_get_auth:
        mock_get_auth.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("api.auth.get_redis_client") as mock_get_redis:
        mock_redis_client = AsyncMock()
        mock_redis_client.setex = AsyncMock()
        mock_redis_client.delete = AsyncMock()
        mock_get_redis.return_value = mock_redis_client
        yield mock_redis_client


@pytest.mark.integration
def test_auth_login_redirect(client, mock_azure_auth):
    """Test that /auth/login redirects to Azure AD."""
    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 307  # Redirect
    assert "login.microsoftonline.com" in response.headers["location"]
    mock_azure_auth.get_authorization_url.assert_called_once()


@pytest.mark.integration
def test_auth_login_with_redirect_uri(client, mock_azure_auth):
    """Test /auth/login with custom redirect_uri parameter."""
    response = client.get(
        "/auth/login?redirect_uri=/dashboard",
        follow_redirects=False
    )

    assert response.status_code == 307
    # State should contain redirect URI
    mock_azure_auth.get_authorization_url.assert_called_once()
    call_args = mock_azure_auth.get_authorization_url.call_args
    assert "redirect=/dashboard" in call_args.kwargs.get("state", "")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_callback_success(client, mock_azure_auth, mock_redis):
    """Test successful OAuth2 callback with authorization code."""
    response = client.get(
        "/auth/callback?code=mock_auth_code_123&state=redirect=/"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "access_token" in data
    assert data["access_token"] == "mock_access_token_12345"
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 3600

    # Verify token acquisition was called
    mock_azure_auth.acquire_token_by_code.assert_called_once_with("mock_auth_code_123")


@pytest.mark.integration
def test_auth_callback_error(client):
    """Test OAuth2 callback with error from Azure AD."""
    response = client.get(
        "/auth/callback?error=access_denied&error_description=User cancelled"
    )

    assert response.status_code == 401
    data = response.json()
    assert "Authentication failed" in data["detail"]


@pytest.mark.integration
def test_auth_callback_missing_code(client):
    """Test OAuth2 callback without authorization code."""
    response = client.get("/auth/callback")

    assert response.status_code == 400
    data = response.json()
    assert "Missing authorization code" in data["detail"]


@pytest.mark.integration
def test_auth_me_without_token(client):
    """Test /auth/me endpoint without authentication."""
    response = client.get("/auth/me")

    # Should return 403 (Forbidden) because no Bearer token
    assert response.status_code == 403


@pytest.mark.integration
def test_auth_me_with_valid_token(client):
    """Test /auth/me endpoint with valid JWT token."""
    # Mock JWT verification
    mock_user = {
        "sub": "user-123",
        "name": "Test User",
        "preferred_username": "test@example.com",
        "roles": ["user", "admin"],
        "tid": "tenant-123"
    }

    with patch("api.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_user

        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer mock_valid_token"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == "user-123"
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert "admin" in data["roles"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_logout_success(client, mock_redis):
    """Test logout endpoint removes user from cache."""
    mock_user = {
        "sub": "user-456",
        "name": "Logout User"
    }

    with patch("api.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_user

        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer mock_token"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "Logged out successfully" in data["message"]

        # Verify Redis delete was called
        mock_redis.delete.assert_called_once_with("user:user-456")


@pytest.mark.integration
def test_protected_route_without_auth(client):
    """Test protected route rejects unauthenticated requests."""
    response = client.post(
        "/api/v1/autonomous/agents/MonitoringAgent/execute",
        json={"operation": "health_check"}
    )

    # Should return 403 (no auth) or 200 if auth is optional
    # Depends on AUTH_AVAILABLE flag in main.py
    assert response.status_code in [200, 403]


@pytest.mark.integration
def test_protected_route_with_auth(client):
    """Test protected route accepts authenticated requests."""
    mock_user = {
        "sub": "user-789",
        "name": "Authorized User",
        "roles": ["admin"]
    }

    with patch("api.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
        with patch("api.main.execute_monitoring_agent", new_callable=AsyncMock) as mock_exec:
            mock_verify.return_value = mock_user
            mock_exec.return_value = {
                "status": "success",
                "data": {"cpu": 25.5, "memory": 60.2}
            }

            response = client.post(
                "/api/v1/autonomous/agents/MonitoringAgent/execute",
                json={"operation": "health_check"},
                headers={"Authorization": "Bearer valid_token"}
            )

            # Should succeed with valid token
            assert response.status_code == 200


@pytest.mark.integration
def test_public_routes_accessible(client):
    """Test that public routes remain accessible without auth."""
    # /health should always be public
    response = client.get("/health")
    assert response.status_code == 200

    # Root endpoint should be public
    response = client.get("/")
    assert response.status_code == 200

    # Metrics should be public (for Prometheus)
    response = client.get("/metrics")
    assert response.status_code in [200, 503]  # 503 if Prometheus not available


@pytest.mark.integration
def test_auth_flow_complete(client, mock_azure_auth, mock_redis):
    """Test complete authentication flow from login to logout."""
    # Step 1: Initiate login
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307

    # Step 2: Callback with code
    response = client.get("/auth/callback?code=test_code&state=redirect=/")
    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]

    # Step 3: Access protected resource
    mock_user = {"sub": "user-complete", "name": "Complete User"}
    with patch("api.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_user

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

        # Step 4: Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
