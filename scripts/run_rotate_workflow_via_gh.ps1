<#
Trigger the Rotate & Test (Staging) workflow via GH CLI with supplied inputs.

Usage:
  .\scripts\run_rotate_workflow_via_gh.ps1 -Owner youneselfakir0 -Repo TwisterLab -Apply false -RotateGrafana true -GrafanaServiceName twisterlab_monitoring_grafana

Notes:
 - Requires `gh` CLI authenticated via `gh auth login`.
 - This script triggers the GitHub Actions workflow and prints the run URL.
#>

param(
    [Parameter(Mandatory=$true)][string]$Owner,
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter()][string]$Environment = "staging",
    [Parameter()][bool]$Apply = $false,
    [Parameter()][bool]$Canary = $false,
    [Parameter()][string]$CanaryService = "",
    [Parameter()][bool]$RotatePostgres = $true,
    [Parameter()][bool]$RotateRedis = $true,
    [Parameter()][bool]$RotateGrafana = $true,
    [Parameter()][bool]$RestartGrafana = $false,
    [Parameter()][string]$GrafanaServiceName = "",
    [Parameter()][int]$WaitSeconds = 10
)

function Write-Log([string]$msg) { Write-Host "[run_rotate_workflow] $msg" }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Write-Host 'gh CLI not found. Please install and authenticate with `gh auth login`.' -ForegroundColor Red; exit 1 }

$repoSpec = "$Owner/$Repo"
Write-Log "Triggering Rotate & Test (Staging) on $repoSpec (dry-run if Apply = false)"

$fields = @(
    "environment=$Environment",
    "apply=$([string]$Apply).ToLower()",
    "canary=$([string]$Canary).ToLower()",
    "canary_service=$CanaryService",
    "rotate_postgres=$([string]$RotatePostgres).ToLower()",
    "rotate_redis=$([string]$RotateRedis).ToLower()",
    "rotate_grafana=$([string]$RotateGrafana).ToLower()",
    "restart_grafana=$([string]$RestartGrafana).ToLower()",
    "grafana_service_name=$GrafanaServiceName"
)

$cmd = "gh workflow run rotate-staging.yml --repo $repoSpec"
foreach ($f in $fields) { $cmd += " --field $f" }

Write-Log "Executing: $cmd"
Invoke-Expression $cmd

Start-Sleep -Seconds $WaitSeconds
Write-Log "Use 'gh run list --repo $repoSpec' to check runs, and 'gh run view <run-id> --repo $repoSpec' to inspect the run and logs."
