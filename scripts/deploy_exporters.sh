#!/bin/bash
# Script de déploiement des exporters Redis et PostgreSQL sur edgeserver
# TwisterLab v1.0.0 - Monitoring Setup

set -e

echo ""
echo "=========================================="
echo "  DEPLOIEMENT EXPORTERS PROMETHEUS"
echo "=========================================="
echo ""

# Function to read secret from Docker secret file or environment variable
get_secret() {
    SECRET_NAME=$1
    SECRET_PATH="/run/secrets/$SECRET_NAME"
    if [ -f "$SECRET_PATH" ]; then
        cat "$SECRET_PATH"
    elif [ -n "${!SECRET_NAME}" ]; then
        echo "${!SECRET_NAME}"
    else
        echo "Error: Secret '$SECRET_NAME' not found in Docker secrets or environment variables." >&2
        exit 1
    fi
}

REDIS_PASSWORD=$(get_secret "redis_password")
POSTGRES_PASSWORD=$(get_secret "postgres_password")

# 1. Déployer Redis Exporter
echo "[1/5] Déploiement Redis Exporter..."
docker service create \
  --name twisterlab_redis-exporter \
  --network twisterlab_prod \
  --network twisterlab_backend \
  --publish 9121:9121 \
  --constraint 'node.role==manager' \
  --label prometheus.scrape=true \
  --label prometheus.port=9121 \
  --secret redis_password \
  oliver006/redis_exporter:latest \
  --redis.addr=twisterlab_redis:6379 \
  --redis.password-file=/run/secrets/redis_password

echo "✅ Redis Exporter créé"
echo ""

# 2. Déployer PostgreSQL Exporter
echo "[2/5] Déploiement PostgreSQL Exporter..."
docker service create \
  --name twisterlab_postgres-exporter \
  --network twisterlab_prod \
  --network twisterlab_backend \
  --publish 9187:9187 \
  --constraint 'node.role==manager' \
  --env DATA_SOURCE_NAME="postgresql://twisterlab:$(cat /run/secrets/postgres_password)@twisterlab_postgres:5432/twisterlab_prod?sslmode=disable" \
  --label prometheus.scrape=true \
  --label prometheus.port=9187 \
  --secret postgres_password \
  prometheuscommunity/postgres-exporter:latest

echo "✅ PostgreSQL Exporter créé"
echo ""

# 3. Attendre le démarrage
echo "[3/5] Attente du démarrage (30 secondes)..."
sleep 30

# 4. Vérifier les services
echo "[4/5] Vérification des services..."
docker service ls --filter name=exporter

echo ""
echo "[5/5] Test des endpoints metrics..."
echo ""
echo "Redis Exporter:"
curl -s http://localhost:9121/metrics | head -n 5
echo ""
echo "PostgreSQL Exporter:"
curl -s http://localhost:9187/metrics | head -n 5

echo ""
echo "=========================================="
echo "✅ DEPLOIEMENT TERMINE!"
echo "=========================================="
echo ""
echo "Services déployés:"
echo "  - twisterlab_redis-exporter (port 9121)"
echo "  - twisterlab_postgres-exporter (port 9187)"
echo ""
echo "Prochaines étapes:"
echo "  1. Configurer Prometheus (ajouter jobs)"
echo "  2. Recharger Prometheus"
echo "  3. Vérifier dashboard Grafana"
echo ""
