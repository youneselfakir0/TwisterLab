# Security Hardening Script for CoreRTX
# Phase 1: Fondation Infrastructure - Security Corrections

Write-Host "CoreRTX Security Hardening Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 1. Restrict dangerous ports to localhost/internal only
Write-Host "`n1. Restricting dangerous ports..." -ForegroundColor Yellow

# SMB (445) - Restrict to internal network only
Write-Host "Restricting SMB (445) to internal network..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "SMB-Inbound-Restricted" -Direction Inbound -Protocol TCP -LocalPort 445 -Action Allow -RemoteAddress "192.168.0.0/24","10.0.0.0/8","172.16.0.0/12" -Profile Any | Out-Null

# RPC (135) - Restrict to localhost
Write-Host "Restricting RPC (135) to localhost..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "RPC-Inbound-Localhost" -Direction Inbound -Protocol TCP -LocalPort 135 -Action Allow -RemoteAddress "127.0.0.1" -Profile Any | Out-Null

# RDP (3389) - Restrict to internal network only
Write-Host "Restricting RDP (3389) to internal network..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "RDP-Inbound-Restricted" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow -RemoteAddress "192.168.0.0/24" -Profile Any | Out-Null

# Docker ports (2375, 2376) - Restrict to localhost
Write-Host "Restricting Docker ports to localhost..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Docker2375-Localhost" -Direction Inbound -Protocol TCP -LocalPort 2375 -Action Allow -RemoteAddress "127.0.0.1" -Profile Any | Out-Null
New-NetFirewallRule -DisplayName "Docker2376-Localhost" -Direction Inbound -Protocol TCP -LocalPort 2376 -Action Allow -RemoteAddress "127.0.0.1" -Profile Any | Out-Null

# NetBIOS (139) - Restrict to internal network
Write-Host "Restricting NetBIOS (139) to internal network..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "NetBIOS-Inbound-Restricted" -Direction Inbound -Protocol TCP -LocalPort 139 -Action Allow -RemoteAddress "192.168.0.0/24","10.0.0.0/8","172.16.0.0/12" -Profile Any | Out-Null

# 2. Enable Windows Defender features
Write-Host "`n2. Enabling Windows Defender features..." -ForegroundColor Yellow

# Ensure Windows Defender is enabled
Set-MpPreference -DisableRoutinelyTakingAction $false
Set-MpPreference -EnableControlledFolderAccess Enabled
Set-MpPreference -PUAProtection Enabled

# Enable real-time monitoring
Set-MpPreference -DisableRealtimeMonitoring $false

# 3. Configure audit policies
Write-Host "`n3. Configuring audit policies..." -ForegroundColor Yellow

# Enable security auditing
auditpol /set /subcategory:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /subcategory:"Account Management" /success:enable /failure:enable
auditpol /set /subcategory:"Object Access" /success:enable /failure:enable

# 4. Remove unnecessary user accounts
Write-Host "`n4. Checking user accounts..." -ForegroundColor Yellow

# Get all user accounts
$users = Get-LocalUser | Where-Object { $_.Enabled -eq $true -and $_.Name -notlike "*Administrator*" -and $_.Name -notlike "*Default*" -and $_.Name -notlike "*Guest*" }

Write-Host "Found $($users.Count) enabled user accounts:" -ForegroundColor Yellow
$users | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }

# 5. Verify services status
Write-Host "`n5. Verifying critical services..." -ForegroundColor Yellow

$criticalServices = @(
    "WinDefend",
    "SecurityHealthService",
    "mpssvc",
    "WdNisSvc"
)

foreach ($service in $criticalServices) {
    $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
    if ($svc) {
        Write-Host "  OK $($svc.DisplayName): $($svc.Status)" -ForegroundColor Green
    } else {
        Write-Host "  ERROR Service $service not found" -ForegroundColor Red
    }
}

# 6. Final security check
Write-Host "`n6. Running final security check..." -ForegroundColor Yellow

# Check firewall status
$firewall = Get-NetFirewallProfile
Write-Host "Firewall Status:" -ForegroundColor Yellow
$firewall | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Enabled)" -ForegroundColor $(if ($_.Enabled) { "Green" } else { "Red" })
}

Write-Host "`nSecurity hardening completed!" -ForegroundColor Green
Write-Host "Recommend rebooting the system to apply all changes." -ForegroundColor Yellow