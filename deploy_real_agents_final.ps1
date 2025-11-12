# TwisterLab - Final Real Agents Deployment
# Complete deployment script with validation

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Change to project directory
Set-Location "C:\twisterlab"

# Configuration
$REMOTE_HOST = "twister@192.168.0.30"
$REMOTE_PATH = "/home/twister/TwisterLab"
$IMAGE_NAME = "twisterlab-api"
$IMAGE_TAG = "real-agents-final-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$SERVICE_NAME = "twisterlab_api"

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "TwisterLab - Real Agents Deployment" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Local validation
Write-Host "Step 1/6: Validating local files..." -ForegroundColor Yellow

$required_files = @(
    "agents\real\real_monitoring_agent.py",
    "agents\real\real_backup_agent.py",
    "agents\real\real_sync_agent.py",
    "agents\real\real_classifier_agent.py",
    "agents\real\real_resolver_agent.py",
    "agents\real\real_desktop_commander_agent.py",
    "agents\real\real_maestro_agent.py"
)

$missing = @()
foreach ($file in $required_files) {
    if (-not (Test-Path $file)) { $missing += $file }
}
if ($missing.Count -gt 0) {
    Write-Host "Missing files:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" }
    exit 1
}
Write-Host "OK - All files present" -ForegroundColor Green
Write-Host ""

# Step 2: Check database config
Write-Host "Step 2/6: Checking database config..." -ForegroundColor Yellow
$config = Get-Content "agents\database\config.py" -Raw
if ($config -match "postgresql\+asyncpg://") {
    Write-Host "OK - Using asyncpg driver" -ForegroundColor Green
} else {
    Write-Host "ERROR - Not using asyncpg" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Create archive
Write-Host "Step 3/6: Creating archive..." -ForegroundColor Yellow
$archive = "agents_real.tar.gz"

if (Get-Command wsl -ErrorAction SilentlyContinue) {
    wsl bash -c "cd /mnt/c/twisterlab ; tar -czf $archive agents/real/*.py agents/database/config.py"
} else {
    Write-Host "WSL not available, using native tar..." -ForegroundColor Yellow
    tar -czf $archive agents\real\*.py agents\database\config.py
}

if (-not (Test-Path $archive)) {
    Write-Host "ERROR - Archive creation failed" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Archive created: $archive" -ForegroundColor Green
Write-Host ""

# Step 4: Transfer to server
Write-Host "Step 4/6: Transferring files..." -ForegroundColor Yellow
scp $archive "${REMOTE_HOST}:${REMOTE_PATH}/"
scp "Dockerfile.production" "${REMOTE_HOST}:${REMOTE_PATH}/"
Write-Host "OK - Files transferred" -ForegroundColor Green
Write-Host ""

# Step 5: Build on server
Write-Host "Step 5/6: Building Docker image..." -ForegroundColor Yellow
$buildCmd = @"
cd $REMOTE_PATH && \
tar -xzf $archive && \
docker build -f Dockerfile.production -t ${IMAGE_NAME}:${IMAGE_TAG} . && \
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
"@

ssh $REMOTE_HOST $buildCmd
Write-Host "OK - Image built: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Green
Write-Host ""

# Step 6: Deploy to Swarm
Write-Host "Step 6/6: Deploying to Swarm..." -ForegroundColor Yellow
$deployCmd = @"
docker service update --image ${IMAGE_NAME}:${IMAGE_TAG} $SERVICE_NAME && \
sleep 30 && \
docker service ps $SERVICE_NAME --format 'table {{.ID}}\t{{.Name}}\t{{.CurrentState}}' | head -3
"@
ssh $REMOTE_HOST $deployCmd
Write-Host "OK - Service deployed" -ForegroundColor Green
Write-Host ""

# Final validation
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Image: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Cyan
Write-Host "Service: $SERVICE_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing endpoints..." -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod -Uri "http://192.168.0.30:8000/health" -TimeoutSec 10
    Write-Host "Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
}
