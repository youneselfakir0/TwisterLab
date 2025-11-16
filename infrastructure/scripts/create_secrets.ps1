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

# Configuration - Do NOT include plaintext defaults here
$secrets = @(
    @{ Name = "postgres_password"; DefaultValue = "" },
    @{ Name = "redis_password"; DefaultValue = "" },
    @{ Name = "grafana_admin_password"; DefaultValue = "" },
    @{ Name = "jwt_secret_key"; DefaultValue = "" },
    @{ Name = "webui_secret_key"; DefaultValue = "" },
    @{ Name = "smtp_password"; DefaultValue = "" }
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Generate-SecretValue {
    param([int]$Length = 32)
    # Generate a secure random base64 string
    $bytes = New-Object 'System.Byte[]' $Length
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return [System.Convert]::ToBase64String($bytes)
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
        # If there is no default value supplied, generate a strong random value for the secret
        if ([string]::IsNullOrWhiteSpace($defaultValue)) {
            $generated = Generate-SecretValue -Length 24
            $defaultValue = $generated
            Write-Log "Generated random secret for '$secretName'"
        }

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
