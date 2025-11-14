# TwisterLab v1.0.0 - Monitoring Baseline Setup
# Phase 1: Fondation Infrastructure - Monitoring Setup
# Date: November 13, 2025
# Author: GitHub Copilot (LLM DevOps Expert)

Write-Host "=== TwisterLab Monitoring Baseline Setup ===" -ForegroundColor Cyan
Write-Host "Setting up Prometheus + Grafana for CoreRTX..." -ForegroundColor Yellow
Write-Host ""

# Check if Docker is running
Write-Host "1. CHECKING DOCKER STATUS" -ForegroundColor Green
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "Docker found: $dockerVersion" -ForegroundColor Green

        # Check if Docker daemon is running
        $dockerInfo = docker info 2>$null
        if ($dockerInfo) {
            Write-Host "Docker daemon is running" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Docker daemon is not running!" -ForegroundColor Red
            Write-Host "Please start Docker Desktop or Docker service" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "ERROR: Docker not found!" -ForegroundColor Red
        Write-Host "Please install Docker from: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Could not check Docker: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create monitoring directory structure
Write-Host "`n2. CREATING MONITORING DIRECTORY STRUCTURE" -ForegroundColor Green
$monitoringDir = "C:\TwisterLab\monitoring"
if (!(Test-Path $monitoringDir)) {
    New-Item -ItemType Directory -Path $monitoringDir -Force | Out-Null
    Write-Host "Created: $monitoringDir" -ForegroundColor Green
} else {
    Write-Host "Directory exists: $monitoringDir" -ForegroundColor Yellow
}

# Create Prometheus configuration
Write-Host "`n3. CREATING PROMETHEUS CONFIGURATION" -ForegroundColor Green

$prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']

  - job_name: 'ollama'
    static_configs:
      - targets: ['host.docker.internal:11434']
    metrics_path: '/api/tags'
    params:
      format: ['json']

  - job_name: 'twisterlab-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
"@

$prometheusConfig | Out-File -FilePath "$monitoringDir\prometheus.yml" -Encoding UTF8
Write-Host "Created: prometheus.yml" -ForegroundColor Green

# Create docker-compose for monitoring stack
Write-Host "`n4. CREATING DOCKER-COMPOSE FOR MONITORING" -ForegroundColor Green

$dockerCompose = @"
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: twisterlab_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - monitoring
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: twisterlab_node_exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: twisterlab_grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=twisterlab2025!
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
"@

$dockerCompose | Out-File -FilePath "$monitoringDir\docker-compose.monitoring.yml" -Encoding UTF8
Write-Host "Created: docker-compose.monitoring.yml" -ForegroundColor Green

# Create Grafana provisioning
Write-Host "`n5. CREATING GRAFANA PROVISIONING" -ForegroundColor Green

$grafanaDir = "$monitoringDir\grafana\provisioning"
if (!(Test-Path $grafanaDir)) {
    New-Item -ItemType Directory -Path $grafanaDir -Force | Out-Null
}

# Data sources
$dataSourcesDir = "$grafanaDir\datasources"
if (!(Test-Path $dataSourcesDir)) {
    New-Item -ItemType Directory -Path $dataSourcesDir -Force | Out-Null
}

$dataSourcesConfig = @"
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
"@

$dataSourcesConfig | Out-File -FilePath "$dataSourcesDir\prometheus.yml" -Encoding UTF8
Write-Host "Created: grafana/provisioning/datasources/prometheus.yml" -ForegroundColor Green

# Dashboards
$dashboardsDir = "$grafanaDir\dashboards"
if (!(Test-Path $dashboardsDir)) {
    New-Item -ItemType Directory -Path $dashboardsDir -Force | Out-Null
}

$dashboardsConfig = @"
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
"@

$dashboardsConfig | Out-File -FilePath "$dashboardsDir\dashboards.yml" -Encoding UTF8
Write-Host "Created: grafana/provisioning/dashboards/dashboards.yml" -ForegroundColor Green

# Create default dashboard
$dashboardsPath = "$monitoringDir\grafana\provisioning\dashboards"
if (!(Test-Path $dashboardsPath)) {
    New-Item -ItemType Directory -Path $dashboardsPath -Force | Out-Null
}

$defaultDashboard = @"
{
  "dashboard": {
    "id": null,
    "title": "TwisterLab System Overview",
    "tags": ["twisterlab", "system"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)",
            "legendFormat": "Memory Usage %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100",
            "legendFormat": "{{mountpoint}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Network I/O",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total[5m])",
            "legendFormat": "RX {{device}}"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total[5m])",
            "legendFormat": "TX {{device}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "timepicker": {},
    "templating": {
      "list": []
    },
    "annotations": {
      "list": []
    },
    "refresh": "30s",
    "schemaVersion": 27,
    "version": 0,
    "links": []
  }
}
"@

$defaultDashboard | Out-File -FilePath "$dashboardsPath\twisterlab-system.json" -Encoding UTF8
Write-Host "Created: grafana/provisioning/dashboards/twisterlab-system.json" -ForegroundColor Green

# Create startup script
Write-Host "`n6. CREATING STARTUP SCRIPT" -ForegroundColor Green

$startupScript = @"
# TwisterLab Monitoring Startup Script
# Run this to start the monitoring stack

Write-Host "Starting TwisterLab Monitoring Stack..." -ForegroundColor Cyan

# Change to monitoring directory
Set-Location "C:\TwisterLab\monitoring"

# Start the monitoring stack
Write-Host "Starting Prometheus, Node Exporter, and Grafana..." -ForegroundColor Yellow
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to start
Start-Sleep -Seconds 10

# Check service status
Write-Host "`nChecking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.monitoring.yml ps

Write-Host "`nMonitoring URLs:" -ForegroundColor Green
Write-Host "Grafana: http://localhost:3000 (admin/twisterlab2025!)" -ForegroundColor White
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "Node Exporter: http://localhost:9100" -ForegroundColor White

Write-Host "`nTo stop monitoring: docker-compose -f docker-compose.monitoring.yml down" -ForegroundColor Yellow
"@

$startupScript | Out-File -FilePath "$monitoringDir\start_monitoring.ps1" -Encoding UTF8
Write-Host "Created: start_monitoring.ps1" -ForegroundColor Green

# Summary
Write-Host "`n7. MONITORING SETUP SUMMARY" -ForegroundColor Green
Write-Host "Monitoring directory: $monitoringDir" -ForegroundColor White
Write-Host "Services configured:" -ForegroundColor White
Write-Host "  - Prometheus (metrics collection)" -ForegroundColor Gray
Write-Host "  - Node Exporter (system metrics)" -ForegroundColor Gray
Write-Host "  - Grafana (visualization)" -ForegroundColor Gray
Write-Host "" -ForegroundColor White
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\monitoring\start_monitoring.ps1" -ForegroundColor White
Write-Host "2. Open: http://localhost:3000 (admin/twisterlab2025!)" -ForegroundColor White
Write-Host "3. Import dashboard: TwisterLab System Overview" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "Monitoring baseline setup completed!" -ForegroundColor Green
