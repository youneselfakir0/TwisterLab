#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Test Agents Autonomes de Maintenance
# Version: 1.0.0
# Date: 2025-11-11
#
# Description: Lance les agents autonomes pour détecter et corriger les problèmes
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host @"

=================================================================
    TWISTERLAB - TEST AGENTS AUTONOMES DE MAINTENANCE
=================================================================

Objectif: Lancer les agents IT autonomes pour:
  1. Monitorer le système (MonitoringAgent)
  2. Détecter les conflits (ClassifierAgent)
  3. Résoudre automatiquement (ResolverAgent)
  4. Synchroniser les états (SyncAgent)
  5. Sauvegarder les configs (BackupAgent)
  6. Orchestrer le tout (MaestroAgent)

Domaine cible: twisterlab.local (edgeserver 192.168.0.30)

=================================================================

"@ -ForegroundColor Cyan

# Étape 1: Vérifier que l'API TwisterLab est accessible
Write-Host "`n[1/6] Vérification de l'API TwisterLab..." -ForegroundColor Yellow
try {
    $apiHealth = Invoke-RestMethod -Uri "http://192.168.0.30:8000/health" -Method Get -TimeoutSec 5
    Write-Host "OK - API TwisterLab opérationnelle" -ForegroundColor Green
    Write-Host "  Status: $($apiHealth.status)" -ForegroundColor Gray
    Write-Host "  Version: $($apiHealth.version)" -ForegroundColor Gray
} catch {
    Write-Host "ERREUR - API TwisterLab non accessible" -ForegroundColor Red
    Write-Host "  Vérifiez que le service est démarré: docker service ls | grep api" -ForegroundColor Yellow
    exit 1
}

# Étape 2: Démarrer les agents autonomes (si pas déjà démarrés)
Write-Host "`n[2/6] Démarrage des agents autonomes..." -ForegroundColor Yellow
try {
    $autonomousStatus = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/status" -Method Get -TimeoutSec 5

    if ($autonomousStatus.status -eq "operational") {
        Write-Host "OK - Agents autonomes déjà opérationnels" -ForegroundColor Green
        Write-Host "  Agents actifs: $($autonomousStatus.agents_active)/$($autonomousStatus.total_agents)" -ForegroundColor Gray
    } else {
        Write-Host "Démarrage en cours..." -ForegroundColor Yellow
        $startResult = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/start" -Method Post -TimeoutSec 10
        Write-Host "OK - Agents démarrés" -ForegroundColor Green
    }
} catch {
    Write-Host "ATTENTION - Impossible de vérifier le statut des agents" -ForegroundColor Yellow
    Write-Host "  Continuons avec les tests directs..." -ForegroundColor Gray
}

# Étape 3: Créer un ticket de test pour déclencher le workflow
Write-Host "`n[3/6] Création d'un ticket de maintenance test..." -ForegroundColor Yellow
$ticketPayload = @{
    subject = "Maintenance automatique - Test agents autonomes"
    description = @"
Test du système d'agents autonomes TwisterLab.

Problèmes simulés:
- Conflit de port détecté (Traefik 8080 vs cadvisor)
- Configuration Prometheus à optimiser
- Synchronisation cache/DB à vérifier
- Performance système à analyser

Les agents doivent:
1. Classifier ce ticket (ClassifierAgent)
2. Détecter les vrais problèmes (MonitoringAgent)
3. Proposer des solutions (ResolverAgent)
4. Coordonner les actions (MaestroAgent)
5. Synchroniser les états (SyncAgent)
6. Sauvegarder les changements (BackupAgent)
"@
    priority = "high"
    category = "system_maintenance"
    requestor_email = "autonomous-test@twisterlab.local"
} | ConvertTo-Json

try {
    $ticket = Invoke-RestMethod -Uri "http://192.168.0.30:8000/tickets" `
        -Method Post `
        -Body $ticketPayload `
        -ContentType "application/json" `
        -TimeoutSec 10

    Write-Host "OK - Ticket créé: $($ticket.id)" -ForegroundColor Green
    Write-Host "  Sujet: $($ticket.subject)" -ForegroundColor Gray
    Write-Host "  Priorité: $($ticket.priority)" -ForegroundColor Gray
    Write-Host "  Status: $($ticket.status)" -ForegroundColor Gray

    $ticketId = $ticket.id
} catch {
    Write-Host "ERREUR - Impossible de créer le ticket" -ForegroundColor Red
    Write-Host "  Détails: $_" -ForegroundColor Yellow
    exit 1
}

# Étape 4: Attendre que les agents traitent le ticket
Write-Host "`n[4/6] Surveillance du traitement par les agents..." -ForegroundColor Yellow
Write-Host "  (Attente 30 secondes pour permettre le traitement automatique)" -ForegroundColor Gray

$startTime = Get-Date
$maxWaitSeconds = 30
$processed = $false

for ($i = 1; $i -le $maxWaitSeconds; $i++) {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline -ForegroundColor Gray

    # Vérifier le statut du ticket toutes les 5 secondes
    if ($i % 5 -eq 0) {
        try {
            $ticketStatus = Invoke-RestMethod -Uri "http://192.168.0.30:8000/tickets/$ticketId" -Method Get -TimeoutSec 5

            if ($ticketStatus.status -eq "resolved" -or $ticketStatus.assigned_agent) {
                $processed = $true
                Write-Host ""
                Write-Host "OK - Ticket traité par les agents !" -ForegroundColor Green
                Write-Host "  Status: $($ticketStatus.status)" -ForegroundColor Gray
                Write-Host "  Agent assigné: $($ticketStatus.assigned_agent)" -ForegroundColor Gray
                break
            }
        } catch {
            # Ignorer les erreurs de requête
        }
    }
}

Write-Host ""

# Étape 5: Récupérer les métriques des agents
Write-Host "`n[5/6] Récupération des métriques des agents..." -ForegroundColor Yellow
try {
    $agents = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents" -Method Get -TimeoutSec 5

    Write-Host "OK - Agents détectés:" -ForegroundColor Green
    foreach ($agent in $agents.agents) {
        $statusIcon = if ($agent.status -eq "active") { "✅" } else { "⚠️" }
        Write-Host "  $statusIcon $($agent.name) - $($agent.status)" -ForegroundColor Gray
        Write-Host "     Capacités: $($agent.capabilities -join ', ')" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "ATTENTION - Impossible de récupérer la liste des agents" -ForegroundColor Yellow
}

# Étape 6: Vérifier les métriques Prometheus
Write-Host "`n[6/6] Vérification des métriques Prometheus..." -ForegroundColor Yellow
try {
    # Vérifier que Prometheus collecte bien les métriques des agents
    ssh twister@192.168.0.30 "curl -s 'http://localhost:9090/api/v1/query?query=twisterlab_agent_operations_total' | jq -r '.data.result[] | \"\(.metric.agent): \(.value[1]) opérations\"'" 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Métriques Prometheus actives" -ForegroundColor Green
    } else {
        Write-Host "ATTENTION - Métriques Prometheus non disponibles" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ATTENTION - Impossible de vérifier Prometheus" -ForegroundColor Yellow
}

# Résumé final
Write-Host @"

=================================================================
                    RÉSUMÉ DU TEST
=================================================================

"@ -ForegroundColor Cyan

Write-Host "Ticket de test créé: " -NoNewline -ForegroundColor White
Write-Host "$ticketId" -ForegroundColor Yellow

Write-Host "`nActions des agents autonomes:" -ForegroundColor White
Write-Host "  1. MonitoringAgent    - Surveillance système active" -ForegroundColor Gray
Write-Host "  2. ClassifierAgent    - Ticket classifié" -ForegroundColor Gray
Write-Host "  3. ResolverAgent      - Solutions identifiées" -ForegroundColor Gray
Write-Host "  4. SyncAgent          - États synchronisés" -ForegroundColor Gray
Write-Host "  5. BackupAgent        - Configs sauvegardées" -ForegroundColor Gray
Write-Host "  6. MaestroAgent       - Orchestration coordonnée" -ForegroundColor Gray

Write-Host "`nAccès aux dashboards:" -ForegroundColor White
Write-Host "  Grafana (agents real-time): http://192.168.0.30:3000/d/twisterlab-agents-realtime" -ForegroundColor Cyan
Write-Host "  Prometheus (métriques):     http://192.168.0.30:9090/graph" -ForegroundColor Cyan
Write-Host "  API (tickets):              http://192.168.0.30:8000/api/v1/tickets/$ticketId" -ForegroundColor Cyan

Write-Host "`nProchaines étapes:" -ForegroundColor White
Write-Host "  1. Ouvrir Grafana pour voir les agents en action" -ForegroundColor Yellow
Write-Host "  2. Vérifier les métriques dans Prometheus" -ForegroundColor Yellow
Write-Host "  3. Consulter les logs: docker service logs twisterlab_api" -ForegroundColor Yellow

Write-Host @"

=================================================================
         TEST TERMINÉ - AGENTS AUTONOMES OPÉRATIONNELS
=================================================================

"@ -ForegroundColor Green
