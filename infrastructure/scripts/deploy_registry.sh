#!/bin/bash
# Script de déploiement de la Docker Registry locale TwisterLab
# Permet d'éviter les limitations de Docker Hub

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  DÉPLOIEMENT DOCKER REGISTRY LOCALE - TwisterLab"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
REGISTRY_HOST="${REGISTRY_HOST:-192.168.0.30}"
REGISTRY_PORT="${REGISTRY_PORT:-5000}"
REGISTRY_UI_PORT="${REGISTRY_UI_PORT:-5001}"

echo "📍 Configuration:"
echo "   Registry: http://${REGISTRY_HOST}:${REGISTRY_PORT}"
echo "   UI:       http://${REGISTRY_HOST}:${REGISTRY_UI_PORT}"
echo ""

# Étape 1: Arrêter les conteneurs existants
echo "1️⃣  Arrêt des conteneurs existants..."
docker-compose -f infrastructure/docker/docker-compose.registry.yml down 2>/dev/null || true

# Étape 2: Créer les volumes
echo ""
echo "2️⃣  Création des volumes..."
docker volume create registry_data 2>/dev/null || echo "   Volume registry_data existe déjà"

# Étape 3: Démarrer la registry
echo ""
echo "3️⃣  Démarrage de la registry..."
docker-compose -f infrastructure/docker/docker-compose.registry.yml up -d

# Étape 4: Attendre que la registry soit prête
echo ""
echo "4️⃣  Attente de la disponibilité (15s)..."
sleep 15

# Étape 5: Vérifier la santé
echo ""
echo "5️⃣  Vérification de la santé..."
if curl -s http://localhost:${REGISTRY_PORT}/v2/ | grep -q '{}'; then
    echo "   ✅ Registry accessible"
else
    echo "   ❌ Registry non accessible"
    exit 1
fi

# Étape 6: Configurer Docker daemon pour registry insecure
echo ""
echo "6️⃣  Configuration Docker daemon..."
DAEMON_JSON="/etc/docker/daemon.json"

if [ -f "$DAEMON_JSON" ]; then
    echo "   ⚠️  $DAEMON_JSON existe, sauvegarde..."
    sudo cp "$DAEMON_JSON" "${DAEMON_JSON}.backup.$(date +%Y%m%d_%H%M%S)"
fi

sudo tee "$DAEMON_JSON" > /dev/null <<EOF
{
  "insecure-registries": ["${REGISTRY_HOST}:${REGISTRY_PORT}"],
  "registry-mirrors": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

echo "   ✅ Configuration mise à jour"

# Étape 7: Redémarrer Docker daemon
echo ""
echo "7️⃣  Redémarrage Docker daemon..."
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "   ⏳ Attente de Docker (10s)..."
sleep 10

# Étape 8: Redémarrer la registry après le restart Docker
echo ""
echo "8️⃣  Redémarrage de la registry..."
docker-compose -f infrastructure/docker/docker-compose.registry.yml up -d

sleep 5

# Étape 9: Vérification finale
echo ""
echo "9️⃣  Vérification finale..."
if curl -s http://localhost:${REGISTRY_PORT}/v2/_catalog | grep -q 'repositories'; then
    echo "   ✅ Registry opérationnelle"
else
    echo "   ❌ Registry non opérationnelle"
    exit 1
fi

# Étape 10: Afficher le statut
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ REGISTRY LOCALE DÉPLOYÉE AVEC SUCCÈS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Services:"
docker ps --filter "label=com.twisterlab.service=registry" --format "   • {{.Names}} ({{.Status}})"
docker ps --filter "label=com.twisterlab.service=registry-ui" --format "   • {{.Names}} ({{.Status}})"
echo ""
echo "🌐 Accès:"
echo "   Registry API: http://${REGISTRY_HOST}:${REGISTRY_PORT}"
echo "   Registry UI:  http://${REGISTRY_HOST}:${REGISTRY_UI_PORT}"
echo ""
echo "📝 Utilisation:"
echo "   # Tag d'une image locale"
echo "   docker tag mon-image:latest ${REGISTRY_HOST}:${REGISTRY_PORT}/mon-image:latest"
echo ""
echo "   # Push vers registry locale"
echo "   docker push ${REGISTRY_HOST}:${REGISTRY_PORT}/mon-image:latest"
echo ""
echo "   # Pull depuis registry locale"
echo "   docker pull ${REGISTRY_HOST}:${REGISTRY_PORT}/mon-image:latest"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
