# 📋 INSTRUCTIONS COPILOT - PHASE 1 AUTH (SUITE)

**Date**: 2025-11-11 19:00  
**Status**: ✅ Backend terminé → Continuer API Integration  
**Branche**: `feature/azure-ad-auth`

---

## 🎯 TON OBJECTIF (COPILOT)

Créer les endpoints API FastAPI pour l'authentification Azure AD OAuth2.

**Durée estimée**: 1-2h  
**Fichiers à modifier**: `api/main.py`, créer `api/auth_middleware.py`

---

## ✅ CE QUI EST DÉJÀ FAIT

- ✅ Module backend `agents/auth/azure_ad_auth.py` (201 lignes)
- ✅ Tests unitaires 12/12 passing (91% coverage)
- ✅ Documentation `docs/PHASE1_AZURE_AD_AUTH.md`
- ✅ Dépendance msal>=1.31.1 installée

---

## 📋 TÂCHES À FAIRE (ÉTAPE PAR ÉTAPE)

### ÉTAPE 1: Créer le Middleware JWT (30 min)

**Fichier**: `api/auth_middleware.py`

**Spécifications**:
```python
"""
JWT Middleware for TwisterLab API
Validates Azure AD tokens on protected routes
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
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

**Tests à créer**: `tests/test_auth_middleware.py`
- Test valid token
- Test expired token
- Test invalid signature
- Test missing token

---

### ÉTAPE 2: Créer les Endpoints Auth (45 min)

**Fichier**: `api/routers/auth.py` (nouveau fichier)

**Endpoints à créer**:

#### 1. `GET /auth/login`
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
    auth = AzureADAuth()
    # Build Azure AD authorization URL
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://192.168.0.30:8000/auth/callback",
        "scope": "openid profile email User.Read",
        "state": generate_state_token(),
        "response_mode": "query"
    }
    return RedirectResponse(url=auth_url + "?" + urlencode(params))
```

#### 2. `GET /auth/callback`
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
    
    Flow:
        1. Validate state token
        2. Exchange code for access_token
        3. Get user info from Graph API
        4. Generate internal JWT
        5. Return token or set cookie
    """
    auth = AzureADAuth()
    # Exchange code for token
    token_result = auth.app.acquire_token_by_authorization_code(
        code=code,
        scopes=["User.Read"],
        redirect_uri="http://192.168.0.30:8000/auth/callback"
    )
    # Generate JWT and return
    pass
```

#### 3. `POST /auth/logout`
```python
@router.post("/logout")
async def logout():
    """
    Logout user (invalidate session).
    """
    # Clear cookie/session
    pass
```

#### 4. `GET /auth/me`
```python
@router.get("/me", dependencies=[Depends(require_auth)])
async def get_current_user(request: Request):
    """
    Get current authenticated user info.
    
    Requires: Valid JWT token
    
    Returns:
        User info from token claims
    """
    return request.state.user
```

**Tests à créer**: `tests/test_auth_endpoints.py`
- Test login redirect
- Test callback with valid code
- Test callback with invalid code
- Test me endpoint with valid token
- Test me endpoint without token

---

### ÉTAPE 3: Intégrer dans api/main.py (15 min)

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

# Add middleware for protected routes
from api.auth_middleware import AzureADMiddleware
app.add_middleware(AzureADMiddleware)

# Update existing routes to require auth (optionnel pour l'instant)
# @router.get("/tickets", dependencies=[Depends(require_auth)])
```

---

### ÉTAPE 4: Créer Tests d'Intégration (30 min)

**Fichier**: `tests/integration/test_auth_flow.py`

**Scénario complet**:
```python
async def test_complete_oauth_flow():
    """Test complete OAuth2 flow end-to-end."""
    
    # 1. Call /auth/login → Get redirect URL
    response = client.get("/auth/login")
    assert response.status_code == 302
    assert "login.microsoftonline.com" in response.headers["location"]
    
    # 2. Simulate Azure AD callback (mock)
    # 3. Exchange code for token
    # 4. Use token to call /auth/me
    # 5. Verify user info returned
```

**Tests à faire**:
- ✅ Login flow initiation
- ✅ Callback handling
- ✅ Token validation
- ✅ Protected endpoint access
- ✅ Logout flow

---

## 🚨 SI TU BLOQUES (COPILOT)

### Problème: "Comment valider JWT Azure AD?"

**Solution**: Utilise `PyJWT` avec les clés publiques Azure AD

```python
import jwt
import requests

# Get Azure AD public keys
jwks = requests.get(f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys").json()

# Validate token
decoded = jwt.decode(
    token,
    jwks,
    algorithms=["RS256"],
    audience=client_id,
    issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
)
```

**→ Consulte Claude** si tu as besoin d'aide sur la crypto/validation JWT.

---

### Problème: "Comment gérer les redirects?"

**Solution**: Utilise `RedirectResponse` de FastAPI

```python
from fastapi.responses import RedirectResponse

return RedirectResponse(
    url=auth_url,
    status_code=302
)
```

**→ Consulte Claude** si problèmes de configuration URLs.

---

### Problème: "Comment stocker les sessions?"

**Solution 1** (Simple): Cookie HTTPOnly
```python
response.set_cookie(
    key="access_token",
    value=jwt_token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="lax",
    max_age=3600  # 1 hour
)
```

**Solution 2** (Avancée): Redis sessions
```python
# Store in Redis
await redis.setex(f"session:{user_id}", 3600, token)
```

**→ Consulte Claude** pour setup Redis ou choix architecture.

---

### Problème: "Tests unitaires échouent"

**Checklist**:
- [ ] msal installé? `pip install msal`
- [ ] Variables env définies? Check `.env.azure_ad.template`
- [ ] Mock MSAL calls? Utilise `unittest.mock`

**→ Consulte Claude** pour debug tests ou setup CI/CD.

---

### Problème: "Comment tester sans vraies credentials Azure?"

**Solution**: Mock MSAL responses

```python
from unittest.mock import patch, MagicMock

@patch('agents.auth.azure_ad_auth.ConfidentialClientApplication')
def test_auth_flow(mock_app):
    mock_app.return_value.acquire_token_by_authorization_code.return_value = {
        "access_token": "fake_token",
        "id_token": "fake_id_token"
    }
    # Test your code
```

**→ Consulte Claude** pour stratégie testing complète.

---

## 🎯 CRITÈRES DE SUCCÈS

Tu as terminé quand:
- [ ] Fichier `api/auth_middleware.py` créé et testé
- [ ] Fichier `api/routers/auth.py` créé avec 4 endpoints
- [ ] `api/main.py` intègre le nouveau router
- [ ] Tests unitaires passent (pytest -v)
- [ ] Tests intégration créés (même si mocked)
- [ ] Documentation endpoints dans `docs/API_REFERENCE.md`
- [ ] Commit avec message: `feat(api): Add Azure AD OAuth2 endpoints`

---

## 📞 COMMENT CONSULTER CLAUDE

### Option 1: Via fichier
Crée un fichier `.copilot/copilot_blocage.md`:
```markdown
# BLOCAGE COPILOT

**Problème**: Description du problème
**Fichier**: `api/auth_middleware.py` ligne 42
**Erreur**: Message d'erreur complet
**Tentatives**: Ce que j'ai essayé

**Besoin**: Aide sur validation JWT Azure AD
```

Claude surveille ce fichier et répondra dans `.copilot/claude_reponse.md`

---

### Option 2: Via commit message
Commit avec tag `[help]`:
```bash
git commit -m "WIP(auth): JWT validation - [help] Need crypto guidance"
```

Claude verra le tag et créera un rapport d'aide.

---

### Option 3: Via l'utilisateur
L'utilisateur peut me demander directement:
> "Copilot bloque sur la validation JWT, peux-tu aider?"

Je vais analyser le code et proposer des solutions.

---

## 📊 PROGRESSION ATTENDUE

**Temps estimé total**: 2h

| Étape | Durée | Status |
|-------|-------|--------|
| Middleware JWT | 30 min | ⏳ À faire |
| Endpoints Auth | 45 min | ⏳ À faire |
| Intégration main.py | 15 min | ⏳ À faire |
| Tests intégration | 30 min | ⏳ À faire |
| **TOTAL** | **2h** | **⏳** |

---

## 🎉 APRÈS CETTE ÉTAPE

**Phase 1 sera à**: 60% complet
- Backend: ✅ 100%
- API: ✅ 100% (après cette tâche)
- Azure Config: ⏳ 0%
- Deploy: ⏳ 0%

**Claude prendra le relais** pour:
- Configuration Azure Portal (si credentials disponibles)
- Tests end-to-end
- Déploiement staging
- Monitoring & alerting

---

## 💡 RESSOURCES UTILES

**Documentation**:
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- PyJWT: https://pyjwt.readthedocs.io/
- MSAL Python: https://msal-python.readthedocs.io/
- Azure AD OAuth2: https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow

**Exemples dans le projet**:
- `agents/auth/azure_ad_auth.py` ← Backend déjà fait
- `tests/test_azure_ad_auth.py` ← Tests backend

---

**GO COPILOT! 🚀**

Tu as tout ce qu'il faut. Si blocage, consulte Claude via `.copilot/copilot_blocage.md`

**Start time**: 2025-11-11 19:00  
**Expected completion**: 2025-11-11 21:00
