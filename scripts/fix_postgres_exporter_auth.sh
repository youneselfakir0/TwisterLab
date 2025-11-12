#!/bin/bash
# Script pour corriger l'authentification PostgreSQL Exporter
# TwisterLab v1.0.0

set -e

echo ""
echo "=========================================="
echo "  FIX POSTGRESQL EXPORTER AUTH"
echo "=========================================="
echo ""

# Variables
POSTGRES_PASSWORD="twisterlab_secure_db_password_2024!"

echo "[1/4] Vérification de l'état actuel..."
echo "PostgreSQL Exporter:"
docker service ps twisterlab_postgres-exporter --format "{{.CurrentState}}" | head -n1

echo ""
echo "Métrique pg_up actuelle:"
curl -s http://192.168.0.30:9187/metrics | grep "^pg_up"

echo ""
echo "[2/4] Mise à jour du service PostgreSQL avec mot de passe..."
docker service update \
  --env-add "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
  twisterlab_postgres

echo "✅ PostgreSQL service mis à jour"
echo ""

echo "[3/4] Attente de la propagation du mot de passe (30s)..."
sleep 30

echo ""
echo "[4/4] Mise à jour de l'exporter avec les bonnes credentials..."
docker service update \
  --env-rm DATA_SOURCE_NAME \
  --env-add "DATA_SOURCE_NAME=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/twisterlab_prod?sslmode=disable" \
  twisterlab_postgres-exporter

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
