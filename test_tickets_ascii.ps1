# INJECTION DE TICKETS REELS - TWISTERLAB
# Duree: Test rapide - Tickets bases sur infrastructure reelle

param(
    [string]$ApiUrl = "http://192.168.0.30:8000"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TWISTERLAB - TEST AGENTS REELS               " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Tickets reels detectes
$tickets = @(
    @{
        id = "T-REAL-001"
        title = "3 services systemd en echec"
        category = "system"
        priority = "medium"
        delay = 0
    },
    @{
        id = "T-REAL-002"
        title = "Disque systeme a 57% d'utilisation"
        category = "performance"
        priority = "low"
        delay = 10
    },
    @{
        id = "T-REAL-003"
        title = "Container twisterlab_api redemarre recemment"
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
Write-Host "Debut: $($startTime.ToString('HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "Tickets: $($tickets.Count)" -ForegroundColor Cyan
Write-Host ""

# Verifier API
Write-Host "Verification API..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "$ApiUrl/health" -TimeoutSec 5
    Write-Host " OK - $($health.status)" -ForegroundColor Green
} catch {
    Write-Host " WARNING - API non accessible" -ForegroundColor Yellow
}
Write-Host ""

$stats = @{ success = 0; failed = 0 }

foreach ($ticket in $tickets) {
    if ($ticket.delay -gt 0) {
        Write-Host "Attente $($ticket.delay) secondes..." -ForegroundColor Yellow
        Start-Sleep -Seconds $ticket.delay
    }

    Write-Host "[$($ticket.id)] $($ticket.title)" -ForegroundColor White
    Write-Host "  Categorie: $($ticket.category) | Priorite: $($ticket.priority)" -ForegroundColor Cyan

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
            Write-Host "  SUCCESS - Classifie avec succes" -ForegroundColor Green
            $stats.success++
        } elseif ($result.status -eq "error") {
            Write-Host "  ERROR - Agent non trouve (normal, pas encore charge)" -ForegroundColor Yellow
            Write-Host "  Message: $($result.error)" -ForegroundColor Gray
            $stats.failed++
        } else {
            Write-Host "  WARNING - Status: $($result.status)" -ForegroundColor Yellow
            $stats.failed++
        }

    } catch {
        Write-Host "  ERROR - $($_.Exception.Message)" -ForegroundColor Red
        $stats.failed++
    }

    Write-Host ""
}

# Rapport
$duration = ((Get-Date) - $startTime).TotalMinutes
Write-Host "================================================" -ForegroundColor Green
Write-Host "            TEST TERMINE                        " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "RESULTATS:" -ForegroundColor Cyan
Write-Host "  Duree: $([Math]::Round($duration, 1)) minutes" -ForegroundColor White
Write-Host "  Tickets: $($tickets.Count)" -ForegroundColor White
Write-Host "  Succes: $($stats.success)" -ForegroundColor Green
Write-Host "  Echecs: $($stats.failed)" -ForegroundColor $(if($stats.failed -gt 0){"Red"}else{"White"})
Write-Host ""
Write-Host "Test termine !" -ForegroundColor Green
