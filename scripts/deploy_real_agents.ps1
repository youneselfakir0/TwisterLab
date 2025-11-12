# Deploy Real Agents to edgeserver Docker Container
# Copies agents/real/ to production container

Write-Host "`n[DEPLOY] REAL AGENTS TO EDGESERVER`n" -ForegroundColor Cyan

$edgeserver = "192.168.0.30"
$container = "twisterlab_api"

# Check edgeserver connectivity
Write-Host "[CHECK] Edgeserver connectivity..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $edgeserver -Count 1 -Quiet
if (-not $ping) {
    Write-Host "[ERROR] Cannot reach edgeserver ($edgeserver)" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Edgeserver accessible" -ForegroundColor Green

# Check if container exists
Write-Host "`n[CHECK] Docker container..." -ForegroundColor Yellow
$containerCheck = ssh root@$edgeserver "docker ps --filter name=$container --format '{{.Names}}'"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($containerCheck)) {
    Write-Host "❌ Container $container not found on edgeserver" -ForegroundColor Red
    Write-Host "Available containers:" -ForegroundColor Yellow
    ssh root@$edgeserver "docker ps --format 'table {{.Names}}\t{{.Status}}'"
    exit 1
}
Write-Host "✅ Container found: $containerCheck" -ForegroundColor Green

# Create temporary archive of real agents
Write-Host "`n📦 Creating agents archive..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archivePath = "agents_real_$timestamp.tar.gz"

if (Get-Command tar -ErrorAction SilentlyContinue) {
    tar -czf $archivePath -C agents real/
} else {
    # Fallback: Use PowerShell Compress-Archive
    $tempDir = "temp_agents_$timestamp"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    Copy-Item -Path "agents\real" -Destination $tempDir -Recurse
    Compress-Archive -Path "$tempDir\*" -DestinationPath "$archivePath.zip"
    Remove-Item -Path $tempDir -Recurse -Force
    $archivePath = "$archivePath.zip"
}

if (Test-Path $archivePath) {
    $size = (Get-Item $archivePath).Length / 1KB
    Write-Host "✅ Archive created: $archivePath ($([math]::Round($size, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create archive" -ForegroundColor Red
    exit 1
}

# Copy archive to edgeserver
Write-Host "`n📤 Copying archive to edgeserver..." -ForegroundColor Yellow
scp $archivePath root@${edgeserver}:/tmp/
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to copy archive" -ForegroundColor Red
    Remove-Item $archivePath -Force
    exit 1
}
Write-Host "✅ Archive copied to edgeserver:/tmp/" -ForegroundColor Green

# Extract in container
Write-Host "`n📂 Extracting agents in container..." -ForegroundColor Yellow

$deployScript = @"
# Extract archive
cd /tmp
if [ -f '$archivePath' ]; then
    tar -xzf $archivePath -C /opt/twisterlab/agents/ 2>/dev/null || unzip -q $archivePath -d /opt/twisterlab/agents/
fi

# Verify extraction
if [ -d /opt/twisterlab/agents/real ]; then
    echo "✅ Agents extracted successfully"
    ls -lh /opt/twisterlab/agents/real/
else
    echo "❌ Extraction failed"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --quiet psutil redis

# Cleanup
rm -f /tmp/$archivePath

echo ""
echo "✅ Deployment complete"
"@

ssh root@$edgeserver "docker exec $container bash -c '$deployScript'"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ AGENTS DEPLOYED SUCCESSFULLY" -ForegroundColor Green
} else {
    Write-Host "`n❌ Deployment failed" -ForegroundColor Red
    Remove-Item $archivePath -Force
    exit 1
}

# Cleanup local archive
Remove-Item $archivePath -Force

# Update orchestrator
Write-Host "`n🔄 Updating autonomous_orchestrator.py..." -ForegroundColor Yellow
scp deploy/agents/orchestrator/autonomous_orchestrator.py root@${edgeserver}:/tmp/
ssh root@$edgeserver "docker cp /tmp/autonomous_orchestrator.py ${container}:/opt/twisterlab/deploy/agents/orchestrator/autonomous_orchestrator.py"

# Restart API to load new agents
Write-Host "`n🔄 Restarting API to load new agents..." -ForegroundColor Yellow
ssh root@$edgeserver "docker exec $container pkill -f 'uvicorn' || true"
ssh root@$edgeserver "docker service update --force twisterlab_api"

Write-Host "`n⏳ Waiting for service restart (10s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verify agents loaded
Write-Host "`n🔍 Verifying agents..." -ForegroundColor Yellow
$apiCheck = Invoke-RestMethod -Uri "http://${edgeserver}:8000/health" -Method GET -ErrorAction SilentlyContinue

if ($apiCheck) {
    Write-Host "✅ API is responsive" -ForegroundColor Green

    # Test agent endpoint
    try {
        $agentTest = Invoke-RestMethod -Uri "http://${edgeserver}:8000/agents/monitoring/execute" -Method POST -Body (@{operation="health_check"} | ConvertTo-Json) -ContentType "application/json"

        if ($agentTest.status -eq "success") {
            Write-Host "✅ Real agents are working!" -ForegroundColor Green
            Write-Host "   CPU: $($agentTest.health_check.cpu_percent)%" -ForegroundColor White
            Write-Host "   Memory: $($agentTest.health_check.memory_percent)%" -ForegroundColor White
        }
    } catch {
        Write-Host "⚠️  Agent test failed, but deployment successful" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  API not responding yet (may need more time)" -ForegroundColor Yellow
}

Write-Host "`n" -NoNewline
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "`n  Real agents deployed to: $container@$edgeserver" -ForegroundColor White
Write-Host "  API endpoint: http://${edgeserver}:8000" -ForegroundColor White
Write-Host "`n  Test agent:" -ForegroundColor Yellow
Write-Host "  curl http://${edgeserver}:8000/agents/monitoring/execute -X POST -H 'Content-Type: application/json' -d '{`"operation`":`"health_check`"}'" -ForegroundColor Gray
Write-Host "`n=========================================================`n" -ForegroundColor Cyan
