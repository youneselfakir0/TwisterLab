# TwisterLab LLM - Deploy Helper
Write-Host "`n=== DEPLOYMENT STEPS ===" -ForegroundColor Cyan

Write-Host "`n1. Copy files to edgeserver:" -ForegroundColor Yellow
Write-Host @"
scp -r agents twister@192.168.0.30:~/twisterlab/
scp -r monitoring twister@192.168.0.30:~/twisterlab/
scp docker-compose.production.yml twister@192.168.0.30:~/twisterlab/
"@

Write-Host "`n2. Deploy stack (in SSH session):" -ForegroundColor Yellow
Write-Host @"
ssh twister@192.168.0.30
cd ~/twisterlab
docker stack deploy -c docker-compose.production.yml twisterlab
"@

Write-Host "`n3. Verify deployment:" -ForegroundColor Yellow
Write-Host @"
curl http://192.168.0.30:8000/health
curl http://192.168.0.30:11434/api/tags
"@

Write-Host "`n4. Import Grafana dashboard:" -ForegroundColor Yellow
Write-Host "   http://192.168.0.30:3001 → Import → llm-agents-performance.json"

Write-Host "`n=== SERVICES ===" -ForegroundColor Cyan
Write-Host "API:        http://192.168.0.30:8000/docs"
Write-Host "Grafana:    http://192.168.0.30:3001"
Write-Host "Prometheus: http://192.168.0.30:9090`n"
