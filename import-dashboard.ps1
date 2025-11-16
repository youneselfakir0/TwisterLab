$dashboardJson = Get-Content "c:\TwisterLab\grafana-dashboard-twisterlab-fixed.json" -Raw
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
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-WebRequest -Uri "http://192.168.0.30:3000/api/dashboards/db" -Method POST -Headers $headers -Body $dashboardJson -TimeoutSec 60
    Write-Host "Dashboard imported successfully!"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error importing dashboard: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody"
    }
}
