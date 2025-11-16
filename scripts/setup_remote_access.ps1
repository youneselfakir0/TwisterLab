<#
PowerShell script: setup_remote_access.ps1
Purpose: Configure the local Windows workstation to allow remote PowerShell and SSH connections for diagnostics.
Usage: Run as Administrator
#>

Write-Host "-- Configuring TrustedHosts for WinRM access --"
try {
    $currentTrustedHosts = (Get-Item -Path WSMan:\localhost\Client\TrustedHosts -ErrorAction SilentlyContinue).Value
    if (-not $currentTrustedHosts) { $currentTrustedHosts = "" }
    $toAdd = "192.168.0.20,192.168.0.30"
    if ($currentTrustedHosts -notlike "*$toAdd*") {
        Write-Host "Adding $toAdd to TrustedHosts..."
        Set-Item -Path WSMan:\localhost\Client\TrustedHosts -Value $toAdd -Force
    } else {
        Write-Host "TrustedHosts already configured: $currentTrustedHosts"
    }
} catch {
    Write-Host "Failed to configure TrustedHosts: $_"
}

Write-Host "-- Configuring WinRM Service --"
try {
    if ((Get-Service -Name WinRM -ErrorAction SilentlyContinue) -eq $null) {
        Write-Host "WinRM service not found. Installing/Enabling WinRM via `winrm quickconfig`..."
        winrm quickconfig -q
    } else {
        Start-Service WinRM -ErrorAction SilentlyContinue
        Set-Service -Name WinRM -StartupType Automatic
        Write-Host "WinRM service started"
    }
} catch {
    Write-Host "Error when configuring WinRM: $_"
}

Write-Host "-- Optional: Ensure OpenSSH client is installed (client is generally installed on Windows 10/11) --"
try {
    if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
        Write-Host "OpenSSH client not found. Installing via optional features..."
        Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
    } else {
        Write-Host "OpenSSH client already installed"
    }
} catch {
    Write-Host "Error when checking/installing OpenSSH client: $_"
}

Write-Host "-- Optional: Enable OpenSSH Server if you want to accept SSH connections to this system --"
try {
    if (-not (Get-Service -Name sshd -ErrorAction SilentlyContinue)) {
        Write-Host "OpenSSH Server not installed. Install it? (y/N)"
        $response = Read-Host
        if ($response -eq 'y' -or $response -eq 'Y') {
            Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
            Start-Service sshd
            Set-Service -Name sshd -StartupType Automatic
            Write-Host "OpenSSH Server installed and started"
        } else {
            Write-Host "Skipping OpenSSH Server installation"
        }
    } else {
        Start-Service sshd -ErrorAction SilentlyContinue
        Set-Service -Name sshd -StartupType Automatic
        Write-Host "OpenSSH Server already installed and started"
    }
} catch {
    Write-Host "Error when installing/configuring OpenSSH Server: $_"
}

Write-Host "Setup finished. If you added TrustedHosts, restart the WinRM service: Restart-Service WinRM"
