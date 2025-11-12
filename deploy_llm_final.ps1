# TwisterLab LLM Deployment Script
$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TWISTERLAB LLM DEPLOYMENT v1.0       " -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

$StartTime = Get-Date
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"

# Step 1: Check Ollama
Write-Host "[1/5] Checking Ollama GPU service..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://${EdgeServer}:11434/api/tags" -TimeoutSec 5
    Write-Host "  ✓ Ollama GPU is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama not accessible!" -ForegroundColor Red
    exit 1
}

# Step 2: Run quick test
Write-Host "`n[2/5] Running quick LLM test..." -ForegroundColor Yellow
$env:OLLAMA_URL = "http://${EdgeServer}:11434"
python -m pytest tests/test_classifier_llm.py::test_classifier_llm_network_ticket -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ LLM test FAILED" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ LLM test passed" -ForegroundColor Green

# Step 3: Build image
Write-Host "`n[3/5] Building Docker image..." -ForegroundColor Yellow
docker build -t twisterlab-api:llm-v1.0 -f Dockerfile.production .
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Docker build FAILED" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Docker image built" -ForegroundColor Green

# Step 4: Deploy
Write-Host "`n[4/5] Deploying to EdgeServer..." -ForegroundColor Yellow

Write-Host "  Transferring image..." -ForegroundColor Gray
docker save twisterlab-api:llm-v1.0 | ssh ${EdgeUser}@${EdgeServer} "docker load"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Image transfer FAILED" -ForegroundColor Red
    exit 1
}

Write-Host "  Copying files..." -ForegroundColor Gray
scp docker-compose.production.yml ${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/
scp -r agents ${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/
scp -r monitoring ${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/

Write-Host "  Deploying stack..." -ForegroundColor Gray
ssh ${EdgeUser}@${EdgeServer} "cd /home/${EdgeUser}/twisterlab; docker stack deploy -c docker-compose.production.yml twisterlab"

Write-Host "  ✓ Deployment complete" -ForegroundColor Green

# Step 5: Health check
Write-Host "`n[5/5] Waiting for services (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

try {
    $healthCheck = Invoke-RestMethod -Uri "http://${EdgeServer}:8000/health" -TimeoutSec 10
    Write-Host "  ✓ API is healthy" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ API not responding yet (may need more time)" -ForegroundColor Yellow
}

# Summary
$Duration = (Get-Date) - $StartTime
$Minutes = [math]::Floor($Duration.TotalMinutes)
$Seconds = [math]::Round($Duration.TotalSeconds - ($Minutes * 60))

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTime: ${Minutes}m ${Seconds}s" -ForegroundColor White
Write-Host "`nServices:" -ForegroundColor Yellow
Write-Host "  API:      http://${EdgeServer}:8000" -ForegroundColor White
Write-Host "  Grafana:  http://${EdgeServer}:3001" -ForegroundColor White
Write-Host "  Ollama:   http://${EdgeServer}:11434" -ForegroundColor White
Write-Host "`nNext: Open Grafana and import LLM dashboard`n" -ForegroundColor Cyan
