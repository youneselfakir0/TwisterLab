# Deploy TwisterLab Monitoring Stack
# This script deploys the complete monitoring infrastructure

Write-Host ' Deploying TwisterLab Monitoring Stack...' -ForegroundColor Green

# Check if Docker is running
try {
    $dockerVersion = docker version --format json | ConvertFrom-Json
    Write-Host ' Docker is running (v'$($dockerVersion.Client.Version)')' -ForegroundColor Green
} catch {
    Write-Host ' Docker is not running. Please start Docker Desktop.' -ForegroundColor Red
    exit 1
}

# Check if Docker Swarm is initialized
try {
    $swarmStatus = docker info --format json | ConvertFrom-Json
    if ($swarmStatus.Swarm.LocalNodeState -ne 'active') {
        Write-Host ' Docker Swarm is not initialized. Please run '\''docker swarm init'\'' first.' -ForegroundColor Red
        exit 1
    }
    Write-Host ' Docker Swarm is active' -ForegroundColor Green
} catch {
    Write-Host ' Cannot check Docker Swarm status' -ForegroundColor Red
    exit 1
}

# Create external volumes if they don't exist
Write-Host ' Creating external volumes...' -ForegroundColor Yellow
$volumes = @('prometheus_data', 'grafana_data', 'alertmanager_data')
foreach ($volume in $volumes) {
    try {
        docker volume create $volume
        Write-Host ' Created volume: '$volume -ForegroundColor Green
    } catch {
        Write-Host 'ℹ  Volume '$volume' already exists' -ForegroundColor Blue
    }
}

# Create external network if it doesn't exist
Write-Host ' Creating external network...' -ForegroundColor Yellow
try {
    docker network create --driver overlay twisterlab_prod
    Write-Host ' Created network: twisterlab_prod' -ForegroundColor Green
} catch {
    Write-Host 'ℹ  Network twisterlab_prod already exists' -ForegroundColor Blue
}

# Deploy monitoring stack
Write-Host ' Deploying monitoring services...' -ForegroundColor Yellow
try {
    docker stack deploy -c docker-compose.monitoring.yml twisterlab-monitoring
    Write-Host ' Monitoring stack deployed successfully!' -ForegroundColor Green
} catch {
    Write-Host ' Failed to deploy monitoring stack: '$($_.Exception.Message) -ForegroundColor Red
    exit 1
}

# Wait for services to start
Write-Host ' Waiting for services to start...' -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host ' Checking service status...' -ForegroundColor Yellow
try {
    $services = docker stack services twisterlab-monitoring
    Write-Host ' Services deployed:' -ForegroundColor Green
    Write-Host $services -ForegroundColor White
} catch {
    Write-Host ' Failed to check service status' -ForegroundColor Red
}

# Display access URLs
Write-Host '
 Monitoring Services Access URLs:' -ForegroundColor Cyan
Write-Host ' Prometheus:    http://localhost:9091' -ForegroundColor White
Write-Host ' Grafana:       http://localhost:3000 (admin account via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD)' -ForegroundColor White
Write-Host ' Jaeger:        http://localhost:16686' -ForegroundColor White
Write-Host ' Alertmanager:  http://localhost:9093' -ForegroundColor White

Write-Host '
 TwisterLab Monitoring Stack deployment complete!' -ForegroundColor Green
Write-Host ' Tip: Use '\''docker stack ps twisterlab-monitoring'\'' to check container status' -ForegroundColor Blue
