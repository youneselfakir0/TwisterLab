#Requires -Version 5.1

<#
.SYNOPSIS
    Créer les comptes nécessaires pour TwisterLab v1.0 (IT Helpdesk uniquement)

.DESCRIPTION
    Crée uniquement 4 identités minimales pour TwisterLab v1.0:
    - 1 agent AI (svc-helpdesk-agent) pour IT Helpdesk
    - 1 service principal (sp-orchestrator) pour orchestration
    - 1 service principal (sp-desktop-commander) pour Desktop Commander
    - 1 service principal (sp-mcp-servers) pour MCP Servers

    Principe: Least Privilege, $0 cost, pas de licences Office 365 sauf nécessaire

.PARAMETER AssignLicenses
    Assigner des licences Office 365 aux comptes utilisateurs (coût supplémentaire)

.PARAMETER SkipExisting
    Ignorer les comptes qui existent déjà

.EXAMPLE
    .\setup_twisterlab_accounts.ps1

.EXAMPLE
    .\setup_twisterlab_accounts.ps1 -AssignLicenses
#>

param(
    [Parameter(Mandatory=$false)]
    [switch]$AssignLicenses,

    [Parameter(Mandatory=$false)]
    [switch]$SkipExisting = $true
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$reportPath = ".\reports"
$accountsFile = Join-Path $reportPath "accounts_created.txt"

# Create reports directory
if (-not (Test-Path $reportPath)) {
    New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   TWISTERLAB v1.0 - SETUP COMPTES OPTIMAUX" -ForegroundColor Cyan
Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Initialize report
$report = @"
═══════════════════════════════════════════════════════════
TWISTERLAB v1.0 - COMPTES CRÉÉS
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
═══════════════════════════════════════════════════════════

"@

# ============================================================================
# CONNECT TO AZURE
# ============================================================================

Write-Host "[0/4] Connexion à Azure..." -ForegroundColor Yellow

try {
    $azContext = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $azContext) {
        Connect-AzAccount
        $azContext = Get-AzContext
    }

    Write-Host "   ✅ Connecté à: $($azContext.Subscription.Name)" -ForegroundColor Green
    $report += "`nAbonnement: $($azContext.Subscription.Name)`n"
    $report += "Tenant ID: $($azContext.Tenant.Id)`n`n"

    # Try to connect to Microsoft Graph
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
        Import-Module Microsoft.Graph.Users, Microsoft.Graph.Applications -ErrorAction SilentlyContinue
        Connect-MgGraph -Scopes "User.ReadWrite.All", "Application.ReadWrite.All", "Directory.ReadWrite.All" -ErrorAction SilentlyContinue
    }

} catch {
    Write-Host "   ❌ Erreur de connexion: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$statistics = @{
    Created = 0
    Skipped = 0
    Failed = 0
}

# ============================================================================
# ACCOUNT 1: IT HELPDESK AGENT (Azure AD User)
# ============================================================================

Write-Host "`n[1/4] Création du compte IT Helpdesk Agent..." -ForegroundColor Yellow

$helpdeskAccount = @{
    DisplayName = "TwisterLab IT Helpdesk Agent"
    UserPrincipalName = "svc-helpdesk-agent@$($azContext.Tenant.Id.Replace('-',''))).onmicrosoft.com"
    MailNickname = "svc-helpdesk-agent"
    AccountEnabled = $true
    PasswordProfile = @{
        Password = "TwisterLab2024!$((Get-Random -Minimum 1000 -Maximum 9999))!"
        ForceChangePasswordNextSignIn = $false
    }
}

try {
    # Check if exists
    $existingUser = $null
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
        $existingUser = Get-MgUser -Filter "userPrincipalName eq '$($helpdeskAccount.UserPrincipalName)'" -ErrorAction SilentlyContinue
    } else {
        $existingUserJson = az ad user show --id $helpdeskAccount.UserPrincipalName 2>$null
        if ($existingUserJson) {
            $existingUser = $existingUserJson | ConvertFrom-Json
        }
    }

    if ($existingUser -and $SkipExisting) {
        Write-Host "   ⏭️  Compte existe déjà: $($helpdeskAccount.UserPrincipalName)" -ForegroundColor Yellow
        $statistics.Skipped++
        $report += "[1] IT Helpdesk Agent: DÉJÀ EXISTANT`n"
        $report += "    UPN: $($helpdeskAccount.UserPrincipalName)`n`n"
    } else {
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
            $newUser = New-MgUser -DisplayName $helpdeskAccount.DisplayName `
                                  -UserPrincipalName $helpdeskAccount.UserPrincipalName `
                                  -MailNickname $helpdeskAccount.MailNickname `
                                  -AccountEnabled $helpdeskAccount.AccountEnabled `
                                  -PasswordProfile $helpdeskAccount.PasswordProfile `
                                  -ErrorAction Stop
        } else {
            az ad user create --display-name $helpdeskAccount.DisplayName `
                             --user-principal-name $helpdeskAccount.UserPrincipalName `
                             --mail-nickname $helpdeskAccount.MailNickname `
                             --password $helpdeskAccount.PasswordProfile.Password `
                             --force-change-password-next-sign-in false 2>$null
        }

        Write-Host "   ✅ Créé: $($helpdeskAccount.UserPrincipalName)" -ForegroundColor Green
        $statistics.Created++

        $report += "[1] IT Helpdesk Agent: CRÉÉ`n"
        $report += "    Type: Azure AD User`n"
        $report += "    UPN: $($helpdeskAccount.UserPrincipalName)`n"
        $report += "    Password: $($helpdeskAccount.PasswordProfile.Password)`n"
        $report += "    License: AUCUNE (ajouter manuellement si nécessaire)`n`n"
    }

} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    $statistics.Failed++
    $report += "[1] IT Helpdesk Agent: ÉCHEC - $($_.Exception.Message)`n`n"
}

# ============================================================================
# ACCOUNT 2: ORCHESTRATOR SERVICE PRINCIPAL
# ============================================================================

Write-Host "`n[2/4] Création du Service Principal Orchestrator..." -ForegroundColor Yellow

try {
    # Check if exists
    $existingApp = $null
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
        $existingApp = Get-MgApplication -Filter "displayName eq 'sp-orchestrator'" -ErrorAction SilentlyContinue
    } else {
        $existingAppJson = az ad app list --filter "displayName eq 'sp-orchestrator'" 2>$null | ConvertFrom-Json
        if ($existingAppJson) {
            $existingApp = $existingAppJson[0]
        }
    }

    if ($existingApp -and $SkipExisting) {
        Write-Host "   ⏭️  Application existe déjà: sp-orchestrator" -ForegroundColor Yellow
        $statistics.Skipped++
        $report += "[2] Orchestrator Service Principal: DÉJÀ EXISTANT`n"
        $report += "    App ID: $($existingApp.AppId)`n`n"
    } else {
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
            $newApp = New-MgApplication -DisplayName "sp-orchestrator" -ErrorAction Stop
            $sp = New-MgServicePrincipal -AppId $newApp.AppId -ErrorAction Stop

            # Create secret
            $passwordCred = Add-MgApplicationPassword -ApplicationId $newApp.Id
            $clientSecret = $passwordCred.SecretText
        } else {
            $newAppJson = az ad app create --display-name "sp-orchestrator" 2>$null | ConvertFrom-Json
            $sp = az ad sp create --id $newAppJson.appId 2>$null | ConvertFrom-Json
            $credJson = az ad app credential reset --id $newAppJson.appId 2>$null | ConvertFrom-Json
            $clientSecret = $credJson.password
        }

        Write-Host "   ✅ Créé: sp-orchestrator" -ForegroundColor Green
        $statistics.Created++

        $report += "[2] Orchestrator Service Principal: CRÉÉ`n"
        $report += "    Type: Service Principal`n"
        $report += "    App ID: $(if ($newApp) { $newApp.AppId } else { $newAppJson.appId })`n"
        $report += "    Client Secret: $clientSecret`n"
        $report += "    Permissions: Directory.Read.All (à assigner manuellement)`n`n"
    }

} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    $statistics.Failed++
    $report += "[2] Orchestrator Service Principal: ÉCHEC - $($_.Exception.Message)`n`n"
}

# ============================================================================
# ACCOUNT 3: DESKTOP COMMANDER SERVICE PRINCIPAL
# ============================================================================

Write-Host "`n[3/4] Création du Service Principal Desktop Commander..." -ForegroundColor Yellow

try {
    $existingApp = $null
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
        $existingApp = Get-MgApplication -Filter "displayName eq 'sp-desktop-commander'" -ErrorAction SilentlyContinue
    } else {
        $existingAppJson = az ad app list --filter "displayName eq 'sp-desktop-commander'" 2>$null | ConvertFrom-Json
        if ($existingAppJson) {
            $existingApp = $existingAppJson[0]
        }
    }

    if ($existingApp -and $SkipExisting) {
        Write-Host "   ⏭️  Application existe déjà: sp-desktop-commander" -ForegroundColor Yellow
        $statistics.Skipped++
        $report += "[3] Desktop Commander Service Principal: DÉJÀ EXISTANT`n"
        $report += "    App ID: $($existingApp.AppId)`n`n"
    } else {
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
            $newApp = New-MgApplication -DisplayName "sp-desktop-commander" -ErrorAction Stop
            $sp = New-MgServicePrincipal -AppId $newApp.AppId -ErrorAction Stop
            $passwordCred = Add-MgApplicationPassword -ApplicationId $newApp.Id
            $clientSecret = $passwordCred.SecretText
        } else {
            $newAppJson = az ad app create --display-name "sp-desktop-commander" 2>$null | ConvertFrom-Json
            $sp = az ad sp create --id $newAppJson.appId 2>$null | ConvertFrom-Json
            $credJson = az ad app credential reset --id $newAppJson.appId 2>$null | ConvertFrom-Json
            $clientSecret = $credJson.password
        }

        Write-Host "   ✅ Créé: sp-desktop-commander" -ForegroundColor Green
        $statistics.Created++

        $report += "[3] Desktop Commander Service Principal: CRÉÉ`n"
        $report += "    Type: Service Principal`n"
        $report += "    App ID: $(if ($newApp) { $newApp.AppId } else { $newAppJson.appId })`n"
        $report += "    Client Secret: $clientSecret`n"
        $report += "    Permissions: Device.Read.All (à assigner manuellement)`n`n"
    }

} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    $statistics.Failed++
    $report += "[3] Desktop Commander Service Principal: ÉCHEC - $($_.Exception.Message)`n`n"
}

# ============================================================================
# ACCOUNT 4: MCP SERVERS SERVICE PRINCIPAL
# ============================================================================

Write-Host "`n[4/4] Création du Service Principal MCP Servers..." -ForegroundColor Yellow

try {
    $existingApp = $null
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
        $existingApp = Get-MgApplication -Filter "displayName eq 'sp-mcp-servers'" -ErrorAction SilentlyContinue
    } else {
        $existingAppJson = az ad app list --filter "displayName eq 'sp-mcp-servers'" 2>$null | ConvertFrom-Json
        if ($existingAppJson) {
            $existingApp = $existingAppJson[0]
        }
    }

    if ($existingApp -and $SkipExisting) {
        Write-Host "   ⏭️  Application existe déjà: sp-mcp-servers" -ForegroundColor Yellow
        $statistics.Skipped++
        $report += "[4] MCP Servers Service Principal: DÉJÀ EXISTANT`n"
        $report += "    App ID: $($existingApp.AppId)`n`n"
    } else {
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
            $newApp = New-MgApplication -DisplayName "sp-mcp-servers" -ErrorAction Stop
            $sp = New-MgServicePrincipal -AppId $newApp.AppId -ErrorAction Stop
            $passwordCred = Add-MgApplicationPassword -ApplicationId $newApp.Id
            $clientSecret = $passwordCred.SecretText
        } else {
            $newAppJson = az ad app create --display-name "sp-mcp-servers" 2>$null | ConvertFrom-Json
            $sp = az ad sp create --id $newAppJson.appId 2>$null | ConvertFrom-Json
            $credJson = az ad app credential reset --id $newAppJson.appId 2>$null | ConvertFrom-Json
            $clientSecret = $credJson.password
        }

        Write-Host "   ✅ Créé: sp-mcp-servers" -ForegroundColor Green
        $statistics.Created++

        $report += "[4] MCP Servers Service Principal: CRÉÉ`n"
        $report += "    Type: Service Principal`n"
        $report += "    App ID: $(if ($newApp) { $newApp.AppId } else { $newAppJson.appId })`n"
        $report += "    Client Secret: $clientSecret`n"
        $report += "    Permissions: User.Read.All, Mail.Send (à assigner manuellement)`n`n"
    }

} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    $statistics.Failed++
    $report += "[4] MCP Servers Service Principal: ÉCHEC - $($_.Exception.Message)`n`n"
}

# ============================================================================
# SUMMARY
# ============================================================================

$report += @"
═══════════════════════════════════════════════════════════
STATISTIQUES
═══════════════════════════════════════════════════════════
Comptes créés: $($statistics.Created)
Comptes ignorés (déjà existants): $($statistics.Skipped)
Échecs: $($statistics.Failed)

COÛT TOTAL: `$0/mois (aucune licence assignée)

ACTIONS MANUELLES REQUISES:
1. Assigner les permissions API dans le portail Azure
2. Accorder le consentement administrateur
3. (Optionnel) Assigner une licence Office 365 à svc-helpdesk-agent

PROCHAINES ÉTAPES:
1. Exécuter: .\daily_trial_monitor.ps1 (monitoring quotidien)
2. Configurer les variables d'environnement avec les credentials ci-dessus
3. Démarrer TwisterLab: docker-compose up -d

═══════════════════════════════════════════════════════════
"@

# Export report
$report | Out-File -FilePath $accountsFile -Encoding UTF8

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ SETUP TERMINÉ" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📊 RÉSUMÉ:" -ForegroundColor Cyan
Write-Host "   • Comptes créés: $($statistics.Created)" -ForegroundColor White
Write-Host "   • Comptes ignorés: $($statistics.Skipped)" -ForegroundColor Gray
Write-Host "   • Échecs: $($statistics.Failed)" -ForegroundColor $(if ($statistics.Failed -gt 0) { "Red" } else { "Gray" })
Write-Host "   • Coût mensuel: `$0" -ForegroundColor Green
Write-Host "`n📄 Rapport complet: $accountsFile" -ForegroundColor Cyan
Write-Host "`n⚠️  IMPORTANT: Assignez les permissions API dans le portail Azure" -ForegroundColor Yellow
Write-Host "   https://portal.azure.com → Azure AD → App registrations" -ForegroundColor Gray
Write-Host "`n🔜 PROCHAINE ÉTAPE: Exécutez .\daily_trial_monitor.ps1 pour le monitoring" -ForegroundColor Yellow
Write-Host ""
