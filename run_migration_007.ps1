# Run the new migration to add allocated room tracking to User table
Write-Host "Running migration 007_add_allocated_room_to_user.sql..." -ForegroundColor Cyan

$env:PGPASSWORD = "admin123"

Get-Content "migrations\007_add_allocated_room_to_user.sql" | psql -U admin -d room_counselling -h localhost

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Migration failed!" -ForegroundColor Red
}

Remove-Item Env:\PGPASSWORD
