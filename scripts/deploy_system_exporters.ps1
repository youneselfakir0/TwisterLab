# Script de deploiement cadvisor et node-exporter pour metriques systeme
# Complete le monitoring TwisterLab avec CPU, Memory, Disk, Network

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "DEPLOIEMENT SYSTEM EXPORTERS (CADVISOR + NODE-EXPORTER)" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

$edgeserver = "192.168.0.30"
$user = "twister"

# 1. Deployer cAdvisor (Container metrics)
Write-Host "[1/4] Deploiement cAdvisor..." -ForegroundColor Yellow
Write-Host "  - Fournit: Container CPU, Memory, Network" -ForegroundColor Gray
Write-Host ""

ssh "${user}@${edgeserver}" @"
docker service create \
  --name twisterlab_cadvisor \
  --mode global \
  --network twisterlab_prod \
  --publish 8081:8080 \
  --mount type=bind,source=/,target=/rootfs,readonly=true \
  --mount type=bind,source=/var/run,target=/var/run,readonly=false \
  --mount type=bind,source=/sys,target=/sys,readonly=true \
  --mount type=bind,source=/var/lib/docker/,target=/var/lib/docker,readonly=true \
  --label prometheus.scrape=true \
  --label prometheus.port=8081 \
  gcr.io/cadvisor/cadvisor:latest
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECHEC deploiement cadvisor" -ForegroundColor Red
    exit 1
}
Write-Host "✅ cAdvisor deploye" -ForegroundColor Green
Write-Host ""

# 2. Deployer Node Exporter (Host metrics)
Write-Host "[2/4] Deploiement Node Exporter..." -ForegroundColor Yellow
Write-Host "  - Fournit: Disk, Network I/O, System metrics" -ForegroundColor Gray
Write-Host ""

ssh "${user}@${edgeserver}" @"
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
  --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)(\$\$|/)'
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECHEC deploiement node-exporter" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node Exporter deploye" -ForegroundColor Green
Write-Host ""

# 3. Attendre le demarrage
Write-Host "[3/4] Attente du demarrage (20 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# 4. Verifier les services
Write-Host "[4/4] Verification des services..." -ForegroundColor Yellow
Write-Host ""

$services = ssh "${user}@${edgeserver}" "docker service ls --filter name=cadvisor --filter name=node-exporter --format 'table {{.Name}}\t{{.Replicas}}\t{{.Ports}}'"
Write-Host $services

Write-Host ""
Write-Host "Test des endpoints metrics..." -ForegroundColor Yellow

# Test cAdvisor
$cadvisorTest = ssh "${user}@${edgeserver}" "curl -s http://localhost:8080/metrics | head -n 5"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ cAdvisor metrics disponibles (port 8080)" -ForegroundColor Green
} else {
    Write-Host "⚠️  cAdvisor metrics non accessibles" -ForegroundColor Yellow
}

# Test Node Exporter
$nodeTest = ssh "${user}@${edgeserver}" "curl -s http://localhost:9100/metrics | head -n 5"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node Exporter metrics disponibles (port 9100)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Node Exporter metrics non accessibles" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT TERMINE!" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROCHAINES ETAPES:" -ForegroundColor Yellow
Write-Host "  1. Ajouter jobs Prometheus (cadvisor, node-exporter)" -ForegroundColor White
Write-Host "  2. Recharger config Prometheus" -ForegroundColor White
Write-Host "  3. Verifier dashboard Grafana" -ForegroundColor White
Write-Host ""
Write-Host "METRIQUES DISPONIBLES:" -ForegroundColor Yellow
Write-Host "  ✅ Container CPU/Memory (cadvisor)" -ForegroundColor Green
Write-Host "  ✅ Disk Usage (node-exporter)" -ForegroundColor Green
Write-Host "  ✅ Network I/O (node-exporter)" -ForegroundColor Green
Write-Host ""
