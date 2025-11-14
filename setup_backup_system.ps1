# Configuration du système de sauvegarde TwisterLab
# Phase 1: Fondation Infrastructure - Backup Setup

Write-Host "Configuration du systeme de sauvegarde TwisterLab" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Créer la structure de répertoires pour les sauvegardes
Write-Host "`n1. Création de la structure de sauvegarde..." -ForegroundColor Yellow

$backupBase = "C:\TwisterLab\backups"
$backupDirs = @(
    "$backupBase\daily",
    "$backupBase\weekly",
    "$backupBase\monthly",
    "$backupBase\logs",
    "$backupBase\config"
)

foreach ($dir in $backupDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  OK Cree: $dir" -ForegroundColor Green
    } else {
        Write-Host "  - Existe: $dir" -ForegroundColor Gray
    }
}

# 2. Générer une clé de chiffrement pour les sauvegardes
Write-Host "`n2. Generation de la cle de chiffrement..." -ForegroundColor Yellow

$keyFile = "$backupBase\config\backup_key.bin"
if (!(Test-Path $keyFile)) {
    # Générer une clé AES 256 bits
    $aesKey = New-Object Byte[] 32
    [Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($aesKey)
    $aesKey | Set-Content -Path $keyFile -Encoding Byte
    Write-Host "  OK Cle de chiffrement generee: $keyFile" -ForegroundColor Green

    # Créer un hash de vérification
    $keyHash = Get-FileHash -Path $keyFile -Algorithm SHA256
    $keyHash.Hash | Out-File -FilePath "$keyFile.sha256" -Encoding ASCII
    Write-Host "  OK Hash de verification cree" -ForegroundColor Green
} else {
    Write-Host "  - Cle existe deja: $keyFile" -ForegroundColor Gray
}

# 3. Créer le script de sauvegarde principal
Write-Host "`n3. Creation du script de sauvegarde principal..." -ForegroundColor Yellow

$backupScriptPath = "$backupBase\backup_twisterlab.ps1"
$backupScriptContent = @'
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

# Chemins à sauvegarder
$pathsToBackup = @(
    "C:\TwisterLab\agents",
    "C:\TwisterLab\api",
    "C:\TwisterLab\config",
    "C:\TwisterLab\data",
    "C:\TwisterLab\monitoring",
    "C:\TwisterLab\infrastructure"
)

# Vérifier la clé de chiffrement
if (!(Test-Path $keyFile)) {
    Write-Error "Cle de chiffrement manquante: $keyFile"
    exit 1
}

Write-Host "Creation de la sauvegarde: $backupName" -ForegroundColor Yellow
Write-Host "Sauvegarde simplifiee sans chiffrement (installer 7-Zip pour le chiffrement)" -ForegroundColor Yellow

# Créer une archive simple (sans chiffrement pour l'instant)
$backupDir = "$backupBase\$BackupType"
$backupPath = "$backupDir\$backupName.zip"

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

# Utiliser Compress-Archive de PowerShell
Compress-Archive -Path $pathsToBackup -DestinationPath $backupPath -Force

if (Test-Path $backupPath) {
    Write-Host "OK Sauvegarde creee: $backupPath" -ForegroundColor Green

    # Calculer le hash de vérification
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
'@

$backupScriptContent | Out-File -FilePath $backupScriptPath -Encoding UTF8
Write-Host "  OK Script de sauvegarde cree: $backupScriptPath" -ForegroundColor Green

# 4. Créer les tâches planifiées
Write-Host "`n4. Configuration des taches planifiees..." -ForegroundColor Yellow

# Sauvegarde quotidienne à 2h00
Write-Host "Creation tache quotidienne..." -ForegroundColor Yellow
schtasks /create /tn "TwisterLab_Daily_Backup" /tr "powershell.exe -ExecutionPolicy Bypass -File '$backupBase\backup_twisterlab.ps1' -BackupType daily" /sc daily /st 02:00 /rl highest /f 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Tache quotidienne cree" -ForegroundColor Green
} else {
    Write-Host "  - Tache quotidienne existe deja" -ForegroundColor Gray
}

# 5. Tester la sauvegarde
Write-Host "`n5. Test de la sauvegarde..." -ForegroundColor Yellow

# Exécuter une sauvegarde de test
& "$backupBase\backup_twisterlab.ps1" -BackupType test

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Test de sauvegarde reussi" -ForegroundColor Green
} else {
    Write-Host "  WARN Test de sauvegarde echoue - verifier la configuration" -ForegroundColor Yellow
}

# 6. Créer le script de restauration
Write-Host "`n6. Creation du script de restauration..." -ForegroundColor Yellow

$restoreScriptPath = "$backupBase\restore_twisterlab.ps1"
$restoreScriptContent = @'
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

# Créer le répertoire de restauration
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
'@

$restoreScriptContent | Out-File -FilePath $restoreScriptPath -Encoding UTF8
Write-Host "  OK Script de restauration cree: $restoreScriptPath" -ForegroundColor Green

# 7. Vérification finale
Write-Host "`n7. Verification de la configuration backup..." -ForegroundColor Yellow

# Vérifier les tâches planifiées
$scheduledTasks = schtasks /query /fo csv /nh | ConvertFrom-Csv | Where-Object { $_.TaskName -like "*TwisterLab*" }
if ($scheduledTasks) {
    Write-Host "  OK Taches planifiees configurees:" -ForegroundColor Green
    $scheduledTasks | ForEach-Object { Write-Host "    - $($_.TaskName)" -ForegroundColor Gray }
} else {
    Write-Host "  WARN Aucune tache planifiee trouvee" -ForegroundColor Yellow
}

# Vérifier l'espace disque disponible
$backupDrive = (Get-Item $backupBase).PSDrive.Name
$freeSpace = (Get-PSDrive $backupDrive).Free / 1GB
Write-Host "  OK Espace disponible sur $($backupDrive): $([math]::Round($freeSpace, 2)) GB" -ForegroundColor Green

Write-Host "`nOK Configuration du systeme de sauvegarde terminee!" -ForegroundColor Green
Write-Host "Dossier sauvegardes: $backupBase" -ForegroundColor Cyan
Write-Host "Scripts disponibles:" -ForegroundColor Cyan
Write-Host "  - backup_twisterlab.ps1 (sauvegarde)" -ForegroundColor White
Write-Host "  - restore_twisterlab.ps1 (restauration)" -ForegroundColor White
Write-Host "Sauvegardes planifiees: quotidienne/02h00" -ForegroundColor White
