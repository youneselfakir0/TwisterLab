#Requires -RunAsAdministrator

# PowerShell script to configure local DNS for TwisterLab
# Run this script as Administrator to update the hosts file

Write-Host "🔧 Configuring DNS for TwisterLab..." -ForegroundColor Green

# Get Traefik container IP from the production network
try {
    $traefikContainer = docker ps --filter "name=twisterlab_prod_traefik" --format "{{.Names}}"
    if ($traefikContainer) {
        $traefikIP = docker inspect $traefikContainer | ConvertFrom-Json | Select-Object -ExpandProperty NetworkSettings -ExpandProperty Networks -ExpandProperty twisterlab_prod | Select-Object -ExpandProperty IPAddress
        Write-Host "✅ Found Traefik container at IP: $traefikIP" -ForegroundColor Green
    } else {
        Write-Host "❌ Traefik container not found. Using default IP..." -ForegroundColor Yellow
        # Try to get from service
        $traefikIP = docker service ps twisterlab_prod_traefik --format "{{.Node}}" | Select-Object -First 1
        if ($traefikIP) {
            # Get node IP
            $nodeIP = docker node inspect $traefikIP --format "{{.Status.Addr}}"
            $traefikIP = $nodeIP
            Write-Host "✅ Using Traefik node IP: $traefikIP" -ForegroundColor Green
        } else {
            Write-Host "❌ Could not determine Traefik IP. Using localhost..." -ForegroundColor Yellow
            $traefikIP = "127.0.0.1"
        }
    }
} catch {
    Write-Host "❌ Error getting Traefik IP: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Using localhost as fallback..." -ForegroundColor Yellow
    $traefikIP = "127.0.0.1"
}

# Hosts file path
$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$backupPath = "$hostsPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "📝 Updating hosts file: $hostsPath" -ForegroundColor Blue

# Create backup
try {
    Copy-Item $hostsPath $backupPath -Force
    Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create backup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Read current hosts file
try {
    $hostsContent = Get-Content $hostsPath -ErrorAction Stop
} catch {
    Write-Host "❌ Failed to read hosts file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Remove existing twisterlab entries
$hostsContent = $hostsContent | Where-Object { $_ -notmatch "twisterlab\.local" }

# Add new entries
$twisterlabEntries = @(
    "$traefikIP api.twisterlab.local",
    "$traefikIP webui.twisterlab.local",
    "$traefikIP traefik.twisterlab.local",
    "$traefikIP grafana.twisterlab.local",
    "$traefikIP prometheus.twisterlab.local",
    "$traefikIP jaeger.twisterlab.local"
)

$hostsContent += $twisterlabEntries

# Write back to hosts file
try {
    $hostsContent | Out-File -FilePath $hostsPath -Encoding ASCII -Force
    Write-Host "✅ Hosts file updated successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to write hosts file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Display added entries
Write-Host "`n📋 Added DNS entries:" -ForegroundColor Cyan
foreach ($entry in $twisterlabEntries) {
    Write-Host "   $entry" -ForegroundColor White
}

# Test the configuration
Write-Host "`n🧪 Testing DNS configuration..." -ForegroundColor Blue

$testUrls = @(
    "http://api.twisterlab.local/health",
    "http://webui.twisterlab.local",
    "http://traefik.twisterlab.local"
)

foreach ($url in $testUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ $url - Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $url - Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nDNS configuration complete!" -ForegroundColor Green
Write-Host "You can now access TwisterLab services using the *.twisterlab.local domains" -ForegroundColor White
Write-Host "`nExample URLs:" -ForegroundColor Cyan
Write-Host "  API: http://api.twisterlab.local/api/v1/autonomous/status" -ForegroundColor White
Write-Host "  WebUI: http://webui.twisterlab.local" -ForegroundColor White
Write-Host "  Traefik Dashboard: http://traefik.twisterlab.local" -ForegroundColor White
