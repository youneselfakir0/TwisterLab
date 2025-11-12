#!/bin/bash
# Script de redéploiement de l'API TwisterLab avec le nouvel endpoint
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 REDÉPLOIEMENT API - list_autonomous_agents endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /home/twister/TwisterLab

echo ""
echo "1️⃣ Vérification du code..."
if grep -q "list_autonomous_agents" api/routes_mcp_real.py; then
    echo "✅ Endpoint list_autonomous_agents trouvé dans le code"
    grep -n "@router.post(\"/list_autonomous_agents" api/routes_mcp_real.py | head -1
else
    echo "❌ Endpoint NON trouvé!"
    exit 1
fi

echo ""
echo "2️⃣ Vérification du conteneur actuel..."
CONTAINER_ID=$(docker ps -q -f name=twisterlab_api)
echo "Container ID: $CONTAINER_ID"

if [ -n "$CONTAINER_ID" ]; then
    echo "Vérification du code dans le conteneur..."
    docker exec "$CONTAINER_ID" grep -c "list_autonomous_agents" /app/api/routes_mcp_real.py || echo "Code pas à jour dans le conteneur"
fi

echo ""
echo "3️⃣ Reconstruction de l'image Docker..."
docker build -t twisterlab-api:latest -f Dockerfile.api .

echo ""
echo "4️⃣ Mise à jour du service..."
docker service update --image twisterlab-api:latest twisterlab_api --force

echo ""
echo "5️⃣ Attente de la stabilisation (30s)..."
sleep 30

echo ""
echo "6️⃣ Vérification du nouveau conteneur..."
NEW_CONTAINER_ID=$(docker ps -q -f name=twisterlab_api)
echo "Nouveau Container ID: $NEW_CONTAINER_ID"

if [ -n "$NEW_CONTAINER_ID" ]; then
    echo "Vérification du code dans le nouveau conteneur..."
    docker exec "$NEW_CONTAINER_ID" grep -c "list_autonomous_agents" /app/api/routes_mcp_real.py
fi

echo ""
echo "7️⃣ Test de l'endpoint..."
curl -s -X POST http://localhost:8000/v1/mcp/tools/list_autonomous_agents \
    -H 'Content-Type: application/json' \
    -d '{}' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Status: {data.get('status')}\"); print(f\"Total agents: {data.get('data', {}).get('total', 'N/A')}\")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Déploiement terminé!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
