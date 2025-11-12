#!/bin/bash
# Script de build et push de l'API TwisterLab vers registry locale
# Évite complètement Docker Hub

set -e

REGISTRY_HOST="${REGISTRY_HOST:-192.168.0.30:5000}"
API_IMAGE="${REGISTRY_HOST}/twisterlab-api"
API_TAG="${API_TAG:-latest}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  BUILD API TWISTERLAB - REGISTRY LOCALE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Configuration:"
echo "   Registry:   $REGISTRY_HOST"
echo "   Image:      $API_IMAGE:$API_TAG"
echo "   Dockerfile: Dockerfile.api"
echo ""

cd /home/twister/TwisterLab

# Étape 1: Vérifier que Dockerfile.api utilise la registry locale
echo "1️⃣  Vérification du Dockerfile..."
if grep -q "FROM python:3.11-slim" Dockerfile.api; then
    echo "   ⚠️  Dockerfile utilise Docker Hub - modification..."
    
    # Créer version avec registry locale
    sed "s|FROM python:3.11-slim|FROM ${REGISTRY_HOST}/python:3.11-slim|g" Dockerfile.api > Dockerfile.api.local
    DOCKERFILE="Dockerfile.api.local"
    echo "   ✅ Dockerfile modifié: $DOCKERFILE"
else
    DOCKERFILE="Dockerfile.api"
    echo "   ✅ Dockerfile OK"
fi

# Étape 2: Build de l'image
echo ""
echo "2️⃣  Build de l'image..."
echo "   Command: docker build -t $API_IMAGE:$API_TAG -f $DOCKERFILE ."
echo ""

if docker build -t "$API_IMAGE:$API_TAG" -f "$DOCKERFILE" .; then
    echo ""
    echo "   ✅ Build réussi"
else
    echo ""
    echo "   ❌ Échec du build"
    exit 1
fi

# Étape 3: Push vers registry locale
echo ""
echo "3️⃣  Push vers registry locale..."
if docker push "$API_IMAGE:$API_TAG"; then
    echo "   ✅ Push réussi"
else
    echo "   ❌ Échec du push"
    exit 1
fi

# Étape 4: Vérifier l'image dans la registry
echo ""
echo "4️⃣  Vérification dans la registry..."
if curl -s "http://${REGISTRY_HOST}/v2/twisterlab-api/tags/list" | grep -q "$API_TAG"; then
    echo "   ✅ Image disponible dans la registry"
else
    echo "   ❌ Image non trouvée dans la registry"
    exit 1
fi

# Étape 5: Mise à jour du service Docker Swarm
echo ""
echo "5️⃣  Mise à jour du service Docker Swarm..."
if docker service update --image "$API_IMAGE:$API_TAG" twisterlab_api; then
    echo "   ✅ Service mis à jour"
else
    echo "   ❌ Échec de la mise à jour"
    exit 1
fi

# Étape 6: Attendre la convergence
echo ""
echo "6️⃣  Attente de la convergence du service (30s)..."
sleep 30

# Étape 7: Vérifier le service
echo ""
echo "7️⃣  Vérification du service..."
REPLICAS=$(docker service ls --filter name=twisterlab_api --format "{{.Replicas}}")
echo "   Replicas: $REPLICAS"

if echo "$REPLICAS" | grep -q "1/1"; then
    echo "   ✅ Service opérationnel"
else
    echo "   ⚠️  Service pas complètement démarré"
fi

# Étape 8: Test de l'endpoint
echo ""
echo "8️⃣  Test de l'endpoint list_autonomous_agents..."
sleep 5

RESPONSE=$(curl -s -X POST http://localhost:8000/v1/mcp/tools/list_autonomous_agents \
    -H 'Content-Type: application/json' \
    -d '{}')

if echo "$RESPONSE" | grep -q '"status":"ok"'; then
    TOTAL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['total'])")
    echo "   ✅ Endpoint opérationnel - $TOTAL agents"
else
    echo "   ❌ Endpoint non fonctionnel"
    echo "   Response: $RESPONSE"
fi

# Nettoyage
if [ -f "Dockerfile.api.local" ]; then
    rm -f Dockerfile.api.local
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BUILD ET DÉPLOIEMENT TERMINÉS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Informations:"
echo "   Image:    $API_IMAGE:$API_TAG"
echo "   Registry: http://${REGISTRY_HOST}"
echo "   UI:       http://${REGISTRY_HOST%:*}:5001"
echo ""
echo "📝 Vérifier dans l'UI: http://192.168.0.30:5001"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
