#!/usr/bin/env pwsh
# Pull des modèles Ollama optimisés pour les agents TwisterLab
# Hardware: Intel i5-6600K (4 cores, 3.5GHz) + 31GB RAM (CPU only)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " PULL MODELES OLLAMA POUR AGENTS TWISTERLAB" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Hardware detecte:" -ForegroundColor Yellow
Write-Host "  CPU: Intel i5-6600K (4 cores @ 3.5GHz)" -ForegroundColor Gray
Write-Host "  RAM: 31GB total, ~24GB disponible" -ForegroundColor Gray
Write-Host "  GPU: Aucun (inference CPU uniquement)" -ForegroundColor Gray
Write-Host ""

# Configuration des modèles pour différents agents
$models = @(
    @{
        Name = "llama3.2:3b-instruct-q4_K_M"
        Size = "~2GB"
        Use = "ClassifierAgent - Classification rapide des tickets"
        Speed = "RAPIDE (~1-2s/requete)"
        Quality = "BONNE"
    },
    @{
        Name = "qwen2.5:3b-instruct-q4_K_M"
        Size = "~2GB"
        Use = "ResolverAgent - Generation de solutions IT"
        Speed = "RAPIDE (~1-2s/requete)"
        Quality = "EXCELLENTE (specialise IT/code)"
    },
    @{
        Name = "phi3.5:3.8b-mini-instruct-q4_K_M"
        Size = "~2.3GB"
        Use = "DesktopCommanderAgent - Validation commandes"
        Speed = "TRES RAPIDE (~0.5-1s/requete)"
        Quality = "BONNE (leger et precis)"
    },
    @{
        Name = "mistral:7b-instruct-q4_K_M"
        Size = "~4.1GB"
        Use = "Backup - Modele general haute qualite"
        Speed = "MOYEN (~3-5s/requete)"
        Quality = "EXCELLENTE"
    },
    @{
        Name = "gemma2:2b-instruct-q4_K_M"
        Size = "~1.6GB"
        Use = "MonitoringAgent - Analyse rapide des metriques"
        Speed = "TRES RAPIDE (~0.5s/requete)"
        Quality = "BONNE"
    }
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " MODELES A TELECHARGER" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$totalSize = 0
foreach ($model in $models) {
    Write-Host "[$($model.Name)]" -ForegroundColor Green
    Write-Host "  Taille: $($model.Size)" -ForegroundColor Gray
    Write-Host "  Usage: $($model.Use)" -ForegroundColor White
    Write-Host "  Vitesse: $($model.Speed)" -ForegroundColor Cyan
    Write-Host "  Qualite: $($model.Quality)" -ForegroundColor Yellow
    Write-Host ""

    # Extraire la taille approximative
    if ($model.Size -match "(\d+\.?\d*)GB") {
        $totalSize += [decimal]$matches[1]
    }
}

Write-Host "Espace total requis: ~$([math]::Round($totalSize, 1))GB" -ForegroundColor Yellow
Write-Host "RAM disponible: ~24GB (suffisant)" -ForegroundColor Green
Write-Host ""

# Confirmation
Write-Host "Voulez-vous telecharger ces modeles? (O/N): " -NoNewline -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne "O" -and $confirm -ne "o") {
    Write-Host "Annule." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " TELECHARGEMENT EN COURS..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0
$skippedCount = 0

foreach ($model in $models) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Telechargement: $($model.Name)" -ForegroundColor Cyan
    Write-Host "   Usage prevu: $($model.Use)" -ForegroundColor Gray

    try {
        # Pull via SSH vers edgeserver
        $pullCmd = "docker exec `$(docker ps -q -f name=twisterlab_ollama) ollama pull $($model.Name)"

        $result = ssh twister@192.168.0.30 $pullCmd 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Status: " -NoNewline -ForegroundColor Gray
            Write-Host "SUCCESS" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "   Status: " -NoNewline -ForegroundColor Gray
            Write-Host "ECHEC" -ForegroundColor Red
            Write-Host "   Erreur: $result" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "   Status: " -NoNewline -ForegroundColor Gray
        Write-Host "ERREUR" -ForegroundColor Red
        Write-Host "   Exception: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }

    Write-Host ""
    Start-Sleep -Seconds 2
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " VERIFICATION DES MODELES" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

try {
    $installedModels = Invoke-RestMethod -Method GET -Uri "http://192.168.0.30:11434/api/tags" -ErrorAction Stop

    Write-Host "Modeles disponibles dans Ollama:" -ForegroundColor Yellow
    foreach ($model in $installedModels.models) {
        $sizeGB = [math]::Round($model.size / 1GB, 2)
        $quantization = $model.details.quantization_level
        Write-Host "  - $($model.name)" -ForegroundColor Green
        Write-Host "    Taille: $sizeGB GB | Quantization: $quantization" -ForegroundColor Gray
    }
    Write-Host ""
} catch {
    Write-Host "Erreur lors de la verification: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " RESUME" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Telechargements reussis: $successCount" -ForegroundColor Green
Write-Host "  Echecs: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "  Les agents peuvent maintenant utiliser ces modeles!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Configuration recommandee pour agents:" -ForegroundColor Yellow
    Write-Host "    ClassifierAgent -> llama3.2:3b-instruct-q4_K_M" -ForegroundColor White
    Write-Host "    ResolverAgent -> qwen2.5:3b-instruct-q4_K_M" -ForegroundColor White
    Write-Host "    DesktopCommanderAgent -> phi3.5:3.8b-mini-instruct-q4_K_M" -ForegroundColor White
    Write-Host "    MonitoringAgent -> gemma2:2b-instruct-q4_K_M" -ForegroundColor White
    Write-Host "    Backup/General -> mistral:7b-instruct-q4_K_M" -ForegroundColor White
    Write-Host ""
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
