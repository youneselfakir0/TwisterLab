#!/usr/bin/env pwsh
# Script de correction automatique Docker - TwisterLab (ASCII Safe)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CORRECTION DOCKER SWARM - TwisterLab" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# ETAPE 1: Construire l'image API
Write-Host "[1/4] Construction de l'image twisterlab-api..." -ForegroundColor Yellow
docker build -t twisterlab-api:latest -f Dockerfile.api .

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Image twisterlab-api:latest construite`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec de construction de l'image`n" -ForegroundColor Red
    exit 1
}

# ETAPE 2: Sauvegarder l'image pour transfert
Write-Host "[2/4] Sauvegarde de l'image pour transfert..." -ForegroundColor Yellow
docker save twisterlab-api:latest -o twisterlab-api.tar

if (Test-Path "twisterlab-api.tar") {
    $fileSize = (Get-Item "twisterlab-api.tar").Length / 1MB
    $fileSizeRounded = [math]::Round($fileSize, 2)
    Write-Host "[OK] Image sauvegardee: twisterlab-api.tar ($fileSizeRounded MB)`n" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Echec de sauvegarde de l'image`n" -ForegroundColor Red
    exit 1
}

# ETAPE 3: Verifier la contrainte WebUI
Write-Host "[3/4] Verification de la contrainte WebUI..." -ForegroundColor Yellow

$composeFile = "docker-compose.production.yml"
$content = Get-Content $composeFile -Raw

if ($content -match 'node\.labels\.os == linux') {
    Write-Host "[OK] Contrainte WebUI deja corrigee (os == linux)`n" -ForegroundColor Green
} else {
    Write-Host "[INFO] Correction de la contrainte WebUI..." -ForegroundColor Yellow
    $newContent = $content -replace 'node\.role == worker', 'node.labels.os == linux'
    Set-Content -Path $composeFile -Value $newContent
    Write-Host "[OK] Contrainte WebUI corrigee`n" -ForegroundColor Green
}

# ETAPE 4: Instructions de transfert
Write-Host "[4/4] Instructions de transfert vers edgeserver`n" -ForegroundColor Yellow
Write-Host "OPTION A - Transfert manuel (recommande):" -ForegroundColor Cyan
Write-Host "  1. Copier twisterlab-api.tar vers edgeserver:" -ForegroundColor White
Write-Host "     scp twisterlab-api.tar user@edgeserver.twisterlab.local:/tmp/" -ForegroundColor Gray
Write-Host "`n  2. Sur edgeserver, charger l'image:" -ForegroundColor White
Write-Host "     ssh edgeserver.twisterlab.local" -ForegroundColor Gray
Write-Host "     docker load -i /tmp/twisterlab-api.tar" -ForegroundColor Gray
Write-Host "`n  3. Redployer le stack:" -ForegroundColor White
Write-Host "     docker stack deploy -c docker-compose.production.yml twisterlab_prod`n" -ForegroundColor Gray

Write-Host "OPTION B - Registre Docker (automatisation):" -ForegroundColor Cyan
Write-Host "  1. Configurer un registre prive" -ForegroundColor White
Write-Host "  2. Pousser l'image:" -ForegroundColor White
Write-Host "     docker tag twisterlab-api:latest registry.twisterlab.local/twisterlab-api:latest" -ForegroundColor Gray
Write-Host "     docker push registry.twisterlab.local/twisterlab-api:latest`n" -ForegroundColor Gray

# Resume
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CORRECTIONS TERMINEES" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Actions completees:" -ForegroundColor Yellow
Write-Host "  [OK] Image twisterlab-api:latest construite" -ForegroundColor Green
Write-Host "  [OK] Image sauvegardee dans twisterlab-api.tar" -ForegroundColor Green
Write-Host "  [OK] Contrainte WebUI verifiee" -ForegroundColor Green

Write-Host "`nActions requises:" -ForegroundColor Yellow
Write-Host "  [ ] Transferer twisterlab-api.tar vers edgeserver" -ForegroundColor White
Write-Host "  [ ] Charger l'image sur edgeserver" -ForegroundColor White
Write-Host "  [ ] Redeployer le stack Docker" -ForegroundColor White

Write-Host "`nSECURITE CRITIQUE:" -ForegroundColor Red
Write-Host "  [!] API Docker exposee sans TLS (ports 2375, 2376)" -ForegroundColor Yellow
Write-Host "  [?] Consulter DOCKER_ANALYSIS_REPORT.md section PRIORITE 1`n" -ForegroundColor White

# Afficher l'etat actuel
Write-Host "Etat des services apres correction locale:`n" -ForegroundColor Cyan
docker service ls

Write-Host "`nProchaine etape:" -ForegroundColor Cyan
Write-Host "   Executer la commande de transfert vers edgeserver ci-dessus`n" -ForegroundColor White
