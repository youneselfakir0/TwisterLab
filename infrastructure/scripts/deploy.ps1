<#
.SYNOPSIS
    Script de déploiement unifié TwisterLab v1.0
.DESCRIPTION
    Déploie TwisterLab en staging OU production avec validation automatique
    UN SEUL script pour tous les environnements
.PARAMETER Environment
    Environnement cible: 'staging' ou 'production'
.PARAMETER SkipValidation
    Ignorer les validations pré-déploiement (non recommandé)
.PARAMETER Force
    Forcer le redéploiement même si des services existent
.EXAMPLE
    .\deploy.ps1 -Environment staging
    .\deploy.ps1 -Environment production -Force
.NOTES
    Auteur: TwisterLab Team
    Date: 2025-11-10
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('staging', 'production')]
    [string]$Environment,

    [Parameter(Mandatory=$false)]
    [switch]$SkipValidation,

    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [string]$JwtSecret,

    [Parameter(Mandatory=$false)]
    [string]$AdminPassword
)

# =============================================================================
# CONFIGURATION
# =============================================================================

$ErrorActionPreference = "Stop"
$InformationPreference = "Continue"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $SCRIPT_DIR)
$INFRASTRUCTURE_DIR = Join-Path $PROJECT_ROOT "infrastructure"
$DOCKER_DIR = Join-Path $INFRASTRUCTURE_DIR "docker"
$CONFIGS_DIR = Join-Path $INFRASTRUCTURE_DIR "configs"

$COMPOSE_FILE = Join-Path $DOCKER_DIR "docker-compose.unified.yml"
$ENV_FILE = Join-Path $CONFIGS_DIR ".env.$Environment"
$STACK_NAME = "twisterlab"

$REQUIRED_SERVICES = @("api", "postgres", "redis", "webui", "traefik")

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

function Write-Status {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $emoji = switch ($Level) {
        "SUCCESS" { "[OK]" }
        "ERROR" { "[ERR]" }
        "WARNING" { "[WARN]" }
        "INFO" { "[INFO]" }
        default { "[LOG]" }
    }

    Write-Host "[$timestamp] $emoji $Message" -ForegroundColor $(
        switch ($Level) {
            "SUCCESS" { "Green" }
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            default { "Cyan" }
        }
    )
}

function Test-Prerequisites {
    Write-Status "Vérification des prérequis..." "INFO"

    # Docker disponible ?
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Status "Docker non trouvé !" "ERROR"
        return $false
    }

    # Docker Swarm actif ?
    $swarmInfo = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
    if ($swarmInfo -ne "active") {
        Write-Status "Docker Swarm non actif. Initialisation..." "WARNING"
        docker swarm init 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Status "Impossible d'initialiser Docker Swarm" "ERROR"
            return $false
        }
    }

    # Fichiers requis existent ?
    if (-not (Test-Path $COMPOSE_FILE)) {
        Write-Status "Fichier docker-compose introuvable: $COMPOSE_FILE" "ERROR"
        return $false
    }

    if (-not (Test-Path $ENV_FILE)) {
        Write-Status "Fichier .env introuvable: $ENV_FILE" "ERROR"
        return $false
    }

    Write-Status "Tous les prérequis sont satisfaits" "SUCCESS"
    return $true
}

function Test-DataDirectories {
    Write-Status "Vérification des répertoires de données..." "INFO"

    # Charger DATA_PATH depuis .env
    $dataPath = (Get-Content $ENV_FILE | Where-Object { $_ -match '^DATA_PATH=' }) -replace 'DATA_PATH=', ''

    if ([string]::IsNullOrEmpty($dataPath)) {
        Write-Status "DATA_PATH non défini dans $ENV_FILE" "WARNING"
        $dataPath = "/twisterlab/data"
    }

    # Créer répertoires si nécessaire (via SSH sur edgeserver)
    $directories = @("postgres", "redis", "webui")

    foreach ($dir in $directories) {
        $fullPath = "$dataPath/$dir"
        Write-Status "Création répertoire: $fullPath" "INFO"

        ssh twister@edgeserver.twisterlab.local "sudo mkdir -p $fullPath && sudo chown -R 1000:1000 $fullPath" 2>$null
    }

    Write-Status "Répertoires de données configurés" "SUCCESS"
}

function Deploy-Stack {
    Write-Status "Déploiement de la stack $STACK_NAME ($Environment)..." "INFO"

    # Copier fichiers sur edgeserver
    Write-Status "Copie des fichiers de configuration..." "INFO"
    scp $COMPOSE_FILE twister@edgeserver.twisterlab.local:/home/twister/docker-compose.yml
    scp $ENV_FILE twister@edgeserver.twisterlab.local:/home/twister/.env

    if ($LASTEXITCODE -ne 0) {
        Write-Status "Échec de la copie des fichiers" "ERROR"
        return $false
    }

    # Déployer la stack
    Write-Status "Lancement du déploiement Docker Swarm..." "INFO"

    $deployCmd = "cd /home/twister && "
    if (-not [string]::IsNullOrEmpty($JwtSecret)) {
        $deployCmd += "export JWT_SECRET_KEY='$JwtSecret' && "
    }
    if (-not [string]::IsNullOrEmpty($AdminPassword)) {
        $deployCmd += "export ADMIN_PASSWORD='$AdminPassword' && "
    }
    $deployCmd += "export $(cat .env | xargs) && "
    $deployCmd += "docker stack deploy -c docker-compose.yml --with-registry-auth $STACK_NAME"

    ssh twister@edgeserver.twisterlab.local $deployCmd

    if ($LASTEXITCODE -ne 0) {
        Write-Status "Échec du déploiement" "ERROR"
        return $false
    }

    Write-Status "Stack déployée avec succès" "SUCCESS"
    return $true
}

function Wait-ServicesReady {
    param([int]$TimeoutSeconds = 120)

    Write-Status "Attente de la convergence des services (timeout: ${TimeoutSeconds}s)..." "INFO"

    $startTime = Get-Date
    $allReady = $false

    while (-not $allReady -and ((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
        $services = ssh twister@edgeserver.twisterlab.local "docker service ls --filter name=${STACK_NAME}_ --format '{{.Name}} {{.Replicas}}'"

        $readyCount = 0
        $totalCount = 0

        foreach ($line in $services) {
            if ($line -match '(\d+)/(\d+)') {
                $current = [int]$matches[1]
                $desired = [int]$matches[2]

                if ($current -eq $desired -and $desired -gt 0) {
                    $readyCount++
                }
                $totalCount++
            }
        }

        Write-Status "Services prêts: $readyCount/$totalCount" "INFO"

        if ($readyCount -eq $totalCount -and $totalCount -ge $REQUIRED_SERVICES.Count) {
            $allReady = $true
        } else {
            Start-Sleep -Seconds 5
        }
    }

    if ($allReady) {
        Write-Status "Tous les services sont convergés !" "SUCCESS"
        return $true
    } else {
        Write-Status "Timeout - Certains services ne sont pas prêts" "WARNING"
        return $false
    }
}

function Test-ApiHealth {
    Write-Status "Test de santé de l'API..." "INFO"

    try {
        $response = Invoke-WebRequest -Uri "http://192.168.0.30:8000/health" -UseBasicParsing -TimeoutSec 10

        if ($response.StatusCode -eq 200) {
            $health = $response.Content | ConvertFrom-Json
            Write-Status "API Status: $($health.status)" "SUCCESS"
            Write-Status "Uptime: $([math]::Round($health.uptime_seconds / 3600, 2))h" "INFO"
            return $true
        }
    } catch {
        Write-Status "API non accessible: $_" "ERROR"
        return $false
    }

    return $false
}

function Show-ServiceStatus {
    Write-Status "État final des services:" "INFO"

    $services = ssh twister@edgeserver.twisterlab.local "docker service ls --filter name=${STACK_NAME}_ --format 'table {{.Name}}\t{{.Replicas}}\t{{.Image}}'"

    Write-Host "`n$services`n" -ForegroundColor Cyan
}

function Show-DeploymentSummary {
    param([bool]$Success)

    Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
    Write-Host "RÉSUMÉ DU DÉPLOIEMENT" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan

    Write-Host "Environnement: $Environment" -ForegroundColor Yellow
    Write-Host "Stack: $STACK_NAME" -ForegroundColor Yellow
    Write-Host "Status: $(if ($Success) { '[OK] SUCCES' } else { '[ERR] ECHEC' })" -ForegroundColor $(if ($Success) { "Green" } else { "Red" })

    Write-Host "`nEndpoints accessibles:" -ForegroundColor Cyan
    Write-Host "  - API Health:    http://192.168.0.30:8000/health" -ForegroundColor White
    Write-Host "  - API Docs:      http://192.168.0.30:8000/docs" -ForegroundColor White
    Write-Host "  - Traefik:       http://192.168.0.30:8080" -ForegroundColor White
    Write-Host "  - WebUI:         http://192.168.0.30:8083" -ForegroundColor White

    Write-Host "`nCommandes utiles:" -ForegroundColor Cyan
    Write-Host "  docker service ls                          # Lister services" -ForegroundColor Gray
    Write-Host "  docker service logs ${STACK_NAME}_api      # Voir logs API" -ForegroundColor Gray
    Write-Host "  docker stack rm $STACK_NAME                # Supprimer stack" -ForegroundColor Gray

    Write-Host "`n" + ("=" * 80) + "`n" -ForegroundColor Cyan
}

# =============================================================================
# SCRIPT PRINCIPAL
# =============================================================================

Write-Host "`n"
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "[*] TWISTERLAB DEPLOYMENT v1.0" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "Environnement: $Environment" -ForegroundColor Yellow
Write-Host "Stack: $STACK_NAME" -ForegroundColor Yellow
Write-Host ("=" * 80) + "`n" -ForegroundColor Cyan

try {
    # Étape 1: Validation
    if (-not $SkipValidation) {
        if (-not (Test-Prerequisites)) {
            throw "Échec de la validation des prérequis"
        }
    }

    # Étape 2: Préparation répertoires données
    Test-DataDirectories

    # Étape 3: Déploiement
    if (-not (Deploy-Stack)) {
        throw "Échec du déploiement de la stack"
    }

    # Étape 4: Attente convergence
    $servicesReady = Wait-ServicesReady -TimeoutSeconds 120

    # Étape 5: Test API
    Start-Sleep -Seconds 10
    $apiHealthy = Test-ApiHealth

    # Étape 6: Affichage état
    Show-ServiceStatus

    # Résumé
    $success = $servicesReady -and $apiHealthy
    Show-DeploymentSummary -Success $success

    if (-not $success) {
        Write-Status "Déploiement partiellement réussi - Vérifier les logs" "WARNING"
        exit 1
    }

    Write-Status "Deploiement termine avec succes !" "SUCCESS"
    exit 0

} catch {
    Write-Status "Erreur fatale: $_" "ERROR"
    Write-Status $_.ScriptStackTrace "ERROR"

    Show-DeploymentSummary -Success $false
    exit 1
}
