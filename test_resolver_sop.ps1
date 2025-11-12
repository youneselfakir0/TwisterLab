# Test ResolverAgent avec SOP - Ticket Performance

$ApiUrl = "http://192.168.0.30:8000"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " TEST RESOLVERAGENT + SOP EXECUTION" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Ticket performance - devrait declencher ResolverAgent avec SOP disk_cleanup
$ticket = @{
    ticket_id = "T-PERF-001"
    title = "Server running slow - disk space is low"
    description = "The server performance is degrading. Disk usage is at 95% and system is very slow. Need cleanup and optimization."
} | ConvertTo-Json

Write-Host "Ticket Performance:" -ForegroundColor Yellow
Write-Host "  ID: T-PERF-001" -ForegroundColor White
Write-Host "  Probleme: Disk space low + slow performance" -ForegroundColor White
Write-Host "  Attendu: ClassifierAgent -> ResolverAgent -> SOP disk_cleanup" -ForegroundColor Gray
Write-Host ""

Write-Host "Envoi au workflow..." -ForegroundColor Yellow

try {
    $result = Invoke-RestMethod -Method POST `
        -Uri "$ApiUrl/api/v1/tickets/process" `
        -Body $ticket `
        -ContentType "application/json" `
        -TimeoutSec 60

    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "RESULTAT WORKFLOW" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  Status: $($result.status)" -ForegroundColor $(if($result.status -eq "success"){"Green"}else{"Red"})
    Write-Host "  Duree: $($result.duration_seconds)s" -ForegroundColor Cyan
    Write-Host ""

    # Afficher chaque etape
    Write-Host "ETAPES DU WORKFLOW:" -ForegroundColor Cyan
    Write-Host ""

    $stepNum = 1
    foreach ($step in $result.workflow_results.steps) {
        Write-Host "[$stepNum] $($step.step.ToUpper())" -ForegroundColor Yellow
        Write-Host "    Agent: $($step.agent)" -ForegroundColor White

        # Classification
        if ($step.step -eq "classification") {
            $class = $step.result.classification
            Write-Host "    Categorie: $($class.category)" -ForegroundColor Cyan
            Write-Host "    Priorite: $($class.priority)" -ForegroundColor Cyan
            Write-Host "    Route vers: $($class.routed_to_agent)" -ForegroundColor Cyan
            Write-Host "    Mots-cles: $($step.result.analysis.keywords_found -join ', ')" -ForegroundColor Gray
        }

        # Resolution (SOP)
        if ($step.step -eq "resolution") {
            Write-Host "    SOP Execute: $($step.sop_executed)" -ForegroundColor Green
            if ($step.result.result) {
                Write-Host "    Steps SOP:" -ForegroundColor White
                foreach ($sopStep in $step.result.result.steps_executed) {
                    Write-Host "      - $sopStep" -ForegroundColor Gray
                }
                if ($step.result.result.estimated_time) {
                    Write-Host "    Duree estimee: $($step.result.result.estimated_time)" -ForegroundColor Cyan
                }
            }
        }

        # Command execution
        if ($step.step -eq "command_execution") {
            Write-Host "    Commande: $($step.command)" -ForegroundColor Cyan
            if ($step.result.output) {
                Write-Host "    Output: $($step.result.output)" -ForegroundColor Gray
            }
        }

        Write-Host "    Resultat: $($step.result.status)" -ForegroundColor $(if($step.result.status -eq "success"){"Green"}else{"Yellow"})
        Write-Host ""

        $stepNum++
    }

    Write-Host "================================================" -ForegroundColor Green
    Write-Host "WORKFLOW TERMINE AVEC SUCCES!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resume: $($result.workflow_results.summary)" -ForegroundColor Cyan
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERREUR:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""

    if ($_.ErrorDetails.Message) {
        Write-Host "Details:" -ForegroundColor Yellow
        $_.ErrorDetails.Message
    }
}
