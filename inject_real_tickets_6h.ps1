# 🎯 INJECTION DE TICKETS RÉELS - TWISTERLAB
# Durée: 6 heures - Tickets basés sur infrastructure réelle

param(
    [int]$DurationHours = 6,
    [string]$ApiUrl = "http://192.168.0.30:8000"
)

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   TWISTERLAB - TEST AGENTS RÉELS (6 HEURES)           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Tickets réels détectés sur ton infrastructure
$realTickets = @(
    @{
        delay_minutes = 0
        ticket = @{
            ticket_id = "T-REAL-001"
            title = "3 services systemd en échec"
            description = "systemd-networkd-wait-online.service, sssd-nss.socket, sssd-pam-priv.socket sont en état failed"
            category = "system"
            priority = "medium"
            metadata = @{
                services_failed = @("systemd-networkd-wait-online.service", "sssd-nss.socket", "sssd-pam-priv.socket")
                action_required = "Redémarrage services + diagnostic cause"
                sop = "SOP-SYSTEM-001"
            }
        }
    },
    @{
        delay_minutes = 30
        ticket = @{
            ticket_id = "T-REAL-002"
            title = "Disque système à 57% d'utilisation"
            description = "/dev/mapper/ubuntu--vg-ubuntu--lv utilise 53G sur 98G (57%)"
            category = "performance"
            priority = "low"
            metadata = @{
                disk_usage = "57%"
                disk_used = "53G"
                disk_total = "98G"
                threshold = "60%"
                action_required = "Nettoyage /tmp, logs, cache"
                sop = "SOP-003"
            }
        }
    },
    @{
        delay_minutes = 60
        ticket = @{
            ticket_id = "T-REAL-006"
            title = "Service réseau systemd-networkd-wait-online failed"
            description = "Timeout réseau au démarrage, vérification connectivité requise"
            category = "network"
            priority = "medium"
            metadata = @{
                service = "systemd-networkd-wait-online.service"
                error = "Timeout waiting for network"
                action_required = "Diagnostic réseau complet"
                sop = "SOP-001"
            }
        }
    },
    @{
        delay_minutes = 120
        ticket = @{
            ticket_id = "T-REAL-003"
            title = "Container twisterlab_api redémarré récemment"
            description = "API container up depuis seulement 16 minutes - investigation crash potentiel"
            category = "docker"
            priority = "high"
            metadata = @{
                container = "twisterlab_api"
                uptime = "16 minutes"
                status = "Running"
                action_required = "Analyse logs pour cause redémarrage"
                sop = "SOP-DOCKER-001"
            }
        }
    },
    @{
        delay_minutes = 150
        ticket = @{
            ticket_id = "T-REAL-004"
            title = "Health check routine - 11 conteneurs actifs"
            description = "Vérification santé de tous les services Docker en production"
            category = "monitoring"
            priority = "low"
            metadata = @{
                containers_count = 11
                services = @("twisterlab_api", "postgres", "redis", "grafana", "prometheus", "traefik")
                action_required = "Health check + métriques"
                sop = "SOP-DOCKER-002"
            }
        }
    },
    @{
        delay_minutes = 240
        ticket = @{
            ticket_id = "T-REAL-005"
            title = "PostgreSQL - Optimisation base de données requise"
            description = "Container postgres up 12h - exécuter VACUUM ANALYZE pour optimisation"
            category = "database"
            priority = "medium"
            metadata = @{
                database = "twisterlab_prod"
                uptime = "12 hours"
                action_required = "VACUUM, ANALYZE, index check"
                sop = "SOP-005"
            }
        }
    },
    @{
        delay_minutes = 330
        ticket = @{
            ticket_id = "T-REAL-007"
            title = "Load average élevé (2.03, 1.54, 1.57)"
            description = "Serveur uptime 7 jours, load average > 2.0 - investigation CPU nécessaire"
            category = "performance"
            priority = "medium"
            metadata = @{
                load_1min = "2.03"
                load_5min = "1.54"
                load_15min = "1.57"
                uptime = "7 days, 7:44"
                threshold = "1.5"
                action_required = "Identifier processus gourmands"
                sop = "SOP-PERF-001"
            }
        }
    }
)

# Fonction pour injecter un ticket
function Inject-Ticket {
    param($ticketData)

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "📋 Injection ticket: " -NoNewline -ForegroundColor Yellow
    Write-Host "$($ticketData.ticket_id) - $($ticketData.title)" -ForegroundColor White

    $body = $ticketData | ConvertTo-Json -Depth 10

    try {
        # Créer le ticket via API
        $response = Invoke-RestMethod -Method POST `
            -Uri "$ApiUrl/api/v1/tickets" `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30 `
            -ErrorAction Stop

        Write-Host "   ✅ Ticket injecté avec succès" -ForegroundColor Green
        Write-Host "   → Catégorie: $($ticketData.category) | Priorité: $($ticketData.priority)" -ForegroundColor Cyan

        # Attendre un peu que l'orchestrateur traite
        Start-Sleep -Seconds 5

        # Vérifier si le ticket a été classifié
        try {
            $status = Invoke-RestMethod -Method GET `
                -Uri "$ApiUrl/api/v1/tickets/$($ticketData.ticket_id)" `
                -TimeoutSec 10 `
                -ErrorAction SilentlyContinue

            if ($status.agent_assigned) {
                Write-Host "   → Agent assigné: $($status.agent_assigned)" -ForegroundColor Green
            }
        } catch {
            # Pas grave si le GET échoue
        }

        return $true

    } catch {
        Write-Host "   ❌ Erreur injection: $($_.Exception.Message)" -ForegroundColor Red

        # Si l'API n'a pas l'endpoint /tickets, on utilise directement l'agent
        try {
            Write-Host "   🔄 Tentative via ClassifierAgent..." -ForegroundColor Yellow

            $agentBody = @{
                operation = "classify_ticket"
                ticket = $ticketData
            } | ConvertTo-Json -Depth 10

            $response = Invoke-RestMethod -Method POST `
                -Uri "$ApiUrl/api/v1/autonomous/agents/ClassifierAgent/execute" `
                -Body $agentBody `
                -ContentType "application/json" `
                -TimeoutSec 30

            Write-Host "   ✅ Ticket traité via ClassifierAgent" -ForegroundColor Green
            return $true

        } catch {
            Write-Host "   ❌ Échec ClassifierAgent: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
}

# Fonction monitoring
function Get-AgentStatus {
    try {
        $health = Invoke-RestMethod -Uri "$ApiUrl/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        return "✅ API: $($health.status)"
    } catch {
        return "❌ API: unreachable"
    }
}

# Démarrage du test
$startTime = Get-Date
$endTime = $startTime.AddHours($DurationHours)

Write-Host "📅 Début du test: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "📅 Fin prévue: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "⏱️  Durée: $DurationHours heures" -ForegroundColor Cyan
Write-Host "🎯 Tickets à injecter: $($realTickets.Count)" -ForegroundColor Cyan
Write-Host ""

# Vérifier que l'API est accessible
Write-Host "🔍 Vérification API..." -NoNewline
$apiStatus = Get-AgentStatus
Write-Host " $apiStatus" -ForegroundColor $(if($apiStatus -match "✅"){"Green"}else{"Red"})

if ($apiStatus -notmatch "✅") {
    Write-Host ""
    Write-Host "⚠️  WARNING: API non accessible, tentative de continuer quand même..." -ForegroundColor Yellow
    Write-Host ""
}

# Initialisation statistiques
$stats = @{
    tickets_injected = 0
    tickets_success = 0
    tickets_failed = 0
    start_time = $startTime
}

# Créer fichier log
$logFile = "test_real_tickets_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"=== TWISTERLAB REAL TICKETS TEST ===" | Out-File $logFile
"Start: $startTime" | Out-File $logFile -Append
"" | Out-File $logFile -Append

# Injection des tickets avec délais
foreach ($item in $realTickets) {
    $currentTime = Get-Date
    $elapsed = ($currentTime - $startTime).TotalMinutes

    # Attendre le délai spécifié
    if ($item.delay_minutes -gt $elapsed) {
        $waitMinutes = $item.delay_minutes - $elapsed
        Write-Host ""
        Write-Host "⏳ Attente $([Math]::Round($waitMinutes, 1)) minutes avant prochain ticket..." -ForegroundColor Yellow
        Write-Host "   (Prochain: $($item.ticket.ticket_id) à $(($startTime.AddMinutes($item.delay_minutes)).ToString('HH:mm:ss')))" -ForegroundColor Gray
        Write-Host ""

        Start-Sleep -Seconds ([Math]::Max(1, $waitMinutes * 60))
    }

    # Injecter le ticket
    $success = Inject-Ticket -ticketData $item.ticket

    $stats.tickets_injected++
    if ($success) {
        $stats.tickets_success++
    } else {
        $stats.tickets_failed++
    }

    # Logger
    $logEntry = "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] $($item.ticket.ticket_id) - $(if($success){'SUCCESS'}else{'FAILED'})"
    $logEntry | Out-File $logFile -Append

    Write-Host ""
    Write-Host "───────────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
}

# Rapport final
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              TEST TERMINÉ - RAPPORT FINAL              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 STATISTIQUES:" -ForegroundColor Cyan
Write-Host "   • Durée totale: $([Math]::Round(((Get-Date) - $startTime).TotalHours, 2))h" -ForegroundColor White
Write-Host "   • Tickets injectés: $($stats.tickets_injected)" -ForegroundColor White
Write-Host "   • Succès: $($stats.tickets_success)" -ForegroundColor Green
Write-Host "   • Échecs: $($stats.tickets_failed)" -ForegroundColor $(if($stats.tickets_failed -gt 0){"Red"}else{"White"})
Write-Host "   • Taux de succès: $([Math]::Round($stats.tickets_success / $stats.tickets_injected * 100, 1))%" -ForegroundColor $(if($stats.tickets_success -eq $stats.tickets_injected){"Green"}else{"Yellow"})
Write-Host ""
Write-Host "📄 Log complet: $logFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Test terminé avec succès !" -ForegroundColor Green
