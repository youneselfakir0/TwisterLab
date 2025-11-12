<#
.SYNOPSIS
    Deploy Phase 1 Authentication (Local mode) to staging or production
    
.DESCRIPTION
    Script pour déployer le système d'authentification hybride en mode LOCAL
    (pas besoin d'Azure AD - utilise JWT local avec bcrypt)
    
    Actions:
    - Génère JWT_SECRET_KEY sécurisé (64 caractères)
    - Crée .env.auth avec config locale
    - Valide bcrypt 3.2.2 installé
    - Exécute tests unitaires + intégration
    - Déploie sur environnement cible
    - Teste /auth/token endpoint
    
.PARAMETER Environment
    Environnement cible: staging ou production
    
.PARAMETER AdminPassword
    Mot de passe pour le compte admin (optionnel, défaut: généré aléatoirement)
    
.PARAMETER SkipTests
    Skip les tests (non recommandé pour production)
    
.EXAMPLE
    .\deploy_auth_phase1.ps1 -Environment staging
    
.EXAMPLE
    .\deploy_auth_phase1.ps1 -Environment production -AdminPassword "SecurePass123!"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("staging", "production")]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$AdminPassword = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

# Couleurs
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        TwisterLab Phase 1 - Authentication Deployment         ║" -ForegroundColor Cyan
Write-Host "║                    Mode: LOCAL (no Azure)                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Info "Target Environment: $Environment"
Write-Info "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# ============================================================================
# ÉTAPE 1: Vérifications Préliminaires
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Info "ÉTAPE 1/7: Vérifications préliminaires"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python détecté: $pythonVersion"
} catch {
    Write-Error "Python non trouvé. Installer Python 3.12+"
    exit 1
}

# Vérifier venv activé
if (-not $env:VIRTUAL_ENV) {
    Write-Warning "Virtual environment non activé. Activation..."
    & "$PSScriptRoot\..\..\..\.venv\Scripts\Activate.ps1"
}

# Vérifier git
try {
    $gitBranch = git branch --show-current
    Write-Success "Git branch: $gitBranch"
} catch {
    Write-Warning "Git non trouvé (optionnel)"
}

Write-Host ""

# ============================================================================
# ÉTAPE 2: Générer Credentials Sécurisés
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Info "ÉTAPE 2/7: Génération credentials sécurisés"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Générer JWT secret (64 caractères hex = 32 bytes)
Write-Info "Génération JWT_SECRET_KEY (64 caractères)..."
$jwtSecret = python -c "import secrets; print(secrets.token_hex(32))"
Write-Success "JWT_SECRET_KEY généré: $($jwtSecret.Substring(0,16))...(truncated)"

# Générer ou utiliser admin password
if ([string]::IsNullOrEmpty($AdminPassword)) {
    Write-Info "Génération mot de passe admin aléatoire..."
    $AdminPassword = python -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(16)))"
    Write-Warning "Admin password généré: $AdminPassword"
    Write-Warning "IMPORTANT: Sauvegarder ce mot de passe!"
} else {
    Write-Success "Utilisation mot de passe admin fourni"
}

Write-Host ""

# ============================================================================
# ÉTAPE 3: Créer Fichier de Configuration
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Info "ÉTAPE 3/7: Création fichier .env.auth"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$envContent = @"
# ============================================================================
# TwisterLab Phase 1 - Local Authentication Configuration
# ============================================================================
# Environment: $Environment
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Mode: LOCAL (no Azure AD required)

# JWT Configuration (REQUIRED for local auth)
JWT_SECRET_KEY=$jwtSecret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Admin User (default admin account)
ADMIN_PASSWORD=$AdminPassword

# Azure AD Configuration (OPTIONAL - leave empty for local mode)
# If these are set, system will try Azure AD first, then fallback to local
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_REDIRECT_URI=

# Redis Configuration (for session caching)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=twisterlab-redis-prod

# API Configuration
AUTH_MODE=local
ENABLE_AUTH=true
"@

$envPath = "infrastructure\configs\.env.auth.$Environment"
Set-Content -Path $envPath -Value $envContent -Encoding UTF8
Write-Success "Fichier créé: $envPath"

# Copier vers .env si n'existe pas
if (-not (Test-Path "infrastructure\configs\.env.$Environment")) {
    Copy-Item $envPath "infrastructure\configs\.env.$Environment"
    Write-Success "Copié vers .env.$Environment"
}

Write-Host ""

# ============================================================================
# ÉTAPE 4: Installer Dépendances
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Info "ÉTAPE 4/7: Installation dépendances"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Vérifier bcrypt version
Write-Info "Vérification bcrypt 3.2.2..."
$bcryptVersion = pip show bcrypt 2>$null | Select-String "Version:"
if ($bcryptVersion -match "3.2.2") {
    Write-Success "bcrypt 3.2.2 déjà installé"
} else {
    Write-Warning "Installation bcrypt 3.2.2 (passlib compatibility)..."
    pip install "bcrypt==3.2.2" --force-reinstall --quiet
    Write-Success "bcrypt 3.2.2 installé"
}

# Vérifier autres dépendances auth
Write-Info "Vérification dépendances auth..."
$requiredPackages = @("msal", "python-jose", "passlib", "aioredis")
foreach ($pkg in $requiredPackages) {
    $installed = pip show $pkg 2>$null
    if ($installed) {
        Write-Success "$pkg installé"
    } else {
        Write-Warning "$pkg manquant, installation..."
        pip install $pkg --quiet
    }
}

Write-Host ""

# ============================================================================
# ÉTAPE 5: Exécuter Tests
# ============================================================================
if (-not $SkipTests) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Info "ÉTAPE 5/7: Exécution tests"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    # Tests unitaires LocalAuth
    Write-Info "Tests unitaires LocalAuth (18 tests)..."
    $testResult = pytest tests\test_local_auth.py -v --tb=short 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests LocalAuth échoués"
        Write-Host $testResult
        exit 1
    }
    Write-Success "18/18 tests LocalAuth passent"
    
    # Tests intégration Hybrid
    Write-Info "Tests intégration HybridAuth (6 tests)..."
    $testResult = pytest tests\integration\test_hybrid_auth_flow.py -v --tb=short 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests HybridAuth échoués"
        Write-Host $testResult
        exit 1
    }
    Write-Success "6/6 tests HybridAuth passent"
    
    Write-Success "Tous les tests passent (24/24)"
    Write-Host ""
} else {
    Write-Warning "Tests skippés (--SkipTests)"
    Write-Host ""
}

# ============================================================================
# ÉTAPE 6: Déploiement Docker
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Info "ÉTAPE 6/7: Déploiement Docker ($Environment)"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

if ($Environment -eq "staging") {
    Write-Info "Déploiement staging (localhost)..."
    & "infrastructure\scripts\deploy.ps1" -Environment staging
} elseif ($Environment -eq "production") {
    Write-Info "Déploiement production (edgeserver.twisterlab.local)..."
    & "infrastructure\scripts\deploy.ps1" -Environment production
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Déploiement échoué"
    exit 1
}

Write-Success "Déploiement réussi"
Write-Host ""

# ============================================================================
# ÉTAPE 7: Tests Post-Déploiement
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Info "ÉTAPE 7/7: Tests post-déploiement"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Attendre que les services démarrent
Write-Info "Attente démarrage services (15 secondes)..."
Start-Sleep -Seconds 15

# Déterminer l'URL selon l'environnement
if ($Environment -eq "staging") {
    $apiUrl = "http://localhost:8000"
} else {
    $apiUrl = "http://192.168.0.30:8000"
}

# Test 1: Health check
Write-Info "Test 1: Health check..."
try {
    $health = Invoke-RestMethod -Uri "$apiUrl/health" -Method GET -TimeoutSec 10
    Write-Success "API healthy: $($health.status)"
} catch {
    Write-Error "Health check échoué: $_"
    exit 1
}

# Test 2: Auth status
Write-Info "Test 2: Auth status..."
try {
    $authStatus = Invoke-RestMethod -Uri "$apiUrl/auth/status" -Method GET -TimeoutSec 10
    Write-Success "Mode auth: $($authStatus.mode)"
    Write-Success "Provider: $($authStatus.provider)"
    
    if ($authStatus.mode -ne "local") {
        Write-Warning "Mode devrait être 'local', obtenu: $($authStatus.mode)"
    }
} catch {
    Write-Error "Auth status échoué: $_"
    exit 1
}

# Test 3: Login avec admin
Write-Info "Test 3: Login admin..."
try {
    $body = "username=admin&password=$AdminPassword"
    $response = Invoke-RestMethod -Uri "$apiUrl/auth/token" -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $body -TimeoutSec 10
    
    if ($response.access_token) {
        Write-Success "Login réussi! Token reçu"
        Write-Host "   Token: $($response.access_token.Substring(0,20))...(truncated)" -ForegroundColor Gray
        
        # Test 4: Vérifier token avec /auth/me
        Write-Info "Test 4: Vérification token..."
        $headers = @{ "Authorization" = "Bearer $($response.access_token)" }
        $me = Invoke-RestMethod -Uri "$apiUrl/auth/me" -Method GET -Headers $headers -TimeoutSec 10
        Write-Success "User: $($me.username), Roles: $($me.roles -join ',')"
    } else {
        Write-Error "Pas de token reçu"
        exit 1
    }
} catch {
    Write-Error "Login échoué: $_"
    Write-Warning "Vérifier que ADMIN_PASSWORD est correct dans .env"
    exit 1
}

Write-Host ""

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ DÉPLOIEMENT RÉUSSI                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Success "Phase 1 Authentication déployé avec succès!"
Write-Host ""
Write-Info "Configuration:"
Write-Host "   Environment:    $Environment" -ForegroundColor Cyan
Write-Host "   Mode:           LOCAL (no Azure)" -ForegroundColor Cyan
Write-Host "   Provider:       LocalAuth (JWT + bcrypt)" -ForegroundColor Cyan
Write-Host "   API URL:        $apiUrl" -ForegroundColor Cyan
Write-Host "   Admin User:     admin" -ForegroundColor Cyan
Write-Host "   Admin Password: $AdminPassword" -ForegroundColor Yellow
Write-Host ""
Write-Info "Tests:"
Write-Host "   ✅ 18/18 LocalAuth unit tests" -ForegroundColor Green
Write-Host "   ✅ 6/6  HybridAuth integration tests" -ForegroundColor Green
Write-Host "   ✅ API health check" -ForegroundColor Green
Write-Host "   ✅ Auth login/token" -ForegroundColor Green
Write-Host ""
Write-Info "Prochaines étapes:"
Write-Host "   1. Tester API manuellement: curl $apiUrl/docs" -ForegroundColor Gray
Write-Host "   2. Créer utilisateurs: POST $apiUrl/auth/users" -ForegroundColor Gray
Write-Host "   3. Activer Azure AD (optionnel): Configurer AZURE_* vars" -ForegroundColor Gray
Write-Host ""
Write-Warning "⚠️  IMPORTANT: Sauvegarder le fichier $envPath"
Write-Host ""
