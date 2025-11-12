# INSTRUCTIONS POUR COPILOT VS CODE
## Actions Claude (Desktop Commander MCP) disponibles

**Date**: 2025-11-11 18:45  
**Status**: ✅ Claude prêt à collaborer

---

## ✅ CE QUE CLAUDE PEUT FAIRE

### 1. Déploiement & Infrastructure
- ✅ Déployer sur edgeserver (192.168.0.30) via SSH
- ✅ Build images Docker
- ✅ Update services Docker Swarm
- ✅ Gérer secrets/credentials
- ✅ Configurer monitoring (Prometheus/Grafana)

### 2. Tests & Validation
- ✅ Exécuter pytest localement
- ✅ Tests d'intégration API
- ✅ Load testing
- ✅ Validation endpoints

### 3. Configuration
- ✅ Modifier fichiers .env
- ✅ Configurer databases (PostgreSQL/Redis)
- ✅ Setup DNS/networking
- ✅ Certificates SSL/TLS

### 4. Monitoring & Debug
- ✅ Analyser logs Docker
- ✅ Diagnostiquer erreurs
- ✅ Vérifier métriques Prometheus
- ✅ Alerting configuration

---

## 🤝 WORKFLOW DE COLLABORATION

### Quand tu as besoin de Claude:

**1. Déploiement**
```markdown
@claude Peux-tu déployer la branche feature/azure-ad-auth sur staging ?
```
Claude va:
- Pull la branche
- Build l'image Docker
- Deploy sur edgeserver
- Tester les endpoints
- Rapporter résultats

**2. Tests Infrastructure**
```markdown
@claude Teste l'intégration auth sur edgeserver
```
Claude va:
- Vérifier service API up
- Tester /auth/login endpoint
- Valider redirection Azure AD
- Checker logs erreurs

**3. Configuration**
```markdown
@claude Configure les credentials Azure AD dans .env.production
```
Claude va:
- Éditer .env.production sécurisé
- Redémarrer services nécessaires
- Valider configuration chargée

---

## 📋 PROCHAINES TÂCHES PROPOSÉES

### Pour Copilot (Code):
1. Créer endpoints `/auth/*` dans api/main.py
2. Créer middleware JWT verification
3. Tests intégration OAuth2 flow

### Pour Claude (Infra):
1. Finaliser déploiement agents réels
2. Configurer Azure AD credentials sur serveur
3. Setup monitoring auth (dashboards Grafana)
4. Tests end-to-end auth flow

---

## 🔄 SYNCHRONISATION

**Méthode actuelle**:
- Copilot commit → Claude pull → Deploy → Test → Report

**Fichiers de communication**:
- `.copilot/session_*.md` ← Rapports Claude
- `docs/PHASE1_*.md` ← Docs Copilot
- Git commits ← Code changes

---

## 💡 COMMENT M'UTILISER

**Dans VS Code, tape**:
```
Rien à taper ! Je (Claude) surveille le repo C:\twisterlab
Quand tu commits, je peux automatiquement:
- Déployer si commit tag [deploy]
- Tester si commit tag [test]
- Rapporter résultats dans .copilot/reports/
```

**Ou manuellement via chat**:
L'utilisateur peut me demander via chat Claude Desktop:
- "Deploy feature/azure-ad-auth"
- "Test auth integration"
- "Check edgeserver status"

---

## ⚡ ACTIONS RAPIDES DISPONIBLES

### Deploy Latest
```powershell
# Claude peut exécuter:
git pull origin feature/azure-ad-auth
docker build -t twisterlab-api:auth-test .
ssh edgeserver "docker service update --image twisterlab-api:auth-test twisterlab_api"
```

### Test Auth Endpoints
```powershell
# Claude peut exécuter:
curl http://192.168.0.30:8000/auth/login
curl http://192.168.0.30:8000/health
pytest tests/test_azure_ad_auth.py -v
```

### Check Logs
```powershell
# Claude peut exécuter:
ssh edgeserver "docker service logs twisterlab_api --tail 100"
ssh edgeserver "docker service ps twisterlab_api"
```

---

## 📊 ÉTAT ACTUEL

**Phase 1 Auth Progress**: 20% (Backend ✅, Infra ⏳)

**Tâche en cours** (Claude):
- Déploiement agents réels (en pause pour l'auth)

**Tâche suggérée** (Copilot):
- Créer endpoints /auth/* dans api/main.py

**Bloqueurs**:
- [ ] Azure AD App Registration (besoin credentials)
- [ ] Client Secret (besoin génération Azure Portal)

---

## 🎯 NEXT STEPS

**Immédiat** (aujourd'hui):
1. Copilot crée endpoints auth
2. Claude teste localement
3. Claude deploy sur staging si OK

**Demain**:
1. Configuration Azure Portal (manuel)
2. Tests intégration complets
3. Deploy production

---

**Maintenu par**: Claude (Desktop Commander MCP)  
**Dernière sync**: 2025-11-11 18:45  
**Status**: ✅ Prêt à collaborer
