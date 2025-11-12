#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Complete diagnostic script for TwisterLab system
.DESCRIPTION
    Performs comprehensive testing of all TwisterLab components:
    - Docker Swarm status
    - Service health
    - API endpoints
    - DNS resolution
    - Database connectivity
    - Agent operations
    - Monitoring systems
.NOTES
    Run as Administrator
    Requires: Docker, PowerShell 7+
#>

param(
    [switch]$Verbose,
    [switch]$FixIssues,
    [string]$OutputFile = "debug_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
)

# Configuration
$Config = @{
    ApiBaseUrl = "http://api.twisterlab.local"
    DirectApiUrl = "http://localhost:8000"
    WebUiUrl = "http://webui.twisterlab.local"
    TraefikUrl = "http://traefik.twisterlab.local"
    GrafanaUrl = "http://grafana.twisterlab.local"
    PrometheusUrl = "http://prometheus.twisterlab.local"
    Timeout = 10
    ExpectedServices = @("postgres", "redis", "traefik", "webui", "ollama")  # API runs as Windows service
}

# Results storage
$Global:DebugResults = @{
    Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    System = @{}
    Services = @{}
    Endpoints = @{}
    Agents = @{}
    Monitoring = @{}
    Issues = @()
    Recommendations = @()
}

function Write-DebugLog {
    param([string]$Message, [string]$Level = "INFO")

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARN" { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        "INFO" { Write-Host $LogMessage -ForegroundColor Blue }
        default { Write-Host $LogMessage -ForegroundColor White }
    }

    if ($Verbose) {
        Add-Content -Path "debug_log.txt" -Value $LogMessage
    }
}

function Test-DockerStatus {
    Write-DebugLog "Testing Docker status..." "INFO"

    try {
        $dockerVersion = docker version --format json | ConvertFrom-Json
        $dockerInfo = docker info --format json | ConvertFrom-Json

        $Global:DebugResults.System.Docker = @{
            Version = $dockerVersion.Client.Version
            Status = "Running"
            Containers = $dockerInfo.Containers
            Images = $dockerInfo.Images
        }

        Write-DebugLog "Docker is running - Version: $($dockerVersion.Client.Version)" "SUCCESS"
        return $true
    }
    catch {
        $Global:DebugResults.System.Docker = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-DebugLog "Docker check failed: $($_.Exception.Message)" "ERROR"
        $Global:DebugResults.Issues += "Docker is not running or accessible"
        return $false
    }
}

function Test-SwarmStatus {
    Write-DebugLog "Testing Docker Swarm status..." "INFO"

    try {
        $swarmStatus = docker node ls --format json | ConvertFrom-Json

        if ($swarmStatus) {
            $nodeCount = $swarmStatus.Count
            $readyNodes = ($swarmStatus | Where-Object { $_.Status -eq "Ready" }).Count

            $Global:DebugResults.System.Swarm = @{
                Status = "Active"
                TotalNodes = $nodeCount
                ReadyNodes = $readyNodes
                Nodes = $swarmStatus
            }

            Write-DebugLog "Swarm active - $readyNodes/$nodeCount nodes ready" "SUCCESS"
            return $true
        }
        else {
            throw "No swarm nodes found"
        }
    }
    catch {
        $Global:DebugResults.System.Swarm = @{
            Status = "Inactive"
            Error = $_.Exception.Message
        }
        Write-DebugLog "Swarm check failed: $($_.Exception.Message)" "ERROR"
        $Global:DebugResults.Issues += "Docker Swarm is not active"
        return $false
    }
}

function Test-Services {
    Write-DebugLog "Testing TwisterLab services..." "INFO"

    foreach ($service in $Config.ExpectedServices) {
        $serviceName = "twisterlab_prod_$service"

        try {
            $serviceInfo = docker service ps $serviceName --format json | ConvertFrom-Json

            if ($serviceInfo) {
                $runningTasks = ($serviceInfo | Where-Object { $_.CurrentState -match "Running" }).Count
                $totalTasks = $serviceInfo.Count

                $Global:DebugResults.Services.$service = @{
                    Name = $serviceName
                    Status = "Running"
                    RunningTasks = $runningTasks
                    TotalTasks = $totalTasks
                    Tasks = $serviceInfo
                }

                if ($runningTasks -eq $totalTasks) {
                    Write-DebugLog "$service - $runningTasks/$totalTasks tasks running" "SUCCESS"
                }
                else {
                    Write-DebugLog "$service - $runningTasks/$totalTasks tasks running" "WARN"
                    $Global:DebugResults.Issues += "$service has only $runningTasks/$totalTasks tasks running"
                }
            }
            else {
                throw "Service not found"
            }
        }
        catch {
            $Global:DebugResults.Services.$service = @{
                Name = $serviceName
                Status = "Failed"
                Error = $_.Exception.Message
            }
            Write-DebugLog "$service check failed: $($_.Exception.Message)" "ERROR"
            $Global:DebugResults.Issues += "$service service is not running"
        }
    }
}

function Test-Endpoints {
    Write-DebugLog "Testing API endpoints..." "INFO"

    $endpoints = @(
        @{Name="API Health"; Url="$($Config.DirectApiUrl)/health"; Type="api"},
        @{Name="Autonomous Status"; Url="$($Config.DirectApiUrl)/api/v1/autonomous/status"; Type="api"},
        @{Name="Agents List"; Url="$($Config.DirectApiUrl)/api/v1/autonomous/agents"; Type="api"},
        @{Name="WebUI"; Url=$Config.WebUiUrl; Type="webui"},
        @{Name="Traefik Dashboard"; Url=$Config.TraefikUrl; Type="traefik"},
        @{Name="Grafana"; Url=$Config.GrafanaUrl; Type="monitoring"},
        @{Name="Prometheus"; Url=$Config.PrometheusUrl; Type="monitoring"}
    )

    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec $Config.Timeout -ErrorAction Stop

            $Global:DebugResults.Endpoints.$($endpoint.Name -replace " ", "_") = @{
                Url = $endpoint.Url
                StatusCode = $response.StatusCode
                Status = "Success"
                ResponseTime = $response.BaseResponse.ResponseTime.TotalMilliseconds
                Type = $endpoint.Type
            }

            Write-DebugLog "$($endpoint.Name) - HTTP $($response.StatusCode) ($([math]::Round($response.BaseResponse.ResponseTime.TotalMilliseconds))ms)" "SUCCESS"
        }
        catch {
            $Global:DebugResults.Endpoints.$($endpoint.Name -replace " ", "_") = @{
                Url = $endpoint.Url
                Status = "Failed"
                Error = $_.Exception.Message
                Type = $endpoint.Type
            }
            Write-DebugLog "$($endpoint.Name) failed: $($_.Exception.Message)" "ERROR"
            $Global:DebugResults.Issues += "$($endpoint.Name) endpoint is not accessible"
        }
    }
}

function Test-AgentOperations {
    Write-DebugLog "Testing autonomous agents..." "INFO"

    $agents = @(
        @{Name="monitoring"; Operation="health_check"; Context=@{check_type="system"}},
        @{Name="backup"; Operation="backup"; Context=@{}},
        @{Name="sync"; Operation="sync"; Context=@{}}
    )

    foreach ($agent in $agents) {
        try {
            $payload = @{
                operation = $agent.Operation
                context = $agent.Context
            } | ConvertTo-Json

            $response = Invoke-WebRequest `
                -Uri "$($Config.DirectApiUrl)/api/v1/autonomous/agents/$($agent.Name)/execute" `
                -Method POST `
                -Body $payload `
                -ContentType "application/json" `
                -TimeoutSec $Config.Timeout `
                -ErrorAction Stop

            $result = $response.Content | ConvertFrom-Json

            $Global:DebugResults.Agents.$($agent.Name) = @{
                Status = "Success"
                ResponseCode = $response.StatusCode
                Result = $result
            }

            Write-DebugLog "$($agent.Name) agent - Status: $($result.status)" "SUCCESS"
        }
        catch {
            $Global:DebugResults.Agents.$($agent.Name) = @{
                Status = "Failed"
                Error = $_.Exception.Message
            }
            Write-DebugLog "$($agent.Name) agent failed: $($_.Exception.Message)" "ERROR"
            $Global:DebugResults.Issues += "$($agent.Name) agent is not responding"
        }
    }
}function Test-DNSResolution {
    Write-DebugLog "Testing DNS resolution..." "INFO"

    $dnsTests = @(
        "api.twisterlab.local",
        "webui.twisterlab.local",
        "traefik.twisterlab.local",
        "grafana.twisterlab.local",
        "prometheus.twisterlab.local"
    )

    foreach ($domain in $dnsTests) {
        try {
            $result = Resolve-DnsName $domain -ErrorAction Stop

            $Global:DebugResults.System.DNS.$domain = @{
                Resolved = $true
                IPAddress = $result.IPAddress
            }

            Write-DebugLog "$domain resolves to $($result.IPAddress)" "SUCCESS"
        }
        catch {
            $Global:DebugResults.System.DNS.$domain = @{
                Resolved = $false
                Error = $_.Exception.Message
            }
            Write-DebugLog "$domain DNS resolution failed" "ERROR"
            $Global:DebugResults.Issues += "DNS resolution failed for $domain"
        }
    }
}

function Test-DatabaseConnectivity {
    Write-DebugLog "Testing database connectivity..." "INFO"

    try {
        # Test PostgreSQL connection via container
        $pgContainer = docker ps --filter "name=twisterlab_prod_postgres" --format "{{.Names}}"
        if ($pgContainer) {
            $pgTest = docker exec $pgContainer pg_isready -U twisterlab -d twisterlab

            if ($LASTEXITCODE -eq 0) {
                $Global:DebugResults.Services.Database = @{
                    PostgreSQL = "Connected"
                    Status = "Success"
                }
                Write-DebugLog "PostgreSQL connection successful" "SUCCESS"
            }
            else {
                throw "pg_isready failed"
            }
        }
        else {
            throw "PostgreSQL container not found"
        }
    }
    catch {
        $Global:DebugResults.Services.Database = @{
            PostgreSQL = "Failed"
            Error = $_.Exception.Message
        }
        Write-DebugLog "PostgreSQL connection failed: $($_.Exception.Message)" "ERROR"
        $Global:DebugResults.Issues += "Database connectivity issues"
    }

    try {
        # Test Redis connection
        $redisContainer = docker ps --filter "name=twisterlab_prod_redis" --format "{{.Names}}"
        if ($redisContainer) {
            $redisTest = docker exec $redisContainer redis-cli ping

            if ($redisTest -eq "PONG") {
                $Global:DebugResults.Services.Database.Redis = "Connected"
                Write-DebugLog "Redis connection successful" "SUCCESS"
            }
            else {
                throw "Redis ping failed"
            }
        }
        else {
            throw "Redis container not found"
        }
    }
    catch {
        $Global:DebugResults.Services.Database.Redis = "Failed"
        Write-DebugLog "Redis connection failed: $($_.Exception.Message)" "ERROR"
        $Global:DebugResults.Issues += "Redis connectivity issues"
    }
}

function Generate-Recommendations {
    Write-DebugLog "Generating recommendations..." "INFO"

    # Analyze results and generate recommendations
    $issueCount = $Global:DebugResults.Issues.Count

    if ($issueCount -eq 0) {
        $Global:DebugResults.Recommendations += "All systems operational - no issues found"
        $Global:DebugResults.Recommendations += "Consider implementing automated monitoring alerts"
        $Global:DebugResults.Recommendations += "Regular backup verification recommended"
    }
    else {
        $Global:DebugResults.Recommendations += "Address $issueCount identified issues"

        if ($Global:DebugResults.Issues -match "Docker") {
            $Global:DebugResults.Recommendations += "Restart Docker service and verify installation"
        }

        if ($Global:DebugResults.Issues -match "Swarm") {
            $Global:DebugResults.Recommendations += "Reinitialize Docker Swarm: docker swarm init"
        }

        if ($Global:DebugResults.Issues -match "service") {
            $Global:DebugResults.Recommendations += "Redeploy services: docker stack deploy -c docker-compose.production.yml twisterlab_prod"
        }

        if ($Global:DebugResults.Issues -match "endpoint") {
            $Global:DebugResults.Recommendations += "Check service logs and restart failing containers"
        }

        if ($Global:DebugResults.Issues -match "DNS") {
            $Global:DebugResults.Recommendations += "Run DNS configuration script: .\configure_dns.ps1"
        }

        if ($Global:DebugResults.Issues -match "agent") {
            $Global:DebugResults.Recommendations += "Verify agent initialization and dependencies"
        }
    }
}

function Export-Results {
    param([string]$OutputPath)

    try {
        $Global:DebugResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
        Write-DebugLog "Results exported to: $OutputPath" "SUCCESS"
    }
    catch {
        Write-DebugLog "Failed to export results: $($_.Exception.Message)" "ERROR"
    }
}

function Show-Summary {
    $issueCount = $Global:DebugResults.Issues.Count
    $serviceCount = $Global:DebugResults.Services.Count
    $endpointCount = $Global:DebugResults.Endpoints.Count

    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "TWISTERLAB SYSTEM DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan

    Write-Host "System Status:" -ForegroundColor White
    Write-Host "  Docker: $($Global:DebugResults.System.Docker.Status)" -ForegroundColor $(if ($Global:DebugResults.System.Docker.Status -eq "Running") { "Green" } else { "Red" })
    Write-Host "  Swarm: $($Global:DebugResults.System.Swarm.Status)" -ForegroundColor $(if ($Global:DebugResults.System.Swarm.Status -eq "Active") { "Green" } else { "Red" })

    Write-Host "`nServices Checked: $serviceCount" -ForegroundColor White
    Write-Host "Endpoints Tested: $endpointCount" -ForegroundColor White

    if ($issueCount -eq 0) {
        Write-Host "`n✅ ALL SYSTEMS OPERATIONAL" -ForegroundColor Green
        Write-Host "No issues detected - TwisterLab is running perfectly!" -ForegroundColor Green
    }
    else {
        Write-Host "`n❌ ISSUES FOUND: $issueCount" -ForegroundColor Red
        Write-Host "Issues:" -ForegroundColor Yellow
        foreach ($issue in $Global:DebugResults.Issues) {
            Write-Host "  • $issue" -ForegroundColor Yellow
        }
    }

    Write-Host "`nRecommendations:" -ForegroundColor Cyan
    foreach ($rec in $Global:DebugResults.Recommendations) {
        Write-Host "  • $rec" -ForegroundColor White
    }

    Write-Host "`nDetailed results saved to: $OutputFile" -ForegroundColor Blue
}

# Main execution
Write-DebugLog "Starting complete TwisterLab system diagnostic..." "INFO"

$tests = @(
    ${function:Test-DockerStatus},
    ${function:Test-SwarmStatus},
    ${function:Test-Services},
    ${function:Test-Endpoints},
    ${function:Test-AgentOperations},
    ${function:Test-DNSResolution},
    ${function:Test-DatabaseConnectivity}
)

foreach ($test in $tests) {
    try {
        & $test
    }
    catch {
        Write-DebugLog "Test $($test.Name) failed: $($_.Exception.Message)" "ERROR"
        $Global:DebugResults.Issues += "Test $($test.Name) execution failed"
    }
}

Generate-Recommendations
Export-Results -OutputPath $OutputFile
Show-Summary

Write-DebugLog "Complete diagnostic finished" "INFO"
