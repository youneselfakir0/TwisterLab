# ============================================================================
# TwisterLab - Deploy Real Agents FINAL
# ============================================================================

$SERVER = "twister@192.168.0.30"
$REMOTE_PATH = "/home/twister/TwisterLab"

Write-Host "`n=== TWISTERLAB REAL AGENTS DEPLOYMENT ===" -ForegroundColor Cyan
Write-Host "Starting deployment at $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Yellow

# Step 1: Verify Docker image has psutil
Write-Host "[1/7] Verifying psutil in Docker image..." -ForegroundColor Yellow
$psutilCheck = ssh $SERVER "docker run --rm twisterlab-api:latest pip list 2>/dev/null | grep psutil"
if ($psutilCheck -match "psutil") {
    Write-Host "  OK: psutil is installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR: psutil is missing! Image needs rebuild." -ForegroundColor Red
    Write-Host "  Run: ssh $SERVER 'cd $REMOTE_PATH && docker build -f Dockerfile.production -t twisterlab-api:latest .'" -ForegroundColor Yellow
    exit 1
}

# Step 2: Verify real agents are in image
Write-Host "`n[2/7] Verifying real agents in image..." -ForegroundColor Yellow
$realAgentsCheck = ssh $SERVER "docker run --rm twisterlab-api:latest ls /app/agents/real/ 2>/dev/null | wc -l"
if ([int]$realAgentsCheck -ge 7) {
    Write-Host "  OK: Found $realAgentsCheck agent files" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Real agents not found in image!" -ForegroundColor Red
    exit 1
}

# Step 3: Verify orchestrator imports real agents
Write-Host "`n[3/7] Verifying orchestrator configuration..." -ForegroundColor Yellow
$orchestratorCheck = ssh $SERVER "docker run --rm twisterlab-api:latest grep 'RealMonitoringAgent' /app/agents/orchestrator/autonomous_orchestrator.py 2>/dev/null"
if ($orchestratorCheck) {
    Write-Host "  OK: Orchestrator uses RealMonitoringAgent" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Orchestrator not configured for real agents!" -ForegroundColor Red
    exit 1
}

# Step 4: Update service with correct DATABASE_URL
Write-Host "`n[4/7] Updating Docker service..." -ForegroundColor Yellow
ssh $SERVER @"
docker service update \
  --image twisterlab-api:latest \
  --env-add 'DATABASE_URL=postgresql+asyncpg://twisterlab:twisterlab2024!@postgres:5432/twisterlab_prod' \
  twisterlab_api
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Service updated" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Service update failed!" -ForegroundColor Red
    exit 1
}

# Step 5: Wait for service convergence
Write-Host "`n[5/7] Waiting for service convergence (40 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 40

# Step 6: Check service status
Write-Host "`n[6/7] Checking service status..." -ForegroundColor Yellow
$serviceStatus = ssh $SERVER "docker service ps twisterlab_api --filter 'desired-state=running' --format '{{.CurrentState}}' | head -1"
Write-Host "  Status: $serviceStatus" -ForegroundColor Cyan

if ($serviceStatus -match "Running") {
    Write-Host "  OK: Service is running" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Service may not be running correctly" -ForegroundColor Yellow
    Write-Host "`nLogs (last 30 lines):" -ForegroundColor Cyan
    ssh $SERVER "docker service logs twisterlab_api --tail 30"
}

# Step 7: Test health endpoint
Write-Host "`n[7/7] Testing API health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://192.168.0.30:8000/health" -TimeoutSec 5
    Write-Host "  OK: API is responding" -ForegroundColor Green
    Write-Host "  Health: $($health.status) | Version: $($health.version)" -ForegroundColor Cyan
} catch {
    Write-Host "  ERROR: API not responding!" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Yellow
}

# Final: Test MonitoringAgent with real data
Write-Host "`n=== FINAL TEST: MonitoringAgent ===" -ForegroundColor Cyan
try {
    $body = @{ operation = "health_check" } | ConvertTo-Json
    $result = Invoke-RestMethod -Method POST -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" -Body $body -ContentType "application/json" -TimeoutSec 10

    Write-Host "`nAgent Status: $($result.status)" -ForegroundColor Cyan

    # Check if we have real data (not mock)
    if ($result.result.results.services.api.status -eq "mock_response") {
        Write-Host "`nRESULT: FAILED - Agent still returns MOCK data" -ForegroundColor Red
        Write-Host "The real agents are NOT active yet." -ForegroundColor Yellow
    } else {
        Write-Host "`nRESULT: SUCCESS - Agent returns REAL data!" -ForegroundColor Green
        Write-Host "Real agents are operational!" -ForegroundColor Green

        # Display sample data
        Write-Host "`nSample metrics:" -ForegroundColor Cyan
        $result.result.results | ConvertTo-Json -Depth 3
    }
} catch {
    Write-Host "`nERROR: Failed to test MonitoringAgent" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
}

Write-Host "`n=== DEPLOYMENT COMPLETED at $(Get-Date -Format 'HH:mm:ss') ===" -ForegroundColor Cyan
