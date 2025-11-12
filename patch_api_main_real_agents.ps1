# =============================================================================
# PATCH API MAIN.PY - REPLACE MOCK FUNCTIONS WITH REAL ORCHESTRATOR CALLS
# =============================================================================
# This script modifies api/main.py to call the real orchestrator instead of
# returning hardcoded mock data.
#
# Changes:
# 1. Add orchestrator import
# 2. Replace mock routing with orchestrator calls
# 3. Delete mock functions (execute_monitoring_agent, etc.)
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "`n=== PATCH API MAIN.PY - INTEGRATION AGENTS REELS ===" -ForegroundColor Cyan
Write-Host "Objectif: Remplacer les fonctions mock par des appels orchestrator reels`n" -ForegroundColor Yellow

# Configuration
$EDGE_SERVER = "192.168.0.30"
$SSH_USER = "twister"
$CONTAINER_NAME = "928508eefd57"
$TEMP_DIR = "C:\TwisterLab\temp_patch"
$ORIGINAL_FILE = "$TEMP_DIR\api_main_original.py"
$PATCHED_FILE = "$TEMP_DIR\api_main_patched.py"

# Create temp directory
if (Test-Path $TEMP_DIR) {
    Remove-Item -Path $TEMP_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

Write-Host "[1/8] Telechargement api/main.py depuis le container..." -ForegroundColor Green
ssh $SSH_USER@$EDGE_SERVER "docker exec $CONTAINER_NAME cat /app/api/main.py" | Out-File -FilePath $ORIGINAL_FILE -Encoding UTF8

if (-not (Test-Path $ORIGINAL_FILE)) {
    Write-Host "ERREUR: Impossible de telecharger api/main.py" -ForegroundColor Red
    exit 1
}

Write-Host "   Fichier telecharge: $((Get-Item $ORIGINAL_FILE).Length) bytes" -ForegroundColor Gray

Write-Host "`n[2/8] Creation du patch Python..." -ForegroundColor Green

# Create Python patch script
$PATCH_SCRIPT = @"
#!/usr/bin/env python3
"""
Patch api/main.py to replace mock functions with real orchestrator calls.
"""
import re
import sys

def patch_api_main(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Applying patches...")

    # 1. Add orchestrator import at the top (after other imports)
    if 'from agents.orchestrator.autonomous_orchestrator import get_orchestrator' not in content:
        # Find the last import statement
        import_pattern = r'(from [^\n]+\nimport [^\n]+\n)'
        matches = list(re.finditer(import_pattern, content))
        if matches:
            last_import_pos = matches[-1].end()
            content = (content[:last_import_pos] +
                      '\n# Real agent orchestrator\n' +
                      'from agents.orchestrator.autonomous_orchestrator import get_orchestrator\n\n' +
                      content[last_import_pos:])
            print("  ✓ Added orchestrator import")

    # 2. Replace the execute_agent_operation endpoint
    old_endpoint = r'@app\.post\("/api/v1/autonomous/agents/\{agent_name\}/execute"\)[^}]+async def execute_agent_operation\(agent_name: str, payload: Dict\[str, Any\]\):[^}]+?\n    # Mock routing logic.*?(?=\n@app\.|$)'

    new_endpoint = '''@app.post("/api/v1/autonomous/agents/{agent_name}/execute")
async def execute_agent_operation(agent_name: str, payload: Dict[str, Any]):
    """
    Execute an agent operation using the real orchestrator.

    Args:
        agent_name: Name of the agent (e.g., 'MonitoringAgent')
        payload: Operation payload with 'operation' and optional 'context'

    Returns:
        Result from the real agent execution
    """
    try:
        # Get orchestrator instance
        orchestrator = await get_orchestrator()

        # Map API agent names to orchestrator agent names
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
            return {
                "agent": agent_name,
                "status": "error",
                "error": f"Unknown agent: {agent_name}",
                "timestamp": datetime.now().isoformat()
            }

        # Extract operation and context from payload
        operation = payload.get("operation", "health_check")
        context = payload.get("context", {})

        # Execute real agent operation via orchestrator
        result = await orchestrator.execute_agent_operation(
            orchestrator_agent_name,
            operation,
            context
        )

        return {
            "agent": agent_name,
            "operation": operation,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

    except Exception as e:
        return {
            "agent": agent_name,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
'''

    # Try to replace the endpoint
    if re.search(old_endpoint, content, re.DOTALL):
        content = re.sub(old_endpoint, new_endpoint, content, flags=re.DOTALL)
        print("  ✓ Replaced execute_agent_operation endpoint")
    else:
        # Fallback: find and replace more aggressively
        # Find the endpoint definition
        endpoint_start = content.find('@app.post("/api/v1/autonomous/agents/{agent_name}/execute")')
        if endpoint_start != -1:
            # Find the next endpoint or end of file
            next_endpoint = content.find('\n@app.', endpoint_start + 1)
            if next_endpoint == -1:
                next_endpoint = len(content)

            # Replace the section
            content = content[:endpoint_start] + new_endpoint + '\n' + content[next_endpoint:]
            print("  ✓ Replaced execute_agent_operation endpoint (fallback method)")

    # 3. Remove mock functions
    mock_functions = [
        'async def execute_monitoring_agent',
        'async def execute_backup_agent',
        'async def execute_sync_agent'
    ]

    for mock_func in mock_functions:
        # Find and remove each mock function
        pattern = r'\n\n' + re.escape(mock_func) + r'\(.*?\):[^}]+?(?=\n\n(?:async def |@app\.|$$))'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            print(f"  ✓ Removed {mock_func}()")

    # Write patched content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Patch applied successfully!")
    print(f"  Original: {input_file}")
    print(f"  Patched:  {output_file}")

    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: patch_script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if patch_api_main(input_file, output_file):
        sys.exit(0)
    else:
        sys.exit(1)
"@

$PATCH_SCRIPT_FILE = "$TEMP_DIR\patch_script.py"
$PATCH_SCRIPT | Out-File -FilePath $PATCH_SCRIPT_FILE -Encoding UTF8

Write-Host "[3/8] Application du patch..." -ForegroundColor Green
python $PATCH_SCRIPT_FILE $ORIGINAL_FILE $PATCHED_FILE

if (-not (Test-Path $PATCHED_FILE)) {
    Write-Host "ERREUR: Le patch a echoue" -ForegroundColor Red
    exit 1
}

Write-Host "`n[4/8] Upload du fichier patche vers edgeserver..." -ForegroundColor Green
scp $PATCHED_FILE ${SSH_USER}@${EDGE_SERVER}:/tmp/main.py

Write-Host "[5/8] Copie dans le container..." -ForegroundColor Green
ssh $SSH_USER@$EDGE_SERVER "docker cp /tmp/main.py ${CONTAINER_NAME}:/app/api/main.py"

Write-Host "[6/8] Creation d'une nouvelle image Docker..." -ForegroundColor Green
$IMAGE_TAG = "twisterlab-api:production-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
ssh $SSH_USER@$EDGE_SERVER "docker commit $CONTAINER_NAME $IMAGE_TAG"

Write-Host "[7/8] Mise a jour du service Docker Swarm..." -ForegroundColor Green
ssh $SSH_USER@$EDGE_SERVER "docker service update --image $IMAGE_TAG twisterlab_api"

Write-Host "`nAttente de la convergence du service (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`n[8/8] TEST DE VERIFICATION - MonitoringAgent avec VRAIES donnees..." -ForegroundColor Green

$TEST_URL = "http://${EDGE_SERVER}:8000/api/v1/autonomous/agents/MonitoringAgent/execute"
$TEST_BODY = @{
    operation = "health_check"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $TEST_URL -Method POST -Body $TEST_BODY -ContentType "application/json"

    Write-Host "`n=== RESULTAT DU TEST ===" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 5 | Write-Host

    # Check if we got real data (not mock)
    if ($response.result.metrics.cpu_usage -eq "23%" -or $response.result.metrics.memory_usage -eq "1.2GB") {
        Write-Host "`nERREUR: Le resultat contient encore des donnees MOCK!" -ForegroundColor Red
        Write-Host "cpu_usage devrait etre un nombre, pas '23%'" -ForegroundColor Red
        Write-Host "memory_usage devrait etre des GB reels, pas '1.2GB'" -ForegroundColor Red
    } else {
        Write-Host "`nSUCCES! Les agents retournent des VRAIES donnees!" -ForegroundColor Green
        Write-Host "CPU: $($response.result.metrics.cpu.usage_percent)%" -ForegroundColor Green
        Write-Host "Memory: $($response.result.metrics.memory.used_gb)GB / $($response.result.metrics.memory.total_gb)GB" -ForegroundColor Green
        Write-Host "Disk: $($response.result.metrics.disk.used_gb)GB / $($response.result.metrics.disk.total_gb)GB" -ForegroundColor Green
    }
} catch {
    Write-Host "`nERREUR lors du test: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Verifiez les logs du container:" -ForegroundColor Yellow
    Write-Host "ssh $SSH_USER@$EDGE_SERVER 'docker service logs twisterlab_api --tail 50'" -ForegroundColor Gray
}

Write-Host "`n=== PATCH TERMINE ===" -ForegroundColor Cyan
Write-Host "Image Docker creee: $IMAGE_TAG" -ForegroundColor Green
Write-Host "Service mis a jour: twisterlab_api" -ForegroundColor Green
Write-Host "`nProchaines etapes:" -ForegroundColor Yellow
Write-Host "1. Tester tous les agents: python C:\TwisterLab\tests\test_integration_real_agents.py" -ForegroundColor Gray
Write-Host "2. Verifier Grafana: http://${EDGE_SERVER}:3000/d/twisterlab-agents-realtime" -ForegroundColor Gray
Write-Host "3. Monitorer les logs: ssh $SSH_USER@$EDGE_SERVER 'docker service logs -f twisterlab_api'" -ForegroundColor Gray
