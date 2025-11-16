# Script de correction automatique des problèmes de sécurité critiques
# TwisterLab - 15 novembre 2025

param(
    [switch]$DryRun
)

$server = "twister@192.168.0.30"

Write-Host "🔒 TwisterLab Security Fix Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
}

# 1. Générer des secrets manquants
Write-Host "`n1️⃣ GÉNÉRATION DES SECRETS MANQUANTS" -ForegroundColor Magenta

$secrets = @("jwt_secret_key", "api_secret_key", "webui_secret_key")

foreach ($secretName in $secrets) {
    $secretValue = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    Write-Host "🔑 Generating $secretName..." -ForegroundColor Blue

    if (-not $DryRun) {
        $tempFile = [System.IO.Path]::GetTempFileName()
        $secretValue | Out-File -FilePath $tempFile -Encoding ASCII -NoNewline
        scp $tempFile "${server}:/tmp/${secretName}_secret.txt" 2>$null
        Remove-Item $tempFile

        ssh $server "docker secret create $secretName /tmp/${secretName}_secret.txt" 2>$null
        ssh $server "rm /tmp/${secretName}_secret.txt" 2>$null
        Write-Host "✅ Secret $secretName created" -ForegroundColor Green
    } else {
        Write-Host "🔍 Would create secret: $secretName" -ForegroundColor Yellow
    }
}

# 2. Générer des mots de passe sécurisés
Write-Host "`n2️⃣ GÉNÉRATION DES MOTS DE PASSE SÉCURISÉS" -ForegroundColor Magenta

$passwords = @("api_password", "postgres_password")

foreach ($passName in $passwords) {
    $newPassword = -join ((48..57) + (65..90) + (97..122) + (33..47) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    Write-Host "🔒 Generating $passName..." -ForegroundColor Blue

    if (-not $DryRun) {
        $tempFile = [System.IO.Path]::GetTempFileName()
        $newPassword | Out-File -FilePath $tempFile -Encoding ASCII -NoNewline
        scp $tempFile "${server}:/tmp/${passName}_secret.txt" 2>$null
        Remove-Item $tempFile

        ssh $server "docker secret create $passName /tmp/${passName}_secret.txt" 2>$null
        ssh $server "rm /tmp/${passName}_secret.txt" 2>$null
        Write-Host "✅ Password secret $passName created" -ForegroundColor Green
    } else {
        Write-Host "🔍 Would create password secret: $passName" -ForegroundColor Yellow
    }
}

# 3. Activer l'authentification WebUI
Write-Host "`n3️⃣ ACTIVATION AUTHENTIFICATION WEBUI" -ForegroundColor Magenta

if (-not $DryRun) {
    Write-Host "🔧 Enabling WebUI authentication..." -ForegroundColor Blue
    ssh $server "docker service update --env-add WEBUI_AUTH=True twisterlab_webui" 2>$null
    Write-Host "✅ WebUI authentication enabled" -ForegroundColor Green
} else {
    Write-Host "🔍 Would enable WebUI authentication" -ForegroundColor Yellow
}

# 4. Redémarrer node-exporter
Write-Host "`n4️⃣ REDÉMARRAGE NODE-EXPORTER" -ForegroundColor Magenta

if (-not $DryRun) {
    Write-Host "🔄 Restarting node-exporter..." -ForegroundColor Blue
    ssh $server "docker service update --force monitoring_node-exporter" 2>$null
    Write-Host "✅ Node-exporter restarted" -ForegroundColor Green
} else {
    Write-Host "🔍 Would restart node-exporter" -ForegroundColor Yellow
}

Write-Host "`n🎉 CORRECTIONS TERMINÉES" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Prochaines étapes manuelles:" -ForegroundColor Yellow
Write-Host "1. Configurer SSL/TLS sur Traefik" -ForegroundColor Yellow
Write-Host "2. Redéployer les services avec les nouveaux secrets" -ForegroundColor Yellow
Write-Host "3. Tester l'authentification" -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "`n🔍 Dry run completed. Run without -DryRun to apply changes." -ForegroundColor Cyan
}
