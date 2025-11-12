#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Fix database/config.py pour utiliser asyncpg au lieu de psycopg2

.DESCRIPTION
    Ce script corrige le problème d'async driver qui empêche le démarrage du service.
    Il remplace psycopg2 par asyncpg dans la DATABASE_URL.

.NOTES
    Durée estimée: 15-20 minutes
    Prérequis: SSH access à edgeserver
#>

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 FIX DATABASE CONFIG - ASYNC DRIVER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SERVER = "twister@192.168.0.30"
$PROJECT_DIR = "/home/twister/TwisterLab"
$CONFIG_FILE = "$PROJECT_DIR/agents/database/config.py"

# Étape 1: Vérifier l'état actuel
Write-Host "[1/6] Vérification de l'état actuel..." -ForegroundColor Yellow
$currentStatus = ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
Write-Host "Status actuel: $currentStatus"
Write-Host ""

# Étape 2: Backup du fichier config
Write-Host "[2/6] Backup du fichier config..." -ForegroundColor Yellow
ssh $SERVER "cp $CONFIG_FILE ${CONFIG_FILE}.backup"
Write-Host "✅ Backup créé: ${CONFIG_FILE}.backup"
Write-Host ""

# Étape 3: Modifier database/config.py
Write-Host "[3/6] Modification de database/config.py..." -ForegroundColor Yellow
$sedCommand = "sed -i 's/postgresql+psycopg2/postgresql+asyncpg/g' $CONFIG_FILE"
ssh $SERVER $sedCommand

# Vérifier la modification
$verification = ssh $SERVER "grep 'postgresql+asyncpg' $CONFIG_FILE"
if ($verification) {
    Write-Host "✅ DATABASE_URL modifié pour utiliser asyncpg" -ForegroundColor Green
    Write-Host "   $verification"
} else {
    Write-Host "❌ Erreur: Modification non détectée" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Étape 4: Rebuild l'image Docker
Write-Host "[4/6] Rebuild de l'image Docker..." -ForegroundColor Yellow
Write-Host "   Durée estimée: 5 minutes"
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$imageName = "twisterlab-api:production-asyncpg-$timestamp"

$buildCommand = @"
cd $PROJECT_DIR && \
docker build \
  -f Dockerfile.production \
  -t $imageName \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  .
"@

ssh $SERVER $buildCommand

# Vérifier que l'image existe
$imageCheck = ssh $SERVER "docker images $imageName --format '{{.Repository}}:{{.Tag}}'"
if ($imageCheck -eq $imageName) {
    Write-Host "✅ Image créée: $imageName" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur: Image non trouvée" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Étape 5: Déployer l'image
Write-Host "[5/6] Déploiement sur Docker Swarm..." -ForegroundColor Yellow
ssh $SERVER "docker service update --image $imageName twisterlab_api"

Write-Host "Attente de la convergence (30 secondes)..."
Start-Sleep -Seconds 30

# Vérifier le statut
$serviceStatus = ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
Write-Host "Statut du service: $serviceStatus"
Write-Host ""

# Étape 6: Tests de validation
Write-Host "[6/6] Tests de validation..." -ForegroundColor Yellow
Write-Host ""

# Test 1: Health check
Write-Host "Test 1: Health check..." -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "http://192.168.0.30:8000/health" -TimeoutSec 10
    Write-Host "✅ Health check OK" -ForegroundColor Green
    Write-Host "   Response: $($healthResponse | ConvertTo-Json -Compress)"
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Agents list
Write-Host "Test 2: Liste des agents..." -ForegroundColor Cyan
try {
    $agentsResponse = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents" -TimeoutSec 10
    Write-Host "✅ Agents list OK" -ForegroundColor Green
    Write-Host "   Nombre d'agents: $($agentsResponse.agents.Count)"
} catch {
    Write-Host "❌ Agents list failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: MonitoringAgent (données réelles)
Write-Host "Test 3: MonitoringAgent (données réelles)..." -ForegroundColor Cyan
try {
    $body = @{ operation = "health_check" } | ConvertTo-Json
    $monitoringResponse = Invoke-RestMethod `
        -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 15

    # Vérifier que ce n'est PAS des données mock
    $cpuUsage = $monitoringResponse.result.metrics.cpu_usage
    if ($cpuUsage -eq "23%") {
        Write-Host "⚠️  ATTENTION: Données MOCK détectées!" -ForegroundColor Yellow
        Write-Host "   CPU: $cpuUsage (devrait être dynamique)"
    } else {
        Write-Host "✅ Données RÉELLES détectées!" -ForegroundColor Green
        Write-Host "   $($monitoringResponse | ConvertTo-Json -Depth 3)"
    }
} catch {
    Write-Host "❌ MonitoringAgent failed: $_" -ForegroundColor Red
}
Write-Host ""

# Résumé final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ FIX TERMINÉ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Image déployée: $imageName" -ForegroundColor Cyan
Write-Host "Backup config: ${CONFIG_FILE}.backup" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vérifiez les logs avec:" -ForegroundColor Yellow
Write-Host "   ssh $SERVER 'docker service logs twisterlab_api --tail 50'" -ForegroundColor Gray
Write-Host ""
Write-Host "Rollback si problème:" -ForegroundColor Yellow
Write-Host "   ssh $SERVER 'docker service update --rollback twisterlab_api'" -ForegroundColor Gray
Write-Host "   ssh $SERVER 'cp ${CONFIG_FILE}.backup $CONFIG_FILE'" -ForegroundColor Gray
Write-Host ""
