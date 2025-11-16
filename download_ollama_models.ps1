# Script pour télécharger les modèles Ollama requis pour Continue IDE Agents
# Exécuter sur CoreRTX (192.168.0.20) ou edgeserver (192.168.0.30)

Write-Host "🚀 Téléchargement des modèles Ollama pour TwisterLab Agents" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Yellow

$models = @(
    "qwen3:8b",           # 8B paramètres - Excellent pour agents
    "deepseek-r1:latest", # Modèle de raisonnement avancé
    "codellama:latest"    # Autocomplétion code
)

foreach ($model in $models) {
    Write-Host "📥 Téléchargement de $model..." -ForegroundColor Cyan
    try {
        & ollama pull $model
        Write-Host "✅ $model téléchargé avec succès" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Erreur lors du téléchargement de $model : $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "🎯 Vérification des modèles disponibles :" -ForegroundColor Yellow
& ollama list

Write-Host ""
Write-Host "✅ Configuration Continue IDE prête pour les agents !" -ForegroundColor Green
Write-Host "💡 Utilise 'Qwen 3 (8B) - Agent Compatible' pour les tâches d'agent" -ForegroundColor Cyan
