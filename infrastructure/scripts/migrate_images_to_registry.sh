#!/bin/bash
# Script de migration des images TwisterLab vers registry locale
# Copie toutes les images Docker Hub vers la registry locale

set -e

REGISTRY_HOST="${REGISTRY_HOST:-192.168.0.30:5000}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 MIGRATION DES IMAGES VERS REGISTRY LOCALE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Images TwisterLab à migrer
IMAGES=(
    "python:3.11-slim"
    "python:3.12-slim"
    "postgres:16-alpine"
    "redis:7-alpine"
    "traefik:v2.10"
    "prom/prometheus:latest"
    "grafana/grafana:latest"
    "registry:2"
    "joxit/docker-registry-ui:latest"
)

# Compteurs
TOTAL=${#IMAGES[@]}
SUCCESS=0
FAILED=0

echo "📋 Images à migrer: $TOTAL"
echo ""

for IMAGE in "${IMAGES[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 Migration: $IMAGE"
    echo ""
    
    # Extraire nom et tag
    IMAGE_NAME="${IMAGE%%:*}"
    IMAGE_TAG="${IMAGE##*:}"
    
    # Nom local
    LOCAL_NAME="${REGISTRY_HOST}/$(basename $IMAGE_NAME):${IMAGE_TAG}"
    
    echo "   Source: $IMAGE"
    echo "   Cible:  $LOCAL_NAME"
    echo ""
    
    # Pull depuis Docker Hub (si pas déjà présent)
    echo "   1/3 Pull depuis Docker Hub..."
    if docker pull "$IMAGE" 2>&1 | grep -q "429 Too Many Requests"; then
        echo "   ⚠️  Rate limit Docker Hub - utilisation de l'image locale si disponible"
        if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
            echo "   ❌ Image non disponible localement"
            FAILED=$((FAILED + 1))
            continue
        fi
    fi
    
    # Tag pour registry locale
    echo "   2/3 Tag pour registry locale..."
    docker tag "$IMAGE" "$LOCAL_NAME"
    
    # Push vers registry locale
    echo "   3/3 Push vers registry locale..."
    if docker push "$LOCAL_NAME"; then
        echo "   ✅ Migration réussie"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "   ❌ Échec du push"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RÉSUMÉ DE LA MIGRATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   Total:   $TOTAL images"
echo "   Succès:  $SUCCESS images"
echo "   Échecs:  $FAILED images"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ Toutes les images migrées avec succès!"
else
    echo "⚠️  Certaines images n'ont pas pu être migrées"
fi

echo ""
echo "📋 Catalogue de la registry locale:"
curl -s "http://${REGISTRY_HOST}/v2/_catalog" | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
