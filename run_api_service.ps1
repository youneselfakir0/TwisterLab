#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Windows service wrapper for TwisterLab API
.DESCRIPTION
    Runs the TwisterLab API as a Windows service using the local Python installation
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "start",
    [Parameter(Mandatory=$false)]
    [string]$PythonPath = "python.exe"
)

$ServiceName = "TwisterLabAPI"
$ScriptPath = "$PSScriptRoot\api\main.py"
$LogPath = "$PSScriptRoot\logs\api_service.log"
$ErrorLogPath = "$PSScriptRoot\logs\api_service_error.log"

# Ensure log directory exists
$LogDir = Split-Path $LogPath -Parent
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force
}

function Write-ServiceLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Add-Content -Path $LogPath -Value $LogMessage
    Write-Host $LogMessage
}

function Test-PythonEnvironment {
    Write-ServiceLog "Testing Python environment..."
    Write-ServiceLog "Current directory: $PSScriptRoot"
    Write-ServiceLog "PATH: $env:PATH"

    # Try to find Python in common locations
    $pythonCandidates = @(
        "python.exe",
        "python3.exe",
        "$env:USERPROFILE\anaconda3\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe"
    )

    foreach ($candidate in $pythonCandidates) {
        Write-ServiceLog "Testing Python candidate: $candidate"
        if (Test-Path $candidate) {
            $script:PythonPath = $candidate
            Write-ServiceLog "Found Python at: $candidate"
            break
        }
        else {
            Write-ServiceLog "Not found: $candidate"
        }
    }

    Write-ServiceLog "Selected Python path: $PythonPath"

    if (!(Test-Path $PythonPath)) {
        Write-ServiceLog "ERROR: Python executable not found at $PythonPath" "ERROR"
        throw "Python executable not found. Please install Python or specify the correct path."
    }

    if (!(Test-Path $PythonPath)) {
        throw "Python executable not found. Please install Python or specify the correct path."
    }

    # Test Python execution
    try {
        $version = & $PythonPath --version 2>&1
        Write-ServiceLog "Python found: $PythonPath - $version"
    }
    catch {
        throw "Cannot execute Python: $($_.Exception.Message)"
    }

    # Test required packages
    $testScript = @"
import sys
try:
    import fastapi, uvicorn, pydantic
    print("Dependencies OK")
except ImportError as e:
    print(f"Missing dependencies: {e}")
    sys.exit(1)
"@

    $testResult = & $PythonPath -c $testScript 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ServiceLog "Installing missing dependencies..."
        & $PythonPath -m pip install fastapi uvicorn pydantic --quiet
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
    }

    Write-ServiceLog "Python environment ready"
}

function Start-TwisterLabAPI {
    Write-ServiceLog "Starting TwisterLab API service..."

    try {
        Test-PythonEnvironment

        if (!(Test-Path $ScriptPath)) {
            throw "API script not found: $ScriptPath"
        }

        # Set environment variables
        $env:ENVIRONMENT = "production"
        $env:DATABASE_URL = "postgresql://twisterlab:twisterlab_prod_db_password_2024!@localhost:5432/twisterlab_prod"
        $env:REDIS_URL = "redis://localhost:6379"

        Write-ServiceLog "Starting API on port 8000..."

        # Start the API in background
        $process = Start-Process -FilePath $PythonPath `
                                -ArgumentList $ScriptPath `
                                -WorkingDirectory $PSScriptRoot `
                                -RedirectStandardOutput $LogPath `
                                -RedirectStandardError $ErrorLogPath `
                                -NoNewWindow `
                                -PassThru

        Write-ServiceLog "API service started with PID: $($process.Id)"

        # Wait a moment and check if it's still running
        Start-Sleep -Seconds 3
        if (!$process.HasExited) {
            Write-ServiceLog "API service is running successfully"
            return $process.Id
        }
        else {
            $errorContent = Get-Content $ErrorLogPath -Raw
            throw "API service exited immediately. Error: $errorContent"
        }

    }
    catch {
        Write-ServiceLog "Failed to start API service: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Stop-TwisterLabAPI {
    Write-ServiceLog "Stopping TwisterLab API service..."

    try {
        # Find and stop Python processes running the API
        $apiProcesses = Get-Process | Where-Object {
            $_.ProcessName -eq "python" -and
            $_.CommandLine -like "*main.py*"
        }

        if ($apiProcesses) {
            foreach ($process in $apiProcesses) {
                Write-ServiceLog "Stopping process PID: $($process.Id)"
                Stop-Process -Id $process.Id -Force
            }
            Write-ServiceLog "API service stopped"
        }
        else {
            Write-ServiceLog "No API processes found running"
        }
    }
    catch {
        Write-ServiceLog "Error stopping API service: $($_.Exception.Message)" "ERROR"
    }
}

function Get-ServiceStatus {
    $apiProcesses = Get-Process | Where-Object {
        $_.ProcessName -eq "python" -and
        $_.CommandLine -like "*main.py*"
    }

    if ($apiProcesses) {
        Write-ServiceLog "API service is running (PID: $($apiProcesses[0].Id))"
        return $true
    }
    else {
        Write-ServiceLog "API service is not running"
        return $false
    }
}

# Main execution
switch ($Action.ToLower()) {
    "start" {
        try {
            $pid = Start-TwisterLabAPI
            Write-ServiceLog "TwisterLab API started successfully (PID: $pid)"
        }
        catch {
            Write-ServiceLog "Failed to start TwisterLab API: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }
    "stop" {
        Stop-TwisterLabAPI
    }
    "restart" {
        Stop-TwisterLabAPI
        Start-Sleep -Seconds 2
        Start-TwisterLabAPI
    }
    "status" {
        Get-ServiceStatus
    }
    default {
        Write-Host "Usage: .\run_api_service.ps1 -Action {start|stop|restart|status} [-PythonPath <path>]"
        exit 1
    }
}
