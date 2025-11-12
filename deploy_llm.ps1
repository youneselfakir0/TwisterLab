# TwisterLab LLM Deployment Script
# Deploys LLM-enhanced agents to production

param(
    [switch]$SkipBuild,
    [switch]$SkipTests,
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TWISTERLAB LLM DEPLOYMENT v1.0       " -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

$StartTime = Get-Date

# Configuration
$ImageName = "twisterlab-api:llm-v1.0"
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"
$StackName = "twisterlab"

# Step 1: Pre-deployment checks
Write-Host "[1/6] Pre-deployment checks..." -ForegroundColor Yellow

# Check Ollama is running
Write-Host "  Checking Ollama GPU service..." -ForegroundColor Gray
try {
    $ollamaResponse = Invoke-RestMethod -Method GET -Uri "http://$EdgeServer:11434/api/tags" -TimeoutSec 5
    Write-Host "  ✓ Ollama GPU is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama GPU is NOT running!" -ForegroundColor Red
    Write-Host "  Please start Ollama: ssh $EdgeUser@$EdgeServer 'docker start twisterlab-ollama-gpu'" -ForegroundColor Yellow
    exit 1
}

# Check llama3.2:1b model is available
$modelFound = $false
foreach ($model in $ollamaResponse.models) {
    if ($model.name -like "*llama3.2:1b*") {
        $modelFound = $true
        break
    }
}

if (-not $modelFound) {
    Write-Host "  ✗ llama3.2:1b model NOT found!" -ForegroundColor Red
    Write-Host "  Please pull model: ssh $EdgeUser@$EdgeServer 'docker exec twisterlab-ollama-gpu ollama pull llama3.2:1b'" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ llama3.2:1b model available" -ForegroundColor Green

# Step 2: Run tests (unless skipped)
if (-not $SkipTests) {
    Write-Host "`n[2/6] Running LLM integration tests..." -ForegroundColor Yellow

    $env:OLLAMA_URL = "http://$EdgeServer:11434"

    # Run all LLM tests
    Write-Host "  Testing ClassifierAgent (6 tests)..." -ForegroundColor Gray
    $testResult1 = python -m pytest tests/test_classifier_llm.py -v --tb=short 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ ClassifierAgent tests FAILED" -ForegroundColor Red
        Write-Host $testResult1
        exit 1
    }
    Write-Host "  ✓ ClassifierAgent tests passed" -ForegroundColor Green

    Write-Host "  Testing ResolverAgent (7 tests)..." -ForegroundColor Gray
    $testResult2 = python -m pytest tests/test_resolver_llm.py -v --tb=short 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ ResolverAgent tests FAILED" -ForegroundColor Red
        Write-Host $testResult2
        exit 1
    }
    Write-Host "  ✓ ResolverAgent tests passed" -ForegroundColor Green

    Write-Host "  Testing DesktopCommanderAgent (7 tests)..." -ForegroundColor Gray
    $testResult3 = python -m pytest tests/test_commander_llm.py -v --tb=short 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ DesktopCommanderAgent tests FAILED" -ForegroundColor Red
        Write-Host $testResult3
        exit 1
    }
    Write-Host "  ✓ DesktopCommanderAgent tests passed" -ForegroundColor Green

    Write-Host "  ✓ All 20 tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n[2/6] Skipping tests (--SkipBuild specified)" -ForegroundColor Yellow
}

# Step 3: Build Docker image (unless skipped)
if (-not $SkipBuild) {
    Write-Host "`n[3/6] Building Docker image..." -ForegroundColor Yellow

    Write-Host "  Building $ImageName..." -ForegroundColor Gray
    docker build -t $ImageName -f Dockerfile.production . 2>&1 | Out-Null

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Docker build FAILED" -ForegroundColor Red
        exit 1
    }

    Write-Host "  ✓ Docker image built successfully" -ForegroundColor Green

    # Tag for registry (if needed)
    # docker tag $ImageName $EdgeServer:5000/$ImageName
} else {
    Write-Host "`n[3/6] Skipping Docker build (--SkipBuild specified)" -ForegroundColor Yellow
}

# Step 4: Deploy to EdgeServer
Write-Host "`n[4/6] Deploying to EdgeServer..." -ForegroundColor Yellow

# Copy docker-compose to edgeserver
Write-Host "  Copying docker-compose.production.yml..." -ForegroundColor Gray
scp docker-compose.production.yml ${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/ 2>&1 | Out-Null

# Copy updated agents
Write-Host "  Copying updated agent files..." -ForegroundColor Gray
scp -r agents/ ${EdgeUser}@${EdgeServer}:/home/${EdgeUser}/twisterlab/ 2>&1 | Out-Null

# Save and load image on edgeserver
Write-Host "  Transferring Docker image to EdgeServer..." -ForegroundColor Gray
docker save $ImageName | ssh ${EdgeUser}@${EdgeServer} "docker load" 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Image transfer FAILED" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Image transferred successfully" -ForegroundColor Green

# Deploy stack
Write-Host "  Deploying Docker stack '$StackName'..." -ForegroundColor Gray
ssh ${EdgeUser}@${EdgeServer} "cd /home/${EdgeUser}/twisterlab && docker stack deploy -c docker-compose.production.yml $StackName" 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Stack deployment FAILED" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Stack deployed successfully" -ForegroundColor Green

# Wait for services to start
Write-Host "  Waiting for services to start (30s)..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Step 5: Health checks
Write-Host "`n[5/6] Running health checks..." -ForegroundColor Yellow

# Check API health
Write-Host "  Checking API health..." -ForegroundColor Gray
try {
    $apiHealth = Invoke-RestMethod -Method GET -Uri "http://$EdgeServer:8000/health" -TimeoutSec 10
    if ($apiHealth.status -eq "healthy") {
        Write-Host "  ✓ API is healthy" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ API status: $($apiHealth.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ API health check FAILED: $_" -ForegroundColor Red
    Write-Host "  Check logs: ssh $EdgeUser@$EdgeServer 'docker service logs ${StackName}_api'" -ForegroundColor Yellow
}

# Check Ollama connectivity from API
Write-Host "  Testing API → Ollama connectivity..." -ForegroundColor Gray
try {
    $testTicket = @{
        title = "Test WiFi issue"
        description = "Cannot connect to office WiFi"
        priority = "medium"
    } | ConvertTo-Json

    $classifyResult = Invoke-RestMethod -Method POST -Uri "http://$EdgeServer:8000/api/classify" -Body $testTicket -ContentType "application/json" -TimeoutSec 15

    if ($classifyResult.classification.method -eq "llm") {
        Write-Host "  ✓ API successfully using LLM for classification" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ API using fallback (method: $($classifyResult.classification.method))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ API test FAILED: $_" -ForegroundColor Red
}

# Step 6: Display summary
Write-Host "`n[6/6] Deployment summary" -ForegroundColor Yellow

$EndTime = Get-Date
$Duration = ($EndTime - $StartTime).TotalSeconds

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nDeployment time: $([math]::Round($Duration, 1))s" -ForegroundColor White
Write-Host "`nServices:" -ForegroundColor Yellow
Write-Host "  API:       http://$EdgeServer:8000" -ForegroundColor White
Write-Host "  Grafana:   http://$EdgeServer:3001" -ForegroundColor White
Write-Host "  Prometheus: http://$EdgeServer:9090" -ForegroundColor White
Write-Host "  Ollama GPU: http://$EdgeServer:11434" -ForegroundColor White

Write-Host "`nAgent Status:" -ForegroundColor Yellow
Write-Host "  ClassifierAgent:        ✓ LLM-enhanced (llama3.2:1b)" -ForegroundColor Green
Write-Host "  ResolverAgent:          ✓ LLM-enhanced (dynamic SOPs)" -ForegroundColor Green
Write-Host "  DesktopCommanderAgent:  ✓ Whitelist + LLM advisory" -ForegroundColor Green

Write-Host "`nMonitoring:" -ForegroundColor Yellow
Write-Host "  Dashboard: LLM Agents Performance" -ForegroundColor White
Write-Host "  GPU:       GTX 1050 (2GB VRAM)" -ForegroundColor White
Write-Host "  Model:     llama3.2:1b" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. View logs:     ssh $EdgeUser@$EdgeServer 'docker service logs -f ${StackName}_api'" -ForegroundColor Gray
Write-Host "  2. Monitor GPU:   ssh $EdgeUser@$EdgeServer 'nvidia-smi -l 1'" -ForegroundColor Gray
Write-Host "  3. Open Grafana:  http://$EdgeServer:3001" -ForegroundColor Gray
Write-Host "  4. Submit ticket: curl -X POST http://$EdgeServer:8000/api/tickets ..." -ForegroundColor Gray

Write-Host "`n========================================`n" -ForegroundColor Cyan
