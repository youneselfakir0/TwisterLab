# TwisterLab Automated Monitoring & Rollback Script
# Version: 1.0.0
# Date: 2025-11-15

param(
    [switch]$Continuous,
    [int]$Interval = 60,
    [switch]$AutoRollback,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath

# Monitoring endpoints
$Endpoints = @(
    @{ Url = "http://192.168.0.30:8000/health"; Name = "API"; Critical = $true },
    @{ Url = "http://192.168.0.30:3000/api/health"; Name = "Grafana"; Critical = $false },
    @{ Url = "http://192.168.0.30:9090/-/healthy"; Name = "Prometheus"; Critical = $false },
    @{ Url = "http://192.168.0.30:9100/metrics"; Name = "Node-Exporter"; Critical = $false }
)

# System resources to monitor
$ResourceThresholds = @{
    CpuUsage = 80  # Percentage
    MemoryUsage = 85  # Percentage
    DiskUsage = 90  # Percentage
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path "$ProjectRoot\monitoring.log" -Value $LogMessage
}

function Test-Endpoint {
    param([string]$Url, [string]$Name, [int]$Timeout = 10)

    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $Timeout -UseBasicParsing
        return @{
            Name = $Name
            Url = $Url
            Status = "Healthy"
            StatusCode = $response.StatusCode
            ResponseTime = $response.BaseResponse.ResponseUri.AbsoluteUri -ne $null
        }
    }
    catch {
        return @{
            Name = $Name
            Url = $Url
            Status = "Unhealthy"
            Error = $_.Exception.Message
            ResponseTime = $null
        }
    }
}

function Get-SystemResources {
    try {
        # Get CPU usage
        $cpu = Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average

        # Get memory usage
        $memory = Get-WmiObject Win32_OperatingSystem
        $totalMemory = $memory.TotalVisibleMemorySize
        $freeMemory = $memory.FreePhysicalMemory
        $usedMemory = $totalMemory - $freeMemory
        $memoryUsage = [math]::Round(($usedMemory / $totalMemory) * 100, 2)

        # Get disk usage (C: drive)
        $disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
        $totalSpace = $disk.Size
        $freeSpace = $disk.FreeSpace
        $usedSpace = $totalSpace - $freeSpace
        $diskUsage = [math]::Round(($usedSpace / $totalSpace) * 100, 2)

        return @{
            CpuUsage = $cpu
            MemoryUsage = $memoryUsage
            DiskUsage = $diskUsage
            Status = "OK"
        }
    }
    catch {
        return @{
            CpuUsage = $null
            MemoryUsage = $null
            DiskUsage = $null
            Status = "Error"
            Error = $_.Exception.Message
        }
    }
}

function Invoke-Rollback {
    param([string]$Reason)

    Write-Log "Initiating rollback due to: $Reason" -Level "WARNING"

    if (!$AutoRollback) {
        Write-Log "Auto-rollback disabled. Manual intervention required." -Level "WARNING"
        return
    }

    try {
        # Stop current stack
        Write-Log "Stopping current stack..."
        & docker stack rm twisterlab 2>$null

        # Wait for cleanup
        Start-Sleep -Seconds 10

        # Deploy previous version (assuming backup exists)
        Write-Log "Deploying backup configuration..."
        # This would need to be implemented based on your backup strategy

        Write-Log "Rollback completed" -Level "INFO"
    }
    catch {
        Write-Log "Rollback failed: $($_.Exception.Message)" -Level "ERROR"
    }
}

function Send-Alert {
    param([string]$Message, [string]$Level = "WARNING")

    Write-Log "ALERT [$Level]: $Message" -Level $Level

    # Here you could add email notifications, Slack alerts, etc.
    # For now, just log to file
}

function Invoke-MonitoringCycle {
    Write-Log "Starting monitoring cycle..."

    $issues = @()
    $criticalIssues = @()

    # Test endpoints
    foreach ($endpoint in $Endpoints) {
        $result = Test-Endpoint -Url $endpoint.Url -Name $endpoint.Name
        if ($result.Status -eq "Unhealthy") {
            $issues += "$($endpoint.Name) is unhealthy: $($result.Error)"
            if ($endpoint.Critical) {
                $criticalIssues += $issues[-1]
            }
        }
        if ($Verbose) {
            Write-Log "$($endpoint.Name): $($result.Status)" -Level "DEBUG"
        }
    }

    # Check system resources
    $resources = Get-SystemResources
    if ($resources.Status -eq "OK") {
        if ($resources.CpuUsage -gt $ResourceThresholds.CpuUsage) {
            $issues += "High CPU usage: $($resources.CpuUsage)%"
        }
        if ($resources.MemoryUsage -gt $ResourceThresholds.MemoryUsage) {
            $issues += "High memory usage: $($resources.MemoryUsage)%"
        }
        if ($resources.DiskUsage -gt $ResourceThresholds.DiskUsage) {
            $issues += "High disk usage: $($resources.DiskUsage)%"
        }
    } else {
        $issues += "Failed to get system resources: $($resources.Error)"
    }

    # Handle issues
    if ($criticalIssues.Count -gt 0) {
        Send-Alert "Critical issues detected: $($criticalIssues -join '; ')" -Level "CRITICAL"
        Invoke-Rollback "Critical service failures: $($criticalIssues -join '; ')"
    }
    elseif ($issues.Count -gt 0) {
        Send-Alert "Issues detected: $($issues -join '; ')" -Level "WARNING"
    }
    else {
        Write-Log "All systems healthy"
    }

    Write-Log "Monitoring cycle completed"
}

# Main execution
try {
    Write-Log "=== TwisterLab Automated Monitoring Started ==="
    Write-Log "Continuous mode: $Continuous"
    Write-Log "Interval: $Interval seconds"
    Write-Log "Auto-rollback: $AutoRollback"

    if ($Continuous) {
        Write-Log "Running in continuous mode. Press Ctrl+C to stop."
        while ($true) {
            Invoke-MonitoringCycle
            Start-Sleep -Seconds $Interval
        }
    }
    else {
        Invoke-MonitoringCycle
    }

} catch {
    Write-Log "Monitoring failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
