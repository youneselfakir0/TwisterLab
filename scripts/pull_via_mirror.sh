#!/bin/bash
# Pull des images via registry mirrors pour éviter Docker Hub rate limiting
# TwisterLab v1.0.0

set -e

echo "Pull des images via registry mirrors"
echo "====================================="
echo ""

# Option 1: Essayer quay.io mirror
echo "[1/2] Tentative Redis Exporter..."
if docker pull quay.io/oliver006/redis_exporter:latest 2>/dev/null; then
    docker tag quay.io/oliver006/redis_exporter:latest oliver006/redis_exporter:latest
    echo "✅ Redis Exporter obtenu via quay.io"
else
    # Fallback: essayer directement (peut échouer avec rate limit)
    echo "⚠️  Quay.io non disponible, tentative Docker Hub..."
    docker pull oliver006/redis_exporter:latest || echo "❌ Rate limit atteint"
fi

echo ""
echo "[2/2] Tentative PostgreSQL Exporter..."
# PostgreSQL exporter depuis ghcr.io (GitHub Container Registry)
if docker pull ghcr.io/prometheus-community/postgres-exporter:latest 2>/dev/null; then
    docker tag ghcr.io/prometheus-community/postgres-exporter:latest prometheuscommunity/postgres-exporter:latest
    echo "✅ PostgreSQL Exporter obtenu via ghcr.io"
else
    # Fallback
    echo "⚠️  GHCR non disponible, tentative Docker Hub..."
    docker pull prometheuscommunity/postgres-exporter:latest || echo "❌ Rate limit atteint"
fi

echo ""
echo "Vérification des images téléchargées:"
docker images | grep -E 'REPOSITORY|redis_exporter|postgres-exporter'

echo ""
echo "Si les images sont présentes, les services Docker Swarm vont redémarrer automatiquement."
echo "Vérifiez avec: docker service ls --filter name=exporter"
