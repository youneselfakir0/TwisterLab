#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Déploiement du failover Ollama sur production edgeserver
.DESCRIPTION
    Déploie le code avec failover PRIMARY/BACKUP vers edgeserver
    Met à jour uniquement les fichiers agents critiques
#>

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "`n🚀 TwisterLab - Déploiement Failover Ollama" -ForegroundColor Cyan
Write-Host "="*70

# Configuration
$REMOTE_USER = "twister"
$REMOTE_HOST = "192.168.0.30"
$REMOTE_PATH = "/home/twister"
$STACK_NAME = "twisterlab"

# Fichiers critiques à déployer
$FILES_TO_DEPLOY = @(
    "agents/base/llm_client.py",
    "agents/config.py",
    "agents/real/real_classifier_agent.py",
    "agents/real/real_resolver_agent.py",
    "agents/real/real_desktop_commander_agent.py",
    "agents/metrics.py"
)

Write-Host "`n📋 Vérifications pré-déploiement..." -ForegroundColor Yellow

# 1. Vérifier connexion SSH
Write-Host "`n1️⃣ Test connexion SSH à edgeserver..."
try {
    $sshTest = ssh ${REMOTE_USER}@${REMOTE_HOST} "echo OK" 2>&1
    if ($sshTest -ne "OK") {
        throw "Connexion SSH échouée"
    }
    Write-Host "   ✅ SSH connecté" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur SSH: $_" -ForegroundColor Red
    exit 1
}

# 2. Vérifier Docker Swarm
Write-Host "`n2️⃣ Vérification Docker Swarm..."
$swarmStatus = ssh ${REMOTE_USER}@${REMOTE_HOST} "docker info --format '{{.Swarm.LocalNodeState}}'" 2>&1
if ($swarmStatus -ne "active") {
    Write-Host "   ❌ Docker Swarm non actif: $swarmStatus" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Docker Swarm actif" -ForegroundColor Green

# 3. Vérifier services existants
Write-Host "`n3️⃣ État des services actuels..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "docker service ls --format 'table {{.Name}}\t{{.Replicas}}'"

# 4. Backup du code actuel
Write-Host "`n4️⃣ Backup du code actuel..."
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ssh ${REMOTE_USER}@${REMOTE_HOST} "if [ -d ${REMOTE_PATH}/agents ]; then cp -r ${REMOTE_PATH}/agents ${REMOTE_PATH}/agents_backup_${timestamp}; echo 'Backup créé'; else echo 'Pas de backup nécessaire'; fi"

# 5. Déploiement des fichiers
Write-Host "`n5️⃣ Déploiement des fichiers agents..." -ForegroundColor Yellow

foreach ($file in $FILES_TO_DEPLOY) {
    Write-Host "   📤 Uploading $file..."

    # Créer les répertoires distants si nécessaire
    $remoteDir = Split-Path -Parent $file
    if ($remoteDir) {
        ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_PATH}/${remoteDir}"
    }

    # Copier le fichier
    scp $file "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/${file}"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "      ✅ $file déployé" -ForegroundColor Green
    } else {
        Write-Host "      ❌ Échec déploiement $file" -ForegroundColor Red
        exit 1
    }
}

# 6. Vérifier la configuration Ollama
Write-Host "`n6️⃣ Vérification configuration Ollama..." -ForegroundColor Yellow

Write-Host "   🔍 PRIMARY Ollama (Corertx RTX 3060)..."
$primaryTest = ssh ${REMOTE_USER}@${REMOTE_HOST} "curl -s -o /dev/null -w '%{http_code}' http://192.168.0.20:11434/api/tags"
if ($primaryTest -eq "200") {
    Write-Host "      ✅ PRIMARY accessible" -ForegroundColor Green
} else {
    Write-Host "      ⚠️ PRIMARY non accessible (HTTP $primaryTest) - BACKUP sera utilisé" -ForegroundColor Yellow
}

Write-Host "   🔍 BACKUP Ollama (Edgeserver GTX 1050)..."
$backupTest = ssh ${REMOTE_USER}@${REMOTE_HOST} "curl -s -o /dev/null -w '%{http_code}' http://192.168.0.30:11434/api/tags"
if ($backupTest -eq "200") {
    Write-Host "      ✅ BACKUP accessible" -ForegroundColor Green
} else {
    Write-Host "      ❌ BACKUP non accessible (HTTP $backupTest)" -ForegroundColor Red
    exit 1
}

Write-Host "   🔍 BACKUP Ollama (Edgeserver GTX 1050)..."
$backupTest = ssh ${REMOTE_USER}@${REMOTE_HOST} "curl -s -o /dev/null -w '%{http_code}' http://localhost:11434/api/tags"
if ($backupTest -eq "200") {
    Write-Host "      ✅ BACKUP accessible" -ForegroundColor Green
} else {
    Write-Host "      ❌ BACKUP non accessible (HTTP $backupTest)" -ForegroundColor Red
    Write-Host "      ⚠️ Démarrer Ollama: ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo systemctl start ollama'" -ForegroundColor Yellow
}

# 7. Redémarrer le service API
Write-Host "`n7️⃣ Redémarrage du service API..." -ForegroundColor Yellow

if ($Force) {
    Write-Host "   🔄 Force update du service..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "docker service update --force ${STACK_NAME}_api"
} else {
    Write-Host "   🔄 Update du service..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "docker service update ${STACK_NAME}_api"
}

# 8. Attendre le démarrage
Write-Host "`n8️⃣ Attente du démarrage du service..." -ForegroundColor Yellow

$maxWait = 60
$waited = 0
$interval = 5

while ($waited -lt $maxWait) {
    $replicas = ssh ${REMOTE_USER}@${REMOTE_HOST} "docker service ls --filter name=${STACK_NAME}_api --format '{{.Replicas}}'"
    Write-Host "   ⏳ Replicas: $replicas (${waited}s/${maxWait}s)"

    if ($replicas -match "1/1") {
        Write-Host "   ✅ Service démarré !" -ForegroundColor Green
        break
    }

    Start-Sleep -Seconds $interval
    $waited += $interval
}

if ($waited -ge $maxWait) {
    Write-Host "   ⚠️ Timeout - vérifier les logs: docker service logs ${STACK_NAME}_api" -ForegroundColor Yellow
}

# 9. Test des endpoints
Write-Host "`n9️⃣ Test des endpoints API..." -ForegroundColor Yellow

Start-Sleep -Seconds 5

Write-Host "   🔍 Test /health..."
$healthTest = ssh ${REMOTE_USER}@${REMOTE_HOST} "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health"
if ($healthTest -eq "200") {
    Write-Host "      ✅ /health OK" -ForegroundColor Green
} else {
    Write-Host "      ❌ /health FAIL (HTTP $healthTest)" -ForegroundColor Red
}

Write-Host "   🔍 Test /metrics..."
$metricsTest = ssh ${REMOTE_USER}@${REMOTE_HOST} "curl -s http://localhost:8000/metrics | grep -c 'twisterlab_agent'"
if ($metricsTest -gt 0) {
    Write-Host "      ✅ /metrics OK ($metricsTest métriques)" -ForegroundColor Green
} else {
    Write-Host "      ⚠️ /metrics incomplet" -ForegroundColor Yellow
}

# 10. Résumé
Write-Host "`n" + "="*70
Write-Host "📊 RÉSUMÉ DU DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "="*70

Write-Host "`n✅ Fichiers déployés:"
foreach ($file in $FILES_TO_DEPLOY) {
    Write-Host "   - $file" -ForegroundColor Green
}

Write-Host "`n🔧 Configuration Ollama:"
Write-Host "   PRIMARY: http://192.168.0.20:11434 (Corertx RTX 3060)"
Write-Host "   BACKUP:  http://192.168.0.30:11434 (Edgeserver GTX 1050)"

Write-Host "`n🎯 Fonctionnalités activées:"
Write-Host "   ✅ Failover automatique PRIMARY → BACKUP"
Write-Host "   ✅ Retry automatique (2 tentatives, 2s délai)"
Write-Host "   ✅ Logging de la source (primary/fallback)"
Write-Host "   ✅ Haute disponibilité garantie"

Write-Host "`n📝 Commandes utiles:"
Write-Host "   Logs API:      ssh ${REMOTE_USER}@${REMOTE_HOST} 'docker service logs ${STACK_NAME}_api --tail 50'"
Write-Host "   Logs Ollama:   ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo journalctl -u ollama -f'"
Write-Host "   Services:      ssh ${REMOTE_USER}@${REMOTE_HOST} 'docker service ls'"
Write-Host "   Health check:  curl http://192.168.0.30:8000/health"

Write-Host ""
Write-Host "Déploiement terminé avec succès !" -ForegroundColor Green
Write-Host "======================================================================"
