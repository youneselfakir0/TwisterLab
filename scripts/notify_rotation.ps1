<#
Notify stakeholders about secret rotation and changes.
This uses `gh` CLI to create an issue or add a comment to an existing PR.

Usage:
  .\scripts\notify_rotation.ps1 -Secret grafana_admin_password -LogFile logs/rotate_grafana_20251116.log -Method issue

#>
param(
    [Parameter(Mandatory = $true)] [string]$Secret,
    [Parameter(Mandatory = $false)] [string]$LogFile = "",
    [ValidateSet("issue", "pr_comment")] [string]$Method = "issue",
    [int]$PrNumber = 0
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "gh CLI not found. Install GitHub CLI to enable automated notifications." -ForegroundColor Yellow
    return 1
}

$title = "Secret rotation: $Secret rotated"
$body = "Secret $Secret rotated on $(Get-Date)."
if ($LogFile -ne "" -and (Test-Path $LogFile)) {
    $details = Get-Content $LogFile -Raw
    $body += "`n`nRotation logs:`n```
$details
```
"
}

if ($Method -eq "issue") {
    gh issue create --title "$title" --body "$body" | Out-Null
    Write-Host "Created GitHub issue for rotation of $Secret" -ForegroundColor Green
} else {
    if ($PrNumber -eq 0) {
        Write-Host "PR number must be provided for PR comment method" -ForegroundColor Red
        return 1
    }
    gh pr comment $PrNumber --body "$body" | Out-Null
    Write-Host "Added PR comment on PR #$PrNumber for rotation of $Secret" -ForegroundColor Green
}

exit 0
