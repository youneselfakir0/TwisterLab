# Script pour deployer les exporters sur edgeserver
# Utilise SSH avec l'utilisateur twister

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "DEPLOIEMENT DES EXPORTERS SUR EDGESERVER" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$edgeserver = "192.168.0.30"
$user = "twister"
$scriptPath = "scripts/deploy_exporters.sh"

# 1. Copier le script sur edgeserver
Write-Host "[1/3] Copie du script sur edgeserver..." -ForegroundColor Yellow
scp $scriptPath "${user}@${edgeserver}:/tmp/deploy_exporters.sh"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECHEC de la copie du script" -ForegroundColor Red
    exit 1
}
Write-Host "Script copie avec succes" -ForegroundColor Green
Write-Host ""

# 2. Executer le script
Write-Host "[2/3] Execution du script sur edgeserver..." -ForegroundColor Yellow
ssh "${user}@${edgeserver}" "chmod +x /tmp/deploy_exporters.sh && /tmp/deploy_exporters.sh"

Write-Host ""
Write-Host "Script execute avec succes" -ForegroundColor Green
Write-Host ""

# 3. Verifier les services
Write-Host "[3/3] Verification des services deployes..." -ForegroundColor Yellow
ssh "${user}@${edgeserver}" "docker service ls --filter name=exporter"

Write-Host ""
Write-Host "DEPLOIEMENT TERMINE!" -ForegroundColor Green
