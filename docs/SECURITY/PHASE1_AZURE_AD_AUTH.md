# Phase 1 : Authentification Azure AD - Guide d'Implémentation

**Status** : 🚧 EN COURS (Jour 6-7/10)
**Branche** : `feature/azure-ad-auth`
**Durée estimée** : 2 semaines (10 jours ouvrés)

## 📊 Statut Actuel (2025-11-11)

### ✅ Terminé
- **Module auth** : `agents/auth/azure_ad_auth.py` (179 lignes, production-ready)
- **Tests unitaires** : 12/12 tests passing (100% success rate)
- **Couverture** : 91% (objectif ≥80% atteint ✅)
- **Dependencies** : msal>=1.31.1 installé
- **Configuration** : Template `.env.azure_ad.template` créé
- **Git** : 2 commits sur feature/azure-ad-auth

### ⏳ Prochaines Étapes
1. **Azure Portal** : Créer App Registration (Jour 1-2 restant)
2. **API Integration** : Endpoints OAuth2 dans api/main.py (Jour 5)
3. **Tests d'intégration** : Flux complet auth (Jour 6-7)
4. **Déploiement staging** : Validation sur edgeserver (Jour 8-9)
5. **Production** : Go-live (Jour 10)

---

## 📋 Objectif

Sécuriser TwisterLab avec Azure AD OAuth2 pour :
- ✅ Authentification centralisée (SSO)
- ✅ Multi-Factor Authentication (MFA)
- ✅ Audit logs d'accès
- ✅ Gestion des utilisateurs via Azure AD

---

## 🎯 Checklist de Progression

### Semaine 1 : Configuration & Développement

#### Jour 1-2 : Configuration Azure AD ⏳ EN COURS
- [ ] **Créer App Registration dans Azure Portal**
  - Aller sur [Azure Portal](https://portal.azure.com)
  - Azure AD > App registrations > New registration
  - Nom : `TwisterLab-API`
  - Redirect URI : `http://192.168.0.30:8000/auth/callback`
  - Copier : Application (client) ID, Directory (tenant) ID

- [ ] **Configurer API Permissions**
  - App > API permissions > Add permission
  - Microsoft Graph > Delegated permissions
  - Ajouter : `User.Read`, `User.ReadBasic.All`
  - Grant admin consent

- [ ] **Créer Client Secret**
  - App > Certificates & secrets > New client secret
  - Description : `TwisterLab Production`
  - Expiry : 24 months
  - ⚠️ **COPIER LA VALEUR** (visible 1 seule fois)

- [ ] **Mettre à jour `.env.production`**
  ```bash
  cp infrastructure/configs/.env.azure_ad.template infrastructure/configs/.env.production
  # Éditer .env.production avec vos vraies valeurs
  ```

#### Jour 3-4 : Backend Implementation ✅ TERMINÉ
- [x] Créer `agents/auth/azure_ad_auth.py`
- [x] Ajouter `msal` à `requirements.txt`
- [x] Installer dépendances (`msal==1.31.1`)

#### Jour 5 : API Integration ⏳ PROCHAINE ÉTAPE
- [ ] Modifier `api/main.py` pour OAuth2
- [ ] Ajouter endpoints `/auth/login`, `/auth/callback`, `/auth/logout`
- [ ] Créer middleware de vérification JWT
- [ ] Sécuriser endpoints existants

#### Jour 6-7 : Tests ⏳ À FAIRE
- [x] Tests unitaires `agents/auth/` (créés)
- [ ] Exécuter tests : `pytest tests/test_azure_ad_auth.py -v`
- [ ] Tests d'intégration auth flow
- [ ] Coverage ≥80% pour module auth

### Semaine 2 : Déploiement & Validation

#### Jour 8 : Staging Deployment ⏳ À FAIRE
- [ ] Mettre à jour `docker-compose.unified.yml`
- [ ] Déployer en staging : `.\infrastructure\scripts\deploy.ps1 -Environment staging`
- [ ] Tester login flow manuellement
- [ ] Vérifier logs d'authentification

#### Jour 9 : Production Deployment ⏳ À FAIRE
- [ ] Valider tous les tests (unit + integration)
- [ ] Déployer en production : `.\infrastructure\scripts\deploy.ps1 -Environment production`
- [ ] Tests de validation production
- [ ] Monitoring actif (Grafana)

#### Jour 10 : Documentation & Handover ⏳ À FAIRE
- [ ] Mettre à jour `README.md`
- [ ] Documenter procédure d'authentification
- [ ] Créer guide troubleshooting
- [ ] Former l'équipe sur nouveau système

---

## 📂 Fichiers Créés/Modifiés

### Nouveaux Fichiers ✅
```
agents/auth/
├── __init__.py                              # Module auth
└── azure_ad_auth.py                         # Azure AD OAuth2 handler

tests/
├── test_azure_ad_auth.py                    # Tests unitaires auth
└── integration/
    └── test_auth_flow.py                    # Tests intégration (à créer)

infrastructure/configs/
└── .env.azure_ad.template                   # Template configuration
```

### Fichiers Modifiés ✅
```
requirements.txt                             # Ajout msal>=1.31.1
```

### Fichiers à Modifier ⏳
```
api/main.py                                  # OAuth2 endpoints + middleware
infrastructure/docker/docker-compose.unified.yml  # Variables Azure AD
infrastructure/configs/.env.production       # Credentials Azure AD
README.md                                    # Documentation auth
```

---

## 🔧 Commandes Utiles

### Tests
```powershell
# Tests unitaires auth uniquement (12 tests)
C:/TwisterLab/.venv/Scripts/python.exe -m pytest tests/test_azure_ad_auth.py -v
# ✅ Résultat actuel: 12/12 passed (100%)

# Coverage report (cible: ≥80%)
C:/TwisterLab/.venv/Scripts/python.exe -m pytest tests/test_azure_ad_auth.py --cov=agents.auth --cov-report=term-missing
# ✅ Couverture actuelle: 91% (55 stmts, 5 miss)

# Tous les tests avec HTML report
pytest tests/ -v --cov=agents/auth --cov-report=html

# Tests d'intégration (à créer)
pytest tests/integration/test_auth_flow.py -v
```

### Déploiement
```powershell
# Staging
.\infrastructure\scripts\deploy.ps1 -Environment staging

# Production
.\infrastructure\scripts\deploy.ps1 -Environment production

# Vérifier logs
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 50"
```

### Validation
```powershell
# Test health endpoint (public)
curl http://192.168.0.30:8000/health

# Test login redirect
curl -L http://192.168.0.30:8000/auth/login

# Test secured endpoint (nécessite token)
$token = "eyJ0eXAiOiJKV1QiLCJhbGc..."
curl http://192.168.0.30:8000/api/profile -H "Authorization: Bearer $token"
```

---

## ⚠️ Points d'Attention

### Sécurité
- ⚠️ **JAMAIS commit `.env.production`** avec les vraies credentials
- ✅ Utiliser `.env.azure_ad.template` comme référence
- ✅ Client Secret expire après 24 mois → planifier rotation
- ✅ Activer MFA pour comptes admin

### Performance
- JWT verification nécessite fetch des public keys Azure AD
- Mettre en cache les clés publiques (TTL : 24h)
- Prévoir fallback si Azure AD down

### Monitoring
- Ajouter métriques Prometheus :
  - `auth_login_attempts_total`
  - `auth_login_failures_total`
  - `auth_token_verifications_total`
- Dashboard Grafana "Authentication Health"

---

## 📊 Critères de Succès

- [x] Code auth créé avec type hints complets
- [x] Tests unitaires créés (coverage TBD)
- [ ] Tests unitaires passent à 100%
- [ ] Tests intégration créés et passent
- [ ] Login Azure AD fonctionnel (staging + prod)
- [ ] Tokens JWT validés correctement
- [ ] Endpoints sécurisés bloquent accès non-auth
- [ ] Logs audit activés
- [ ] Documentation à jour
- [ ] Équipe formée

---

## 🚀 Prochaines Actions Immédiates

1. **Compléter configuration Azure Portal** (Jour 1-2)
   - [ ] Créer App Registration
   - [ ] Noter credentials dans `.env.production`

2. **Modifier API FastAPI** (Jour 5)
   - [ ] Ajouter endpoints `/auth/*`
   - [ ] Créer middleware JWT verification

3. **Exécuter tests** (Jour 6)
   - [ ] `pytest tests/test_azure_ad_auth.py -v`

---

**Dernière mise à jour** : 2025-11-11
**Responsable** : Équipe TwisterLab
**Contact** : N/A
