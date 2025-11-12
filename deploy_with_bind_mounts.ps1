# Deploy with bind mounts for live code updates
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"

Write-Host "Deploying TwisterLab with code bind mounts..." -ForegroundColor Cyan

# Step 1: Create agents directory on edgeserver
Write-Host "`n[1/4] Creating directories on EdgeServer..." -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "mkdir -p ~/twisterlab/agents ~/twisterlab/monitoring ~/twisterlab/logs"
Write-Host "OK" -ForegroundColor Green

# Step 2: Copy agents code
Write-Host "`n[2/4] Copying agents code..." -ForegroundColor Yellow
scp -r agents ${EdgeUser}@${EdgeServer}:~/twisterlab/
scp -r monitoring ${EdgeUser}@${EdgeServer}:~/twisterlab/
Write-Host "OK" -ForegroundColor Green

# Step 3: Copy updated docker-compose
Write-Host "`n[3/4] Copying docker-compose.production.yml..." -ForegroundColor Yellow
scp docker-compose.production.yml ${EdgeUser}@${EdgeServer}:~/twisterlab/
Write-Host "OK" -ForegroundColor Green

# Step 4: Redeploy stack
Write-Host "`n[4/4] Redeploying stack with bind mounts..." -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "cd ~/twisterlab && docker stack deploy -c docker-compose.production.yml twisterlab"
Write-Host "OK - Redeploying" -ForegroundColor Green

Write-Host "`nWaiting for services (30s)..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Health check
try {
    $health = Invoke-RestMethod -Uri "http://${EdgeServer}:8000/health" -TimeoutSec 10
    Write-Host "`n✅ API is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "`n⚠️  API not ready yet" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE WITH BIND MOUNTS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nCode is now live-mounted from ~/twisterlab/agents/"
Write-Host "Any changes to agents/ will be reflected immediately!"
Write-Host ""
