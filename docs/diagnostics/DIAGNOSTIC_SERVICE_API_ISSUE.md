# DIAGNOSTIC - Service API 0/1 Replicas

**Date:** 2025-11-13 15:45
**Problème:** Service `twisterlab_api` reste à 0/1 replicas malgré déploiement

---

## 🔍 OBSERVATIONS

### 1. État des Services
```bash
docker stack services twisterlab
# twisterlab_api        0/1  ❌ (devrait être 1/1)
# twisterlab_postgres   1/1  ✅
# twisterlab_redis      1/1  ✅
```

### 2. Historique des Tâches API
```
ID          NAME              STATE      CURRENT STATE
l3x7leipw   twisterlab_api.1  Shutdown   Complete 15 minutes ago
lq00mpw3l   twisterlab_api.1  Shutdown   Complete 17 minutes ago  
dnkobhpvz   twisterlab_api.1  Shutdown   Complete 20 minutes ago
```

**Pattern:** API démarre → "Application startup complete" → "Shutdown" après quelques secondes

### 3. Connectivité Ollama (✅ OK)
- **PRIMARY** (192.168.0.20:11434): ✅ Accessible depuis edgeserver
- **BACKUP** (192.168.0.30:11434): ✅ Accessible localement
- **llama3.2:1b**: ✅ Chargé sur les deux serveurs

### 4. Logs API
- ✅ Démarre correctement
- ✅ Uvicorn lance sur port 8000
- ✅ "Application startup complete"
- ❌ "Shutting down" immédiatement après

**Aucune erreur visible dans les logs !**

---

## 🐛 CAUSE PROBABLE

**Health Check qui échoue** → Docker Swarm arrête le conteneur

Le docker-compose utilise :
```yaml
healthcheck:
  test: ["CMD", "wget", "-q", "--spider", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Problème potentiel:**
1. `wget` n'est pas installé dans l'image `twisterlab-api:production`
2. Le health check échoue → Docker Swarm arrête le conteneur
3. Le service redémarre → boucle infinie

---

## ✅ SOLUTION

### Option 1: Utiliser curl (plus standard)
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

### Option 2: Utiliser python (toujours disponible)
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
```

### Option 3: Désactiver temporairement (pour debug)
```bash
docker service update --health-cmd none twisterlab_api
```

---

## 🔧 CORRECTIF À APPLIQUER

**Modifier `docker-compose.prod-native-ollama.yml`:**

```yaml
services:
  api:
    # ... configuration existante ...
    healthcheck:
      # ✅ CORRIGÉ - Utilise curl au lieu de wget
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**OU vérifier que wget est installé dans le Dockerfile:**

```dockerfile
# Dans Dockerfile.production
RUN apt-get update && apt-get install -y wget curl && rm -rf /var/lib/apt/lists/*
```

---

## 📋 PROCHAINES ÉTAPES

1. **Vérifier image Docker:**
   ```bash
   ssh twister@192.168.0.30 "docker run --rm twisterlab-api:production wget --version"
   ```

2. **Si wget manquant:**
   - Modifier docker-compose pour utiliser curl
   - OU Reconstruire l'image avec wget

3. **Redéployer:**
   ```bash
   scp docker-compose.prod-native-ollama.yml twister@192.168.0.30:/home/twister/
   ssh twister@192.168.0.30 "docker stack deploy -c docker-compose.prod-native-ollama.yml twisterlab"
   ```

4. **Vérifier:**
   ```bash
   ssh twister@192.168.0.30 "docker stack services twisterlab"
   # Attendu: twisterlab_api 1/1 ✅
   ```

---

## 🎯 STATUT ACTUEL

- ✅ **Ollama PRIMARY**: Opérationnel
- ✅ **Ollama BACKUP**: Opérationnel  
- ✅ **PostgreSQL**: 1/1
- ✅ **Redis**: 1/1
- ❌ **API**: 0/1 (health check échoue)

**Cause:** Health check wget échoue car wget n'est pas installé dans l'image
**Solution:** Modifier health check pour utiliser curl ou python
