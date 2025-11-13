# Script pour configurer Prometheus comme data source dans Grafana
param(
    [string]$GrafanaUrl = "http://192.168.0.30:3000",
    [string]$Username = "admin",
    [string]$Password = "admin",
    [string]$PrometheusUrl = "http://192.168.0.30:9090"
)

Write-Host "Configuration de Prometheus comme data source dans Grafana..." -ForegroundColor Green

# Créer les credentials en base64
$Credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))

# Headers pour l'API Grafana
$Headers = @{
    "Authorization" = "Basic $Credentials"
    "Content-Type" = "application/json"
}

# Configuration de la data source Prometheus
$DataSourceConfig = @{
    name = "Prometheus"
    type = "prometheus"
    url = $PrometheusUrl
    access = "proxy"
    isDefault = $true
} | ConvertTo-Json

# Créer la data source
try {
    $Response = Invoke-RestMethod -Uri "$GrafanaUrl/api/datasources" -Method Post -Headers $Headers -Body $DataSourceConfig

    if ($Response.datasource.id) {
        Write-Host "✅ Data source Prometheus configurée avec succès!" -ForegroundColor Green
        Write-Host "🆔 ID de la data source: $($Response.datasource.id)" -ForegroundColor Cyan
    } else {
        Write-Warning "⚠️ La data source pourrait déjà exister"
    }
} catch {
    Write-Warning "⚠️ Impossible de configurer la data source Prometheus: $($_.Exception.Message)"
    Write-Host "ℹ️ Vous devrez la configurer manuellement dans Grafana" -ForegroundColor Yellow
}