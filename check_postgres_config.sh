#!/bin/bash
echo "=== PostgreSQL Configuration Check ==="
docker exec twisterlab_postgres.1.y6hdertgnrdd7e5yxcmorldgt psql -U twisterlab -c "SELECT name, setting FROM pg_settings WHERE name IN ('wal_level', 'synchronous_commit', 'maintenance_work_mem');"
echo ""
echo "=== PostgreSQL Error Count (last 5 minutes) ==="
docker exec twisterlab_postgres.1.y6hdertgnrdd7e5yxcmorldgt psql -U twisterlab -c "SELECT COUNT(*) as error_count FROM pg_log WHERE message LIKE '%ERROR%' AND log_time > NOW() - INTERVAL '5 minutes';"