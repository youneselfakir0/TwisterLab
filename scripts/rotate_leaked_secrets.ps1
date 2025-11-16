<#
Rotate leaked secrets and ensure Docker Swarm secrets are updated.
This script calls `infrastructure/scripts/security.ps1 -Action rotate-passwords` and reports the secrets rotated.

Usage: .\scripts\rotate_leaked_secrets.ps1 [-Force]

Note: This will rotate all secrets defined in infrastructure/scripts/security.ps1. Review the list and update any external systems.
#>

param(
    [switch]$Force
)

Write-Host "Initiating secrets rotation via infrastructure/scripts/security.ps1..." -ForegroundColor Cyan

$scriptPath = Join-Path -Path (Split-Path -Parent $MyInvocation.MyCommand.Path) -ChildPath "..\infrastructure\scripts\security.ps1"
$scriptPath = Resolve-Path $scriptPath

if ($Force) {
    Write-Host "Rotation will force apply new secrets (existing secrets will be replaced)." -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File $scriptPath -Action rotate-passwords -Force
} else {
    powershell -ExecutionPolicy Bypass -File $scriptPath -Action rotate-passwords
}

Write-Host "Rotation completed. If secrets were rotated, ensure you update external consumers and restart services to pick up the new Docker secrets." -ForegroundColor Green

return 0
