# run_all_tests.ps1 - Script d'automatisation TwisterLab
# Execute tous les tests et affiche un resume colore

param(
    [switch]$SkipInstall,
    [switch]$Verbose,
    [string]$PythonPath = "python"
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Couleurs pour la sortie
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput $Message "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput $Message "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput $Message "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput $Message "Cyan" }

# Variables de suivi
$TestsPassed = 0
$TestsFailed = 0
$TestsTotal = 25  # 19 unitaires + 6 integration
$StartTime = Get-Date

# Fonction pour executer une commande et capturer le resultat
function Invoke-TestCommand {
    param(
        [string]$Command,
        [string]$Description,
        [ref]$PassedCount,
        [ref]$FailedCount
    )

    Write-Info "==> $Description..."
    try {
        $result = Invoke-Expression $Command 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Success "[OK] $Description - REUSSI"
            $PassedCount.Value++
            return $true
        } else {
            Write-Error "[ECHEC] $Description - ECHEC (Code: $exitCode)"
            if ($Verbose) {
                Write-ColorOutput $result "Gray"
            }
            $FailedCount.Value++
            return $false
        }
    }
    catch {
        Write-Error "[ERREUR] $Description - ERREUR: $($_.Exception.Message)"
        $FailedCount.Value++
        return $false
    }
}

# Banniere
Write-ColorOutput "========================================================" "Magenta"
Write-ColorOutput "               TWISTERLAB TESTS" "Magenta"
Write-ColorOutput "         Script d'Automatisation Complet" "Magenta"
Write-ColorOutput "========================================================" "Magenta"

Write-Info "Demarrage a $(Get-Date -Format 'HH:mm:ss')"
Write-Info "Repertoire: $ScriptDir"
Write-Info ""

# 1. Verifier Python
Write-Info "1. VERIFICATION PYTHON"
$pythonVersion = & $PythonPath --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "[OK] Python trouve: $pythonVersion"
} else {
    Write-Error "[ERREUR] Python non trouve ou erreur"
    exit 1
}

# 2. Installer les dependances (optionnel)
if (-not $SkipInstall) {
    Write-Info ""
    Write-Info "2. INSTALLATION DEPENDANCES"

    if (Test-Path "requirements.txt") {
        Write-Info "Installation des dependances..."
        $installResult = Invoke-TestCommand "& $PythonPath -m pip install -r requirements.txt" "Installation requirements.txt" ([ref]$TestsPassed) ([ref]$TestsFailed)
    } else {
        Write-Warning "[ATTENTION] requirements.txt non trouve, installation ignoree"
    }
}

# 3. Verifier les imports critiques
Write-Info ""
Write-Info "3. VERIFICATION IMPORTS"
$imports = @("fastapi", "uvicorn", "sqlalchemy", "alembic", "pytest", "asyncpg")
$importSuccess = $true

# 3. Verifier les imports critiques
Write-Info ""
Write-Info "3. VERIFICATION IMPORTS"
$imports = @("fastapi", "uvicorn", "sqlalchemy", "alembic", "pytest", "asyncpg")
$importSuccess = $true

foreach ($module in $imports) {
    try {
        # Utiliser Start-Process pour eviter les problemes d'echappement
        $process = Start-Process python -ArgumentList "-c", "import $module; print('OK - $module')" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "temp_output.txt" -RedirectStandardError "temp_error.txt"
        $output = Get-Content "temp_output.txt" -ErrorAction SilentlyContinue
        $error = Get-Content "temp_error.txt" -ErrorAction SilentlyContinue

        if ($process.ExitCode -eq 0 -and $output) {
            Write-Success $output
        } else {
            Write-Error "[ECHEC] Import $module echoue"
            if ($error) { Write-Error "Details: $error" }
            $importSuccess = $false
        }

        # Nettoyer les fichiers temporaires
        Remove-Item "temp_output.txt" -ErrorAction SilentlyContinue
        Remove-Item "temp_error.txt" -ErrorAction SilentlyContinue
    }
    catch {
        Write-Error "[ERREUR] Erreur lors de l'import de $module"
        $importSuccess = $false
    }
}

if (-not $importSuccess) {
    Write-Error "[ERREUR] Problemes d'import detectes. Arret du script."
    exit 1
}

# 4. Creer la structure de repertoires de tests si necessaire
Write-Info ""
Write-Info "4. PREPARATION STRUCTURE TESTS"
if (-not (Test-Path "tests")) {
    New-Item -ItemType Directory -Path "tests" -Force | Out-Null
    Write-Success "[OK] Dossier tests/ cree"
}

if (-not (Test-Path "tests/unit")) {
    New-Item -ItemType Directory -Path "tests/unit" -Force | Out-Null
    Write-Success "[OK] Dossier tests/unit/ cree"
}

if (-not (Test-Path "tests/integration")) {
    New-Item -ItemType Directory -Path "tests/integration" -Force | Out-Null
    Write-Success "[OK] Dossier tests/integration/ cree"
}

# 5. Executer les tests unitaires
Write-Info ""
Write-Info "5. TESTS UNITAIRES (19 tests attendus)"
$unitTestPath = "tests/unit"
if (Test-Path $unitTestPath) {
    $unitCommand = "& $PythonPath -m pytest $unitTestPath -v --tb=short --disable-warnings"
    Invoke-TestCommand $unitCommand "Tests unitaires" ([ref]$TestsPassed) ([ref]$TestsFailed)
} else {
    Write-Warning "[ATTENTION] Dossier tests/unit non trouve"
    $TestsFailed++
}

# 6. Executer les tests d'integration
Write-Info ""
Write-Info "6. TESTS D'INTEGRATION (6 tests attendus)"
$integrationTestPath = "test_maestro_integration.py"
if (Test-Path $integrationTestPath) {
    $integrationCommand = "& $PythonPath -m pytest $integrationTestPath -v --tb=short --disable-warnings"
    Invoke-TestCommand $integrationCommand "Tests d'integration" ([ref]$TestsPassed) ([ref]$TestsFailed)
} else {
    Write-Warning "[ATTENTION] Fichier test_maestro_integration.py non trouve"
    $TestsFailed++
}

# 7. Calculer le coverage (optionnel)
Write-Info ""
Write-Info "7. CALCUL COVERAGE"
$coverageCommand = "& $PythonPath -m pytest --cov=agents --cov-report=term-missing --cov-fail-under=80 --disable-warnings"
$coverageResult = Invoke-TestCommand $coverageCommand "Coverage analysis" ([ref]$TestsPassed) ([ref]$TestsFailed)

# 8. Resume final
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Info ""
Write-ColorOutput "========================================================" "Magenta"
Write-ColorOutput "                   RESULTATS" "Magenta"
Write-ColorOutput "========================================================" "Magenta"

Write-Info "Duree totale: $($Duration.TotalSeconds.ToString('F1')) secondes"
Write-Info "Tests executes: $($TestsPassed + $TestsFailed)/$TestsTotal"

if ($TestsPassed -gt 0) {
    Write-Success "Tests reussis: $TestsPassed"
}

if ($TestsFailed -gt 0) {
    Write-Error "Tests echoues: $TestsFailed"
}

$successRate = [math]::Round(($TestsPassed / $TestsTotal) * 100, 1)
Write-Info "Taux de succes: $successRate%"

# Evaluation finale
Write-Info ""
if ($TestsFailed -eq 0 -and $successRate -ge 80) {
    Write-ColorOutput "========================================================" "Green"
    Write-ColorOutput "           TOUS LES TESTS SONT REUSSIS !" "Green"
    Write-ColorOutput "      TwisterLab est pret pour la production !" "Green"
    Write-ColorOutput "========================================================" "Green"

    Write-Success "Pret pour les prochaines etapes:"
    Write-Success "  - Demarrer l'API: uvicorn agents.api.main:app --reload"
    Write-Success "  - Consulter la doc: http://localhost:8000/docs"
    Write-Success "  - Prochaines etapes: .github/copilot-prompt-next-steps.md"

} elseif ($TestsFailed -gt 0) {
    Write-ColorOutput "========================================================" "Yellow"
    Write-ColorOutput "              PROBLEMES DETECTES" "Yellow"
    Write-ColorOutput "    Certains tests ont echoue - voir les details ci-dessus" "Yellow"
    Write-ColorOutput "========================================================" "Yellow"

    Write-Warning "Actions recommandees:"
    Write-Warning "  - Verifier les logs d'erreur ci-dessus"
    Write-Warning "  - Corriger les imports manquants"
    Write-Warning "  - Verifier la configuration PostgreSQL"
    Write-Warning "  - Consulter: .github/copilot-prompt-next-steps.md"

} else {
    Write-ColorOutput "========================================================" "Yellow"
    Write-ColorOutput "             AUCUN TEST TROUVE" "Yellow"
    Write-ColorOutput "    Verifier la structure des fichiers de test" "Yellow"
    Write-ColorOutput "========================================================" "Yellow"

    Write-Warning "Verifications:"
    Write-Warning "  - Fichier test_maestro.py existe ?"
    Write-Warning "  - Fichier test_maestro_integration.py existe ?"
    Write-Warning "  - pytest est installe ?"
}

Write-Info ""
Write-Info "Logs detailles disponibles dans le terminal ci-dessus"
Write-Info "Documentation: START_HERE.md"
Write-Info "Prochaines etapes: .github/copilot-prompt-next-steps.md"

# Code de sortie base sur les resultats
if ($TestsFailed -eq 0 -and $successRate -ge 80) {
    exit 0  # Succes
} else {
    exit 1  # Echec
}
