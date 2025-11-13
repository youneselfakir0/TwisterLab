param($OutputFile = "security_audit_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt")

Write-Host "=== CoreRTX Security & Health Audit ===" -ForegroundColor Cyan
Write-Host "Starting comprehensive system audit..." -ForegroundColor Yellow
Write-Host ""

# Initialize audit results
$auditResults = @{}
$complianceScore = 0
$totalChecks = 0

function Write-AuditSection {
    param($title, $status, $details = "")
    Write-Host "[$title]" -ForegroundColor Green
    Write-Host "Status: $status" -ForegroundColor $(if ($status -eq "PASS") { "Green" } elseif ($status -eq "WARNING") { "Yellow" } else { "Red" })
    if ($details) { Write-Host "Details: $details" -ForegroundColor Gray }
    Write-Host ""
}

function Add-ComplianceScore {
    param($passed, $weight = 1)
    $script:totalChecks += $weight
    if ($passed) { $script:complianceScore += $weight }
}

# 1. System Information
Write-Host "1. SYSTEM INFORMATION" -ForegroundColor Cyan
$osInfo = Get-WmiObject Win32_OperatingSystem
$computerInfo = Get-WmiObject Win32_ComputerSystem
$uptime = (Get-Date) - [Management.ManagementDateTimeConverter]::ToDateTime($osInfo.LastBootUpTime)

Write-Host "OS: $($osInfo.Caption) $($osInfo.Version)" -ForegroundColor White
Write-Host "Computer: $($computerInfo.Name)" -ForegroundColor White
Write-Host "Uptime: $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m" -ForegroundColor White
Write-Host "Architecture: $($computerInfo.SystemType)" -ForegroundColor White
Write-Host ""

# 2. Windows Updates
Write-Host "2. WINDOWS UPDATES" -ForegroundColor Cyan
try {
    # Check if Windows Update service is running updates
    $updateService = Get-Service -Name wuauserv -ErrorAction SilentlyContinue
    if ($updateService.Status -eq "Running") {
        Write-AuditSection "Windows Updates" "INFO" "Windows Update service is running - updates may be installing"
        Add-ComplianceScore $true 1  # Assume it's working if service is running
    } else {
        $updateSession = New-Object -ComObject Microsoft.Update.Session
        $updateSearcher = $updateSession.CreateUpdateSearcher()
        $searchResult = $updateSearcher.Search("IsInstalled=0")

        $criticalUpdates = $searchResult.Updates | Where-Object { $_.MsrcSeverity -eq "Critical" }
        $importantUpdates = $searchResult.Updates | Where-Object { $_.MsrcSeverity -eq "Important" }

        if ($criticalUpdates.Count -eq 0 -and $importantUpdates.Count -eq 0) {
            Write-AuditSection "Windows Updates" "PASS" "All critical and important updates installed"
            Add-ComplianceScore $true 3
        } elseif ($criticalUpdates.Count -gt 0) {
            Write-AuditSection "Windows Updates" "ERROR" "$($criticalUpdates.Count) critical updates pending"
            Add-ComplianceScore $false 3
        } else {
            Write-AuditSection "Windows Updates" "WARNING" "$($importantUpdates.Count) important updates pending"
            Add-ComplianceScore $true 2
        }
    }
} catch {
    Write-AuditSection "Windows Updates" "WARNING" "Could not check updates: $($_.Exception.Message)"
    Add-ComplianceScore $false 1
}

# 3. Firewall Status
Write-Host "3. FIREWALL STATUS" -ForegroundColor Cyan
try {
    $firewall = Get-NetFirewallProfile
    $activeProfiles = $firewall | Where-Object { $_.Enabled -eq $true }

    if ($activeProfiles.Count -ge 2) {
        Write-AuditSection "Firewall" "PASS" "Firewall enabled on $($activeProfiles.Count) profiles"
        Add-ComplianceScore $true 2
    } else {
        Write-AuditSection "Firewall" "WARNING" "Firewall not fully enabled"
        Add-ComplianceScore $false 2
    }
} catch {
    Write-AuditSection "Firewall" "ERROR" "Could not check firewall: $($_.Exception.Message)"
    Add-ComplianceScore $false 2
}

# 4. Antivirus Status
Write-Host "4. ANTIVIRUS STATUS" -ForegroundColor Cyan
try {
    $antivirus = Get-WmiObject -Namespace "root\SecurityCenter2" -Class AntiVirusProduct -ErrorAction Stop
    if ($antivirus) {
        $enabledProducts = $antivirus | Where-Object { $_.productState -band 0x1000 }
        if ($enabledProducts) {
            Write-AuditSection "Antivirus" "PASS" "$($enabledProducts.Count) antivirus products active"
            Add-ComplianceScore $true 2
        } else {
            Write-AuditSection "Antivirus" "ERROR" "No active antivirus detected"
            Add-ComplianceScore $false 2
        }
    } else {
        Write-AuditSection "Antivirus" "WARNING" "Could not retrieve antivirus information"
        Add-ComplianceScore $false 1
    }
} catch {
    Write-AuditSection "Antivirus" "WARNING" "Security Center not accessible: $($_.Exception.Message)"
    Add-ComplianceScore $false 1
}

# 5. User Accounts
Write-Host "5. USER ACCOUNTS" -ForegroundColor Cyan
$adminUsers = Get-LocalUser | Where-Object { $_.Enabled -and $_.Name -notlike "*Guest*" -and $_.Name -notlike "*Default*" }
$adminGroup = Get-LocalGroupMember -Group "Administrators" -ErrorAction SilentlyContinue

Write-Host "Total enabled users: $($adminUsers.Count)" -ForegroundColor White
Write-Host "Administrator group members:" -ForegroundColor White
$adminGroup | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }

if ($adminUsers.Count -le 3) {
    Write-AuditSection "User Accounts" "PASS" "Reasonable number of user accounts"
    Add-ComplianceScore $true 1
} else {
    Write-AuditSection "User Accounts" "WARNING" "Many user accounts detected - review for necessity"
    Add-ComplianceScore $true 1
}

# 6. Network Security
Write-Host "6. NETWORK SECURITY" -ForegroundColor Cyan
try {
    $listeningPorts = Get-NetTCPConnection | Where-Object { $_.State -eq "Listen" -and $_.LocalPort -notin @(80,443,3389,5985,5986) }
    $vulnerablePorts = @(21,23,25,53,110,135,137,138,139,445,1433,1434,3306,5432)

    Write-Host "Listening ports (excluding common):" -ForegroundColor White
    $listeningPorts | Select-Object LocalPort, OwningProcess | ForEach-Object {
        $processName = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName
        $isVulnerable = $vulnerablePorts -contains $_.LocalPort
        $color = if ($isVulnerable) { "Red" } else { "Gray" }
        Write-Host "  Port $($_.LocalPort): $processName" -ForegroundColor $color
    }

    $vulnerableListening = $listeningPorts | Where-Object { $vulnerablePorts -contains $_.LocalPort }
    if ($vulnerableListening.Count -eq 0) {
        Write-AuditSection "Network Security" "PASS" "No vulnerable ports exposed"
        Add-ComplianceScore $true 2
    } else {
        Write-AuditSection "Network Security" "WARNING" "$($vulnerableListening.Count) potentially vulnerable ports listening"
        Add-ComplianceScore $false 2
    }
} catch {
    Write-AuditSection "Network Security" "WARNING" "Could not check network ports: $($_.Exception.Message)"
    Add-ComplianceScore $false 1
}

# 7. Services Status
Write-Host "7. SERVICES STATUS" -ForegroundColor Cyan
$criticalServices = @("WinDefend", "SecurityCenter", "wscsvc", "EventLog", "RpcSs")
$runningServices = Get-Service | Where-Object { $_.Name -in $criticalServices -and $_.Status -eq "Running" }

Write-Host "Critical security services status:" -ForegroundColor White
$criticalServices | ForEach-Object {
    $service = Get-Service -Name $_ -ErrorAction SilentlyContinue
    $status = if ($service) { $service.Status } else { "Not Found" }
    $color = if ($status -eq "Running") { "Green" } else { "Red" }
    Write-Host "  $_ : $status" -ForegroundColor $color
}

if ($runningServices.Count -eq $criticalServices.Count) {
    Write-AuditSection "Services" "PASS" "All critical services running"
    Add-ComplianceScore $true 2
} else {
    Write-AuditSection "Services" "WARNING" "$($criticalServices.Count - $runningServices.Count) critical services not running"
    Add-ComplianceScore $false 2
}

# 8. Disk Usage
Write-Host "8. DISK USAGE" -ForegroundColor Cyan
$disks = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }

$disks | ForEach-Object {
    $usedPercent = [math]::Round(($_.Size - $_.FreeSpace) / $_.Size * 100, 1)
    $color = if ($usedPercent -gt 90) { "Red" } elseif ($usedPercent -gt 80) { "Yellow" } else { "Green" }
    Write-Host "Drive $($_.DeviceID): $usedPercent% used ($([math]::Round($_.FreeSpace/1GB,1))GB free)" -ForegroundColor $color
}

$fullDisks = $disks | Where-Object { (($_.Size - $_.FreeSpace) / $_.Size * 100) -gt 90 }
if ($fullDisks.Count -eq 0) {
    Write-AuditSection "Disk Usage" "PASS" "No disks critically full"
    Add-ComplianceScore $true 1
} else {
    Write-AuditSection "Disk Usage" "WARNING" "$($fullDisks.Count) disks over 90% full"
    Add-ComplianceScore $false 1
}

# 9. GPU Status (NVIDIA)
Write-Host "9. GPU STATUS" -ForegroundColor Cyan
try {
    $gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
    if ($gpu) {
        Write-Host "GPU: $($gpu.Name)" -ForegroundColor White
        Write-Host "Driver: $($gpu.DriverVersion)" -ForegroundColor White
        Write-Host "Memory: $([math]::Round($gpu.AdapterRAM/1GB,1))GB" -ForegroundColor White

        # Check for NVIDIA services
        $nvidiaServices = Get-Service | Where-Object { $_.Name -like "*nv*" -or $_.Name -like "*nvidia*" }
        $runningNvidia = $nvidiaServices | Where-Object { $_.Status -eq "Running" }

        if ($runningNvidia) {
            Write-AuditSection "GPU Status" "PASS" "NVIDIA GPU detected and services running"
            Add-ComplianceScore $true 1
        } else {
            Write-AuditSection "GPU Status" "WARNING" "NVIDIA GPU detected but services may not be running"
            Add-ComplianceScore $true 1
        }
    } else {
        Write-AuditSection "GPU Status" "INFO" "No NVIDIA GPU detected"
        Add-ComplianceScore $true 1
    }
} catch {
    Write-AuditSection "GPU Status" "WARNING" "Could not check GPU: $($_.Exception.Message)"
    Add-ComplianceScore $true 1
}

# 10. System Performance
Write-Host "10. SYSTEM PERFORMANCE" -ForegroundColor Cyan
try {
    $cpu = Get-WmiObject Win32_Processor
    $memory = Get-WmiObject Win32_OperatingSystem

    $cpuUsage = (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    $memoryUsage = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize * 100, 1)

    Write-Host "CPU Usage: $cpuUsage%" -ForegroundColor $(if ($cpuUsage -gt 80) { "Red" } elseif ($cpuUsage -gt 60) { "Yellow" } else { "Green" })
    Write-Host "Memory Usage: $memoryUsage%" -ForegroundColor $(if ($memoryUsage -gt 90) { "Red" } elseif ($memoryUsage -gt 80) { "Yellow" } else { "Green" })

    $highLoad = ($cpuUsage -gt 80) -or ($memoryUsage -gt 90)
    if (-not $highLoad) {
        Write-AuditSection "Performance" "PASS" "System performance within normal ranges"
        Add-ComplianceScore $true 1
    } else {
        Write-AuditSection "Performance" "WARNING" "High system load detected"
        Add-ComplianceScore $false 1
    }
} catch {
    Write-AuditSection "Performance" "WARNING" "Could not check performance: $($_.Exception.Message)"
    Add-ComplianceScore $false 1
}

# 11. Compliance Score
Write-Host "11. COMPLIANCE SUMMARY" -ForegroundColor Cyan
$scorePercent = [math]::Round(($complianceScore / $totalChecks) * 100, 1)

if ($scorePercent -ge 90) {
    $grade = "A"
} elseif ($scorePercent -ge 80) {
    $grade = "B"
} elseif ($scorePercent -ge 70) {
    $grade = "C"
} elseif ($scorePercent -ge 60) {
    $grade = "D"
} else {
    $grade = "F"
}

Write-Host "Compliance Score: $complianceScore / $totalChecks ($scorePercent%)" -ForegroundColor $(if ($scorePercent -ge 80) { "Green" } elseif ($scorePercent -ge 60) { "Yellow" } else { "Red" })
Write-Host "Grade: $grade" -ForegroundColor $(if ($grade -eq "A" -or $grade -eq "B") { "Green" } elseif ($grade -eq "C") { "Yellow" } else { "Red" })

# Generate report
$report = @"
CoreRTX Security & Health Audit Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
System: $($computerInfo.Name)
Uptime: $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m

COMPLIANCE SCORE: $scorePercent% (Grade: $grade)
Total Checks: $totalChecks
Passed: $complianceScore

RECOMMENDATIONS:
"@

if ($scorePercent -lt 80) {
    $report += "`n- Address failed security checks immediately"
}
if ($scorePercent -lt 90) {
    $report += "`n- Review warnings and implement improvements"
}
$report += "`n- Schedule regular audits (monthly recommended)"

$report | Out-File -FilePath $OutputFile -Encoding UTF8
Write-Host "`nReport saved to: $OutputFile" -ForegroundColor Green
Write-Host "Audit completed successfully!" -ForegroundColor Green