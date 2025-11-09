# TwisterLab Night Shift Test Run
# This script runs one complete cycle of the night shift system for testing

Write-Host "🧪 Testing TwisterLab Night Shift Autonomous System..." -ForegroundColor Cyan
Write-Host "Running one complete cycle with all tasks..." -ForegroundColor White
Write-Host ""

# Run one cycle for testing
.\night_shift_autonomous.ps1 -RunOnce -Verbose