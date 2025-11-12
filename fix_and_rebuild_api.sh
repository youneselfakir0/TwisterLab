#!/bin/bash
# Fix Dockerfile.api to use correct entry point

cd /home/twister/TwisterLab

# Create fixed Dockerfile
cat Dockerfile.api.local | sed 's/FROM python:3.11-slim/FROM python:3.10-slim/' | \
  sed 's|CMD \["python", "swarm_ia_api.py"\]|CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]|' \
  > Dockerfile.api.final

echo "✅ Dockerfile.api.final créé"
echo ""
echo "🔍 Vérification CMD:"
grep "^CMD" Dockerfile.api.final

echo ""
echo "🏗️  Rebuild de l'image..."
docker build -f Dockerfile.api.final -t twisterlab-api:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build réussi"
    echo ""
    echo "🚀 Déploiement..."
    docker service update twisterlab_api --image twisterlab-api:latest --force
else
    echo "❌ Build échoué"
    exit 1
fi
