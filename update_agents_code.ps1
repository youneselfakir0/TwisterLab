# Update TwisterLab agents with LLM + metrics (direct container copy)
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"
$Container = "twisterlab_api.1.ewoh8iji9lurmghblkiykda2z"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UPDATING AGENTS CODE (Direct Copy)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Copy new metrics module
Write-Host "`n[1/5] Copying metrics.py..." -ForegroundColor Yellow
scp agents/metrics.py "${EdgeUser}@${EdgeServer}:/tmp/metrics.py"
ssh ${EdgeUser}@${EdgeServer} "docker cp /tmp/metrics.py ${Container}:/app/agents/metrics.py"
Write-Host "OK - metrics.py copied" -ForegroundColor Green

# Step 2: Copy updated ClassifierAgent
Write-Host "`n[2/5] Copying real_classifier_agent.py..." -ForegroundColor Yellow
scp agents/real/real_classifier_agent.py "${EdgeUser}@${EdgeServer}:/tmp/real_classifier_agent.py"
ssh ${EdgeUser}@${EdgeServer} "docker cp /tmp/real_classifier_agent.py ${Container}:/app/agents/real/real_classifier_agent.py"
Write-Host "OK - ClassifierAgent updated" -ForegroundColor Green

# Step 3: Copy config.py (LLM settings)
Write-Host "`n[3/5] Copying config.py..." -ForegroundColor Yellow
scp agents/config.py "${EdgeUser}@${EdgeServer}:/tmp/config.py"
ssh ${EdgeUser}@${EdgeServer} "docker cp /tmp/config.py ${Container}:/app/agents/config.py"
Write-Host "OK - config.py updated" -ForegroundColor Green

# Step 4: Copy LLM client
Write-Host "`n[4/5] Copying llm_client.py..." -ForegroundColor Yellow
scp agents/base/llm_client.py "${EdgeUser}@${EdgeServer}:/tmp/llm_client.py"
ssh ${EdgeUser}@${EdgeServer} "docker cp /tmp/llm_client.py ${Container}:/app/agents/base/llm_client.py"
Write-Host "OK - llm_client.py updated" -ForegroundColor Green

# Step 5: Restart container
Write-Host "`n[5/5] Restarting API container..." -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "docker service update --force twisterlab_api"
Write-Host "OK - Container restarting" -ForegroundColor Green

# Wait for restart
Write-Host "`nWaiting for API restart (20s)..." -ForegroundColor Gray
Start-Sleep -Seconds 20

# Health check
$apiUrl = "http://${EdgeServer}:8000/health"
try {
    $health = Invoke-RestMethod -Uri $apiUrl -TimeoutSec 10
    Write-Host "`nOK - API is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "`nWARNING - API not responding yet" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CODE UPDATE COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nUpdated files:"
Write-Host "  - agents/metrics.py (NEW)"
Write-Host "  - agents/config.py (LLM config)"
Write-Host "  - agents/base/llm_client.py (Ollama client)"
Write-Host "  - agents/real/real_classifier_agent.py (metrics integrated)"
Write-Host "`nNext: Test LLM classification and check metrics"
Write-Host ""
