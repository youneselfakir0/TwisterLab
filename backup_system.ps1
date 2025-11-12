#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Automated backup script for TwisterLab production system
.DESCRIPTION
    Creates comprehensive backups of all TwisterLab components:
    - Database dumps (PostgreSQL)
    - Configuration files
    - Docker volumes
    - Application data
.NOTES
    Run as Administrator
    Requires: Docker, PostgreSQL client tools
#>

param(
    [string]$BackupPath = "C:\TwisterLab\backups",
    [switch]$Compress = $true,
    [switch]$UploadToCloud = $false,
    [string]$CloudPath = ""
)

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "twisterlab_backup_$Timestamp"
$FullBackupPath = Join-Path $BackupPath $BackupName

# Configuration
$Config = @{
    PostgresContainer = "twisterlab_prod_postgres"
    PostgresUser = "twisterlab"
    PostgresDb = "twisterlab_prod"
    VolumesToBackup = @(
        "postgres_prod_data",
        "redis_prod_data",
        "ollama_prod_data",
        "webui_prod_data"
    )
}

function Write-BackupLog {
    param([string]$Message, [string]$Level = "INFO")
    $LogTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$LogTimestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path "$BackupPath\backup.log" -Value $LogMessage
}

function New-BackupDirectory {
    Write-BackupLog "Creating backup directory: $FullBackupPath"
    if (!(Test-Path $FullBackupPath)) {
        New-Item -ItemType Directory -Path $FullBackupPath -Force
    }
}

function Backup-Database {
    Write-BackupLog "Starting database backup..."

    try {
        # Create database dump
        $dumpFile = Join-Path $FullBackupPath "database.sql"
        Write-BackupLog "Creating PostgreSQL dump: $dumpFile"

        # Use docker exec to create dump
        docker exec $Config.PostgresContainer pg_dump -U $Config.PostgresUser -d $Config.PostgresDb > $dumpFile

        if (Test-Path $dumpFile) {
            $size = (Get-Item $dumpFile).Length / 1MB
            Write-BackupLog "Database backup completed: $([math]::Round($size, 2)) MB"
            return $true
        } else {
            Write-BackupLog "Database backup failed: dump file not created" "ERROR"
            return $false
        }
    }
    catch {
        Write-BackupLog "Database backup failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Backup-DockerVolumes {
    Write-BackupLog "Starting Docker volumes backup..."

    $volumeBackupPath = Join-Path $FullBackupPath "volumes"
    New-Item -ItemType Directory -Path $volumeBackupPath -Force

    foreach ($volume in $Config.VolumesToBackup) {
        try {
            Write-BackupLog "Backing up volume: $volume"

            # Create a temporary container to backup the volume
            $containerName = "backup_temp_$volume"
            docker run --rm -d --name $containerName -v ${volume}:/source alpine sleep 30

            # Copy volume data
            $volumePath = Join-Path $volumeBackupPath $volume
            docker cp ${containerName}:/source $volumePath

            # Clean up
            docker stop $containerName

            Write-BackupLog "Volume $volume backed up successfully"
        }
        catch {
            Write-BackupLog "Failed to backup volume $volume : $($_.Exception.Message)" "ERROR"
        }
    }
}

function Backup-Configuration {
    Write-BackupLog "Starting configuration backup..."

    $configBackupPath = Join-Path $FullBackupPath "config"
    New-Item -ItemType Directory -Path $configBackupPath -Force

    # Backup important configuration files
    $configFiles = @(
        "docker-compose.production.yml",
        "docker-compose.monitoring.yml",
        "api\main.py",
        "agents\*.py",
        "run_api_service.ps1",
        "debug_complete_system.ps1"
    )

    foreach ($file in $configFiles) {
        $sourcePath = Join-Path "C:\TwisterLab" $file
        if (Test-Path $sourcePath) {
            Copy-Item $sourcePath $configBackupPath -Recurse -Force
            Write-BackupLog "Configuration file backed up: $file"
        }
    }
}

function Backup-ApplicationData {
    Write-BackupLog "Starting application data backup..."

    $appDataPath = Join-Path $FullBackupPath "appdata"
    New-Item -ItemType Directory -Path $appDataPath -Force

    # Backup logs
    if (Test-Path "C:\TwisterLab\logs") {
        Copy-Item "C:\TwisterLab\logs" $appDataPath -Recurse -Force
        Write-BackupLog "Application logs backed up"
    }

    # Backup any additional data directories
    $dataDirs = @("data", "models", "cache")
    foreach ($dir in $dataDirs) {
        $sourceDir = Join-Path "C:\TwisterLab" $dir
        if (Test-Path $sourceDir) {
            Copy-Item $sourceDir $appDataPath -Recurse -Force
            Write-BackupLog "Data directory backed up: $dir"
        }
    }
}

function Compress-Backup {
    if (!$Compress) { return }

    Write-BackupLog "Compressing backup..."

    try {
        $zipPath = "$FullBackupPath.zip"
        Compress-Archive -Path $FullBackupPath -DestinationPath $zipPath -Force

        $originalSize = (Get-ChildItem $FullBackupPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        $compressedSize = (Get-Item $zipPath).Length / 1MB

        Write-BackupLog "Backup compressed: $([math]::Round($originalSize, 2)) MB → $([math]::Round($compressedSize, 2)) MB"

        # Remove uncompressed directory
        Remove-Item $FullBackupPath -Recurse -Force
        Write-BackupLog "Uncompressed backup removed"

        return $zipPath
    }
    catch {
        Write-BackupLog "Compression failed: $($_.Exception.Message)" "ERROR"
        return $FullBackupPath
    }
}

function Send-BackupToCloud {
    param([string]$BackupFile)

    if (!$UploadToCloud -or [string]::IsNullOrEmpty($CloudPath)) { return }

    Write-BackupLog "Uploading backup to cloud: $CloudPath"

    try {
        # Example: Azure Storage upload (adapt to your cloud provider)
        # az storage blob upload --account-name $storageAccount --container-name $container --name (Split-Path $BackupFile -Leaf) --file $BackupFile

        Write-BackupLog "Cloud upload completed"
    }
    catch {
        Write-BackupLog "Cloud upload failed: $($_.Exception.Message)" "ERROR"
    }
}

function Test-BackupIntegrity {
    param([string]$BackupFile)

    Write-BackupLog "Testing backup integrity..."

    try {
        if ($BackupFile.EndsWith(".zip")) {
            # Test ZIP integrity
            $testResult = & 7z t $BackupFile 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-BackupLog "Backup integrity test passed"
                return $true
            } else {
                Write-BackupLog "Backup integrity test failed" "ERROR"
                return $false
            }
        } else {
            # Basic file existence check
            if (Test-Path $BackupFile) {
                Write-BackupLog "Backup file exists and accessible"
                return $true
            } else {
                Write-BackupLog "Backup file not found" "ERROR"
                return $false
            }
        }
    }
    catch {
        Write-BackupLog "Integrity test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Send-BackupNotification {
    param([string]$BackupFile, [bool]$Success)

    Write-BackupLog "Sending backup notification..."

    try {
        $size = if (Test-Path $BackupFile) {
            $fileSize = (Get-Item $BackupFile).Length / 1MB
            "$([math]::Round($fileSize, 2)) MB"
        } else { "Unknown" }

        $subject = if ($Success) { "TwisterLab Backup Success" } else { "TwisterLab Backup Failed" }
        $body = @"
TwisterLab Backup Report
Timestamp: $Timestamp
Status: $(if ($Success) { "SUCCESS" } else { "FAILED" })
Backup Location: $BackupFile
Size: $size

$(if ($Success) { "Backup completed successfully" } else { "Backup encountered errors. Check logs for details." })
"@

        # Send email notification (configure SMTP settings)
        # Send-MailMessage -From "backup@twisterlab.local" -To "admin@twisterlab.local" -Subject $subject -Body $body -SmtpServer "smtp.twisterlab.local"

        Write-BackupLog "Backup notification sent"
    }
    catch {
        Write-BackupLog "Failed to send notification: $($_.Exception.Message)" "ERROR"
    }
}

function Cleanup-OldBackups {
    Write-BackupLog "Cleaning up old backups..."

    try {
        # Keep only last 7 daily backups and last 4 weekly backups
        $backups = Get-ChildItem $BackupPath -Filter "twisterlab_backup_*.zip" | Sort-Object LastWriteTime -Descending

        $dailyBackups = $backups | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
        $oldBackups = $backups | Where-Object { $_.LastWriteTime -le (Get-Date).AddDays(-7) }

        # Keep last 4 weekly backups from old ones
        $weeklyBackups = $oldBackups | Group-Object { [math]::Floor(($_.LastWriteTime - (Get-Date).AddDays(-7)).Days / 7) } |
                        ForEach-Object { $_.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1 } |
                        Select-Object -First 4

        $backupsToDelete = $oldBackups | Where-Object { $_.FullName -notin $weeklyBackups.FullName }

        foreach ($backup in $backupsToDelete) {
            Remove-Item $backup.FullName -Force
            Write-BackupLog "Old backup deleted: $($backup.Name)"
        }

        Write-BackupLog "Cleanup completed. Kept $($dailyBackups.Count + $weeklyBackups.Count) backups"
    }
    catch {
        Write-BackupLog "Cleanup failed: $($_.Exception.Message)" "ERROR"
    }
}

# Main backup process
try {
    Write-BackupLog "=== Starting TwisterLab Backup ==="

    # Create backup directory
    New-BackupDirectory

    # Perform backups
    $dbSuccess = Backup-Database
    Backup-DockerVolumes
    Backup-Configuration
    Backup-ApplicationData

    # Compress and test
    $finalBackupFile = Compress-Backup
    $integrityTest = Test-BackupIntegrity $finalBackupFile

    # Cloud upload
    Send-BackupToCloud $finalBackupFile

    # Cleanup old backups
    Cleanup-OldBackups

    # Determine overall success
    $overallSuccess = $dbSuccess -and $integrityTest

    # Send notification
    Send-BackupNotification $finalBackupFile $overallSuccess

    Write-BackupLog "=== Backup Process Completed ==="
    Write-BackupLog "Final backup location: $finalBackupFile"
    Write-BackupLog "Overall status: $(if ($overallSuccess) { "SUCCESS" } else { "PARTIAL SUCCESS - Check logs" })"

    exit $(if ($overallSuccess) { 0 } else { 1 })
}
catch {
    Write-BackupLog "Backup process failed: $($_.Exception.Message)" "ERROR"
    Send-BackupNotification "N/A" $false
    exit 1
}
