#!/usr/bin/env pwsh
# Construction d'image Linux via WSL - TwisterLab

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CONSTRUCTION IMAGE LINUX (via WSL)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ETAPE 1: Verifier WSL
Write-Host "[1/5] Verification de WSL..." -ForegroundColor Yellow
$wslCheck = wsl --status 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] WSL est installe et disponible`n" -ForegroundColor Green

    # Afficher la distribution par defaut
    $wslDistro = wsl -l -v | Select-String "Default" -Context 0,1
    Write-Host "[INFO] Distribution WSL:" -ForegroundColor Cyan
    Write-Host "$wslDistro`n" -ForegroundColor Gray
} else {
    Write-Host "[ERREUR] WSL non disponible`n" -ForegroundColor Red
    Write-Host "[ACTION] Installer WSL:" -ForegroundColor Yellow
    Write-Host "  wsl --install`n" -ForegroundColor White
    exit 1
}

# ETAPE 2: Verifier Docker dans WSL
Write-Host "[2/5] Verification de Docker dans WSL..." -ForegroundColor Yellow
$dockerInWSL = wsl docker --version 2>&1

if ($dockerInWSL -match "Docker version") {
    Write-Host "[OK] Docker disponible dans WSL`n" -ForegroundColor Green
    Write-Host "[INFO] $dockerInWSL`n" -ForegroundColor Gray
} else {
    Write-Host "[WARN] Docker non trouve dans WSL" -ForegroundColor Yellow
    Write-Host "[INFO] Docker Desktop doit partager son contexte avec WSL`n" -ForegroundColor Cyan
}

# ETAPE 3: Preparer le repertoire dans WSL
Write-Host "[3/5] Preparation du repertoire dans WSL..." -ForegroundColor Yellow

$wslPath = "/tmp/twisterlab-build"
$currentDir = (Get-Location).Path

# Convertir le chemin Windows en chemin WSL
$wslCurrentDir = wsl wslpath -a "$currentDir"

Write-Host "[INFO] Repertoire Windows: $currentDir" -ForegroundColor Cyan
Write-Host "[INFO] Repertoire WSL: $wslCurrentDir`n" -ForegroundColor Cyan

# Creer le repertoire de build
wsl bash -c "rm -rf $wslPath && mkdir -p $wslPath"

# Copier uniquement les fichiers et dossiers necessaires
$filesToCopy = @(
    "Dockerfile.api",
    "requirements.txt",
    "pyproject.toml",
    "api",
    "agents"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Write-Host "[INFO] Copie de $file..." -ForegroundColor Cyan
        wsl bash -c "cp -r $wslCurrentDir/$file $wslPath/"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] $file copie" -ForegroundColor Green
        } else {
            Write-Host "[ERREUR] Echec de copie de $file" -ForegroundColor Red
        }
    } else {
        Write-Host "[WARN] $file introuvable" -ForegroundColor Yellow
    }
}

Write-Host "[OK] Fichiers copies dans WSL:$wslPath`n" -ForegroundColor Green

# ETAPE 4: Construire l'image dans WSL
Write-Host "[4/5] Construction de l'image dans WSL..." -ForegroundColor Yellow
Write-Host "[INFO] Ceci peut prendre plusieurs minutes...`n" -ForegroundColor Cyan

$buildCommand = @"
cd $wslPath && docker build -t twisterlab-api:latest -f Dockerfile.api .
"@

wsl bash -c $buildCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Image construite avec succes dans WSL`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERREUR] Echec de construction dans WSL`n" -ForegroundColor Red
    exit 1
}

# ETAPE 5: Sauvegarder l'image
Write-Host "[5/5] Sauvegarde de l'image..." -ForegroundColor Yellow

$tarFile = "twisterlab-api.tar"

wsl bash -c "cd $wslPath && docker save twisterlab-api:latest -o $tarFile"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Image sauvegardee dans WSL`n" -ForegroundColor Green

    # Copier le tar vers Windows
    Write-Host "[INFO] Copie du fichier .tar vers Windows..." -ForegroundColor Cyan
    wsl bash -c "cp $wslPath/$tarFile $wslCurrentDir/"

    if (Test-Path $tarFile) {
        $fileSize = (Get-Item $tarFile).Length / 1MB
        Write-Host "[OK] Archive disponible: $tarFile ($([math]::Round($fileSize, 2)) MB)`n" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Fichier .tar non trouve dans Windows`n" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERREUR] Echec de sauvegarde`n" -ForegroundColor Red
    exit 1
}

# VERIFICATION
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONSTRUCTION TERMINEE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Image construite avec succes!" -ForegroundColor Green
if (Test-Path $tarFile) {
    Write-Host "  Archive: $tarFile`n" -ForegroundColor White
}

Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  Option A - Transfert vers edgeserver:" -ForegroundColor Cyan
Write-Host "    scp $tarFile administrator@edgeserver.twisterlab.local:/tmp/" -ForegroundColor White
Write-Host "    ssh edgeserver.twisterlab.local" -ForegroundColor White
Write-Host "    docker load -i /tmp/$tarFile" -ForegroundColor White
Write-Host "    docker stack deploy -c docker-compose.production.yml twisterlab_prod`n" -ForegroundColor White

Write-Host "  Option B - Script automatique:" -ForegroundColor Cyan
Write-Host "    .\deploy_to_edgeserver.ps1`n" -ForegroundColor White

Write-Host "  Option C - Charger dans Docker local:" -ForegroundColor Cyan
Write-Host "    docker load -i $tarFile" -ForegroundColor White
Write-Host "    docker images twisterlab-api`n" -ForegroundColor White
