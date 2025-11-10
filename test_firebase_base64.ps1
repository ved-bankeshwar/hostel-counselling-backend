# Test if your Firebase Base64 encoding is correct
# Run this to verify before deploying

$serviceAccountFile = "serviceAccountKey.json"

if (-Not (Test-Path $serviceAccountFile)) {
    Write-Host "ERROR: $serviceAccountFile not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Testing Firebase Base64 encoding..." -ForegroundColor Cyan

# Read and encode
$content = Get-Content $serviceAccountFile -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)

Write-Host "`n1. Base64 created successfully" -ForegroundColor Green
Write-Host "   Length: $($base64.Length) characters" -ForegroundColor Gray

# Test decode
try {
    $decoded_bytes = [Convert]::FromBase64String($base64)
    $decoded_json = [System.Text.Encoding]::UTF8.GetString($decoded_bytes)
    $json_obj = $decoded_json | ConvertFrom-Json
    
    Write-Host "`n2. Base64 decodes successfully" -ForegroundColor Green
    Write-Host "   Project ID: $($json_obj.project_id)" -ForegroundColor Gray
    Write-Host "   Client Email: $($json_obj.client_email)" -ForegroundColor Gray
    
    Write-Host "`n✅ Your Firebase Base64 is valid!" -ForegroundColor Green
    Write-Host "`nCopy this to Render:" -ForegroundColor Yellow
    $base64 | Set-Clipboard
    Write-Host "✓ Copied to clipboard" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ ERROR: Failed to decode - $_" -ForegroundColor Red
    exit 1
}
