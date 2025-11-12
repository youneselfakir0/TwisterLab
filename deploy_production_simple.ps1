# DEPLOYMENT PRODUCTION - REAL AGENTS WITH PSYCOPG2
$ErrorActionPreference = "Stop"

Write-Host "`n=== DEPLOYMENT PRODUCTION - REAL AGENTS ===" -ForegroundColor Cyan

$EDGE_SERVER = "192.168.0.30"
$SSH_USER = "twister"
$REMOTE_DIR = "/home/twister/TwisterLab"
$IMAGE_NAME = "twisterlab-api"
$IMAGE_TAG = "production-real-agents-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$SERVICE_NAME = "twisterlab_api"

# Step 1: Upload files
Write-Host "[1/6] Upload Dockerfile..." -ForegroundColor Green
scp C:\TwisterLab\Dockerfile.production ${SSH_USER}@${EDGE_SERVER}:${REMOTE_DIR}/Dockerfile.production

Write-Host "[2/6] Upload API..." -ForegroundColor Green
scp C:\TwisterLab\api_main_corrected.py ${SSH_USER}@${EDGE_SERVER}:${REMOTE_DIR}/api/main.py

# Step 2: Build image
Write-Host "[3/6] Build Docker image (2-3 minutes)..." -ForegroundColor Green

ssh ${SSH_USER}@${EDGE_SERVER} @"
cd ${REMOTE_DIR}
docker build -f Dockerfile.production -t ${IMAGE_NAME}:${IMAGE_TAG} .
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:production
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    exit 1
}

Write-Host "Build OK!" -ForegroundColor Green

# Step 3: Verify image
Write-Host "[4/6] Verify psycopg2..." -ForegroundColor Green

ssh ${SSH_USER}@${EDGE_SERVER} "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} python -c 'import psycopg2; print(psycopg2.__version__)'"

# Step 4: Deploy
Write-Host "[5/6] Deploy to Swarm..." -ForegroundColor Green

ssh ${SSH_USER}@${EDGE_SERVER} "docker service update --image ${IMAGE_NAME}:${IMAGE_TAG} ${SERVICE_NAME}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "DEPLOY FAILED - Rolling back..." -ForegroundColor Red
    ssh ${SSH_USER}@${EDGE_SERVER} "docker service update --rollback ${SERVICE_NAME}"
    exit 1
}

Write-Host "Waiting for convergence (45s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Step 5: Test
Write-Host "[6/6] Testing..." -ForegroundColor Green

Write-Host "Test 1: Health check" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://${EDGE_SERVER}:8000/health"
    Write-Host "OK: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Test 2: Agents list" -ForegroundColor Cyan
try {
    $agents = Invoke-RestMethod -Uri "http://${EDGE_SERVER}:8000/api/v1/autonomous/agents"
    Write-Host "OK: $($agents.total) agents" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Test 3: MonitoringAgent execution" -ForegroundColor Cyan
try {
    $body = @{ operation = "health_check" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://${EDGE_SERVER}:8000/api/v1/autonomous/agents/MonitoringAgent/execute" -Method POST -Body $body -ContentType "application/json"

    $response | ConvertTo-Json -Depth 5 | Write-Host

    if ($response.result.metrics.cpu_usage -eq "23%") {
        Write-Host "WARNING: Still mock data!" -ForegroundColor Red
    } else {
        Write-Host "SUCCESS: Real data detected!" -ForegroundColor Green
    }
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== DEPLOYMENT DONE ===" -ForegroundColor Cyan
Write-Host "Image: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Green
Write-Host "Service: ${SERVICE_NAME}" -ForegroundColor Green
