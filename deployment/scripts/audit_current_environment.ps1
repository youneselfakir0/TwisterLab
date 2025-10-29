#Requires -Version 5.1

<#
.SYNOPSIS
    Audit complet de l'environnement AD, Azure AD et Azure Resources

.DESCRIPTION
    Scan complet de tous les utilisateurs, service principals, app registrations et ressources Azure.
    Génère des rapports CSV détaillés avec estimation des coûts.

.PARAMETER ExportPath
    Chemin où exporter les rapports CSV (défaut: ./reports)

.PARAMETER IncludeLocalAD
    Inclure l'audit Active Directory local

.EXAMPLE
    .\audit_current_environment.ps1

.EXAMPLE
    .\audit_current_environment.ps1 -ExportPath "C:\Reports" -IncludeLocalAD
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ExportPath = ".\reports",

    [Parameter(Mandatory=$false)]
    [switch]$IncludeLocalAD
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"

# Create reports directory if it doesn't exist
if (-not (Test-Path $ExportPath)) {
    New-Item -ItemType Directory -Path $ExportPath -Force | Out-Null
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   TWISTERLAB - AUDIT ENVIRONNEMENT COMPLET" -ForegroundColor Cyan
Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PHASE 1: AZURE AD USERS AUDIT
# ============================================================================

Write-Host "[1/6] Audit des utilisateurs Azure AD..." -ForegroundColor Yellow

try {
    # Check if Az.Resources module is available
    if (-not (Get-Module -ListAvailable -Name Az.Resources)) {
        Write-Host "   ⚠️  Module Az.Resources non installé. Installation..." -ForegroundColor Yellow
        Install-Module -Name Az.Resources -Scope CurrentUser -Force -AllowClobber
    }

    # Connect to Azure if not already connected
    $azContext = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $azContext) {
        Write-Host "   Connexion à Azure requise..." -ForegroundColor Yellow
        Connect-AzAccount
    }

    # Get Azure AD users via Microsoft Graph
    $azureADUsers = @()

    # Try using Microsoft Graph PowerShell
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
        Import-Module Microsoft.Graph.Users -ErrorAction SilentlyContinue
        Connect-MgGraph -Scopes "User.Read.All", "Directory.Read.All" -ErrorAction SilentlyContinue

        $users = Get-MgUser -All -ErrorAction SilentlyContinue
        foreach ($user in $users) {
            $azureADUsers += [PSCustomObject]@{
                DisplayName = $user.DisplayName
                UserPrincipalName = $user.UserPrincipalName
                AccountEnabled = $user.AccountEnabled
                UserType = $user.UserType
                CreatedDateTime = $user.CreatedDateTime
                Department = $user.Department
                JobTitle = $user.JobTitle
                Mail = $user.Mail
                HasLicense = ($user.AssignedLicenses.Count -gt 0)
                Source = "AzureAD"
            }
        }
    } else {
        Write-Host "   ⚠️  Module Microsoft.Graph non installé. Utilisation de Az CLI..." -ForegroundColor Yellow

        # Fallback to Az CLI
        $usersJson = az ad user list --query "[].{DisplayName:displayName, UPN:userPrincipalName, Enabled:accountEnabled, Type:userType, Created:createdDateTime, Dept:department, Job:jobTitle, Mail:mail}" 2>$null | ConvertFrom-Json

        foreach ($user in $usersJson) {
            $azureADUsers += [PSCustomObject]@{
                DisplayName = $user.DisplayName
                UserPrincipalName = $user.UPN
                AccountEnabled = $user.Enabled
                UserType = $user.Type
                CreatedDateTime = $user.Created
                Department = $user.Dept
                JobTitle = $user.Job
                Mail = $user.Mail
                HasLicense = $false
                Source = "AzureAD"
            }
        }
    }

    Write-Host "   ✅ Trouvé $($azureADUsers.Count) utilisateurs Azure AD" -ForegroundColor Green

    # Export to CSV
    $usersFile = Join-Path $ExportPath "users_$timestamp.csv"
    $azureADUsers | Export-Csv -Path $usersFile -NoTypeInformation -Encoding UTF8
    Write-Host "   📄 Exporté vers: $usersFile" -ForegroundColor Gray

} catch {
    Write-Host "   ❌ Erreur lors de l'audit Azure AD: $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================================
# PHASE 2: LOCAL AD USERS AUDIT (si demandé)
# ============================================================================

if ($IncludeLocalAD) {
    Write-Host "`n[2/6] Audit des utilisateurs Active Directory local..." -ForegroundColor Yellow

    try {
        Import-Module ActiveDirectory -ErrorAction Stop

        $localADUsers = Get-ADUser -Filter * -Properties DisplayName, EmailAddress, Enabled, Created, Department, Title, Description |
            Select-Object @{N='DisplayName';E={$_.DisplayName}},
                         @{N='UserPrincipalName';E={$_.UserPrincipalName}},
                         @{N='AccountEnabled';E={$_.Enabled}},
                         @{N='UserType';E={'Member'}},
                         @{N='CreatedDateTime';E={$_.Created}},
                         @{N='Department';E={$_.Department}},
                         @{N='JobTitle';E={$_.Title}},
                         @{N='Mail';E={$_.EmailAddress}},
                         @{N='HasLicense';E={$false}},
                         @{N='Source';E={'LocalAD'}}

        Write-Host "   ✅ Trouvé $($localADUsers.Count) utilisateurs AD local" -ForegroundColor Green

        # Append to CSV
        $localADUsers | Export-Csv -Path $usersFile -NoTypeInformation -Encoding UTF8 -Append

    } catch {
        Write-Host "   ⚠️  Module Active Directory non disponible ou non connecté à un domaine" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[2/6] Audit AD local ignoré (utilisez -IncludeLocalAD pour inclure)" -ForegroundColor Gray
}

# ============================================================================
# PHASE 3: APP REGISTRATIONS & SERVICE PRINCIPALS AUDIT
# ============================================================================

Write-Host "`n[3/6] Audit des App Registrations et Service Principals..." -ForegroundColor Yellow

try {
    $apps = @()

    # Try Microsoft Graph
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
        Import-Module Microsoft.Graph.Applications -ErrorAction SilentlyContinue

        $graphApps = Get-MgApplication -All -ErrorAction SilentlyContinue
        foreach ($app in $graphApps) {
            $apps += [PSCustomObject]@{
                DisplayName = $app.DisplayName
                ApplicationId = $app.AppId
                ObjectId = $app.Id
                CreatedDateTime = $app.CreatedDateTime
                SignInAudience = $app.SignInAudience
                PublisherDomain = $app.PublisherDomain
                Type = "Application"
            }
        }

        $spns = Get-MgServicePrincipal -All -ErrorAction SilentlyContinue
        foreach ($spn in $spns) {
            $apps += [PSCustomObject]@{
                DisplayName = $spn.DisplayName
                ApplicationId = $spn.AppId
                ObjectId = $spn.Id
                CreatedDateTime = $spn.CreatedDateTime
                SignInAudience = $spn.ServicePrincipalType
                PublisherDomain = $spn.AppOwnerOrganizationId
                Type = "ServicePrincipal"
            }
        }
    } else {
        # Fallback to Az CLI
        $appsJson = az ad app list --query "[].{DisplayName:displayName, AppId:appId, ObjectId:id, Created:createdDateTime, Audience:signInAudience, Publisher:publisherDomain}" 2>$null | ConvertFrom-Json

        foreach ($app in $appsJson) {
            $apps += [PSCustomObject]@{
                DisplayName = $app.DisplayName
                ApplicationId = $app.AppId
                ObjectId = $app.ObjectId
                CreatedDateTime = $app.Created
                SignInAudience = $app.Audience
                PublisherDomain = $app.Publisher
                Type = "Application"
            }
        }

        $spnsJson = az ad sp list --all --query "[].{DisplayName:displayName, AppId:appId, ObjectId:id}" 2>$null | ConvertFrom-Json

        foreach ($spn in $spnsJson) {
            $apps += [PSCustomObject]@{
                DisplayName = $spn.DisplayName
                ApplicationId = $spn.AppId
                ObjectId = $spn.ObjectId
                CreatedDateTime = $null
                SignInAudience = "ServicePrincipal"
                PublisherDomain = $null
                Type = "ServicePrincipal"
            }
        }
    }

    Write-Host "   ✅ Trouvé $($apps.Count) applications et service principals" -ForegroundColor Green

    # Export to CSV
    $appsFile = Join-Path $ExportPath "apps_$timestamp.csv"
    $apps | Export-Csv -Path $appsFile -NoTypeInformation -Encoding UTF8
    Write-Host "   📄 Exporté vers: $appsFile" -ForegroundColor Gray

} catch {
    Write-Host "   ❌ Erreur lors de l'audit des applications: $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================================
# PHASE 4: AZURE RESOURCE GROUPS & RESOURCES AUDIT
# ============================================================================

Write-Host "`n[4/6] Audit des Resource Groups et Ressources Azure..." -ForegroundColor Yellow

try {
    $resourceGroups = Get-AzResourceGroup
    $allResources = @()

    foreach ($rg in $resourceGroups) {
        $resources = Get-AzResource -ResourceGroupName $rg.ResourceGroupName

        foreach ($resource in $resources) {
            # Estimate cost category
            $costCategory = "Low"
            if ($resource.ResourceType -match "VirtualMachines|Databases|Kubernetes") {
                $costCategory = "High"
            } elseif ($resource.ResourceType -match "Storage|Functions|AppService") {
                $costCategory = "Medium"
            }

            $allResources += [PSCustomObject]@{
                ResourceGroup = $rg.ResourceGroupName
                ResourceName = $resource.Name
                ResourceType = $resource.ResourceType
                Location = $resource.Location
                CreatedTime = $rg.Tags.CreatedTime
                Tags = ($resource.Tags.Keys -join "; ")
                CostCategory = $costCategory
                Status = "Active"
            }
        }
    }

    Write-Host "   ✅ Trouvé $($resourceGroups.Count) resource groups avec $($allResources.Count) ressources" -ForegroundColor Green

    # Export to CSV
    $resourcesFile = Join-Path $ExportPath "resources_$timestamp.csv"
    $allResources | Export-Csv -Path $resourcesFile -NoTypeInformation -Encoding UTF8
    Write-Host "   📄 Exporté vers: $resourcesFile" -ForegroundColor Gray

} catch {
    Write-Host "   ❌ Erreur lors de l'audit des ressources: $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================================
# PHASE 5: IDENTIFY OLD PROJECTS
# ============================================================================

Write-Host "`n[5/6] Identification des anciens projets..." -ForegroundColor Yellow

$oldPatterns = @("test-*", "demo-*", "old-*", "poc-*", "temp-*", "dev-*")
$oldItems = @{
    Users = @()
    Apps = @()
    Resources = @()
}

# Check users
foreach ($pattern in $oldPatterns) {
    $matchingUsers = $azureADUsers | Where-Object { $_.UserPrincipalName -like $pattern -or $_.DisplayName -like $pattern }
    $oldItems.Users += $matchingUsers
}

# Check apps
foreach ($pattern in $oldPatterns) {
    $matchingApps = $apps | Where-Object { $_.DisplayName -like $pattern }
    $oldItems.Apps += $matchingApps
}

# Check resource groups (older than 30 days)
$thirtyDaysAgo = (Get-Date).AddDays(-30)
$oldResources = $allResources | Where-Object {
    $_.CreatedTime -and [DateTime]$_.CreatedTime -lt $thirtyDaysAgo
}
$oldItems.Resources += $oldResources

Write-Host "   ⚠️  Trouvé $($oldItems.Users.Count) anciens utilisateurs" -ForegroundColor Yellow
Write-Host "   ⚠️  Trouvé $($oldItems.Apps.Count) anciennes applications" -ForegroundColor Yellow
Write-Host "   ⚠️  Trouvé $($oldItems.Resources.Count) ressources inactives (>30 jours)" -ForegroundColor Yellow

# Export old items
$oldItemsFile = Join-Path $ExportPath "old_items_$timestamp.csv"
$oldItemsSummary = @()

foreach ($user in $oldItems.Users) {
    $oldItemsSummary += [PSCustomObject]@{
        Type = "User"
        Name = $user.DisplayName
        Identifier = $user.UserPrincipalName
        Created = $user.CreatedDateTime
        Reason = "Naming pattern match"
    }
}

foreach ($app in $oldItems.Apps) {
    $oldItemsSummary += [PSCustomObject]@{
        Type = "Application"
        Name = $app.DisplayName
        Identifier = $app.ApplicationId
        Created = $app.CreatedDateTime
        Reason = "Naming pattern match"
    }
}

foreach ($resource in $oldItems.Resources) {
    $oldItemsSummary += [PSCustomObject]@{
        Type = "Resource"
        Name = $resource.ResourceName
        Identifier = $resource.ResourceGroup
        Created = $resource.CreatedTime
        Reason = "Inactive >30 days"
    }
}

$oldItemsSummary | Export-Csv -Path $oldItemsFile -NoTypeInformation -Encoding UTF8
Write-Host "   📄 Exporté vers: $oldItemsFile" -ForegroundColor Gray

# ============================================================================
# PHASE 6: COST ESTIMATION
# ============================================================================

Write-Host "`n[6/6] Estimation des coûts..." -ForegroundColor Yellow

$costEstimation = @{
    Users = @{
        Total = $azureADUsers.Count
        Licensed = ($azureADUsers | Where-Object { $_.HasLicense }).Count
        EstimatedCost = 0
    }
    Resources = @{
        High = ($allResources | Where-Object { $_.CostCategory -eq "High" }).Count
        Medium = ($allResources | Where-Object { $_.CostCategory -eq "Medium" }).Count
        Low = ($allResources | Where-Object { $_.CostCategory -eq "Low" }).Count
        EstimatedCost = 0
    }
}

# Rough cost estimation (Office 365 Business Basic = ~$5/user/month)
$costEstimation.Users.EstimatedCost = $costEstimation.Users.Licensed * 5

# Rough resource cost estimation
$costEstimation.Resources.EstimatedCost = (
    ($costEstimation.Resources.High * 100) +    # High = ~$100/month
    ($costEstimation.Resources.Medium * 20) +   # Medium = ~$20/month
    ($costEstimation.Resources.Low * 2)         # Low = ~$2/month
)

$totalEstimatedCost = $costEstimation.Users.EstimatedCost + $costEstimation.Resources.EstimatedCost

Write-Host "`n   💰 Estimation des coûts mensuels:" -ForegroundColor Cyan
Write-Host "   ├─ Utilisateurs: $($costEstimation.Users.Licensed) licensés × $5 = `$$($costEstimation.Users.EstimatedCost)" -ForegroundColor White
Write-Host "   ├─ Ressources High: $($costEstimation.Resources.High) × $100 = `$$($costEstimation.Resources.High * 100)" -ForegroundColor White
Write-Host "   ├─ Ressources Medium: $($costEstimation.Resources.Medium) × $20 = `$$($costEstimation.Resources.Medium * 20)" -ForegroundColor White
Write-Host "   ├─ Ressources Low: $($costEstimation.Resources.Low) × $2 = `$$($costEstimation.Resources.Low * 2)" -ForegroundColor White
Write-Host "   └─ TOTAL ESTIMÉ: `$$totalEstimatedCost/mois" -ForegroundColor Yellow

# Export cost estimation
$costFile = Join-Path $ExportPath "cost_estimation_$timestamp.txt"
@"
═══════════════════════════════════════════════════════════
TWISTERLAB - ESTIMATION DES COÛTS
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
═══════════════════════════════════════════════════════════

UTILISATEURS:
- Total: $($costEstimation.Users.Total)
- Licensés: $($costEstimation.Users.Licensed)
- Coût estimé: `$$($costEstimation.Users.EstimatedCost)/mois

RESSOURCES AZURE:
- High cost: $($costEstimation.Resources.High) ressources
- Medium cost: $($costEstimation.Resources.Medium) ressources
- Low cost: $($costEstimation.Resources.Low) ressources
- Coût estimé: `$$($costEstimation.Resources.EstimatedCost)/mois

TOTAL ESTIMÉ: `$$totalEstimatedCost/mois

ANCIENS PROJETS DÉTECTÉS:
- Utilisateurs à nettoyer: $($oldItems.Users.Count)
- Applications à nettoyer: $($oldItems.Apps.Count)
- Ressources à nettoyer: $($oldItems.Resources.Count)

FICHIERS GÉNÉRÉS:
- $usersFile
- $appsFile
- $resourcesFile
- $oldItemsFile
- $costFile

═══════════════════════════════════════════════════════════
"@ | Out-File -FilePath $costFile -Encoding UTF8

Write-Host "`n   📄 Rapport complet exporté vers: $costFile" -ForegroundColor Gray

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ AUDIT TERMINÉ AVEC SUCCÈS" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📊 RÉSUMÉ:" -ForegroundColor Cyan
Write-Host "   • Utilisateurs Azure AD: $($azureADUsers.Count)" -ForegroundColor White
Write-Host "   • Applications/SPs: $($apps.Count)" -ForegroundColor White
Write-Host "   • Resource Groups: $($resourceGroups.Count)" -ForegroundColor White
Write-Host "   • Ressources Azure: $($allResources.Count)" -ForegroundColor White
Write-Host "   • Coût mensuel estimé: `$$totalEstimatedCost" -ForegroundColor Yellow
Write-Host "`n📁 Tous les rapports exportés dans: $ExportPath" -ForegroundColor Cyan
Write-Host "`n🔜 PROCHAINE ÉTAPE: Exécutez .\cleanup_old_projects.ps1 pour nettoyer" -ForegroundColor Yellow
Write-Host ""
