#!/bin/bash
# Script pour corriger l'authentification PostgreSQL Exporter
# TwisterLab v1.0.0

set -e

echo ""
echo "=========================================="
echo "  FIX POSTGRESQL EXPORTER AUTH"
echo "=========================================="
echo ""

# Function to read secret from Docker secret file or environment variable
get_secret() {
    SECRET_NAME=$1
    SECRET_PATH="/run/secrets/$SECRET_NAME"
    if [ -f "$SECRET_PATH" ]; then
        cat "$SECRET_PATH"
    elif [ -n "${!SECRET_NAME}" ]; then
        echo "${!SECRET_NAME}"
    else
        echo "Error: Secret '$SECRET_NAME' not found in Docker secrets or environment variables." >&2
        exit 1
    fi
}

# Variables
POSTGRES_PASSWORD=$(get_secret "postgres_password")

echo "[1/4] Vérification de l'état actuel..."
echo "PostgreSQL Exporter:"
docker service ps twisterlab_postgres-exporter --format "{{.CurrentState}}" | head -n1

echo ""
echo "Métrique pg_up actuelle:"
curl -s http://192.168.0.30:9187/metrics | grep "^pg_up"

echo ""
echo "[2/4] Mise à jour du service PostgreSQL pour utiliser le secret Docker..."
# Ensure the postgres service has the secret attached and uses a file-backed password
docker service update \
  --secret-add postgres_password \
  --env-add "POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password" \
  twisterlab_postgres || true

echo "✅ PostgreSQL service configured to use Docker secret (postgres_password)"
echo ""

echo "[3/4] Attente de la propagation du mot de passe (30s)..."
sleep 30

echo ""
echo "[4/4] Mise à jour de l'exporter pour utiliser le secret Docker..."
# Attach the postgres secret to the exporter and use DATA_SOURCE_NAME__FILE to avoid inline password
docker service update \
  --secret-add postgres_password \
  --env-rm DATA_SOURCE_NAME \
  --env-add "DATA_SOURCE_NAME__FILE=/run/secrets/postgres_password" \
  twisterlab_postgres-exporter || true

echo "✅ Exporter configured to use Docker secret (postgres_password)"

echo "✅ Exporter mis à jour"
echo ""

echo "Attente de la connexion (20s)..."
sleep 20

echo ""
echo "=========================================="
echo "  VERIFICATION FINALE"
echo "=========================================="
echo ""

echo "Métrique pg_up:"
curl -s http://192.168.0.30:9187/metrics | grep "^pg_up"

echo ""
echo "Si pg_up = 1, le problème est résolu!"
echo "Sinon, vérifiez les logs:"
echo "  docker service logs twisterlab_postgres-exporter --tail 20"
echo ""
