$basePath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $basePath "frontend")
Write-Host "Starting Interview Agent Frontend on http://localhost:5173" -ForegroundColor Green
npm run dev
