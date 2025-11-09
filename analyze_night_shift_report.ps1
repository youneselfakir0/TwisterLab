# TwisterLab Night Shift Report Analyzer
# Analyzes the autonomous night shift report and provides actionable insights

Write-Host "🔍 Analyzing TwisterLab Night Shift Report..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$reportFile = "twisterlab_night_shift_report.txt"

if (-not (Test-Path $reportFile)) {
    Write-Host "❌ Report file not found: $reportFile" -ForegroundColor Red
    exit 1
}

# Read and analyze the report
$report = Get-Content $reportFile -Raw

# Extract key metrics
$tasksCompleted = ($report | Select-String -Pattern "\[.*?\] (SUCCESS|WARNING|ERROR) TASK:" -AllMatches).Matches.Count
$warnings = ($report | Select-String -Pattern "\[.*?\] WARNING TASK:" -AllMatches).Matches.Count
$errors = ($report | Select-String -Pattern "\[.*?\] ERROR TASK:" -AllMatches).Matches.Count
$successes = ($report | Select-String -Pattern "\[.*?\] SUCCESS TASK:" -AllMatches).Matches.Count

# Extract specific findings
$apiIssues = @()
$securityIssues = @()
$performanceIssues = @()

# Parse API issues
if ($report -match "Endpoint /api/v1/tickets/ not responding") {
    $apiIssues += "❌ /api/v1/tickets/ endpoint returns 404"
}
if ($report -match "Database endpoint not available") {
    $apiIssues += "❌ /api/v1/tickets/count endpoint missing"
}

# Parse security issues
if ($report -match "CORS headers not configured") {
    $securityIssues += "⚠️ CORS headers not configured"
}

# Parse performance issues
if ($report -match "Large ticket queries may be slow") {
    $performanceIssues += "⚠️ Large ticket queries may be slow - consider database indexing"
}

# Display results
Write-Host "`n📊 NIGHT SHIFT SUMMARY" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow
Write-Host "Tasks Executed: $tasksCompleted" -ForegroundColor White
Write-Host "✅ Successful: $successes" -ForegroundColor Green
Write-Host "⚠️ Warnings: $warnings" -ForegroundColor Yellow
Write-Host "❌ Errors: $errors" -ForegroundColor Red

Write-Host "`n🔧 ISSUES DISCOVERED" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow

if ($apiIssues.Count -gt 0) {
    Write-Host "`n🚀 API Issues:" -ForegroundColor Cyan
    $apiIssues | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
}

if ($securityIssues.Count -gt 0) {
    Write-Host "`n🔒 Security Issues:" -ForegroundColor Cyan
    $securityIssues | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
if ($performanceIssues.Count -gt 0) {
    Write-Host "`n⚡ Performance Issues:" -ForegroundColor Cyan
    $performanceIssues | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
}

Write-Host "`n✅ SYSTEM STATUS" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow

# Overall assessment
$overallScore = 0
if ($errors -eq 0) { $overallScore += 50 }
if ($warnings -le 2) { $overallScore += 30 }
if ($successes -ge ($tasksCompleted * 0.7)) { $overallScore += 20 }

if ($overallScore -ge 80) {
    Write-Host "🎉 System Health: EXCELLENT ($overallScore/100)" -ForegroundColor Green
} elseif ($overallScore -ge 60) {
    Write-Host "👍 System Health: GOOD ($overallScore/100)" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ System Health: NEEDS ATTENTION ($overallScore/100)" -ForegroundColor Red
}

Write-Host "`n📝 RECOMMENDATIONS" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow

if ($apiIssues.Count -gt 0) {
    Write-Host "1. Fix API endpoints - implement missing routes" -ForegroundColor White
    Write-Host "2. Add comprehensive error handling" -ForegroundColor White
}

if ($securityIssues.Count -gt 0) {
    Write-Host "3. Configure CORS middleware in FastAPI" -ForegroundColor White
    Write-Host "4. Add security headers (CSP, HSTS, etc.)" -ForegroundColor White
}

if ($performanceIssues.Count -gt 0) {
    Write-Host "5. Optimize database queries and add indexing" -ForegroundColor White
    Write-Host "6. Implement caching for frequently accessed data" -ForegroundColor White
}

Write-Host "7. Run Night Shift continuously for ongoing monitoring" -ForegroundColor White
Write-Host "8. Set up alerts for critical issues" -ForegroundColor White

Write-Host "`n🌙 Night Shift Report Analysis Complete!" -ForegroundColor Cyan
Write-Host "Full report available at: $reportFile" -ForegroundColor Gray