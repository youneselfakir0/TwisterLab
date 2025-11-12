#Requires -RunAsAdministrator

Write-Host "🔧 Redéploiement WebUI avec authentification désactivée..." -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Blue
Write-Host ""

# 1. Supprimer le service actuel
Write-Host "🛑 Suppression du service WebUI actuel..." -ForegroundColor Yellow
docker service rm twisterlab_prod_webui 2>$null
Start-Sleep -Seconds 5

# 2. Redéployer la stack complète pour appliquer les changements
Write-Host "🚀 Redéploiement de la stack production..." -ForegroundColor Blue
docker stack deploy -c docker-compose.production.yml twisterlab_prod
Start-Sleep -Seconds 15

# 3. Vérifier le statut du service
Write-Host "🔍 Vérification du statut WebUI..." -ForegroundColor Blue
$webuiStatus = docker service ps twisterlab_prod_webui --format "{{.CurrentState}}" | Select-Object -First 1
Write-Host "Statut WebUI: $webuiStatus" -ForegroundColor $(if ($webuiStatus -match "Running") { "Green" } else { "Red" })

# 4. Tester l'accès
Write-Host "🧪 Test d'accès à WebUI..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://edgeserver.twisterlab.local:8083" -TimeoutSec 15 -ErrorAction Stop
    Write-Host "✅ WebUI accessible: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "🎉 Authentification désactivée - accès direct disponible !" -ForegroundColor Green
} catch {
    Write-Host "❌ WebUI non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🌐 URL d'accès:" -ForegroundColor Blue
Write-Host "  WebUI: http://edgeserver.twisterlab.local:8083" -ForegroundColor Cyan
Write-Host "  (Aucune authentification requise)" -ForegroundColor Green

Write-Host ""
Write-Host "✨ Redéploiement terminé - $(Get-Date)" -ForegroundColor Green
