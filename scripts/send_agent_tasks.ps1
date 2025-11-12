#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Envoyer des tâches aux agents via prompts
# Version: 1.0.0
# Date: 2025-11-11
#
# Description: Interface pour contrôler les agents autonomes avec du texte
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host @"

=================================================================
    TWISTERLAB - CONTROLE DES AGENTS PAR PROMPTS
=================================================================

Les agents comprennent le langage naturel !
Pas besoin de modifier le code - juste envoyer des instructions.

=================================================================

"@ -ForegroundColor Cyan

# Fonction pour envoyer une tâche à un agent
function Send-AgentTask {
    param(
        [string]$Agent,
        [string]$Operation,
        [hashtable]$Context = @{}
    )

    $payload = @{
        operation = $Operation
        context = $Context
    } | ConvertTo-Json

    Write-Host "`n→ Envoi à $Agent..." -ForegroundColor Yellow
    Write-Host "  Operation: $Operation" -ForegroundColor Gray
    Write-Host "  Context: $($Context | ConvertTo-Json -Compress)" -ForegroundColor Gray

    try {
        $result = Invoke-RestMethod `
            -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/$Agent/execute" `
            -Method Post `
            -Body $payload `
            -ContentType "application/json"

        Write-Host "✅ Succès !" -ForegroundColor Green
        Write-Host "  Status: $($result.status)" -ForegroundColor White
        if ($result.result) {
            Write-Host "  Résultat:" -ForegroundColor White
            $result.result | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
        }

        return $result
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Menu interactif
while ($true) {
    Write-Host @"

=================================================================
            EXEMPLES DE TÂCHES À ENVOYER AUX AGENTS
=================================================================

[1] MonitoringAgent - Vérifier la santé du système
[2] BackupAgent - Créer un backup maintenant
[3] SyncAgent - Synchroniser cache et DB
[4] ClassifierAgent - Analyser un problème
[5] ResolverAgent - Résoudre un incident
[6] MaestroAgent - Orchestrer une maintenance
[7] Custom - Entrer une tâche personnalisée
[0] Quitter

"@ -ForegroundColor White

    $choice = Read-Host "Choix"

    switch ($choice) {
        "1" {
            Write-Host "`n=== MONITORING AGENT - HEALTH CHECK ===" -ForegroundColor Cyan
            Send-AgentTask -Agent "monitoringagent" -Operation "health_check" -Context @{
                check_type = "full_system"
                include_details = $true
            }
        }

        "2" {
            Write-Host "`n=== BACKUP AGENT - BACKUP MAINTENANT ===" -ForegroundColor Cyan
            $target = Read-Host "Backup de quoi? (prometheus/grafana/config/all)"
            Send-AgentTask -Agent "backupagent" -Operation "create_backup" -Context @{
                backup_type = "manual"
                target = $target
                timestamp = (Get-Date -Format "yyyy-MM-dd_HH-mm-ss")
            }
        }

        "3" {
            Write-Host "`n=== SYNC AGENT - SYNCHRONISATION ===" -ForegroundColor Cyan
            Send-AgentTask -Agent "syncagent" -Operation "sync_all" -Context @{
                sync_type = "cache_to_db"
                verify = $true
            }
        }

        "4" {
            Write-Host "`n=== CLASSIFIER AGENT - ANALYSE ===" -ForegroundColor Cyan
            $problem = Read-Host "Décris le problème"
            Send-AgentTask -Agent "classifieragent" -Operation "classify" -Context @{
                description = $problem
                auto_route = $true
            }
        }

        "5" {
            Write-Host "`n=== RESOLVER AGENT - RESOLUTION ===" -ForegroundColor Cyan
            $issue = Read-Host "Quel problème résoudre?"
            Send-AgentTask -Agent "resolveragent" -Operation "resolve" -Context @{
                issue_type = $issue
                auto_execute = $false  # Preview first
            }
        }

        "6" {
            Write-Host "`n=== MAESTRO AGENT - ORCHESTRATION ===" -ForegroundColor Cyan
            $task = Read-Host "Quelle maintenance? (update/optimize/cleanup)"
            Send-AgentTask -Agent "maestroorchestratoragent" -Operation "orchestrate" -Context @{
                workflow_type = $task
                agents_to_coordinate = @("monitoring", "sync", "backup")
            }
        }

        "7" {
            Write-Host "`n=== TÂCHE PERSONNALISÉE ===" -ForegroundColor Cyan
            $agent = Read-Host "Agent (ex: monitoringagent)"
            $operation = Read-Host "Operation (ex: custom_task)"
            $description = Read-Host "Description de la tâche"

            Send-AgentTask -Agent $agent -Operation $operation -Context @{
                task = $description
                timestamp = (Get-Date).ToString()
            }
        }

        "0" {
            Write-Host "`nAu revoir ! Les agents continuent de travailler en arrière-plan." -ForegroundColor Green
            break
        }

        default {
            Write-Host "Choix invalide" -ForegroundColor Red
        }
    }

    Write-Host "`nAppuyez sur Entrée pour continuer..." -ForegroundColor Gray
    Read-Host
}

Write-Host @"

=================================================================
        AGENTS TOUJOURS ACTIFS EN ARRIÈRE-PLAN
=================================================================

Les agents continuent leur travail automatique:
  - MonitoringAgent: Surveillance toutes les 30s
  - SyncAgent: Synchronisation toutes les 5 min
  - BackupAgent: Backups toutes les 6h

Dashboard: http://192.168.0.30:3000/d/twisterlab-agents-fixed
API Status: http://192.168.0.30:8000/api/v1/autonomous/status

=================================================================

"@ -ForegroundColor Cyan
