# Script principal pour deployer le monitoring TwisterLab
param(
    [string]$GrafanaUrl = "$env:GRAFANA_URL",
    [string]$Username = "$env:GRAFANA_ADMIN_USER",
    [string]$PrometheusUrl = "http://192.168.0.30:9090"
)

# Function to read secret from Docker secret file or environment variable
function Get-Secret {
    param(
        [string]$SecretName,
        [string]$DefaultValue = $null
    )
    $secretPath = "/run/secrets/$SecretName"
    if (Test-Path $secretPath) {
        return (Get-Content $secretPath).Trim()
    }
    $envValue = Get-Item ENV:$SecretName -ErrorAction SilentlyContinue
    if ($envValue) {
        return $envValue.Value
    }
    if ($DefaultValue) {
        return $DefaultValue
    }
    throw "Secret '$SecretName' not found in Docker secrets or environment variables."
}

$Password = Get-Secret -SecretName "grafana_admin_password"

Write-Host ">>> Deploiement du systeme de monitoring TwisterLab" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Etape 1: Verifier la connectivite
Write-Host "`n>>> Etape 1: Verification de la connectivite..." -ForegroundColor Yellow

$GrafanaTest = Test-NetConnection -ComputerName 192.168.0.30 -Port 3000
if ($GrafanaTest.TcpTestSucceeded) {
    Write-Host "OK Grafana accessible sur le port 3000" -ForegroundColor Green
} else {
    Write-Error "ERREUR Grafana n'est pas accessible sur le port 3000"
    exit 1
}

# Etape 2: Configuration de la data source Prometheus
Write-Host "`n>>> Etape 2: Configuration de Prometheus..." -ForegroundColor Yellow

$Credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
$Headers = @{
    "Authorization" = "Basic $Credentials"
    "Content-Type" = "application/json"
}

$DataSourceConfig = @{
    name = "Prometheus"
    type = "prometheus"
    url = $PrometheusUrl
    access = "proxy"
    isDefault = $true
} | ConvertTo-Json

try {
    $Response = Invoke-RestMethod -Uri "$GrafanaUrl/api/datasources" -Method Post -Headers $Headers -Body $DataSourceConfig
    Write-Host "OK Data source Prometheus configuree" -ForegroundColor Green
} catch {
    Write-Host "WARNING Data source Prometheus deja configuree ou erreur: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Etape 3: Import du dashboard
Write-Host "`n>>> Etape 3: Import du dashboard TwisterLab..." -ForegroundColor Yellow

if (!(Test-Path "grafana-dashboard-twisterlab.json")) {
    Write-Error "ERREUR Fichier dashboard non trouve: grafana-dashboard-twisterlab.json"
    exit 1
}

$DashboardContent = Get-Content "grafana-dashboard-twisterlab.json" -Raw | ConvertFrom-Json
$ImportPayload = @{
    dashboard = $DashboardContent.dashboard
    overwrite = $true
} | ConvertTo-Json -Depth 10

try {
    $Response = Invoke-RestMethod -Uri "$GrafanaUrl/api/dashboards/import" -Method Post -Headers $Headers -Body $ImportPayload
    Write-Host "OK Dashboard importe avec succes!" -ForegroundColor Green
    Write-Host "URL: $GrafanaUrl/d/$($Response.uid)" -ForegroundColor Cyan
} catch {
    Write-Error "ERREUR Echec de l'import du dashboard: $($_.Exception.Message)"
    exit 1
}

# Etape 4: Instructions finales
Write-Host "`nSUCCESS Deploiement termine avec succes!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "`nProchaines etapes:" -ForegroundColor Yellow
Write-Host "1. Ouvrez Grafana: $GrafanaUrl" -ForegroundColor White
Write-Host "2. Connectez-vous avec le compte admin Grafana (configuré via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD ou Docker secret)" -ForegroundColor White
Write-Host "3. Accedez au dashboard 'TwisterLab - Complete Monitoring Dashboard'" -ForegroundColor White
Write-Host "4. Configurez des alertes si necessaire" -ForegroundColor White

Write-Host "`nMetriques monitorees:" -ForegroundColor Cyan
Write-Host "- Utilisation CPU/RAM/Disque" -ForegroundColor White
Write-Host "- Sante des services Docker" -ForegroundColor White
Write-Host "- Activite des agents autonomes" -ForegroundColor White
Write-Host "- Metriques PostgreSQL" -ForegroundColor White
Write-Host "- Performance Redis (quand disponible)" -ForegroundColor White
Write-Host "- Metriques API et HTTP" -ForegroundColor White
Write-Host "- Utilisation Ollama/LLM" -ForegroundColor White
Write-Host "- Alertes et incidents" -ForegroundColor White

Write-Host "`nNote: Certaines metriques necessitent Prometheus et des exporters configures" -ForegroundColor Yellow
