# Check TwisterLab Monitoring Services Status
# This script checks the health of all monitoring services

Write-Host " Checking TwisterLab Monitoring Services Status..." -ForegroundColor Cyan

# Check Docker Swarm status
Write-Host "`n Docker Swarm Status:" -ForegroundColor Yellow
try {
    $swarmStatus = docker info --format json | ConvertFrom-Json
    if ($swarmStatus.Swarm.LocalNodeState -eq "active") {
        Write-Host " Docker Swarm is active" -ForegroundColor Green
    } else {
        Write-Host " Docker Swarm is not active" -ForegroundColor Red
    }
} catch {
    Write-Host " Cannot check Docker Swarm status" -ForegroundColor Red
}

# Check monitoring stack services
Write-Host "`n Monitoring Stack Services:" -ForegroundColor Yellow
try {
    $services = docker stack services twisterlab-monitoring
    Write-Host " Services deployed:" -ForegroundColor Green
    Write-Host $services -ForegroundColor White
} catch {
    Write-Host " Failed to check service status" -ForegroundColor Red
}

# Check Docker containers
Write-Host "`n Docker Containers Status:" -ForegroundColor Yellow
try {
    $containers = docker stack ps twisterlab-monitoring --format "table {{.Name}}\t{{.Image}}\t{{.CurrentState}}"
    Write-Host $containers -ForegroundColor White
} catch {
    Write-Host " Cannot check container status" -ForegroundColor Red
}

# Display access URLs
Write-Host "`n Access URLs (if services are running):" -ForegroundColor Cyan
Write-Host " Prometheus:    http://localhost:9091" -ForegroundColor White
Write-Host " Grafana:       http://localhost:3000 (admin via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD or Docker secret)" -ForegroundColor White
Write-Host " Jaeger:        http://localhost:16686" -ForegroundColor White
Write-Host " Alertmanager:  http://localhost:9093" -ForegroundColor White

Write-Host "`n Troubleshooting Tips:" -ForegroundColor Blue
Write-Host " If services are not running, check '\''docker stack ps twisterlab-monitoring'\''" -ForegroundColor White
Write-Host " If ports are not accessible, check firewall settings" -ForegroundColor White
Write-Host " If health checks fail, check container logs" -ForegroundColor White
