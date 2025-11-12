param()

$ErrorActionPreference = "Stop"
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TWISTERLAB LLM DEPLOYMENT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Check Ollama
Write-Host ""
Write-Host "[1/5] Checking Ollama..." -ForegroundColor Yellow
$ollamaUrl = "http://$EdgeServer`:11434/api/tags"
try {
    Invoke-RestMethod -Uri $ollamaUrl -TimeoutSec 5 | Out-Null
    Write-Host "OK - Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR - Ollama not accessible" -ForegroundColor Red
    exit 1
}

# Step 2: Test
Write-Host ""
Write-Host "[2/5] Running LLM test..." -ForegroundColor Yellow
$env:OLLAMA_URL = "http://$EdgeServer`:11434"
python -m pytest tests/test_classifier_llm.py::test_classifier_llm_network_ticket -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - Test failed" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Test passed" -ForegroundColor Green

# Step 3: Build
Write-Host ""
Write-Host "[3/5] Building Docker image..." -ForegroundColor Yellow
docker build -t twisterlab-api:llm-v1.0 -f Dockerfile.production .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Image built" -ForegroundColor Green

# Step 4: Deploy
Write-Host ""
Write-Host "[4/5] Deploying to EdgeServer..." -ForegroundColor Yellow

Write-Host "Transferring image..."
docker save twisterlab-api:llm-v1.0 | ssh "$EdgeUser@$EdgeServer" "docker load"

Write-Host "Copying files..."
$remotePath = "${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/"
scp docker-compose.production.yml $remotePath
scp -r agents $remotePath
scp -r monitoring $remotePath

Write-Host "Deploying stack..."
ssh "$EdgeUser@$EdgeServer" "cd /home/$EdgeUser/twisterlab && docker stack deploy -c docker-compose.production.yml twisterlab"

Write-Host "OK - Deployed" -ForegroundColor Green

# Step 5: Health
Write-Host ""
Write-Host "[5/5] Health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

$apiUrl = "http://$EdgeServer`:8000/health"
try {
    Invoke-RestMethod -Uri $apiUrl -TimeoutSec 10 | Out-Null
    Write-Host "OK - API is healthy" -ForegroundColor Green
} catch {
    Write-Host "WARNING - API not ready yet" -ForegroundColor Yellow
}

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:"
Write-Host "  API:     http://$EdgeServer`:8000"
Write-Host "  Grafana: http://$EdgeServer`:3001"
Write-Host "  Ollama:  http://$EdgeServer`:11434"
Write-Host ""
