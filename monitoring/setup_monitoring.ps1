# TwisterLab Monitoring Setup Instructions
# Phase 1: Fondation Infrastructure - Monitoring Setup
# Date: November 13, 2025

Write-Host "=== TwisterLab Monitoring Setup Instructions ===" -ForegroundColor Cyan
Write-Host "Setting up monitoring for CoreRTX..." -ForegroundColor Yellow
Write-Host ""

Write-Host "IMPORTANT: Docker Desktop Configuration Required" -ForegroundColor Red
Write-Host "The monitoring stack requires Linux containers." -ForegroundColor Yellow
Write-Host ""
Write-Host "To enable Linux containers:" -ForegroundColor Cyan
Write-Host "1. Right-click Docker Desktop icon in system tray" -ForegroundColor White
Write-Host "2. Select 'Switch to Linux containers'" -ForegroundColor White
Write-Host "3. Wait for Docker to restart" -ForegroundColor White
Write-Host "4. Run this script again" -ForegroundColor White
Write-Host ""

# Check Docker mode
Write-Host "Checking Docker configuration..." -ForegroundColor Green
$dockerOSType = docker info --format '{{.OSType}}' 2>$null
if ($dockerOSType -eq "linux") {
    Write-Host "SUCCESS: Docker is in Linux mode" -ForegroundColor Green

    # Start monitoring stack
    Write-Host "`nStarting monitoring stack..." -ForegroundColor Green
    Set-Location $PSScriptRoot
    docker compose -f docker-compose.monitoring.yml up -d

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nMonitoring stack started successfully!" -ForegroundColor Green
        Write-Host "`nAccess URLs:" -ForegroundColor Cyan
        Write-Host "Grafana: http://localhost:3000 (admin/twisterlab2025!)" -ForegroundColor White
        Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White

        Write-Host "`nTo check status: docker compose -f docker-compose.monitoring.yml ps" -ForegroundColor Yellow
        Write-Host "To stop: docker compose -f docker-compose.monitoring.yml down" -ForegroundColor Yellow
    } else {
        Write-Host "`nERROR: Failed to start monitoring stack" -ForegroundColor Red
        exit 1
    }

} else {
    Write-Host "ERROR: Docker is in Windows mode (current: $dockerOSType)" -ForegroundColor Red
    Write-Host "Please switch to Linux containers as described above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Install monitoring tools directly on Windows:" -ForegroundColor Cyan
    Write-Host "1. Prometheus: https://prometheus.io/download/" -ForegroundColor White
    Write-Host "2. Grafana: https://grafana.com/grafana/download" -ForegroundColor White
    Write-Host "3. Windows Exporter: https://github.com/prometheus-community/windows_exporter" -ForegroundColor White
    exit 1
}

Write-Host "`nMonitoring setup completed!" -ForegroundColor Green