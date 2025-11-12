$body = @{
    operation = "classify"
    context = @{
        text = "WiFi broken in conference room"
    }
} | ConvertTo-Json

Write-Host "Testing ClassifierAgent with real API..."
Write-Host "Request: $body"
Write-Host ""

try {
    $response = Invoke-RestMethod `
        -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/ClassifierAgent/execute" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "ERROR:" -ForegroundColor Red
    $_.Exception.Message
    if ($_.ErrorDetails.Message) {
        Write-Host "Details:" -ForegroundColor Yellow
        $_.ErrorDetails.Message
    }
}
