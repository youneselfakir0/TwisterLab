#Requires -Version 5.1

<#
.SYNOPSIS
    Monitoring quotidien des crédits Azure Trial et détection automatique

.DESCRIPTION
    Auto-détecte les trials Azure/Office 365, calcule le budget quotidien,
    surveille les dépenses et envoie des alertes si nécessaire.

.EXAMPLE
    .\daily_trial_monitor.ps1
#>

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$reportPath = ".\reports"
$reportFile = Join-Path $reportPath "daily_budget_$timestamp.txt"

if (-not (Test-Path $reportPath)) {
    New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   TWISTERLAB - MONITORING QUOTIDIEN AZURE TRIAL" -ForegroundColor Cyan
Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# CONNECT TO AZURE
# ============================================================================

try {
    $azContext = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $azContext) {
        Connect-AzAccount
        $azContext = Get-AzContext
    }
    Write-Host "✅ Connecté: $($azContext.Subscription.Name)" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur de connexion Azure" -ForegroundColor Red
    exit 1
}

# ============================================================================
# DETECT TRIAL STATUS
# ============================================================================

Write-Host "`n[1/4] Détection du statut Trial..." -ForegroundColor Yellow

$subscription = Get-AzSubscription -SubscriptionId $azContext.Subscription.Id
$isTrial = $subscription.Name -match "Trial|Free|Student|Starter"

$trialInfo = @{
    IsTrial = $isTrial
    Name = $subscription.Name
    TotalCredit = if ($isTrial) { 200 } else { 0 }
    TrialDays = 30
    DailyBudget = if ($isTrial) { [math]::Round(200 / 30, 2) } else { 0 }
}

if ($isTrial) {
    Write-Host "   ⚠️  Trial détecté: $($subscription.Name)" -ForegroundColor Yellow
    Write-Host "   💰 Crédit total: `$$($trialInfo.TotalCredit)" -ForegroundColor Cyan
    Write-Host "   📅 Durée: $($trialInfo.TrialDays) jours" -ForegroundColor Cyan
    Write-Host "   💵 Budget quotidien recommandé: `$$($trialInfo.DailyBudget)/jour" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Abonnement standard: $($subscription.Name)" -ForegroundColor Gray
}

# ============================================================================
# CHECK CURRENT SPENDING
# ============================================================================

Write-Host "`n[2/4] Vérification des dépenses actuelles..." -ForegroundColor Yellow

try {
    $startDate = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
    $endDate = (Get-Date).ToString("yyyy-MM-dd")

    # Try to get consumption data
    $consumption = Get-AzConsumptionUsageDetail -StartDate $startDate -EndDate $endDate -ErrorAction SilentlyContinue

    if ($consumption) {
        $dailySpending = ($consumption | Measure-Object -Property PretaxCost -Sum).Sum
        $percentOfBudget = if ($trialInfo.DailyBudget -gt 0) {
            [math]::Round(($dailySpending / $trialInfo.DailyBudget) * 100, 2)
        } else { 0 }

        Write-Host "   💸 Dépenses hier: `$$([math]::Round($dailySpending, 2))" -ForegroundColor White

        if ($percentOfBudget -ge 100) {
            Write-Host "   🚨 ALERTE: Budget quotidien dépassé ($percentOfBudget%)" -ForegroundColor Red
        } elseif ($percentOfBudget -ge 80) {
            Write-Host "   ⚠️  Attention: 80% du budget atteint ($percentOfBudget%)" -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ Dans le budget ($percentOfBudget%)" -ForegroundColor Green
        }
    } else {
        Write-Host "   ℹ️  Données de consommation non disponibles (peut prendre 24-48h)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Impossible de récupérer les données: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ============================================================================
# CHECK ACTIVE RESOURCES
# ============================================================================

Write-Host "`n[3/4] Inventaire des ressources actives..." -ForegroundColor Yellow

$resourceGroups = Get-AzResourceGroup
$allResources = @()

foreach ($rg in $resourceGroups) {
    $resources = Get-AzResource -ResourceGroupName $rg.ResourceGroupName
    $allResources += $resources
}

$highCostResources = $allResources | Where-Object {
    $_.ResourceType -match "VirtualMachines|Databases|Kubernetes|AppService|Functions"
}

Write-Host "   📦 Resource Groups: $($resourceGroups.Count)" -ForegroundColor White
Write-Host "   📦 Total Ressources: $($allResources.Count)" -ForegroundColor White
Write-Host "   💰 Ressources à coût élevé: $($highCostResources.Count)" -ForegroundColor $(if ($highCostResources.Count -gt 0) { "Yellow" } else { "Green" })

if ($highCostResources.Count -gt 0) {
    Write-Host "`n   ⚠️  Ressources à surveiller:" -ForegroundColor Yellow
    foreach ($resource in $highCostResources) {
        Write-Host "      • $($resource.Name) ($($resource.ResourceType))" -ForegroundColor Gray
    }
}

# ============================================================================
# CHECK OFFICE 365 LICENSES
# ============================================================================

Write-Host "`n[4/4] Vérification des licences Office 365..." -ForegroundColor Yellow

try {
    if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
        Import-Module Microsoft.Graph.Users -ErrorAction SilentlyContinue
        Connect-MgGraph -Scopes "User.Read.All" -ErrorAction SilentlyContinue

        $users = Get-MgUser -All -ErrorAction SilentlyContinue
        $licensedUsers = $users | Where-Object { $_.AssignedLicenses.Count -gt 0 }

        Write-Host "   👥 Utilisateurs total: $($users.Count)" -ForegroundColor White
        Write-Host "   📄 Utilisateurs licensés: $($licensedUsers.Count)" -ForegroundColor White

        $estimatedO365Cost = $licensedUsers.Count * 5
        Write-Host "   💰 Coût estimé O365: `$$estimatedO365Cost/mois" -ForegroundColor Cyan
    } else {
        Write-Host "   ℹ️  Module Microsoft.Graph non installé" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Impossible de vérifier les licences: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ============================================================================
# GENERATE REPORT
# ============================================================================

$report = @"
═══════════════════════════════════════════════════════════
TWISTERLAB - RAPPORT QUOTIDIEN
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
═══════════════════════════════════════════════════════════

ABONNEMENT:
- Nom: $($subscription.Name)
- Type: $(if ($isTrial) { "TRIAL" } else { "Standard" })
- ID: $($subscription.Id)

BUDGET:
$(if ($isTrial) {
"- Crédit total: `$$($trialInfo.TotalCredit)
- Durée: $($trialInfo.TrialDays) jours
- Budget quotidien: `$$($trialInfo.DailyBudget)/jour
- Dépenses hier: `$$([math]::Round($dailySpending, 2))
- % du budget: $percentOfBudget%"
} else {
"- Abonnement payant (pas de limite trial)"
})

RESSOURCES:
- Resource Groups: $($resourceGroups.Count)
- Total ressources: $($allResources.Count)
- Ressources à coût élevé: $($highCostResources.Count)

LICENCES OFFICE 365:
- Utilisateurs licensés: $($licensedUsers.Count)
- Coût estimé: `$$estimatedO365Cost/mois

═══════════════════════════════════════════════════════════
RECOMMANDATIONS:
$(if ($percentOfBudget -ge 100) {
"🚨 URGENT: Budget dépassé! Exécutez:
   .\cleanup_azure_paid_services.ps1
"
} elseif ($percentOfBudget -ge 80) {
"⚠️  Attention: Budget à 80%
   - Surveillez les dépenses
   - Réduisez les ressources non essentielles
"
} else {
"✅ Tout va bien! Continuez le monitoring quotidien.
"
})
═══════════════════════════════════════════════════════════
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ MONITORING TERMINÉ" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📄 Rapport: $reportFile" -ForegroundColor Cyan
Write-Host "`n💡 TIP: Ajoutez ce script au Task Scheduler pour exécution quotidienne" -ForegroundColor Yellow
Write-Host ""
