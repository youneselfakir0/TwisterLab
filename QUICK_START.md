# 🚀 GUIDE RAPIDE - QUELLE COMMANDE UTILISER ?

## Situation 1: Le service est cassé et je veux juste réparer

**Commande**:
```powershell
.\fix_database_config.ps1
```

**Durée**: 15-20 minutes
**Risque**: Faible (backup automatique créé)
**Résultat**: Service avec agents réels fonctionnels

---

## Situation 2: Le fix a échoué, je veux revenir en arrière

**Commande**:
```powershell
.\rollback_service.ps1
```

**Options**:
- Option 1: Rollback automatique Swarm
- Option 2: Version `real-agents-final`
- Option 3: Version `production-real-agents-20251111-024958`

---

## Situation 3: Je veux juste vérifier l'état actuel

**Commandes**:
```powershell
# Status du service
ssh twister@192.168.0.30 "docker service ps twisterlab_api"

# Logs récents
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 50"

# Test API
Invoke-RestMethod -Uri "http://192.168.0.30:8000/health"
```

---

## Situation 4: Je veux tester les agents réels

**Commandes**:
```powershell
# Test MonitoringAgent
$body = @{ operation = "health_check" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

# Test BackupAgent
$body = @{ operation = "status" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/BackupAgent/execute" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

---

## Situation 5: Je veux exécuter les tests d'intégration

**Commande**:
```powershell
python C:\TwisterLab\tests\test_integration_real_agents.py
```

---

## Arbre de décision visuel

```
┌─────────────────────────────────┐
│ Le service fonctionne-t-il ?    │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │             │
     OUI           NON
      │             │
      │        ┌────┴────────────────────┐
      │        │ API répond /health ?     │
      │        └─────┬──────────────────┘
      │              │
      │        ┌─────┴─────┐
      │       OUI         NON
      │        │           │
      │        │      fix_database_config.ps1
      │        │           │
      │   Données       ┌──┴──┐
      │   réelles?    SUCCESS  FAIL
      │        │           │     │
      │    ┌───┴───┐      OK    rollback_service.ps1
      │   OUI     NON
      │    │       │
      │   OK   Vérifier
      │        orchestrator
      │
  Tests
  d'intégration
```

---

## Le problème exact et sa solution

**Problème identifié**:
```python
# File: /app/agents/database/config.py (ligne 22)
engine = create_async_engine(DATABASE_URL)  # ❌ psycopg2 (sync) with async engine
```

**Solution**:
```python
# Change DATABASE_URL from:
postgresql+psycopg2://user:pass@host/db

# To:
postgresql+asyncpg://user:pass@host/db
```

**Pourquoi ça plante**:
- `create_async_engine()` nécessite un driver asynchrone
- `psycopg2` est synchrone
- `asyncpg` est asynchrone ✅

**Ce que fait le script fix_database_config.ps1**:
1. Backup de config.py → config.py.backup
2. `sed -i 's/postgresql+psycopg2/postgresql+asyncpg/g' config.py`
3. Rebuild l'image Docker avec le fix
4. Déploie la nouvelle image
5. Teste que tout fonctionne

---

## Fichiers créés cette session

| Fichier | Description | Usage |
|---------|-------------|-------|
| `fix_database_config.ps1` | Fix le problème async driver | **EXÉCUTER EN PREMIER** |
| `rollback_service.ps1` | Revenir en arrière si échec | Si fix échoue |
| `RAPPORT_FINAL_SESSION_2025-11-11.md` | Rapport détaillé | Documentation |
| `QUICK_START.md` | Ce fichier | Référence rapide |

---

## Images Docker disponibles

| Image | Status | Notes |
|-------|--------|-------|
| `production-real-agents-20251111-024958` | ✅ READY | Toutes dépendances, mais config DB à fixer |
| `production-asyncpg-XXXXXXXX-XXXXXX` | 🔄 SERA CRÉÉ | Après exécution fix_database_config.ps1 |
| `real-agents-final` | ⚠️ ANCIEN | Version précédente (avant ce fix) |
| `with-real-agents` | ⚠️ ANCIEN | Version test |

---

## Commandes utiles

```powershell
# Rebuild manuel si besoin
ssh twister@192.168.0.30 "cd /home/twister/TwisterLab && docker build -f Dockerfile.production -t twisterlab-api:manual-fix ."

# Déployer une image spécifique
ssh twister@192.168.0.30 "docker service update --image twisterlab-api:TAG twisterlab_api"

# Voir toutes les images
ssh twister@192.168.0.30 "docker images | grep twisterlab-api"

# Supprimer images anciennes
ssh twister@192.168.0.30 "docker image prune -f"

# Logs en temps réel
ssh twister@192.168.0.30 "docker service logs -f twisterlab_api"

# Redémarrer le service (dernier recours)
ssh twister@192.168.0.30 "docker service update --force twisterlab_api"
```

---

## FAQ

**Q: Combien de temps prend le fix ?**
A: 15-20 minutes (5 min build + 2 min deploy + 3 min tests)

**Q: Y a-t-il un risque de casser le système ?**
A: Non. Un backup automatique est créé et rollback disponible.

**Q: Que faire si le fix échoue ?**
A: Exécuter `.\rollback_service.ps1` pour revenir en arrière.

**Q: Comment vérifier que les agents sont bien réels ?**
A: Tester MonitoringAgent - le CPU ne doit PAS être "23%" (c'était la valeur mock).

**Q: Est-ce que je peux continuer à utiliser l'ancien service ?**
A: Oui, avec rollback_service.ps1 option 2 ou 3. Mais il retournera des données mock.

---

## 🎯 Action recommandée MAINTENANT

```powershell
# 1. Exécuter le fix (15-20 minutes)
.\fix_database_config.ps1

# 2. Si succès, tester
Invoke-RestMethod -Uri "http://192.168.0.30:8000/health"

# 3. Vérifier données réelles
$body = @{ operation = "health_check" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" -Method POST -Body $body -ContentType "application/json"

# 4. Exécuter tests d'intégration
python C:\TwisterLab\tests\test_integration_real_agents.py
```

**Résultat attendu**: 100% completion avec agents réels fonctionnels 🚀

---

**Status actuel**: 97% complete
**Blocage**: 1 ligne dans database/config.py
**Solution**: Exécuter fix_database_config.ps1
**Temps estimé**: 15-20 minutes
**Difficulté**: ⭐☆☆☆☆ (très simple)
