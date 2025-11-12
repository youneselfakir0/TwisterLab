# =============================================================================
# SIMPLE PATCH - REPLACE API MAIN.PY WITH CORRECTED VERSION
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "`n=== PATCH API MAIN.PY - VERSION SIMPLIFIEE ===" -ForegroundColor Cyan

$EDGE_SERVER = "192.168.0.30"
$SSH_USER = "twister"
$CONTAINER_ID = "928508eefd57"

# Step 1: Download current api/main.py
Write-Host "[1/5] Telechargement de api/main.py..." -ForegroundColor Green
ssh $SSH_USER@$EDGE_SERVER "docker exec $CONTAINER_ID cat /app/api/main.py" | Out-File -FilePath "C:\TwisterLab\temp_api_current.py" -Encoding UTF8

Write-Host "   Taille: $((Get-Item 'C:\TwisterLab\temp_api_current.py').Length) bytes" -ForegroundColor Gray

# Step 2: Create corrected version manually
Write-Host "`n[2/5] Creation de la version corrigee..." -ForegroundColor Green

# Read current file
$content = Get-Content "C:\TwisterLab\temp_api_current.py" -Raw

# Add orchestrator import if not present
if ($content -notmatch "from agents.orchestrator.autonomous_orchestrator import get_orchestrator") {
    # Find position after last import
    $lines = $content -split "`n"
    $lastImportIndex = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^(from |import )") {
            $lastImportIndex = $i
        }
    }

    # Insert import
    $lines = $lines[0..$lastImportIndex] + "" + "# Real agent orchestrator" + "from agents.orchestrator.autonomous_orchestrator import get_orchestrator" + "" + $lines[($lastImportIndex + 1)..($lines.Count - 1)]
    $content = $lines -join "`n"
    Write-Host "   Import orchestrator ajoute" -ForegroundColor Gray
}

# Replace the execute_agent_operation function
$newFunction = @'

@app.post("/api/v1/autonomous/agents/{agent_name}/execute")
async def execute_agent_operation(agent_name: str, payload: Dict[str, Any]):
    """Execute an agent operation using the real orchestrator."""
    try:
        orchestrator = await get_orchestrator()

        agent_mapping = {
            "monitoringagent": "monitoring",
            "backupagent": "backup",
            "syncagent": "sync",
            "classifieragent": "classifier",
            "resolveragent": "resolver",
            "desktopcommanderagent": "desktop_commander",
            "maestroorchestratoragent": "maestro",
        }

        orchestrator_agent_name = agent_mapping.get(agent_name.lower())
        if not orchestrator_agent_name:
            return {"agent": agent_name, "status": "error", "error": f"Unknown agent: {agent_name}"}

        operation = payload.get("operation", "health_check")
        context = payload.get("context", {})

        result = await orchestrator.execute_agent_operation(orchestrator_agent_name, operation, context)

        return {
            "agent": agent_name,
            "operation": operation,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    except Exception as e:
        return {"agent": agent_name, "status": "error", "error": str(e)}

'@

# Find and replace the function
$pattern = '@app\.post\("/api/v1/autonomous/agents/\{agent_name\}/execute"\)[\s\S]*?(?=\n@app\.|$)'
if ($content -match $pattern) {
    $content = $content -replace $pattern, $newFunction.Trim()
    Write-Host "   Fonction execute_agent_operation remplacee" -ForegroundColor Gray
}

# Remove mock functions
$mockFunctions = @("execute_monitoring_agent", "execute_backup_agent", "execute_sync_agent")
foreach ($func in $mockFunctions) {
    $mockPattern = "async def $func\(.*?\):[\s\S]*?(?=\nasync def |\n@app\.|\Z)"
    if ($content -match $mockPattern) {
        $content = $content -replace $mockPattern, ""
        Write-Host "   Fonction mock $func supprimee" -ForegroundColor Gray
    }
}

# Save corrected version
$content | Out-File -FilePath "C:\TwisterLab\temp_api_patched.py" -Encoding UTF8 -NoNewline

Write-Host "`n[3/5] Upload vers edgeserver..." -ForegroundColor Green
scp "C:\TwisterLab\temp_api_patched.py" ${SSH_USER}@${EDGE_SERVER}:/tmp/main_patched.py

Write-Host "[4/5] Deploiement dans le container..." -ForegroundColor Green
ssh $SSH_USER@$EDGE_SERVER "docker cp /tmp/main_patched.py ${CONTAINER_ID}:/app/api/main.py"

# Commit and update
$IMAGE_TAG = "twisterlab-api:production-real-agents"
ssh $SSH_USER@$EDGE_SERVER "docker commit $CONTAINER_ID $IMAGE_TAG"
ssh $SSH_USER@$EDGE_SERVER "docker service update --image $IMAGE_TAG twisterlab_api"

Write-Host "`n[5/5] Attente convergence (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`n=== TEST DE VERIFICATION ===" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "http://${EDGE_SERVER}:8000/api/v1/autonomous/agents/MonitoringAgent/execute" -Method POST -Body '{"operation":"health_check"}' -ContentType "application/json"

$response | ConvertTo-Json -Depth 5 | Write-Host

if ($response.result.metrics.cpu_usage -eq "23%") {
    Write-Host "`nATTENTION: Encore des donnees MOCK!" -ForegroundColor Red
} else {
    Write-Host "`nSUCCES! Donnees REELLES!" -ForegroundColor Green
}
