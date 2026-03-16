# AI Sakhi - Quick Start Script (PowerShell)
# This script activates the virtual environment and starts the application

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   AI Sakhi - Starting Application" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "ai-sakhi-env\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create virtual environment
    python -m venv ai-sakhi-env
    
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\ai-sakhi-env\Scripts\pip.exe install -r requirements.txt
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\ai-sakhi-env\Scripts\Activate.ps1

# Check if app file exists
if (-not (Test-Path "app_integrated.py")) {
    Write-Host "ERROR: app_integrated.py not found!" -ForegroundColor Red
    Write-Host "Please make sure you're in the correct directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the application
Write-Host ""
Write-Host "Starting AI Sakhi application..." -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Application will start on port 8080" -ForegroundColor Cyan
Write-Host "   Open your browser to: http://localhost:8080" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

# Start the Flask application
python app_integrated.py
