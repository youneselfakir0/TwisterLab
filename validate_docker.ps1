#!/usr/bin/env pwsh
# Script de validation Docker - TwisterLab
# V?rifie que toutes les corrections sont appliqu?es

Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "? VALIDATION DOCKER SWARM - TwisterLab" -ForegroundColor Cyan
Write-Host "="*70 + "`n" -ForegroundColor Cyan

$issues = @()
$warnings = @()
$success = @()

# TEST 1: S?curit? API Docker
Write-Host "[1/7] ? V?rification s?curit? API Docker..." -ForegroundColor Yellow
$dockerInfo = docker info 2>&1 | Out-String
if ($dockerInfo -match "accessible on http://0.0.0.0:2375 without encryption") {
    $issues += "? API Docker expos?e sans TLS (port 2375)"
} else {
    $success += "? API Docker s?curis?e"
}

# TEST 2: Configuration Swarm
Write-Host "[2/7] ? V?rification configuration Swarm..." -ForegroundColor Yellow
$swarmState = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
if ($swarmState -eq "active") {
    $success += "? Docker Swarm actif"

    $managers = (docker info --format '{{.Swarm.Managers}}' 2>$null)
    if ($managers -lt 3) {
        $warnings += "??  Seulement $managers manager(s) - recommand?: 3 pour HA"
    } else {
        $success += "? $managers managers configur?s (haute disponibilit?)"
    }
} else {
    $issues += "? Docker Swarm non actif"
}

# TEST 3: N?uds disponibles
Write-Host "[3/7] ? V?rification des n?uds..." -ForegroundColor Yellow
$nodes = docker node ls --format '{{.Hostname}}' 2>$null
$nodeCount = ($nodes | Measure-Object).Count
if ($nodeCount -ge 3) {
    $success += "OK $nodeCount noeuds dans le cluster"
} else {
    $warnings += "WARN Seulement $nodeCount noeud(s) - recommande: 3+"
}

# Verifier edgeserver
if ($nodes -match "edgeserver") {
    $success += "OK Noeud edgeserver.twisterlab.local present"
} else {
    $issues += "ERREUR Noeud edgeserver.twisterlab.local absent"
}

# TEST 4: Image API disponible
Write-Host "[4/7] ??  V?rification de l'image twisterlab-api..." -ForegroundColor Yellow
$apiImage = docker images --format '{{.Repository}}:{{.Tag}}' | Select-String "twisterlab-api:latest"
if ($apiImage) {
    $success += "? Image twisterlab-api:latest disponible localement"

    # V?rifier si sauvegard?e
    if (Test-Path "twisterlab-api.tar") {
        $success += "? Archive twisterlab-api.tar cr??e"
    } else {
        $warnings += "??  Archive twisterlab-api.tar non trouv?e"
    }
} else {
    $issues += "? Image twisterlab-api:latest manquante"
}

# TEST 5: Services critiques
Write-Host "[5/7] ? V?rification des services..." -ForegroundColor Yellow
$services = docker service ls --format '{{.Name}}\t{{.Replicas}}' 2>$null

$criticalServices = @(
    "twisterlab_prod_api",
    "twisterlab_prod_webui",
    "twisterlab-monitoring_grafana",
    "twisterlab-monitoring_prometheus"
)

foreach ($svc in $criticalServices) {
    $serviceStatus = $services | Select-String $svc
    if ($serviceStatus) {
        if ($serviceStatus -match "1/1") {
            $success += "? Service $svc op?rationnel (1/1)"
        } elseif ($serviceStatus -match "0/1") {
            $issues += "? Service $svc arr?t? (0/1)"
        } else {
            $warnings += "??  Service $svc en ?tat partiel"
        }
    } else {
        $issues += "? Service $svc non d?ploy?"
    }
}

# TEST 6: Contrainte WebUI
Write-Host "[6/7] ? V?rification contrainte WebUI..." -ForegroundColor Yellow
$composeContent = Get-Content "docker-compose.production.yml" -Raw
if ($composeContent -match "node\.labels\.os == linux") {
    $success += "? Contrainte WebUI corrig?e (os == linux)"
} elseif ($composeContent -match "node\.role == worker") {
    $issues += "? Contrainte WebUI toujours incorrecte (worker au lieu de os==linux)"
} else {
    $warnings += "??  Contrainte WebUI non d?tect?e"
}

# TEST 7: Accessibilit? des endpoints
Write-Host "[7/7] ? V?rification des endpoints..." -ForegroundColor Yellow

$endpoints = @{
    "Grafana" = "http://edgeserver.twisterlab.local:3000"
    "Prometheus" = "http://edgeserver.twisterlab.local:9090"
}

foreach ($name in $endpoints.Keys) {
    try {
        $response = Invoke-WebRequest -Uri $endpoints[$name] -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $success += "? $name accessible ($($endpoints[$name]))"
        }
    } catch {
        $warnings += "??  $name non accessible ($($endpoints[$name]))"
    }
}

# RAPPORT FINAL
Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "? R?SULTATS DE VALIDATION" -ForegroundColor Cyan
Write-Host "="*70 + "`n" -ForegroundColor Cyan

if ($success.Count -gt 0) {
    Write-Host "? SUCC?S ($($success.Count)):" -ForegroundColor Green
    foreach ($item in $success) {
        Write-Host "   $item" -ForegroundColor Green
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "??  AVERTISSEMENTS ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($item in $warnings) {
        Write-Host "   $item" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($issues.Count -gt 0) {
    Write-Host "? PROBL?MES ($($issues.Count)):" -ForegroundColor Red
    foreach ($item in $issues) {
        Write-Host "   $item" -ForegroundColor Red
    }
    Write-Host ""
}

# Score final
$total = $success.Count + $warnings.Count + $issues.Count
$score = [math]::Round(($success.Count / $total) * 100, 1)

Write-Host "="*70 -ForegroundColor Cyan
if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "? SYST?ME 100% OP?RATIONNEL" -ForegroundColor Green
} elseif ($issues.Count -eq 0) {
    Write-Host "? SYST?ME OP?RATIONNEL ($score% - avertissements mineurs)" -ForegroundColor Yellow
} else {
    Write-Host "??  SYST?ME PARTIELLEMENT OP?RATIONNEL ($score%)" -ForegroundColor Red
    Write-Host "`n? Actions requises:" -ForegroundColor Yellow
    Write-Host "   1. Ex?cuter: .\fix_docker_issues.ps1" -ForegroundColor White
    Write-Host "   2. Transf?rer l'image vers edgeserver" -ForegroundColor White
    Write-Host "   3. Red?ployer le stack Docker" -ForegroundColor White
    Write-Host "   4. Consulter DOCKER_ANALYSIS_REPORT.md pour d?tails`n" -ForegroundColor White
}
Write-Host "="*70 + "`n" -ForegroundColor Cyan

# Code de sortie
if ($issues.Count -eq 0) { exit 0 } else { exit 1 }
