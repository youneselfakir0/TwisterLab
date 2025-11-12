param()

$ErrorActionPreference = "Stop"
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TWISTERLAB CODE UPDATE (Skip Docker Build)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Copy updated code
Write-Host ""
Write-Host "[1/3] Copying updated agents code..." -ForegroundColor Yellow
$remotePath = "${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/"
scp -r agents $remotePath
scp -r monitoring $remotePath
Write-Host "OK - Code transferred" -ForegroundColor Green

# Step 2: Restart services
Write-Host ""
Write-Host "[2/3] Restarting TwisterLab services..." -ForegroundColor Yellow
ssh "$EdgeUser@$EdgeServer" "cd /home/$EdgeUser/twisterlab && docker service update --force twisterlab_api"
Write-Host "OK - Services restarting" -ForegroundColor Green

# Step 3: Health check
Write-Host ""
Write-Host "[3/3] Waiting for services (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

$apiUrl = "http://${EdgeServer}:8000/health"
try {
    Invoke-RestMethod -Uri $apiUrl -TimeoutSec 10 | Out-Null
    Write-Host "OK - API is healthy" -ForegroundColor Green
} catch {
    Write-Host "WARNING - API not ready yet" -ForegroundColor Yellow
}

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CODE UPDATE COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Updated:"
Write-Host "  - agents/metrics.py (NEW - 30+ Prometheus metrics)"
Write-Host "  - agents/real/real_classifier_agent.py (metrics integrated)"
Write-Host "  - monitoring/grafana/dashboards/ (LLM dashboard ready)"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Import Grafana dashboard: http://${EdgeServer}:3001"
Write-Host "  2. Submit test ticket to generate metrics"
Write-Host "  3. Complete ResolverAgent + DesktopCommanderAgent metrics integration"
Write-Host ""
