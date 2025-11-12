param([string]$Action = 'all')
$REGISTRY_HOST = "192.168.0.30"
Write-Host "Deploying registry..." -ForegroundColor Green
$files = @("infrastructure\docker\docker-compose.registry.yml","infrastructure\docker\registry-config.yml","infrastructure\scripts\deploy_registry.sh","infrastructure\scripts\migrate_images_to_registry.sh","infrastructure\scripts\build_api_local_registry.sh")
foreach ($f in $files) { scp $f "twister@${REGISTRY_HOST}:/home/twister/TwisterLab/$($f.Replace('\','/'))" }
if ($Action -in @('deploy','all')) { ssh "twister@${REGISTRY_HOST}" "cd /home/twister/TwisterLab && chmod +x infrastructure/scripts/deploy_registry.sh && ./infrastructure/scripts/deploy_registry.sh" }
if ($Action -in @('migrate','all')) { ssh "twister@${REGISTRY_HOST}" "cd /home/twister/TwisterLab && chmod +x infrastructure/scripts/migrate_images_to_registry.sh && ./infrastructure/scripts/migrate_images_to_registry.sh" }
if ($Action -in @('build','all')) { ssh "twister@${REGISTRY_HOST}" "cd /home/twister/TwisterLab && chmod +x infrastructure/scripts/build_api_local_registry.sh && ./infrastructure/scripts/build_api_local_registry.sh" }
Write-Host "Deployment complete. Registry: http://${REGISTRY_HOST}:5000 UI: http://${REGISTRY_HOST}:5001" -ForegroundColor Green
