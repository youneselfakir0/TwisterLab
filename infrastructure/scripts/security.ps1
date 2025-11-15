# TwisterLab Security Hardening Script
# Version: 1.0.0
# Date: 2025-11-15

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("create-secrets", "update-compose", "validate-secrets", "rotate-passwords", "audit-security")]
    [string]$Action,
    [switch]$Force,
    [switch]$DryRun,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath

# Security configuration
$SecretsConfig = @{
    "grafana_admin_password" = @{
        Description = "Grafana admin password"
        DefaultValue = "TwisterLab_Grafana_Admin_2025!"
        Length = 24
    }
    "postgres_password" = @{
        Description = "PostgreSQL database password"
        DefaultValue = "TwisterLab_PostgreSQL_2025!"
        Length = 32
    }
    "redis_password" = @{
        Description = "Redis cache password"
        DefaultValue = "TwisterLab_Redis_2025!"
        Length = 24
    }
    "prometheus_basic_auth" = @{
        Description = "Prometheus basic auth credentials"
        DefaultValue = "admin:TwisterLab_Prometheus_2025!"
        Length = 40
    }
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    if (!$Silent) {
        Write-Host $LogMessage
    }
}

function Generate-SecurePassword {
    param([int]$Length = 24)

    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    for ($i = 1; $i -le $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

function Test-DockerSwarm {
    try {
        $swarmStatus = docker info --format "{{.Swarm.LocalNodeState}}"
        if ($swarmStatus -eq "active") {
            Write-Log "Docker Swarm is active"
            return $true
        } else {
            Write-Log "Docker Swarm is not active. Please initialize Swarm first." -Level "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to check Docker Swarm status: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Get-ExistingSecrets {
    try {
        $secrets = docker secret ls --format "{{.Name}}"
        return $secrets -split "`n" | Where-Object { $_ -and $_.Trim() }
    } catch {
        Write-Log "Failed to list secrets: $($_.Exception.Message)" -Level "ERROR"
        return @()
    }
}

function Create-DockerSecret {
    param([string]$SecretName, [string]$Value, [string]$Description)

    if ($DryRun) {
        Write-Log "[DRY RUN] Would create secret: $SecretName ($Description)"
        return $true
    }

    try {
        # Remove existing secret if it exists and force is specified
        if ($Force) {
            docker secret rm $SecretName 2>$null | Out-Null
        }

        # Create new secret
        $Value | docker secret create $SecretName -
        Write-Log "Created secret: $SecretName ($Description)"
        return $true
    } catch {
        Write-Log "Failed to create secret $SecretName`: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Invoke-CreateSecrets {
    Write-Log "=== Creating Docker Secrets ==="

    if (!(Test-DockerSwarm)) {
        exit 1
    }

    $existingSecrets = Get-ExistingSecrets
    Write-Log "Existing secrets: $($existingSecrets -join ', ')"

    $createdCount = 0
    $skippedCount = 0

    foreach ($secretName in $SecretsConfig.Keys) {
        $config = $SecretsConfig[$secretName]

        if ($existingSecrets -contains $secretName) {
            if ($Force) {
                Write-Log "Recreating existing secret: $secretName"
                $password = Generate-SecurePassword -Length $config.Length
            } else {
                Write-Log "Secret already exists, skipping: $secretName (use -Force to recreate)"
                $skippedCount++
                continue
            }
        } else {
            Write-Log "Creating new secret: $secretName"
            $password = Generate-SecurePassword -Length $config.Length
        }

        if (Create-DockerSecret -SecretName $secretName -Value $password -Description $config.Description) {
            $createdCount++
        }
    }

    Write-Log "=== Secrets Creation Complete ==="
    Write-Log "Created: $createdCount, Skipped: $skippedCount"

    if ($createdCount -gt 0) {
        Write-Log "IMPORTANT: Save these passwords securely for emergency access!" -Level "WARNING"
        Write-Log "Consider storing them in a secure password manager." -Level "WARNING"
    }
}

function Update-ComposeFile {
    param([string]$ComposeFile)

    if (!(Test-Path $ComposeFile)) {
        Write-Log "Compose file not found: $ComposeFile" -Level "ERROR"
        return $false
    }

    Write-Log "Updating compose file: $ComposeFile"

    $content = Get-Content $ComposeFile -Raw

    # Define replacements for hardcoded passwords
    $replacements = @(
        @{
            Pattern = 'GF_SECURITY_ADMIN_PASSWORD=admin'
            Replacement = 'GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/grafana_admin_password'
        },
        @{
            Pattern = 'DATA_SOURCE_NAME=postgresql://twisterlab:twisterlab_prod_db_password_2024%21@postgres:5432/twisterlab_prod\?sslmode=disable'
            Replacement = 'DATA_SOURCE_NAME__FILE=/run/secrets/postgres_exporter_password'
        },
        @{
            Pattern = '--redis\.password=twisterlab_prod_redis_password_2024!'
            Replacement = '--redis.password-file=/run/secrets/redis_password'
        }
    )

    $updated = $false
    foreach ($replacement in $replacements) {
        if ($content -match [regex]::Escape($replacement.Pattern)) {
            if ($DryRun) {
                Write-Log "[DRY RUN] Would replace: $($replacement.Pattern)"
            } else {
                $content = $content -replace [regex]::Escape($replacement.Pattern), $replacement.Replacement
                $updated = $true
                Write-Log "Replaced: $($replacement.Pattern)"
            }
        }
    }

    # Add secrets section if not present
    if ($content -notmatch "secrets:") {
        $secretsSection = @"

secrets:
  grafana_admin_password:
    external: true
  postgres_password:
    external: true
  redis_password:
    external: true
  prometheus_basic_auth:
    external: true
"@

        if ($DryRun) {
            Write-Log "[DRY RUN] Would add secrets section to compose file"
        } else {
            $content += $secretsSection
            $updated = $true
            Write-Log "Added secrets section to compose file"
        }
    }

    # Add secrets references to services
    $servicesToUpdate = @(
        @{
            Service = "grafana"
            Secrets = @("grafana_admin_password")
        },
        @{
            Service = "postgres_exporter"
            Secrets = @("postgres_password")
        },
        @{
            Service = "redis_exporter"
            Secrets = @("redis_password")
        }
    )

    foreach ($service in $servicesToUpdate) {
        $servicePattern = "(?s)($($service.Service):.*?(?=\n  [a-z]|\nservices|\n$))"
        $serviceMatch = [regex]::Match($content, $servicePattern)

        if ($serviceMatch.Success) {
            $serviceBlock = $serviceMatch.Groups[1].Value

            if ($serviceBlock -notmatch "secrets:") {
                # Add secrets section to service
                $secretsYaml = "    secrets:`n"
                foreach ($secret in $service.Secrets) {
                    $secretsYaml += "      - $secret`n"
                }

                if ($DryRun) {
                    Write-Log "[DRY RUN] Would add secrets to service: $($service.Service)"
                } else {
                    $updatedServiceBlock = $serviceBlock + $secretsYaml
                    $content = $content -replace [regex]::Escape($serviceBlock), $updatedServiceBlock
                    $updated = $true
                    Write-Log "Added secrets to service: $($service.Service)"
                }
            }
        }
    }

    if (!$DryRun -and $updated) {
        $content | Out-File -FilePath $ComposeFile -Encoding UTF8
        Write-Log "Updated compose file: $ComposeFile"
    }

    return $updated
}

function Invoke-UpdateCompose {
    Write-Log "=== Updating Docker Compose Files ==="

    $composeFiles = @(
        "$ProjectRoot\docker-compose.monitoring.yml",
        "$ProjectRoot\docker-compose.monitoring-full.yml",
        "$ProjectRoot\infrastructure\docker\docker-compose.unified.yml"
    )

    $updatedCount = 0
    foreach ($file in $composeFiles) {
        if (Update-ComposeFile -ComposeFile $file) {
            $updatedCount++
        }
    }

    Write-Log "=== Compose Files Update Complete ==="
    Write-Log "Files updated: $updatedCount"
}

function Invoke-ValidateSecrets {
    Write-Log "=== Validating Docker Secrets ==="

    if (!(Test-DockerSwarm)) {
        exit 1
    }

    $existingSecrets = Get-ExistingSecrets
    $missingSecrets = @()
    $validSecrets = @()

    foreach ($secretName in $SecretsConfig.Keys) {
        if ($existingSecrets -contains $secretName) {
            $validSecrets += $secretName
            Write-Log "✓ Secret exists: $secretName"
        } else {
            $missingSecrets += $secretName
            Write-Log "✗ Secret missing: $secretName" -Level "WARNING"
        }
    }

    Write-Log "=== Validation Complete ==="
    Write-Log "Valid secrets: $($validSecrets.Count)"
    Write-Log "Missing secrets: $($missingSecrets.Count)"

    if ($missingSecrets.Count -gt 0) {
        Write-Log "Missing secrets: $($missingSecrets -join ', ')" -Level "WARNING"
        Write-Log "Run '.\security.ps1 -Action create-secrets' to create missing secrets" -Level "INFO"
        return $false
    }

    return $true
}

function Invoke-RotatePasswords {
    Write-Log "=== Rotating Passwords ==="

    if (!(Test-DockerSwarm)) {
        exit 1
    }

    Write-Log "This will generate new passwords for all secrets and update them in Docker Swarm."
    Write-Log "Make sure to update any external systems that use these passwords!" -Level "WARNING"

    if (!$Force) {
        $confirmation = Read-Host "Are you sure you want to rotate all passwords? (yes/no)"
        if ($confirmation -ne "yes") {
            Write-Log "Password rotation cancelled"
            return
        }
    }

    $rotatedCount = 0
    foreach ($secretName in $SecretsConfig.Keys) {
        $config = $SecretsConfig[$secretName]
        $newPassword = Generate-SecurePassword -Length $config.Length

        if (Create-DockerSecret -SecretName $secretName -Value $newPassword -Description $config.Description) {
            $rotatedCount++
        }
    }

    Write-Log "=== Password Rotation Complete ==="
    Write-Log "Rotated secrets: $rotatedCount"

    if ($rotatedCount -gt 0) {
        Write-Log "IMPORTANT: Update external systems with new passwords!" -Level "WARNING"
        Write-Log "Services may need to be restarted to pick up new secrets." -Level "WARNING"
    }
}

function Invoke-AuditSecurity {
    Write-Log "=== Security Audit ==="

    $issues = @()

    # Check for hardcoded passwords in compose files
    $composeFiles = Get-ChildItem -Path $ProjectRoot -Filter "docker-compose*.yml" -Recurse
    foreach ($file in $composeFiles) {
        $content = Get-Content $file.FullName -Raw

        # Check for common hardcoded password patterns
        $passwordPatterns = @(
            'password.*=.*[a-zA-Z0-9]{8,}',
            'PASSWORD.*=.*[a-zA-Z0-9]{8,}',
            'admin.*=.*admin',
            'GF_SECURITY_ADMIN_PASSWORD.*=.*admin'
        )

        foreach ($pattern in $passwordPatterns) {
            if ($content -match $pattern) {
                $issues += @{
                    File = $file.FullName
                    Type = "Hardcoded Password"
                    Pattern = $pattern
                    Severity = "Critical"
                }
            }
        }
    }

    # Check for latest image tags
    $imagePatterns = @(":latest", ":main", ":master")
    foreach ($file in $composeFiles) {
        $content = Get-Content $file.FullName -Raw

        foreach ($pattern in $imagePatterns) {
            if ($content -match $pattern) {
                $issues += @{
                    File = $file.FullName
                    Type = "Unversioned Image"
                    Pattern = $pattern
                    Severity = "High"
                }
            }
        }
    }

    # Check Docker secrets usage
    if (Test-DockerSwarm) {
        $existingSecrets = Get-ExistingSecrets
        $expectedSecrets = $SecretsConfig.Keys

        foreach ($secret in $expectedSecrets) {
            if ($existingSecrets -notcontains $secret) {
                $issues += @{
                    File = "Docker Swarm"
                    Type = "Missing Secret"
                    Pattern = $secret
                    Severity = "Critical"
                }
            }
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
        Write-Log "Issues found:" -Level "WARNING"
        foreach ($issue in $issues) {
            Write-Log "  [$($issue.Severity)] $($issue.Type) in $($issue.File): $($issue.Pattern)" -Level "WARNING"
        }
    } else {
        Write-Log "No security issues found!" -Level "INFO"
    }

    return $issues.Count -eq 0
}

# Main execution
try {
    Write-Log "=== TwisterLab Security Hardening Script ==="
    Write-Log "Action: $Action"
    Write-Log "Dry run: $DryRun"
    Write-Log "Force: $Force"

    switch ($Action) {
        "create-secrets" {
            Invoke-CreateSecrets
        }
        "update-compose" {
            Invoke-UpdateCompose
        }
        "validate-secrets" {
            $result = Invoke-ValidateSecrets
            exit [int](!$result)
        }
        "rotate-passwords" {
            Invoke-RotatePasswords
        }
        "audit-security" {
            $result = Invoke-AuditSecurity
            exit [int](!$result)
        }
    }

    Write-Log "=== Operation Completed Successfully ==="

} catch {
    Write-Log "Security hardening failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
