# Helper script to convert Firebase service account JSON to Base64
# Use this to prepare your Firebase credentials for Render deployment

$serviceAccountFile = "serviceAccountKey.json"

if (-Not (Test-Path $serviceAccountFile)) {
    Write-Host "ERROR: $serviceAccountFile not found!" -ForegroundColor Red
    Write-Host "Please ensure your Firebase service account JSON file is in the current directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "Reading $serviceAccountFile..." -ForegroundColor Cyan

try {
    # Read the JSON file
    $content = Get-Content $serviceAccountFile -Raw
    
    # Convert to Base64
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    $base64 = [Convert]::ToBase64String($bytes)
    
    # Copy to clipboard
    $base64 | Set-Clipboard
    
    Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    Write-Host "`nYour Firebase service account has been converted to Base64 and copied to clipboard." -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Go to Render Dashboard → Your Web Service → Environment" -ForegroundColor White
    Write-Host "2. Add a new environment variable:" -ForegroundColor White
    Write-Host "   Key: FIREBASE_SERVICE_ACCOUNT_BASE64" -ForegroundColor Cyan
    Write-Host "   Value: <Paste from clipboard>" -ForegroundColor Cyan
    Write-Host "3. Save changes and redeploy" -ForegroundColor White
    
    Write-Host "`n📋 Base64 string length: $($base64.Length) characters" -ForegroundColor Gray
    Write-Host "First 50 characters: $($base64.Substring(0, [Math]::Min(50, $base64.Length)))..." -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ ERROR: $_" -ForegroundColor Red
    exit 1
}
