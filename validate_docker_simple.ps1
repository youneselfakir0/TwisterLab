#!/usr/bin/env pwsh
# Validation Docker - TwisterLab (Version ASCII Safe)

Write-Host "`n======================================================================`n" -ForegroundColor Cyan
Write-Host "VALIDATION DOCKER SWARM - TwisterLab`n" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

$issues = 0
$success = 0

# TEST 1: Swarm actif
Write-Host "[1/6] Docker Swarm..." -ForegroundColor Yellow
$swarmState = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
if ($swarmState -eq "active") {
    Write-Host "  [OK] Swarm actif" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [ERREUR] Swarm non actif" -ForegroundColor Red
    $issues++
}

# TEST 2: Securite API
Write-Host "[2/6] Securite API Docker..." -ForegroundColor Yellow
$dockerInfo = docker info 2>&1 | Out-String
if ($dockerInfo -match "accessible on http://0.0.0.0:2375 without encryption") {
    Write-Host "  [CRITIQUE] API Docker exposee sans TLS" -ForegroundColor Red
    $issues++
} else {
    Write-Host "  [OK] API Docker securisee" -ForegroundColor Green
    $success++
}

# TEST 3: Noeuds
Write-Host "[3/6] Noeuds Swarm..." -ForegroundColor Yellow
$nodes = docker node ls --format '{{.Hostname}}' 2>$null
$nodeCount = ($nodes | Measure-Object).Count
Write-Host "  [INFO] $nodeCount noeuds detectes" -ForegroundColor Cyan
if ($nodes -match "edgeserver") {
    Write-Host "  [OK] edgeserver.twisterlab.local present" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [ERREUR] edgeserver.twisterlab.local absent" -ForegroundColor Red
    $issues++
}

# TEST 4: Image API
Write-Host "[4/6] Image twisterlab-api..." -ForegroundColor Yellow
$apiImage = docker images --format '{{.Repository}}:{{.Tag}}' | Select-String "twisterlab-api:latest"
if ($apiImage) {
    Write-Host "  [OK] Image disponible localement" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [ERREUR] Image manquante" -ForegroundColor Red
    $issues++
}

# TEST 5: Services critiques
Write-Host "[5/6] Services critiques..." -ForegroundColor Yellow
$services = docker service ls --format '{{.Name}}\t{{.Replicas}}' 2>$null

$svcAPI = $services | Select-String "twisterlab_prod_api"
if ($svcAPI -match "1/1") {
    Write-Host "  [OK] API operationnelle (1/1)" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [ERREUR] API arretee ou pending" -ForegroundColor Red
    $issues++
}

$svcWebUI = $services | Select-String "twisterlab_prod_webui"
if ($svcWebUI -match "1/1") {
    Write-Host "  [OK] WebUI operationnelle (1/1)" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [ERREUR] WebUI arretee ou pending" -ForegroundColor Red
    $issues++
}

$svcGrafana = $services | Select-String "twisterlab-monitoring_grafana"
if ($svcGrafana -match "1/1") {
    Write-Host "  [OK] Grafana operationnelle (1/1)" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [WARN] Grafana arretee ou pending" -ForegroundColor Yellow
}

# TEST 6: Contrainte WebUI
Write-Host "[6/6] Configuration WebUI..." -ForegroundColor Yellow
$composeContent = Get-Content "docker-compose.production.yml" -Raw
if ($composeContent -match "node\.labels\.os == linux") {
    Write-Host "  [OK] Contrainte corrigee (os == linux)" -ForegroundColor Green
    $success++
} else {
    Write-Host "  [ERREUR] Contrainte incorrecte (worker)" -ForegroundColor Red
    $issues++
}

# RESUME
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "RESUME" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

$total = $success + $issues
$score = [math]::Round(($success / $total) * 100, 1)

Write-Host "Reussite: $success/$total tests ($score%)`n" -ForegroundColor $(if ($score -ge 80) { "Green" } elseif ($score -ge 50) { "Yellow" } else { "Red" })

if ($issues -gt 0) {
    Write-Host "ACTIONS REQUISES:" -ForegroundColor Yellow
    Write-Host "  1. Executer: .\fix_docker_issues.ps1" -ForegroundColor White
    Write-Host "  2. Consulter: DOCKER_ANALYSIS_REPORT.md`n" -ForegroundColor White
} else {
    Write-Host "SYSTEME OPERATIONNEL`n" -ForegroundColor Green
}

Write-Host "======================================================================`n" -ForegroundColor Cyan

if ($issues -eq 0) { exit 0 } else { exit 1 }
