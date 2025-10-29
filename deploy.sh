#!/bin/bash

# Script de déploiement automatisé pour TwisterLab
# Utilisation: ./deploy.sh [environment]
# Environment: prod (par défaut), staging, dev

set -e

ENVIRONMENT=${1:-prod}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"
ENV_FILE=".env.${ENVIRONMENT}"

echo "🚀 Déploiement de TwisterLab en environnement: $ENVIRONMENT"

# Vérifier les prérequis
echo "📋 Vérification des prérequis..."

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Fichier $ENV_FILE manquant. Copiez .env.prod.example vers $ENV_FILE et configurez-le."
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Fichier $COMPOSE_FILE manquant."
    exit 1
fi

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p logs
mkdir -p deployment/nginx/ssl
mkdir -p secrets

# Générer des mots de passe sécurisés si nécessaire
if [ ! -f "secrets/postgres_password.txt" ]; then
    echo "🔐 Génération du mot de passe PostgreSQL..."
    openssl rand -base64 32 > secrets/postgres_password.txt
fi

if [ ! -f "secrets/redis_password.txt" ]; then
    echo "🔐 Génération du mot de passe Redis..."
    openssl rand -base64 32 > secrets/redis_password.txt
fi

# Construire et démarrer les services
echo "🐳 Construction des images Docker..."
docker-compose -f $COMPOSE_FILE build --no-cache

echo "🚀 Démarrage des services..."
docker-compose -f $COMPOSE_FILE up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier la santé des services
echo "🏥 Vérification de la santé des services..."
docker-compose -f $COMPOSE_FILE ps

# Exécuter les migrations de base de données
echo "🗄️ Exécution des migrations de base de données..."
docker-compose -f $COMPOSE_FILE exec -T api alembic upgrade head

# Configuration SSL si domaine configuré
if [ -n "$DOMAIN_NAME" ] && [ "$DOMAIN_NAME" != "your-domain.com" ]; then
    echo "🔒 Configuration SSL pour $DOMAIN_NAME..."
    docker-compose -f $COMPOSE_FILE --profile certbot run --rm certbot
    docker-compose -f $COMPOSE_FILE exec nginx nginx -s reload
fi

# Test final
echo "🧪 Test des endpoints..."
curl -f http://localhost/health || echo "⚠️ Endpoint health non accessible"
curl -f https://$DOMAIN_NAME/health 2>/dev/null || echo "⚠️ Endpoint HTTPS non accessible"

echo "✅ Déploiement terminé!"
echo ""
echo "📊 Services disponibles:"
echo "  - API: http://localhost:8000"
echo "  - WebUI: http://localhost:3000"
if [ -n "$DOMAIN_NAME" ] && [ "$DOMAIN_NAME" != "your-domain.com" ]; then
    echo "  - Production: https://$DOMAIN_NAME"
fi
echo ""
echo "📋 Commandes utiles:"
echo "  - Logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  - Stop: docker-compose -f $COMPOSE_FILE down"
echo "  - Restart: docker-compose -f $COMPOSE_FILE restart"