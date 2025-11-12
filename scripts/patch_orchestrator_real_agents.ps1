# Patch Orchestrator to Load Real Agents
# This script modifies autonomous_orchestrator.py to use real agents

param(
    [string]$EdgeServer = "192.168.0.30",
    [string]$User = "twister"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PATCH ORCHESTRATOR FOR REAL AGENTS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Get container ID
Write-Host "[1/4] Getting container ID..." -ForegroundColor Yellow
$containerId = ssh ${User}@$EdgeServer "docker ps --filter name=twisterlab_api --format '{{.ID}}' | head -1"
$containerId = $containerId.Trim()

if ([string]::IsNullOrEmpty($containerId)) {
    Write-Host "[ERROR] No container found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Container: $containerId`n" -ForegroundColor Green

# Backup original file
Write-Host "[2/4] Backing up original orchestrator..." -ForegroundColor Yellow
ssh ${User}@$EdgeServer "docker exec $containerId cp /app/agents/orchestrator/autonomous_orchestrator.py /app/agents/orchestrator/autonomous_orchestrator.py.backup"
Write-Host "[OK] Backup created`n" -ForegroundColor Green

# Create patch script
Write-Host "[3/4] Applying patch..." -ForegroundColor Yellow

$patchScript = @'
docker exec CONTAINER_ID bash -c 'cat > /tmp/patch_orchestrator.py << "PYTHON_EOF"
import re

# Read original file
with open("/app/agents/orchestrator/autonomous_orchestrator.py", "r") as f:
    content = f.read()

# Replace imports
old_imports = r"from agents\.core\.(classifier|resolver|desktop_commander|monitoring|backup|sync)_agent import"
new_imports_block = """
# Real Agents (deployed on edgeserver)
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_backup_agent import RealBackupAgent
from agents.real.real_sync_agent import RealSyncAgent
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent
"""

# Check if already patched
if "from agents.real." in content:
    print("Already patched!")
    exit(0)

# Add new imports after existing imports
import_section_end = content.find("\nclass ")
if import_section_end > 0:
    content = content[:import_section_end] + "\n" + new_imports_block + content[import_section_end:]
else:
    print("Could not find class definition!")
    exit(1)

# Replace agent instantiation
replacements = {
    "ClassifierAgent()": "RealClassifierAgent()",
    "ResolverAgent()": "RealResolverAgent()",
    "DesktopCommanderAgent()": "RealDesktopCommanderAgent()",
    "MaestroOrchestratorAgent()": "RealMaestroAgent()",
    "MonitoringAgent()": "RealMonitoringAgent()",
    "BackupAgent()": "RealBackupAgent()",
    "SyncAgent()": "RealSyncAgent()",
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write patched file
with open("/app/agents/orchestrator/autonomous_orchestrator.py", "w") as f:
    f.write(content)

print("Patch applied successfully!")
PYTHON_EOF
python3 /tmp/patch_orchestrator.py'
'@

$patchScript = $patchScript.Replace("CONTAINER_ID", $containerId)

try {
    ssh ${User}@$EdgeServer $patchScript
    Write-Host "[OK] Patch applied`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Patch failed: $_" -ForegroundColor Red
    exit 1
}

# Restart service
Write-Host "[4/4] Restarting API service..." -ForegroundColor Yellow
ssh ${User}@$EdgeServer "docker service update --force twisterlab_api" | Out-Null

Write-Host "Waiting for service to stabilize (10 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Test
try {
    $response = Invoke-RestMethod -Uri "http://${EdgeServer}:8000/health" -Method GET -TimeoutSec 5
    Write-Host "[OK] API is responsive" -ForegroundColor Green
} catch {
    Write-Host "[WARN] API not yet ready" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PATCH COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "  Orchestrator now loads REAL agents!" -ForegroundColor White
Write-Host ""
Write-Host "  Test command:" -ForegroundColor Yellow
Write-Host "  Invoke-RestMethod -Uri 'http://${EdgeServer}:8000/api/v1/autonomous/agents/MonitoringAgent/execute' \" -ForegroundColor Gray
Write-Host "    -Method POST -ContentType 'application/json' \" -ForegroundColor Gray
Write-Host "    -Body '{`"operation`":`"health_check`"}'" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================`n" -ForegroundColor Cyan

exit 0
