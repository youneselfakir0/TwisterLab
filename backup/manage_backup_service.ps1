# TwisterLab Backup Service Management Script
# Manages the automated backup system for production

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "status", "logs", "manual", "stats")]
    [string]$Action = "status",

    [Parameter(Mandatory=$false)]
    [ValidateSet("database", "config", "logs", "full_system")]
    [string]$BackupType,

    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Configuration
$BackupServiceName = "TwisterLab-Backup"
$PythonPath = "python"
$BackupScript = Join-Path $PSScriptRoot "start_backup_service.py"
$LogFile = Join-Path $PSScriptRoot "logs\backup_service.log"

function Write-Header {
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  TwisterLab Backup Service Manager" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    # Check if Python is available
    try {
        $pythonVersion = & $PythonPath --version 2>$null
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
        exit 1
    }

    # Check if backup script exists
    if (-not (Test-Path $BackupScript)) {
        Write-Host "✗ Backup script not found: $BackupScript" -ForegroundColor Red
        exit 1
    }

    # Check if required directories exist
    $dirs = @("logs", "backup")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✓ Created directory: $dir" -ForegroundColor Green
        }
    }
}

function Start-BackupService {
    Write-Host "Starting TwisterLab Backup Service..." -ForegroundColor Yellow

    # Check if service is already running
    $existingProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*start_backup_service.py*" }

    if ($existingProcess) {
        Write-Host "✗ Backup service is already running (PID: $($existingProcess.Id))" -ForegroundColor Red
        if (-not $Force) {
            Write-Host "Use -Force to restart the service" -ForegroundColor Yellow
            return
        } else {
            Write-Host "Stopping existing service..." -ForegroundColor Yellow
            Stop-Process -Id $existingProcess.Id -Force
            Start-Sleep -Seconds 2
        }
    }

    # Start the service in background
    try {
        $process = Start-Process -FilePath $PythonPath -ArgumentList $BackupScript -NoNewWindow -PassThru
        Write-Host "✓ Backup service started (PID: $($process.Id))" -ForegroundColor Green

        # Wait a moment and check if it's still running
        Start-Sleep -Seconds 3
        $runningProcess = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
        if ($runningProcess) {
            Write-Host "✓ Service is running successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Service failed to start. Check logs for details." -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Failed to start backup service: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-BackupService {
    Write-Host "Stopping TwisterLab Backup Service..." -ForegroundColor Yellow

    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*start_backup_service.py*" }

    if ($processes) {
        foreach ($process in $processes) {
            Write-Host "Stopping process (PID: $($process.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force
        }
        Write-Host "✓ Backup service stopped" -ForegroundColor Green
    } else {
        Write-Host "ℹ Backup service is not running" -ForegroundColor Yellow
    }
}

function Get-BackupServiceStatus {
    Write-Host "Backup Service Status:" -ForegroundColor Cyan
    Write-Host "----------------------" -ForegroundColor Cyan

    # Check if process is running
    $process = Get-Process -Name "python" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*start_backup_service.py*" }

    if ($process) {
        Write-Host "Status: Running" -ForegroundColor Green
        Write-Host "PID: $($process.Id)" -ForegroundColor White
        Write-Host "CPU Time: $($process.CPU)" -ForegroundColor White
        Write-Host "Memory: $([math]::Round($process.WorkingSet / 1MB, 2)) MB" -ForegroundColor White
        Write-Host "Start Time: $($process.StartTime)" -ForegroundColor White
    } else {
        Write-Host "Status: Stopped" -ForegroundColor Red
    }

    # Show recent log entries
    Write-Host ""
    Write-Host "Recent Log Entries:" -ForegroundColor Cyan
    Write-Host "-------------------" -ForegroundColor Cyan

    if (Test-Path $LogFile) {
        Get-Content $LogFile -Tail 5 -ErrorAction SilentlyContinue
    } else {
        Write-Host "No log file found" -ForegroundColor Yellow
    }
}

function Show-BackupLogs {
    if (Test-Path $LogFile) {
        Write-Host "Backup Service Logs:" -ForegroundColor Cyan
        Write-Host "====================" -ForegroundColor Cyan
        Get-Content $LogFile -Wait
    } else {
        Write-Host "Log file not found: $LogFile" -ForegroundColor Red
    }
}

function Invoke-ManualBackup {
    if (-not $BackupType) {
        Write-Host "✗ Backup type is required for manual backup" -ForegroundColor Red
        Write-Host "Available types: database, config, logs, full_system" -ForegroundColor Yellow
        return
    }

    Write-Host "Starting manual backup: $BackupType" -ForegroundColor Yellow

    try {
        & $PythonPath (Join-Path $PSScriptRoot "automated_backup.py") manual $BackupType
    } catch {
        Write-Host "✗ Manual backup failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-BackupStats {
    Write-Host "Backup Statistics:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan

    try {
        & $PythonPath (Join-Path $PSScriptRoot "automated_backup.py") stats
    } catch {
        Write-Host "✗ Failed to get backup stats: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
Write-Header
Test-Prerequisites

switch ($Action) {
    "start" {
        Start-BackupService
    }
    "stop" {
        Stop-BackupService
    }
    "status" {
        Get-BackupServiceStatus
    }
    "logs" {
        Show-BackupLogs
    }
    "manual" {
        Invoke-ManualBackup
    }
    "stats" {
        Show-BackupStats
    }
    default {
        Write-Host "Usage: .\manage_backup_service.ps1 -Action <action> [-BackupType <type>] [-Force]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Cyan
        Write-Host "  start   - Start the backup service" -ForegroundColor White
        Write-Host "  stop    - Stop the backup service" -ForegroundColor White
        Write-Host "  status  - Show service status" -ForegroundColor White
        Write-Host "  logs    - Show service logs" -ForegroundColor White
        Write-Host "  manual  - Run manual backup (requires -BackupType)" -ForegroundColor White
        Write-Host "  stats   - Show backup statistics" -ForegroundColor White
        Write-Host ""
        Write-Host "Backup Types:" -ForegroundColor Cyan
        Write-Host "  database    - Database backup" -ForegroundColor White
        Write-Host "  config      - Configuration backup" -ForegroundColor White
        Write-Host "  logs        - Log backup" -ForegroundColor White
        Write-Host "  full_system - Full system backup" -ForegroundColor White
    }
}
