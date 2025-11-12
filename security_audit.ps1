#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Comprehensive security audit for TwisterLab production system
.DESCRIPTION
    Performs security assessment including:
    - Credential security validation
    - Network security checks
    - Access control verification
    - Vulnerability scanning
    - Compliance checks
.NOTES
    Run as Administrator
    Requires: Windows security tools, network access
#>

param(
    [switch]$QuickScan = $false,
    [string]$ReportPath = "C:\TwisterLab\security_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
)

$AuditResults = @{
    Passed = 0
    Failed = 0
    Warnings = 0
    Critical = 0
}

function Write-AuditLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $ReportPath -Value $logMessage
}

function Write-AuditHeader {
    param([string]$Title)
    $header = "=" * 60
    $logMessage = "`n$header`n$Title`n$header"
    Write-Host $logMessage
    Add-Content -Path $ReportPath -Value $logMessage
}

function Test-AuditResult {
    param([string]$TestName, [bool]$Result, [string]$Details = "", [string]$Severity = "INFO")

    if ($Result) {
        Write-AuditLog "✅ PASS: $TestName" "PASS"
        $AuditResults.Passed++
    } else {
        $level = switch ($Severity) {
            "CRITICAL" { "CRITICAL"; $AuditResults.Critical++ }
            "WARNING" { "WARNING"; $AuditResults.Warnings++ }
            default { "FAIL"; $AuditResults.Failed++ }
        }
        Write-AuditLog "❌ $level`: $TestName" $level
    }

    if ($Details) {
        Write-AuditLog "   Details: $Details" "INFO"
    }
}

function Test-CredentialSecurity {
    Write-AuditHeader "CREDENTIAL SECURITY AUDIT"

    # Check for plaintext credentials in config files
    Write-AuditLog "Checking for plaintext credentials in configuration files..."

    $configFiles = @(
        "docker-compose*.yml",
        "*.env",
        "*.json",
        "*.py",
        "*.ps1"
    )

    $plaintextPatterns = @(
        'password.*=.*[^$]',
        'secret.*=.*[^$]',
        'key.*=.*[^$]',
        'token.*=.*[^$]'
    )

    $foundPlaintext = $false
    foreach ($pattern in Get-ChildItem -Path "C:\TwisterLab" -Include $configFiles -Recurse -File) {
        $content = Get-Content $pattern.FullName -Raw
        foreach ($credPattern in $plaintextPatterns) {
            if ($content -match $credPattern) {
                $foundPlaintext = $true
                Test-AuditResult "Plaintext credentials check" $false "Found potential plaintext credentials in $($pattern.Name)" "CRITICAL"
                break
            }
        }
    }

    if (!$foundPlaintext) {
        Test-AuditResult "Plaintext credentials check" $true "No plaintext credentials found in configuration files"
    }

    # Check vault directory encryption
    $vaultPath = "C:\TwisterLab\vault"
    if (Test-Path $vaultPath) {
        $vaultFiles = Get-ChildItem $vaultPath -File
        $encryptedFiles = $vaultFiles | Where-Object { $_.Extension -eq ".enc" }
        $plaintextFiles = $vaultFiles | Where-Object { $_.Extension -ne ".enc" }

        Test-AuditResult "Vault encryption" ($plaintextFiles.Count -eq 0) "Found $($encryptedFiles.Count) encrypted files, $($plaintextFiles.Count) plaintext files in vault"

        if ($plaintextFiles.Count -gt 0) {
            foreach ($file in $plaintextFiles) {
                Write-AuditLog "   WARNING: Plaintext file in vault: $($file.Name)" "WARNING"
            }
        }
    } else {
        Test-AuditResult "Vault directory exists" $false "Vault directory not found" "CRITICAL"
    }

    # Check credential access logging
    $logFiles = Get-ChildItem "C:\TwisterLab\logs" -Filter "*.log" -File -ErrorAction SilentlyContinue
    $credentialAccessLogged = $false
    foreach ($logFile in $logFiles) {
        $content = Get-Content $logFile.FullName -Raw
        if ($content -match "credential.*access|access.*credential") {
            $credentialAccessLogged = $true
            break
        }
    }
    Test-AuditResult "Credential access logging" $credentialAccessLogged "Credential access operations are logged"
}

function Test-NetworkSecurity {
    Write-AuditHeader "NETWORK SECURITY AUDIT"

    # Check firewall status
    $firewallProfiles = Get-NetFirewallProfile
    $firewallEnabled = $true
    foreach ($profile in $firewallProfiles) {
        if ($profile.Enabled -eq "False") {
            $firewallEnabled = $false
            break
        }
    }
    Test-AuditResult "Windows Firewall enabled" $firewallEnabled "All firewall profiles are enabled"

    # Check open ports
    Write-AuditLog "Checking for open ports..."
    $openPorts = netstat -ano | Where-Object { $_ -match "LISTENING" -and $_ -notmatch "^Active|^Proto" } | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^(\S+)\s+(\S+:\d+)\s+(\S+:\d+)\s+(\S+)\s+(\d+)$') {
            [PSCustomObject]@{
                Protocol = $matches[1]
                LocalAddress = $matches[2]
                ForeignAddress = $matches[3]
                State = $matches[4]
                PID = $matches[5]
            }
        }
    }

    $criticalPorts = @(21, 23, 25, 53, 110, 143, 993, 995, 3389)  # FTP, Telnet, SMTP, DNS, POP3, IMAP, etc.
    $exposedCriticalPorts = $false

    foreach ($port in $openPorts) {
        if ($port -and $port.LocalAddress) {
            try {
                $addressParts = $port.LocalAddress -split ':'
                if ($addressParts.Count -gt 1) {
                    $portNumber = [int]$addressParts[-1]
                    if ($criticalPorts -contains $portNumber) {
                        $exposedCriticalPorts = $true
                        Write-AuditLog "   WARNING: Critical port $portNumber is open" "WARNING"
                    }
                }
            } catch {
                Write-AuditLog "   ERROR: Failed to parse port from $($port.LocalAddress): $($_.Exception.Message)" "ERROR"
            }
        }
    }

    Test-AuditResult "Critical ports protection" (!$exposedCriticalPorts) "No critical ports exposed to external access"

    # Check Docker network isolation
    $dockerNetworks = docker network ls --format "{{.Name}}"
    $isolatedNetworks = $dockerNetworks | Where-Object { $_ -match "twisterlab" }
    Test-AuditResult "Docker network isolation" ($isolatedNetworks.Count -gt 0) "Found $($isolatedNetworks.Count) isolated Docker networks"

    # Check for exposed Docker ports
    $exposedContainers = docker ps --format "{{.Names}}:{{.Ports}}" | Where-Object { $_ -match "0\.0\.0\.0:" }
    Test-AuditResult "Docker port exposure" ($exposedContainers.Count -eq 0) "No containers exposing ports to 0.0.0.0"
}

function Test-AccessControl {
    Write-AuditHeader "ACCESS CONTROL AUDIT"

    # Check administrator privileges
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    Test-AuditResult "Running as administrator" $isAdmin "Audit running with administrator privileges"

    # Check service account permissions
    $twisterlabService = Get-WmiObject -Class Win32_Service -Filter "Name='TwisterLabAPI'"
    if ($twisterlabService) {
        $serviceAccount = $twisterlabService.StartName
        Test-AuditResult "Service account security" ($serviceAccount -ne "LocalSystem") "Service running as: $serviceAccount"
    } else {
        Test-AuditResult "API service exists" $false "TwisterLab API service not found" "WARNING"
    }

    # Check file permissions on sensitive directories
    $sensitivePaths = @(
        "C:\TwisterLab\vault",
        "C:\TwisterLab\logs",
        "C:\TwisterLab\backups"
    )

    foreach ($path in $sensitivePaths) {
        if (Test-Path $path) {
            $acl = Get-Acl $path
            $unauthorizedAccess = $false

            foreach ($access in $acl.Access) {
                if ($access.IdentityReference -match "Everyone|Users" -and $access.FileSystemRights -match "FullControl|Modify") {
                    $unauthorizedAccess = $true
                    break
                }
            }

            Test-AuditResult "Permissions on $path" (!$unauthorizedAccess) "Directory permissions are properly restricted"
        }
    }

    # Check for unauthorized shares
    $shares = Get-WmiObject -Class Win32_Share
    $sensitiveShares = $shares | Where-Object { $_.Name -match "TwisterLab|vault|backup" }
    Test-AuditResult "Unauthorized shares" ($sensitiveShares.Count -eq 0) "No sensitive directories shared on network"
}

function Test-SystemSecurity {
    Write-AuditHeader "SYSTEM SECURITY AUDIT"

    # Check Windows Defender status
    $defenderStatus = Get-MpComputerStatus -ErrorAction SilentlyContinue
    if ($defenderStatus) {
        $defenderEnabled = $defenderStatus.RealTimeProtectionEnabled
        Test-AuditResult "Windows Defender enabled" $defenderEnabled "Real-time protection is active"
    } else {
        Test-AuditResult "Windows Defender status" $false "Unable to check Windows Defender status" "WARNING"
    }

    # Check for pending Windows updates
    $updateSession = New-Object -ComObject Microsoft.Update.Session
    $updateSearcher = $updateSession.CreateUpdateSearcher()
    $pendingUpdates = $updateSearcher.Search("IsInstalled=0").Updates.Count
    Test-AuditResult "Windows updates" ($pendingUpdates -eq 0) "Found $pendingUpdates pending updates"

    # Check system logs for security events
    $securityEvents = Get-WinEvent -LogName Security -MaxEvents 100 -ErrorAction SilentlyContinue |
        Where-Object { $_.Id -in @(4625, 4624, 4672, 4720, 4728) }  # Failed/Successful logins, privilege escalation, user creation/modification

    $recentSecurityEvents = $securityEvents | Where-Object { $_.TimeCreated -gt (Get-Date).AddHours(-24) }
    Test-AuditResult "Security event monitoring" ($recentSecurityEvents.Count -gt 0) "Found $($recentSecurityEvents.Count) security events in last 24 hours"

    # Check for suspicious processes
    $suspiciousProcesses = Get-Process | Where-Object {
        $_.ProcessName -match "keylogger|trojan|ransomware|miner" -or
        $_.Path -match "temp|tmp" -and $_.CPU -gt 50
    }
    Test-AuditResult "Suspicious processes" ($suspiciousProcesses.Count -eq 0) "Found $($suspiciousProcesses.Count) suspicious processes"
}

function Test-Compliance {
    Write-AuditHeader "COMPLIANCE AUDIT"

    # Check encryption standards
    $encryptionCheck = $true
    $vaultFiles = Get-ChildItem "C:\TwisterLab\vault\*.enc" -ErrorAction SilentlyContinue
    if ($vaultFiles) {
        # Basic check for Fernet encryption (starts with gAAAAA)
        foreach ($file in $vaultFiles) {
            $content = Get-Content $file.FullName -Raw
            if ($content -notmatch "^gAAAAA") {
                $encryptionCheck = $false
                break
            }
        }
    }
    Test-AuditResult "Encryption standards" $encryptionCheck "Credentials encrypted with Fernet cipher"

    # Check audit logging
    $logFiles = Get-ChildItem "C:\TwisterLab\logs\*.log" -ErrorAction SilentlyContinue
    $auditLogging = $logFiles.Count -gt 0
    if ($auditLogging) {
        $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $hoursSinceLastLog = ((Get-Date) - $latestLog.LastWriteTime).TotalHours
        $auditLogging = $hoursSinceLastLog -lt 24
    }
    Test-AuditResult "Audit logging active" $auditLogging "System audit logs are current"

    # Check backup compliance
    $backupDir = "C:\TwisterLab\backups"
    if (Test-Path $backupDir) {
        $recentBackups = Get-ChildItem $backupDir -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
        Test-AuditResult "Regular backups" ($recentBackups.Count -gt 0) "Found $($recentBackups.Count) backups in last 7 days"
    } else {
        Test-AuditResult "Backup directory exists" $false "Backup directory not found" "CRITICAL"
    }
}

function Test-ContainerSecurity {
    Write-AuditHeader "CONTAINER SECURITY AUDIT"

    # Check Docker daemon security
    $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
    Test-AuditResult "Docker version check" ($dockerVersion -match "^2[0-9]\.") "Docker version: $dockerVersion"

    # Check for privileged containers
    $privilegedContainers = docker ps --quiet | ForEach-Object {
        docker inspect $_ --format "{{.Name}}: {{.HostConfig.Privileged}}"
    } | Where-Object { $_ -match "true$" }

    Test-AuditResult "Privileged containers" ($privilegedContainers.Count -eq 0) "Found $($privilegedContainers.Count) privileged containers"

    # Check for root user containers
    $rootContainers = docker ps --quiet | ForEach-Object {
        docker exec $_ whoami 2>$null
    } | Where-Object { $_ -eq "root" }

    Test-AuditResult "Root user containers" ($rootContainers.Count -eq 0) "Found $($rootContainers.Count) containers running as root"

    # Check image vulnerabilities (basic check)
    $images = docker images --format "{{.Repository}}:{{.Tag}}"
    $outdatedImages = @()
    foreach ($image in $images) {
        if ($image -match "latest|<none>") {
            $outdatedImages += $image
        }
    }
    Test-AuditResult "Container image updates" ($outdatedImages.Count -eq 0) "Found $($outdatedImages.Count) potentially outdated images"
}

function Show-AuditSummary {
    Write-AuditHeader "AUDIT SUMMARY"

    $totalTests = $AuditResults.Passed + $AuditResults.Failed + $AuditResults.Warnings + $AuditResults.Critical

    Write-AuditLog "Total Tests Run: $totalTests"
    Write-AuditLog "✅ Passed: $($AuditResults.Passed)"
    Write-AuditLog "❌ Failed: $($AuditResults.Failed)"
    Write-AuditLog "⚠️  Warnings: $($AuditResults.Warnings)"
    Write-AuditLog "🚨 Critical: $($AuditResults.Critical)"

    $passRate = [math]::Round(($AuditResults.Passed / $totalTests) * 100, 1)
    Write-AuditLog "Pass Rate: $passRate%"

    # Overall assessment
    if ($AuditResults.Critical -eq 0 -and $AuditResults.Failed -eq 0 -and $passRate -ge 90) {
        Write-AuditLog "OVERALL ASSESSMENT: ✅ SECURE" "PASS"
    } elseif ($AuditResults.Critical -eq 0 -and $passRate -ge 75) {
        Write-AuditLog "OVERALL ASSESSMENT: ⚠️ REQUIRES ATTENTION" "WARNING"
    } else {
        Write-AuditLog "OVERALL ASSESSMENT: 🚨 SECURITY ISSUES FOUND" "CRITICAL"
    }

    Write-AuditLog "`nReport saved to: $ReportPath"
}

# Main audit process
try {
    Write-AuditLog "=== TwisterLab Security Audit Started ==="
    Write-AuditLog "Report Path: $ReportPath"
    Write-AuditLog "Quick Scan: $QuickScan"

    # Run all security checks
    Test-CredentialSecurity
    Test-NetworkSecurity
    Test-AccessControl
    Test-SystemSecurity

    if (!$QuickScan) {
        Test-Compliance
        Test-ContainerSecurity
    }

    # Generate summary
    Show-AuditSummary

    Write-AuditLog "=== Security Audit Completed ==="

    # Display results
    Write-Host "`nSecurity Audit Results:" -ForegroundColor Cyan
    Write-Host "Total Tests: $($AuditResults.Passed + $AuditResults.Failed + $AuditResults.Warnings + $AuditResults.Critical)" -ForegroundColor White
    Write-Host "Passed: $($AuditResults.Passed)" -ForegroundColor Green
    Write-Host "Failed: $($AuditResults.Failed)" -ForegroundColor Red
    Write-Host "Warnings: $($AuditResults.Warnings)" -ForegroundColor Yellow
    Write-Host "Critical: $($AuditResults.Critical)" -ForegroundColor Magenta

    $totalTests = $AuditResults.Passed + $AuditResults.Failed + $AuditResults.Warnings + $AuditResults.Critical
    $passRate = [math]::Round(($AuditResults.Passed / $totalTests) * 100, 1)

    if ($AuditResults.Critical -eq 0 -and $AuditResults.Failed -eq 0) {
        Write-Host "Security Status: EXCELLENT ($passRate% pass rate)" -ForegroundColor Green
    } elseif ($AuditResults.Critical -eq 0) {
        Write-Host "Security Status: GOOD ($passRate% pass rate)" -ForegroundColor Yellow
    } else {
        Write-Host "Security Status: REQUIRES IMMEDIATE ATTENTION ($passRate% pass rate)" -ForegroundColor Red
    }

    Write-Host "Detailed report: $ReportPath" -ForegroundColor Cyan

    exit 0
}
catch {
    Write-AuditLog "Security audit failed: $($_.Exception.Message)" "ERROR"
    exit 1
}
