# ============================================================================
# Script d'import des dashboards Grafana TwisterLab
# ============================================================================

$GRAFANA_URL = "http://192.168.0.30:3000"
$GRAFANA_USER = "admin"
$GRAFANA_PASS = "admin"

# Créer l'header d'authentification
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${GRAFANA_USER}:${GRAFANA_PASS}"))
$headers = @{
    Authorization = "Basic $base64AuthInfo"
    "Content-Type" = "application/json"
}

Write-Host "`n[1] Configuration de la datasource Prometheus..." -ForegroundColor Cyan

# Créer la datasource Prometheus
$datasource = @{
    name = "Prometheus"
    type = "prometheus"
    url = "http://prometheus:9090"
    access = "proxy"
    isDefault = $true
    jsonData = @{
        timeInterval = "15s"
        queryTimeout = "60s"
        httpMethod = "POST"
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$GRAFANA_URL/api/datasources" -Method Post -Headers $headers -Body $datasource
    Write-Host "    [OK] Datasource Prometheus creee: $($response.name)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "    [OK] Datasource Prometheus deja existante" -ForegroundColor Yellow
    } else {
        Write-Host "    [X] Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n[2] Import des dashboards TwisterLab..." -ForegroundColor Cyan

# Liste des dashboards à importer
$dashboards = @(
    "monitoring\grafana\provisioning\dashboards\twisterlab-overview.json",
    "monitoring\grafana\provisioning\dashboards\twisterlab-system-overview.json",
    "monitoring\grafana\provisioning\dashboards\twisterlab-backup-monitoring.json"
)

foreach ($dashboardPath in $dashboards) {
    $dashboardName = Split-Path $dashboardPath -Leaf
    
    Write-Host "    Importing $dashboardName..." -ForegroundColor White
    
    try {
        # Lire le contenu du dashboard
        $dashboardContent = Get-Content $dashboardPath -Raw | ConvertFrom-Json
        
        # Si le JSON contient déjà un objet dashboard, l'utiliser tel quel
        # Sinon, l'encapsuler
        if ($dashboardContent.dashboard) {
            $payload = $dashboardContent | ConvertTo-Json -Depth 100
        } else {
            $payload = @{
                dashboard = $dashboardContent
                overwrite = $true
                message = "Imported via PowerShell script"
            } | ConvertTo-Json -Depth 100
        }
        
        # Importer le dashboard
        $response = Invoke-RestMethod -Uri "$GRAFANA_URL/api/dashboards/db" -Method Post -Headers $headers -Body $payload
        Write-Host "    [OK] $dashboardName importe - UID: $($response.uid)" -ForegroundColor Green
        
    } catch {
        Write-Host "    [X] Erreur lors de l'import: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n[3] Verification des dashboards..." -ForegroundColor Cyan

try {
    $dashboards = Invoke-RestMethod -Uri "$GRAFANA_URL/api/search?type=dash-db" -Headers $headers
    Write-Host "    [OK] $($dashboards.Count) dashboard(s) trouve(s):" -ForegroundColor Green
    foreach ($dash in $dashboards) {
        Write-Host "        - $($dash.title) (UID: $($dash.uid))" -ForegroundColor White
    }
} catch {
    Write-Host "    [X] Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n[4] URLs des dashboards:" -ForegroundColor Cyan
Write-Host "    Grafana: http://192.168.0.30:3000" -ForegroundColor White
Write-Host "    Login: admin / admin" -ForegroundColor White

Write-Host "`n[OK] Import termine!`n" -ForegroundColor Green
