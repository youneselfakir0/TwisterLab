<#
Rotate the `grafana_admin_password` Docker Swarm secret and optionally update provisioning files.
Usage: .\scripts\rotate_grafana_secret.ps1 [-DryRun] [-Force] [-RestartService]
#>
param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$RestartService,
    [string]$ServiceName = ""
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
Write-Host "Generated new password for grafana admin (length=24)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN: grafana_admin_password would be rotate to: $newPass" -ForegroundColor Yellow
    exit 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker CLI not found in PATH. Skipping secret rotation." -ForegroundColor Red
    exit 1
}

try {
    if ($Force) { docker secret rm grafana_admin_password 2>$null | Out-Null }
    $tmpFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tmpFile, $newPass)
    docker secret create grafana_admin_password $tmpFile
    Remove-Item $tmpFile -Force

    if ($RestartService) {
        Write-Host "Restarting Grafana service to pick up new secret" -ForegroundColor Yellow
        # Service name may differ across stacks (e.g., twisterlab_monitoring_grafana, grafana, monitoring_grafana)
        if ($ServiceName -and $ServiceName -ne "") {
            $svc = $ServiceName
            Write-Host "Using provided service name: $svc" -ForegroundColor Cyan
        } else {
            # Attempt to detect service name via Docker Service list
            try {
                $svcListRaw = docker service ls --format "{{.Name}}" 2>$null
                if ($LASTEXITCODE -eq 0 -and $svcListRaw) {
                    $services = $svcListRaw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
                    $candidates = $services | Where-Object { $_ -match '(?i:grafana)' }
                    if ($candidates.Count -gt 1) {
                        # Prefer a service name that contains stack prefix 'twisterlab' if present
                        $preferred = $candidates | Where-Object { $_ -match '(?i:twisterlab).*grafana' }
                        if ($preferred) { $svc = $preferred[0] } else { $svc = $candidates[0] }
                    } elseif ($candidates.Count -eq 1) {
                        $svc = $candidates[0]
                    } else {
                        $svc = ""
                    }
                } else {
                    $svc = ""
                }
            } catch {
                $svc = ""
            }
            if ($svc -eq "") {
                # Fallback: try to detect running container name that looks like grafana
                try {
                    $psRaw = docker ps --format "{{.Names}}" 2>$null
                    if ($LASTEXITCODE -eq 0 -and $psRaw) {
                        $containers = $psRaw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
                        $candidates = $containers | Where-Object { $_ -match '(?i:grafana)' }
                        if ($candidates.Count -ge 1) { $svc = $candidates[0] }
                    }
                } catch { $svc = "" }
            }
            if ($svc -eq "") {
                Write-Host "Could not auto-detect Grafana service name. Skipping service restart." -ForegroundColor Yellow
            } else {
                Write-Host "Auto-detected Grafana service name: $svc" -ForegroundColor Cyan
            }
        }
        if ($svc -and $svc -ne "") {
            try {
                docker service update --force $svc 2>$null | Out-Null
                Write-Host "Restarted service ${svc}" -ForegroundColor Green
            } catch {
                Write-Host "Failed to restart service ${svc}: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }

    $logdir = "logs"
    if (!(Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
    $logFile = Join-Path $logdir "rotate_grafana_$(Get-Date -Format yyyyMMddHHmmss).log"
    "Rotated grafana_admin_password at $(Get-Date)" | Out-File -FilePath $logFile
    Write-Host "Rotated grafana_admin_password and logged to $logFile" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "Failed to rotate grafana_admin_password: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
