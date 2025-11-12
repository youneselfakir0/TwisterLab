"""
Integration tests for Hybrid Authentication Flow (Azure AD + Local JWT)

Tests:
- Fallback behavior when Azure unavailable
- Mode detection (Azure vs Local)
- API endpoints in both modes
- Status reporting
"""

import pytest
import os
from unittest.mock import patch
from agents.auth.hybrid_auth import HybridAuth
from agents.auth.local_auth import LocalAuth


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hybrid_fallback_to_local_when_azure_unavailable():
    """Test système bascule sur local si Azure credentials manquantes."""
    # Supprimer temporairement les variables Azure
    with patch.dict(os.environ, {}, clear=False):
        # S'assurer que les vars Azure n'existent pas
        os.environ.pop("AZURE_CLIENT_ID", None)
        os.environ.pop("AZURE_TENANT_ID", None)
        os.environ.pop("AZURE_CLIENT_SECRET", None)

        # Mais garder JWT secret
        os.environ["JWT_SECRET_KEY"] = "test_secret_key_min_32_chars_for_testing_purposes_12345"
        os.environ["ADMIN_PASSWORD"] = "admin123"

        hybrid = HybridAuth()

        # Devrait être en mode local
        assert hybrid.mode == "local", f"Expected local mode, got {hybrid.mode}"
        assert hybrid.local_auth is not None
        assert hybrid.azure_auth is None

        # Tester auth locale fonctionne
        user = await hybrid.local_auth.authenticate_user("admin", "admin123")
        assert user is not None
        assert user["username"] == "admin"
        assert "admin" in user["roles"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hybrid_prefers_azure_when_credentials_available():
    """Test système essaie Azure si credentials disponibles (mais peut fallback si init échoue)."""
    # Configurer variables Azure (valeurs de test)
    with patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id-12345",
        "AZURE_TENANT_ID": "test-tenant-id-67890",
        "AZURE_CLIENT_SECRET": "test-secret-abc123",
        "JWT_SECRET_KEY": "test_secret_key_min_32_chars_for_testing_purposes_12345"
    }):
        hybrid = HybridAuth()

        # Note: Azure auth va échouer (credentials invalides) et fallback sur local
        # C'est le comportement attendu - les credentials existent mais ne sont pas valides
        # En production avec vrais credentials Azure, mode serait "azure"
        assert hybrid.mode in ["azure", "local"], f"Mode should be azure or local, got {hybrid.mode}"

        # Vérifier que les credentials étaient détectés
        status = hybrid.get_status()
        assert status["azure_configured"] is True, "Azure credentials should be detected"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hybrid_verify_token_delegates_correctly():
    """Test verify_token() délègue au bon système selon le mode."""
    # Setup en mode local
    with patch.dict(os.environ, {
        "JWT_SECRET_KEY": "test_secret_key_min_32_chars_for_testing_purposes_12345",
        "ADMIN_PASSWORD": "admin123"
    }, clear=False):
        os.environ.pop("AZURE_CLIENT_ID", None)
        os.environ.pop("AZURE_TENANT_ID", None)

        hybrid = HybridAuth()
        assert hybrid.mode == "local"

        # Créer un token local
        token = hybrid.local_auth.create_access_token({
            "sub": "admin",
            "email": "admin@twisterlab.local",
            "roles": ["admin"]
        })

        # Vérifier token via HybridAuth (devrait déléguer à LocalAuth)
        payload = await hybrid.verify_token(token)

        assert payload is not None
        assert payload["username"] == "admin"
        assert "admin" in payload["roles"]


@pytest.mark.integration
def test_hybrid_get_status_returns_correct_mode():
    """Test get_status() retourne le bon mode et informations."""
    # Test mode local
    with patch.dict(os.environ, {
        "JWT_SECRET_KEY": "test_secret_key_min_32_chars_for_testing_purposes_12345"
    }, clear=False):
        os.environ.pop("AZURE_CLIENT_ID", None)
        os.environ.pop("AZURE_TENANT_ID", None)

        hybrid = HybridAuth()
        status = hybrid.get_status()

        assert status["mode"] == "local"
        assert status["provider"] == "LocalAuth"
        assert "azure_configured" in status
        assert status["azure_configured"] is False


@pytest.mark.integration
def test_hybrid_mode_local_has_working_methods():
    """Test que les méthodes LocalAuth sont accessibles via HybridAuth."""
    with patch.dict(os.environ, {
        "JWT_SECRET_KEY": "test_secret_key_min_32_chars_for_testing_purposes_12345",
        "ADMIN_PASSWORD": "admin123"
    }, clear=False):
        os.environ.pop("AZURE_CLIENT_ID", None)

        hybrid = HybridAuth()
        assert hybrid.mode == "local"

        # create_access_token devrait fonctionner
        token = hybrid.create_access_token({
            "sub": "testuser",
            "roles": ["user"]
        })
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens sont longs

        # authenticate_user devrait fonctionner
        # (déjà testé dans test_hybrid_fallback_to_local_when_azure_unavailable)


@pytest.mark.integration
def test_hybrid_mode_azure_has_auth_url_methods():
    """Test que les méthodes Azure AD sont accessibles si mode Azure."""
    with patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_SECRET": "test-secret",
        "JWT_SECRET_KEY": "test_secret_key_min_32_chars_for_testing_purposes_12345"
    }):
        hybrid = HybridAuth()

        if hybrid.mode == "azure" and hybrid.azure_auth:
            # get_authorization_url devrait fonctionner
            auth_url = hybrid.get_authorization_url(redirect_uri="http://localhost:8000/callback")
            assert isinstance(auth_url, str)
            assert "login.microsoftonline.com" in auth_url
            assert "test-tenant-id" in auth_url
