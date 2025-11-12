# Deploy Grafana Dashboard - TwisterLab Workflow

$GrafanaUrl = "http://192.168.0.30:3000"
$GrafanaUser = "admin"
$GrafanaPassword = "admin"  # Changer si mot de passe modifie

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " DEPLOIEMENT DASHBOARD GRAFANA - WORKFLOW" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Credentials
$base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${GrafanaUser}:${GrafanaPassword}"))
$headers = @{
    "Authorization" = "Basic $base64Auth"
    "Content-Type" = "application/json"
}

# Lire le dashboard
$dashboardPath = "C:\TwisterLab\monitoring\grafana\dashboards\twisterlab_workflow.json"

if (-not (Test-Path $dashboardPath)) {
    Write-Host "ERREUR: Dashboard non trouve: $dashboardPath" -ForegroundColor Red
    exit 1
}

Write-Host "Chargement dashboard depuis: $dashboardPath" -ForegroundColor Cyan
$dashboardContent = Get-Content $dashboardPath -Raw | ConvertFrom-Json

# Preparer le payload pour Grafana API
$payload = @{
    dashboard = $dashboardContent.dashboard
    overwrite = $true
    message = "TwisterLab Workflow Dashboard - Auto deploy"
} | ConvertTo-Json -Depth 20

Write-Host "Deploiement vers Grafana: $GrafanaUrl" -ForegroundColor Yellow

try {
    # Creer/Mettre a jour le dashboard
    $response = Invoke-RestMethod -Method POST `
        -Uri "$GrafanaUrl/api/dashboards/db" `
        -Headers $headers `
        -Body $payload `
        -ContentType "application/json"

    Write-Host ""
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "  Dashboard ID: $($response.id)" -ForegroundColor White
    Write-Host "  Dashboard UID: $($response.uid)" -ForegroundColor White
    Write-Host "  URL: $($response.url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Dashboard accessible a:" -ForegroundColor Cyan
    Write-Host "  $GrafanaUrl$($response.url)" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERREUR lors du deploiement:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red

    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "Details:" -ForegroundColor Yellow
        $_.ErrorDetails.Message
    }

    Write-Host ""
    Write-Host "Verifications:" -ForegroundColor Yellow
    Write-Host "  1. Grafana est accessible: curl $GrafanaUrl" -ForegroundColor Gray
    Write-Host "  2. Credentials corrects: admin/admin" -ForegroundColor Gray
    Write-Host "  3. API activee dans Grafana" -ForegroundColor Gray

    exit 1
}

Write-Host "================================================" -ForegroundColor Green
Write-Host " DASHBOARD DEPLOYE AVEC SUCCES!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
