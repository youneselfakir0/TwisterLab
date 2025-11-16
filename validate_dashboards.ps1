#Requires -RunAsAdministrator

Write-Host "🎯 VALIDATION FINALE - TWISTERLAB DASHBOARDS" -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Blue
Write-Host ""

$nodeIP = "edgeserver.twisterlab.local"
$dashboards = @(
    @{Name="Traefik Dashboard"; Url="http://$nodeIP`:8084"; ExpectedCode=200},
    @{Name="OpenWebUI"; Url="http://$nodeIP`:8083"; ExpectedCode=200},
    @{Name="Grafana"; Url="http://$nodeIP`:3000"; ExpectedCode=200},
    @{Name="Prometheus"; Url="http://$nodeIP`:9090"; ExpectedCode=200}
)

$allTestsPassed = $true
$results = @()

foreach ($dashboard in $dashboards) {
    Write-Host "Testing $($dashboard.Name)..." -ForegroundColor Blue -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $dashboard.Url -TimeoutSec 15 -ErrorAction Stop
        if ($response.StatusCode -eq $dashboard.ExpectedCode) {
            Write-Host " ✅ HTTP $($response.StatusCode)" -ForegroundColor Green
            $results += @{Name=$dashboard.Name; Status="SUCCESS"; Code=$response.StatusCode}
        } else {
            Write-Host " ⚠️ HTTP $($response.StatusCode) (expected $($dashboard.ExpectedCode))" -ForegroundColor Yellow
            $results += @{Name=$dashboard.Name; Status="WARNING"; Code=$response.StatusCode}
        }
    } catch {
        Write-Host " ❌ $($_.Exception.Message)" -ForegroundColor Red
        $results += @{Name=$dashboard.Name; Status="FAILED"; Error=$_.Exception.Message}
        $allTestsPassed = $false
    }
}

Write-Host "`n📊 RÉSULTATS DE TEST" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

foreach ($result in $results) {
    $statusColor = switch ($result.Status) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "FAILED" { "Red" }
    }
    Write-Host "$($result.Name): $($result.Status)" -ForegroundColor $statusColor
    if ($result.Code) { Write-Host "  Code: $($result.Code)" -ForegroundColor White }
    if ($result.Error) { Write-Host "  Error: $($result.Error)" -ForegroundColor Red }
}

Write-Host "`n🌐 URLS D'ACCÈS" -ForegroundColor Blue
Write-Host "=" * 30 -ForegroundColor Blue

if ($allTestsPassed) {
    Write-Host "✅ TOUS LES DASHBOARDS SONT ACCESSIBLES !" -ForegroundColor Green
    Write-Host ""

    Write-Host "📋 URLs des services :" -ForegroundColor White
    Write-Host "  • Traefik Dashboard: http://$nodeIP`:8084" -ForegroundColor Cyan
    Write-Host "  • OpenWebUI: http://$nodeIP`:8083" -ForegroundColor Cyan
    Write-Host "  • Grafana: http://$nodeIP`:3000 (admin account via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD)" -ForegroundColor Cyan
    Write-Host "  • Prometheus: http://$nodeIP`:9090" -ForegroundColor Cyan

    Write-Host "`n🔧 Configuration DNS recommandée :" -ForegroundColor Yellow
    Write-Host "  Ajouter dans C:\Windows\System32\drivers\etc\hosts :" -ForegroundColor White
    Write-Host "  $nodeIP traefik.twisterlab.local" -ForegroundColor Gray
    Write-Host "  $nodeIP webui.twisterlab.local" -ForegroundColor Gray
    Write-Host "  $nodeIP grafana.twisterlab.local" -ForegroundColor Gray
    Write-Host "  $nodeIP prometheus.twisterlab.local" -ForegroundColor Gray

    Write-Host "`n🚀 PROCHAINES ÉTAPES :" -ForegroundColor Green
    Write-Host "  1. Tester les agents autonomes via l'API" -ForegroundColor White
    Write-Host "  2. Configurer les modèles Ollama" -ForegroundColor White
    Write-Host "  3. Déployer en production complète" -ForegroundColor White

} else {
    Write-Host "❌ DES DASHBOARDS NÉCESSITENT UNE ATTENTION" -ForegroundColor Red
    Write-Host "`n🔍 Debugging :" -ForegroundColor Yellow
    Write-Host "  • Vérifier les logs: docker service logs [service_name]" -ForegroundColor White
    Write-Host "  • Vérifier les ports: docker service ls" -ForegroundColor White
    Write-Host "  • Redémarrer les services si nécessaire" -ForegroundColor White
}
}

Write-Host "`n✨ TRAVAIL TERMINÉ - $(Get-Date)" -ForegroundColor Green
