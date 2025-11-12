"""
Unit tests for Azure AD authentication module
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agents.auth.azure_ad_auth import AzureADAuth
from fastapi import HTTPException


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("AZURE_TENANT_ID", "test-tenant-id-1234")
    monkeypatch.setenv("AZURE_CLIENT_ID", "test-client-id-5678")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "test-secret-abcd")


@pytest.fixture
def mock_msal_app():
    """Mock MSAL ConfidentialClientApplication"""
    with patch('agents.auth.azure_ad_auth.ConfidentialClientApplication') as mock:
        yield mock


@pytest.mark.unit
def test_azure_auth_init_success(mock_env, mock_msal_app):
    """Test AzureADAuth initializes correctly with valid credentials"""
    auth = AzureADAuth()
    
    assert auth.client_id == "test-client-id-5678"
    assert auth.tenant_id == "test-tenant-id-1234"
    assert auth.client_secret == "test-secret-abcd"
    assert "test-tenant-id-1234" in auth.authority
    assert auth.scopes == ["https://graph.microsoft.com/.default"]


@pytest.mark.unit
def test_azure_auth_init_missing_client_id(monkeypatch):
    """Test initialization fails when AZURE_CLIENT_ID is missing"""
    monkeypatch.setenv("AZURE_TENANT_ID", "test-tenant")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "test-secret")
    # AZURE_CLIENT_ID intentionally not set
    
    with pytest.raises(ValueError, match="Missing Azure AD credentials"):
        AzureADAuth()


@pytest.mark.unit
def test_azure_auth_init_missing_tenant_id(monkeypatch):
    """Test initialization fails when AZURE_TENANT_ID is missing"""
    monkeypatch.setenv("AZURE_CLIENT_ID", "test-client")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "test-secret")
    # AZURE_TENANT_ID intentionally not set
    
    with pytest.raises(ValueError, match="Missing Azure AD credentials"):
        AzureADAuth()


@pytest.mark.unit
def test_azure_auth_init_missing_secret(monkeypatch):
    """Test initialization fails when AZURE_CLIENT_SECRET is missing"""
    monkeypatch.setenv("AZURE_CLIENT_ID", "test-client")
    monkeypatch.setenv("AZURE_TENANT_ID", "test-tenant")
    # AZURE_CLIENT_SECRET intentionally not set
    
    with pytest.raises(ValueError, match="Missing Azure AD credentials"):
        AzureADAuth()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_app_token_success(mock_env, mock_msal_app):
    """Test successful application token acquisition"""
    mock_instance = MagicMock()
    mock_instance.acquire_token_for_client.return_value = {
        "access_token": "test-token-123456789",
        "token_type": "Bearer",
        "expires_in": 3600
    }
    mock_msal_app.return_value = mock_instance
    
    auth = AzureADAuth()
    token = await auth.get_app_token()
    
    assert token == "test-token-123456789"
    mock_instance.acquire_token_for_client.assert_called_once_with(
        scopes=["https://graph.microsoft.com/.default"]
    )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_app_token_auth_failure(mock_env, mock_msal_app):
    """Test token acquisition failure with Azure AD error"""
    mock_instance = MagicMock()
    mock_instance.acquire_token_for_client.return_value = {
        "error": "invalid_client",
        "error_description": "Client credentials are invalid"
    }
    mock_msal_app.return_value = mock_instance
    
    auth = AzureADAuth()
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_app_token()
    
    assert exc_info.value.status_code == 500
    assert "Client credentials are invalid" in exc_info.value.detail


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_app_token_unexpected_error(mock_env, mock_msal_app):
    """Test token acquisition with unexpected exception"""
    mock_instance = MagicMock()
    mock_instance.acquire_token_for_client.side_effect = Exception("Network error")
    mock_msal_app.return_value = mock_instance
    
    auth = AzureADAuth()
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_app_token()
    
    assert exc_info.value.status_code == 500
    assert "Network error" in exc_info.value.detail


@pytest.mark.unit
def test_get_authorization_url(mock_env, mock_msal_app):
    """Test authorization URL generation"""
    mock_instance = MagicMock()
    mock_instance.get_authorization_request_url.return_value = (
        "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/authorize?"
        "client_id=test-client&redirect_uri=http://localhost/callback"
    )
    mock_msal_app.return_value = mock_instance
    
    auth = AzureADAuth()
    url = auth.get_authorization_url(
        redirect_uri="http://localhost:8000/auth/callback",
        state="random-state-123"
    )
    
    assert "login.microsoftonline.com" in url
    assert "test-tenant" in url or "test-client" in url
    mock_instance.get_authorization_request_url.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_acquire_token_by_code_success(mock_env, mock_msal_app):
    """Test successful token exchange with authorization code"""
    mock_instance = MagicMock()
    mock_instance.acquire_token_by_authorization_code.return_value = {
        "access_token": "user-token-abc123",
        "refresh_token": "refresh-token-xyz789",
        "id_token": "id-token-def456",
        "token_type": "Bearer",
        "expires_in": 3600
    }
    mock_msal_app.return_value = mock_instance
    
    auth = AzureADAuth()
    result = await auth.acquire_token_by_code(
        code="auth-code-123",
        redirect_uri="http://localhost:8000/auth/callback"
    )
    
    assert result["access_token"] == "user-token-abc123"
    assert "refresh_token" in result
    mock_instance.acquire_token_by_authorization_code.assert_called_once_with(
        code="auth-code-123",
        scopes=["User.Read"],
        redirect_uri="http://localhost:8000/auth/callback"
    )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_acquire_token_by_code_failure(mock_env, mock_msal_app):
    """Test token exchange failure"""
    mock_instance = MagicMock()
    mock_instance.acquire_token_by_authorization_code.return_value = {
        "error": "invalid_grant",
        "error_description": "Authorization code expired"
    }
    mock_msal_app.return_value = mock_instance
    
    auth = AzureADAuth()
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.acquire_token_by_code(
            code="expired-code",
            redirect_uri="http://localhost:8000/auth/callback"
        )
    
    assert exc_info.value.status_code == 400
    assert "expired" in exc_info.value.detail.lower()


@pytest.mark.unit
def test_validate_token_structure_valid(mock_env, mock_msal_app):
    """Test token structure validation with valid JWT"""
    auth = AzureADAuth()
    
    # Valid JWT structure (3 parts separated by dots)
    valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456"
    
    assert auth.validate_token_structure(valid_token) is True


@pytest.mark.unit
def test_validate_token_structure_invalid(mock_env, mock_msal_app):
    """Test token structure validation with invalid token"""
    auth = AzureADAuth()
    
    # Invalid tokens (not 3 parts or empty parts)
    assert auth.validate_token_structure("not-a-jwt-token") is False
    assert auth.validate_token_structure("only.two") is False  # Only 2 parts
    assert auth.validate_token_structure("") is False
    assert auth.validate_token_structure("too.many.parts.here.invalid") is False  # More than 3 parts
    assert auth.validate_token_structure("..") is False  # 3 parts but all empty
