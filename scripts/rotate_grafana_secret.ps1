<#
Rotate the `grafana_admin_password` Docker Swarm secret and optionally update provisioning files.
Usage: .\scripts\rotate_grafana_secret.ps1 [-DryRun] [-Force] [-RestartService]
#>
param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$RestartService,
    [string]$ServiceName = "",
    [string]$TestServiceList = "",
    [string]$TestServicePortMap = ""
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
    # In dry-run mode, do not actually create or update the Docker secret or restart services,
    # but we'll still perform detection and report which service would be restarted.
    $isDryRun = $true
} else {
    $isDryRun = $false
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker CLI not found in PATH. Skipping secret rotation." -ForegroundColor Red
    exit 1
}

try {
    if (-not $isDryRun) {
        if ($Force) { docker secret rm grafana_admin_password 2>$null | Out-Null }
        $tmpFile = [System.IO.Path]::GetTempFileName()
        [System.IO.File]::WriteAllText($tmpFile, $newPass)
        docker secret create grafana_admin_password $tmpFile
        Remove-Item $tmpFile -Force
    }
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
                if ($TestServiceList -and $TestServiceList -ne "") {
                    $svcListRaw = $TestServiceList
                } else {
                    $svcListRaw = docker service ls --format "{{.Name}}" 2>$null
                }
                if ($svcListRaw) {
                    # Split on newline or comma for test/service-list input
                    $services = $svcListRaw -split '[,\r\n]' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
                    $candidates = @($services | Where-Object { $_ -match '(?i:grafana)' })
                    if ($candidates.Count -gt 1) {
                        # Prefer a candidate with port 3000 or stack/owner prefix 'twisterlab' if present
                        # Build a port map from input (format: svc1:3000,svc2:80)
                        $portMap = @{}
                        if ($TestServicePortMap -and $TestServicePortMap -ne "") {
                            $pairs = $TestServicePortMap -split ','
                            foreach ($pair in $pairs) {
                                $parts = $pair -split ':'
                                if ($parts.Length -eq 2) { $portMap[$parts[0]] = [int]$parts[1] }
                            }
                        }
                        $preferred = $null
                        foreach ($c in @($candidates)) {
                            $has3000 = $false
                            if ($portMap.ContainsKey($c) -and $portMap[$c] -eq 3000) { $has3000 = $true }
                            else {
                                # Attempt to inspect the service for ports; ignore errors
                                try {
                                    $json = docker service inspect $c --format '{{json .Endpoint.Ports}}' 2>$null
                                    if ($json -and $json -ne 'null') {
                                        if ($json -match '3000') { $has3000 = $true }
                                    }
                                } catch { }
                            }
                            if ($has3000) { $preferred = $c; break }
                        }
                            if ($preferred) { $svc = $preferred } else {
                            $preferred = @($candidates | Where-Object { $_ -match '(?i:twisterlab).*grafana' })
                            if ($preferred) { $svc = $preferred[0] } else { $svc = @($candidates)[0] }
                        }
                    } elseif (@($candidates).Count -eq 1) {
                        $svc = @($candidates)[0]
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
                    if ($TestServiceList -and $TestServiceList -ne "") {
                        $psRaw = $TestServiceList
                    } else {
                        $psRaw = docker ps --format "{{.Names}}" 2>$null
                    }
                    if ($psRaw) {
                        $containers = $psRaw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
                        $candidates = $containers | Where-Object { $_ -match '(?i:grafana)' }
                        if (@($candidates).Count -ge 1) { $svc = @($candidates)[0] }
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
            if ($isDryRun) {
                Write-Host "DRY RUN: would restart service ${svc}" -ForegroundColor Yellow
            } else {
                try {
                    docker service update --force $svc 2>$null | Out-Null
                    Write-Host "Restarted service ${svc}" -ForegroundColor Green
                } catch {
                    Write-Host "Failed to restart service ${svc}: $($_.Exception.Message)" -ForegroundColor Red
                }
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
