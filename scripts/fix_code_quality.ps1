<#
.SYNOPSIS
    Fix code quality issues (ruff, black, unused imports)
#>

Write-Host "=== TwisterLab Code Quality Fix ===" -ForegroundColor Cyan

# 1. Remove unused imports automatically
Write-Host "`n1. Removing unused imports..." -ForegroundColor Yellow
ruff check --select F401 --fix src/

# 2. Fix all auto-fixable ruff issues
Write-Host "`n2. Fixing ruff issues..." -ForegroundColor Yellow
ruff check --fix src/

# 3. Format code with black
Write-Host "`n3. Formatting code with black..." -ForegroundColor Yellow
black src/ tests/

# 4. Sort imports with isort
Write-Host "`n4. Sorting imports..." -ForegroundColor Yellow
isort src/ tests/

# 5. Verify
Write-Host "`n5. Verification..." -ForegroundColor Yellow
ruff check src/
black --check src/

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All code quality issues fixed!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some issues remain. Review output above." -ForegroundColor Yellow
}
