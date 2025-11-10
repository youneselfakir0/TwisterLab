# TwisterLab - Cleanup Old Files Script
# Archive les anciens fichiers suite à réorganisation

param([switch]$DryRun, [switch]$Force)

Write-Host "=== TWISTERLAB CLEANUP OLD FILES ===" -ForegroundColor Cyan

if (!(Test-Path ".\infrastructure")) {
    Write-Host "[ERROR] Executer depuis la racine TwisterLab" -ForegroundColor Red
    exit 1
}

if (-not $Force -and -not $DryRun) {
    Write-Host "[WARN] Archivage anciens fichiers - ENTER pour continuer, CTRL+C annuler" -ForegroundColor Yellow
    Read-Host
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveDir = "archive\old-structure-$timestamp"

$filesToArchive = @(
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "docker-compose.production.yml",
    "docker-compose.staging.yml",
    "docker-compose.override.yml",
    "docker-compose.monitoring*.yml",
    "Dockerfile",
    "Dockerfile.api.prod"
)

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    Write-Host "[INFO] Archive: $archiveDir" -ForegroundColor Cyan
}

$archived = 0
foreach ($pattern in $filesToArchive) {
    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        if ($DryRun) {
            Write-Host "[DRY-RUN] Archive: $($file.Name)" -ForegroundColor Yellow
        } else {
            Move-Item $file.FullName "$archiveDir\$($file.Name)" -Force
            Write-Host "[OK] Archive: $($file.Name)" -ForegroundColor Green
        }
        $archived++
    }
}

Write-Host "`n=== RESULTAT ===" -ForegroundColor Cyan
Write-Host "[INFO] Fichiers archives: $archived" -ForegroundColor Green
if ($DryRun) {
    Write-Host "[WARN] DRY-RUN - Aucune modification" -ForegroundColor Yellow
    Write-Host "[INFO] Pour executer: .\infrastructure\scripts\cleanup_old_files.ps1 -Force"
}
Write-Host "[OK] Nouvelle structure: infrastructure/" -ForegroundColor Green
