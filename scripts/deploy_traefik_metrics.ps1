#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Deploy Traefik Metrics Monitoring
# Version: 1.0.0
# Date: 2025-11-11
#
# Description: Configure Prometheus to scrape Traefik metrics (zero conflicts)
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "`n=== DEPLOIEMENT TRAEFIK METRICS MONITORING ===" -ForegroundColor Cyan

# 1. Copier la config Prometheus mise à jour
Write-Host "`n[1/3] Copie de la configuration Prometheus..." -ForegroundColor Yellow
scp monitoring/prometheus/config/prometheus.yml twister@192.168.0.30:/tmp/prometheus.yml
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Impossible de copier prometheus.yml" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Configuration copiée" -ForegroundColor Green

# 2. Mettre à jour Prometheus
Write-Host "`n[2/3] Mise à jour de Prometheus..." -ForegroundColor Yellow
ssh twister@192.168.0.30 @"
promId=`$(docker ps --filter name=prometheus --format '{{.ID}}' | head -n1)
if [ -z "`$promId" ]; then
    echo "ERREUR: Container Prometheus introuvable"
    exit 1
fi

docker cp /tmp/prometheus.yml `${promId}:/etc/prometheus/prometheus.yml
docker exec `${promId} kill -HUP 1

echo "OK - Prometheus rechargé"
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Mise à jour Prometheus échouée" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Prometheus rechargé" -ForegroundColor Green

# 3. Vérifier les targets
Write-Host "`n[3/3] Vérification des targets Prometheus..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$targets = ssh twister@192.168.0.30 "curl -s http://localhost:9090/api/v1/targets"
if ($targets -match "traefik-metrics") {
    Write-Host "OK - Target traefik-metrics actif" -ForegroundColor Green
} else {
    Write-Host "ATTENTION: Target traefik-metrics non trouvé" -ForegroundColor Yellow
}

# 4. Résumé
Write-Host "`n=== DEPLOIEMENT TERMINE ===" -ForegroundColor Cyan
Write-Host "`nServices de monitoring actifs:" -ForegroundColor White
Write-Host "  - TwisterLab API (192.168.0.30:8000)" -ForegroundColor Green
Write-Host "  - Redis (192.168.0.30:9121)" -ForegroundColor Green
Write-Host "  - PostgreSQL (192.168.0.30:9187)" -ForegroundColor Green
Write-Host "  - Traefik Metrics (traefik:8080/metrics)" -ForegroundColor Green
Write-Host "  - Prometheus (self)" -ForegroundColor Green

Write-Host "`nAccès Prometheus: http://192.168.0.30:9090/targets" -ForegroundColor Cyan
Write-Host "Accès Grafana: http://192.168.0.30:3000" -ForegroundColor Cyan

Write-Host "`nMétriques Traefik disponibles:" -ForegroundColor White
Write-Host "  - traefik_entrypoint_requests_total" -ForegroundColor Gray
Write-Host "  - traefik_entrypoint_request_duration_seconds" -ForegroundColor Gray
Write-Host "  - traefik_service_requests_total" -ForegroundColor Gray
Write-Host "  - traefik_service_request_duration_seconds" -ForegroundColor Gray

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Yellow
Write-Host "1. Ouvrir Grafana: http://192.168.0.30:3000" -ForegroundColor White
Write-Host "2. Vérifier les métriques Traefik dans les dashboards" -ForegroundColor White
Write-Host "3. (Optionnel) Créer un dashboard spécifique Traefik" -ForegroundColor White
