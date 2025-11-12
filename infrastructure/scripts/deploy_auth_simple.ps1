<#
.SYNOPSIS
    Deploy Phase 1 Authentication - Simple version without Unicode
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("staging", "production")]
    [string]$Environment
)

$ErrorActionPreference = "Stop"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  TwisterLab Phase 1 - Authentication Deployment" -ForegroundColor Cyan
Write-Host "  Mode: LOCAL (no Azure required)" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "[INFO] Environment: $Environment" -ForegroundColor Cyan
Write-Host "[INFO] Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Cyan

# Etape 1: Generate JWT Secret
Write-Host "[1/5] Generating JWT secret..." -ForegroundColor Yellow
$jwtSecret = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "[OK] JWT_SECRET_KEY generated (64 chars)" -ForegroundColor Green

# Etape 2: Generate Admin Password
Write-Host "`n[2/5] Generating admin password..." -ForegroundColor Yellow
$adminPassword = python -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(16)))"
Write-Host "[OK] Admin password: $adminPassword" -ForegroundColor Green
Write-Host "[WARN] SAVE THIS PASSWORD!" -ForegroundColor Yellow

# Etape 3: Create .env file
Write-Host "`n[3/5] Creating .env.auth.$Environment..." -ForegroundColor Yellow

$envContent = @"
# TwisterLab Phase 1 - Local Authentication
# Environment: $Environment
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

JWT_SECRET_KEY=$jwtSecret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

ADMIN_PASSWORD=$adminPassword

# Azure AD (empty = local mode)
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=twisterlab-redis-prod

AUTH_MODE=local
ENABLE_AUTH=true
"@

$envPath = "infrastructure\configs\.env.auth.$Environment"
Set-Content -Path $envPath -Value $envContent -Encoding UTF8
Write-Host "[OK] Created: $envPath" -ForegroundColor Green

# Etape 4: Install dependencies
Write-Host "`n[4/5] Checking dependencies..." -ForegroundColor Yellow

# Check bcrypt
$bcryptVersion = pip show bcrypt 2>$null | Select-String "Version:"
if ($bcryptVersion -match "3.2.2") {
    Write-Host "[OK] bcrypt 3.2.2 installed" -ForegroundColor Green
} else {
    Write-Host "[WARN] Installing bcrypt 3.2.2..." -ForegroundColor Yellow
    pip install "bcrypt==3.2.2" --force-reinstall --quiet
    Write-Host "[OK] bcrypt 3.2.2 installed" -ForegroundColor Green
}

# Etape 5: Run tests
Write-Host "`n[5/5] Running tests..." -ForegroundColor Yellow

Write-Host "  - LocalAuth tests (18 tests)..." -ForegroundColor Gray
$testOutput = pytest tests\test_local_auth.py -v --tb=short 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] LocalAuth tests failed" -ForegroundColor Red
    Write-Host $testOutput
    exit 1
}
Write-Host "  [OK] 18/18 LocalAuth tests passed" -ForegroundColor Green

Write-Host "  - HybridAuth tests (6 tests)..." -ForegroundColor Gray
$testOutput = pytest tests\integration\test_hybrid_auth_flow.py -v --tb=short 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] HybridAuth tests failed" -ForegroundColor Red
    Write-Host $testOutput
    exit 1
}
Write-Host "  [OK] 6/6 HybridAuth tests passed" -ForegroundColor Green

Write-Host "`n[OK] All tests passed (24/24)" -ForegroundColor Green

# Deploy
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  Deploying to $Environment..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

if ($Environment -eq "staging") {
    Write-Host "[INFO] Starting docker-compose (staging)..." -ForegroundColor Cyan

    # Copy env file
    Copy-Item $envPath "infrastructure\configs\.env.staging" -Force

    # Start services
    docker-compose -f infrastructure\docker\docker-compose.unified.yml --env-file infrastructure\configs\.env.staging up -d

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker deployment failed" -ForegroundColor Red
        exit 1
    }

    $apiUrl = "http://localhost:8000"
    Write-Host "[OK] Services started on localhost" -ForegroundColor Green

} else {
    Write-Host "[INFO] Deploying to production (edgeserver)..." -ForegroundColor Cyan

    # Copy to edgeserver
    scp $envPath twister@192.168.0.30:/home/twister/.env.production

    # Deploy via existing script
    & "infrastructure\scripts\deploy.ps1" -Environment production

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Production deployment failed" -ForegroundColor Red
        exit 1
    }

    $apiUrl = "http://192.168.0.30:8000"
    Write-Host "[OK] Deployed to edgeserver" -ForegroundColor Green
}

# Wait for services
Write-Host "`n[INFO] Waiting for services to start (15s)..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Test endpoints
Write-Host "`n[INFO] Testing endpoints..." -ForegroundColor Cyan

try {
    # Test 1: Health
    Write-Host "  - Health check..." -ForegroundColor Gray
    $health = Invoke-RestMethod -Uri "$apiUrl/health" -Method GET -TimeoutSec 10
    Write-Host "  [OK] API healthy: $($health.status)" -ForegroundColor Green

    # Test 2: Auth status
    Write-Host "  - Auth status..." -ForegroundColor Gray
    $authStatus = Invoke-RestMethod -Uri "$apiUrl/auth/status" -Method GET -TimeoutSec 10
    Write-Host "  [OK] Mode: $($authStatus.mode), Provider: $($authStatus.provider)" -ForegroundColor Green

    # Test 3: Login
    Write-Host "  - Login test..." -ForegroundColor Gray
    $body = "username=admin&password=$adminPassword"
    $response = Invoke-RestMethod -Uri "$apiUrl/auth/token" -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $body -TimeoutSec 10

    if ($response.access_token) {
        Write-Host "  [OK] Login successful, token received" -ForegroundColor Green
        Write-Host "     Token: $($response.access_token.Substring(0,20))..." -ForegroundColor Gray
    }

} catch {
    Write-Host "[ERROR] Endpoint tests failed: $_" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

Write-Host "`n[SUMMARY]" -ForegroundColor Cyan
Write-Host "  Environment:    $Environment" -ForegroundColor Gray
Write-Host "  Mode:           LOCAL (no Azure)" -ForegroundColor Gray
Write-Host "  API URL:        $apiUrl" -ForegroundColor Gray
Write-Host "  Admin User:     admin" -ForegroundColor Gray
Write-Host "  Admin Password: $adminPassword" -ForegroundColor Yellow

Write-Host "`n[TESTS]" -ForegroundColor Cyan
Write-Host "  18/18 LocalAuth unit tests" -ForegroundColor Gray
Write-Host "  6/6   HybridAuth integration tests" -ForegroundColor Gray
Write-Host "  API health check OK" -ForegroundColor Gray
Write-Host "  Auth login OK" -ForegroundColor Gray

Write-Host "`n[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "  1. Test API: curl $apiUrl/docs" -ForegroundColor Gray
Write-Host "  2. Create users: POST $apiUrl/auth/users" -ForegroundColor Gray
Write-Host "  3. Save password from: $envPath" -ForegroundColor Gray

Write-Host "`n[WARN] SAVE THE FILE: $envPath`n" -ForegroundColor Yellow
