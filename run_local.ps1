# Local Development Startup Script for Backend
# This script starts the FastAPI backend server for local development

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Hostel Counselling Backend - Local Server  " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list
if (-not ($pipList -match "fastapi")) {
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Dependencies already installed." -ForegroundColor Green
}
Write-Host ""

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "WARNING: .env.local file not found!" -ForegroundColor Red
    Write-Host "Creating .env.local from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env.local
    Write-Host ""
    Write-Host "Please edit .env.local with your configuration before continuing." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to exit and configure, or any key to continue..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Load environment variables from .env.local
Write-Host "Loading environment variables from .env.local..." -ForegroundColor Yellow
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        if ($key -and $value -and -not $key.StartsWith('#')) {
            [System.Environment]::SetEnvironmentVariable($key, $value, 'Process')
        }
    }
}
Write-Host "Environment variables loaded." -ForegroundColor Green
Write-Host ""

# Check if serviceAccountKey.json exists
if (-not (Test-Path "serviceAccountKey.json")) {
    Write-Host "WARNING: serviceAccountKey.json not found!" -ForegroundColor Yellow
    Write-Host "Make sure you have either:" -ForegroundColor Yellow
    Write-Host "  1. serviceAccountKey.json in the root directory, OR" -ForegroundColor Yellow
    Write-Host "  2. FIREBASE_SERVICE_ACCOUNT_BASE64 set in .env.local" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  - API: http://localhost:8000" -ForegroundColor White
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
