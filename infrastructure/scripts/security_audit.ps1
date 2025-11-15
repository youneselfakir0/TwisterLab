# TwisterLab Security Audit Script
# Version: 1.0.0
# Date: 2025-11-15

param(
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
}

function Invoke-SecurityAudit {
    Write-Log "=== TwisterLab Security Audit ==="

    $issues = @()

    # Check for hardcoded passwords in compose files
    $composeFiles = Get-ChildItem -Path $ProjectRoot -Filter "docker-compose*.yml" -Recurse
    foreach ($file in $composeFiles) {
        $content = Get-Content $file.FullName -Raw

        # Check for hardcoded passwords
        if ($content -match 'GF_SECURITY_ADMIN_PASSWORD=admin') {
            $issues += @{
                File = $file.FullName
                Type = "Hardcoded Grafana Password"
                Severity = "Critical"
                Description = "Grafana admin password is set to 'admin'"
            }
        }

        if ($content -match 'twisterlab_prod_db_password_2024') {
            $issues += @{
                File = $file.FullName
                Type = "Hardcoded Database Password"
                Severity = "Critical"
                Description = "PostgreSQL password is hardcoded in compose file"
            }
        }

        if ($content -match 'twisterlab_prod_redis_password_2024') {
            $issues += @{
                File = $file.FullName
                Type = "Hardcoded Redis Password"
                Severity = "Critical"
                Description = "Redis password is hardcoded in compose file"
            }
        }
    }

    # Check for latest image tags
    foreach ($file in $composeFiles) {
        $content = Get-Content $file.FullName -Raw

        if ($content -match ':latest') {
            $issues += @{
                File = $file.FullName
                Type = "Unversioned Docker Images"
                Severity = "High"
                Description = "Using :latest tag can lead to unpredictable deployments"
            }
        }
    }

    # Check Docker Swarm secrets
    try {
        $swarmStatus = docker info --format "{{.Swarm.LocalNodeState}}"
        if ($swarmStatus -eq "active") {
            $existingSecrets = docker secret ls --format "{{.Name}}"
            $expectedSecrets = @("grafana_admin_password", "postgres_password", "redis_password")

            foreach ($secret in $expectedSecrets) {
                if ($existingSecrets -notcontains $secret) {
                    $issues += @{
                        File = "Docker Swarm"
                        Type = "Missing Docker Secret"
                        Severity = "Critical"
                        Description = "Required secret '$secret' is not created in Docker Swarm"
                    }
                }
            }
        } else {
            $issues += @{
                File = "Docker Swarm"
                Type = "Swarm Not Active"
                Severity = "High"
                Description = "Docker Swarm is not active - cannot use Docker Secrets"
            }
        }
    } catch {
        $issues += @{
            File = "Docker"
            Type = "Docker Not Available"
            Severity = "High"
            Description = "Cannot check Docker/Swarm status: $($_.Exception.Message)"
        }
    }

    # Report findings
    Write-Log "=== Security Audit Results ==="
    Write-Log "Total issues found: $($issues.Count)"

    $criticalIssues = $issues | Where-Object { $_.Severity -eq "Critical" }
    $highIssues = $issues | Where-Object { $_.Severity -eq "High" }

    Write-Log "Critical issues: $($criticalIssues.Count)"
    Write-Log "High severity issues: $($highIssues.Count)"

    if ($issues.Count -gt 0) {
        Write-Log ""
        Write-Log "Issues found:" -Level "WARNING"
        foreach ($issue in $issues) {
            Write-Log "  [$($issue.Severity)] $($issue.Type)" -Level "WARNING"
            Write-Log "    File: $($issue.File)" -Level "WARNING"
            Write-Log "    Description: $($issue.Description)" -Level "WARNING"
            Write-Log ""
        }

        Write-Log "RECOMMENDED ACTIONS:" -Level "WARNING"
        Write-Log "1. Create Docker Secrets for sensitive data" -Level "WARNING"
        Write-Log "2. Update compose files to use secrets instead of hardcoded passwords" -Level "WARNING"
        Write-Log "3. Version all Docker images (avoid :latest)" -Level "WARNING"
        Write-Log "4. Ensure Docker Swarm is active for secrets management" -Level "WARNING"

        return $false
    } else {
        Write-Log "No security issues found!" -Level "INFO"
        return $true
    }
}

# Main execution
try {
    Write-Log "=== TwisterLab Security Audit Script ==="
    Invoke-SecurityAudit

} catch {
    Write-Log "Security audit failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
