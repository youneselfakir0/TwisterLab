#!/bin/bash
echo "=== Correction PostgreSQL synchronous_commit ==="
docker exec twisterlab_postgres.1.y6hdertgnrdd7e5yxcmorldgt psql -U twisterlab -c "ALTER SYSTEM SET synchronous_commit = 'off';"
echo "Redémarrage PostgreSQL..."
docker service update --force twisterlab_postgres
sleep 10
echo "Vérification de la configuration après redémarrage..."
docker exec twisterlab_postgres.1.y6hdertgnrdd7e5yxcmorldgt psql -U twisterlab -c "SELECT name, setting FROM pg_settings WHERE name = 'synchronous_commit';"
