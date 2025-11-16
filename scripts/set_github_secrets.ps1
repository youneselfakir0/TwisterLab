<#
Set GitHub repository secrets using the `gh` CLI.

Usage:
  .\scripts\set_github_secrets.ps1 -Owner youneselfakir0 -Repo TwisterLab -StagingKeyPath ./ssh_key -StagingHost 192.0.2.10 -StagingUser deploy -StagingPort 22 -StagingDir /home/deploy/twisterlab

Notes:
 - Requires `gh` CLI authenticated via `gh auth login`.
 - Accepts a path to a file for private key input.
#>

param(
    [Parameter(Mandatory=$true)][string]$Owner,
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][string]$StagingHost,
    [Parameter(Mandatory=$true)][string]$StagingUser,
    [Parameter(Mandatory=$false)][string]$StagingPort = "22",
    [Parameter(Mandatory=$true)][string]$StagingDir,
    [Parameter(Mandatory=$false)][string]$StagingKeyPath = ""
)

function Write-Log([string]$msg) { Write-Host "[set_github_secrets] $msg" }

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Write-Host 'gh CLI not found. Please install and authenticate with `gh auth login`.' -ForegroundColor Red; exit 1 }

$repoSpec = "$Owner/$Repo"

if ($StagingKeyPath -and (Test-Path $StagingKeyPath)) {
    Write-Log "Reading SSH private key from $StagingKeyPath"
    $keyVal = Get-Content -Path $StagingKeyPath -Raw
} else {
    $keyVal = Read-Host -Prompt "Enter STAGING_SSH_PRIVATE_KEY content (paste)" -AsSecureString
    $keyVal = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($keyVal))
}

Write-Log "Setting STAGING_SSH_PRIVATE_KEY"
gh secret set STAGING_SSH_PRIVATE_KEY --body "$keyVal" --repo $repoSpec

Write-Log "Setting STAGING_SSH_HOST"
gh secret set STAGING_SSH_HOST --body "$StagingHost" --repo $repoSpec

Write-Log "Setting STAGING_SSH_USER"
gh secret set STAGING_SSH_USER --body "$StagingUser" --repo $repoSpec

Write-Log "Setting STAGING_SSH_PORT"
gh secret set STAGING_SSH_PORT --body "$StagingPort" --repo $repoSpec

Write-Log "Setting STAGING_SSH_DEPLOY_DIR"
gh secret set STAGING_SSH_DEPLOY_DIR --body "$StagingDir" --repo $repoSpec

Write-Log "Done: GitHub secrets updated (ensure the GH user has repo admin perms)."
