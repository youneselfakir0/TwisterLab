# Script de sauvegarde TwisterLab avec chiffrement
param(
    [string]$BackupType = "daily",
    [switch]$Force
)

Write-Host "TwisterLab Backup Script - Type: $BackupType" -ForegroundColor Cyan

# Configuration
$backupBase = "C:\TwisterLab\backups"
$keyFile = "$backupBase\config\backup_key.bin"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "twisterlab_$($BackupType)_$timestamp"

# Chemins Ã  sauvegarder
$pathsToBackup = @(
    "C:\TwisterLab\agents",
    "C:\TwisterLab\api",
    "C:\TwisterLab\config",
    "C:\TwisterLab\data",
    "C:\TwisterLab\monitoring",
    "C:\TwisterLab\infrastructure"
)

# VÃ©rifier la clÃ© de chiffrement
if (!(Test-Path $keyFile)) {
    Write-Error "Cle de chiffrement manquante: $keyFile"
    exit 1
}

Write-Host "Creation de la sauvegarde: $backupName" -ForegroundColor Yellow
Write-Host "Sauvegarde simplifiee sans chiffrement (installer 7-Zip pour le chiffrement)" -ForegroundColor Yellow

# CrÃ©er une archive simple (sans chiffrement pour l'instant)
$backupDir = "$backupBase\$BackupType"
$backupPath = "$backupDir\$backupName.zip"

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

# Utiliser Compress-Archive de PowerShell
Compress-Archive -Path $pathsToBackup -DestinationPath $backupPath -Force

if (Test-Path $backupPath) {
    Write-Host "OK Sauvegarde creee: $backupPath" -ForegroundColor Green

    # Calculer le hash de vÃ©rification
    $fileHash = Get-FileHash -Path $backupPath -Algorithm SHA256
    "$backupName.zip|$($fileHash.Hash)" | Out-File -FilePath "$backupDir\backup_manifest.txt" -Append

    # Nettoyer les anciennes sauvegardes (garder 7 jours pour daily)
    $oldBackups = Get-ChildItem $backupDir -Filter "*.zip" |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }

    foreach ($oldBackup in $oldBackups) {
        Remove-Item $oldBackup.FullName -Force
        Write-Host "  Nettoye: $($oldBackup.Name)" -ForegroundColor Gray
    }

    Write-Host "OK Sauvegarde terminee" -ForegroundColor Green
} else {
    Write-Error "Echec de la creation de la sauvegarde"
    exit 1
}

# Log de la sauvegarde
$logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $BackupType backup completed: $backupName"
$logEntry | Out-File -FilePath "$backupBase\logs\backup.log" -Append
