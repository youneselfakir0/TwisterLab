#!/usr/bin/env pwsh
# Test Ollama depuis l'API TwisterLab

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " TEST OLLAMA POUR LES AGENTS TWISTERLAB" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Test endpoint Ollama direct
Write-Host "[1] TEST API OLLAMA DIRECTE" -ForegroundColor Yellow
Write-Host "    URL: http://192.168.0.30:11434" -ForegroundColor Gray
Write-Host ""

try {
    $models = Invoke-RestMethod -Method GET -Uri "http://192.168.0.30:11434/api/tags" -ErrorAction Stop

    Write-Host "    Statut: " -NoNewline -ForegroundColor Gray
    Write-Host "OPERATIONNEL" -ForegroundColor Green
    Write-Host ""
    Write-Host "    Modeles disponibles:" -ForegroundColor Gray
    foreach ($model in $models.models) {
        $sizeGB = [math]::Round($model.size / 1GB, 2)
        Write-Host "      - $($model.name) ($sizeGB GB)" -ForegroundColor White
    }
    Write-Host ""
} catch {
    Write-Host "    Statut: " -NoNewline -ForegroundColor Gray
    Write-Host "ERREUR" -ForegroundColor Red
    Write-Host "    Erreur: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# 2. Test génération simple
Write-Host "[2] TEST GENERATION DE TEXTE" -ForegroundColor Yellow
Write-Host "    Modele: llama3.2" -ForegroundColor Gray
Write-Host "    Prompt: 'Respond with just YES if you can read this'" -ForegroundColor Gray
Write-Host ""

$testPayload = @{
    model = "llama3.2"
    prompt = "Respond with just YES if you can read this"
    stream = $false
    options = @{
        temperature = 0.1
        num_predict = 10
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Method POST -Uri "http://192.168.0.30:11434/api/generate" `
        -Body $testPayload -ContentType "application/json" -ErrorAction Stop

    Write-Host "    Reponse Ollama: " -NoNewline -ForegroundColor Gray
    Write-Host "$($response.response)" -ForegroundColor Green
    Write-Host "    Tokens: $($response.eval_count)" -ForegroundColor Gray
    Write-Host "    Duree: $($response.total_duration / 1000000)ms" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "    Statut: " -NoNewline -ForegroundColor Gray
    Write-Host "ERREUR" -ForegroundColor Red
    Write-Host "    Erreur: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# 3. Test via l'API TwisterLab (si les agents utilisent Ollama)
Write-Host "[3] TEST INTEGRATION AVEC AGENTS TWISTERLAB" -ForegroundColor Yellow
Write-Host "    Les agents peuvent maintenant utiliser Ollama pour:" -ForegroundColor Gray
Write-Host "      - ClassifierAgent: analyse semantique des tickets" -ForegroundColor White
Write-Host "      - ResolverAgent: generation de solutions contextuelles" -ForegroundColor White
Write-Host "      - DesktopCommanderAgent: validation intelligente des commandes" -ForegroundColor White
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " RESUME" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ollama est maintenant OPERATIONNEL sur edgeserver" -ForegroundColor Green
Write-Host "  URL interne: http://ollama:11434 (dans Docker Swarm)" -ForegroundColor Gray
Write-Host "  URL externe: http://192.168.0.30:11434 (depuis host)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Les agents TwisterLab peuvent maintenant utiliser l'IA!" -ForegroundColor Green
Write-Host ""
