# =============================================================================
# TWISTERLAB DOCKER SECRETS CREATION SCRIPT
# Version: 1.0.0
# Date: 2025-11-15
#
# Creates Docker Swarm secrets for secure password management
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

# Configuration
$secrets = @(
    @{
        Name = "postgres_password"
        Description = "PostgreSQL database password"
        DefaultValue = "twisterlab_prod_2024_secure!"
    },
    @{
        Name = "redis_password"
        Description = "Redis cache password"
        DefaultValue = "twisterlab_redis_2024_secure!"
    },
    @{
        Name = "grafana_admin_password"
        Description = "Grafana admin password"
        DefaultValue = "twisterlab_grafana_admin_2024!"
    },
    @{
        Name = "jwt_secret_key"
        Description = "JWT secret key for API authentication"
        DefaultValue = "twisterlab_jwt_secret_2024_super_secure_key!"
    },
    @{
        Name = "webui_secret_key"
        Description = "Open WebUI secret key"
        DefaultValue = "twisterlab_webui_secret_2024_secure!"
    }
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-DockerSwarm {
    try {
        $swarmStatus = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
        if ($swarmStatus -eq "active") {
            Write-Log "Docker Swarm is active"
            return $true
        } else {
            Write-Log "Docker Swarm is not active. Current state: $swarmStatus" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to check Docker Swarm status: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Get-SecretExists {
    param([string]$SecretName)
    try {
        $existingSecrets = docker secret ls --format '{{.Name}}'
        return $existingSecrets -contains $SecretName
    } catch {
        Write-Log "Failed to check if secret '$SecretName' exists: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function New-DockerSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue,
        [string]$Description
    )

    if ($DryRun) {
        Write-Log "DRY RUN: Would create secret '$SecretName' with description '$Description'"
        return $true
    }

    try {
        # Create temporary file with secret value
        $tempFile = [System.IO.Path]::GetTempFileName()
        [System.IO.File]::WriteAllText($tempFile, $SecretValue)

        # Create Docker secret
        $null = docker secret create $SecretName $tempFile

        # Clean up temporary file
        Remove-Item $tempFile -Force

        Write-Log "Successfully created secret '$SecretName'"
        return $true
    } catch {
        Write-Log "Failed to create secret '$SecretName': $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Update-DockerSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue,
        [string]$Description
    )

    if ($DryRun) {
        Write-Log "DRY RUN: Would update secret '$SecretName' with description '$Description'"
        return $true
    }

    try {
        # Remove existing secret
        docker secret rm $SecretName | Out-Null

        # Create new secret
        return New-DockerSecret -SecretName $SecretName -SecretValue $SecretValue -Description $Description
    } catch {
        Write-Log "Failed to update secret '$SecretName': $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
Write-Log "=== TwisterLab Docker Secrets Creation Script ==="

# Check Docker Swarm
if (-not (Test-DockerSwarm)) {
    Write-Log "Docker Swarm must be active to create secrets. Exiting." "ERROR"
    exit 1
}

# Process each secret
$createdCount = 0
$updatedCount = 0
$failedCount = 0

foreach ($secret in $secrets) {
    $secretName = $secret.Name
    $description = $secret.Description
    $defaultValue = $secret.DefaultValue

    Write-Log "Processing secret '$secretName' ($description)"

    $exists = Get-SecretExists -SecretName $secretName

    if ($exists -and -not $Force) {
        Write-Log "Secret '$secretName' already exists. Use -Force to update." "WARNING"
        continue
    }

    if ($exists -and $Force) {
        Write-Log "Updating existing secret '$secretName'"
        if (Update-DockerSecret -SecretName $secretName -SecretValue $defaultValue -Description $description) {
            $updatedCount++
        } else {
            $failedCount++
        }
    } else {
        Write-Log "Creating new secret '$secretName'"
        if (New-DockerSecret -SecretName $secretName -SecretValue $defaultValue -Description $description) {
            $createdCount++
        } else {
            $failedCount++
        }
    }
}

# Summary
Write-Log "=== Secrets Creation Summary ==="
Write-Log "Created: $createdCount secrets"
Write-Log "Updated: $updatedCount secrets"
Write-Log "Failed: $failedCount secrets"

if ($failedCount -eq 0) {
    Write-Log "All secrets processed successfully!" "SUCCESS"

    # List all secrets
    Write-Log "Current Docker secrets:"
    try {
        docker secret ls
    } catch {
        Write-Log "Failed to list secrets: $($_.Exception.Message)" "WARNING"
    }
} else {
    Write-Log "$failedCount secrets failed to process. Check logs above." "ERROR"
    exit 1
}

Write-Log "=== Next Steps ==="
Write-Log "1. Update your .env files to remove hardcoded passwords"
Write-Log "2. Deploy the updated stack: docker stack deploy -c docker-compose.unified.yml twisterlab"
Write-Log "3. Verify services are using secrets correctly"
