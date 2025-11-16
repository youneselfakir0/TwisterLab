$grafanaPassword = $env:GRAFANA_ADMIN_PASSWORD
if (-not $grafanaPassword -and (Test-Path "/run/secrets/grafana_admin_password")) {
    $grafanaPassword = Get-Content -Path "/run/secrets/grafana_admin_password" -Raw
}
if (-not $grafanaPassword) {
    Write-Host "GRAFANA admin password not set. Set GRAFANA_ADMIN_PASSWORD or mount /run/secrets/grafana_admin_password" -ForegroundColor Red
    exit 1
}
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:$grafanaPassword"))
$headers = @{
    "Authorization" = "Basic $auth"
}

try {
    $response = Invoke-WebRequest -Uri "http://192.168.0.30:3000/api/datasources" -Headers $headers -TimeoutSec 30
    $datasources = $response.Content | ConvertFrom-Json
    Write-Host "Datasources found:"
    foreach ($ds in $datasources) {
        Write-Host "Name: $($ds.name), UID: $($ds.uid), URL: $($ds.url)"
    }
} catch {
    Write-Host "Error getting datasources: $($_.Exception.Message)"
}
