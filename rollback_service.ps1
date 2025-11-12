#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Rollback vers une version stable du service

.DESCRIPTION
    Restaure le service à son état stable précédent si le fix a échoué.
    Restaure également la config database si nécessaire.

.NOTES
    Utiliser si fix_database_config.ps1 a échoué
#>

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Red
Write-Host "🔄 ROLLBACK SERVICE" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Configuration
$SERVER = "twister@192.168.0.30"
$PROJECT_DIR = "/home/twister/TwisterLab"
$CONFIG_FILE = "$PROJECT_DIR/agents/database/config.py"

# Étape 1: Afficher l'état actuel
Write-Host "[1/4] État actuel du service..." -ForegroundColor Yellow
ssh $SERVER "docker service ps twisterlab_api --no-trunc | head -5"
Write-Host ""

# Étape 2: Lister les images disponibles
Write-Host "[2/4] Images disponibles..." -ForegroundColor Yellow
$images = ssh $SERVER "docker images twisterlab-api --format '{{.Tag}}' | head -10"
Write-Host $images
Write-Host ""

# Demander confirmation
Write-Host "Options de rollback:" -ForegroundColor Cyan
Write-Host "  1. Rollback Docker Swarm automatique (dernière version stable)"
Write-Host "  2. Restaurer l'image 'real-agents-final'"
Write-Host "  3. Restaurer l'image 'production-real-agents-20251111-024958'"
Write-Host "  4. Annuler"
Write-Host ""

$choice = Read-Host "Choisir une option (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "[3/4] Rollback Swarm automatique..." -ForegroundColor Yellow
        ssh $SERVER "docker service update --rollback twisterlab_api"

        Write-Host "Attente de convergence..."
        Start-Sleep -Seconds 20

        $status = ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
        Write-Host "Statut: $status"
    }

    "2" {
        Write-Host ""
        Write-Host "[3/4] Restauration vers 'real-agents-final'..." -ForegroundColor Yellow
        ssh $SERVER "docker service update --image twisterlab-api:real-agents-final twisterlab_api"

        Write-Host "Attente de convergence..."
        Start-Sleep -Seconds 20

        $status = ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
        Write-Host "Statut: $status"
    }

    "3" {
        Write-Host ""
        Write-Host "[3/4] Restauration vers 'production-real-agents-20251111-024958'..." -ForegroundColor Yellow
        ssh $SERVER "docker service update --image twisterlab-api:production-real-agents-20251111-024958 twisterlab_api"

        Write-Host "Attente de convergence..."
        Start-Sleep -Seconds 20

        $status = ssh $SERVER "docker service ps twisterlab_api --format '{{.CurrentState}}' | head -1"
        Write-Host "Statut: $status"
    }

    "4" {
        Write-Host "Annulé." -ForegroundColor Gray
        exit 0
    }

    default {
        Write-Host "Option invalide." -ForegroundColor Red
        exit 1
    }
}

# Étape 3: Restaurer le fichier config si backup existe
Write-Host ""
Write-Host "[4/4] Vérification du backup config..." -ForegroundColor Yellow
$backupExists = ssh $SERVER "test -f ${CONFIG_FILE}.backup && echo 'exists' || echo 'missing'"

if ($backupExists -eq "exists") {
    Write-Host "Backup trouvé: ${CONFIG_FILE}.backup"
    $restore = Read-Host "Restaurer le backup? (o/n)"

    if ($restore -eq "o") {
        ssh $SERVER "cp ${CONFIG_FILE}.backup $CONFIG_FILE"
        Write-Host "✅ Config restaurée" -ForegroundColor Green
    } else {
        Write-Host "Config non modifiée" -ForegroundColor Gray
    }
} else {
    Write-Host "Pas de backup trouvé" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rollback terminé" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vérifiez l'état avec:" -ForegroundColor Yellow
Write-Host "  Invoke-RestMethod -Uri 'http://192.168.0.30:8000/health'" -ForegroundColor Gray
Write-Host ""
