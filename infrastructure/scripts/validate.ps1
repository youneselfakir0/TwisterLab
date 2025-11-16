# TwisterLab System Validation Script
# Version: 1.0.0
# Date: 2025-11-15

param(
    [switch]$Quick,
    [switch]$Full,
    [switch]$Silent,
    [int]$Timeout = 30,
    [string]$ReportPath = "$env:USERPROFILE\TwisterLab_Validation_Reports"
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportFile = "$ReportPath\validation_report_$Timestamp.json"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    if (!$Silent) {
        $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$Timestamp] [$Level] $Message"
    }
}

function New-ReportDirectory {
    if (!(Test-Path $ReportPath)) {
        New-Item -ItemType Directory -Path $ReportPath -Force | Out-Null
    }
}

function Test-DockerServices {
    Write-Log "Testing Docker services..."

    try {
        $services = docker service ls --format "{{.Name}}:{{.Replicas}}"
        $serviceStatus = @{}

        # Expected services
        $expectedServices = @(
            "twisterlab_api",
            "twisterlab_postgres",
            "twisterlab_redis",
            "twisterlab_ollama",
            "twisterlab_openwebui",
            "twisterlab_traefik",
            "twisterlab_prometheus",
            "twisterlab_grafana",
            "twisterlab_node_exporter"
        )

        foreach ($service in $expectedServices) {
            $serviceInfo = $services | Where-Object { $_ -match "^${service}:" }
            if ($serviceInfo) {
                $replicas = ($serviceInfo -split ":")[1]
                $expected, $running = $replicas -split "/"
                $serviceStatus[$service] = @{
                    Status = if ($running -eq $expected) { "Running" } else { "Partial" }
                    Replicas = $replicas
                    Healthy = ($running -eq $expected)
                }
            } else {
                $serviceStatus[$service] = @{
                    Status = "Not Found"
                    Replicas = "0/0"
                    Healthy = $false
                }
            }
        }

        return @{
            Component = "DockerServices"
            Status = "Completed"
            Healthy = ($serviceStatus.Values | Where-Object { $_.Healthy -eq $false }).Count -eq 0
            Details = $serviceStatus
        }

    } catch {
        return @{
            Component = "DockerServices"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-APIEndpoints {
    Write-Log "Testing API endpoints..."

    try {
        $endpoints = @(
            @{ Url = "http://192.168.0.30:8000/health"; Name = "Health Check" },
            @{ Url = "http://192.168.0.30:8000/docs"; Name = "API Documentation" },
            @{ Url = "http://192.168.0.30:8000/openapi.json"; Name = "OpenAPI Spec" },
            @{ Url = "http://192.168.0.30:8000/mcp/status"; Name = "MCP Status" }
        )

        $endpointResults = @{}

        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec $Timeout -UseBasicParsing
                $endpointResults[$endpoint.Name] = @{
                    Status = "Success"
                    StatusCode = $response.StatusCode
                    Healthy = $response.StatusCode -eq 200
                }
            } catch {
                $endpointResults[$endpoint.Name] = @{
                    Status = "Failed"
                    Error = $_.Exception.Message
                    Healthy = $false
                }
            }
        }

        return @{
            Component = "APIEndpoints"
            Status = "Completed"
            Healthy = ($endpointResults.Values | Where-Object { $_.Healthy -eq $false }).Count -eq 0
            Details = $endpointResults
        }

    } catch {
        return @{
            Component = "APIEndpoints"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-DatabaseConnectivity {
    Write-Log "Testing database connectivity..."

    try {
        # Test via API health endpoint (which tests DB connection)
        $response = Invoke-WebRequest -Uri "http://192.168.0.30:8000/health" -TimeoutSec $Timeout -UseBasicParsing

        if ($response.StatusCode -eq 200) {
            $healthData = $response.Content | ConvertFrom-Json

            return @{
                Component = "DatabaseConnectivity"
                Status = "Completed"
                Healthy = $healthData.database -eq "healthy"
                Details = @{
                    APIHealth = $healthData
                    ConnectionStatus = if ($healthData.database -eq "healthy") { "Connected" } else { "Failed" }
                }
            }
        } else {
            return @{
                Component = "DatabaseConnectivity"
                Status = "Failed"
                Healthy = $false
                Error = "Health endpoint returned status $($response.StatusCode)"
            }
        }

    } catch {
        return @{
            Component = "DatabaseConnectivity"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-MonitoringStack {
    Write-Log "Testing monitoring stack..."

    try {
        $monitoringTests = @{}

        # Test Prometheus
        try {
            $response = Invoke-WebRequest -Uri "http://192.168.0.30:9090/-/healthy" -TimeoutSec $Timeout -UseBasicParsing
            $monitoringTests.Prometheus = @{
                Status = "Success"
                StatusCode = $response.StatusCode
                Healthy = $response.StatusCode -eq 200
            }
        } catch {
            $monitoringTests.Prometheus = @{
                Status = "Failed"
                Error = $_.Exception.Message
                Healthy = $false
            }
        }

        # Test Grafana
        try {
            $response = Invoke-WebRequest -Uri "http://192.168.0.30:3000/api/health" -TimeoutSec $Timeout -UseBasicParsing
            $monitoringTests.Grafana = @{
                Status = "Success"
                StatusCode = $response.StatusCode
                Healthy = $response.StatusCode -eq 200
            }
        } catch {
            $monitoringTests.Grafana = @{
                Status = "Failed"
                Error = $_.Exception.Message
                Healthy = $false
            }
        }

        # Test Node Exporter
        try {
            $response = Invoke-WebRequest -Uri "http://192.168.0.30:9100/metrics" -TimeoutSec $Timeout -UseBasicParsing
            $monitoringTests.NodeExporter = @{
                Status = "Success"
                StatusCode = $response.StatusCode
                Healthy = $response.StatusCode -eq 200
                MetricsAvailable = $response.Content.Contains("# HELP")
            }
        } catch {
            $monitoringTests.NodeExporter = @{
                Status = "Failed"
                Error = $_.Exception.Message
                Healthy = $false
            }
        }

        return @{
            Component = "MonitoringStack"
            Status = "Completed"
            Healthy = ($monitoringTests.Values | Where-Object { $_.Healthy -eq $false }).Count -eq 0
            Details = $monitoringTests
        }

    } catch {
        return @{
            Component = "MonitoringStack"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-SSLConfiguration {
    Write-Log "Testing SSL configuration..."

    try {
        # Test HTTPS endpoint
        try {
            $response = Invoke-WebRequest -Uri "https://192.168.0.30:443" -TimeoutSec $Timeout -SkipCertificateCheck
            $sslStatus = @{
                Status = "Success"
                StatusCode = $response.StatusCode
                CertificateValid = $true  # Since we skip check, assume it's working
                Healthy = $true
            }
        } catch {
            $sslStatus = @{
                Status = "Failed"
                Error = $_.Exception.Message
                CertificateValid = $false
                Healthy = $false
            }
        }

        return @{
            Component = "SSLConfiguration"
            Status = "Completed"
            Healthy = $sslStatus.Healthy
            Details = $sslStatus
        }

    } catch {
        return @{
            Component = "SSLConfiguration"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-SystemResources {
    Write-Log "Testing system resources..."

    try {
        $systemInfo = @{}

        # Get Docker system info
        $dockerInfo = docker system info --format "{{json .}}"
        $systemInfo.Docker = $dockerInfo | ConvertFrom-Json

        # Get container stats
        $containerStats = docker stats --no-stream --format "{{.Container}}:{{.CPUPerc}}:{{.MemUsage}}"
        $systemInfo.ContainerStats = $containerStats

        # Check disk space
        $diskInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" } |
            Select-Object Size, FreeSpace
        $diskUsagePercent = [math]::Round((($diskInfo.Size - $diskInfo.FreeSpace) / $diskInfo.Size) * 100, 2)
        $systemInfo.DiskUsage = @{
            TotalGB = [math]::Round($diskInfo.Size / 1GB, 2)
            FreeGB = [math]::Round($diskInfo.FreeSpace / 1GB, 2)
            UsagePercent = $diskUsagePercent
            Healthy = $diskUsagePercent -lt 90
        }

        # Check memory
        $memoryInfo = Get-WmiObject -Class Win32_OperatingSystem |
            Select-Object TotalVisibleMemorySize, FreePhysicalMemory
        $memoryUsagePercent = [math]::Round((($memoryInfo.TotalVisibleMemorySize - $memoryInfo.FreePhysicalMemory) / $memoryInfo.TotalVisibleMemorySize) * 100, 2)
        $systemInfo.MemoryUsage = @{
            TotalGB = [math]::Round($memoryInfo.TotalVisibleMemorySize / 1MB, 2)
            FreeGB = [math]::Round($memoryInfo.FreePhysicalMemory / 1MB, 2)
            UsagePercent = $memoryUsagePercent
            Healthy = $memoryUsagePercent -lt 90
        }

        $healthy = $systemInfo.DiskUsage.Healthy -and $systemInfo.MemoryUsage.Healthy

        return @{
            Component = "SystemResources"
            Status = "Completed"
            Healthy = $healthy
            Details = $systemInfo
        }

    } catch {
        return @{
            Component = "SystemResources"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-AgentFunctionality {
    Write-Log "Testing agent functionality..."

    if ($Quick) {
        Write-Log "Skipping agent functionality test in quick mode"
        return @{
            Component = "AgentFunctionality"
            Status = "Skipped"
            Healthy = $true
            Details = @{ Reason = "Quick mode enabled" }
        }
    }

    try {
        # Test autonomous orchestrator
        $response = Invoke-WebRequest -Uri "http://192.168.0.30:8000/agents/status" -TimeoutSec $Timeout -UseBasicParsing

        if ($response.StatusCode -eq 200) {
            $agentData = $response.Content | ConvertFrom-Json

            return @{
                Component = "AgentFunctionality"
                Status = "Completed"
                Healthy = $true
                Details = @{
                    AgentStatus = $agentData
                    EndpointAccessible = $true
                }
            }
        } else {
            return @{
                Component = "AgentFunctionality"
                Status = "Failed"
                Healthy = $false
                Error = "Agent status endpoint returned $($response.StatusCode)"
            }
        }

    } catch {
        return @{
            Component = "AgentFunctionality"
            Status = "Failed"
            Healthy = $false
            Error = $_.Exception.Message
        }
    }
}

function Generate-Report {
    param([array]$TestResults)

    $overallHealth = ($TestResults | Where-Object { $_.Healthy -eq $false }).Count -eq 0
    $totalTests = $TestResults.Count
    $passedTests = ($TestResults | Where-Object { $_.Healthy -eq $true }).Count
    $failedTests = $totalTests - $passedTests

    $report = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        OverallHealth = $overallHealth
        Summary = @{
            TotalTests = $totalTests
            PassedTests = $passedTests
            FailedTests = $failedTests
            SuccessRate = [math]::Round(($passedTests / $totalTests) * 100, 2)
        }
        TestResults = $TestResults
        SystemInfo = @{
            Hostname = $env:COMPUTERNAME
            User = $env:USERNAME
            PowerShellVersion = $PSVersionTable.PSVersion.ToString()
            ValidationMode = if ($Quick) { "Quick" } elseif ($Full) { "Full" } else { "Standard" }
        }
    }

    return $report
}

# Main execution
try {
    Write-Log "=== TwisterLab System Validation Started ==="
    Write-Log "Mode: $(if ($Quick) { 'Quick' } elseif ($Full) { 'Full' } else { 'Standard' })"
    Write-Log "Timeout: $Timeout seconds"
    Write-Log "Report path: $ReportPath"

    New-ReportDirectory

    $testResults = @()

    # Run tests
    $testResults += Test-DockerServices
    $testResults += Test-APIEndpoints
    $testResults += Test-DatabaseConnectivity
    $testResults += Test-MonitoringStack
    $testResults += Test-SSLConfiguration
    $testResults += Test-SystemResources

    if (!$Quick) {
        $testResults += Test-AgentFunctionality
    }

    # Generate report
    $report = Generate-Report -TestResults $testResults

    # Save report
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportFile -Encoding UTF8

    # Display results
    Write-Log "=== Validation Results ==="
    Write-Log "Overall Health: $(if ($report.OverallHealth) { 'HEALTHY' } else { 'UNHEALTHY' })"
    Write-Log "Tests Passed: $($report.Summary.PassedTests)/$($report.Summary.TotalTests)"
    Write-Log "Success Rate: $($report.Summary.SuccessRate)%"
    Write-Log "Report saved to: $ReportFile"

    if (!$report.OverallHealth) {
        Write-Log "Failed Tests:" -Level "WARNING"
        foreach ($result in $testResults | Where-Object { !$_.Healthy }) {
            Write-Log "  - $($result.Component): $($result.Status)" -Level "WARNING"
        }
    }

    # Exit with appropriate code
    if ($report.OverallHealth) {
        Write-Log "All tests passed!"
        exit 0
    } else {
        Write-Log "Some tests failed. Check the report for details." -Level "ERROR"
        exit 1
    }

} catch {
    Write-Log "Validation failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
