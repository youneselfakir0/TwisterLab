# Locate current TwisterLab deployment on EdgeServer
$EdgeServer = "192.168.0.30"
$EdgeUser = "twister"

Write-Host "Locating TwisterLab deployment on EdgeServer..." -ForegroundColor Cyan

# Find running containers
Write-Host "`n[1] Running containers:" -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' | grep -E 'NAME|twister|api|ollama'"

# Find mounts and volumes
Write-Host "`n[2] Checking container mounts:" -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "docker ps -q | xargs -I {} docker inspect {} --format '{{.Name}}: {{range .Mounts}}{{.Type}}={{.Source}}->{{.Destination}} {{end}}' | grep -E 'twister|api'"

# Check if stack exists
Write-Host "`n[3] Docker stacks:" -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "docker stack ls"

# Find Python app location
Write-Host "`n[4] Searching for agents code:" -ForegroundColor Yellow
ssh ${EdgeUser}@${EdgeServer} "docker ps -q | head -1 | xargs -I {} docker exec {} find / -name 'real_classifier_agent.py' 2>/dev/null"
