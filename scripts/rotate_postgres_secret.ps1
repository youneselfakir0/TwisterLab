<#
Rotate the `postgres_password` Docker Swarm secret.
This script will generate a new secure password and rotate the Docker secret.
If `-DryRun` is supplied it will print the new password and not change the Docker secret.

Usage:
  .\scripts\rotate_postgres_secret.ps1 [-DryRun] [-Force]
#>

param(
    [switch]$DryRun,
    [switch]$Force
)

function New-SecurePassword([int]$length = 32) {
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] $length
    $rng.GetBytes($bytes)
    $sb = New-Object System.Text.StringBuilder
    foreach ($b in $bytes) {
        $sb.Append($chars[$b % $chars.Length]) | Out-Null
    }
    return $sb.ToString()
}

$newPass = New-SecurePassword -length 32
Write-Host "Generated new password for postgres (length=32)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN: postgres_password would be rotate to: $newPass" -ForegroundColor Yellow
    exit 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker CLI not found in PATH. Skipping secret rotation." -ForegroundColor Red
    exit 1
}

try {
    if ($Force) {
        docker secret rm postgres_password 2>$null | Out-Null
    }
    # Create the secret via stdin
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($newPass)
    $ms = New-Object System.IO.MemoryStream(,$bytes)
    # Write to a temp file for docker secret create to read
    $tmpFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tmpFile, $newPass)
    docker secret create postgres_password $tmpFile
    Remove-Item $tmpFile -Force

    $logdir = "logs"
    if (!(Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
    $logFile = Join-Path $logdir "rotate_postgres_$(Get-Date -Format yyyyMMddHHmmss).log"
    "Rotated postgres_password at $(Get-Date)" | Out-File -FilePath $logFile
    Write-Host "Rotated postgres_password and logged to $logFile" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "Failed to rotate postgres_password: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
