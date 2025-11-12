#!/bin/bash
# Déploiement cadvisor et node-exporter pour métriques système complètes
# TwisterLab v1.0.0

set -e

echo ""
echo "=========================================="
echo "  DÉPLOIEMENT EXPORTERS SYSTÈME"
echo "=========================================="
echo ""

# 1. Déployer cAdvisor (métriques conteneurs)
echo "[1/4] Déploiement cAdvisor..."
docker service create \
  --name twisterlab_cadvisor \
  --mode global \
  --network twisterlab_prod \
  --publish 8080:8080 \
  --mount type=bind,source=/,target=/rootfs,readonly=true \
  --mount type=bind,source=/var/run,target=/var/run,readonly=false \
  --mount type=bind,source=/sys,target=/sys,readonly=true \
  --mount type=bind,source=/var/lib/docker/,target=/var/lib/docker,readonly=true \
  --label prometheus.scrape=true \
  --label prometheus.port=8080 \
  google/cadvisor:latest

echo "✅ cAdvisor déployé (port 8080)"
echo ""

# 2. Déployer Node Exporter (métriques système)
echo "[2/4] Déploiement Node Exporter..."
docker service create \
  --name twisterlab_node-exporter \
  --mode global \
  --network twisterlab_prod \
  --publish 9100:9100 \
  --mount type=bind,source=/proc,target=/host/proc,readonly=true \
  --mount type=bind,source=/sys,target=/host/sys,readonly=true \
  --mount type=bind,source=/,target=/rootfs,readonly=true \
  --label prometheus.scrape=true \
  --label prometheus.port=9100 \
  prom/node-exporter:latest \
  --path.procfs=/host/proc \
  --path.sysfs=/host/sys \
  --collector.filesystem.mount-points-exclude="^/(sys|proc|dev|host|etc)($$|/)"

echo "✅ Node Exporter déployé (port 9100)"
echo ""

# 3. Attendre le démarrage
echo "[3/4] Attente du démarrage (20 secondes)..."
sleep 20

# 4. Vérifier les services
echo "[4/4] Vérification des services..."
echo ""
docker service ls --filter name=cadvisor
docker service ls --filter name=node-exporter

echo ""
echo "Test des endpoints:"
echo ""
echo "cAdvisor:"
curl -s http://localhost:8080/metrics | grep -E '^container_cpu_usage_seconds_total' | head -n 3 || echo "  En attente..."

echo ""
echo "Node Exporter:"
curl -s http://localhost:9100/metrics | grep -E '^node_filesystem_size_bytes' | head -n 3 || echo "  En attente..."

echo ""
echo "=========================================="
echo "✅ DÉPLOIEMENT TERMINÉ!"
echo "=========================================="
echo ""
echo "Services déployés:"
echo "  - twisterlab_cadvisor (port 8080)"
echo "  - twisterlab_node-exporter (port 9100)"
echo ""
echo "Prochaines étapes:"
echo "  1. Ajouter jobs Prometheus (cadvisor, node-exporter)"
echo "  2. Recharger Prometheus config"
echo "  3. Vérifier dashboard Grafana"
echo ""
