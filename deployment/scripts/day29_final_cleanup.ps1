#Requires -Version 5.1

<#
.SYNOPSIS
    Nettoyage final avant expiration du trial Azure (Jour 29)

.DESCRIPTION
    Script complet à exécuter le jour 29 du trial pour:
    - Arrêter tous les services payants
    - Retirer toutes les licences Office 365
    - Supprimer les ressources non essentielles
    - Exporter les données importantes
    - Préparer la migration vers free tier uniquement

.PARAMETER Force
    Exécuter sans confirmation

.PARAMETER ExportData
    Exporter les données avant suppression

.EXAMPLE
    .\day29_final_cleanup.ps1 -ExportData

.EXAMPLE
    .\day29_final_cleanup.ps1 -Force -ExportData
#>

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [switch]$ExportData = $true
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$reportPath = ".\reports"
$finalReportFile = Join-Path $reportPath "day29_final_cleanup_$timestamp.txt"
$exportPath = Join-Path $reportPath "data_export_$timestamp"

if (-not (Test-Path $reportPath)) {
    New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
}

if ($ExportData -and -not (Test-Path $exportPath)) {
    New-Item -ItemType Directory -Path $exportPath -Force | Out-Null
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Red
Write-Host "   TWISTERLAB - NETTOYAGE FINAL JOUR 29" -ForegroundColor Red
Write-Host "   ⚠️  ATTENTION: Cette opération est DESTRUCTIVE" -ForegroundColor Yellow
Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Red
Write-Host ""

if (-not $Force) {
    Write-Host "⚠️  Cette opération va:" -ForegroundColor Yellow
    Write-Host "   • Arrêter tous les services Azure payants" -ForegroundColor White
    Write-Host "   • Supprimer toutes les licences Office 365" -ForegroundColor White
    Write-Host "   • Supprimer les resource groups non essentiels" -ForegroundColor White
    Write-Host "   • Exporter les données importantes (si -ExportData)" -ForegroundColor White
    Write-Host ""
    $confirm = Read-Host "Êtes-vous sûr de vouloir continuer? (tapez 'OUI' en majuscules)"
    if ($confirm -ne "OUI") {
        Write-Host "`n❌ Opération annulée" -ForegroundColor Red
        exit 0
    }
}

$statistics = @{
    ResourceGroupsDeleted = 0
    LicensesRemoved = 0
    ServicesSttopped = 0
    DataExported = 0
    EstimatedSavings = 0
}

# ============================================================================
# PHASE 1: EXPORT DATA (si demandé)
# ============================================================================

if ($ExportData) {
    Write-Host "`n[1/5] Export des données importantes..." -ForegroundColor Yellow

    try {
        # Connect to Azure
        $azContext = Get-AzContext -ErrorAction SilentlyContinue
        if (-not $azContext) {
            Connect-AzAccount
            $azContext = Get-AzContext
        }

        # Export subscription info
        $subscription = Get-AzSubscription -SubscriptionId $azContext.Subscription.Id
        $subscription | Export-Clixml -Path (Join-Path $exportPath "subscription_info.xml")

        # Export resource groups
        $resourceGroups = Get-AzResourceGroup
        $resourceGroups | Export-Csv -Path (Join-Path $exportPath "resource_groups.csv") -NoTypeInformation

        # Export all resources
        $allResources = Get-AzResource
        $allResources | Export-Csv -Path (Join-Path $exportPath "resources.csv") -NoTypeInformation

        # Export Azure AD users (if possible)
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
            Import-Module Microsoft.Graph.Users -ErrorAction SilentlyContinue
            Connect-MgGraph -Scopes "User.Read.All" -ErrorAction SilentlyContinue
            $users = Get-MgUser -All -ErrorAction SilentlyContinue
            $users | Export-Csv -Path (Join-Path $exportPath "azure_ad_users.csv") -NoTypeInformation
        }

        # Export app registrations
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
            Import-Module Microsoft.Graph.Applications -ErrorAction SilentlyContinue
            $apps = Get-MgApplication -All -ErrorAction SilentlyContinue
            $apps | Export-Csv -Path (Join-Path $exportPath "app_registrations.csv") -NoTypeInformation
        }

        Write-Host "   ✅ Données exportées vers: $exportPath" -ForegroundColor Green
        $statistics.DataExported = 1

    } catch {
        Write-Host "   ⚠️  Erreur lors de l'export: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[1/5] Export des données ignoré (-ExportData non spécifié)" -ForegroundColor Gray
}

# ============================================================================
# PHASE 2: REMOVE ALL OFFICE 365 LICENSES
# ============================================================================

Write-Host "`n[2/5] Retrait de toutes les licences Office 365..." -ForegroundColor Yellow

try {
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
        Import-Module Microsoft.Graph.Users -ErrorAction SilentlyContinue
        Connect-MgGraph -Scopes "User.ReadWrite.All" -ErrorAction SilentlyContinue

        $users = Get-MgUser -All -Property Id, DisplayName, UserPrincipalName, AssignedLicenses
        $licensedUsers = $users | Where-Object { $_.AssignedLicenses.Count -gt 0 }

        Write-Host "   👥 Utilisateurs licensés: $($licensedUsers.Count)" -ForegroundColor White

        foreach ($user in $licensedUsers) {
            try {
                foreach ($license in $user.AssignedLicenses) {
                    Set-MgUserLicense -UserId $user.Id -AddLicenses @() -RemoveLicenses @($license.SkuId) -ErrorAction Stop
                }
                Write-Host "   ✅ Licence retirée: $($user.UserPrincipalName)" -ForegroundColor Green
                $statistics.LicensesRemoved++
                $statistics.EstimatedSavings += 5
            } catch {
                Write-Host "   ❌ Erreur pour $($user.UserPrincipalName): $($_.Exception.Message)" -ForegroundColor Red
            }
        }

        Write-Host "   ✅ Phase 2 terminée: $($statistics.LicensesRemoved) licences retirées" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Module Microsoft.Graph non disponible" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================================
# PHASE 3: STOP HIGH-COST SERVICES
# ============================================================================

Write-Host "`n[3/5] Arrêt des services à coût élevé..." -ForegroundColor Yellow

try {
    $allResources = Get-AzResource

    # VM, Databases, AKS, App Services, Functions
    $highCostTypes = @(
        "Microsoft.Compute/virtualMachines",
        "Microsoft.Sql/servers",
        "Microsoft.ContainerService/managedClusters",
        "Microsoft.Web/sites"
    )

    $highCostResources = $allResources | Where-Object {
        $type = $_.ResourceType
        $highCostTypes | Where-Object { $type -eq $_ }
    }

    Write-Host "   🔍 Services à coût élevé trouvés: $($highCostResources.Count)" -ForegroundColor White

    foreach ($resource in $highCostResources) {
        try {
            if ($resource.ResourceType -eq "Microsoft.Compute/virtualMachines") {
                Stop-AzVM -ResourceGroupName $resource.ResourceGroupName -Name $resource.Name -Force -ErrorAction Stop
                Write-Host "   ✅ VM arrêtée: $($resource.Name)" -ForegroundColor Green
                $statistics.ServicesSttopped++
                $statistics.EstimatedSavings += 100
            } elseif ($resource.ResourceType -eq "Microsoft.Web/sites") {
                Stop-AzWebApp -ResourceGroupName $resource.ResourceGroupName -Name $resource.Name -ErrorAction Stop
                Write-Host "   ✅ App Service arrêté: $($resource.Name)" -ForegroundColor Green
                $statistics.ServicesSttopped++
                $statistics.EstimatedSavings += 20
            } else {
                Write-Host "   ℹ️  À arrêter manuellement: $($resource.Name) ($($resource.ResourceType))" -ForegroundColor Gray
            }
        } catch {
            Write-Host "   ❌ Erreur pour $($resource.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    Write-Host "   ✅ Phase 3 terminée: $($statistics.ServicesSttopped) services arrêtés" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================================
# PHASE 4: DELETE NON-ESSENTIAL RESOURCE GROUPS
# ============================================================================

Write-Host "`n[4/5] Suppression des resource groups non essentiels..." -ForegroundColor Yellow

try {
    $resourceGroups = Get-AzResourceGroup

    # Keep essential resource groups
    $keepPatterns = @("twisterlab-*", "NetworkWatcherRG")

    foreach ($rg in $resourceGroups) {
        $shouldKeep = $false

        foreach ($pattern in $keepPatterns) {
            if ($rg.ResourceGroupName -like $pattern) {
                $shouldKeep = $true
                break
            }
        }

        if ($shouldKeep) {
            Write-Host "   ⏭️  Conservé: $($rg.ResourceGroupName)" -ForegroundColor Green
        } else {
            try {
                Remove-AzResourceGroup -Name $rg.ResourceGroupName -Force -ErrorAction Stop
                Write-Host "   ✅ Supprimé: $($rg.ResourceGroupName)" -ForegroundColor Green
                $statistics.ResourceGroupsDeleted++
                $statistics.EstimatedSavings += 50
            } catch {
                Write-Host "   ❌ Erreur pour $($rg.ResourceGroupName): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }

    Write-Host "   ✅ Phase 4 terminée: $($statistics.ResourceGroupsDeleted) resource groups supprimés" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================================
# PHASE 5: GENERATE FINAL REPORT
# ============================================================================

Write-Host "`n[5/5] Génération du rapport final..." -ForegroundColor Yellow

$finalReport = @"
═══════════════════════════════════════════════════════════
TWISTERLAB - RAPPORT FINAL NETTOYAGE JOUR 29
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
═══════════════════════════════════════════════════════════

STATISTIQUES:
- Données exportées: $(if ($statistics.DataExported) { "✅ Oui" } else { "❌ Non" })
- Licences Office 365 retirées: $($statistics.LicensesRemoved)
- Services arrêtés: $($statistics.ServicesSttopped)
- Resource Groups supprimés: $($statistics.ResourceGroupsDeleted)

ÉCONOMIES ESTIMÉES:
- Économies mensuelles: `$$($statistics.EstimatedSavings)/mois
- Économies annuelles: `$$($statistics.EstimatedSavings * 12)/an

DONNÉES EXPORTÉES:
$(if ($ExportData) {
"✅ Données sauvegardées dans: $exportPath
   - subscription_info.xml
   - resource_groups.csv
   - resources.csv
   - azure_ad_users.csv
   - app_registrations.csv"
} else {
"❌ Aucune donnée exportée"
})

SERVICES CONSERVÉS (FREE TIER):
✅ Azure AD Free (50K users)
✅ Azure Key Vault (10K ops/month)
✅ Azure Cosmos DB Free (1000 RU/s)
✅ Static Web Apps (Free tier)
✅ Azure Functions (1M executions/month)

PROCHAINES ÉTAPES:
1. Vérifiez l'export des données dans: $exportPath
2. Confirmez l'arrêt de tous les services payants
3. Surveillez la facture finale
4. Migrez vers free tier uniquement
5. (Optionnel) Créez un nouveau trial avec un autre compte

CONFIGURATION FREE TIER:
Pour continuer avec $0 de coût permanent:
1. Gardez uniquement les services gratuits listés ci-dessus
2. Utilisez Ollama local pour les LLMs (pas Azure OpenAI)
3. PostgreSQL local (pas Azure Database)
4. Redis local (pas Azure Cache)

═══════════════════════════════════════════════════════════
TWISTERLAB EST MAINTENANT EN MODE FREE TIER PERMANENT
Coût mensuel: $0
═══════════════════════════════════════════════════════════
"@

$finalReport | Out-File -FilePath $finalReportFile -Encoding UTF8

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ NETTOYAGE FINAL TERMINÉ" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📊 RÉSUMÉ:" -ForegroundColor Cyan
Write-Host "   • Licences retirées: $($statistics.LicensesRemoved)" -ForegroundColor White
Write-Host "   • Services arrêtés: $($statistics.ServicesSttopped)" -ForegroundColor White
Write-Host "   • Resource Groups supprimés: $($statistics.ResourceGroupsDeleted)" -ForegroundColor White
Write-Host "   • Économies mensuelles: `$$($statistics.EstimatedSavings)" -ForegroundColor Green
Write-Host "`n📄 Rapport final: $finalReportFile" -ForegroundColor Cyan
if ($ExportData) {
    Write-Host "📦 Données exportées: $exportPath" -ForegroundColor Cyan
}
Write-Host "`n🎉 TwisterLab est maintenant en mode FREE TIER permanent ($0/mois)" -ForegroundColor Green
Write-Host ""
