# TwisterLab Maintenance Orchestrator
# Version: 1.0.0
# Date: 2025-11-15

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("backup", "restore", "validate", "monitor", "maintenance", "full-check")]
    [string]$Action,
    [string]$BackupName,
    [switch]$Full,
    [switch]$Compress,
    [switch]$DryRun,
    [switch]$Silent,
    [int]$RetentionDays = 7,
    [string]$ReportPath = "$env:USERPROFILE\TwisterLab_Maintenance_Reports"
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$ReportPath\maintenance_$Timestamp.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    if (!$Silent) {
        Write-Host $LogMessage
    }
    Add-Content -Path $LogFile -Value $LogMessage
}

function New-ReportDirectory {
    if (!(Test-Path $ReportPath)) {
        New-Item -ItemType Directory -Path $ReportPath -Force | Out-Null
    }
}

function Invoke-Backup {
    param([switch]$Full, [switch]$Compress, [int]$RetentionDays)

    Write-Log "=== Starting Backup Operation ==="

    $backupScript = Join-Path $ScriptPath "backup.ps1"
    if (!(Test-Path $backupScript)) {
        throw "Backup script not found: $backupScript"
    }

    $args = @()
    if ($Full) { $args += "-Full" }
    if ($Compress) { $args += "-Compress" }
    $args += "-RetentionDays", $RetentionDays

    Write-Log "Executing: $backupScript $($args -join ' ')"
    $result = & $backupScript @args

    if ($LASTEXITCODE -eq 0) {
        Write-Log "Backup completed successfully"
        return @{ Success = $true; Output = $result }
    } else {
        Write-Log "Backup failed with exit code $LASTEXITCODE" -Level "ERROR"
        return @{ Success = $false; Output = $result; ExitCode = $LASTEXITCODE }
    }
}

function Invoke-Restore {
    param([Parameter(Mandatory=$true)][string]$BackupName, [switch]$DryRun)

    Write-Log "=== Starting Restore Operation ==="
    Write-Log "Backup name: $BackupName"
    Write-Log "Dry run: $DryRun"

    $restoreScript = Join-Path $ScriptPath "restore.ps1"
    if (!(Test-Path $restoreScript)) {
        throw "Restore script not found: $restoreScript"
    }

    $args = @("-BackupName", $BackupName)
    if ($DryRun) { $args += "-DryRun" }

    Write-Log "Executing: $restoreScript $($args -join ' ')"
    $result = & $restoreScript @args

    if ($LASTEXITCODE -eq 0) {
        Write-Log "Restore completed successfully"
        return @{ Success = $true; Output = $result }
    } else {
        Write-Log "Restore failed with exit code $LASTEXITCODE" -Level "ERROR"
        return @{ Success = $false; Output = $result; ExitCode = $LASTEXITCODE }
    }
}

function Invoke-Validation {
    param([switch]$Full, [switch]$Silent)

    Write-Log "=== Starting Validation Operation ==="

    $validateScript = Join-Path $ScriptPath "validate.ps1"
    if (!(Test-Path $validateScript)) {
        throw "Validation script not found: $validateScript"
    }

    $args = @()
    if ($Full) { $args += "-Full" }
    if ($Silent) { $args += "-Silent" }

    Write-Log "Executing: $validateScript $($args -join ' ')"
    $result = & $validateScript @args

    $success = $LASTEXITCODE -eq 0
    if ($success) {
        Write-Log "Validation completed successfully"
    } else {
        Write-Log "Validation failed with exit code $LASTEXITCODE" -Level "ERROR"
    }

    return @{ Success = $success; Output = $result; ExitCode = $LASTEXITCODE }
}

function Invoke-Monitoring {
    Write-Log "=== Starting Monitoring Check ==="

    $monitorScript = Join-Path $ScriptPath "monitor.ps1"
    if (!(Test-Path $monitorScript)) {
        throw "Monitor script not found: $monitorScript"
    }

    Write-Log "Executing: $monitorScript"
    $result = & $monitorScript

    $success = $LASTEXITCODE -eq 0
    if ($success) {
        Write-Log "Monitoring check completed successfully"
    } else {
        Write-Log "Monitoring check failed with exit code $LASTEXITCODE" -Level "ERROR"
    }

    return @{ Success = $success; Output = $result; ExitCode = $LASTEXITCODE }
}

function Invoke-FullMaintenance {
    Write-Log "=== Starting Full Maintenance Cycle ==="

    $results = @{}

    # Step 1: Pre-maintenance validation
    Write-Log "Step 1: Pre-maintenance validation"
    $results.PreValidation = Invoke-Validation -Silent:$Silent

    if (!$results.PreValidation.Success) {
        Write-Log "Pre-maintenance validation failed. Aborting maintenance." -Level "ERROR"
        return @{ Success = $false; Results = $results; Error = "Pre-validation failed" }
    }

    # Step 2: Backup
    Write-Log "Step 2: Creating backup"
    $results.Backup = Invoke-Backup -Full -Compress -RetentionDays $RetentionDays

    if (!$results.Backup.Success) {
        Write-Log "Backup failed. Maintenance aborted." -Level "ERROR"
        return @{ Success = $false; Results = $results; Error = "Backup failed" }
    }

    # Step 3: System monitoring check
    Write-Log "Step 3: System monitoring check"
    $results.Monitoring = Invoke-Monitoring

    # Step 4: Post-maintenance validation
    Write-Log "Step 4: Post-maintenance validation"
    $results.PostValidation = Invoke-Validation -Full -Silent:$Silent

    # Step 5: Generate maintenance report
    Write-Log "Step 5: Generating maintenance report"
    $maintenanceReport = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        MaintenanceType = "Full"
        OverallSuccess = ($results.Values | Where-Object { $_.Success -eq $false }).Count -eq 0
        Steps = $results
        SystemInfo = @{
            Hostname = $env:COMPUTERNAME
            User = $env:USERNAME
            PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        }
    }

    $reportFile = "$ReportPath\maintenance_report_$Timestamp.json"
    $maintenanceReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8

    Write-Log "Maintenance report saved to: $reportFile"

    $overallSuccess = $maintenanceReport.OverallSuccess
    if ($overallSuccess) {
        Write-Log "Full maintenance cycle completed successfully"
    } else {
        Write-Log "Full maintenance cycle completed with issues" -Level "WARNING"
    }

    return @{
        Success = $overallSuccess
        Results = $results
        ReportPath = $reportFile
    }
}

function Invoke-FullSystemCheck {
    Write-Log "=== Starting Full System Check ==="

    $results = @{}

    # Run validation
    $results.Validation = Invoke-Validation -Full

    # Run monitoring
    $results.Monitoring = Invoke-Monitoring

    # Check backup status
    Write-Log "Checking backup status..."
    $backupPath = "$env:USERPROFILE\TwisterLab_Backups"
    if (Test-Path $backupPath) {
        $latestBackup = Get-ChildItem $backupPath -File |
            Where-Object { $_.Name -match '^twisterlab_backup_' } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestBackup) {
            $backupAge = (Get-Date) - $latestBackup.LastWriteTime
            $results.BackupStatus = @{
                LatestBackup = $latestBackup.Name
                BackupAgeDays = [math]::Round($backupAge.TotalDays, 1)
                BackupAgeHours = [math]::Round($backupAge.TotalHours, 1)
                IsRecent = $backupAge.TotalDays -lt 1
            }
        } else {
            $results.BackupStatus = @{
                Status = "No backups found"
                IsRecent = $false
            }
        }
    } else {
        $results.BackupStatus = @{
            Status = "Backup directory not found"
            IsRecent = $false
        }
    }

    # Generate system check report
    $systemReport = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        CheckType = "FullSystemCheck"
        OverallHealth = ($results.Validation.Success -and $results.Monitoring.Success -and $results.BackupStatus.IsRecent)
        Components = $results
        Recommendations = @()
    }

    # Generate recommendations
    if (!$results.Validation.Success) {
        $systemReport.Recommendations += "Run validation to identify system issues"
    }
    if (!$results.Monitoring.Success) {
        $systemReport.Recommendations += "Check monitoring alerts and resolve issues"
    }
    if (!$results.BackupStatus.IsRecent) {
        $systemReport.Recommendations += "Create a recent backup of the system"
    }

    $reportFile = "$ReportPath\system_check_$Timestamp.json"
    $systemReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8

    Write-Log "System check report saved to: $reportFile"
    Write-Log "Overall system health: $(if ($systemReport.OverallHealth) { 'HEALTHY' } else { 'NEEDS ATTENTION' })"

    if ($systemReport.Recommendations.Count -gt 0) {
        Write-Log "Recommendations:" -Level "WARNING"
        foreach ($rec in $systemReport.Recommendations) {
            Write-Log "  - $rec" -Level "WARNING"
        }
    }

    return @{
        Success = $systemReport.OverallHealth
        Results = $results
        ReportPath = $reportFile
        Recommendations = $systemReport.Recommendations
    }
}

# Main execution
try {
    Write-Log "=== TwisterLab Maintenance Orchestrator Started ==="
    Write-Log "Action: $Action"
    Write-Log "Timestamp: $Timestamp"

    New-ReportDirectory

    $result = $null

    switch ($Action) {
        "backup" {
            $result = Invoke-Backup -Full:$Full -Compress:$Compress -RetentionDays $RetentionDays
        }
        "restore" {
            if (!$BackupName) {
                throw "BackupName parameter is required for restore action"
            }
            $result = Invoke-Restore -BackupName $BackupName -DryRun:$DryRun
        }
        "validate" {
            $result = Invoke-Validation -Full:$Full -Silent:$Silent
        }
        "monitor" {
            $result = Invoke-Monitoring
        }
        "maintenance" {
            $result = Invoke-FullMaintenance
        }
        "full-check" {
            $result = Invoke-FullSystemCheck
        }
    }

    Write-Log "=== Operation Completed ==="
    Write-Log "Success: $($result.Success)"

    if ($result.ReportPath) {
        Write-Log "Report saved to: $($result.ReportPath)"
    }

    if ($result.Recommendations -and $result.Recommendations.Count -gt 0) {
        Write-Log "Recommendations:" -Level "INFO"
        foreach ($rec in $result.Recommendations) {
            Write-Log "  - $rec" -Level "INFO"
        }
    }

    # Exit with appropriate code
    if ($result.Success) {
        exit 0
    } else {
        exit 1
    }

} catch {
    Write-Log "Maintenance orchestrator failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
