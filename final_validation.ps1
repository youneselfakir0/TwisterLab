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

Write-Host "Testing all dashboards..." -ForegroundColor Blue
Write-Host ""

foreach ($dashboard in $dashboards) {
    Write-Host "$($dashboard.Name): " -NoNewline -ForegroundColor White

    try {
        $response = Invoke-WebRequest -Uri $dashboard.Url -TimeoutSec 15 -ErrorAction Stop
        if ($response.StatusCode -eq $dashboard.ExpectedCode) {
            Write-Host "✅ HTTP $($response.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "⚠️ HTTP $($response.StatusCode)" -ForegroundColor Yellow
            $allTestsPassed = $false
        }
    } catch {
        Write-Host "❌ FAILED" -ForegroundColor Red
        $allTestsPassed = $false
    }
}

Write-Host ""
if ($allTestsPassed) {
    Write-Host "✅ TOUS LES DASHBOARDS SONT ACCESSIBLES !" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 URLs d'accès :" -ForegroundColor White
    Write-Host "  • Traefik Dashboard: http://$nodeIP`:8084" -ForegroundColor Cyan
    Write-Host "  • OpenWebUI: http://$nodeIP`:8083" -ForegroundColor Cyan
    Write-Host "  • Grafana: http://$nodeIP`:3000 (admin account via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD)" -ForegroundColor Cyan
    Write-Host "  • Prometheus: http://$nodeIP`:9090" -ForegroundColor Cyan
} else {
    Write-Host "❌ Certains dashboards nécessitent une attention" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ Validation terminée - $(Get-Date)" -ForegroundColor Green
