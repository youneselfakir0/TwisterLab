# INSTRUCTIONS COPILOT - PHASE 1 AUTH (SUITE)

**Date**: 2025-11-11 19:00  
**Status**: READY - Backend termine, Continuer API Integration  
**Branche**: feature/azure-ad-auth

---

## TON OBJECTIF (COPILOT)

Creer les endpoints API FastAPI pour l'authentification Azure AD OAuth2.

**Duree estimee**: 1-2h  
**Fichiers a modifier**: api/main.py, creer api/auth_middleware.py

---

## CE QUI EST DEJA FAIT

- [OK] Module backend agents/auth/azure_ad_auth.py (201 lignes)
- [OK] Tests unitaires 12/12 passing (91% coverage)
- [OK] Documentation docs/PHASE1_AZURE_AD_AUTH.md
- [OK] Dependance msal>=1.31.1 installee

---

## TACHES A FAIRE (ETAPE PAR ETAPE)

### ETAPE 1: Creer le Middleware JWT (30 min)

**Fichier**: api/auth_middleware.py

**Specifications**:

```python
"""
JWT Middleware for TwisterLab API
Validates Azure AD tokens on protected routes
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
import os
from typing import Optional

class AzureADMiddleware:
    """
    Middleware for JWT token validation.
    
    Features:
    - Extract Bearer token from Authorization header
    - Validate JWT signature with Azure AD public keys
    - Check token expiration
    - Extract user claims (email, name, roles)
    """
    
    def __init__(self):
        # Load Azure AD configuration
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.jwks_uri = f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"
        
    async def __call__(self, request: Request, call_next):
        # 1. Extract token from header
        # 2. Validate JWT
        # 3. Add user info to request.state.user
        # 4. Call next middleware
        pass
    
    def validate_token(self, token: str) -> dict:
        """Validate JWT token and return claims"""
        pass
```

**Tests a creer**: tests/test_auth_middleware.py
- Test valid token
- Test expired token
- Test invalid signature
- Test missing token

---

### ETAPE 2: Creer les Endpoints Auth (45 min)

**Fichier**: api/routers/auth.py (nouveau fichier)

**Endpoints a creer**:

#### 1. GET /auth/login

```python
@router.get("/login")
async def login():
    """
    Initiate Azure AD OAuth2 flow.
    
    Returns:
        RedirectResponse: Redirect to Azure AD login page
    
    Flow:
        1. Generate state token (CSRF protection)
        2. Build authorization URL
        3. Redirect user to Azure AD
    """
    from urllib.parse import urlencode
    from fastapi.responses import RedirectResponse
    
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://192.168.0.30:8000/auth/callback",
        "scope": "openid profile email User.Read",
        "state": "random_state_token",
        "response_mode": "query"
    }
    return RedirectResponse(url=auth_url + "?" + urlencode(params))
```

#### 2. GET /auth/callback
```python
@router.get("/callback")
async def callback(code: str, state: str):
    """
    Handle Azure AD OAuth2 callback.
    
    Args:
        code: Authorization code from Azure AD
        state: State token for CSRF validation
    
    Returns:
        JWT token for API access
    """
    from agents.auth.azure_ad_auth import AzureADAuth
    
    auth = AzureADAuth()
    # Exchange code for token
    token_result = auth.app.acquire_token_by_authorization_code(
        code=code,
        scopes=["User.Read"],
        redirect_uri="http://192.168.0.30:8000/auth/callback"
    )
    
    if "error" in token_result:
        raise HTTPException(status_code=400, detail=token_result["error_description"])
    
    return {"access_token": token_result["access_token"]}
```

#### 3. POST /auth/logout

```python
@router.post("/logout")
async def logout():
    """Logout user (invalidate session)."""
    return {"message": "Logged out successfully"}
```

#### 4. GET /auth/me
```python
@router.get("/me")
async def get_current_user(request: Request):
    """
    Get current authenticated user info.
    Requires: Valid JWT token
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return request.state.user
```

**Tests a creer**: tests/test_auth_endpoints.py
- Test login redirect
- Test callback with valid code
- Test callback with invalid code
- Test me endpoint with valid token
- Test me endpoint without token

---

### ETAPE 3: Integrer dans api/main.py (15 min)

**Modifications**:
```python
# api/main.py

from api.routers import auth  # Nouveau router

# Add auth router
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Add middleware (optionnel pour l'instant)
# from api.auth_middleware import AzureADMiddleware
# app.add_middleware(AzureADMiddleware)
```

---

### ETAPE 4: Creer Tests d'Integration (30 min)

**Fichier**: tests/integration/test_auth_flow.py

**Scenario complet**:

```python
import pytest
from fastapi.testclient import TestClient

async def test_complete_oauth_flow():
    """Test complete OAuth2 flow end-to-end."""
    
    # 1. Call /auth/login -> Get redirect URL
    response = client.get("/auth/login")
    assert response.status_code == 302
    assert "login.microsoftonline.com" in response.headers["location"]
    
    # 2. Simulate Azure AD callback (mock)
    # 3. Exchange code for token
    # 4. Use token to call /auth/me
    # 5. Verify user info returned
```

**Tests a faire**:
- Login flow initiation
- Callback handling
- Token validation
- Protected endpoint access
- Logout flow

---

## SI TU BLOQUES (COPILOT)

### Probleme: "Comment valider JWT Azure AD?"

**Solution**: Utilise PyJWT avec les cles publiques Azure AD

```python
import jwt
import requests

# Get Azure AD public keys
jwks_response = requests.get(
    f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
)
jwks = jwks_response.json()

# Validate token
decoded = jwt.decode(
    token,
    jwks,
    algorithms=["RS256"],
    audience=client_id,
    issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
)
```

**-> Consulte Claude** si besoin aide sur crypto/validation JWT.

Cree fichier: .copilot/copilot_blocage.md avec details du probleme.

---

### Probleme: "Comment tester sans vraies credentials Azure?"


**Solution**: Mock MSAL responses

```python
from unittest.mock import patch, MagicMock

@patch('agents.auth.azure_ad_auth.ConfidentialClientApplication')
def test_auth_flow(mock_app):
    mock_app.return_value.acquire_token_by_authorization_code.return_value = {
        "access_token": "fake_token_12345",
        "id_token": "fake_id_token_67890"
    }
    # Test your code here
```

**-> Consulte Claude** pour strategie testing complete.

---

## CRITERES DE SUCCES

Tu as termine quand:
- [ ] Fichier api/auth_middleware.py cree
- [ ] Fichier api/routers/auth.py cree avec 4 endpoints
- [ ] api/main.py integre le nouveau router
- [ ] Tests unitaires passent (pytest -v)
- [ ] Tests integration crees (meme si mocked)
- [ ] Commit avec message: "feat(api): Add Azure AD OAuth2 endpoints"

---

## COMMENT CONSULTER CLAUDE

### Option 1: Via fichier
Cree/modifie .copilot/copilot_blocage.md:
```markdown
# BLOCAGE COPILOT

**Probleme**: [Description]
**Fichier**: api/auth_middleware.py ligne 42
**Erreur**: [Message complet]
**Besoin**: Aide sur validation JWT Azure AD
```

Claude surveille ce fichier et repondra dans .copilot/claude_reponse.md

---

### Option 2: Via l'utilisateur
L'utilisateur peut demander directement a Claude:
> "Copilot bloque sur la validation JWT, peux-tu aider?"

---

## PROGRESSION ATTENDUE

**Temps estime total**: 2h

| Etape | Duree | Status |
|-------|-------|--------|
| Middleware JWT | 30 min | A faire |
| Endpoints Auth | 45 min | A faire |
| Integration | 15 min | A faire |
| Tests | 30 min | A faire |
| **TOTAL** | **2h** | **Pending** |

---

## APRES CETTE ETAPE

**Phase 1 sera a**: 60% complet
- Backend: 100% (deja fait)
- API: 100% (apres cette tache)
- Azure Config: 0% (manuel)
- Deploy: 0% (Claude prendra le relais)

**Claude fera ensuite**:
- Tests end-to-end
- Deploiement staging
- Monitoring & alerting

---

## RESSOURCES UTILES

**Documentation**:
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- PyJWT: https://pyjwt.readthedocs.io/
- MSAL Python: https://msal-python.readthedocs.io/
- Azure AD OAuth2: https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow

**Exemples dans le projet**:
- agents/auth/azure_ad_auth.py <- Backend deja fait
- tests/test_azure_ad_auth.py <- Tests backend

---

**GO COPILOT!**

Tu as tout ce qu'il faut. Si blocage, remplis .copilot/copilot_blocage.md

**Start time**: 2025-11-11 19:00  
**Expected completion**: 2025-11-11 21:00  
**Status**: READY TO START
