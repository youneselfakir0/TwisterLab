#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Complete diagnostic script for TwisterLab system
.DESCRIPTION
    Performs comprehensive diagnostics of all TwisterLab components
#>

param(
    [switch]$FixIssues,
    [switch]$Verbose
)

Write-Host "=== TwisterLab Complete System Diagnostic ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)" -ForegroundColor White
Write-Host "Mode: $(if ($FixIssues) { 'Diagnostic + Auto-Fix' } else { 'Diagnostic Only' })" -ForegroundColor White
Write-Host ""

$issues = @()
$warnings = @()
$successes = @()

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    switch ($Type) {
        "SUCCESS" { Write-Host "[OK] $Message" -ForegroundColor Green; $script:successes += $Message }
        "ERROR" { Write-Host "[ERROR] $Message" -ForegroundColor Red; $script:issues += $Message }
        "WARNING" { Write-Host "[WARN] $Message" -ForegroundColor Yellow; $script:warnings += $Message }
        "INFO" { Write-Host "[INFO] $Message" -ForegroundColor Blue }
        "HEADER" { Write-Host "`n=== $Message ===" -ForegroundColor Magenta }
    }
}

# 1. Docker and Swarm Check
Write-Status "Checking Docker and Swarm..." "HEADER"

try {
    $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Docker is running (v$dockerVersion)" "SUCCESS"
    } else {
        Write-Status "Docker is not running or not accessible" "ERROR"
        if ($FixIssues) {
            Write-Status "Attempting to start Docker service..." "INFO"
            Start-Service docker -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 5
        }
    }
} catch {
    Write-Status "Docker check failed: $($_.Exception.Message)" "ERROR"
}

try {
    $swarmStatus = docker node ls 2>$null
    if ($LASTEXITCODE -eq 0 -and $swarmStatus -match "Ready") {
        Write-Status "Docker Swarm is active" "SUCCESS"
        $nodeCount = ($swarmStatus | Measure-Object -Line).Lines - 1
        Write-Status "Swarm nodes: $nodeCount" "INFO"
    } else {
        Write-Status "Docker Swarm is not active" "ERROR"
        if ($FixIssues) {
            Write-Status "Initializing Docker Swarm..." "INFO"
            docker swarm init --advertise-addr 127.0.0.1 2>$null | Out-Null
            Start-Sleep -Seconds 3
        }
    }
} catch {
    Write-Status "Swarm check failed: $($_.Exception.Message)" "ERROR"
}

# 2. Network Check
Write-Status "Checking Docker Networks..." "HEADER"

try {
    $networks = docker network ls --format "{{.Name}}" 2>$null
    if ($networks -contains "twisterlab_prod") {
        Write-Status "TwisterLab production network exists" "SUCCESS"
    } else {
        Write-Status "TwisterLab production network missing" "ERROR"
        if ($FixIssues) {
            Write-Status "Creating production network..." "INFO"
            docker network create --driver overlay twisterlab_prod 2>$null | Out-Null
        }
    }
} catch {
    Write-Status "Network check failed: $($_.Exception.Message)" "ERROR"
}

# 3. Service Status Check
Write-Status "Checking TwisterLab Services..." "HEADER"

$expectedServices = @(
    "twisterlab_prod_api",
    "twisterlab_prod_postgres",
    "twisterlab_prod_redis",
    "twisterlab_prod_traefik",
    "twisterlab_prod_webui",
    "twisterlab_prod_ollama"
)

$runningServices = 0
$totalServices = $expectedServices.Count

foreach ($service in $expectedServices) {
    try {
        $serviceInfo = docker service ps $service --format "{{.CurrentState}}" 2>$null | Select-Object -First 1
        if ($serviceInfo -match "Running") {
            Write-Status "$($service.Replace('twisterlab_prod_', '')) service is running" "SUCCESS"
            $runningServices++
        } else {
            Write-Status "$($service.Replace('twisterlab_prod_', '')) service is not running: $serviceInfo" "ERROR"
        }
    } catch {
        Write-Status "$($service.Replace('twisterlab_prod_', '')) service check failed: $($_.Exception.Message)" "ERROR"
    }
}

Write-Status "Service Summary: $runningServices/$totalServices services running" $(if ($runningServices -eq $totalServices) { "SUCCESS" } else { "WARNING" })

# 4. API Endpoint Tests
Write-Status "Testing API Endpoints..." "HEADER"

$endpoints = @(
    @{Name="API Health"; Url="http://localhost:8000/health"; Method="GET"},
    @{Name="Autonomous Status"; Url="http://localhost:8000/api/v1/autonomous/status"; Method="GET"},
    @{Name="Agent List"; Url="http://localhost:8000/api/v1/autonomous/agents"; Method="GET"},
    @{Name="Traefik Dashboard"; Url="http://localhost:8084"; Method="GET"}
)

$workingEndpoints = 0
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -Method $endpoint.Method -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Status "$($endpoint.Name): HTTP $($response.StatusCode)" "SUCCESS"
            $workingEndpoints++
        } else {
            Write-Status "$($endpoint.Name): HTTP $($response.StatusCode)" "WARNING"
        }
    } catch {
        Write-Status "$($endpoint.Name): $($_.Exception.Message)" "ERROR"
    }
}

Write-Status "API Summary: $workingEndpoints/$($endpoints.Count) endpoints working" $(if ($workingEndpoints -gt 0) { "SUCCESS" } else { "ERROR" })

# 5. DNS Configuration Check
Write-Status "Checking DNS Configuration..." "HEADER"

$dnsEntries = @("api.twisterlab.local", "webui.twisterlab.local", "traefik.twisterlab.local")
$workingDNS = 0

foreach ($dns in $dnsEntries) {
    try {
        $result = Resolve-DnsName $dns -ErrorAction Stop
        Write-Status "$dns resolves to $($result.IPAddress)" "SUCCESS"
        $workingDNS++
    } catch {
        Write-Status "$dns resolution failed" "WARNING"
    }
}

# Check hosts file
$hostsPath = "$env:windir\System32\drivers\etc\hosts"
try {
    $hostsContent = Get-Content $hostsPath -ErrorAction Stop
    $twisterlabEntries = $hostsContent | Where-Object { $_ -match "twisterlab\.local" }
    if ($twisterlabEntries.Count -gt 0) {
        Write-Status "Found $($twisterlabEntries.Count) TwisterLab entries in hosts file" "SUCCESS"
    } else {
        Write-Status "No TwisterLab entries in hosts file" "WARNING"
        if ($FixIssues) {
            Write-Status "Running DNS configuration script..." "INFO"
            & ".\configure_dns.ps1"
        }
    }
} catch {
    Write-Status "Hosts file check failed: $($_.Exception.Message)" "ERROR"
}

# 6. Monitoring Stack Check
Write-Status "Checking Monitoring Stack..." "HEADER"

$monitoringEndpoints = @(
    @{Name="Prometheus"; Url="http://localhost:9090/-/healthy"},
    @{Name="Grafana"; Url="http://localhost:3001/api/health"}
)

$workingMonitoring = 0
foreach ($endpoint in $monitoringEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Status "$($endpoint.Name) is accessible" "SUCCESS"
            $workingMonitoring++
        } else {
            Write-Status "$($endpoint.Name): HTTP $($response.StatusCode)" "WARNING"
        }
    } catch {
        Write-Status "$($endpoint.Name): $($_.Exception.Message)" "ERROR"
    }
}

# 7. Log Analysis
Write-Status "Analyzing Service Logs..." "HEADER"

$servicesToCheck = @("twisterlab_prod_api", "twisterlab_prod_traefik", "twisterlab_prod_postgres")
foreach ($service in $servicesToCheck) {
    try {
        $logs = docker service logs $service --tail 20 2>$null
        $errorCount = ($logs | Select-String -Pattern "ERROR|error|Error|FATAL|fatal" -CaseSensitive:$false).Count
        $warningCount = ($logs | Select-String -Pattern "WARNING|warning|WARN" -CaseSensitive:$false).Count

        if ($errorCount -gt 0) {
            Write-Status "$($service.Replace('twisterlab_prod_', '')): $errorCount errors found" "ERROR"
        } elseif ($warningCount -gt 0) {
            Write-Status "$($service.Replace('twisterlab_prod_', '')): $warningCount warnings found" "WARNING"
        } else {
            Write-Status "$($service.Replace('twisterlab_prod_', '')): logs clean" "SUCCESS"
        }
    } catch {
        Write-Status "$($service.Replace('twisterlab_prod_', '')): log check failed" "WARNING"
    }
}

# 8. Test Suite Execution
Write-Status "Running Test Suite..." "HEADER"

$testFiles = @(
    "test_autonomous_agents.py",
    "test_api.py",
    "test_database_integration.py"
)

$passedTests = 0
$totalTestFiles = $testFiles.Count

foreach ($testFile in $testFiles) {
    if (Test-Path $testFile) {
        try {
            $testResult = & python $testFile 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Status "$testFile PASSED" "SUCCESS"
                $passedTests++
            } else {
                Write-Status "$testFile FAILED (Exit code $LASTEXITCODE)" "ERROR"
                if ($Verbose) {
                    Write-Host "Test output:" -ForegroundColor Gray
                    $testResult | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
                }
            }
        } catch {
            Write-Status "$testFile EXECUTION FAILED - $($_.Exception.Message)" "ERROR"
        }
    } else {
        Write-Status "$testFile FILE NOT FOUND" "WARNING"
    }
}

Write-Status "Test Summary: $passedTests/$totalTestFiles test files passed" $(if ($passedTests -eq $totalTestFiles) { "SUCCESS" } else { "WARNING" })

# 9. Backup System Check
Write-Status "Checking Backup System..." "HEADER"

if (Test-Path "backup\automated_backup.py") {
    try {
        $backupResult = & python backup\automated_backup.py stats 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Backup system operational" "SUCCESS"
            if ($Verbose) {
                Write-Host "Backup stats:" -ForegroundColor Gray
                $backupResult | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
            }
        } else {
            Write-Status "Backup system check failed" "WARNING"
        }
    } catch {
        Write-Status "Backup system check error: $($_.Exception.Message)" "ERROR"
    }
} else {
    Write-Status "Backup system files not found" "WARNING"
}

# 10. Resource Usage Check
Write-Status "Checking Resource Usage..." "HEADER"

try {
    $containers = docker ps --format "{{.Names}}:{{.Ports}}" 2>$null
    $twisterlabContainers = $containers | Where-Object { $_ -match "twisterlab" }
    Write-Status "Active TwisterLab containers: $($twisterlabContainers.Count)" "INFO"

    if ($Verbose -and $twisterlabContainers.Count -gt 0) {
        Write-Host "Container details:" -ForegroundColor Gray
        $twisterlabContainers | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }
} catch {
    Write-Status "Container check failed: $($_.Exception.Message)" "WARNING"
}

# 11. Final Recommendations
Write-Status "Diagnostic Summary and Recommendations" "HEADER"

Write-Host "`nSUMMARY:" -ForegroundColor Cyan
Write-Host "   [OK] Successes: $($successes.Count)" -ForegroundColor Green
Write-Host "   [WARN] Warnings: $($warnings.Count)" -ForegroundColor Yellow
Write-Host "   [ERROR] Issues: $($issues.Count)" -ForegroundColor Red

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "`nSYSTEM STATUS: ALL CLEAR - TwisterLab is fully operational!" -ForegroundColor Green
} elseif ($issues.Count -eq 0) {
    Write-Host "`nSYSTEM STATUS: MOSTLY HEALTHY - Some minor issues to address" -ForegroundColor Yellow
} else {
    Write-Host "`nSYSTEM STATUS: ISSUES DETECTED - Immediate attention required" -ForegroundColor Red
}

if ($issues.Count -gt 0) {
    Write-Host "`nCRITICAL ISSUES TO FIX:" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
}

if ($warnings.Count -gt 0) {
    Write-Host "`nWARNINGS TO ADDRESS:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
}

if ($FixIssues -and ($issues.Count -gt 0 -or $warnings.Count -gt 0)) {
    Write-Host "`nRECOMMENDED ACTIONS:" -ForegroundColor Cyan
    Write-Host "   1. Redeploy services: docker stack deploy -c docker-compose.production.yml twisterlab_prod" -ForegroundColor White
    Write-Host "   2. Run DNS config: .\configure_dns.ps1" -ForegroundColor White
    Write-Host "   3. Check logs: docker service logs [service_name]" -ForegroundColor White
    Write-Host "   4. Run tests: python test_production_apis.py" -ForegroundColor White
}

Write-Host "`nDiagnostic complete at $(Get-Date)" -ForegroundColor Cyan
