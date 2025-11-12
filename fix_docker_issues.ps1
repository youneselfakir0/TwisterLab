#!/usr/bin/env pwsh
# Script de correction automatique Docker - TwisterLab
# Date: 10 Nov 2025

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🔧 CORRECTION DOCKER SWARM - TwisterLab" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# ÉTAPE 1: Construire l'image API
Write-Host "[1/4] 🏗️  Construction de l'image twisterlab-api..." -ForegroundColor Yellow
docker build -t twisterlab-api:latest -f Dockerfile.api .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image twisterlab-api:latest construite avec succès`n" -ForegroundColor Green
} else {
    Write-Host "❌ Échec de construction de l'image`n" -ForegroundColor Red
    exit 1
}

# ÉTAPE 2: Sauvegarder l'image pour transfert
Write-Host "[2/4] 💾 Sauvegarde de l'image pour transfert vers edgeserver..." -ForegroundColor Yellow
docker save twisterlab-api:latest -o twisterlab-api.tar

if (Test-Path "twisterlab-api.tar") {
    $fileSize = (Get-Item "twisterlab-api.tar").Length / 1MB
    Write-Host "✅ Image sauvegardée: twisterlab-api.tar ($([math]::Round($fileSize, 2)) MB)`n" -ForegroundColor Green
} else {
    Write-Host "❌ Échec de sauvegarde de l'image`n" -ForegroundColor Red
    exit 1
}

# ÉTAPE 3: Corriger la contrainte WebUI
Write-Host "[3/4] 📝 Correction de la contrainte de placement WebUI..." -ForegroundColor Yellow

$composeFile = "docker-compose.production.yml"
$content = Get-Content $composeFile -Raw

# Remplacer la contrainte node.role == worker par node.labels.os == linux
$newContent = $content -replace 'node\.role == worker', 'node.labels.os == linux'

Set-Content -Path $composeFile -Value $newContent
Write-Host "✅ Contrainte WebUI corrigée (worker → os==linux)`n" -ForegroundColor Green

# ÉTAPE 4: Afficher les instructions de transfert
Write-Host "[4/4] 📦 Instructions de transfert vers edgeserver`n" -ForegroundColor Yellow
Write-Host "OPTION A - Transfert manuel (recommandé):" -ForegroundColor Cyan
Write-Host "  1. Copier twisterlab-api.tar vers edgeserver:" -ForegroundColor White
Write-Host "     scp twisterlab-api.tar user@edgeserver.twisterlab.local:/tmp/" -ForegroundColor Gray
Write-Host "`n  2. Sur edgeserver, charger l'image:" -ForegroundColor White
Write-Host "     ssh edgeserver.twisterlab.local" -ForegroundColor Gray
Write-Host "     docker load -i /tmp/twisterlab-api.tar" -ForegroundColor Gray
Write-Host "`n  3. Redéployer le stack:" -ForegroundColor White
Write-Host "     docker stack deploy -c docker-compose.production.yml twisterlab_prod`n" -ForegroundColor Gray

Write-Host "OPTION B - Registre Docker (pour automatisation):" -ForegroundColor Cyan
Write-Host "  1. Configurer un registre privé" -ForegroundColor White
Write-Host "  2. Pousser l'image:" -ForegroundColor White
Write-Host "     docker tag twisterlab-api:latest registry.twisterlab.local/twisterlab-api:latest" -ForegroundColor Gray
Write-Host "     docker push registry.twisterlab.local/twisterlab-api:latest`n" -ForegroundColor Gray

# Résumé
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ CORRECTIONS TERMINÉES" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📋 Actions complétées:" -ForegroundColor Yellow
Write-Host "  ✅ Image twisterlab-api:latest construite" -ForegroundColor Green
Write-Host "  ✅ Image sauvegardée dans twisterlab-api.tar" -ForegroundColor Green
Write-Host "  ✅ Contrainte WebUI corrigée dans docker-compose.production.yml" -ForegroundColor Green

Write-Host "`n⚠️  Actions requises:" -ForegroundColor Yellow
Write-Host "  ⏭️  Transférer twisterlab-api.tar vers edgeserver" -ForegroundColor White
Write-Host "  ⏭️  Charger l'image sur edgeserver" -ForegroundColor White
Write-Host "  ⏭️  Redéployer le stack Docker" -ForegroundColor White

Write-Host "`n🔒 SÉCURITÉ CRITIQUE:" -ForegroundColor Red
Write-Host "  ⚠️  API Docker exposée sans TLS (ports 2375, 2376)" -ForegroundColor Yellow
Write-Host "  📖 Consulter DOCKER_ANALYSIS_REPORT.md section PRIORITÉ 1`n" -ForegroundColor White

# Afficher l'état actuel
Write-Host "📊 État des services après correction locale:`n" -ForegroundColor Cyan
docker service ls

Write-Host "`n🎯 Prochaine étape:" -ForegroundColor Cyan
Write-Host "   Exécuter la commande de transfert vers edgeserver ci-dessus`n" -ForegroundColor White
