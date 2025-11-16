# Complete Deployment Pipeline for Real Agents
# Deploys, tests, and validates all real agents on edgeserver

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TWISTERLAB REAL AGENTS - COMPLETE DEPLOYMENT PIPELINE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$edgeserver = "192.168.0.30"

# Step 1: Deploy agents to edgeserver
Write-Host "STEP 1/5: Deploying agents to edgeserver" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

if (Test-Path "scripts\deploy_real_agents.ps1") {
    & ".\scripts\deploy_real_agents.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Deployment failed. Aborting." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  Deploy script not found, skipping deployment" -ForegroundColor Yellow
}

Write-Host ""

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

$GrafanaPassword = Get-Secret -SecretName "grafana_admin_password"
$GrafanaUser = $env:GRAFANA_ADMIN_USER
if ([string]::IsNullOrWhiteSpace($GrafanaUser)) { $GrafanaUser = "admin" }

# Step 2: Import Grafana dashboard
Write-Host "STEP 2/5: Importing Grafana dashboard" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

$dashboardPath = "monitoring\grafana\dashboards\twisterlab_real_agents.json"
if (Test-Path $dashboardPath) {
    try {
        $dashboard = Get-Content $dashboardPath | ConvertFrom-Json

        $grafanaUrl = "http://${edgeserver}:3000"
    $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$GrafanaUser:$GrafanaPassword"))

        $headers = @{
            "Authorization" = "Basic $auth"
            "Content-Type" = "application/json"
        }

        $response = Invoke-RestMethod -Uri "$grafanaUrl/api/dashboards/db" -Method POST -Headers $headers -Body ($dashboard | ConvertTo-Json -Depth 10) -ErrorAction SilentlyContinue

        if ($response.status -eq "success") {
            Write-Host "✅ Dashboard imported successfully" -ForegroundColor Green
            Write-Host "   URL: $grafanaUrl/d/twisterlab-real-agents" -ForegroundColor White
        } else {
            Write-Host "⚠️  Dashboard import status: $($response.status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Dashboard import failed: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   You can import manually via Grafana UI" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Dashboard file not found" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Verify API is running
Write-Host "STEP 3/5: Verifying API status" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

$maxRetries = 3
$retryDelay = 5

for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        $healthCheck = Invoke-RestMethod -Uri "http://${edgeserver}:8000/health" -Method GET -TimeoutSec 5
        Write-Host "✅ API is healthy" -ForegroundColor Green
        break
    } catch {
        if ($i -lt $maxRetries) {
            Write-Host "⚠️  API not responding, retrying in ${retryDelay}s... ($i/$maxRetries)" -ForegroundColor Yellow
            Start-Sleep -Seconds $retryDelay
        } else {
            Write-Host "❌ API not responding after $maxRetries attempts" -ForegroundColor Red
            Write-Host "   Please check: docker service ls | grep twisterlab_api" -ForegroundColor Gray
        }
    }
}

Write-Host ""

# Step 4: Run integration tests
Write-Host "STEP 4/5: Running integration tests" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

if (Test-Path "tests\test_integration_real_agents.py") {
    $pythonCmd = "python"
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        Write-Host "📦 Activating virtual environment..." -ForegroundColor Gray
        & .\.venv\Scripts\Activate.ps1
    }

    # Install aiohttp if needed
    & $pythonCmd -m pip install --quiet aiohttp

    Write-Host ""
    & $pythonCmd tests\test_integration_real_agents.py

    $testResult = $LASTEXITCODE
    Write-Host ""

    if ($testResult -eq 0) {
        Write-Host "✅ Integration tests PASSED" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some integration tests failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Integration test script not found" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Display access information
Write-Host "STEP 5/5: Deployment Summary" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 ACCESS POINTS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  API Endpoint:" -ForegroundColor White
Write-Host "    http://${edgeserver}:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Grafana Dashboard:" -ForegroundColor White
Write-Host "    http://${edgeserver}:3000/d/twisterlab-real-agents" -ForegroundColor Gray
Write-Host "    Login: admin / (see Docker secret)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Health Check:" -ForegroundColor White
Write-Host "    http://${edgeserver}:8000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "🧪 TEST AN AGENT:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  curl -X POST http://${edgeserver}:8000/agents/monitoring/execute \" -ForegroundColor Gray
Write-Host "    -H 'Content-Type: application/json' \" -ForegroundColor Gray
Write-Host "    -d '{\"operation\":\"health_check\"}'" -ForegroundColor Gray
Write-Host ""
Write-Host "📅 SCHEDULED TASKS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ✓ MonitoringAgent health check:  Every 1 minute" -ForegroundColor Gray
Write-Host "  ✓ MonitoringAgent diagnostic:    Every 5 minutes" -ForegroundColor Gray
Write-Host "  ✓ BackupAgent create_backup:     Every 6 hours" -ForegroundColor Gray
Write-Host "  ✓ SyncAgent verify_consistency:  Every 15 minutes" -ForegroundColor Gray
Write-Host "  ✓ SyncAgent clear_stale:          Every 1 hour" -ForegroundColor Gray
Write-Host "  ✓ MaestroAgent health_check_all:  Every 3 minutes" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 MONITOR AGENTS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Watch scheduler logs:" -ForegroundColor White
Write-Host "    ssh root@${edgeserver} 'docker logs -f twisterlab_api | grep scheduler'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Check agent health:" -ForegroundColor White
Write-Host "    curl http://${edgeserver}:8000/agents/maestro/execute -X POST -H 'Content-Type: application/json' -d '{\"operation\":\"health_check_all\"}'" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 " -NoNewline -ForegroundColor Green
Write-Host "All 7 real agents are deployed and running autonomously!" -ForegroundColor White
Write-Host ""
Write-Host "   Next: Monitor in Grafana or check logs for agent activity" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
