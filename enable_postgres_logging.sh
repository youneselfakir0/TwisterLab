#!/bin/bash
echo "=== Activation logging avancé PostgreSQL ==="
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 psql -U twisterlab -c "ALTER SYSTEM SET logging_collector = 'on';"
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 psql -U twisterlab -c "ALTER SYSTEM SET log_min_duration_statement = '500';"
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 psql -U twisterlab -c "ALTER SYSTEM SET log_min_messages = 'debug';"
echo "Redémarrage PostgreSQL pour appliquer les changements..."
docker service update --force twisterlab_postgres
sleep 15
echo "Vérification de la configuration après redémarrage..."
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 psql -U twisterlab -c "SELECT name, setting FROM pg_settings WHERE name IN ('logging_collector', 'log_min_duration_statement', 'log_min_messages');"
