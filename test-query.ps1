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

$queryBody = '{
    "queries": [
        {
            "refId": "A",
            "datasource": {
                "type": "prometheus",
                "uid": "ef4615is4737kd"
            },
            "expr": "node_memory_MemTotal_bytes"
        }
    ]
}'

try {
    $response = Invoke-WebRequest -Uri "http://192.168.0.30:3000/api/ds/query" -Method POST -Headers $headers -Body $queryBody -TimeoutSec 30
    Write-Host "Query successful! Status: $($response.StatusCode)"
    Write-Host "Response length: $($response.Content.Length) characters"

    $result = $response.Content | ConvertFrom-Json
    if ($result.results -and $result.results.A -and $result.results.A.frames) {
        Write-Host "Data found in response!"
        Write-Host "Memory value: $($result.results.A.frames[0].data.values[1]) bytes"
    } else {
        Write-Host "No data frames in response"
        Write-Host "Full response: $($response.Content)"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "HTTP Status: $($_.Exception.Response.StatusCode.Value__)"
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody"
    }
}
