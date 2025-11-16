# PowerShell script to install Playwright package and browsers for Playwright
# Run as user with Python environment active

Write-Host "Installing pip dependencies from requirements.txt..."
python -m pip install -r requirements.txt

Write-Host "Installing Playwright browsers..."
# Use the playwright CLI to install browsers
python -m playwright install

Write-Host "Done. You can run tests with: pytest tests/test_browser_agent.py -q"
