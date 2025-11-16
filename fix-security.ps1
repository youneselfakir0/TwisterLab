# Script de correction sécurité TwisterLab
# Exécuter avec: .\fix-security.ps1

param([switch]$DryRun)

$server = "twister@192.168.0.30"

Write-Host "🔒 TwisterLab Security Audit & Fix" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE" -ForegroundColor Yellow
}

# Vérifier les services actuels
Write-Host "`n🔍 ANALYSE DES SERVICES ACTUELS" -ForegroundColor Blue
$services = ssh $server "docker service ls --format 'table {{.Name}}\t{{.Replicas}}'"
Write-Host $services

# Vérifier les secrets actuels
Write-Host "`n🔑 SECRETS ACTUELS" -ForegroundColor Blue
$secrets = ssh $server "docker secret ls"
Write-Host $secrets

# Générer nouveaux secrets
Write-Host "`n🔧 CRÉATION DE NOUVEAUX SECRETS" -ForegroundColor Magenta

$secretNames = @("jwt_secret_key", "api_secret_key", "webui_secret_key", "api_password", "postgres_password")

foreach ($secretName in $secretNames) {
    Write-Host "📝 Creating secret: $secretName" -ForegroundColor Yellow

    if (-not $DryRun) {
        # Générer une valeur aléatoire
        $secretValue = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

        # Créer le fichier temporaire
        $tempFile = [System.IO.Path]::GetTempFileName()
        $secretValue | Out-File -FilePath $tempFile -Encoding ASCII -NoNewline

        # Transférer et créer le secret
        scp $tempFile "${server}:/tmp/${secretName}.txt" 2>$null
        ssh $server "docker secret create $secretName /tmp/${secretName}.txt" 2>$null
        ssh $server "rm /tmp/${secretName}.txt" 2>$null

        Remove-Item $tempFile
        Write-Host "✅ Created: $secretName" -ForegroundColor Green
    } else {
        Write-Host "🔍 Would create: $secretName" -ForegroundColor Cyan
    }
}

# Corrections de configuration
Write-Host "`n⚙️ CORRECTIONS DE CONFIGURATION" -ForegroundColor Magenta

if (-not $DryRun) {
    Write-Host "🔐 Enabling WebUI auth..." -ForegroundColor Yellow
    ssh $server "docker service update --env-add WEBUI_AUTH=True twisterlab_webui" 2>$null

    Write-Host "🔄 Restarting node-exporter..." -ForegroundColor Yellow
    ssh $server "docker service update --force monitoring_node-exporter" 2>$null

    Write-Host "✅ Configuration updates applied" -ForegroundColor Green
} else {
    Write-Host "🔍 Would enable WebUI auth and restart node-exporter" -ForegroundColor Cyan
}

Write-Host "`n📋 PROCHAINES ÉTAPES MANUELLES:" -ForegroundColor Yellow
Write-Host "1. Modifier docker-compose.yml pour utiliser les secrets" -ForegroundColor White
Write-Host "2. Configurer SSL/TLS sur Traefik" -ForegroundColor White
Write-Host "3. Redéployer tous les services" -ForegroundColor White
Write-Host "4. Tester l'authentification sur tous les services" -ForegroundColor White
Write-Host "5. Configurer SSO/LDAP si nécessaire" -ForegroundColor White

Write-Host "`n🎯 RÉSULTAT: $(if ($DryRun) {'DRY RUN COMPLETED'} else {'CHANGES APPLIED'})" -ForegroundColor Green
