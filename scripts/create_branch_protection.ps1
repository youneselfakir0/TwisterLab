<#
Use GitHub CLI to automate creation of branch protection rules for `main`.
Requires: `gh` CLI and appropriate permissions (repo admin). Prompts for confirmation if not provided.

Usage: .\scripts\create_branch_protection.ps1 [-RequireChecks @('ci','secret-scan.yml')] [-RequireReviews 1]
#>
param(
    [string[]]$RequireChecks = @("ci", "secret-scan.yml"),
    [int]$RequireReviews = 1
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "gh CLI not found. Install GitHub CLI to continue." -ForegroundColor Red
    exit 1
}

$repo = (gh repo view --json nameWithOwner -q .nameWithOwner) -replace '"',''
Write-Host "Configuring branch protection for $repo/main" -ForegroundColor Cyan

$rules = @{ required_status_checks = @{ strict = $true; contexts = $RequireChecks }; required_pull_request_reviews = @{ required_approving_review_count = $RequireReviews }; enforce_admins = $false }

$payload = $rules | ConvertTo-Json -Depth 10

Write-Host "Applying branch protection (requires admin privileges)" -ForegroundColor Yellow
gh api --method PUT -H "Accept: application/vnd.github+json" /repos/$repo/branches/main/protection -f "$payload" | Out-Null
Write-Host "Branch protection updated for main with status checks: $($RequireChecks -join ', ') and required reviews: $RequireReviews" -ForegroundColor Green

exit 0
