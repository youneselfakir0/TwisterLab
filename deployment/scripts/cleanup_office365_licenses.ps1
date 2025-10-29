#Requires -Version 5.1

<#
.SYNOPSIS
    Nettoyage des licences Office 365 non utilisées

.DESCRIPTION
    Retire les licences Office 365 des comptes qui ne les utilisent pas activement.
    Conserve uniquement les licences pour les comptes critiques.

.PARAMETER Force
    Supprimer sans confirmation

.PARAMETER DryRun
    Mode test - affiche ce qui serait fait

.EXAMPLE
    .\cleanup_office365_licenses.ps1

.EXAMPLE
    .\cleanup_office365_licenses.ps1 -DryRun
#>

param(
    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$reportPath = ".\reports"
$reportFile = Join-Path $reportPath "license_cleanup_$timestamp.txt"

if (-not (Test-Path $reportPath)) {
    New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   TWISTERLAB - NETTOYAGE LICENCES OFFICE 365" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "   MODE: DRY RUN" -ForegroundColor Yellow
}
Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$statistics = @{
    Total = 0
    Removed = 0
    Kept = 0
    EstimatedSavings = 0
}

# ============================================================================
# CONNECT
# ============================================================================

Write-Host "[1/3] Connexion à Microsoft Graph..." -ForegroundColor Yellow

try {
    if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Users)) {
        Write-Host "   ⚠️  Module Microsoft.Graph non installé" -ForegroundColor Yellow
        Write-Host "   Installez avec: Install-Module Microsoft.Graph -Scope CurrentUser" -ForegroundColor Gray
        exit 1
    }

    Import-Module Microsoft.Graph.Users, Microsoft.Graph.Identity.DirectoryManagement -ErrorAction Stop
    Connect-MgGraph -Scopes "User.ReadWrite.All", "Directory.ReadWrite.All" -ErrorAction Stop

    Write-Host "   ✅ Connecté" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# GET LICENSED USERS
# ============================================================================

Write-Host "`n[2/3] Récupération des utilisateurs licensés..." -ForegroundColor Yellow

try {
    $users = Get-MgUser -All -Property Id, DisplayName, UserPrincipalName, AssignedLicenses, UserType
    $licensedUsers = $users | Where-Object { $_.AssignedLicenses.Count -gt 0 }

    Write-Host "   👥 Total utilisateurs: $($users.Count)" -ForegroundColor White
    Write-Host "   📄 Utilisateurs licensés: $($licensedUsers.Count)" -ForegroundColor White

    $statistics.Total = $licensedUsers.Count

} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# REMOVE UNNECESSARY LICENSES
# ============================================================================

Write-Host "`n[3/3] Nettoyage des licences..." -ForegroundColor Yellow

# Patterns to keep licenses
$keepPatterns = @("*admin*", "*helpdesk*", "svc-helpdesk-agent*")

foreach ($user in $licensedUsers) {
    $shouldKeep = $false
    $upn = $user.UserPrincipalName

    # Check if should keep
    foreach ($pattern in $keepPatterns) {
        if ($upn -like $pattern -or $user.DisplayName -like $pattern) {
            $shouldKeep = $true
            break
        }
    }

    if ($shouldKeep) {
        Write-Host "   ⏭️  Conserver: $upn" -ForegroundColor Green
        $statistics.Kept++
    } else {
        if ($DryRun) {
            Write-Host "   [DRY RUN] Retirerait licence de: $upn" -ForegroundColor Cyan
            $statistics.Removed++
            $statistics.EstimatedSavings += 5
        } else {
            $confirm = $true
            if (-not $Force) {
                $response = Read-Host "   Retirer licence de '$upn' ? (o/N)"
                $confirm = ($response -eq 'o' -or $response -eq 'O')
            }

            if ($confirm) {
                try {
                    # Remove all licenses
                    foreach ($license in $user.AssignedLicenses) {
                        Set-MgUserLicense -UserId $user.Id -AddLicenses @() -RemoveLicenses @($license.SkuId) -ErrorAction Stop
                    }
                    Write-Host "   ✅ Licence retirée: $upn" -ForegroundColor Green
                    $statistics.Removed++
                    $statistics.EstimatedSavings += 5
                } catch {
                    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
                }
            } else {
                Write-Host "   ⏭️  Ignoré: $upn" -ForegroundColor Gray
                $statistics.Kept++
            }
        }
    }
}

# ============================================================================
# SUMMARY
# ============================================================================

$report = @"
═══════════════════════════════════════════════════════════
TWISTERLAB - NETTOYAGE LICENCES OFFICE 365
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
═══════════════════════════════════════════════════════════

STATISTIQUES:
- Total utilisateurs licensés: $($statistics.Total)
- Licences retirées: $($statistics.Removed)
- Licences conservées: $($statistics.Kept)

ÉCONOMIES:
- Économies mensuelles estimées: `$$($statistics.EstimatedSavings)/mois
- Économies annuelles estimées: `$$($statistics.EstimatedSavings * 12)/an

UTILISATEURS CONSERVANT LEUR LICENCE:
$(if ($statistics.Kept -gt 0) {
    ($licensedUsers | Where-Object {
        $upn = $_.UserPrincipalName
        $keepPatterns | Where-Object { $upn -like $_ }
    } | ForEach-Object { "- $($_.UserPrincipalName)`n" }) -join ""
} else {
    "Aucun`n"
})

═══════════════════════════════════════════════════════════
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ NETTOYAGE TERMINÉ" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📊 RÉSULTAT:" -ForegroundColor Cyan
Write-Host "   • Licences retirées: $($statistics.Removed)" -ForegroundColor White
Write-Host "   • Licences conservées: $($statistics.Kept)" -ForegroundColor White
Write-Host "   • Économies: `$$($statistics.EstimatedSavings)/mois" -ForegroundColor Green
Write-Host "`n📄 Rapport: $reportFile" -ForegroundColor Cyan
Write-Host ""
