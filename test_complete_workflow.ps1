# Test du workflow complet - Ticket REEL traite de A a Z

$ApiUrl = "http://192.168.0.30:8000"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " TEST WORKFLOW COMPLET - ClassifierAgent -> ResolverAgent" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Ticket reel: probleme reseau
$ticket = @{
    ticket_id = "T-WORKFLOW-001"
    title = "Cannot connect to WiFi - connection keeps dropping"
    description = "User reports that WiFi connection is unstable and drops every few minutes. Network troubleshooting needed."
} | ConvertTo-Json

Write-Host "Ticket a traiter:" -ForegroundColor Yellow
Write-Host "  ID: T-WORKFLOW-001" -ForegroundColor White
Write-Host "  Title: Cannot connect to WiFi" -ForegroundColor White
Write-Host "  Category: (auto-detect)" -ForegroundColor Gray
Write-Host ""

Write-Host "Envoi au workflow..." -ForegroundColor Yellow

try {
    $result = Invoke-RestMethod -Method POST `
        -Uri "$ApiUrl/api/v1/tickets/process" `
        -Body $ticket `
        -ContentType "application/json" `
        -TimeoutSec 60

    Write-Host ""
    Write-Host "RESULTAT WORKFLOW:" -ForegroundColor Green
    Write-Host "  Status: $($result.status)" -ForegroundColor $(if($result.status -eq "success"){"Green"}else{"Red"})
    Write-Host "  Duree: $($result.duration_seconds)s" -ForegroundColor Cyan
    Write-Host ""

    # Afficher les etapes du workflow
    Write-Host "ETAPES EXECUTEES:" -ForegroundColor Cyan
    $stepNum = 1
    foreach ($step in $result.workflow_results.steps) {
        Write-Host ""
        Write-Host "  [$stepNum] $($step.step.ToUpper())" -ForegroundColor Yellow
        Write-Host "      Agent: $($step.agent)" -ForegroundColor White

        if ($step.sop_executed) {
            Write-Host "      SOP: $($step.sop_executed)" -ForegroundColor Cyan
        }

        if ($step.command) {
            Write-Host "      Commande: $($step.command)" -ForegroundColor Cyan
        }

        if ($step.result.status) {
            Write-Host "      Resultat: $($step.result.status)" -ForegroundColor $(if($step.result.status -eq "success"){"Green"}else{"Yellow"})
        }

        $stepNum++
    }

    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "WORKFLOW COMPLET EXECUTE AVEC SUCCES!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resultats complets (JSON):" -ForegroundColor Gray
    $result | ConvertTo-Json -Depth 10

} catch {
    Write-Host ""
    Write-Host "ERREUR:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""

    if ($_.ErrorDetails.Message) {
        Write-Host "Details:" -ForegroundColor Yellow
        $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 5
    }
}
