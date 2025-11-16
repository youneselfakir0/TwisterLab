# Script de correction automatique des problèmes de sécurité critiques
# TwisterLab - 15 novembre 2025

param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$server = "twister@192.168.0.30"

Write-Host "🔒 TwisterLab Security Fix Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
}

# Fonction pour exécuter des commandes SSH
function Invoke-SSHCommand {
    param([string]$command, [string]$description)

    Write-Host "`n📡 $description" -ForegroundColor Blue
    Write-Host "Command: $command" -ForegroundColor Gray

    if (-not $DryRun) {
        try {
            $result = ssh $server $command
            Write-Host "✅ Success" -ForegroundColor Green
            return $result
        }
        catch {
            Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
            return $null
        }
    } else {
        Write-Host "🔍 Would execute: ssh $server $command" -ForegroundColor Yellow
    }
}

# 1. Générer et définir les secrets manquants
Write-Host "`n1️⃣ GÉNÉRATION DES SECRETS MANQUANTS" -ForegroundColor Magenta

$secrets = @(
    @{Name="jwt_secret_key"; Length=64; Description="JWT Secret Key"},
    @{Name="api_secret_key"; Length=32; Description="API Secret Key"},
    @{Name="webui_secret_key"; Length=32; Description="WebUI Secret Key"}
)

foreach ($secret in $secrets) {
    $secretName = $secret.Name
    $secretValue = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count $secret.Length | ForEach-Object {[char]$_})

    Write-Host "🔑 Generating $($secret.Description)..." -ForegroundColor Blue

    if (-not $DryRun) {
        # Supprimer l'ancien secret s'il existe
        try {
            ssh $server "docker secret rm $secretName" 2>$null
        } catch {
            # Secret n'existe pas, continuer
        }

        # Créer le nouveau secret
        $tempFile = [System.IO.Path]::GetTempFileName()
        $secretValue | Out-File -FilePath $tempFile -Encoding ASCII -NoNewline
        scp $tempFile "${server}:/tmp/${secretName}_secret.txt"
        Remove-Item $tempFile

        ssh $server "docker secret create $secretName /tmp/${secretName}_secret.txt"
        ssh $server "rm /tmp/${secretName}_secret.txt"
        Write-Host "✅ Secret $secretName created" -ForegroundColor Green
    }
        Write-Host "✅ Secret $secretName created" -ForegroundColor Green
    }
}

# 2. Corriger les mots de passe par défaut
Write-Host "`n2️⃣ CORRECTION DES MOTS DE PASSE PAR DÉFAUT" -ForegroundColor Magenta

$defaultPasswords = @(
    @{Service="api"; Variable="ADMIN_PASSWORD"; Current="changeme_admin_2024!"; Description="API Admin Password"},
    @{Service="postgres"; Variable="POSTGRES_PASSWORD"; Current=""; Description="PostgreSQL Password"}
)

foreach ($password in $defaultPasswords) {
    $newPassword = -join ((48..57) + (65..90) + (97..122) + (33..47) | Get-Random -Count 32 | ForEach-Object {[char]$_})

    Write-Host "🔒 Updating $($password.Description)..." -ForegroundColor Blue

    if (-not $DryRun) {
        # Créer un secret pour le mot de passe
        $secretName = "$($password.Service)_password"
        try {
            ssh $server "docker secret rm $secretName" 2>$null
        } catch {
            # Secret n'existe pas, continuer
        }

        $tempFile = [System.IO.Path]::GetTempFileName()
        $newPassword | Out-File -FilePath $tempFile -Encoding ASCII -NoNewline
        scp $tempFile "${server}:/tmp/${secretName}_secret.txt"
        Remove-Item $tempFile

        ssh $server "docker secret create $secretName /tmp/${secretName}_secret.txt"
        ssh $server "rm /tmp/${secretName}_secret.txt"
        Write-Host "✅ Password secret $secretName created" -ForegroundColor Green
    }
}

# 3. Activer l'authentification WebUI
Write-Host "`n3️⃣ ACTIVATION AUTHENTIFICATION WEBUI" -ForegroundColor Magenta

if (-not $DryRun) {
    Invoke-SSHCommand "docker service update --env-add WEBUI_AUTH=True twisterlab_webui" "Enable WebUI authentication"
}

# 4. Redémarrer le service node-exporter défaillant
Write-Host "`n4️⃣ REDÉMARRAGE NODE-EXPORTER" -ForegroundColor Magenta

if (-not $DryRun) {
    Invoke-SSHCommand "docker service update --force monitoring_node-exporter" "Restart node-exporter service"
}

# 5. Générer un rapport de vérification
Write-Host "`n5️⃣ RAPPORT DE VÉRIFICATION" -ForegroundColor Magenta

if (-not $DryRun) {
    Write-Host "🔍 Vérification des services..." -ForegroundColor Blue

    # Vérifier que tous les services sont en cours d'exécution
    $services = ssh $server "docker service ls --format 'table {{.Name}}\t{{.Replicas}}'"
    Write-Host "Services status:" -ForegroundColor Cyan
    Write-Host $services

    # Vérifier les secrets
    $secrets = ssh $server "docker secret ls"
    Write-Host "`nSecrets configured:" -ForegroundColor Cyan
    Write-Host $secrets
}

Write-Host "`n🎉 CORRECTIONS TERMINÉES" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Prochaines étapes manuelles requises:" -ForegroundColor Yellow
Write-Host "1. Configurer SSL/TLS sur Traefik" -ForegroundColor Yellow
Write-Host "2. Redéployer les services avec les nouveaux secrets" -ForegroundColor Yellow
Write-Host "3. Tester l'authentification sur tous les services" -ForegroundColor Yellow
Write-Host "4. Configurer SSO/LDAP si nécessaire" -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "`n🔍 Dry run completed. Run without -DryRun to apply changes." -ForegroundColor Cyan
}</content>
<parameter name="filePath">c:\TwisterLab\fix-security-issues.ps1
