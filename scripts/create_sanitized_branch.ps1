<#
Create a sanitized branch containing sanitized copies of files containing leaked secrets.
This script runs the `scripts/sanitize_archives.py --apply` command and creates a PR branch with the sanitized files.
It does NOT automatically push to main - it creates a branch and pushes it to origin for review.

Usage:
  .\scripts\create_sanitized_branch.ps1 [-BranchName sanitized/archives-YYYYMMDD] [-BackupDir sanitized_archives] [-DryRun]

Note: This script requires Git to be installed and the working directory to be a git repository.
#>

param(
    [string]$BranchName = "sanitized/archives-$(Get-Date -Format yyyyMMdd)",
    [string]$BackupDir = "sanitized_archives",
    [switch]$DryRun
)

Write-Host "Running sanitize script..." -ForegroundColor Cyan
if ($DryRun) { Write-Host "Dry run mode: no files will be written or pushed." -ForegroundColor Yellow }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Push-Location $root

try {
    # Run sanitization - always write results to a backup dir
    if ($DryRun) {
        python "$root\scripts\sanitize_archives.py" --apply --backup-dir $BackupDir --quiet
        Write-Host "Sanitization completed (dry-run)." -ForegroundColor Yellow
        return
    }

    python "$root\scripts\sanitize_archives.py" --apply --backup-dir $BackupDir

    if (!(Test-Path $BackupDir)) {
        Write-Host "No sanitized files found in $BackupDir. Aborting." -ForegroundColor Red
        return 1
    }

    $branch = $BranchName
    # Create new branch
    git checkout -b $branch

    # Copy back sanitized files to repo and create commits
    # Copy files from backup dir to repo, preserving structure
    Get-ChildItem -Path $BackupDir -Recurse -File | ForEach-Object {
        $dest = Join-Path -Path $root -ChildPath ($_.FullName.Substring($(Resolve-Path $BackupDir).Path.Length+1))
        Copy-Item -Path $_.FullName -Destination $dest -Force
    }

    git add .
    $commitMessage = "chore: sanitize archived files - remove hard-coded secrets (automated)"
    git commit -m $commitMessage
    git push -u origin $branch
    Write-Host "Sanitized branch created and pushed: $branch" -ForegroundColor Green
    Write-Host "Please open a PR for review before merging." -ForegroundColor Green

} catch {
    Write-Host "Failed to create sanitized branch: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

return 0
