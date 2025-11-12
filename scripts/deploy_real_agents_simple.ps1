# Deploy Real Agents to edgeserver - Simple Version
# No emojis, no special characters

param(
    [string]$EdgeServer = "192.168.0.30",
    [string]$Container = "twisterlab_api"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TWISTERLAB REAL AGENTS DEPLOYMENT" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check connectivity
Write-Host "[1/6] Checking edgeserver connectivity..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $EdgeServer -Count 1 -Quiet
if (-not $ping) {
    Write-Host "[ERROR] Cannot reach edgeserver ($EdgeServer)" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Edgeserver accessible`n" -ForegroundColor Green

# Step 2: Check container
Write-Host "[2/6] Checking Docker container..." -ForegroundColor Yellow
try {
    $containerCheck = ssh twister@$EdgeServer "docker ps --filter name=$Container --format '{{.Names}}'" 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($containerCheck)) {
        Write-Host "[ERROR] Container $Container not found" -ForegroundColor Red
        Write-Host "Available containers:" -ForegroundColor Yellow
        ssh twister@$EdgeServer "docker ps --format '{{.Names}}'"
        exit 1
    }
    Write-Host "[OK] Container found: $containerCheck`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to check container: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Create archive
Write-Host "[3/6] Creating agents archive..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveName = "real_agents_$timestamp.tar.gz"
$archivePath = "C:\TwisterLab\$archiveName"

try {
    # Use tar (available in Windows 10+)
    cd C:\TwisterLab
    tar -czf $archivePath agents/real/

    if (Test-Path $archivePath) {
        $size = (Get-Item $archivePath).Length / 1KB
        Write-Host "[OK] Archive created: $archiveName ($([math]::Round($size, 2)) KB)`n" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Archive not created" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to create archive: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Copy to edgeserver
Write-Host "[4/6] Copying archive to edgeserver..." -ForegroundColor Yellow
try {
    scp $archivePath twister@${EdgeServer}:/tmp/
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Archive copied to /tmp/`n" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] SCP failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to copy: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Extract in container
Write-Host "[5/6] Deploying agents in container..." -ForegroundColor Yellow
$deployScript = @"
cd /tmp
docker cp $archiveName ${Container}:/tmp/
docker exec $Container bash -c 'cd /opt/twisterlab && tar -xzf /tmp/$archiveName'
docker exec $Container bash -c 'pip install psutil redis -q'
echo "[OK] Agents deployed"
"@

try {
    ssh twister@$EdgeServer $deployScript
    Write-Host "[OK] Deployment complete`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Deployment failed: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Restart API
Write-Host "[6/6] Restarting API service..." -ForegroundColor Yellow
try {
    # Find the service name
    $serviceName = ssh twister@$EdgeServer "docker service ls --filter name=twisterlab_api --format '{{.Name}}'" 2>$null

    if ([string]::IsNullOrEmpty($serviceName)) {
        Write-Host "[WARN] No service found, trying container restart..." -ForegroundColor Yellow
        ssh twister@$EdgeServer "docker restart $Container"
    } else {
        Write-Host "Restarting service: $serviceName" -ForegroundColor Gray
        ssh twister@$EdgeServer "docker service update --force $serviceName"
    }

    Write-Host "Waiting for API to be ready..." -ForegroundColor Gray
    Start-Sleep -Seconds 10

    # Test API
    $testUrl = "http://${EdgeServer}:8000/health"
    try {
        $response = Invoke-RestMethod -Uri $testUrl -Method GET -TimeoutSec 5
        Write-Host "[OK] API is responsive`n" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] API not yet ready (this is normal)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Restart may have failed, check manually" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Archive: $archiveName" -ForegroundColor White
Write-Host "  Target: ${Container}@${EdgeServer}" -ForegroundColor White
Write-Host "  Path: /opt/twisterlab/agents/real/" -ForegroundColor White
Write-Host ""
Write-Host "  API: http://${EdgeServer}:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Test command:" -ForegroundColor Yellow
Write-Host "  curl http://${EdgeServer}:8000/agents/monitoring/execute -X POST \" -ForegroundColor Gray
Write-Host "    -H 'Content-Type: application/json' \" -ForegroundColor Gray
Write-Host "    -d '{`"operation`":`"health_check`"}'" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================`n" -ForegroundColor Cyan

# Cleanup
Remove-Item $archivePath -Force -ErrorAction SilentlyContinue

Write-Host "[INFO] Deployment script finished" -ForegroundColor Green
exit 0
