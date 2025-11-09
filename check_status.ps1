#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verification rapide du statut TwisterLab Production
#>

Write-Host "STATUT TWISTERLAB PRODUCTION" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Verifier les services
Write-Host "`nServices:" -ForegroundColor Yellow
docker stack services twisterlab --format "table {{.Name}}`t{{.Replicas}}`t{{.Ports}}"

# Verifier les taches
Write-Host "`nTaches:" -ForegroundColor Yellow
docker stack ps twisterlab --format "table {{.Name}}`t{{.Node}}`t{{.CurrentState}}"

# Tests d'acces rapide
Write-Host "`nTests d'acces:" -ForegroundColor Yellow
$serverIP = "192.168.0.30"

# API direct
try {
    Invoke-WebRequest -Uri "http://$serverIP`:8000/health" -Method GET -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "OK API direct" -ForegroundColor Green
} catch {
    Write-Host "KO API direct" -ForegroundColor Red
}

# Traefik dashboard
try {
    Invoke-WebRequest -Uri "http://$serverIP`:8080" -Method GET -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "OK Traefik dashboard" -ForegroundColor Green
} catch {
    Write-Host "KO Traefik dashboard" -ForegroundColor Red
}

Write-Host "`nAccess points:" -ForegroundColor White
Write-Host "   API: http://$serverIP`:8000" -ForegroundColor White
Write-Host "   Traefik: http://$serverIP`:8080" -ForegroundColor White