<#
.SYNOPSIS
    Reconfigure Continue IDE pour CoreRTX avec TwisterLab MCP Server

.DESCRIPTION
    Applique la configuration optimisée Continue IDE avec :
    - 6 modèles Ollama (GPU RTX 3060)
    - TwisterLab MCP Server activé
    - Custom commands optimisés par modèle
    - Slash commands pour agents réels
    - Security & production rules

.NOTES
    Author: TwisterLab Team
    Date: 2025-11-15
    Version: 1.0.3
#>

[CmdletBinding()]
param(
    [switch]$Backup,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ContinueDir = "C:\Users\Administrator\.continue"

Write-Host "=== TwisterLab Continue IDE Reconfiguration ===" -ForegroundColor Cyan

# 1. Vérifier que Continue IDE est fermé
Write-Host "`n[1/6] Vérification de Continue IDE..." -ForegroundColor Yellow
$continueProcesses = Get-Process -Name "Code" -ErrorAction SilentlyContinue
if ($continueProcesses -and -not $Force) {
    Write-Host "❌ VS Code est en cours d'exécution. Fermez VS Code ou utilisez -Force" -ForegroundColor Red
    exit 1
}

# 2. Backup de l'ancienne configuration
if ($Backup) {
    Write-Host "`n[2/6] Backup de la configuration actuelle..." -ForegroundColor Yellow
    $backupDir = "$ContinueDir\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

    if (Test-Path "$ContinueDir\config.yaml") {
        Copy-Item "$ContinueDir\config.yaml" "$backupDir\config.yaml.bak"
        Write-Host "  ✅ config.yaml → $backupDir\config.yaml.bak" -ForegroundColor Green
    }

    if (Test-Path "$ContinueDir\config.json") {
        Copy-Item "$ContinueDir\config.json" "$backupDir\config.json.bak"
        Write-Host "  ✅ config.json → $backupDir\config.json.bak" -ForegroundColor Green
    }

    if (Test-Path "$ContinueDir\mcp.json") {
        Copy-Item "$ContinueDir\mcp.json" "$backupDir\mcp.json.bak"
        Write-Host "  ✅ mcp.json → $backupDir\mcp.json.bak" -ForegroundColor Green
    }
} else {
    Write-Host "`n[2/6] Backup désactivé (-Backup:$false)" -ForegroundColor Yellow
}

# 3. Appliquer la nouvelle configuration YAML
Write-Host "`n[3/6] Application de config.optimized.yaml..." -ForegroundColor Yellow
if (Test-Path "$ContinueDir\config.optimized.yaml") {
    Copy-Item "$ContinueDir\config.optimized.yaml" "$ContinueDir\config.yaml" -Force
    Write-Host "  ✅ config.yaml mis à jour" -ForegroundColor Green
} else {
    Write-Host "  ❌ config.optimized.yaml introuvable" -ForegroundColor Red
    exit 1
}

# 4. Appliquer la nouvelle configuration MCP JSON
Write-Host "`n[4/6] Application de mcp.optimized.json..." -ForegroundColor Yellow
if (Test-Path "$ContinueDir\mcp.optimized.json") {
    Copy-Item "$ContinueDir\mcp.optimized.json" "$ContinueDir\mcp.json" -Force
    Write-Host "  ✅ mcp.json mis à jour" -ForegroundColor Green
} else {
    Write-Host "  ❌ mcp.optimized.json introuvable" -ForegroundColor Red
    exit 1
}

# 5. Vérifier Ollama local
Write-Host "`n[5/6] Vérification d'Ollama Desktop (CoreRTX)..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    $models = ($ollamaResponse.Content | ConvertFrom-Json).models
    Write-Host "  ✅ Ollama opérationnel - $($models.Count) modèles disponibles" -ForegroundColor Green

    foreach ($model in $models) {
        $sizeGB = [math]::Round($model.size / 1GB, 2)
        Write-Host "     • $($model.name) - $sizeGB GB" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ⚠️  Ollama non accessible sur localhost:11434" -ForegroundColor Yellow
    Write-Host "     Démarrez Ollama Desktop avant d'utiliser Continue IDE" -ForegroundColor Yellow
}

# 6. Vérifier le serveur MCP TwisterLab
Write-Host "`n[6/6] Vérification du serveur MCP TwisterLab..." -ForegroundColor Yellow
$mcpServerPath = "C:\TwisterLab\agents\mcp\mcp_server_continue_sync.py"
if (Test-Path $mcpServerPath) {
    Write-Host "  ✅ MCP Server: $mcpServerPath" -ForegroundColor Green

    # Vérifier que Python peut l'importer
    try {
        $pythonCheck = python -c "import sys; sys.path.append('C:\\TwisterLab'); from agents.mcp.mcp_server_continue_sync import main; print('OK')" 2>&1
        if ($pythonCheck -match "OK") {
            Write-Host "  ✅ MCP Server importable par Python" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  MCP Server existe mais import échoue:" -ForegroundColor Yellow
            Write-Host "     $pythonCheck" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠️  Impossible de tester l'import Python" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ MCP Server introuvable: $mcpServerPath" -ForegroundColor Red
}

# Résumé final
Write-Host "`n=== Configuration Continue IDE Terminée ===" -ForegroundColor Cyan
Write-Host "`nModèles configurés:" -ForegroundColor White
Write-Host "  🚀 Llama 3.2 (1B) - Ultra Fast" -ForegroundColor Cyan
Write-Host "  💬 Llama 3 (8B) - Chat Expert" -ForegroundColor Cyan
Write-Host "  🧠 DeepSeek R1 - Reasoning Agent" -ForegroundColor Cyan
Write-Host "  💻 CodeLlama - Code Generation" -ForegroundColor Cyan
Write-Host "  🔧 Qwen 3 (8B) - Refactoring Expert" -ForegroundColor Cyan
Write-Host "  👁️ Qwen3 VL - Vision Agent" -ForegroundColor Cyan

Write-Host "`nMCP Servers:" -ForegroundColor White
Write-Host "  ✅ TwisterLab MCP Server activé" -ForegroundColor Green
Write-Host "     Command: python C:\TwisterLab\agents\mcp\mcp_server_continue_sync.py" -ForegroundColor Gray

Write-Host "`nSlash Commands disponibles:" -ForegroundColor White
Write-Host "  /agents   - Liste des 7 agents TwisterLab" -ForegroundColor Cyan
Write-Host "  /health   - État de santé système" -ForegroundColor Cyan
Write-Host "  /classify - Classifier un ticket IT" -ForegroundColor Cyan
Write-Host "  /resolve  - Résoudre un problème IT" -ForegroundColor Cyan
Write-Host "  /deploy   - Guide de déploiement" -ForegroundColor Cyan

Write-Host "`nCustom Commands disponibles:" -ForegroundColor White
Write-Host "  @quick    - Question rapide (Llama 3.2)" -ForegroundColor Cyan
Write-Host "  @explain  - Explication détaillée (Llama 3)" -ForegroundColor Cyan
Write-Host "  @reason   - Analyse complexe (DeepSeek)" -ForegroundColor Cyan
Write-Host "  @code     - Génération code (CodeLlama)" -ForegroundColor Cyan
Write-Host "  @refactor - Refactoring (Qwen 3)" -ForegroundColor Cyan
Write-Host "  @vision   - Analyse image (Qwen3 VL)" -ForegroundColor Cyan

Write-Host "`n🎯 Prochaine étape:" -ForegroundColor Yellow
Write-Host "   1. Démarrez VS Code" -ForegroundColor White
Write-Host "   2. Ouvrez Continue IDE (Ctrl+L)" -ForegroundColor White
Write-Host "   3. Testez: @quick Quelle est la version de TwisterLab ?" -ForegroundColor White
Write-Host "   4. Testez MCP: /agents" -ForegroundColor White

if ($Backup) {
    Write-Host "`n💾 Backup sauvegardé dans: $backupDir" -ForegroundColor Gray
}
