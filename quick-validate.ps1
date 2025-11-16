# Validation rapide TwisterLab
$server = "twister@192.168.0.30"

Write-Host "🔍 VALIDATION RAPIDE TWISTERLAB" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Services Docker
Write-Host "`n📊 SERVICES DOCKER:" -ForegroundColor Blue
ssh $server "docker service ls --format 'table {{.Name}}\t{{.Replicas}}'"

# Secrets
Write-Host "`n🔐 SECRETS CONFIGURÉS:" -ForegroundColor Blue
ssh $server "docker secret ls --format 'table {{.Name}}'"

# Santé API
Write-Host "`n🏥 SANTÉ API:" -ForegroundColor Blue
ssh $server "curl -s http://localhost:8000/health | jq -r '.status'"

# SSL Status
Write-Host "`n🔒 SSL STATUS:" -ForegroundColor Blue
ssh $server "curl -kI https://localhost 2>/dev/null | head -1 || echo 'Certificate generating...'"

# Métriques Prometheus
Write-Host "`n📈 PROMETHEUS:" -ForegroundColor Blue
ssh $server "curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'"

Write-Host "`n✅ Validation terminée !" -ForegroundColor Green
