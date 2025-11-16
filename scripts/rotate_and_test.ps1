<#
Rotate secrets and run an end-to-end verification checklist.

This script coordinates secret rotation and validates system health after rotation.
It supports dry-run, canary, and full apply modes. It currently orchestrates the
per-secret rotate scripts (`rotate_postgres_secret.ps1`, `rotate_redis_secret.ps1`,
`rotate_grafana_secret.ps1`) and runs a suite of checks.

Usage examples:
# Dry-run (no changes):
#  .\scripts\rotate_and_test.ps1 -DryRun

# Staging canary apply (rotate Postgres only):
#  .\scripts\rotate_and_test.ps1 -Apply -Canary -RotatePostgres -Environment staging -CanaryService twisterlab_api
# For Grafana service name override:
#  .\scripts\rotate_and_test.ps1 -DryRun -RotateGrafana -GrafanaServiceName twisterlab_monitoring_grafana

Note: Only run `-Apply` on a machine that has Docker & Swarm access and needed permissions.
#>

param(
    [switch]$DryRun,
    [switch]$Apply,
    [switch]$Canary,
    [string]$CanaryService = "",
    [ValidateSet("dev", "staging", "prod", "production", "local")] [string]$Environment = "local",
    [switch]$RotatePostgres,
    [switch]$RotateRedis,
    [switch]$RotateGrafana,
    [switch]$RestartGrafana,
    [switch]$Force,
    [string]$GrafanaServiceName = ""
)

function Write-Log ([string]$message, [string]$level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] [$level] $message"
    Write-Host $line
    $log = "logs/rotate_and_test_$(Get-Date -Format yyyyMMddHHmmss).log"
    $line | Out-File -FilePath $log -Append
}

function Run-HealthCheck {
    param([string]$url, [int]$expected = 200)
    try {
        Write-Log "Health check: $url"
        $resp = curl -sS -o /dev/null -w "%{http_code}" $url 2>$null
        return $resp -eq $expected
    } catch {
        return $false
    }
}

function Run-SmokeChecks {
    Write-Log "Running smoke checks..."
    $ok = $true
    # API
    if (-not (Run-HealthCheck -url "http://localhost:8000/health" -expected 200)) { Write-Log "API health check failed" "ERROR"; $ok = $false }
    # Prometheus
    if (-not (Run-HealthCheck -url "http://localhost:9090/-/healthy" -expected 200)) { Write-Log "Prometheus health check failed" "ERROR"; $ok = $false }
    # Grafana
    if (-not (Run-HealthCheck -url "http://localhost:3000/api/health" -expected 200)) { Write-Log "Grafana health check failed" "ERROR"; $ok = $false }
    return $ok
}

function Run-DataChecks {
    Write-Log "Running DB/Redis connect checks..."
    $ok = $true
    # DB check - requires docker network or a helper container; attempt using docker run
    try {
        $pgOut = docker run --rm --network twisterlab_backend --entrypoint psql postgres:15 -h twisterlab_postgres -U twisterlab -c "SELECT 1;" -d twisterlab 2>&1
        if ($LASTEXITCODE -ne 0) { Write-Log "Postgres test failed: $pgOut" "ERROR"; $ok = $false }
    } catch {
        Write-Log "Postgres test error: $_" "ERROR"; $ok = $false
    }
    # Redis check
    try {
        $redisId = (docker ps -q -f name=twisterlab_redis) -join ""
        if ($redisId -ne "") {
            $redisPing = docker exec $redisId redis-cli ping
            if ($redisPing -ne "PONG") { Write-Log "Redis ping failed: $redisPing" "ERROR"; $ok = $false }
        } else {
            Write-Log "Redis container not found" "WARN"
            $ok = $false
        }
    } catch {
        Write-Log "Redis test error: $_" "ERROR"; $ok = $false
    }
    return $ok
}

function Run-MonitoringChecks {
    Write-Log "Checking exporters and Prometheus targets..."
    $ok = $true
    try {
        $pgEx = curl -sS -o /dev/null -w "%{http_code}" http://localhost:9187/metrics
        if ($pgEx -ne 200) { Write-Log "Postgres exporter metrics unreachable" "ERROR"; $ok = $false }
        $redisEx = curl -sS -o /dev/null -w "%{http_code}" http://localhost:9121/metrics
        if ($redisEx -ne 200) { Write-Log "Redis exporter metrics unreachable" "ERROR"; $ok = $false }
        # Prometheus targets
        $targets = curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | "\(.labels.job) --- \(.health)"'
        if ($targets -eq "") { Write-Log "Prometheus targets not found" "WARN"; $ok = $false }
    } catch {
        Write-Log "Monitoring checks error: $_" "ERROR"; $ok = $false
    }
    return $ok
}

function Run-GrafanaChecks {
    Write-Log "Testing Grafana datasources & API..."
    $ok = $true
    try {
        # We'll fetch datasources and ensure status OK
        $code = curl -s -o /dev/null -w "%{http_code}" -u "admin:$(cat /run/secrets/grafana_admin_password)" http://localhost:3000/api/datasources
        if ($code -ne 200) { Write-Log "Grafana API/datasources failed: $code" "ERROR"; $ok = $false }
    } catch {
        Write-Log "Grafana checks error: $_" "ERROR"; $ok = $false
    }
    return $ok
}

function Run-IntegrationTests {
    Write-Log "Running integration tests (pytest)"
    try {
        pip install pytest pytest-asyncio -q
        $result = pytest -q tests/ --maxfail=1
        if ($LASTEXITCODE -ne 0) { Write-Log "Integration tests failed (pytests)." "ERROR"; return $false }
        Write-Log "Integration tests passed." "INFO"; return $true
    } catch {
        Write-Log "Integration tests error: $_" "ERROR"; return $false
    }
}

function Run-CISecretScan {
    Write-Log "Running CI secret scan (local)"
    try {
        $exitCode = & python scripts/ci_secret_scan.py
        if ($LASTEXITCODE -ne 0) { Write-Log "CI secret scan found issues" "ERROR"; return $false }
        Write-Log "CI secret scan ok" "INFO"; return $true
    } catch {
        Write-Log "CI secret scan error: $_" "ERROR"; return $false
    }
}

function Run-VerificationSuite {
    Write-Log "Starting verification suite..."
    $s1 = Run-SmokeChecks
    $s2 = Run-DataChecks
    $s3 = Run-MonitoringChecks
    $s4 = Run-GrafanaChecks
    $s5 = Run-IntegrationTests
    $s6 = Run-CISecretScan
    return ($s1 -and $s2 -and $s3 -and $s4 -and $s5 -and $s6)
}

Write-Log "rotate_and_test started (Environment=$Environment, DryRun=$DryRun, Apply=$Apply, Canary=$Canary, GrafanaServiceName=$GrafanaServiceName)."

if ($Canary -and $CanaryService -eq "") {
    Write-Log "Canary mode requires a service to be specified (CanaryService)." "ERROR"
    exit 1
}

if ($DryRun -and $Apply) {
    Write-Log "Conflicting flags: DryRun and Apply cannot both be set." "ERROR"; exit 1
}

# Default to rotate all if none specified
if (-not ($RotatePostgres -or $RotateRedis -or $RotateGrafana)) { $RotatePostgres = $true; $RotateRedis = $true; $RotateGrafana = $true }

if ($DryRun) { Write-Log "DRY RUN: No changes will be applied. Will run verification steps only." "INFO" }

# Perform the rotation (or dry-run)
if ($Apply -or $DryRun) {
    if ($RotatePostgres) {
        if ($DryRun) { powershell -ExecutionPolicy Bypass -File .\scripts\rotate_postgres_secret.ps1 -DryRun } else { powershell -ExecutionPolicy Bypass -File .\scripts\rotate_postgres_secret.ps1 -Force }
    }
    if ($RotateRedis) {
        if ($DryRun) { powershell -ExecutionPolicy Bypass -File .\scripts\rotate_redis_secret.ps1 -DryRun } else { powershell -ExecutionPolicy Bypass -File .\scripts\rotate_redis_secret.ps1 -Force }
    }
    if ($RotateGrafana) {
        if ($DryRun) {
            if ($GrafanaServiceName -and $GrafanaServiceName -ne "") {
                powershell -ExecutionPolicy Bypass -File .\scripts\rotate_grafana_secret.ps1 -DryRun -ServiceName $GrafanaServiceName
            } else {
                powershell -ExecutionPolicy Bypass -File .\scripts\rotate_grafana_secret.ps1 -DryRun
            }
        } else {
            if ($GrafanaServiceName -and $GrafanaServiceName -ne "") {
                powershell -ExecutionPolicy Bypass -File .\scripts\rotate_grafana_secret.ps1 -Force -RestartService:$RestartGrafana -ServiceName $GrafanaServiceName
            } else {
                powershell -ExecutionPolicy Bypass -File .\scripts\rotate_grafana_secret.ps1 -Force -RestartService:$RestartGrafana
            }
        }
    }
}

Write-Log "Rotation phase done, starting validation checks..."
if (-not (Run-VerificationSuite)) {
    Write-Log "Validation checks failed after rotation. Please review logs and consider rotating again or rolling back." "ERROR"
    exit 2
}

Write-Log "All verification checks passed after rotation." "INFO"
Write-Log "End of rotate_and_test run." "INFO"
exit 0
