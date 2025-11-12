Write-Host "VALIDATION FINALE - TWISTERLAB DASHBOARDS" -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Blue
Write-Host ""

$nodeIP = "edgeserver.twisterlab.local"

Write-Host "Testing Traefik Dashboard..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://$nodeIP`:8084" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "Traefik Dashboard: SUCCESS (HTTP $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Traefik Dashboard: FAILED" -ForegroundColor Red
}

Write-Host "Testing OpenWebUI..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://$nodeIP`:8083" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "OpenWebUI: SUCCESS (HTTP $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "OpenWebUI: FAILED" -ForegroundColor Red
}

Write-Host "Testing Grafana..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://$nodeIP`:3000" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "Grafana: SUCCESS (HTTP $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Grafana: FAILED" -ForegroundColor Red
}

Write-Host "Testing Prometheus..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://$nodeIP`:9090" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "Prometheus: SUCCESS (HTTP $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Prometheus: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "URLs d'acces:" -ForegroundColor Blue
Write-Host "  Traefik Dashboard: http://$nodeIP`:8084" -ForegroundColor White
Write-Host "  OpenWebUI: http://$nodeIP`:8083" -ForegroundColor White
Write-Host "  Grafana: http://$nodeIP`:3000" -ForegroundColor White
Write-Host "  Prometheus: http://$nodeIP`:9090" -ForegroundColor White

Write-Host ""
Write-Host "Travail termine - $(Get-Date)" -ForegroundColor Green
