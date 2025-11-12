# Generer du trafic pour peupler le dashboard Grafana

$ApiUrl = "http://192.168.0.30:8000"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " GENERATION TRAFIC POUR DASHBOARD" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$tickets = @(
    @{id="T-NET-001"; title="WiFi not working"; desc="Cannot connect to WiFi network"; cat="network"},
    @{id="T-SOFT-002"; title="Install Office 365"; desc="Need Microsoft Office installation"; cat="software"},
    @{id="T-PERF-003"; title="Computer running slow"; desc="System performance is degraded"; cat="performance"},
    @{id="T-SEC-004"; title="Password reset request"; desc="User forgot password"; cat="security"},
    @{id="T-DB-005"; title="Database slow queries"; desc="PostgreSQL needs optimization"; cat="database"},
    @{id="T-HW-006"; title="Disk space full"; desc="Server disk at 95% capacity"; cat="hardware"},
    @{id="T-NET-007"; title="Internet down"; desc="No internet connectivity"; cat="network"},
    @{id="T-SOFT-008"; title="Software update needed"; desc="Update Python to latest version"; cat="software"}
)

$stats = @{sent=0; success=0; failed=0}

foreach ($ticket in $tickets) {
    Write-Host "[$($ticket.id)] $($ticket.title)" -ForegroundColor Yellow

    $body = @{
        ticket_id = $ticket.id
        title = $ticket.title
        description = $ticket.desc
    } | ConvertTo-Json

    try {
        $result = Invoke-RestMethod -Method POST `
            -Uri "$ApiUrl/api/v1/tickets/process" `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30

        $stats.sent++

        if ($result.status -eq "success") {
            Write-Host "  SUCCESS - Categorie: $($ticket.cat)" -ForegroundColor Green
            $stats.success++
        } else {
            Write-Host "  PARTIAL - Status: $($result.status)" -ForegroundColor Yellow
            $stats.failed++
        }

    } catch {
        Write-Host "  ERROR - $($_.Exception.Message)" -ForegroundColor Red
        $stats.failed++
    }

    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "STATISTIQUES" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Tickets envoyes: $($stats.sent)" -ForegroundColor White
Write-Host "  Succes: $($stats.success)" -ForegroundColor Green
Write-Host "  Echecs: $($stats.failed)" -ForegroundColor Red
Write-Host "  Taux succes: $([math]::Round($stats.success / $stats.sent * 100))%" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard Grafana mis a jour avec les metriques!" -ForegroundColor Cyan
Write-Host "URL: http://192.168.0.30:3000/d/9a3af07c-aa4a-4627-bc32-20151bce5887/twisterlab-workflow-autonome" -ForegroundColor Green
