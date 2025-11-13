# TwisterLab Monitoring Startup Script
# Run this to start the monitoring stack

Write-Host "Starting TwisterLab Monitoring Stack..." -ForegroundColor Cyan

# Change to monitoring directory
Set-Location "C:\TwisterLab\monitoring"

# Start the monitoring stack
Write-Host "Starting Prometheus, Node Exporter, and Grafana..." -ForegroundColor Yellow
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to start
Start-Sleep -Seconds 10

# Check service status
Write-Host "
Checking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.monitoring.yml ps

Write-Host "
Monitoring URLs:" -ForegroundColor Green
Write-Host "Grafana: http://localhost:3000 (admin/twisterlab2025!)" -ForegroundColor White
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "Node Exporter: http://localhost:9100" -ForegroundColor White

Write-Host "
To stop monitoring: docker-compose -f docker-compose.monitoring.yml down" -ForegroundColor Yellow
