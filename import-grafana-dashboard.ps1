# Script pour importer le dashboard TwisterLab dans Grafana
param(
    [string]$GrafanaUrl = "http://192.168.0.30:3000",
    [string]$Username = "admin",
    [string]$Password = "admin",
    [string]$DashboardFile = "grafana-dashboard-twisterlab.json"
)

Write-Host "Importation du dashboard TwisterLab dans Grafana..." -ForegroundColor Green

# Vérifier que le fichier dashboard existe
if (!(Test-Path $DashboardFile)) {
    Write-Error "Fichier dashboard non trouvé: $DashboardFile"
    exit 1
}

# Créer les credentials en base64
$Credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))

# Headers pour l'API Grafana
$Headers = @{
    "Authorization" = "Basic $Credentials"
    "Content-Type" = "application/json"
}

# Lire le contenu du dashboard
$DashboardContent = Get-Content $DashboardFile -Raw | ConvertFrom-Json

# Préparer la payload pour l'import
$ImportPayload = @{
    dashboard = $DashboardContent.dashboard
    overwrite = $true
} | ConvertTo-Json -Depth 10

# Importer le dashboard
try {
    $Response = Invoke-RestMethod -Uri "$GrafanaUrl/api/dashboards/import" -Method Post -Headers $Headers -Body $ImportPayload

    if ($Response.id) {
        Write-Host "✅ Dashboard importé avec succès!" -ForegroundColor Green
        Write-Host "📊 URL du dashboard: $GrafanaUrl/d/$($Response.uid)" -ForegroundColor Cyan
        Write-Host "🆔 ID du dashboard: $($Response.id)" -ForegroundColor Cyan
    } else {
        Write-Error "❌ Échec de l'importation du dashboard"
    }
} catch {
    Write-Error "❌ Erreur lors de l'importation: $($_.Exception.Message)"

    # Vérifier si Grafana est accessible
    try {
        $TestResponse = Invoke-WebRequest -Uri "$GrafanaUrl/api/health" -Headers $Headers -TimeoutSec 10
        Write-Host "🔍 Grafana est accessible, mais l'import a échoué" -ForegroundColor Yellow
    } catch {
        Write-Error "❌ Grafana n'est pas accessible sur $GrafanaUrl"
    }
}

Write-Host "`n📋 Instructions d'utilisation:" -ForegroundColor Yellow
Write-Host "1. Ouvrez Grafana: $GrafanaUrl" -ForegroundColor White
Write-Host "2. Connectez-vous avec admin/admin" -ForegroundColor White
Write-Host "3. Le dashboard 'TwisterLab - Complete Monitoring Dashboard' sera disponible" -ForegroundColor White
Write-Host "4. Configurez les data sources Prometheus si nécessaire" -ForegroundColor White
