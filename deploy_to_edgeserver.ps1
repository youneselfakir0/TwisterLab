#!/usr/bin/env pwsh
# Script de deploiement sur edgeserver - TwisterLab

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT SUR EDGESERVER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Configuration
$edgeserver = "edgeserver.twisterlab.local"
$remoteUser = "administrator"  # Ajuster selon votre configuration
$remotePath = "/tmp/twisterlab"

Write-Host "[INFO] Configuration:" -ForegroundColor Cyan
Write-Host "  Serveur: $edgeserver" -ForegroundColor White
Write-Host "  Utilisateur: $remoteUser" -ForegroundColor White
Write-Host "  Chemin distant: $remotePath`n" -ForegroundColor White

# ETAPE 1: Creer l'archive du projet
Write-Host "[1/5] Creation de l'archive du projet..." -ForegroundColor Yellow

$filesToCopy = @(
    "Dockerfile.api",
    "requirements.txt",
    "pyproject.toml",
    "docker-compose.production.yml",
    "api",
    "agents"
)

$archiveName = "twisterlab-deploy.zip"

if (Test-Path $archiveName) {
    Remove-Item $archiveName -Force
}

Compress-Archive -Path $filesToCopy -DestinationPath $archiveName -Force

if (Test-Path $archiveName) {
    $archiveSize = (Get-Item $archiveName).Length / 1MB
    Write-Host "[OK] Archive creee: $archiveName ($([math]::Round($archiveSize, 2)) MB)`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec de creation de l'archive`n" -ForegroundColor Red
    exit 1
}

# ETAPE 2: Tester la connexion SSH
Write-Host "[2/5] Test de connexion SSH..." -ForegroundColor Yellow
$testSSH = ssh -o ConnectTimeout=5 "$remoteUser@$edgeserver" "echo OK" 2>$null

if ($testSSH -eq "OK") {
    Write-Host "[OK] Connexion SSH reussie`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Impossible de se connecter a $edgeserver" -ForegroundColor Red
    Write-Host "[INFO] Veuillez configurer l'acces SSH sans mot de passe:`n" -ForegroundColor Yellow
    Write-Host "  ssh-keygen -t rsa" -ForegroundColor Gray
    Write-Host "  ssh-copy-id $remoteUser@$edgeserver`n" -ForegroundColor Gray
    Write-Host "OU fournissez le mot de passe manuellement dans les etapes suivantes.`n" -ForegroundColor Yellow
}

# ETAPE 3: Transfert de l'archive
Write-Host "[3/5] Transfert de l'archive vers edgeserver..." -ForegroundColor Yellow
Write-Host "[INFO] Commande: scp $archiveName ${remoteUser}@${edgeserver}:${remotePath}/" -ForegroundColor Cyan

ssh "$remoteUser@$edgeserver" "mkdir -p $remotePath" 2>$null
scp $archiveName "${remoteUser}@${edgeserver}:${remotePath}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Archive transferee`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec du transfert`n" -ForegroundColor Red
    Write-Host "[ACTION] Executez manuellement:" -ForegroundColor Yellow
    Write-Host "  scp $archiveName ${remoteUser}@${edgeserver}:${remotePath}/`n" -ForegroundColor Gray
    exit 1
}

# ETAPE 4: Deploiement sur edgeserver
Write-Host "[4/5] Deploiement sur edgeserver..." -ForegroundColor Yellow

$deployScript = @"
cd $remotePath
unzip -o twisterlab-deploy.zip
docker build -t twisterlab-api:latest -f Dockerfile.api .
docker stack deploy -c docker-compose.production.yml twisterlab_prod
"@

Write-Host "[INFO] Script de deploiement:" -ForegroundColor Cyan
Write-Host $deployScript -ForegroundColor Gray

ssh "$remoteUser@$edgeserver" $deployScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Deploiement execute`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERREUR] Echec du deploiement`n" -ForegroundColor Red
    Write-Host "[ACTION] Connectez-vous manuellement:" -ForegroundColor Yellow
    Write-Host "  ssh $remoteUser@$edgeserver" -ForegroundColor Gray
    Write-Host "  cd $remotePath" -ForegroundColor Gray
    Write-Host "  unzip -o twisterlab-deploy.zip" -ForegroundColor Gray
    Write-Host "  docker build -t twisterlab-api:latest -f Dockerfile.api ." -ForegroundColor Gray
    Write-Host "  docker stack deploy -c docker-compose.production.yml twisterlab_prod`n" -ForegroundColor Gray
}

# ETAPE 5: Verification
Write-Host "[5/5] Verification des services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

docker service ls

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT TERMINE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Verifier l'etat avec:" -ForegroundColor Yellow
Write-Host "  docker service ps twisterlab_prod_api" -ForegroundColor White
Write-Host "  docker service ps twisterlab_prod_webui" -ForegroundColor White
Write-Host "  .\validate_docker_simple.ps1`n" -ForegroundColor White
