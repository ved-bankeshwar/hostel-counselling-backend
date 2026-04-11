# Quick Setup Script - First Time Setup
# This script sets up everything needed for local development

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Hostel Counselling System - Quick Setup    " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$backendDir = Get-Location
$frontendDir = Join-Path (Split-Path $backendDir -Parent) "hostel-counselling-frontend\room_counselling"

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check PostgreSQL
Write-Host "Checking PostgreSQL installation..." -ForegroundColor Yellow
try {
    $psqlVersion = psql --version 2>&1
    Write-Host "  ✓ $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ PostgreSQL not found. Please install PostgreSQL 14+" -ForegroundColor Red
    Write-Host "    Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Backend Setup
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Write-Host ""

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate and install dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null
Write-Host "  ✓ Backend dependencies installed" -ForegroundColor Green
Write-Host ""

# Setup environment file
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env.local
    Write-Host "  ✓ .env.local created" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ⚠️  IMPORTANT: Please edit .env.local with your database and Firebase credentials" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ .env.local already exists" -ForegroundColor Green
}
Write-Host ""

# Frontend Setup
if (Test-Path $frontendDir) {
    Write-Host "Setting up Frontend..." -ForegroundColor Cyan
    Write-Host ""
    
    Push-Location $frontendDir
    
    # Install dependencies
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies (this may take a while)..." -ForegroundColor Yellow
        npm install | Out-Null
        Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Frontend dependencies already installed" -ForegroundColor Green
    }
    
    # Setup environment file
    if (-not (Test-Path ".env.local")) {
        Write-Host "Creating frontend .env.local from template..." -ForegroundColor Yellow
        Copy-Item .env.example .env.local
        
        # Update API URL to localhost
        (Get-Content .env.local) -replace 'https://hostel-counselling-backend.onrender.com', 'http://localhost:8000' | Set-Content .env.local
        
        Write-Host "  ✓ Frontend .env.local created" -ForegroundColor Green
        Write-Host ""
        Write-Host "  ⚠️  IMPORTANT: Please add your Firebase web app credentials to frontend .env.local" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ Frontend .env.local already exists" -ForegroundColor Green
    }
    
    Pop-Location
} else {
    Write-Host "Frontend directory not found at: $frontendDir" -ForegroundColor Yellow
    Write-Host "Skipping frontend setup." -ForegroundColor Yellow
}
Write-Host ""

# Final instructions
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Setup Complete! Next Steps:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configure Environment Variables:" -ForegroundColor Yellow
Write-Host "   Backend: Edit .env.local with your PostgreSQL password and Firebase credentials" -ForegroundColor White
Write-Host "   Frontend: Edit $frontendDir\.env.local with Firebase config" -ForegroundColor White
Write-Host ""
Write-Host "2. Setup Database:" -ForegroundColor Yellow
Write-Host "   Create database: createdb -U postgres room_counselling" -ForegroundColor White
Write-Host "   Run migrations: .\run_migrations_local.ps1" -ForegroundColor White
Write-Host ""
Write-Host "3. Start the Servers:" -ForegroundColor Yellow
Write-Host "   Backend: .\run_local.ps1" -ForegroundColor White
Write-Host "   Frontend: cd $frontendDir; npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "4. Access the Application:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see LOCAL_SETUP.md" -ForegroundColor Cyan
Write-Host ""
