# Database Migration Script for Local Development
# This script runs all database migrations in order

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Database Migration Runner - Local Setup    " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables from .env.local
if (Test-Path ".env.local") {
    Write-Host "Loading database configuration from .env.local..." -ForegroundColor Yellow
    $dbConfig = @{}
    Get-Content .env.local | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and -not $key.StartsWith('#')) {
                $dbConfig[$key] = $value
            }
        }
    }
    
    $dbHost = $dbConfig['DB_HOST'] ?? 'localhost'
    $dbPort = $dbConfig['DB_PORT'] ?? '5432'
    $dbName = $dbConfig['DB_NAME'] ?? 'room_counselling'
    $dbUser = $dbConfig['DB_USER'] ?? 'postgres'
    $dbPassword = $dbConfig['DB_PASSWORD']
} else {
    Write-Host "WARNING: .env.local not found. Using defaults..." -ForegroundColor Yellow
    $dbHost = 'localhost'
    $dbPort = '5432'
    $dbName = 'room_counselling'
    $dbUser = 'postgres'
    $dbPassword = 'postgres'
}

Write-Host "Database Configuration:" -ForegroundColor Cyan
Write-Host "  Host: $dbHost" -ForegroundColor White
Write-Host "  Port: $dbPort" -ForegroundColor White
Write-Host "  Database: $dbName" -ForegroundColor White
Write-Host "  User: $dbUser" -ForegroundColor White
Write-Host ""

# Set password environment variable for psql
$env:PGPASSWORD = $dbPassword

# Get all migration files
$migrations = Get-ChildItem -Path "migrations" -Filter "*.sql" | Sort-Object Name

if ($migrations.Count -eq 0) {
    Write-Host "No migration files found in migrations directory!" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($migrations.Count) migration files:" -ForegroundColor Green
$migrations | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
Write-Host ""

# Ask for confirmation
Write-Host "This will run all migrations on database '$dbName'." -ForegroundColor Yellow
Write-Host "Do you want to continue? (Y/N): " -ForegroundColor Yellow -NoNewline
$confirmation = Read-Host

if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
    Write-Host "Migration cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Running migrations..." -ForegroundColor Green
Write-Host ""

# Run each migration
$successCount = 0
$failCount = 0

foreach ($migration in $migrations) {
    Write-Host "Running: $($migration.Name)..." -ForegroundColor Cyan
    
    $result = psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -f $migration.FullName 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Success" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  ✗ Failed" -ForegroundColor Red
        Write-Host "  Error: $result" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
}

# Clear password from environment
$env:PGPASSWORD = $null

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Migration Summary:" -ForegroundColor Cyan
Write-Host "  Total: $($migrations.Count)" -ForegroundColor White
Write-Host "  Success: $successCount" -ForegroundColor Green
Write-Host "  Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "White" })
Write-Host "===============================================" -ForegroundColor Cyan

if ($failCount -gt 0) {
    Write-Host ""
    Write-Host "Some migrations failed. Please check the errors above." -ForegroundColor Red
    exit 1
} else {
    Write-Host ""
    Write-Host "All migrations completed successfully! 🎉" -ForegroundColor Green
    exit 0
}
