#!/usr/bin/env pwsh
# Construction d'image Linux sur Windows avec buildx

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CONSTRUCTION IMAGE LINUX (buildx)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ETAPE 1: Verifier/creer le builder
Write-Host "[1/3] Configuration du builder multiplateforme..." -ForegroundColor Yellow

$builders = docker buildx ls
if ($builders -match "multiplatform") {
    Write-Host "[OK] Builder multiplatform existe deja`n" -ForegroundColor Green
} else {
    Write-Host "[INFO] Creation du builder multiplatform..." -ForegroundColor Cyan
    docker buildx create --name multiplatform --use
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Builder cree`n" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Echec de creation du builder`n" -ForegroundColor Red
        exit 1
    }
}

# ETAPE 2: Construire l'image pour Linux
Write-Host "[2/3] Construction de l'image pour Linux AMD64..." -ForegroundColor Yellow
Write-Host "[INFO] Ceci peut prendre plusieurs minutes...`n" -ForegroundColor Cyan

docker buildx build --platform linux/amd64 -t twisterlab-api:latest -f Dockerfile.api --load .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Image construite avec succes`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERREUR] Echec de construction`n" -ForegroundColor Red
    Write-Host "[INFO] Tentative avec cache desactive..." -ForegroundColor Yellow
    docker buildx build --platform linux/amd64 -t twisterlab-api:latest -f Dockerfile.api --no-cache --load .

    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n[ERREUR] Echec persistant`n" -ForegroundColor Red
        exit 1
    }
}

# ETAPE 3: Verification
Write-Host "[3/3] Verification de l'image..." -ForegroundColor Yellow
docker images twisterlab-api:latest

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "IMAGE CONSTRUITE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Sauvegarder l'image: docker save twisterlab-api:latest -o twisterlab-api.tar" -ForegroundColor White
Write-Host "  2. Transferer vers edgeserver" -ForegroundColor White
Write-Host "  3. Charger sur edgeserver: docker load -i twisterlab-api.tar" -ForegroundColor White
Write-Host "  4. Redeployer: docker stack deploy -c docker-compose.production.yml twisterlab_prod`n" -ForegroundColor White

Write-Host "OU utiliser le script automatique:" -ForegroundColor Yellow
Write-Host "  .\deploy_to_edgeserver.ps1`n" -ForegroundColor White
