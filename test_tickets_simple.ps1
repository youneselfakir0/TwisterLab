# 🎯 INJECTION DE TICKETS RÉELS - TWISTERLAB (VERSION SIMPLIFIÉE)
# Durée: 1 heure de test - Tickets basés sur infrastructure réelle

param(
    [string]$ApiUrl = "http://192.168.0.30:8000"
)

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   TWISTERLAB - TEST AGENTS RÉELS (1 HEURE)            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Tickets réels détectés
$tickets = @(
    @{
        id = "T-REAL-001"
        title = "3 services systemd en échec"
        category = "system"
        priority = "medium"
        delay = 0
    },
    @{
        id = "T-REAL-002"
        title = "Disque système à 57% d'utilisation"
        category = "performance"
        priority = "low"
        delay = 10
    },
    @{
        id = "T-REAL-003"
        title = "Container twisterlab_api redémarré récemment"
        category = "docker"
        priority = "high"
        delay = 20
    },
    @{
        id = "T-REAL-004"
        title = "Health check - 11 conteneurs actifs"
        category = "monitoring"
        priority = "low"
        delay = 30
    }
)

$startTime = Get-Date
Write-Host "📅 Début: $($startTime.ToString('HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "🎯 Tickets: $($tickets.Count)" -ForegroundColor Cyan
Write-Host ""

# Vérifier API
Write-Host "🔍 Vérification API..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "$ApiUrl/health" -TimeoutSec 5
    Write-Host " ✅ $($health.status)" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  API non accessible" -ForegroundColor Yellow
}
Write-Host ""

$stats = @{ success = 0; failed = 0 }

foreach ($ticket in $tickets) {
    if ($ticket.delay -gt 0) {
        Write-Host "⏳ Attente $($ticket.delay) secondes..." -ForegroundColor Yellow
        Start-Sleep -Seconds $ticket.delay
    }

    Write-Host "📋 [$($ticket.id)] $($ticket.title)" -ForegroundColor White
    Write-Host "   Catégorie: $($ticket.category) | Priorité: $($ticket.priority)" -ForegroundColor Cyan

    # Essayer via ClassifierAgent directement
    $body = @{
        operation = "classify_ticket"
        ticket = @{
            ticket_id = $ticket.id
            title = $ticket.title
            category = $ticket.category
            priority = $ticket.priority
            timestamp = (Get-Date -Format "o")
        }
    } | ConvertTo-Json -Depth 10

    try {
        $result = Invoke-RestMethod -Method POST `
            -Uri "$ApiUrl/api/v1/autonomous/agents/ClassifierAgent/execute" `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30

        if ($result.status -eq "completed") {
            Write-Host "   ✅ Classifié avec succès" -ForegroundColor Green
            $stats.success++
        } else {
            Write-Host "   ⚠️  Status: $($result.status)" -ForegroundColor Yellow
            $stats.failed++
        }

    } catch {
        Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        $stats.failed++
    }

    Write-Host ""
}

# Rapport
$duration = ((Get-Date) - $startTime).TotalMinutes
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  TEST TERMINÉ                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 RÉSULTATS:" -ForegroundColor Cyan
Write-Host "   • Durée: $([Math]::Round($duration, 1)) minutes" -ForegroundColor White
Write-Host "   • Tickets: $($tickets.Count)" -ForegroundColor White
Write-Host "   • Succès: $($stats.success)" -ForegroundColor Green
Write-Host "   • Échecs: $($stats.failed)" -ForegroundColor $(if($stats.failed -gt 0){"Red"}else{"White"})
Write-Host ""
Write-Host "✅ Test terminé !" -ForegroundColor Green
