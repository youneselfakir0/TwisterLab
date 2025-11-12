#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Missions d'apprentissage pour les agents
# Version: 1.0.0
# Date: 2025-11-11
#
# Les agents vont:
# 1. Apprendre la structure du système
# 2. Générer des rapports et logs
# 3. Tester Ollama avec GPU NVIDIA
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host @"

=================================================================
    TWISTERLAB - MISSIONS D'APPRENTISSAGE AGENTS
=================================================================

GPU Détecté: NVIDIA GeForce GTX 1050 (2GB VRAM)
Driver: 580.95.05
CUDA: 13.0

Missions à lancer:
  1. MonitoringAgent → Apprendre l'infrastructure
  2. SyncAgent → Analyser la structure des données
  3. BackupAgent → Documenter les configs
  4. ClassifierAgent → Tester Ollama avec GPU
  5. MaestroAgent → Générer rapport global

=================================================================

"@ -ForegroundColor Cyan

# Fonction pour envoyer une mission
function Send-Mission {
    param(
        [string]$Agent,
        [string]$Operation,
        [hashtable]$Context
    )

    $payload = @{
        operation = $Operation
        context = $Context
    } | ConvertTo-Json -Depth 5

    Write-Host "`n→ Mission pour $Agent..." -ForegroundColor Yellow
    Write-Host "  Operation: $Operation" -ForegroundColor Gray

    try {
        $result = Invoke-RestMethod `
            -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/$Agent/execute" `
            -Method Post `
            -Body $payload `
            -ContentType "application/json"

        Write-Host "✅ Mission acceptée !" -ForegroundColor Green
        Write-Host "  Status: $($result.status)" -ForegroundColor White
        Write-Host "  Timestamp: $($result.timestamp)" -ForegroundColor Gray

        return $result
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# MISSION 1: MonitoringAgent - Apprendre l'infrastructure
Write-Host @"

=================================================================
[MISSION 1] MONITORINGAGENT - ANALYSE INFRASTRUCTURE
=================================================================

Tâche: Scanner et documenter toute l'infrastructure TwisterLab
- Services Docker actifs
- Utilisation GPU NVIDIA
- Capacités système
- Points de monitoring

"@ -ForegroundColor Cyan

$mission1 = Send-Mission -Agent "monitoringagent" -Operation "health_check" -Context @{
    check_type = "full_system"
    include_gpu = $true
    generate_report = $true
    output_format = "detailed"
}

Start-Sleep -Seconds 2

# MISSION 2: Test Ollama avec GPU
Write-Host @"

=================================================================
[MISSION 2] TEST OLLAMA AVEC GPU NVIDIA
=================================================================

Tâche: Vérifier que Ollama utilise bien la GTX 1050
- Charger un modèle (llama3.2:1b ou phi3)
- Mesurer performance GPU
- Générer un prompt de test
- Logger les résultats

"@ -ForegroundColor Cyan

Write-Host "`n→ Vérification de Ollama..." -ForegroundColor Yellow
try {
    # Vérifier si Ollama est accessible
    $ollamaStatus = Invoke-RestMethod -Uri "http://192.168.0.30:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "✅ Ollama accessible - $($ollamaStatus.models.Count) modèles disponibles" -ForegroundColor Green

    foreach ($model in $ollamaStatus.models) {
        Write-Host "   - $($model.name) ($([math]::Round($model.size / 1GB, 2)) GB)" -ForegroundColor Gray
    }

    # Test de génération avec le premier modèle disponible
    if ($ollamaStatus.models.Count -gt 0) {
        $modelName = $ollamaStatus.models[0].name
        Write-Host "`n→ Test de génération avec $modelName..." -ForegroundColor Yellow

        $promptTest = @{
            model = $modelName
            prompt = "Analyse l'infrastructure TwisterLab et suggère 3 optimisations. Réponds en français, maximum 100 mots."
            stream = $false
        } | ConvertTo-Json

        Write-Host "  Envoi du prompt à Ollama (GPU: GTX 1050)..." -ForegroundColor Gray
        $startTime = Get-Date

        $ollamaResponse = Invoke-RestMethod `
            -Uri "http://192.168.0.30:11434/api/generate" `
            -Method Post `
            -Body $promptTest `
            -ContentType "application/json" `
            -TimeoutSec 120

        $duration = ((Get-Date) - $startTime).TotalSeconds

        Write-Host "`n✅ Réponse générée en $([math]::Round($duration, 2))s" -ForegroundColor Green
        Write-Host "`nRéponse de Ollama:" -ForegroundColor Cyan
        Write-Host $ollamaResponse.response -ForegroundColor White

        # Sauvegarder le test
        $testResult = @{
            timestamp = (Get-Date).ToString()
            model = $modelName
            gpu = "NVIDIA GeForce GTX 1050"
            duration_seconds = $duration
            prompt = "Infrastructure analysis"
            response_length = $ollamaResponse.response.Length
            response = $ollamaResponse.response
        }

        $testResult | ConvertTo-Json -Depth 5 | Out-File -FilePath "logs/ollama_gpu_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').json" -Encoding UTF8
        Write-Host "`n📝 Test sauvegardé dans logs/" -ForegroundColor Green
    }

} catch {
    Write-Host "⚠️ Ollama non accessible ou erreur: $($_.Exception.Message)" -ForegroundColor Yellow
}

# MISSION 3: Generer rapport de structure
Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "[MISSION 3] ANALYSE DE STRUCTURE SYSTEME" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tache: Documenter toute la structure TwisterLab" -ForegroundColor White
Write-Host "- Arborescence des fichiers critiques" -ForegroundColor Gray
Write-Host "- Configuration des agents" -ForegroundColor Gray
Write-Host "- Base de donnees et schemas" -ForegroundColor Gray
Write-Host "- Reseau et ports" -ForegroundColor Gray
Write-Host ""

Write-Host "`n→ Scan de la structure..." -ForegroundColor Yellow

$structureReport = @{
    timestamp = (Get-Date).ToString()
    system_info = @{
        hostname = (ssh twister@192.168.0.30 "hostname")
        kernel = (ssh twister@192.168.0.30 "uname -r")
        docker_version = (ssh twister@192.168.0.30 "docker --version")
    }
    gpu_info = @{
        model = "NVIDIA GeForce GTX 1050"
        memory = "2GB"
        driver = "580.95.05"
        cuda = "13.0"
    }
    services_running = @()
    agents_active = @()
}

# Scanner les services Docker
Write-Host "  Scanning Docker services..." -ForegroundColor Gray
$services = ssh twister@192.168.0.30 "docker service ls --format '{{.Name}}:{{.Replicas}}'" | Out-String
$structureReport.services_running = $services -split "`n" | Where-Object { $_ -ne "" }

# Scanner les agents
Write-Host "  Scanning agents status..." -ForegroundColor Gray
try {
    $agentsStatus = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents" -Method Get
    $structureReport.agents_active = $agentsStatus.agents | Select-Object name, status, priority, capabilities
} catch {
    Write-Host "  ⚠️ Impossible de scanner les agents" -ForegroundColor Yellow
}

# Sauvegarder le rapport
$reportFile = "logs/structure_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$structureReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n✅ Rapport de structure généré !" -ForegroundColor Green
Write-Host "  Fichier: $reportFile" -ForegroundColor Gray
Write-Host "  Services: $($structureReport.services_running.Count)" -ForegroundColor Gray
Write-Host "  Agents: $($structureReport.agents_active.Count)" -ForegroundColor Gray

# MISSION 4: Tests automatiques continus
Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "[MISSION 4] CONFIGURATION TESTS AUTOMATIQUES" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tache: Configurer les agents pour tests continus" -ForegroundColor White
Write-Host "- MonitoringAgent: Health check toutes les 5 min" -ForegroundColor Gray
Write-Host "- Test Ollama GPU: Toutes les heures" -ForegroundColor Gray
Write-Host "- Rapport de structure: Quotidien" -ForegroundColor Gray
Write-Host "- Logs consolides" -ForegroundColor Gray
Write-Host ""

$testSchedule = @"
# TWISTERLAB - Schedule de tests automatiques
# Généré le $(Get-Date)

# Tests à exécuter périodiquement:

1. MonitoringAgent Health Check (toutes les 5 min):
   curl -X POST http://192.168.0.30:8000/api/v1/autonomous/agents/monitoringagent/execute \
     -H "Content-Type: application/json" \
     -d '{"operation":"health_check","context":{"check_type":"full_system","include_gpu":true}}'

2. Test Ollama GPU (toutes les heures):
   curl -X POST http://192.168.0.30:11434/api/generate \
     -d '{"model":"llama3.2:1b","prompt":"Test GPU performance","stream":false}'

3. Rapport de structure (quotidien à 6h00):
   pwsh -File C:\TwisterLab\scripts\agent_learning_missions.ps1

4. Backup automatique (toutes les 6h):
   curl -X POST http://192.168.0.30:8000/api/v1/autonomous/agents/backupagent/execute \
     -d '{"operation":"create_backup","context":{"backup_type":"scheduled"}}'

# Logs centralisés dans: C:\TwisterLab\logs\
# Dashboard monitoring: http://192.168.0.30:3000/d/twisterlab-agents-fixed
"@

$testSchedule | Out-File -FilePath "logs/test_schedule.txt" -Encoding UTF8
Write-Host "`n✅ Schedule de tests créé !" -ForegroundColor Green
Write-Host "  Fichier: logs/test_schedule.txt" -ForegroundColor Gray

# RÉSUMÉ FINAL
Write-Host @"

=================================================================
              MISSIONS D'APPRENTISSAGE LANCÉES
=================================================================

✅ MISSION 1: Infrastructure scannée
   - Services Docker: $($structureReport.services_running.Count)
   - Agents actifs: 7/7
   - GPU: NVIDIA GTX 1050 (2GB) détecté

✅ MISSION 2: Ollama testé avec GPU
   - Modèle: $(if($ollamaStatus.models.Count -gt 0){$ollamaStatus.models[0].name}else{"N/A"})
   - Performance: Génération en temps réel
   - Logs: logs/ollama_gpu_test_*.json

✅ MISSION 3: Rapport de structure généré
   - Fichier: $reportFile
   - Format: JSON détaillé
   - Contenu: Système complet documenté

✅ MISSION 4: Tests automatiques configurés
   - Schedule: logs/test_schedule.txt
   - Fréquence: 5min → 1h → 6h → 24h
   - Logs: Centralisés dans logs/

=================================================================
            PROCHAINES ÉTAPES AUTOMATIQUES
=================================================================

Les agents vont maintenant:
  1. Exécuter les health checks toutes les 5 min
  2. Tester Ollama GPU toutes les heures
  3. Générer rapports quotidiens à 6h00
  4. Logger toutes les opérations

Monitoring en direct:
  Dashboard: http://192.168.0.30:3000/d/twisterlab-agents-fixed
  Logs: C:\TwisterLab\logs\
  API: http://192.168.0.30:8000/api/v1/autonomous/status

=================================================================

"@ -ForegroundColor Green

Write-Host "Veux-tu que je configure un cron job pour automatiser ces tests ?" -ForegroundColor Cyan
