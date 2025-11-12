<#
.SYNOPSIS
    Audit complet de toutes les instances Ollama dans TwisterLab

.DESCRIPTION
    Analyse:
    - Ollama CLI sur edgeserver (192.168.0.30:11434)
    - Ollama Desktop sur corertx (Windows)
    - Ollama WSL sur corertx (si installé)
    - Modèles téléchargés sur chaque instance
    - Utilisation dans le code TwisterLab

.OUTPUTS
    Fichier audit_ollama_results_<timestamp>.txt
#>

$ErrorActionPreference = "Continue"

# Timestamp pour fichier de sortie
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "audit_ollama_results_$timestamp.txt"

function Write-Section {
    param($title)
    $line = "=" * 64
    Write-Host "`n$line" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "$line" -ForegroundColor Cyan
}

function Write-SubSection {
    param($title)
    Write-Host "`n--- $title ---" -ForegroundColor Yellow
}

function Write-Result {
    param($status, $msg)
    $icon = if ($status -eq "ok") { "[OK]" } elseif ($status -eq "warn") { "[WARN]" } else { "[ERROR]" }
    $color = if ($status -eq "ok") { "Green" } elseif ($status -eq "warn") { "Yellow" } else { "Red" }
    Write-Host "  $icon $msg" -ForegroundColor $color
}

Write-Host ""
Write-Section "TWISTERLAB - AUDIT OLLAMA MULTI-INSTANCES"
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "Output: $outputFile" -ForegroundColor Gray
Write-Host ""

# Début du transcript
Start-Transcript -Path $outputFile -Append

# ============================================================================
# 1. OLLAMA CLI SUR EDGESERVER (192.168.0.30)
# ============================================================================
Write-Section "1. OLLAMA CLI - edgeserver (192.168.0.30:11434)"

try {
    Write-SubSection "Service Status"
    $edgeStatus = ssh twister@192.168.0.30 "systemctl is-active ollama 2>/dev/null || echo 'inactive'" 2>$null
    if ($edgeStatus -match "active") {
        Write-Result "ok" "Service Ollama actif sur edgeserver"
    } else {
        Write-Result "error" "Service Ollama non actif: $edgeStatus"
    }

    Write-SubSection "Version"
    $edgeVersion = ssh twister@192.168.0.30 "ollama --version 2>/dev/null" 2>$null
    if ($edgeVersion) {
        Write-Result "ok" "Version: $edgeVersion"
    } else {
        Write-Result "error" "Impossible de recuperer la version"
    }

    Write-SubSection "API Test"
    try {
        $edgeApi = Invoke-RestMethod -Uri "http://192.168.0.30:11434/api/tags" -TimeoutSec 5 2>$null
        Write-Result "ok" "API accessible (HTTP 200)"
    } catch {
        Write-Result "error" "API non accessible: $_"
    }

    Write-SubSection "Modeles Installes"
    $edgeModels = ssh twister@192.168.0.30 @"
curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for m in data.get('models', []):
        size_gb = round(m['size'] / (1024**3), 2)
        print(f\"{m['name']}|{size_gb}|{m.get('modified_at', 'N/A')[:10]}\")
except:
    pass
"
"@ 2>$null

    if ($edgeModels) {
        $modelList = $edgeModels -split "`n" | Where-Object { $_ -ne "" }
        foreach ($model in $modelList) {
            $parts = $model -split "\|"
            if ($parts.Count -eq 3) {
                Write-Result "ok" "$($parts[0].PadRight(30)) - $($parts[1]) GB (Modified: $($parts[2]))"
            }
        }
    } else {
        Write-Result "warn" "Aucun modele trouve ou erreur de parsing"
    }

    Write-SubSection "Espace Disque"
    $edgeDisk = ssh twister@192.168.0.30 "du -sh ~/.ollama/models 2>/dev/null || echo 'N/A'" 2>$null
    Write-Result "ok" "Dossier modeles: $edgeDisk"

    Write-SubSection "Processus Ollama"
    $edgeProcess = ssh twister@192.168.0.30 "ps aux | grep -E 'ollama|llama' | grep -v grep | wc -l" 2>$null
    Write-Result "ok" "$edgeProcess processus Ollama actifs"

} catch {
    Write-Result "error" "Erreur connexion edgeserver: $_"
}

# ============================================================================
# 2. OLLAMA DESKTOP SUR CORERTX (WINDOWS)
# ============================================================================
Write-Section "2. OLLAMA DESKTOP - corertx (Windows/localhost)"

Write-SubSection "Detection Processus"
$ollamaProcess = Get-Process -Name "ollama*" -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Result "ok" "Processus Ollama actif (PID: $($ollamaProcess.Id))"
    Write-Host "     CPU: $($ollamaProcess.CPU)s | Memory: $([math]::Round($ollamaProcess.WorkingSet/1MB, 2)) MB" -ForegroundColor Gray
} else {
    Write-Result "warn" "Aucun processus Ollama detecte"
}

Write-SubSection "Installation"
$ollamaPaths = @(
    "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
    "$env:LOCALAPPDATA\Ollama\ollama.exe",
    "C:\Program Files\Ollama\ollama.exe",
    "$env:ProgramFiles\Ollama\ollama.exe"
)

$foundOllama = $false
foreach ($path in $ollamaPaths) {
    if (Test-Path $path) {
        $foundOllama = $true
        Write-Result "ok" "Installe: $path"
        try {
            $version = & $path --version 2>$null
            Write-Host "     Version: $version" -ForegroundColor Gray
        } catch {
            Write-Result "warn" "Impossible de lire la version"
        }
        break
    }
}

if (-not $foundOllama) {
    Write-Result "error" "Ollama Desktop non trouve dans les chemins standards"
}

Write-SubSection "API Test (localhost:11434)"
try {
    $localResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5
    Write-Result "ok" "API accessible"

    if ($localResponse.models) {
        Write-SubSection "Modeles Installes (localhost)"
        foreach ($model in $localResponse.models) {
            $sizeGB = [math]::Round($model.size / 1GB, 2)
            $name = $model.name.PadRight(30)
            Write-Result "ok" "$name - $sizeGB GB"
        }
    } else {
        Write-Result "warn" "Aucun modele installe"
    }
} catch {
    Write-Result "error" "API non accessible: $_"
    Write-Host "     Verifier si Ollama Desktop est demarre" -ForegroundColor Yellow
}

Write-SubSection "Dossier Modeles"
$modelPaths = @(
    "$env:USERPROFILE\.ollama\models",
    "$env:LOCALAPPDATA\Ollama\models"
)

foreach ($path in $modelPaths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size / 1GB, 2)
        Write-Result "ok" "Dossier: $path ($sizeGB GB)"

        # Liste des fichiers modeles
        $modelFiles = Get-ChildItem $path -Recurse -Include "*.bin","*.gguf" -ErrorAction SilentlyContinue
        if ($modelFiles) {
            Write-Host "     Fichiers modeles: $($modelFiles.Count)" -ForegroundColor Gray
        }
        break
    }
}

# ============================================================================
# 3. OLLAMA WSL SUR CORERTX
# ============================================================================
Write-Section "3. OLLAMA WSL - corertx (Ubuntu WSL)"

Write-SubSection "Detection WSL"
try {
    $wslList = wsl --list --quiet 2>$null
    if ($wslList) {
        Write-Result "ok" "WSL installe"
        Write-Host "     Distributions:" -ForegroundColor Gray
        wsl --list --verbose | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }

        Write-SubSection "Ollama dans WSL"
        $wslOllamaCheck = wsl bash -c "which ollama 2>/dev/null" 2>$null
        if ($wslOllamaCheck) {
            Write-Result "warn" "Ollama trouve dans WSL: $wslOllamaCheck"

            $wslVersion = wsl bash -c "ollama --version 2>/dev/null" 2>$null
            Write-Host "     Version: $wslVersion" -ForegroundColor Gray

            $wslService = wsl bash -c "systemctl is-active ollama 2>/dev/null || service ollama status 2>/dev/null | head -1" 2>$null
            if ($wslService -match "active|running") {
                Write-Result "warn" "Service Ollama ACTIF dans WSL (CONFLIT potentiel avec Desktop)"
            } else {
                Write-Result "ok" "Service Ollama non actif dans WSL"
            }

            # Check processus
            $wslProcess = wsl bash -c "ps aux | grep ollama | grep -v grep | wc -l" 2>$null
            if ($wslProcess -gt 0) {
                Write-Result "warn" "$wslProcess processus Ollama dans WSL"
            }

            # Check modeles
            $wslModels = wsl bash -c "ls -lh ~/.ollama/models 2>/dev/null | grep -v total | wc -l" 2>$null
            if ($wslModels -gt 0) {
                Write-Result "ok" "$wslModels fichiers dans ~/.ollama/models"
            }
        } else {
            Write-Result "ok" "Ollama non installe dans WSL"
        }

    } else {
        Write-Result "ok" "WSL non installe (pas de conflit)"
    }
} catch {
    Write-Result "error" "Erreur audit WSL: $_"
}

# ============================================================================
# 4. UTILISATION DANS LE CODE TWISTERLAB
# ============================================================================
Write-Section "4. UTILISATION OLLAMA DANS LE CODE"

Write-SubSection "Recherche References Ollama"
$ollamaRefs = Get-ChildItem -Path "agents","api","tests" -Recurse -Include *.py -ErrorAction SilentlyContinue |
    Select-String -Pattern "ollama|11434|OLLAMA" -CaseSensitive:$false |
    Select-Object Path, LineNumber, Line

if ($ollamaRefs) {
    $grouped = $ollamaRefs | Group-Object Path
    Write-Result "ok" "$($grouped.Count) fichiers referencent Ollama"

    foreach ($group in $grouped | Select-Object -First 5) {
        $fileName = Split-Path $group.Name -Leaf
        Write-Host "     [FILE] $fileName ($($group.Count) refs)" -ForegroundColor Cyan

        $group.Group | Select-Object -First 2 | ForEach-Object {
            $line = $_.Line.Trim()
            if ($line.Length -gt 70) { $line = $line.Substring(0, 67) + "..." }
            Write-Host "        L$($_.LineNumber): $line" -ForegroundColor DarkGray
        }
    }

    if ($grouped.Count -gt 5) {
        Write-Host "     ... et $($grouped.Count - 5) autres fichiers" -ForegroundColor Gray
    }
} else {
    Write-Result "warn" "Aucune reference Ollama trouvee"
}

Write-SubSection "Imports LLM/Ollama"
$llmImports = Get-ChildItem -Path "agents" -Recurse -Include *.py -ErrorAction SilentlyContinue |
    Select-String -Pattern "from agents.*llm|import.*LLM|import.*ollama|llm_client" -CaseSensitive:$false

if ($llmImports) {
    $importGroups = $llmImports | Group-Object Path
    Write-Result "ok" "$($importGroups.Count) fichiers avec imports LLM"

    foreach ($group in $importGroups | Select-Object -First 5) {
        $fileName = Split-Path $group.Name -Leaf
        Write-Host "     [IMPORT] $fileName" -ForegroundColor Cyan
        $group.Group | Select-Object -First 2 | ForEach-Object {
            Write-Host "        $($_.Line.Trim())" -ForegroundColor DarkGray
        }
    }
}

Write-SubSection "Modules LLM Existants"
$llmModules = Get-ChildItem -Path "agents" -Recurse -Include "*llm*.py" -ErrorAction SilentlyContinue
if ($llmModules) {
    Write-Result "ok" "$($llmModules.Count) modules LLM trouves"
    foreach ($mod in $llmModules) {
        $relativePath = $mod.FullName.Replace((Get-Location).Path, "").TrimStart("\")
        Write-Host "     [MODULE] $relativePath" -ForegroundColor Cyan
    }
} else {
    Write-Result "warn" "Aucun module LLM trouve"
}

# ============================================================================
# 5. ANALYSE DÉTAILLÉE DES AGENTS
# ============================================================================
Write-Section "5. ANALYSE AGENTS UTILISANT LLM"

Write-SubSection "Agents Real (Production)"
$realAgents = Get-ChildItem -Path "agents\real" -Filter "*.py" -ErrorAction SilentlyContinue

if ($realAgents) {
    foreach ($agent in $realAgents) {
        $content = Get-Content $agent.FullName -Raw

        # Check import LLMClient
        if ($content -match "from agents\.base\.llm_client import") {
            Write-Result "warn" "$($agent.Name) - Utilise ancien agents.base.llm_client"
        } elseif ($content -match "from agents\.llm\.ollama_client import") {
            Write-Result "ok" "$($agent.Name) - Utilise nouveau agents.llm.ollama_client"
        } elseif ($content -match "llm|LLM") {
            Write-Result "warn" "$($agent.Name) - Reference LLM mais import unclear"
        } else {
            Write-Host "     [SKIP] $($agent.Name) - Pas de reference LLM" -ForegroundColor Gray
        }

        # Check logger
        if ($content -notmatch "logger\s*=\s*logging\.getLogger") {
            if ($content -match "\blogger\b") {
                Write-Result "error" "$($agent.Name) - Utilise logger sans l'initialiser"
            }
        }
    }
} else {
    Write-Result "warn" "Aucun agent real trouve"
}

# ============================================================================
# 6. RÉSUMÉ & RECOMMANDATIONS
# ============================================================================
Write-Section "6. RESUME & RECOMMANDATIONS"

Write-Host ""
Write-Host "Instances Ollama detectees:" -ForegroundColor Cyan
Write-Host "  1. edgeserver CLI      (192.168.0.30:11434) - Status: $(if ($edgeStatus -match 'active') { 'ACTIF' } else { 'INACTIF' })" -ForegroundColor Gray
Write-Host "  2. corertx Desktop     (localhost:11434)    - Status: $(if ($ollamaProcess) { 'ACTIF' } else { 'INACTIF' })" -ForegroundColor Gray
Write-Host "  3. corertx WSL         (localhost:11434)    - Status: $(if ($wslOllamaCheck) { 'INSTALLE' } else { 'NON INSTALLE' })" -ForegroundColor Gray
Write-Host ""

Write-Host "Recommandations:" -ForegroundColor Yellow
if ($edgeStatus -match "active") {
    Write-Host "  [HIGH] GARDER: Ollama CLI sur edgeserver (PRIMARY)" -ForegroundColor Green
}
if ($ollamaProcess) {
    Write-Host "  [HIGH] GARDER: Ollama Desktop sur corertx (SECONDARY/failover)" -ForegroundColor Green
}
if ($wslOllamaCheck) {
    if ($wslService -match "active|running") {
        Write-Host "  [CRITICAL] DESACTIVER: Ollama dans WSL (CONFLIT port 11434)" -ForegroundColor Red
    } else {
        Write-Host "  [MEDIUM] DESINSTALLER: Ollama dans WSL (redondance inutile)" -ForegroundColor Yellow
    }
}
if ($llmImports -match "agents\.base\.llm_client") {
    Write-Host "  [HIGH] MIGRER: Imports agents.base.llm_client vers agents.llm.ollama_client" -ForegroundColor Yellow
}

Write-Host ""
Stop-Transcript

Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "                  AUDIT TERMINE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Fichier sauvegarde: $outputFile" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaine etape:" -ForegroundColor Cyan
Write-Host "  1. Review: notepad $outputFile" -ForegroundColor Gray
Write-Host "  2. Cleanup: .\infrastructure\scripts\cleanup_ollama.ps1 -DryRun" -ForegroundColor Gray
Write-Host ""
