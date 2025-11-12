#Requires -RunAsAdministrator

Write-Host "Configuring DNS for TwisterLab..." -ForegroundColor Green

# Get container IPs
$apiIP = docker inspect twisterlab_prod_traefik | ConvertFrom-Json | Select-Object -ExpandProperty NetworkSettings -ExpandProperty Networks -ExpandProperty twisterlab_prod | Select-Object -ExpandProperty IPAddress
if (-not $apiIP) { $apiIP = "127.0.0.1" }

# Hosts file path
$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$backupPath = "$hostsPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Create backup
Copy-Item $hostsPath $backupPath -Force
Write-Host "Backup created: $backupPath" -ForegroundColor Green

# Read current hosts
$hostsContent = Get-Content $hostsPath

# Remove existing twisterlab entries
$hostsContent = $hostsContent | Where-Object { $_ -notmatch "twisterlab\.local" }

# Add new entries
$hostsContent += "$apiIP api.twisterlab.local"
$hostsContent += "$apiIP webui.twisterlab.local"
$hostsContent += "$apiIP traefik.twisterlab.local"
$hostsContent += "$apiIP grafana.twisterlab.local"
$hostsContent += "$apiIP prometheus.twisterlab.local"

# Write back
$hostsContent | Out-File -FilePath $hostsPath -Encoding ASCII -Force
Write-Host "DNS configuration updated successfully!" -ForegroundColor Green

# Test configuration
Write-Host "`nTesting DNS resolution..." -ForegroundColor Cyan
$domains = @("api.twisterlab.local", "webui.twisterlab.local", "traefik.twisterlab.local")
foreach ($domain in $domains) {
    try {
        $result = Resolve-DnsName $domain -ErrorAction Stop
        Write-Host "  $domain -> $($result.IPAddress)" -ForegroundColor Green
    } catch {
        Write-Host "  $domain -> FAILED" -ForegroundColor Red
    }
}

Write-Host "`nDNS configuration complete!" -ForegroundColor Green
