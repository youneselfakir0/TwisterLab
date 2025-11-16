#!/bin/bash
echo "=== Configuration Logging PostgreSQL ==="
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 psql -U twisterlab -c "SELECT name, setting FROM pg_settings WHERE name LIKE '%log%';"
echo ""
echo "=== Logs disponibles ==="
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 find /var/lib/postgresql/data -name "*.log" 2>/dev/null || echo "Pas de logs dans data"
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 ls -la /var/log/ 2>/dev/null || echo "Pas de /var/log"
