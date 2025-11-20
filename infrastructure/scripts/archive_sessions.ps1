<#
.SYNOPSIS
  Archive session files (SESSION_*, REPORT_*, RAPPORT_*) into docs/archive/sessions.
.DESCRIPTION
  Scans the repository for session/report files and moves (or copies) them into an archive
  folder while preserving directory structure relative to the repo root. Supports DryRun,
  backup mode (copy instead of move), and logs operations. Safe by default (DryRun = $true).
#>

param(
    [string]$RepoRoot = "C:\TwisterLab",
    [string]$ArchiveDir,
    [switch]$DryRun = $true,
    [switch]$Backup = $false,
    [string[]]$Patterns = @("SESSION_*.md", "SESSION-*.md", "REPORT_*.md", "REPORT-*.md", "RAPPORT_*.md", "RAPPORT-*.md")
)

try {
    $RepoRoot = (Resolve-Path -Path $RepoRoot).ProviderPath
} catch {
    Write-Error "Repo root not found: $RepoRoot"
    exit 1
}

if (-not $ArchiveDir) {
    $ArchiveDir = Join-Path -Path $RepoRoot -ChildPath "docs\archive\sessions"
}

$LogDir = Join-Path -Path $RepoRoot -ChildPath "docs\archive"
if (-not (Test-Path -Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$Timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$LogFile = Join-Path $LogDir ("archive_sessions_log_$Timestamp.txt")

# Build regex from patterns (case-insensitive)
$patternRegex = ($Patterns | ForEach-Object {
    $_ -replace '\*', '.*' -replace '[.-]', '[-_.]?'
}) -join '|'
$patternRegex = "(?i)^($patternRegex)$"

Write-Output "Repo root: $RepoRoot"
Write-Output "Archive dir: $ArchiveDir"
Write-Output "DryRun: $DryRun; Backup(copy): $Backup"
Write-Output "Patterns: $($Patterns -join ', ')"
Write-Output "Log: $LogFile"
"`n--- Start archive run: $Timestamp ---`n" | Out-File -FilePath $LogFile -Encoding UTF8

# Find files recursively (excluding files already in archive dir)
$allFiles = Get-ChildItem -Path $RepoRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { -not $_.FullName.StartsWith($ArchiveDir, [System.StringComparison]::InvariantCultureIgnoreCase) }
$files = @()
foreach ($p in $Patterns) {
    $files += $allFiles | Where-Object { $_.Name -ilike $p }
}
$files = $files | Sort-Object FullName -Unique

if (-not $files -or $files.Count -eq 0) {
    Write-Output "No session/report files found. Nothing to archive." | Tee-Object -FilePath $LogFile -Append
    exit 0
}

foreach ($file in $files) {
    try {
        # Relative path to preserve directory structure
        $relativePath = $file.FullName.Substring($RepoRoot.Length).TrimStart('\','/')
        $targetPath = Join-Path -Path $ArchiveDir -ChildPath $relativePath
        $targetDir = Split-Path -Path $targetPath -Parent

        # create target dir
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }

        # If the target file exists, append a short GUID suffix to avoid collision
        $finalTarget = $targetPath
        if (-not $DryRun -and (Test-Path -Path $finalTarget)) {
            $guid = [System.Guid]::NewGuid().ToString("N").Substring(0, 8)
            $base = [System.IO.Path]::GetFileNameWithoutExtension($finalTarget)
            $ext = [System.IO.Path]::GetExtension($finalTarget)
            $finalTarget = Join-Path -Path $targetDir -ChildPath ("$base.$guid$ext")
        } elseif ($DryRun -and (Test-Path -Path $finalTarget)) {
            $finalTarget += " (would append suffix for collision)"
        }

        $operation = if ($Backup) { "COPY" } else { "MOVE" }
        $message = "$operation `"$($file.FullName)`" -> `"$finalTarget`""
        Write-Output $message
        $message | Out-File -FilePath $LogFile -Append

        if (-not $DryRun) {
            if ($Backup) {
                Copy-Item -Path $file.FullName -Destination $finalTarget -Force
            } else {
                Move-Item -Path $file.FullName -Destination $finalTarget -Force
            }
            $null = (Get-Item -Path $finalTarget).LastWriteTime = $file.LastWriteTime
        }
    } catch {
        $err = "ERROR processing $($file.FullName): $($_.Exception.Message)"
        Write-Error $err
        $err | Out-File -FilePath $LogFile -Append
    }
}

if (-not $DryRun) {
    $archivedCount = (Get-ChildItem -Path $ArchiveDir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    "Archived file count: $archivedCount" | Out-File -FilePath $LogFile -Append
} else {
    "DryRun completed. No files moved." | Out-File -FilePath $LogFile -Append
}

Write-Output "`nDone. Log: $LogFile"
