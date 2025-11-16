# TwisterLab Automated Restore Script
# Version: 1.0.0
# Date: 2025-11-15

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupName,
    [string]$BackupPath = "$env:USERPROFILE\TwisterLab_Backups",
    [switch]$DatabaseOnly,
    [switch]$VolumesOnly,
    [switch]$ConfigOnly,
    [switch]$DryRun,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path "$BackupPath\restore.log" -Value $LogMessage
}

function Find-BackupFiles {
    param([string]$BackupName)

    $files = @{}

    # Find database backup
    $dbPattern = "$BackupName*_db.sql*"
    $dbFile = Get-ChildItem $BackupPath -File -Filter $dbPattern | Select-Object -First 1
    if ($dbFile) {
        $files.Database = $dbFile.FullName
    }

    # Find volume backup
    $volumePattern = "$BackupName*_volumes*"
    $volumeFile = Get-ChildItem $BackupPath -File -Filter $volumePattern | Select-Object -First 1
    if ($volumeFile) {
        $files.Volumes = $volumeFile.FullName
    }

    # Find config backup
    $configPattern = "$BackupName*_config*"
    $configFile = Get-ChildItem $BackupPath -File -Filter $configPattern | Select-Object -First 1
    if ($configFile) {
        $files.Config = $configFile.FullName
    }

    return $files
}

function Restore-Database {
    param([string]$BackupFile)

    Write-Log "Starting database restore from: $BackupFile"

    if ($DryRun) {
        Write-Log "[DRY RUN] Would restore database from $BackupFile"
        return $true
    }

    try {
        # Stop dependent services
        Write-Log "Stopping dependent services..."
        & docker service scale twisterlab_api=0
        Start-Sleep -Seconds 10

        # Load environment variables
        $envFile = "$ProjectRoot\infrastructure\configs\.env.production"
        if (Test-Path $envFile) {
            $envContent = Get-Content $envFile | Where-Object { $_ -match '^POSTGRES_' }
            $envVars = @{}
            foreach ($line in $envContent) {
                if ($line -match '^POSTGRES_([^=]+)=(.*)$') {
                    $envVars[$1] = $2
                }
            }
        }

        $dbUser = $envVars['POSTGRES_USER'] ?: "twisterlab"

        # Handle compressed files
        $tempFile = $null
        if ($BackupFile -like "*.zip") {
            Write-Log "Extracting compressed database backup..."
            $tempFile = "$env:TEMP\twisterlab_restore_db.sql"
            Expand-Archive -Path $BackupFile -DestinationPath $env:TEMP -Force
            $extractedFile = Get-ChildItem $env:TEMP -Filter "*_db.sql" | Select-Object -First 1
            if ($extractedFile) {
                Move-Item $extractedFile.FullName $tempFile -Force
            } else {
                throw "Could not find extracted database file"
            }
            $BackupFile = $tempFile
        }

        # Restore database
        $containerId = docker ps -q -f name=twisterlab_postgres
        if ($containerId) {
            Write-Log "Restoring PostgreSQL database..."
            Get-Content $BackupFile | docker exec -i $containerId psql -U $dbUser -d twisterlab_prod

            Write-Log "Database restore completed"
            $result = $true
        } else {
            Write-Log "PostgreSQL container not found" -Level "ERROR"
            $result = $false
        }

        # Cleanup temp file
        if ($tempFile -and (Test-Path $tempFile)) {
            Remove-Item $tempFile -Force
        }

        # Restart services
        if (!$DryRun) {
            Write-Log "Restarting services..."
            & docker service scale twisterlab_api=1
        }

        return $result

    } catch {
        Write-Log "Database restore failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Restore-Volumes {
    param([string]$BackupFile)

    Write-Log "Starting volume restore from: $BackupFile"

    if ($DryRun) {
        Write-Log "[DRY RUN] Would restore volumes from $BackupFile"
        return $true
    }

    try {
        # Stop all services
        Write-Log "Stopping all services for volume restore..."
        & docker service scale twisterlab_api=0 twisterlab_redis=0
        Start-Sleep -Seconds 15

        $tempDir = $null
        if ($BackupFile -like "*.zip") {
            Write-Log "Extracting compressed volume backup..."
            $tempDir = "$env:TEMP\twisterlab_restore_volumes"
            Expand-Archive -Path $BackupFile -DestinationPath $tempDir -Force
        } else {
            $tempDir = Split-Path $BackupFile -Parent
        }

        # Restore PostgreSQL data
        $postgresBackup = Join-Path $tempDir "postgres_data.tar.gz"
        if (Test-Path $postgresBackup) {
            Write-Log "Restoring PostgreSQL volume..."
            & docker run --rm -v postgres_data:/data -v ${tempDir}:/backup alpine sh -c "cd /data && tar xzf /backup/postgres_data.tar.gz --strip-components=1"
        }

        # Restore Redis data
        $redisBackup = Join-Path $tempDir "redis_data.tar.gz"
        if (Test-Path $redisBackup) {
            Write-Log "Restoring Redis volume..."
            & docker run --rm -v redis_data:/data -v ${tempDir}:/backup alpine sh -c "cd /data && tar xzf /backup/redis_data.tar.gz --strip-components=1"
        }

        # Cleanup temp directory if we created it
        if ($BackupFile -like "*.zip" -and $tempDir -and (Test-Path $tempDir)) {
            Remove-Item $tempDir -Recurse -Force
        }

        Write-Log "Volume restore completed"
        $result = $true

        # Restart services
        Write-Log "Restarting services..."
        & docker service scale twisterlab_api=1 twisterlab_redis=1

        return $result

    } catch {
        Write-Log "Volume restore failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Restore-Configuration {
    param([string]$BackupFile)

    Write-Log "Starting configuration restore from: $BackupFile"

    if ($DryRun) {
        Write-Log "[DRY RUN] Would restore configuration from $BackupFile"
        return $true
    }

    try {
        $tempDir = $null
        if ($BackupFile -like "*.zip") {
            Write-Log "Extracting compressed configuration backup..."
            $tempDir = "$env:TEMP\twisterlab_restore_config"
            Expand-Archive -Path $BackupFile -DestinationPath $tempDir -Force
        } else {
            $tempDir = $BackupFile
        }

        # Restore configuration files
        $configFiles = @(
            "infrastructure\docker\docker-compose.unified.yml",
            "infrastructure\configs\.env.production",
            "infrastructure\configs\.env.staging",
            "infrastructure\docker\postgresql.conf"
        )

        foreach ($file in $configFiles) {
            $sourcePath = Join-Path $tempDir $file
            $destPath = Join-Path $ProjectRoot $file

            if (Test-Path $sourcePath) {
                $destDir = Split-Path $destPath -Parent
                if (!(Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item $sourcePath $destPath -Force -Verbose:$Verbose
                Write-Log "Restored: $file"
            }
        }

        # Cleanup temp directory if we created it
        if ($BackupFile -like "*.zip" -and $tempDir -and (Test-Path $tempDir)) {
            Remove-Item $tempDir -Recurse -Force
        }

        Write-Log "Configuration restore completed"
        return $true

    } catch {
        Write-Log "Configuration restore failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-RestorePrerequisites {
    # Check if Docker is running
    try {
        $null = docker version
    } catch {
        Write-Log "Docker is not running or not accessible" -Level "ERROR"
        return $false
    }

    # Check if services are running
    $services = docker service ls --format "{{.Name}}:{{.Replicas}}"
    if ($services -notmatch "twisterlab_postgres") {
        Write-Log "TwisterLab services are not running. Please start them first." -Level "ERROR"
        return $false
    }

    return $true
}

# Main execution
try {
    Write-Log "=== TwisterLab Automated Restore Started ==="
    Write-Log "Backup name: $BackupName"
    Write-Log "Backup path: $BackupPath"
    Write-Log "Database only: $DatabaseOnly"
    Write-Log "Volumes only: $VolumesOnly"
    Write-Log "Config only: $ConfigOnly"
    Write-Log "Dry run: $DryRun"

    # Validate prerequisites
    if (!(Test-RestorePrerequisites)) {
        exit 1
    }

    # Find backup files
    $backupFiles = Find-BackupFiles -BackupName $BackupName

    if ($backupFiles.Count -eq 0) {
        Write-Log "No backup files found for: $BackupName" -Level "ERROR"
        exit 1
    }

    Write-Log "Found backup files:"
    foreach ($key in $backupFiles.Keys) {
        Write-Log "  $key : $($backupFiles[$key])"
    }

    $restoreResults = @{}

    # Restore database (always included unless specific flags)
    if (!$VolumesOnly -and !$ConfigOnly) {
        if ($backupFiles.Database) {
            $restoreResults.Database = Restore-Database -BackupFile $backupFiles.Database
        } else {
            Write-Log "Database backup not found" -Level "WARNING"
        }
    }

    # Restore volumes
    if (!$DatabaseOnly -and !$ConfigOnly) {
        if ($backupFiles.Volumes) {
            $restoreResults.Volumes = Restore-Volumes -BackupFile $backupFiles.Volumes
        } else {
            Write-Log "Volume backup not found" -Level "WARNING"
        }
    }

    # Restore configuration
    if (!$DatabaseOnly -and !$VolumesOnly) {
        if ($backupFiles.Config) {
            $restoreResults.Config = Restore-Configuration -BackupFile $backupFiles.Config
        } else {
            Write-Log "Configuration backup not found" -Level "WARNING"
        }
    }

    # Summary
    $successCount = ($restoreResults.Values | Where-Object { $_ -eq $true }).Count
    $totalCount = $restoreResults.Count

    Write-Log "=== Restore completed ==="
    Write-Log "Successful restores: $successCount/$totalCount"

    if ($successCount -eq $totalCount) {
        Write-Log "All restores completed successfully"
        exit 0
    } else {
        Write-Log "Some restores failed" -Level "WARNING"
        exit 1
    }

} catch {
    Write-Log "Restore failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
