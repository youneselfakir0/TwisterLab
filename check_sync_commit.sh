#!/bin/bash
echo "=== Vérification synchronous_commit ==="
docker exec twisterlab_postgres.1.d45yh53uituxcyz3pmh8eljk8 psql -U twisterlab -c "SELECT name, setting FROM pg_settings WHERE name = 'synchronous_commit';"
