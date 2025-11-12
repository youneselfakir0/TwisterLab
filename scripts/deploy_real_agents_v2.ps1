# Deploy Real Agents to edgeserver - Version 2
# This version updates the Docker IMAGE, not just the container

param(
    [string]$EdgeServer = "192.168.0.30",
    [string]$User = "twister"
)

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  TWISTERLAB REAL AGENTS DEPLOYMENT V2" -ForegroundColor Green
Write-Host "  (Updates Docker Image)" -ForegroundColor Yellow
Write-Host "==========================================`n" -ForegroundColor Cyan

# Step 1: Check connectivity
Write-Host "[1/7] Checking edgeserver connectivity..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $EdgeServer -Count 1 -Quiet
if (-not $ping) {
    Write-Host "[ERROR] Cannot reach edgeserver ($EdgeServer)" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Edgeserver accessible`n" -ForegroundColor Green

# Step 2: Create archive
Write-Host "[2/7] Creating agents archive..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveName = "real_agents_$timestamp.tar.gz"
$archivePath = "C:\TwisterLab\$archiveName"

try {
    Set-Location C:\TwisterLab

    # Check if agents/real directory exists and has files
    if (-not (Test-Path "agents\real")) {
        Write-Host "[ERROR] agents\real directory not found!" -ForegroundColor Red
        exit 1
    }

    $agentFiles = Get-ChildItem -Path "agents\real" -Filter "*.py" -Recurse
    if ($agentFiles.Count -eq 0) {
        Write-Host "[ERROR] No Python files found in agents\real!" -ForegroundColor Red
        exit 1
    }

    Write-Host "Found $($agentFiles.Count) agent files" -ForegroundColor Gray

    # Create tar.gz
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

# Step 3: Copy to edgeserver
Write-Host "[3/7] Copying archive to edgeserver..." -ForegroundColor Yellow
try {
    scp $archivePath ${User}@${EdgeServer}:/tmp/
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

# Step 4: Find running container
Write-Host "[4/7] Finding running container..." -ForegroundColor Yellow
$containerName = ssh ${User}@$EdgeServer "docker ps --filter name=twisterlab_api --format '{{.Names}}' | head -1"
$containerName = $containerName.Trim()

if ([string]::IsNullOrEmpty($containerName)) {
    Write-Host "[ERROR] No container found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Container: $containerName`n" -ForegroundColor Green

# Step 5: Extract files in container
Write-Host "[5/7] Deploying agents to container..." -ForegroundColor Yellow
$deployCommands = @"
# Copy archive into container
docker cp /tmp/$archiveName ${containerName}:/tmp/

# Extract in container
docker exec $containerName bash -c 'cd /opt/twisterlab && tar -xzf /tmp/$archiveName && ls -lh /opt/twisterlab/agents/real/'

# Install dependencies
docker exec $containerName bash -c 'pip install psutil redis -q'

echo "[OK] Files extracted"
"@

try {
    ssh ${User}@$EdgeServer $deployCommands
    Write-Host "[OK] Agents deployed in container`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    exit 1
}

# Step 6: Commit container to new image
Write-Host "[6/7] Creating new Docker image..." -ForegroundColor Yellow
$newImageTag = "twisterlab-api:real-agents-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

$commitCmd = "docker commit $containerName $newImageTag"
try {
    ssh ${User}@$EdgeServer $commitCmd
    Write-Host "[OK] Image created: $newImageTag`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create image" -ForegroundColor Red
    exit 1
}

# Step 7: Update service to use new image
Write-Host "[7/7] Updating service with new image..." -ForegroundColor Yellow
$updateCmd = "docker service update --image $newImageTag twisterlab_api"

try {
    Write-Host "Executing: docker service update..." -ForegroundColor Gray
    ssh ${User}@$EdgeServer $updateCmd

    Write-Host "`nWaiting for service to stabilize (15 seconds)..." -ForegroundColor Gray
    Start-Sleep -Seconds 15

    # Test API
    try {
        $response = Invoke-RestMethod -Uri "http://${EdgeServer}:8000/health" -Method GET -TimeoutSec 5
        Write-Host "[OK] API is responsive" -ForegroundColor Green
        Write-Host "Status: $($response.status)" -ForegroundColor Gray
    } catch {
        Write-Host "[WARN] API not yet ready" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Service update failed" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "  New Image: $newImageTag" -ForegroundColor White
Write-Host "  Service: twisterlab_api" -ForegroundColor White
Write-Host "  Agents Path: /opt/twisterlab/agents/real/" -ForegroundColor White
Write-Host ""
Write-Host "  API: http://${EdgeServer}:8000" -ForegroundColor Cyan
Write-Host "  Docs: http://${EdgeServer}:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Test commands:" -ForegroundColor Yellow
Write-Host "  # List agents" -ForegroundColor Gray
Write-Host "  curl http://${EdgeServer}:8000/api/v1/autonomous/agents" -ForegroundColor Gray
Write-Host ""
Write-Host "  # Test MonitoringAgent" -ForegroundColor Gray
Write-Host "  curl -X POST http://${EdgeServer}:8000/api/v1/autonomous/agents/MonitoringAgent/execute \" -ForegroundColor Gray
Write-Host "    -H 'Content-Type: application/json' \" -ForegroundColor Gray
Write-Host "    -d '{`"operation`":`"health_check`"}'" -ForegroundColor Gray
Write-Host ""
Write-Host "==========================================`n" -ForegroundColor Cyan

# Cleanup
Remove-Item $archivePath -Force -ErrorAction SilentlyContinue

Write-Host "[INFO] Deployment finished successfully!" -ForegroundColor Green
Write-Host "`nNext step: Verify agents with integration tests" -ForegroundColor Cyan
Write-Host "python tests\test_integration_real_agents.py`n" -ForegroundColor White

exit 0
