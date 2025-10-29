#Requires -Version 5.1

<#
.SYNOPSIS
    Nettoyage sélectif des anciens projets et ressources

.DESCRIPTION
    Nettoie les utilisateurs, applications et ressources Azure identifiés comme anciens ou de test.
    Demande confirmation pour chaque action sauf si -Force est utilisé.

.PARAMETER Force
    Supprime sans confirmation interactive

.PARAMETER DryRun
    Mode test - affiche ce qui serait supprimé sans rien faire

.PARAMETER ExcludeUsers
    Ne pas supprimer les utilisateurs

.PARAMETER ExcludeApps
    Ne pas supprimer les applications

.PARAMETER ExcludeResources
    Ne pas supprimer les ressources Azure

.EXAMPLE
    .\cleanup_old_projects.ps1

.EXAMPLE
    .\cleanup_old_projects.ps1 -DryRun

.EXAMPLE
    .\cleanup_old_projects.ps1 -Force -ExcludeUsers
#>

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun,

    [Parameter(Mandatory=$false)]
    [switch]$ExcludeUsers,

    [Parameter(Mandatory=$false)]
    [switch]$ExcludeApps,

    [Parameter(Mandatory=$false)]
    [switch]$ExcludeResources
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$reportPath = ".\reports"
$logFile = Join-Path $reportPath "cleanup_report_$timestamp.txt"

# Create reports directory
if (-not (Test-Path $reportPath)) {
    New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
}

# Initialize log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")

    $logMessage = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Add-Content -Path $logFile -Value $logMessage

    switch ($Level) {
        "INFO" { Write-Host $Message -ForegroundColor White }
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "WARNING" { Write-Host $Message -ForegroundColor Yellow }
        "ERROR" { Write-Host $Message -ForegroundColor Red }
        "DRYRUN" { Write-Host $Message -ForegroundColor Cyan }
    }
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   TWISTERLAB - NETTOYAGE DES ANCIENS PROJETS" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "   MODE: DRY RUN (Aucune suppression réelle)" -ForegroundColor Yellow
} elseif ($Force) {
    Write-Host "   MODE: FORCE (Sans confirmation)" -ForegroundColor Red
} else {
    Write-Host "   MODE: INTERACTIF (Avec confirmation)" -ForegroundColor Green
}
Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Log "=== Début du nettoyage ===" "INFO"
Write-Log "Mode: DryRun=$DryRun, Force=$Force" "INFO"

# ============================================================================
# CONNECT TO AZURE
# ============================================================================

Write-Log "Vérification de la connexion Azure..." "INFO"

try {
    $azContext = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $azContext) {
        Write-Log "Connexion à Azure requise..." "WARNING"
        Connect-AzAccount
        $azContext = Get-AzContext
    }

    Write-Log "✅ Connecté à: $($azContext.Subscription.Name)" "SUCCESS"
} catch {
    Write-Log "❌ Erreur de connexion Azure: $($_.Exception.Message)" "ERROR"
    exit 1
}

# ============================================================================
# PATTERNS FOR OLD PROJECTS
# ============================================================================

$oldPatterns = @("test-*", "demo-*", "old-*", "poc-*", "temp-*", "dev-*", "sample-*")
$keepPatterns = @("*admin*", "*root*", "*prod*", "*production*", "twisterlab-*", "svc-*", "sp-*")

$statistics = @{
    UsersDeleted = 0
    UsersSkipped = 0
    AppsDeleted = 0
    AppsSkipped = 0
    ResourceGroupsDeleted = 0
    ResourceGroupsSkipped = 0
}

# ============================================================================
# PHASE 1: CLEANUP AZURE AD USERS
# ============================================================================

if (-not $ExcludeUsers) {
    Write-Host "`n[1/3] Nettoyage des utilisateurs Azure AD..." -ForegroundColor Yellow
    Write-Log "=== Phase 1: Nettoyage utilisateurs ===" "INFO"

    try {
        # Try Microsoft Graph
        $users = @()
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
            Import-Module Microsoft.Graph.Users -ErrorAction SilentlyContinue
            Connect-MgGraph -Scopes "User.ReadWrite.All" -ErrorAction SilentlyContinue
            $users = Get-MgUser -All -ErrorAction SilentlyContinue
        } else {
            # Fallback to Az CLI
            $usersJson = az ad user list 2>$null | ConvertFrom-Json
            $users = $usersJson | ForEach-Object {
                [PSCustomObject]@{
                    DisplayName = $_.displayName
                    UserPrincipalName = $_.userPrincipalName
                    Id = $_.id
                }
            }
        }

        foreach ($user in $users) {
            $upn = $user.UserPrincipalName
            $shouldDelete = $false

            # Check if matches old patterns
            foreach ($pattern in $oldPatterns) {
                if ($upn -like $pattern -or $user.DisplayName -like $pattern) {
                    $shouldDelete = $true
                    break
                }
            }

            # Check if should be kept
            foreach ($keepPattern in $keepPatterns) {
                if ($upn -like $keepPattern -or $user.DisplayName -like $keepPattern) {
                    $shouldDelete = $false
                    Write-Log "   ⏭️  Ignoré (pattern protégé): $upn" "WARNING"
                    $statistics.UsersSkipped++
                    break
                }
            }

            if ($shouldDelete) {
                if ($DryRun) {
                    Write-Log "   [DRY RUN] Supprimerait: $upn ($($user.DisplayName))" "DRYRUN"
                } else {
                    $confirm = $true
                    if (-not $Force) {
                        $response = Read-Host "   Supprimer l'utilisateur '$upn' ? (o/N)"
                        $confirm = ($response -eq 'o' -or $response -eq 'O')
                    }

                    if ($confirm) {
                        try {
                            if (Get-Module -ListAvailable -Name Microsoft.Graph.Users) {
                                Remove-MgUser -UserId $user.Id -ErrorAction Stop
                            } else {
                                az ad user delete --id $user.Id 2>$null
                            }
                            Write-Log "   ✅ Supprimé: $upn" "SUCCESS"
                            $statistics.UsersDeleted++
                        } catch {
                            Write-Log "   ❌ Erreur lors de la suppression de $upn : $($_.Exception.Message)" "ERROR"
                            $statistics.UsersSkipped++
                        }
                    } else {
                        Write-Log "   ⏭️  Ignoré (utilisateur): $upn" "WARNING"
                        $statistics.UsersSkipped++
                    }
                }
            }
        }

        Write-Log "Phase 1 terminée: $($statistics.UsersDeleted) supprimés, $($statistics.UsersSkipped) ignorés" "SUCCESS"

    } catch {
        Write-Log "❌ Erreur lors du nettoyage des utilisateurs: $($_.Exception.Message)" "ERROR"
    }
} else {
    Write-Host "`n[1/3] Nettoyage des utilisateurs ignoré (-ExcludeUsers)" -ForegroundColor Gray
    Write-Log "Phase 1 ignorée (ExcludeUsers)" "INFO"
}

# ============================================================================
# PHASE 2: CLEANUP APP REGISTRATIONS & SERVICE PRINCIPALS
# ============================================================================

if (-not $ExcludeApps) {
    Write-Host "`n[2/3] Nettoyage des App Registrations..." -ForegroundColor Yellow
    Write-Log "=== Phase 2: Nettoyage applications ===" "INFO"

    try {
        # Get apps
        $apps = @()
        if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
            Import-Module Microsoft.Graph.Applications -ErrorAction SilentlyContinue
            $apps = Get-MgApplication -All -ErrorAction SilentlyContinue
        } else {
            $appsJson = az ad app list 2>$null | ConvertFrom-Json
            $apps = $appsJson | ForEach-Object {
                [PSCustomObject]@{
                    DisplayName = $_.displayName
                    AppId = $_.appId
                    Id = $_.id
                }
            }
        }

        foreach ($app in $apps) {
            $shouldDelete = $false

            # Check if matches old patterns
            foreach ($pattern in $oldPatterns) {
                if ($app.DisplayName -like $pattern) {
                    $shouldDelete = $true
                    break
                }
            }

            # Check if should be kept
            foreach ($keepPattern in $keepPatterns) {
                if ($app.DisplayName -like $keepPattern) {
                    $shouldDelete = $false
                    Write-Log "   ⏭️  Ignoré (pattern protégé): $($app.DisplayName)" "WARNING"
                    $statistics.AppsSkipped++
                    break
                }
            }

            if ($shouldDelete) {
                if ($DryRun) {
                    Write-Log "   [DRY RUN] Supprimerait: $($app.DisplayName) (App ID: $($app.AppId))" "DRYRUN"
                } else {
                    $confirm = $true
                    if (-not $Force) {
                        $response = Read-Host "   Supprimer l'application '$($app.DisplayName)' ? (o/N)"
                        $confirm = ($response -eq 'o' -or $response -eq 'O')
                    }

                    if ($confirm) {
                        try {
                            if (Get-Module -ListAvailable -Name Microsoft.Graph.Applications) {
                                Remove-MgApplication -ApplicationId $app.Id -ErrorAction Stop
                            } else {
                                az ad app delete --id $app.Id 2>$null
                            }
                            Write-Log "   ✅ Supprimé: $($app.DisplayName)" "SUCCESS"
                            $statistics.AppsDeleted++
                        } catch {
                            Write-Log "   ❌ Erreur lors de la suppression de $($app.DisplayName): $($_.Exception.Message)" "ERROR"
                            $statistics.AppsSkipped++
                        }
                    } else {
                        Write-Log "   ⏭️  Ignoré (utilisateur): $($app.DisplayName)" "WARNING"
                        $statistics.AppsSkipped++
                    }
                }
            }
        }

        Write-Log "Phase 2 terminée: $($statistics.AppsDeleted) supprimés, $($statistics.AppsSkipped) ignorés" "SUCCESS"

    } catch {
        Write-Log "❌ Erreur lors du nettoyage des applications: $($_.Exception.Message)" "ERROR"
    }
} else {
    Write-Host "`n[2/3] Nettoyage des applications ignoré (-ExcludeApps)" -ForegroundColor Gray
    Write-Log "Phase 2 ignorée (ExcludeApps)" "INFO"
}

# ============================================================================
# PHASE 3: CLEANUP AZURE RESOURCE GROUPS
# ============================================================================

if (-not $ExcludeResources) {
    Write-Host "`n[3/3] Nettoyage des Resource Groups Azure..." -ForegroundColor Yellow
    Write-Log "=== Phase 3: Nettoyage resource groups ===" "INFO"

    try {
        $resourceGroups = Get-AzResourceGroup

        foreach ($rg in $resourceGroups) {
            $shouldDelete = $false

            # Check if matches old patterns
            foreach ($pattern in $oldPatterns) {
                if ($rg.ResourceGroupName -like $pattern) {
                    $shouldDelete = $true
                    break
                }
            }

            # Check if inactive (>30 days with no resources modified)
            $resources = Get-AzResource -ResourceGroupName $rg.ResourceGroupName
            if ($resources.Count -eq 0) {
                $shouldDelete = $true
            }

            # Check if should be kept
            foreach ($keepPattern in $keepPatterns) {
                if ($rg.ResourceGroupName -like $keepPattern) {
                    $shouldDelete = $false
                    Write-Log "   ⏭️  Ignoré (pattern protégé): $($rg.ResourceGroupName)" "WARNING"
                    $statistics.ResourceGroupsSkipped++
                    break
                }
            }

            if ($shouldDelete) {
                $resourceCount = $resources.Count

                if ($DryRun) {
                    Write-Log "   [DRY RUN] Supprimerait: $($rg.ResourceGroupName) ($resourceCount ressources)" "DRYRUN"
                } else {
                    $confirm = $true
                    if (-not $Force) {
                        Write-Host "`n   ⚠️  Resource Group: $($rg.ResourceGroupName)" -ForegroundColor Yellow
                        Write-Host "      Ressources: $resourceCount" -ForegroundColor Gray
                        Write-Host "      Localisation: $($rg.Location)" -ForegroundColor Gray
                        $response = Read-Host "   Supprimer ce resource group ? (o/N)"
                        $confirm = ($response -eq 'o' -or $response -eq 'O')
                    }

                    if ($confirm) {
                        try {
                            Remove-AzResourceGroup -Name $rg.ResourceGroupName -Force -ErrorAction Stop
                            Write-Log "   ✅ Supprimé: $($rg.ResourceGroupName) ($resourceCount ressources)" "SUCCESS"
                            $statistics.ResourceGroupsDeleted++
                        } catch {
                            Write-Log "   ❌ Erreur lors de la suppression de $($rg.ResourceGroupName): $($_.Exception.Message)" "ERROR"
                            $statistics.ResourceGroupsSkipped++
                        }
                    } else {
                        Write-Log "   ⏭️  Ignoré (utilisateur): $($rg.ResourceGroupName)" "WARNING"
                        $statistics.ResourceGroupsSkipped++
                    }
                }
            }
        }

        Write-Log "Phase 3 terminée: $($statistics.ResourceGroupsDeleted) supprimés, $($statistics.ResourceGroupsSkipped) ignorés" "SUCCESS"

    } catch {
        Write-Log "❌ Erreur lors du nettoyage des resource groups: $($_.Exception.Message)" "ERROR"
    }
} else {
    Write-Host "`n[3/3] Nettoyage des ressources ignoré (-ExcludeResources)" -ForegroundColor Gray
    Write-Log "Phase 3 ignorée (ExcludeResources)" "INFO"
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ NETTOYAGE TERMINÉ" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📊 STATISTIQUES:" -ForegroundColor Cyan
Write-Host "   • Utilisateurs supprimés: $($statistics.UsersDeleted)" -ForegroundColor White
Write-Host "   • Utilisateurs ignorés: $($statistics.UsersSkipped)" -ForegroundColor Gray
Write-Host "   • Applications supprimées: $($statistics.AppsDeleted)" -ForegroundColor White
Write-Host "   • Applications ignorées: $($statistics.AppsSkipped)" -ForegroundColor Gray
Write-Host "   • Resource Groups supprimés: $($statistics.ResourceGroupsDeleted)" -ForegroundColor White
Write-Host "   • Resource Groups ignorés: $($statistics.ResourceGroupsSkipped)" -ForegroundColor Gray
Write-Host "`n📄 Rapport détaillé: $logFile" -ForegroundColor Cyan
Write-Host "`n🔜 PROCHAINE ÉTAPE: Exécutez .\setup_twisterlab_accounts.ps1" -ForegroundColor Yellow
Write-Host ""

Write-Log "=== Nettoyage terminé ===" "SUCCESS"
Write-Log "Utilisateurs: $($statistics.UsersDeleted) supprimés, $($statistics.UsersSkipped) ignorés" "INFO"
Write-Log "Applications: $($statistics.AppsDeleted) supprimés, $($statistics.AppsSkipped) ignorés" "INFO"
Write-Log "Resource Groups: $($statistics.ResourceGroupsDeleted) supprimés, $($statistics.ResourceGroupsSkipped) ignorés" "INFO"
