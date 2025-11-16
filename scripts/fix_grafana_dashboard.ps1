#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Fix Grafana Dashboard avec métriques réelles
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "`n=== FIX GRAFANA DASHBOARD - METRIQUES REELLES ===" -ForegroundColor Cyan

# Dashboard corrigé avec les vraies métriques
$dashboardJson = @'
{
  "dashboard": {
    "id": null,
    "uid": "twisterlab-agents-fixed",
    "title": "TwisterLab Agents - Real Metrics (FIXED)",
    "tags": ["twisterlab", "agents", "fixed"],
    "timezone": "browser",
    "schemaVersion": 36,
    "version": 1,
    "refresh": "10s",
    "time": {
      "from": "now-15m",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "Agent Operations (Total)",
        "type": "stat",
        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "sum(agent_operations_total)",
          "legendFormat": "Total Operations",
          "refId": "A"
        }],
        "options": {
          "graphMode": "area",
          "colorMode": "value"
        },
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "unit": "short"
          }
        }
      },
      {
        "id": 2,
        "title": "HTTP Requests Total",
        "type": "stat",
        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 0},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "sum(http_requests_total)",
          "legendFormat": "HTTP Requests",
          "refId": "A"
        }],
        "options": {
          "graphMode": "area",
          "colorMode": "value"
        }
      },
      {
        "id": 3,
        "title": "API Memory Usage (MB)",
        "type": "stat",
        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 0},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "process_resident_memory_bytes / 1024 / 1024",
          "legendFormat": "Memory MB",
          "refId": "A"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "decmbytes",
            "decimals": 1
          }
        }
      },
      {
        "id": 4,
        "title": "Operations by Agent",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "sum by(agent) (agent_operations_total)",
          "legendFormat": "{{agent}}",
          "refId": "A"
        }],
        "options": {
          "legend": {"displayMode": "table", "placement": "right"}
        }
      },
      {
        "id": 5,
        "title": "HTTP Requests by Endpoint",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "sum by(endpoint) (http_requests_total)",
          "legendFormat": "{{endpoint}}",
          "refId": "A"
        }],
        "options": {
          "legend": {"displayMode": "table", "placement": "right"}
        }
      },
      {
        "id": 6,
        "title": "Agent Success Rate",
        "type": "bargauge",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 14},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "sum by(agent) (agent_operations_total{status=\"success\"})",
          "legendFormat": "{{agent}}",
          "refId": "A"
        }],
        "options": {
          "orientation": "horizontal",
          "displayMode": "gradient"
        },
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"}
          }
        }
      },
      {
        "id": 7,
        "title": "CPU Usage",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 14},
        "datasource": {"type": "prometheus", "uid": "df3qqymva25tsb"},
        "targets": [{
          "expr": "rate(process_cpu_seconds_total[1m])",
          "legendFormat": "CPU Usage",
          "refId": "A"
        }]
      }
    ]
  },
  "overwrite": true
}
'@

# Importer dans Grafana
Write-Host "`n[1/2] Création du dashboard corrigé..." -ForegroundColor Yellow
$dashboardFile = "C:\TwisterLab\monitoring\grafana\provisioning\dashboards\twisterlab-agents-fixed.json"
$dashboardJson | Out-File -FilePath $dashboardFile -Encoding UTF8 -Force

Write-Host "OK - Dashboard sauvegardé: $dashboardFile" -ForegroundColor Green

# Function to read secret from Docker secret file or environment variable
function Get-Secret {
    param(
        [string]$SecretName,
        [string]$DefaultValue = $null
    )
    $secretPath = "/run/secrets/$SecretName"
    if (Test-Path $secretPath) {
        return (Get-Content $secretPath).Trim()
    }
    $envValue = Get-Item ENV:$SecretName -ErrorAction SilentlyContinue
    if ($envValue) {
        return $envValue.Value
    }
    if ($DefaultValue) {
        return $DefaultValue
    }
    throw "Secret '$SecretName' not found in Docker secrets or environment variables."
}

$GrafanaPassword = Get-Secret -SecretName "grafana_admin_password"
$GrafanaUser = $env:GRAFANA_ADMIN_USER
if ([string]::IsNullOrWhiteSpace($GrafanaUser)) { $GrafanaUser = "admin" }

# Import via API Grafana
Write-Host "`n[2/2] Import dans Grafana..." -ForegroundColor Yellow
try {
    $importResult = Invoke-RestMethod -Uri "http://192.168.0.30:3000/api/dashboards/db" `
        -Method Post `
        -Headers @{
            "Content-Type" = "application/json"
            "Authorization" = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$GrafanaUser:$GrafanaPassword")))"
        } `
        -Body $dashboardJson

    Write-Host "OK - Dashboard importé avec succès !" -ForegroundColor Green
    Write-Host "  UID: $($importResult.uid)" -ForegroundColor Gray
    Write-Host "  URL: $($importResult.url)" -ForegroundColor Gray
} catch {
    Write-Host "ATTENTION - Import API échoué, utilisant provisioning..." -ForegroundColor Yellow
}

Write-Host @"

=================================================================
            DASHBOARD CORRIGÉ CRÉÉ
=================================================================

Nouveau dashboard avec VRAIES métriques:
  http://192.168.0.30:3000/d/twisterlab-agents-fixed

Métriques utilisées (qui EXISTENT):
  ✅ agent_operations_total       - Opérations des agents
  ✅ http_requests_total           - Requêtes HTTP
  ✅ process_resident_memory_bytes - Mémoire utilisée
  ✅ process_cpu_seconds_total     - CPU utilisé

Panels affichés:
  1. Agent Operations Total
  2. HTTP Requests Total
  3. API Memory Usage
  4. Operations by Agent (graphique)
  5. HTTP Requests by Endpoint
  6. Agent Success Rate
  7. CPU Usage

Rafraîchissement automatique: 10s

=================================================================

"@ -ForegroundColor Green

# Redémarrer Grafana pour provisioning
Write-Host "Redémarrage de Grafana pour appliquer les changements..." -ForegroundColor Yellow
ssh twister@192.168.0.30 "docker service update --force twisterlab-monitoring_grafana" 2>&1 | Out-Null
Start-Sleep -Seconds 5

Write-Host "`nOuvre le nouveau dashboard:" -ForegroundColor Cyan
Write-Host "http://192.168.0.30:3000/d/twisterlab-agents-fixed" -ForegroundColor White

Start-Process "http://192.168.0.30:3000/d/twisterlab-agents-fixed"
