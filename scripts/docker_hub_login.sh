#!/bin/bash
# Configuration Docker Hub authentication pour éviter rate limiting
# TwisterLab v1.0.0

echo "Configuration Docker Hub Authentication"
echo "========================================"
echo ""
echo "Pour éviter le rate limiting Docker Hub, vous devez:"
echo "1. Créer un compte gratuit sur https://hub.docker.com"
echo "2. Générer un token d'accès (Settings > Security > New Access Token)"
echo ""
read -p "Docker Hub Username: " DOCKER_USERNAME
read -sp "Docker Hub Token/Password: " DOCKER_PASSWORD
echo ""

# Login Docker
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Authentication Docker Hub réussie!"
    echo ""
    echo "Vous pouvez maintenant:"
    echo "  docker pull oliver006/redis_exporter:latest"
    echo "  docker pull prometheuscommunity/postgres-exporter:latest"
else
    echo "❌ Échec de l'authentication"
    exit 1
fi
