# Installation des Exporters Prometheus (Redis & PostgreSQL)

## Statut Actuel

**Dashboard Grafana**: ✅ OPERATIONNEL (Version 5)
**Monitoring API**: ✅ Fonctionnel (78+ operations trackées)
**Redis/PostgreSQL Status**: 🟠 "NO EXPORTER" (affichage informatif, pas une erreur)

## Problème Identifié

Edgeserver (192.168.0.30) **n'a pas d'accès Internet**, donc Docker ne peut pas télécharger les images:
- `oliver006/redis_exporter:latest` ❌
- `prometheuscommunity/postgres-exporter:latest` ❌

## Solutions Disponibles

### Option 1: Activer Internet Temporairement (RECOMMANDÉ)

1. Configurer accès Internet sur edgeserver
2. Exécuter le script de déploiement:
   ```powershell
   .\scripts\deploy_exporters_direct.ps1
   ```
3. Une fois les images téléchargées, désactiver Internet

### Option 2: Utiliser un Proxy Docker

1. Configurer un proxy Docker sur une machine avec Internet
2. Modifier `/etc/docker/daemon.json` sur edgeserver:
   ```json
   {
     "registry-mirrors": ["http://proxy-ip:port"]
   }
   ```
3. Redémarrer Docker: `sudo systemctl restart docker`
4. Exécuter le script de déploiement

### Option 3: Registry Privé avec Images Pré-téléchargées

1. Sur une machine avec Internet, télécharger les images:
   ```bash
   docker pull oliver006/redis_exporter:latest
   docker pull prometheuscommunity/postgres-exporter:latest
   ```

2. Sauvegarder les images:
   ```bash
   docker save oliver006/redis_exporter:latest -o redis-exporter.tar
   docker save prometheuscommunity/postgres-exporter:latest -o postgres-exporter.tar
   ```

3. Copier les fichiers .tar sur edgeserver:
   ```powershell
   scp redis-exporter.tar twister@192.168.0.30:/tmp/
   scp postgres-exporter.tar twister@192.168.0.30:/tmp/
   ```

4. Sur edgeserver, charger les images:
   ```bash
   ssh twister@192.168.0.30
   docker load -i /tmp/redis-exporter.tar
   docker load -i /tmp/postgres-exporter.tar
   ```

5. Exécuter le script de déploiement:
   ```powershell
   .\scripts\deploy_exporters_direct.ps1
   ```

## Configuration Prometheus (Après Installation)

Une fois les exporters déployés, ajouter les jobs dans `monitoring/prometheus/config/prometheus.yml`:

```yaml
scrape_configs:
  # ... jobs existants ...

  - job_name: 'twisterlab-redis'
    static_configs:
      - targets: ['192.168.0.30:9121']
    scrape_interval: 15s
    metrics_path: '/metrics'

  - job_name: 'twisterlab-postgres'
    static_configs:
      - targets: ['192.168.0.30:9187']
    scrape_interval: 15s
    metrics_path: '/metrics'
```

Recharger Prometheus:
```bash
ssh twister@192.168.0.30
docker exec $(docker ps -qf name=prometheus) kill -HUP 1
```

## Vérification

1. **Exporters déployés**:
   ```bash
   ssh twister@192.168.0.30 "docker service ls --filter name=exporter"
   ```

2. **Métriques accessibles**:
   ```bash
   curl http://192.168.0.30:9121/metrics | head -n 10  # Redis
   curl http://192.168.0.30:9187/metrics | head -n 10  # PostgreSQL
   ```

3. **Prometheus scraping**:
   ```
   http://192.168.0.30:9090/targets
   ```
   - Vérifier que `twisterlab-redis` et `twisterlab-postgres` sont UP

4. **Dashboard Grafana**:
   ```
   http://192.168.0.30:3000/d/twisterlab-agents-realtime
   ```
   - Redis Status: devrait afficher "CONNECTED" ✅ (vert)
   - PostgreSQL Status: devrait afficher "CONNECTED" ✅ (vert)

## Métriques Disponibles Après Installation

### Redis Exporter
- `redis_up` - Redis disponible (1=UP, 0=DOWN)
- `redis_connected_clients` - Nombre de clients connectés
- `redis_used_memory_bytes` - Mémoire utilisée
- `redis_commands_processed_total` - Commandes traitées
- `redis_keyspace_hits_total` - Cache hits
- `redis_keyspace_misses_total` - Cache misses

### PostgreSQL Exporter
- `pg_up` - PostgreSQL disponible (1=UP, 0=DOWN)
- `pg_stat_database_numbackends` - Connexions actives
- `pg_stat_database_tup_returned` - Lignes retournées
- `pg_stat_database_tup_inserted` - Lignes insérées
- `pg_database_size_bytes` - Taille de la base
- `pg_stat_activity_count` - Nombre de sessions

## Fichiers Modifiés

- ✅ `infrastructure/docker/docker-compose.unified.yml` - Services exporters ajoutés
- ✅ `scripts/deploy_exporters_direct.ps1` - Script de déploiement
- ✅ `monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json` - Dashboard Version 5

## Notes

- Les exporters utilisent très peu de ressources (128MB RAM, 0.1 CPU chacun)
- Aucune interruption de service lors du déploiement
- Les exporters se connectent automatiquement à Redis et PostgreSQL
- Les credentials sont configurés dans les variables d'environnement

## Auteur

TwisterLab Team - 2025-11-10
