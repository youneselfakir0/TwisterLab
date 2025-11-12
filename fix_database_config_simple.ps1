#!/usr/bin/env pwsh
# Fix database config - Version simplifiée

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FIX DATABASE CONFIG" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SERVER = "twister@192.168.0.30"

# Étape 1: Vérifier état
Write-Host "[1/5] Verification..." -ForegroundColor Yellow
ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
Write-Host ""

# Étape 2: Backup
Write-Host "[2/5] Backup..." -ForegroundColor Yellow
ssh $SERVER "cp /home/twister/TwisterLab/agents/database/config.py /home/twister/TwisterLab/agents/database/config.py.backup"
Write-Host "Backup cree" -ForegroundColor Green
Write-Host ""

# Étape 3: Modifier le fichier
Write-Host "[3/5] Modification..." -ForegroundColor Yellow
ssh $SERVER "sed -i 's/postgresql+psycopg2/postgresql+asyncpg/g' /home/twister/TwisterLab/agents/database/config.py"

# Vérifier
$check = ssh $SERVER "grep 'postgresql+asyncpg' /home/twister/TwisterLab/agents/database/config.py"
if ($check) {
    Write-Host "Modification OK: asyncpg detecte" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Erreur: asyncpg non detecte" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Étape 4: Rebuild
Write-Host "[4/5] Rebuild image - 5 minutes" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$image = "twisterlab-api:asyncpg-$timestamp"
Write-Host "Image: $image" -ForegroundColor Gray
Write-Host ""

ssh $SERVER "cd /home/twister/TwisterLab; docker build -f Dockerfile.production -t $image ."

# Vérifier image
$imageExists = ssh $SERVER "docker images $image --format '{{.Repository}}:{{.Tag}}'"
if ($imageExists -eq $image) {
    Write-Host ""
    Write-Host "Image creee: $image" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Image non trouvee" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Étape 5: Deploy
Write-Host "[5/5] Deploiement..." -ForegroundColor Yellow
Write-Host ""
ssh $SERVER "docker service update --image $image twisterlab_api"

Write-Host ""
Write-Host "Attente 30s..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Tests
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test 1: Health check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://192.168.0.30:8000/health" -TimeoutSec 10
    Write-Host "OK: $($health | ConvertTo-Json -Compress)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Test 2: MonitoringAgent..." -ForegroundColor Cyan
try {
    $body = @{ operation = "health_check" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15

    if ($result.result.metrics.cpu_usage -eq "23%") {
        Write-Host "MOCK DATA detecte" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "REAL DATA: $($result | ConvertTo-Json -Depth 2)" -ForegroundColor Green
        Write-Host ""
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TERMINE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Image: $image" -ForegroundColor Cyan
Write-Host "Backup: /home/twister/TwisterLab/agents/database/config.py.backup" -ForegroundColor Cyan
Write-Host ""
