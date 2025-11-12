# Test ResolverAgent avec SOP SECURITY

$ApiUrl = "http://192.168.0.30:8000"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " TEST RESOLVERAGENT + SOP PASSWORD_RESET" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Ticket security - devrait declencher ResolverAgent avec SOP password_reset
$ticket = @{
    ticket_id = "T-SEC-001"
    title = "User forgot password - need reset"
    description = "User john.doe@company.com cannot login. He forgot his password and needs a password reset with temporary credentials."
} | ConvertTo-Json

Write-Host "Ticket Security:" -ForegroundColor Yellow
Write-Host "  ID: T-SEC-001" -ForegroundColor White
Write-Host "  Probleme: Password reset needed" -ForegroundColor White
Write-Host "  Attendu: ClassifierAgent -> ResolverAgent -> SOP password_reset" -ForegroundColor Gray
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

    Write-Host "ETAPES DU WORKFLOW:" -ForegroundColor Cyan
    Write-Host ""

    $stepNum = 1
    foreach ($step in $result.workflow_results.steps) {
        Write-Host "[$stepNum] $($step.step.ToUpper())" -ForegroundColor Yellow
        Write-Host "    Agent: $($step.agent)" -ForegroundColor White

        if ($step.step -eq "classification") {
            $class = $step.result.classification
            Write-Host "    Categorie: $($class.category)" -ForegroundColor Cyan
            Write-Host "    Priorite: $($class.priority)" -ForegroundColor Cyan
            Write-Host "    Route vers: $($class.routed_to_agent)" -ForegroundColor Cyan
            Write-Host "    Mots-cles: $($step.result.analysis.keywords_found -join ', ')" -ForegroundColor Gray
        }

        if ($step.step -eq "resolution") {
            Write-Host "    SOP Execute: $($step.sop_executed)" -ForegroundColor Green
            Write-Host "    Status SOP: $($step.result.status)" -ForegroundColor $(if($step.result.status -eq "success"){"Green"}else{"Yellow"})

            if ($step.result.result) {
                if ($step.result.result.steps_executed) {
                    Write-Host "    Steps executes:" -ForegroundColor White
                    foreach ($sopStep in $step.result.result.steps_executed) {
                        Write-Host "      ✓ $sopStep" -ForegroundColor Gray
                    }
                }
                if ($step.result.result.estimated_time) {
                    Write-Host "    Duree: $($step.result.result.estimated_time)" -ForegroundColor Cyan
                }
                if ($step.result.result.success_rate) {
                    Write-Host "    Taux succes: $([math]::Round($step.result.result.success_rate * 100))%" -ForegroundColor Green
                }
            }
        }

        Write-Host ""
        $stepNum++
    }

    Write-Host "================================================" -ForegroundColor Green
    Write-Host "WORKFLOW TERMINE!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERREUR:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
}
