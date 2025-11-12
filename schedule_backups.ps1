#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Schedule automated backups for TwisterLab system
.DESCRIPTION
    Creates Windows Task Scheduler tasks for automated backups
.NOTES
    Run as Administrator
#>

param(
    [string]$BackupPath = "C:\TwisterLab\backups",
    [string]$TaskUser = "SYSTEM"
)

$ScriptPath = "C:\TwisterLab\backup_system.ps1"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "C:\TwisterLab\backup_schedule.log" -Value $logMessage
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."

    if (!(Test-Path $ScriptPath)) {
        Write-Log "Backup script not found: $ScriptPath" "ERROR"
        return $false
    }

    if (!(Test-Path $BackupPath)) {
        Write-Log "Creating backup directory: $BackupPath"
        New-Item -ItemType Directory -Path $BackupPath -Force
    }

    return $true
}

function New-DailyBackupTask {
    Write-Log "Creating daily backup task..."

    try {
        $taskName = "TwisterLab Daily Backup"

        # Remove existing task
        if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        }

        # Create new task
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -BackupPath `"$BackupPath`""
        $trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $principal = New-ScheduledTaskPrincipal -UserId $TaskUser -LogonType ServiceAccount

        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automated daily backup of TwisterLab system at 2:00 AM"

        Write-Log "Daily backup task created successfully"
        return $true
    }
    catch {
        Write-Log "Failed to create daily backup task: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function New-WeeklyBackupTask {
    Write-Log "Creating weekly backup task..."

    try {
        $taskName = "TwisterLab Weekly Backup"

        # Remove existing task
        if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        }

        # Create new task
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -BackupPath `"$BackupPath`" -Compress `$true"
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "03:00"
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $principal = New-ScheduledTaskPrincipal -UserId $TaskUser -LogonType ServiceAccount

        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automated weekly full backup of TwisterLab system every Sunday at 3:00 AM"

        Write-Log "Weekly backup task created successfully"
        return $true
    }
    catch {
        Write-Log "Failed to create weekly backup task: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-Status {
    Write-Log "=== Scheduled Tasks Status ==="

    $tasks = Get-ScheduledTask | Where-Object { $_.TaskName -like "*TwisterLab*" }

    foreach ($task in $tasks) {
        Write-Log "Task: $($task.TaskName)"
        Write-Log "  State: $($task.State)"
        Write-Log "  Next Run: $($task.NextRunTime)"
        Write-Log "  Last Run: $($task.LastRunTime)"
        Write-Log "  Last Result: $($task.LastTaskResult)"
    }
}

# Main process
Write-Log "=== Starting TwisterLab Backup Scheduling ==="

if (!(Test-Prerequisites)) {
    Write-Log "Prerequisites not met. Exiting." "ERROR"
    exit 1
}

$dailySuccess = New-DailyBackupTask
$weeklySuccess = New-WeeklyBackupTask

$overallSuccess = $dailySuccess -and $weeklySuccess

Write-Log "=== Backup Scheduling Completed ==="
Write-Log "Overall status: $(if ($overallSuccess) { "SUCCESS" } else { "PARTIAL SUCCESS" })"

if ($overallSuccess) {
    Write-Host "✅ Automated backup system scheduled successfully!" -ForegroundColor Green
    Write-Host "📅 Daily backups at 2:00 AM" -ForegroundColor Cyan
    Write-Host "📅 Weekly backups every Sunday at 3:00 AM" -ForegroundColor Cyan
}

Show-Status

exit $(if ($overallSuccess) { 0 } else { 1 })
