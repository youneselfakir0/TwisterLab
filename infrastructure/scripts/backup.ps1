# TwisterLab Automated Backup Script
# Version: 1.0.0
# Date: 2025-11-15

param(
    [switch]$Full,
    [string]$BackupPath = "$env:USERPROFILE\TwisterLab_Backups",
    [int]$RetentionDays = 7,
    [switch]$Compress,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "twisterlab_backup_$Timestamp"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path "$BackupPath\backup.log" -Value $LogMessage
}

function New-BackupDirectory {
    if (!(Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
        Write-Log "Created backup directory: $BackupPath"
    }
}

function Backup-Database {
    Write-Log "Starting database backup..."

    try {
        # Create database dump
        $dumpFile = "$BackupPath\$BackupName`_db.sql"
        $envFile = "$ProjectRoot\infrastructure\configs\.env.production"

        # Load environment variables
        if (Test-Path $envFile) {
            $envContent = Get-Content $envFile | Where-Object { $_ -match '^POSTGRES_' }
            $envVars = @{}
            foreach ($line in $envContent) {
                if ($line -match '^POSTGRES_([^=]+)=(.*)$') {
                    $envVars[$1] = $2
                }
            }
        }

        $dbHost = $envVars['POSTGRES_HOST'] ?: "192.168.0.30"
        $dbPort = $envVars['POSTGRES_PORT'] ?: "5432"
        $dbName = $envVars['POSTGRES_DB'] ?: "twisterlab_prod"
        $dbUser = $envVars['POSTGRES_USER'] ?: "twisterlab"

        # Use docker to create backup
        $containerId = docker ps -q -f name=twisterlab_postgres
        if ($containerId) {
            Write-Log "Creating PostgreSQL dump..."
            & docker exec $containerId pg_dump -U $dbUser -d $dbName > $dumpFile

            if ($Compress) {
                Write-Log "Compressing database backup..."
                Compress-Archive -Path $dumpFile -DestinationPath "$dumpFile.zip" -Force
                Remove-Item $dumpFile -Force
                $dumpFile = "$dumpFile.zip"
            }

            Write-Log "Database backup completed: $dumpFile"
            return $dumpFile
        } else {
            Write-Log "PostgreSQL container not found" -Level "ERROR"
            return $null
        }
    }
    catch {
        Write-Log "Database backup failed: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

function Backup-Volumes {
    Write-Log "Starting volume backup..."

    try {
        $volumeBackupPath = "$BackupPath\$BackupName`_volumes"

        # Backup PostgreSQL data
        Write-Log "Backing up PostgreSQL data volume..."
        & docker run --rm -v postgres_data:/data -v ${volumeBackupPath}:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .

        # Backup Redis data
        Write-Log "Backing up Redis data volume..."
        & docker run --rm -v redis_data:/data -v ${volumeBackupPath}:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .

        if ($Compress) {
            Write-Log "Compressing volume backups..."
            Compress-Archive -Path $volumeBackupPath -DestinationPath "$volumeBackupPath.zip" -Force
            Remove-Item $volumeBackupPath -Recurse -Force
            $volumeBackupPath = "$volumeBackupPath.zip"
        }

        Write-Log "Volume backup completed: $volumeBackupPath"
        return $volumeBackupPath
    }
    catch {
        Write-Log "Volume backup failed: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

function Backup-Configuration {
    Write-Log "Starting configuration backup..."

    try {
        $configBackupPath = "$BackupPath\$BackupName`_config"

        # Backup configuration files
        $configFiles = @(
            "infrastructure\docker\docker-compose.unified.yml",
            "infrastructure\configs\.env.production",
            "infrastructure\configs\.env.staging",
            "infrastructure\docker\postgresql.conf"
        )

        foreach ($file in $configFiles) {
            $sourcePath = Join-Path $ProjectRoot $file
            if (Test-Path $sourcePath) {
                $destPath = Join-Path $configBackupPath $file
                $destDir = Split-Path $destPath -Parent
                if (!(Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item $sourcePath $destPath -Force
            }
        }

        if ($Compress) {
            Write-Log "Compressing configuration backup..."
            Compress-Archive -Path $configBackupPath -DestinationPath "$configBackupPath.zip" -Force
            Remove-Item $configBackupPath -Recurse -Force
            $configBackupPath = "$configBackupPath.zip"
        }

        Write-Log "Configuration backup completed: $configBackupPath"
        return $configBackupPath
    }
    catch {
        Write-Log "Configuration backup failed: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

function Clear-OldBackups {
    Write-Log "Cleaning up old backups (retention: $RetentionDays days)..."

    try {
        $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
        $oldBackups = Get-ChildItem $BackupPath -File | Where-Object {
            $_.Name -match '^twisterlab_backup_\d{8}_\d{6}' -and
            $_.LastWriteTime -lt $cutoffDate
        }

        foreach ($backup in $oldBackups) {
            Write-Log "Removing old backup: $($backup.Name)" -Level "DEBUG"
            Remove-Item $backup.FullName -Force
        }

        Write-Log "Cleanup completed. Removed $($oldBackups.Count) old backups"
    }
    catch {
        Write-Log "Cleanup failed: $($_.Exception.Message)" -Level "ERROR"
    }
}

function Get-BackupSummary {
    param([array]$BackupFiles)

    $totalSize = 0
    foreach ($file in $BackupFiles) {
        if ($file -and (Test-Path $file)) {
            $totalSize += (Get-Item $file).Length
        }
    }

    return @{
        FileCount = ($BackupFiles | Where-Object { $_ }).Count
        TotalSize = [math]::Round($totalSize / 1MB, 2)
        BackupPath = $BackupPath
    }
}

# Main execution
try {
    Write-Log "=== TwisterLab Automated Backup Started ==="
    Write-Log "Backup path: $BackupPath"
    Write-Log "Full backup: $Full"
    Write-Log "Compression: $Compress"
    Write-Log "Retention: $RetentionDays days"

    New-BackupDirectory

    $backupFiles = @()

    # Always backup database
    $dbBackup = Backup-Database
    if ($dbBackup) { $backupFiles += $dbBackup }

    if ($Full) {
        # Full backup includes volumes and configuration
        $volumeBackup = Backup-Volumes
        if ($volumeBackup) { $backupFiles += $volumeBackup }

        $configBackup = Backup-Configuration
        if ($configBackup) { $backupFiles += $configBackup }
    }

    # Cleanup old backups
    Clear-OldBackups

    # Summary
    $summary = Get-BackupSummary -BackupFiles $backupFiles
    Write-Log "=== Backup completed successfully ==="
    Write-Log "Files created: $($summary.FileCount)"
    Write-Log "Total size: $($summary.TotalSize) MB"
    Write-Log "Backup location: $($summary.BackupPath)"

} catch {
    Write-Log "Backup failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
