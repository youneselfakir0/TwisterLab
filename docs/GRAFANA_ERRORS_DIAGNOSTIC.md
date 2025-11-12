# Diagnostic Grafana Dashboard Erreurs "An unexpected error happened"
**Date**: 2025-11-10
**Dashboard**: TwisterLab Agents - Real-time Monitoring (Version 5)

---

## 🔴 PROBLÈME RAPPORTÉ PAR L'UTILISATEUR

**Panels affichant "An unexpected error happened":**
- API Health Check
- Redis Status
- PostgreSQL Status
- API Response Time (ms) - Pas de données
- Container CPU Usage (%) - Pas de données
- Container Memory Usage (MB) - Pas de données
- PostgreSQL Connections - Pas de données
- Disk Usage (%) - Pas de données
- Network I/O (MB/s) - Pas de données

**Seule métrique visible:**
- Redis Memory Usage: 0.226% (fonctionne!)

---

## ✅ DIAGNOSTIC EFFECTUÉ

### 1. Analyse du Dashboard
```bash
python scripts/diagnose_dashboard.py
```

**Résultat**: ✅ Queries du dashboard CORRECTES (17 panels analysés)
- Toutes les queries utilisent la bonne syntaxe Prometheus
- Pas d'erreurs de syntaxe PromQL
- Dashboard Version 5 avec graceful fallbacks

### 2. Métriques Disponibles dans l'API

```bash
curl http://192.168.0.30:8000/metrics
```

**✅ Métriques confirmées:**
```
http_requests_total{endpoint="/health",method="GET",status="200"} 309
agent_operations_total{agent="classifieragent",operation="classify",status="success"} 20
agent_operations_total{agent="backupagent",...} ...
process_cpu_seconds_total 44.82
process_resident_memory_bytes 54562816
```

### 3. Exporters Déployés

```bash
docker service ls --filter name=exporter
```

**Services actifs:**
- ✅ `twisterlab_redis-exporter` (1/1) - Port 9121
- ✅ `twisterlab_postgres-exporter` (1/1) - Port 9187

**Métriques exporters vérifiées:**
- ✅ Redis: `redis_up 1`, `redis_connected_clients 1`
- ⚠️ PostgreSQL: `pg_up 0` (problème d'authentification connu)

### 4. Services Monitoring Manquants

**❌ NON DÉPLOYÉS:**
- `cadvisor` - Requis pour CPU/Memory conteneurs
- `node-exporter` - Requis pour Disk/Network I/O

---

## 🎯 CAUSE RACINE IDENTIFIÉE

Le message "An unexpected error happened" dans Grafana est causé par **UN ou PLUSIEURS de ces problèmes**:

### Problème #1: Datasource Prometheus Non Accessible
Si Grafana ne peut pas contacter Prometheus, tous les panels affichent l'erreur.

**Test**:
```bash
# Depuis Grafana UI
Configuration > Data Sources > Prometheus > Test
```

**Causes possibles**:
- Prometheus down (vérifier: `docker service ls | grep prometheus`)
- Réseau entre Grafana et Prometheus cassé
- URL datasource incorrecte (actuellement: `http://prometheus:9090`)

### Problème #2: Métriques Pas Encore Scrapées par Prometheus
Prometheus doit scraper les endpoints avant que Grafana puisse afficher les données.

**Test**:
```bash
# Vérifier Prometheus targets
curl http://192.168.0.30:9090/targets

# Vérifier si métrique 'up' existe
curl 'http://192.168.0.30:9090/api/v1/query?query=up'
```

**Causes possibles**:
- Config Prometheus pas rechargée correctement
- Jobs de scraping pas configurés
- Endpoints inaccess ibles (firewall, réseau)

### Problème #3: Query Timeout ou Trop de Données
Grafana timeout si Prometheus met trop de temps à répondre.

**Causes possibles**:
- Range trop large (actuellement: `now-15m to now`)
- Trop de séries temporelles
- Prometheus surcharger

### Problème #4: Services Manquants (Confirmé)
❌ **cadvisor** et **node-exporter** ne sont pas déployés.

---

## 🔧 SOLUTIONS PAR PRIORITÉ

### PRIORITÉ 1: Vérifier Datasource Grafana ✅

**Action**:
```bash
# 1. Ouvrir Grafana
http://192.168.0.30:3000

# 2. Aller dans Configuration > Data Sources > Prometheus

# 3. Vérifier:
#    - URL: http://prometheus:9090
#    - Access: Server (not Browser)
#    - Auth: None

# 4. Cliquer "Save & Test"
#    - Doit afficher "Data source is working"
#    - Si erreur: voir le message exact
```

### PRIORITÉ 2: Vérifier Prometheus Scraping 🔍

**Action**:
```bash
# 1. Accéder Prometheus UI
http://192.168.0.30:9090

# 2. Aller dans Status > Targets

# 3. Vérifier que ces jobs sont UP:
#    - twisterlab-api (192.168.0.30:8000)
#    - twisterlab-redis (192.168.0.30:9121)
#    - twisterlab-postgres (192.168.0.30:9187)

# 4. Si DOWN, cliquer sur le target pour voir l'erreur
```

### PRIORITÉ 3: Tester Queries Manuellement 🧪

**Action dans Grafana Explore**:
```
# 1. Aller dans Explore (icône boussole)

# 2. Tester chaque query problématique:

up{job="twisterlab-api"}
# Résultat attendu: 1

count(up{job=~".*redis.*"}) OR on() vector(0)
# Résultat attendu: 1 ou 0

http_requests_total{job="twisterlab-api"}
# Résultat attendu: Counter avec valeur

# 3. Noter quelles queries fonctionnent/échouent
```

### PRIORITÉ 4: Déployer Services Manquants 📦

**Services requis pour métriques système:**

#### A. Déployer cadvisor
```bash
docker service create \
  --name twisterlab_cadvisor \
  --mode global \
  --network twisterlab_prod \
  --publish 8080:8080 \
  --mount type=bind,source=/,target=/rootfs,readonly=true \
  --mount type=bind,source=/var/run,target=/var/run,readonly=false \
  --mount type=bind,source=/sys,target=/sys,readonly=true \
  --mount type=bind,source=/var/lib/docker/,target=/var/lib/docker,readonly=true \
  google/cadvisor:latest
```

#### B. Déployer node-exporter
```bash
docker service create \
  --name twisterlab_node-exporter \
  --mode global \
  --network twisterlab_prod \
  --publish 9100:9100 \
  --mount type=bind,source=/proc,target=/host/proc,readonly=true \
  --mount type=bind,source=/sys,target=/host/sys,readonly=true \
  --mount type=bind,source=/,target=/rootfs,readonly=true \
  prom/node-exporter:latest \
  --path.procfs=/host/proc \
  --path.sysfs=/host/sys \
  --collector.filesystem.mount-points-exclude="^/(sys|proc|dev|host|etc)($$|/)"
```

#### C. Ajouter à Prometheus Config
```yaml
scrape_configs:
  # ... existing jobs ...

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['192.168.0.30:8080']
    scrape_interval: 15s
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['192.168.0.30:9100']
    scrape_interval: 15s
```

#### D. Recharger Prometheus
```bash
PROM_ID=$(docker ps -qf name=prometheus)
docker cp /tmp/prometheus.yml ${PROM_ID}:/etc/prometheus/prometheus.yml
docker exec ${PROM_ID} kill -HUP 1
```

### PRIORITÉ 5: Ajouter Métriques Manquantes dans l'API 📊

**Métriques à ajouter dans `api/main.py`:**

```python
from prometheus_client import Histogram

# Ajouter histogram pour response time
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint', 'status']
)

# Dans le middleware:
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).observe(duration)

    return response
```

---

## 📋 CHECKLIST DE DÉPANNAGE

**Étape par étape pour résoudre les erreurs:**

- [ ] 1. Vérifier Grafana Datasource (Save & Test)
- [ ] 2. Vérifier Prometheus UI accessible (http://192.168.0.30:9090)
- [ ] 3. Vérifier Prometheus Targets (Status > Targets)
- [ ] 4. Tester queries dans Grafana Explore
- [ ] 5. Vérifier logs Grafana: `docker service logs twisterlab-monitoring_grafana`
- [ ] 6. Vérifier logs Prometheus: `docker service logs twisterlab-monitoring_prometheus`
- [ ] 7. Déployer cadvisor et node-exporter
- [ ] 8. Ajouter jobs Prometheus pour cadvisor/node-exporter
- [ ] 9. Recharger Prometheus config
- [ ] 10. Rafraîchir dashboard Grafana (F5)
- [ ] 11. Résoudre auth PostgreSQL (`pg_up 0 → 1`)
- [ ] 12. Ajouter histogram response time dans l'API

---

## 🎯 PROCHAINE ACTION IMMÉDIATE

**COMMENCER PAR** (30 secondes):

```bash
# Tester datasource Grafana
curl -u admin:admin http://192.168.0.30:3000/api/datasources/1

# Vérifier Prometheus répond
curl http://192.168.0.30:9090/-/healthy

# Lister targets Prometheus
curl http://192.168.0.30:9090/api/v1/targets
```

Si ces 3 commandes réussissent → Problème est ailleurs (queries, permissions, etc)
Si une échoue → Identifier quel service est down

---

**Auteur**: TwisterLab Diagnostic System
**Version**: 1.0
**Dernière Mise à Jour**: 2025-11-10 04:00 UTC
