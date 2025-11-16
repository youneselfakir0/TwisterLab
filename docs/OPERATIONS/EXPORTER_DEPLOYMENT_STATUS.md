# État du Déploiement des Exporters Prometheus
**Date**: 2025-11-10
**Session**: Déploiement Redis et PostgreSQL Exporters

---

## ✅ REDIS EXPORTER - OPÉRATIONNEL

**Service**: `twisterlab_redis-exporter`
**Image**: `oliver006/redis_exporter:latest` (via quay.io)
**Port**: 9121
**Status**: ✅ **CONNECTÉ** (`redis_up 1`)

### Métriques Disponibles
```
redis_up 1
redis_connected_clients 1
redis_uptime_in_seconds 18959+
```

### Configuration Prometheus
```yaml
- job_name: 'twisterlab-redis'
  static_configs:
    - targets: ['192.168.0.30:9121']
  metrics_path: '/metrics'
  scrape_interval: 15s
```

### État dans Grafana
- ✅ Panneau "Redis Status" affiche **CONNECTED** (vert)
- ✅ Métriques temps réel disponibles
- ✅ Auto-refresh 10 secondes

---

## ⚠️ POSTGRESQL EXPORTER - PROBLÈME D'AUTHENTIFICATION

**Service**: `twisterlab_postgres-exporter`
**Image**: `prometheuscommunity/postgres-exporter:latest` (via quay.io)
**Port**: 9187
**Status**: ⚠️ **DÉPLOYÉ mais NON CONNECTÉ** (`pg_up 0`)

### Problème Identifié
```
Error: pq: password authentication failed for user "twisterlab"
```

### Diagnostic
- ✅ Service en cours d'exécution (1/1 replicas)
- ✅ Port 9187 accessible
- ✅ Réseau `twisterlab_backend` configuré
- ❌ Authentification PostgreSQL échoue
- ❌ Le service PostgreSQL n'a **pas de mot de passe** configuré (variable env vide)

### Configuration Actuelle
```bash
# PostgreSQL service
POSTGRES_PASSWORD=    # ← VIDE!
POSTGRES_USER=twisterlab

# Exporter essaie de se connecter avec:
DATA_SOURCE_NAME=postgresql://postgres:@postgres:5432/twisterlab_prod?sslmode=disable
```

### Solutions Possibles

#### Option 1: Configurer un mot de passe PostgreSQL (RECOMMANDÉ)
```bash
# 1. Mettre à jour le service PostgreSQL avec mot de passe
docker service update \
  --env-add POSTGRES_PASSWORD=twisterlab_secure_db_password_2024! \
  twisterlab_postgres

# 2. Mettre à jour l'exporter avec le même mot de passe
docker service update \
  --env-rm DATA_SOURCE_NAME \
  --env-add 'DATA_SOURCE_NAME=postgresql://postgres:twisterlab_secure_db_password_2024!@postgres:5432/twisterlab_prod?sslmode=disable' \
  twisterlab_postgres-exporter
```

#### Option 2: Configurer PostgreSQL en mode trust
```bash
# Modifier pg_hba.conf pour accepter connexions sans mot de passe
# (NON RECOMMANDÉ en production)
```

#### Option 3: Créer un utilisateur dédié pour l'exporter
```sql
-- Depuis PostgreSQL
CREATE USER postgres_exporter WITH PASSWORD 'monitoring_password';
GRANT pg_monitor TO postgres_exporter;
GRANT CONNECT ON DATABASE twisterlab_prod TO postgres_exporter;
```

---

## 📊 ÉTAT FINAL DES SERVICES

| Service | Replicas | Port | Status | Prometheus Job |
|---------|----------|------|--------|----------------|
| `twisterlab_postgres` | 1/1 | - | ✅ Running | - |
| `twisterlab_redis` | 1/1 | - | ✅ Running | - |
| `twisterlab_redis-exporter` | 1/1 | 9121 | ✅ Connected (`redis_up 1`) | `twisterlab-redis` ✅ |
| `twisterlab_postgres-exporter` | 1/1 | 9187 | ⚠️ Auth Failed (`pg_up 0`) | `twisterlab-postgres` ⚠️ |
| `twisterlab-monitoring_prometheus` | 1/1 | 9090 | ✅ Running | - |

---

## 🔧 CONFIGURATION PROMETHEUS

**Fichier**: `monitoring/prometheus/config/prometheus.yml`

### Nouveaux Jobs Ajoutés
```yaml
scrape_configs:
  # ... jobs existants ...

  - job_name: 'twisterlab-redis'
    static_configs:
      - targets: ['192.168.0.30:9121']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'twisterlab-postgres'
    static_configs:
      - targets: ['192.168.0.30:9187']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Rechargement Effectué
```bash
# Configuration copiée et Prometheus rechargé avec succès
docker cp /tmp/prometheus.yml ab9d06197512:/etc/prometheus/prometheus.yml
docker exec ab9d06197512 kill -HUP 1
```

---

## 📈 GRAFANA DASHBOARD

**URL**: http://192.168.0.30:3000/d/twisterlab-agents-realtime

### Panneaux Mis à Jour

#### Redis Status (Panel 2)
- **Avant**: NO EXPORTER (orange)
- **Après**: ✅ **CONNECTED** (vert)
- **Query**: `count(up{job=~".*redis.*"}) OR on() vector(0)`

#### PostgreSQL Status (Panel 3)
- **Avant**: NO EXPORTER (orange)
- **Après**: ⚠️ **NO EXPORTER** (orange - toujours)
- **Raison**: `pg_up 0` à cause du problème d'auth
- **Query**: `count(up{job=~".*postgres.*"}) OR on() vector(0)`

---

## 🚀 PROCHAINES ÉTAPES

### Priorité 1: Résoudre PostgreSQL Auth
- [ ] Vérifier la configuration du service PostgreSQL existant
- [ ] Décider: ajouter mot de passe ou configurer trust auth
- [ ] Mettre à jour l'exporter avec les bonnes credentials
- [ ] Vérifier `pg_up 1` dans les métriques
- [ ] Confirmer "CONNECTED" dans Grafana

### Priorité 2: Métriques Additionnelles
- [ ] Configurer alertes Prometheus
  - Redis: `redis_up == 0`
  - PostgreSQL: `pg_up == 0`
- [ ] Ajouter panels Grafana pour métriques détaillées:
  - Redis: `redis_commands_processed_total`, `redis_memory_used_bytes`
  - PostgreSQL: `pg_stat_database_numbackends`, `pg_stat_activity_count`

### Priorité 3: Documentation
- [ ] Mettre à jour docker-compose.unified.yml avec configuration finale
- [ ] Documenter la procédure de dépannage
- [ ] Ajouter monitoring setup au README.md

---

## 📝 COMMANDES UTILES

### Vérifier les Exporters
```bash
# Redis Exporter
curl http://192.168.0.30:9121/metrics | grep redis_up

# PostgreSQL Exporter
curl http://192.168.0.30:9187/metrics | grep pg_up
```

### Logs des Services
```bash
# Redis Exporter
docker service logs twisterlab_redis-exporter --tail 50

# PostgreSQL Exporter
docker service logs twisterlab_postgres-exporter --tail 50
```

### Prometheus Targets
```bash
# Vérifier les targets actives
curl -s http://192.168.0.30:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job | contains("twisterlab"))'
```

---

## 🎯 RÉSUMÉ

**Déploiement Exporters**: ✅ 50% Complet (1/2 opérationnel)

- ✅ **Redis Exporter**: Déployé et fonctionnel
- ⚠️ **PostgreSQL Exporter**: Déployé mais authentification à corriger
- ✅ **Prometheus**: Configuré pour scraper les deux exporters
- ✅ **Grafana**: Dashboard mis à jour avec graceful fallbacks
- ✅ **Images Docker**: Téléchargées via quay.io (bypass rate limit)
- ✅ **Scripts**: Créés pour déploiement futur

**Temps Total**: ~45 minutes
**Problèmes Rencontrés**: Docker Hub rate limit (résolu), PostgreSQL auth (en cours)
**Prochaine Action**: Configurer PostgreSQL authentication

---

**Auteur**: TwisterLab Team
**Version**: 1.0.0
**Dernière Mise à Jour**: 2025-11-10 03:30 UTC
