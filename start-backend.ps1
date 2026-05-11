$basePath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $basePath "backend")
Write-Host "Starting Interview Agent Backend on http://localhost:8000" -ForegroundColor Green
python -m uvicorn main:app --host 0.0.0.0 --port 8000
