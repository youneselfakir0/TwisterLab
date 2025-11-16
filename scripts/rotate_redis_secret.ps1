<#
Rotate the `redis_password` Docker Swarm secret.
Usage: .\scripts\rotate_redis_secret.ps1 [-DryRun] [-Force]
#>
param(
    [switch]$DryRun,
    [switch]$Force
)

function New-SecurePassword([int]$length = 24) {
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

$newPass = New-SecurePassword -length 24
Write-Host "Generated new password for redis (length=24)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN: redis_password would be rotate to: $newPass" -ForegroundColor Yellow
    exit 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker CLI not found in PATH. Skipping secret rotation." -ForegroundColor Red
    exit 1
}

try {
    if ($Force) {
        docker secret rm redis_password 2>$null | Out-Null
    }
    $tmpFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tmpFile, $newPass)
    docker secret create redis_password $tmpFile
    Remove-Item $tmpFile -Force

    $logdir = "logs"
    if (!(Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
    $logFile = Join-Path $logdir "rotate_redis_$(Get-Date -Format yyyyMMddHHmmss).log"
    "Rotated redis_password at $(Get-Date)" | Out-File -FilePath $logFile
    Write-Host "Rotated redis_password and logged to $logFile" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "Failed to rotate redis_password: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
