#!/usr/bin/env pwsh
# Construction image Linux via WSL - Version simplifiee

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CONSTRUCTION IMAGE LINUX (WSL)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verifier WSL
Write-Host "[1/4] Verification WSL..." -ForegroundColor Yellow
$wslVersion = wsl --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] WSL disponible`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] WSL non disponible`n" -ForegroundColor Red
    exit 1
}

# Verifier Docker dans WSL
Write-Host "[2/4] Verification Docker dans WSL..." -ForegroundColor Yellow
$dockerVersion = wsl docker --version 2>&1
if ($dockerVersion -match "Docker") {
    Write-Host "[OK] Docker disponible: $dockerVersion`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Docker non disponible dans WSL`n" -ForegroundColor Red
    exit 1
}

# Construire directement depuis le repertoire Windows monte
Write-Host "[3/4] Construction de l'image..." -ForegroundColor Yellow
Write-Host "[INFO] Utilisation du montage Windows dans WSL (/mnt/c/TwisterLab)`n" -ForegroundColor Cyan

# Construire l'image en utilisant le chemin WSL monte (sans buildkit)
wsl bash -c "cd /mnt/c/TwisterLab && DOCKER_BUILDKIT=0 docker build -t twisterlab-api:latest -f Dockerfile.api ."

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Image construite avec succes!`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERREUR] Echec de construction`n" -ForegroundColor Red
    exit 1
}

# Sauvegarder l'image
Write-Host "[4/4] Sauvegarde de l'image..." -ForegroundColor Yellow
wsl bash -c "cd /mnt/c/TwisterLab && docker save twisterlab-api:latest -o twisterlab-api.tar"

if ($LASTEXITCODE -eq 0 -and (Test-Path "twisterlab-api.tar")) {
    $fileSize = (Get-Item "twisterlab-api.tar").Length / 1MB
    Write-Host "[OK] Archive creee: twisterlab-api.tar ($([math]::Round($fileSize, 2)) MB)`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec de sauvegarde`n" -ForegroundColor Red
    exit 1
}

# Succes
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONSTRUCTION TERMINEE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Fichier genere: twisterlab-api.tar`n" -ForegroundColor White

Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Transferer vers edgeserver:" -ForegroundColor Cyan
Write-Host "     scp twisterlab-api.tar administrator@edgeserver.twisterlab.local:/tmp/`n" -ForegroundColor White

Write-Host "  2. Sur edgeserver, charger et deployer:" -ForegroundColor Cyan
Write-Host "     ssh edgeserver.twisterlab.local" -ForegroundColor White
Write-Host "     docker load -i /tmp/twisterlab-api.tar" -ForegroundColor White
Write-Host "     docker stack deploy -c docker-compose.production.yml twisterlab_prod`n" -ForegroundColor White

Write-Host "  3. Verifier:" -ForegroundColor Cyan
Write-Host "     .\validate_docker_simple.ps1`n" -ForegroundColor White
