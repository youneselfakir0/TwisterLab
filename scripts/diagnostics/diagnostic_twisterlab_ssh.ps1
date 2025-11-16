<#
PowerShell: diagnostic_twisterlab_ssh.ps1
Purpose: Run diagnostics against remote Linux servers (CoreRTX and edgeserver) using SSH.
Prerequisites: OpenSSH client installed on running host, SSH keys or passwordless auth configured.
Usage: Run in PowerShell from your workstation as a user with SSH access to remote nodes.
#>

param(
    [string]$user = 'twister',
    [string]$core = '192.168.0.20',
    [string]$edge = '192.168.0.30',
    [string]$sshKey = '' # optional: path to private key
)

## Gather local IPs at script scope for local detection
$LocalIps = @()
try { $LocalIps = Get-NetIPAddress -AddressFamily IPv4 | Select-Object -ExpandProperty IPAddress -ErrorAction SilentlyContinue } catch { $LocalIps = @() }
$LocalIps += '127.0.0.1'

function Invoke-Run {
    param($targetHost, $command)
    # If the target host is a local address, run the command locally
    $isLocal = $false
    if ($null -ne $LocalIps -and $LocalIps -contains $targetHost) { $isLocal = $true }
    if ($targetHost -eq 'localhost' -or $targetHost -eq $env:COMPUTERNAME) { $isLocal = $true }

    if ($isLocal) {
        Write-Host "Running locally: $command"
        try {
            $outLocal = Invoke-Expression -Command $command 2>&1
            return $outLocal
        } catch { return "LOCAL_ERR: $_" }
    } else {
        # Run via ssh if available
        if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
            return "SSH_NOT_AVAILABLE: 'ssh' command not found on this system"
        }
        $sshExe = 'ssh'
        $sshArgs = @()
        if ($sshKey -ne '') { $sshArgs += '-i'; $sshArgs += $sshKey }
        $sshArgs += "$user@$targetHost"
        $sshArgs += '--'
        $sshArgs += $command
        Write-Host "Running remotely ($targetHost): $command"
        try {
            $out = & $sshExe @sshArgs 2>&1
            return $out
        } catch { return "SSH_CALL_ERROR: $_" }
    }
}

Write-Host "--- Diagnostic SSH script started ---" -ForegroundColor Cyan

# Check if SSH is available locally for remote checks
$sshAvailable = $false
if (Get-Command ssh -ErrorAction SilentlyContinue) { $sshAvailable = $true }
Write-Host "Checking SSH connection to CoreRTX ($core)..."
try {
    $out1 = Invoke-Run -targetHost $core -command "echo SSH_OK"
    if ($out1 -match 'SSH_OK') { Write-Host "CoreRTX: LOCAL/SSH OK" -ForegroundColor Green } else { Write-Host "CoreRTX: FAILED - $out1" -ForegroundColor Red }
} catch { Write-Host "CoreRTX: ERROR - $_" }

Write-Host "Checking SSH connection to edgeserver ($edge)..."
try {
    if (-not $sshAvailable) { Write-Host "SSH client not found locally; remote checks will be skipped. Install OpenSSH client or run script from a host with SSH." -ForegroundColor Yellow }
    else {
        $out2 = Invoke-Run -targetHost $edge -command "echo SSH_OK"
        if ($out2 -match 'SSH_OK') { Write-Host "edgeserver: SSH OK" -ForegroundColor Green } else { Write-Host "edgeserver: SSH FAILED - $out2" -ForegroundColor Red }
    }
} catch { Write-Host "edgeserver: ERROR - $_" }

Write-Host "\n-- CoreRTX: Service checks --"
# Ollama (systemd) + port 11434 check
try {
    # CoreRTX may be Windows (Ollama desktop). Try Windows checks (service/process then port)
    if ($LocalIps -contains $core -or $core -eq $env:COMPUTERNAME) {
        # Local Windows: check service or process directly
        try {
            $svc = Get-Service -Name 'ollama' -ErrorAction SilentlyContinue
            if ($svc) { $o1 = $svc.Status } elseif (Get-Process -Name 'ollama' -ErrorAction SilentlyContinue) { $o1 = 'running_process' } else { $o1 = 'not-installed' }
        } catch { $o1 = "error: $_" }
        Write-Host "Ollama status (Windows): $o1"
        $o2 = Invoke-Run -targetHost $core -command "netstat -ano | findstr :11434"
    } else {
        $o1 = Invoke-Run -targetHost $core -command "systemctl is-active ollama || echo 'not-installed'"
        Write-Host "Ollama status (Linux): $o1"
        $o2 = Invoke-Run -targetHost $core -command "ss -tuln | grep :11434 || true"
    }
    if ($o2 -ne '') { Write-Host "Port 11434 listening" -ForegroundColor Green } else { Write-Host "Port 11434 not listening" -ForegroundColor Yellow }
    if ($LocalIps -contains $core -or $core -eq $env:COMPUTERNAME) { $o3 = Invoke-Run -targetHost $core -command "netstat -ano | findstr :11434" } else { $o3 = Invoke-Run -targetHost $core -command "netstat -tuln | grep :11434 || true" }
    if ($o3 -ne '') { Write-Host "netstat: port 11434 listening" -ForegroundColor Green } else { Write-Host "netstat: port 11434 not found" -ForegroundColor Yellow }
} catch { Write-Host "CoreRTX service check failed: $_" }

Write-Host "\n-- edgeserver: Service checks --"
try {
    if ($sshAvailable) { $a1 = Invoke-Run -targetHost $edge -command "systemctl is-active twisterlab-api || echo 'not-installed'" } else { $a1 = 'ssh-not-available' }
        try {
            if ($LocalIps -contains $core -or $core -eq $env:COMPUTERNAME) {
                $logs2 = Get-EventLog -LogName Application -Newest 200 | Where-Object { $_.Message -match 'ollama' }
            } else {
                $logs2 = Invoke-Run -targetHost $core -command "journalctl -u ollama -n 200 --no-pager || true"
            }
            Write-Host $logs2
        } catch { Write-Host "Error collecting Ollama logs: $_" }
    if ($sshAvailable) { $a2 = Invoke-Run -targetHost $edge -command "ss -tuln | grep :8000 || true" } else { $a2 = 'ssh-not-available' }
    if ($a2 -ne '') { Write-Host "Port 8000 listening" -ForegroundColor Green } else { Write-Host "Port 8000 not listening" -ForegroundColor Yellow }
    if ($sshAvailable) { $a3 = Invoke-Run -targetHost $edge -command "netstat -tuln | grep :8000 || true" } else { $a3 = 'ssh-not-available' }
    if ($a3 -ne '') { Write-Host "netstat: port 8000 listening" -ForegroundColor Green } else { Write-Host "netstat: port 8000 not found" -ForegroundColor Yellow }
} catch { Write-Host "edgeserver service check failed: $_" }

Write-Host "\n-- Docker services on edgeserver --"
try {
    if ($sshAvailable) { $d1 = Invoke-Run -targetHost $edge -command "docker service ls --format '{{.Name}} {{.Replicas}} {{.Ports}}' || true" } else { $d1 = 'ssh-not-available' }
    Write-Host $d1
} catch { Write-Host "Docker check failed: $_" }

Write-Host "\n-- Endpoint test via direct curl from workstation --"
try {
    Write-Host "Invoke-RestMethod http://${edge}:8000/health"
    try {
    $c1 = Invoke-RestMethod -Uri "http://${edge}:8000/health" -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
        Write-Host "Edge API health OK" -ForegroundColor Green
    } catch {
        Write-Host "Edge API health non-responsive or error: $_" -ForegroundColor Yellow
    }
} catch { Write-Host "Curl test failed: $_" }

Write-Host "\n-- Endpoint test via remote curl on nodes --"
try {
    if ($LocalIps -contains $core -or $core -eq $env:COMPUTERNAME) {
    $r1 = Invoke-Run -targetHost $core -command "powershell -Command \"(Test-Connection -ComputerName ${edge} -Count 1 -Quiet) -and (Invoke-RestMethod -Uri 'http://${edge}:8000/health' -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop)\""
    } else {
    $r1 = Invoke-Run -targetHost $core -command "curl -s -o /dev/null -w '%{http_code}' http://${edge}:8000/health || echo 'curlfail'"
    }
    Write-Host "Core → edgeserver API: $r1"
} catch { Write-Host "Core → edgeserver curl failed: $_" }

try { $r2 = Invoke-Run -targetHost $edge -command "curl -s -o /dev/null -w '%{http_code}' http://${core}:11434 || echo 'curlfail'"; Write-Host "Edge → Core Ollama: $r2" } catch { Write-Host "Edge → Core curl failed: $_" }

Write-Host "\n-- Connectivity checks --"
try { $p1 = Invoke-Run -targetHost $core -command "powershell -Command \"Test-Connection -ComputerName $edge -Count 2 -Quiet\""; Write-Host "Core → Edge ping: $p1" } catch { Write-Host "Core ping failed: $_" }
try { if ($sshAvailable) { $p2 = Invoke-Run -targetHost $edge -command "ping -c 2 $core >/dev/null && echo OK || echo FAIL"; Write-Host "Edge → Core ping: $p2" } else { Write-Host "Edge → Core ping skipped: SSH not available" } } catch { Write-Host "Edge ping failed: $_" }

Write-Host "\n-- Collect logs for TwisterLab API (last 200 lines) --"
try { $logs = Invoke-Run -targetHost $edge -command "docker service logs --tail 200 twisterlab_api || true"; Write-Host $logs } catch { Write-Host "Error collecting logs: $_" }

Write-Host "\n-- Collect Ollama logs (last 200 lines) --"
try {
    if ($LocalIps -contains $core -or $core -eq $env:COMPUTERNAME) {
        $logs2 = Invoke-Run -targetHost $core -command "Get-EventLog -LogName Application -Newest 200 | Where-Object { $_.Message -match 'ollama' }"
    } else {
        $logs2 = Invoke-Run -targetHost $core -command "journalctl -u ollama -n 200 --no-pager || true"
    }
    Write-Host $logs2
} catch { Write-Host "Error collecting Ollama logs: $_" }

Write-Host "\n--- Diagnostic SSH script ended ---" -ForegroundColor Cyan
