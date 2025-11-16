# Generate Production Secrets for TwisterLab
param([switch]$Force, [switch]$Rotate)

$ErrorActionPreference = "Stop"
$SECRETS_DIR = "secrets"
$BACKUP_DIR = "secrets/backup"

Write-Host "TwisterLab Secrets Generator" -ForegroundColor Cyan

# Check existing
if ((Test-Path "$SECRETS_DIR/*.txt") -and -not $Force -and -not $Rotate) {
    Write-Host "Secrets already exist! Use -Force or -Rotate" -ForegroundColor Yellow
    exit 1
}

# Create directories
New-Item -ItemType Directory -Path $SECRETS_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
Write-Host "Directories created" -ForegroundColor Green

# Backup if rotating
if ($Rotate -and (Test-Path "$SECRETS_DIR/*.txt")) {
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    Get-ChildItem "$SECRETS_DIR/*.txt" | ForEach-Object {
        Copy-Item $_.FullName "$BACKUP_DIR/$($_.BaseName)_$ts.txt"
    }
    Write-Host "Secrets backed up" -ForegroundColor Green
}

# Generate function
function New-SecurePassword {
    param([int]$Length = 32)
    $chars = (65..90) + (97..122) + (48..57) + (33, 35, 36, 37, 38, 42, 43, 45, 61, 63, 64)
    -join ($chars | Get-Random -Count $Length | ForEach-Object {[char]$_})
}

Write-Host "Generating secrets..." -ForegroundColor Yellow

# Generate all secrets
$secrets = @{
    "postgres_password.txt" = 32
    "redis_password.txt" = 32
    "admin_password.txt" = 24
    "jwt_secret.txt" = 64
    "webui_secret_key.txt" = 48
    "grafana_admin_password.txt" = 24
}

foreach ($secret in $secrets.GetEnumerator()) {
    $file = "$SECRETS_DIR/$($secret.Key)"
    if (-not (Test-Path $file) -or $Force -or $Rotate) {
        $password = New-SecurePassword -Length $secret.Value
        $password | Out-File -NoNewline -FilePath $file -Encoding ASCII
        Write-Host "  Created: $($secret.Key)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "All secrets generated!" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "Secrets Summary:" -ForegroundColor Cyan
Get-ChildItem "$SECRETS_DIR/*.txt" | ForEach-Object {
    $size = (Get-Content $_.FullName -Raw).Length
    Write-Host "  $($_.Name): $size bytes"
}

Write-Host ""
Write-Host "SECURITY NOTES:" -ForegroundColor Yellow
Write-Host "1. Never commit secrets/ to Git"
Write-Host "2. Backup secrets securely"
Write-Host "3. Rotate periodically (use -Rotate)"
Write-Host "4. Check .gitignore includes secrets/"
Write-Host ""

# Verify .gitignore
if (Test-Path ".gitignore") {
    $content = Get-Content ".gitignore" -Raw
    if ($content -match "secrets/") {
        Write-Host "OK: secrets/ in .gitignore" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Add secrets/ to .gitignore!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Next: Update .env.prod to use _FILE variables" -ForegroundColor Cyan
