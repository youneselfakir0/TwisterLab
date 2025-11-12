#!/bin/bash
# Script de mise à jour rapide de l'API (sans rebuild complet)
# Copie juste les nouveaux fichiers dans l'image existante

set -e

echo "🚀 MISE À JOUR RAPIDE API TWISTERLAB"
echo "====================================="
echo ""

# Récupérer l'ID du conteneur API
CONTAINER_ID=$(docker ps -q -f name=twisterlab_api)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Erreur: Conteneur twisterlab_api non trouvé"
    exit 1
fi

echo "📦 Conteneur trouvé: $CONTAINER_ID"
echo ""

# Copier les fichiers mis à jour
echo "📁 Copie des fichiers mis à jour..."
docker cp agents/ ${CONTAINER_ID}:/app/
docker cp api/ ${CONTAINER_ID}:/app/

if [ $? -eq 0 ]; then
    echo "✅ Fichiers copiés avec succès"
    echo ""

    # Redémarrer le service
    echo "🔄 Redémarrage du service API..."
    docker service update --force twisterlab_api

    if [ $? -eq 0 ]; then
        echo "✅ Service redémarré"
        echo ""
        echo "⏳ Attente du démarrage (10s)..."
        sleep 10

        # Tester l'API
        echo "🧪 Test de l'API..."
        curl -s http://localhost:8000/health | python3 -m json.tool

        echo ""
        echo "✅ MISE À JOUR TERMINÉE"
    else
        echo "❌ Erreur lors du redémarrage"
        exit 1
    fi
else
    echo "❌ Erreur lors de la copie des fichiers"
    exit 1
fi
