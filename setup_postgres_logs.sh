#!/bin/bash
echo "=== Configuration répertoire logs PostgreSQL ==="
# Créer le répertoire de logs
mkdir -p /var/log/postgresql
# Changer les permissions
chown postgres:postgres /var/log/postgresql
chmod 755 /var/log/postgresql
# Vérifier
ls -la /var/log/postgresql
echo "Répertoire de logs configuré avec succès"