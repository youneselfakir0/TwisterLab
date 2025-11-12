# ================================================================
# TEST TICKET OLLAMA - TRAITEMENT AUTONOME PAR LES AGENTS
# ================================================================
# Ce ticket sera traité par:
#   ClassifierAgent -> ResolverAgent -> Exécution SOP
# ================================================================

$apiUrl = "http://192.168.0.30:8000/api/v1/tickets/process"

# Ticket réaliste: Ollama ne démarre pas
$ticket = @{
    ticket_id = "T-OLLAMA-001"
    title = "Ollama service fails to start"
    description = @"
User reports that Ollama service is not starting on the server.
Error message: 'Failed to start ollama.service: Unit ollama.service not found'

Expected behavior: Ollama should be running and accessible on port 11434
Actual behavior: Service not found, cannot run AI models locally

Environment:
- Server: edgeserver.twisterlab.local
- OS: Ubuntu 22.04
- Expected port: 11434
- User: twister

Steps already tried:
1. Checked service status: systemctl status ollama
2. Attempted restart: systemctl restart ollama
3. Both failed with 'unit not found' error

Impact: Users cannot run local AI models, affecting development workflow
"@
    priority = "high"
    category = "software"
    reported_by = "admin@twisterlab.local"
    created_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
} | ConvertTo-Json -Depth 10

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host " TICKET OLLAMA - TRAITEMENT AUTONOME" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "Ticket ID: T-OLLAMA-001" -ForegroundColor Yellow
Write-Host "Probleme: Ollama service ne demarre pas" -ForegroundColor Yellow
Write-Host "Priorite: HIGH" -ForegroundColor Red
Write-Host "Categorie attendue: software" -ForegroundColor Yellow
Write-Host "`nAgent attendu: ClassifierAgent -> ResolverAgent" -ForegroundColor Green
Write-Host "SOP attendu: software_install (ou equivalent)" -ForegroundColor Green

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host " ENVOI DU TICKET AU WORKFLOW" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Method POST -Uri $apiUrl -Body $ticket -ContentType "application/json" -ErrorAction Stop

    Write-Host "✓ REPONSE RECUE" -ForegroundColor Green
    Write-Host "`n================================================" -ForegroundColor Cyan
    Write-Host " RESULTATS DU WORKFLOW" -ForegroundColor Cyan
    Write-Host "================================================`n" -ForegroundColor Cyan

    Write-Host "Status: $($response.status)" -ForegroundColor $(if ($response.status -eq "success") { "Green" } else { "Red" })
    Write-Host "Duree: $($response.duration_seconds)s" -ForegroundColor Cyan

    if ($response.workflow_results.steps) {
        Write-Host "`nETAPES DU WORKFLOW:" -ForegroundColor Yellow

        foreach ($step in $response.workflow_results.steps) {
            Write-Host "`n[$($step.step.ToUpper())]" -ForegroundColor Cyan
            Write-Host "  Agent: $($step.agent)" -ForegroundColor White

            if ($step.step -eq "classification") {
                $classif = $step.result.classification
                Write-Host "  Categorie: $($classif.category)" -ForegroundColor Yellow
                Write-Host "  Confiance: $($classif.confidence)" -ForegroundColor Yellow
                Write-Host "  Priorite: $($classif.priority)" -ForegroundColor Yellow
                Write-Host "  Route vers: $($classif.routed_to_agent)" -ForegroundColor Green

                if ($step.result.analysis.keywords_found) {
                    Write-Host "  Mots-cles: $($step.result.analysis.keywords_found -join ', ')" -ForegroundColor Gray
                }
            }
            elseif ($step.step -eq "resolution") {
                Write-Host "  SOP Execute: $($step.sop_executed)" -ForegroundColor Cyan
                Write-Host "  Resultat: $($step.result.status)" -ForegroundColor $(if ($step.result.status -eq "success") { "Green" } else { "Yellow" })

                if ($step.result.error) {
                    Write-Host "  Erreur: $($step.result.error)" -ForegroundColor Red
                }

                if ($step.result.steps_executed) {
                    Write-Host "`n  ETAPES SOP EXECUTEES:" -ForegroundColor Magenta
                    foreach ($sopStep in $step.result.steps_executed) {
                        Write-Host "    - $sopStep" -ForegroundColor Gray
                    }
                }
            }
            elseif ($step.step -eq "command_execution") {
                Write-Host "  Commande: $($step.command)" -ForegroundColor Yellow
                Write-Host "  Resultat: $($step.result.status)" -ForegroundColor $(if ($step.result.status -eq "success") { "Green" } else { "Yellow" })

                if ($step.result.output) {
                    Write-Host "  Output:" -ForegroundColor Gray
                    Write-Host "    $($step.result.output)" -ForegroundColor DarkGray
                }
            }
        }
    }

    if ($response.workflow_results.summary) {
        Write-Host "`n================================================" -ForegroundColor Cyan
        Write-Host " RESUME" -ForegroundColor Cyan
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host $response.workflow_results.summary -ForegroundColor White
    }

    Write-Host "`n================================================" -ForegroundColor Green
    Write-Host " TICKET TRAITE PAR LES AGENTS" -ForegroundColor Green
    Write-Host "================================================`n" -ForegroundColor Green

} catch {
    Write-Host "✗ ERREUR" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

    if ($_.ErrorDetails.Message) {
        Write-Host "`nDetails:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Gray
    }
}

Write-Host "`nVoir dashboard Grafana pour metriques:" -ForegroundColor Cyan
Write-Host "http://192.168.0.30:3000/d/9a3af07c-aa4a-4627-bc32-20151bce5887/twisterlab-workflow-autonome" -ForegroundColor Blue
}
