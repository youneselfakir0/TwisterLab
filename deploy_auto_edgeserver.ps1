#!/usr/bin/env pwsh
# Deploiement automatise complet sur edgeserver

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT AUTO - EDGESERVER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Configuration
$edgeserver = "edgeserver.twisterlab.local"
$user = "administrator"

# ETAPE 1: Preparer l'archive
Write-Host "[1/4] Preparation de l'archive..." -ForegroundColor Yellow

$files = @("Dockerfile.api", "requirements.txt", "pyproject.toml", "docker-compose.production.yml")
$deployDir = "deploy"

if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $deployDir | Out-Null

foreach ($file in $files) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination "$deployDir/" -Force
        Write-Host "[OK] $file copie" -ForegroundColor Green
    } else {
        Write-Host "[WARN] $file introuvable" -ForegroundColor Yellow
    }
}

if (Test-Path "api") {
    Copy-Item -Path "api" -Destination "$deployDir/" -Recurse -Force
    Write-Host "[OK] Dossier api copie" -ForegroundColor Green
}

if (Test-Path "agents") {
    Copy-Item -Path "agents" -Destination "$deployDir/" -Recurse -Force
    Write-Host "[OK] Dossier agents copie" -ForegroundColor Green
}

Compress-Archive -Path "$deployDir\*" -DestinationPath "twisterlab-deploy.zip" -Force

if (Test-Path "twisterlab-deploy.zip") {
    $size = (Get-Item "twisterlab-deploy.zip").Length / 1MB
    Write-Host "[OK] Archive creee: twisterlab-deploy.zip ($([math]::Round($size, 2)) MB)`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec de creation de l'archive`n" -ForegroundColor Red
    exit 1
}

# ETAPE 2: Tester SSH
Write-Host "[2/4] Test de connexion SSH..." -ForegroundColor Yellow
$testSSH = ssh -o ConnectTimeout=5 "$user@$edgeserver" "echo OK" 2>$null

if ($testSSH -eq "OK") {
    Write-Host "[OK] Connexion SSH reussie`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Impossible de se connecter a $edgeserver" -ForegroundColor Red
    Write-Host "`nPour configurer SSH:" -ForegroundColor Yellow
    Write-Host "  1. ssh-keygen -t rsa" -ForegroundColor White
    Write-Host "  2. type `$env:USERPROFILE\.ssh\id_rsa.pub | ssh $user@$edgeserver 'cat >> ~/.ssh/authorized_keys'`n" -ForegroundColor White
    Write-Host "OU suivez le guide manuel dans SOLUTION_FINALE_DEPLOYMENT.md`n" -ForegroundColor Yellow
    exit 1
}

# ETAPE 3: Transfert
Write-Host "[3/4] Transfert vers edgeserver..." -ForegroundColor Yellow
scp twisterlab-deploy.zip "${user}@${edgeserver}:/tmp/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Archive transferee`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec du transfert`n" -ForegroundColor Red
    exit 1
}

# ETAPE 4: Construction et deploiement sur edgeserver
Write-Host "[4/4] Construction et deploiement..." -ForegroundColor Yellow
Write-Host "[INFO] Cette etape peut prendre 2-3 minutes...`n" -ForegroundColor Cyan

$deployScript = "cd /tmp && unzip -o twisterlab-deploy.zip && docker build -t twisterlab-api:latest -f Dockerfile.api . && docker stack deploy -c docker-compose.production.yml twisterlab_prod"

ssh "$user@$edgeserver" $deployScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Deploiement execute`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERREUR] Echec du deploiement`n" -ForegroundColor Red
    Write-Host "[INFO] Consultez SOLUTION_FINALE_DEPLOYMENT.md pour le deploiement manuel`n" -ForegroundColor Yellow
    exit 1
}

# VERIFICATION
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT TERMINE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Attente du demarrage des services (15 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "`nEtat des services:" -ForegroundColor Cyan
docker service ls

Write-Host "`n========================================`n" -ForegroundColor Cyan

Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Verifier: .\validate_docker_simple.ps1" -ForegroundColor White
Write-Host "  2. Tester API: curl http://edgeserver.twisterlab.local:8000/health" -ForegroundColor White
Write-Host "  3. Consulter logs: docker service logs twisterlab_prod_api`n" -ForegroundColor White
