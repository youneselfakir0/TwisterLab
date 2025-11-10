#!/bin/bash
# Script de rebuild de l'image API TwisterLab
# Version: 1.0.0
# Date: 2025-11-10

set -e

echo "🔨 REBUILD TWISTERLAB API IMAGE"
echo "================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
IMAGE_NAME="twisterlab/api"
VERSION="v1.0.0"
DOCKERFILE="infrastructure/dockerfiles/Dockerfile.api"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}❌ Erreur: $DOCKERFILE introuvable${NC}"
    echo "Assurez-vous d'être dans le répertoire racine de TwisterLab"
    exit 1
fi

echo -e "${YELLOW}📁 Répertoire de travail: $(pwd)${NC}"
echo ""

# Build l'image
echo -e "${YELLOW}🔨 Building image ${IMAGE_NAME}:${VERSION}...${NC}"
docker build \
    -f "$DOCKERFILE" \
    -t "${IMAGE_NAME}:latest" \
    -t "${IMAGE_NAME}:${VERSION}" \
    --build-arg VERSION="${VERSION}" \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image buildée avec succès${NC}"
    echo ""
    
    # Afficher les images
    echo -e "${YELLOW}📦 Images créées:${NC}"
    docker images | grep "${IMAGE_NAME}"
    echo ""
    
    echo -e "${GREEN}✅ REBUILD TERMINÉ${NC}"
    echo ""
    echo "Pour redéployer:"
    echo "  docker stack deploy -c infrastructure/docker/docker-compose.unified.yml twisterlab"
else
    echo -e "${RED}❌ Erreur lors du build${NC}"
    exit 1
fi
