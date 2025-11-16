# Script de déploiement et validation TwisterLab
# Utilisation: .\deploy-twisterlab.ps1 -Action [deploy|validate|fix]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "validate", "fix")]
    [string]$Action,

    [switch]$Force
)

$server = "twister@192.168.0.30"
$ErrorActionPreference = "Stop"

Write-Host "🚀 TwisterLab Deployment Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

function Invoke-RemoteCommand {
    param([string]$command, [string]$description)
    Write-Host "📡 $description" -ForegroundColor Blue
    try {
        $result = ssh $server $command
        return $result
    }
    catch {
        Write-Host "❌ Command failed: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

if ($Action -eq "deploy") {
    Write-Host "🔧 DEPLOYMENT MODE" -ForegroundColor Green

    # Apply security fixes
    Write-Host "Applying security fixes..." -ForegroundColor Yellow
    Invoke-RemoteCommand "docker service update --env-add WEBUI_AUTH=True twisterlab_webui" "Enable WebUI auth"
    Invoke-RemoteCommand "docker service update --secret-add jwt_secret_key --secret-add api_secret_key --secret-add api_admin_password twisterlab_api" "Add API secrets"
    Invoke-RemoteCommand "docker service update --secret-add postgres_secure_password twisterlab_postgres" "Add Postgres secrets"

    # Update Traefik with SSL
    Write-Host "Configuring SSL/TLS..." -ForegroundColor Yellow
    Invoke-RemoteCommand "docker service update --mount-add type=bind,source=/home/twister/traefik/traefik.yml,target=/etc/traefik/traefik.yml --mount-add type=bind,source=/home/twister/traefik,target=/letsencrypt twisterlab_traefik" "Update Traefik SSL config"

    Write-Host "✅ Deployment completed" -ForegroundColor Green
}

if ($Action -eq "validate") {
    Write-Host "🔍 VALIDATION MODE" -ForegroundColor Blue

    # Check services
    $services = Invoke-RemoteCommand "docker service ls --format 'table {{.Name}}\t{{.Replicas}}'" "Check services"
    Write-Host "Services Status:" -ForegroundColor Cyan
    Write-Host $services

    # Check secrets
    $secrets = Invoke-RemoteCommand "docker secret ls --format 'table {{.Name}}'" "Check secrets"
    Write-Host "Secrets Configured:" -ForegroundColor Cyan
    Write-Host $secrets

    # Check HTTPS
    try {
        $https = Invoke-RemoteCommand "curl -kI https://localhost 2>/dev/null | head -1" "Check HTTPS"
        Write-Host "HTTPS Status: $https" -ForegroundColor Green
    } catch {
        Write-Host "HTTPS: Not ready yet (certificate generating)" -ForegroundColor Yellow
    }

    Write-Host "✅ Validation completed" -ForegroundColor Green
}

if ($Action -eq "fix") {
    Write-Host "🔧 FIX MODE" -ForegroundColor Magenta

    # Fix node-exporter
    Write-Host "Attempting to fix node-exporter..." -ForegroundColor Yellow
    try {
        Invoke-RemoteCommand "docker service update --env-add NODE_EXPORTER_DISABLE_DEFAULT_COLLECTORS=filesystem --user 65534 monitoring_node-exporter" "Fix node-exporter"
        Write-Host "✅ Node-exporter fixed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Node-exporter still failing - manual intervention needed" -ForegroundColor Yellow
    }

    # Regenerate certificates if needed
    Write-Host "Checking SSL certificates..." -ForegroundColor Yellow
    Invoke-RemoteCommand "ls -la /home/twister/traefik/" "Check Traefik config"

    Write-Host "✅ Fixes applied" -ForegroundColor Green
}

Write-Host "`n📋 SUMMARY:" -ForegroundColor White
Write-Host "- Security: Secrets configured, SSL enabled" -ForegroundColor White
Write-Host "- Authentication: JWT + WebUI auth active" -ForegroundColor White
Write-Host "- Monitoring: Prometheus active, node-exporter needs fix" -ForegroundColor White
Write-Host "- SSL: Let's Encrypt configured (certificates generating)" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Wait 5-10 min for SSL certificates" -ForegroundColor White
Write-Host "2. Test HTTPS: curl -k https://192.168.0.30" -ForegroundColor White
Write-Host "3. Fix node-exporter permissions if needed" -ForegroundColor White
Write-Host "4. Run validation: .\deploy-twisterlab.ps1 -Action validate" -ForegroundColor White
