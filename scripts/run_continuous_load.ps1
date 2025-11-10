# TwisterLab Continuous Load Generator
# Runs in background to continuously generate realistic agent metrics

param(
    [int]$DurationMinutes = 30,
    [int]$OperationsPerMinute = 10,
    [switch]$EnableMetricsCheck
)

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🚀 TWISTERLAB CONTINUOUS LOAD GENERATOR" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "`n📊 Configuration:" -ForegroundColor Yellow
Write-Host "   Duration: $DurationMinutes minutes" -ForegroundColor White
Write-Host "   Rate: $OperationsPerMinute ops/min (1 every $([Math]::Round(60/$OperationsPerMinute, 1))s)" -ForegroundColor White
Write-Host "   Metrics Check: $EnableMetricsCheck" -ForegroundColor White
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if not already active
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & "$PSScriptRoot/../.venv/Scripts/Activate.ps1"
}

# Build Python command
$pythonCmd = "python"
$scriptPath = "$PSScriptRoot/continuous_agent_testing.py"
$args = @(
    "--duration", $DurationMinutes,
    "--rate", $OperationsPerMinute
)

if ($EnableMetricsCheck) {
    $args += "--check-metrics"
}

# Start the load test
Write-Host "🎬 Starting continuous load test..." -ForegroundColor Green
Write-Host "   Script: $scriptPath" -ForegroundColor Gray
Write-Host "   Args: $($args -join ' ')" -ForegroundColor Gray
Write-Host ""

try {
    & $pythonCmd $scriptPath @args
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Load test completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Load test failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "`n❌ Error running load test: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n📈 View results in Grafana:" -ForegroundColor Cyan
Write-Host "   http://192.168.0.30:3000/d/twisterlab-agents-realtime" -ForegroundColor White
Write-Host ""
