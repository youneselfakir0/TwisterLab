# =============================================================================
# TWISTERLAB PRODUCTION DEPLOYMENT SCRIPT
# Version: 1.0.0
# Date: 2025-11-15
#
# Deploys the complete TwisterLab stack with security hardening
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    [Parameter(Mandatory=$false)]
    [switch]$SkipSecrets
)

# Configuration
$REMOTE_HOST = "192.168.0.30"
$REMOTE_USER = "twister"
$STACK_NAME = "twisterlab"
$COMPOSE_FILE = "docker-compose.unified.yml"
$ENV_FILE = ".env.production"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-RemoteConnection {
    Write-Log "Testing SSH connection to $REMOTE_USER@$REMOTE_HOST"
    try {
        $result = ssh -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo 'OK'"
        if ($result -eq "OK") {
            Write-Log "SSH connection successful"
            return $true
        }
    } catch {
        Write-Log "SSH connection failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-DockerSwarm {
    Write-Log "Checking Docker Swarm status"
    $swarmStatus = ssh "$REMOTE_USER@$REMOTE_HOST" "docker info --format '{{.Swarm.LocalNodeState}}'"
    if ($swarmStatus -eq "active") {
        Write-Log "Docker Swarm is active"
        return $true
    } else {
        Write-Log "Docker Swarm is not active: $swarmStatus" "ERROR"
        return $false
    }
}

function Test-DockerSecrets {
    Write-Log "Verifying Docker secrets exist"
    $requiredSecrets = @(
        "postgres_password",
        "redis_password",
        "grafana_admin_password",
        "jwt_secret_key",
        "webui_secret_key",
        "smtp_password"
    )

    $existingSecrets = ssh "$REMOTE_USER@$REMOTE_HOST" "docker secret ls --format '{{.Name}}'"
    $missing = @()

    foreach ($secret in $requiredSecrets) {
        if ($existingSecrets -notcontains $secret) {
            $missing += $secret
        }
    }

    if ($missing.Count -gt 0) {
        Write-Log "Missing secrets: $($missing -join ', ')" "ERROR"
        return $false
    }

    Write-Log "All required secrets exist"
    return $true
}

function Copy-FilesToRemote {
    Write-Log "Copying deployment files to remote server"

    if ($DryRun) {
        Write-Log "DRY RUN: Would copy files to $REMOTE_USER@$REMOTE_HOST" "WARNING"
        return $true
    }

    try {
        # Get absolute paths
        $composePath = Join-Path (Get-Location).Path "..\..\infrastructure\docker\$COMPOSE_FILE"
        $envPath = Join-Path (Get-Location).Path "..\..\infrastructure\configs\$ENV_FILE"
        $prometheusPath = Join-Path (Get-Location).Path "..\..\infrastructure\docker\monitoring\prometheus.yml"
        $postgresPath = Join-Path (Get-Location).Path "..\..\infrastructure\docker\postgresql.conf"

        # Resolve to absolute paths
        $composePath = Resolve-Path $composePath -ErrorAction Stop
        $envPath = Resolve-Path $envPath -ErrorAction Stop
        $prometheusPath = Resolve-Path $prometheusPath -ErrorAction Stop
        $postgresPath = Resolve-Path $postgresPath -ErrorAction Stop

        # Copy docker-compose file
        scp "$composePath" "$REMOTE_USER@$REMOTE_HOST`:~/docker-compose.unified.yml"

        # Copy environment file
        scp "$envPath" "$REMOTE_USER@$REMOTE_HOST`:~/.env.production"

        # Create monitoring directory
        ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p ~/monitoring"

        # Copy monitoring config
        scp "$prometheusPath" "$REMOTE_USER@$REMOTE_HOST`:~/monitoring/prometheus.yml"

        # Copy PostgreSQL config
        scp "$postgresPath" "$REMOTE_USER@$REMOTE_HOST`:~/postgresql.conf"

        Write-Log "Files copied successfully"
        return $true
    } catch {
        Write-Log "Failed to copy files: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Deploy-Stack {
    Write-Log "Deploying TwisterLab stack"

    if ($DryRun) {
        Write-Log "DRY RUN: Would deploy stack '$STACK_NAME'" "WARNING"
        return $true
    }

    try {
        $deployCmd = "cd ~ && docker stack deploy -c docker-compose.unified.yml --with-registry-auth $STACK_NAME"

        Write-Log "Executing: $deployCmd"
        $result = ssh "$REMOTE_USER@$REMOTE_HOST" $deployCmd

        Write-Log "Deployment initiated"
        Write-Host $result
        return $true
    } catch {
        Write-Log "Deployment failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Wait-ForServices {
    param([int]$TimeoutSeconds = 120)

    Write-Log "Waiting for services to start (timeout: ${TimeoutSeconds}s)"

    $elapsed = 0
    $interval = 10

    while ($elapsed -lt $TimeoutSeconds) {
        $services = ssh "$REMOTE_USER@$REMOTE_HOST" "docker service ls --format '{{.Name}} {{.Replicas}}'" | ForEach-Object {
            $parts = $_ -split ' '
            [PSCustomObject]@{
                Name = $parts[0]
                Replicas = $parts[1]
            }
        }

        $allReady = $true
        foreach ($service in $services) {
            $replicaParts = $service.Replicas -split '/'
            if ($replicaParts.Count -eq 2 -and $replicaParts[0] -ne $replicaParts[1]) {
                $allReady = $false
                Write-Log "Service $($service.Name): $($service.Replicas)" "WARNING"
            }
        }

        if ($allReady) {
            Write-Log "All services are ready!" "SUCCESS"
            return $true
        }

        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }

    Write-Log "Timeout waiting for services to start" "ERROR"
    return $false
}

function Show-ServiceStatus {
    Write-Log "Current service status:"
    ssh "$REMOTE_USER@$REMOTE_HOST" "docker service ls"
}

function Test-Endpoints {
    Write-Log "Testing service endpoints"

    $endpoints = @(
        @{Name="API Health"; URL="http://$REMOTE_HOST:8000/health"},
        @{Name="Traefik Dashboard"; URL="http://$REMOTE_HOST:8080"},
        @{Name="Prometheus"; URL="http://$REMOTE_HOST:9090/-/healthy"},
        @{Name="Grafana"; URL="http://$REMOTE_HOST:3000/api/health"},
        @{Name="Open WebUI"; URL="http://$REMOTE_HOST:8083"}
    )

    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.URL -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Log "$($endpoint.Name): OK" "SUCCESS"
            } else {
                Write-Log "$($endpoint.Name): Status $($response.StatusCode)" "WARNING"
            }
        } catch {
            Write-Log "$($endpoint.Name): FAILED" "ERROR"
        }
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

Write-Log "=== TwisterLab Production Deployment ==="
Write-Log "Target: $REMOTE_USER@$REMOTE_HOST"
Write-Log "Stack: $STACK_NAME"

# Pre-deployment checks
if (-not (Test-RemoteConnection)) {
    Write-Log "Cannot connect to remote server. Exiting." "ERROR"
    exit 1
}

if (-not (Test-DockerSwarm)) {
    Write-Log "Docker Swarm is not active. Exiting." "ERROR"
    exit 1
}

if (-not $SkipSecrets -and -not (Test-DockerSecrets)) {
    Write-Log "Docker secrets are missing. Run create_secrets.ps1 first or use -SkipSecrets" "ERROR"
    exit 1
}

# Deployment
if (-not (Copy-FilesToRemote)) {
    Write-Log "Failed to copy files. Exiting." "ERROR"
    exit 1
}

if (-not (Deploy-Stack)) {
    Write-Log "Deployment failed. Exiting." "ERROR"
    exit 1
}

# Post-deployment validation
Write-Log "Waiting for services to stabilize..."
Start-Sleep -Seconds 30

Show-ServiceStatus

if (Wait-ForServices -TimeoutSeconds 120) {
    Write-Log "=== Deployment Successful! ===" "SUCCESS"

    Write-Log "Testing endpoints..."
    Test-Endpoints

    Write-Log ""
    Write-Log "=== Access URLs ===" "SUCCESS"
    Write-Log "  API:        http://$REMOTE_HOST:8000"
    Write-Log "  WebUI:      http://$REMOTE_HOST:8083"
    Write-Log "  Traefik:    http://$REMOTE_HOST:8080"
    Write-Log "  Prometheus: http://$REMOTE_HOST:9090"
    Write-Log "  Grafana:    http://$REMOTE_HOST:3000"
    Write-Log ""
    Write-Log "Default Grafana credentials: admin / (see Docker secret)"
} else {
    Write-Log "Some services failed to start. Check logs." "ERROR"
    exit 1
}
