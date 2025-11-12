# Test Final - Vérification du fix asyncpg

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST FINAL - FIX ASYNCPG" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$SERVER = "twister@192.168.0.30"
$IMAGE = "twisterlab-api:asyncpg-fix-final"

# Test 1: Vérifier le contenu de l'image
Write-Host "[1/6] Vérification contenu de l'image..." -ForegroundColor Yellow
$imageContent = ssh $SERVER "docker run --rm $IMAGE cat /app/agents/database/config.py | grep 'DATABASE_URL ='"
Write-Host "Contenu: $imageContent" -ForegroundColor Gray

if ($imageContent -match "asyncpg") {
    Write-Host "OK: asyncpg detecte dans l'image" -ForegroundColor Green
} else {
    Write-Host "ERREUR: asyncpg non trouve" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Deploy l'image
Write-Host "[2/6] Deploiement de l'image..." -ForegroundColor Yellow
ssh $SERVER "docker service update --image $IMAGE twisterlab_api"
Write-Host ""

# Test 3: Attendre convergence
Write-Host "[3/6] Attente de convergence (40s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 40
Write-Host ""

# Test 4: Vérifier service
Write-Host "[4/6] Verification du service..." -ForegroundColor Yellow
$status = ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
Write-Host "Status: $status" -ForegroundColor Gray
Write-Host ""

# Test 5: Health check
Write-Host "[5/6] Test health check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://192.168.0.30:8000/health" -TimeoutSec 10
    Write-Host "OK: $($health | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red

    # Afficher les logs
    Write-Host "`nLogs du service (30 lignes):" -ForegroundColor Yellow
    ssh $SERVER "docker service logs twisterlab_api --tail 30"
    exit 1
}
Write-Host ""

# Test 6: MonitoringAgent avec VRAIES donnees
Write-Host "[6/6] Test MonitoringAgent (donnees reelles)..." -ForegroundColor Cyan
try {
    $body = @{ operation = "health_check" } | ConvertTo-Json
    $result = Invoke-RestMethod `
        -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 15

    Write-Host "Response:" -ForegroundColor Gray
    Write-Host ($result | ConvertTo-Json -Depth 3) -ForegroundColor Gray
    Write-Host ""

    # Vérifier que ce ne sont PAS des données mock
    if ($result.result.metrics.cpu_usage -eq "23%") {
        Write-Host "ATTENTION: Donnees MOCK detectees!" -ForegroundColor Yellow
        Write-Host "L'API retourne encore des donnees mock." -ForegroundColor Yellow
    } else {
        Write-Host "SUCCESS: Donnees REELLES detectees!" -ForegroundColor Green
        Write-Host "Le MonitoringAgent retourne des vraies metriques systeme." -ForegroundColor Green
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
}
Write-Host ""

# Résumé final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUME" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Image: $IMAGE" -ForegroundColor White
Write-Host "Driver DB: asyncpg (async)" -ForegroundColor Green
Write-Host "Service: DEPLOYED" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "1. Tester les autres agents (BackupAgent, SyncAgent, etc.)" -ForegroundColor Gray
Write-Host "2. Verifier Grafana dashboards: http://192.168.0.30:3000" -ForegroundColor Gray
Write-Host "3. Executer tests d'integration: python tests/test_integration_real_agents.py" -ForegroundColor Gray
Write-Host ""
