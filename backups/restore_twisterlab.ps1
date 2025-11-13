param(
    [string]$BackupPath,
    [string]$RestorePath = "C:\TwisterLab\restore",
    [switch]$Force
)

Write-Host "Restauration TwisterLab" -ForegroundColor Cyan
Write-Host "De: $BackupPath" -ForegroundColor Yellow
Write-Host "Vers: $RestorePath" -ForegroundColor Yellow

if (!(Test-Path $BackupPath)) {
    Write-Error "Fichier de sauvegarde introuvable: $BackupPath"
    exit 1
}

if ((Test-Path $RestorePath) -and !$Force) {
    Write-Error "Repertoire de restauration existe deja. Utilisez -Force pour ecraser."
    exit 1
}

# CrÃ©er le rÃ©pertoire de restauration
New-Item -ItemType Directory -Path $RestorePath -Force | Out-Null

# Extraire l'archive
Write-Host "Extraction de l'archive..." -ForegroundColor Yellow
Expand-Archive -Path $BackupPath -DestinationPath $RestorePath -Force

if (Test-Path $RestorePath) {
    Write-Host "OK Restauration terminee: $RestorePath" -ForegroundColor Green
} else {
    Write-Error "Echec de la restauration"
    exit 1
}
