#!/bin/bash
echo "=== Vérification configuration logging ==="
docker exec twisterlab_postgres.1.2tceu06qegmi2dq1q5olsa50q psql -U twisterlab -c "SELECT name, setting FROM pg_settings WHERE name IN ('logging_collector', 'log_min_duration_statement', 'log_min_messages');"
echo ""
echo "=== Logs disponibles ==="
docker exec twisterlab_postgres.1.2tceu06qegmi2dq1q5olsa50q ls -la /var/lib/postgresql/data/log/ 2>/dev/null || echo "Pas de logs dans data/log"