$basePath = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $basePath "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

# Kill existing processes on ports 8000 and 5173
Write-Host "检查并清理旧进程..." -ForegroundColor Yellow

$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $port8000) {
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc -and $proc.Name -match "python") {
        Write-Host "  终止旧后端进程 PID: $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force
    }
}

$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $port5173) {
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc -and $proc.Name -match "node") {
        Write-Host "  终止旧前端进程 PID: $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force
    }
}

Start-Sleep -Seconds 2

# Start Backend in a new PowerShell window (persistent, with -NoExit)
Write-Host "`n启动后端 http://localhost:8000 ..." -ForegroundColor Green
$backendCmd = @"
Set-Location '$basePath\backend'
Write-Host '[Backend] Starting uvicorn on :8000...' -ForegroundColor Cyan
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | Tee-Object -FilePath '$logDir\backend.log'
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Wait for backend with health check
Write-Host "等待后端启动..." -ForegroundColor Yellow
$backendReady = $false
for ($i = 1; $i -le 15; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            Write-Host "  [OK] 后端已就绪" -ForegroundColor Green
            $backendReady = $true
            break
        }
    } catch {
        Write-Host "  等待中... ($i/15)" -ForegroundColor DarkGray
    }
}
if (-not $backendReady) {
    Write-Host "  [WARN] 后端可能未就绪，请检查弹出窗口" -ForegroundColor Red
}

# Start Frontend in a new PowerShell window (persistent, with -NoExit)
Write-Host "`n启动前端 http://localhost:5173 ..." -ForegroundColor Green
$frontendCmd = @"
Set-Location '$basePath\frontend'
Write-Host '[Frontend] Starting Vite dev server...' -ForegroundColor Cyan
npx vite --host 2>&1 | Tee-Object -FilePath '$logDir\frontend.log'
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Start-Sleep -Seconds 3

# Verify frontend
$frontendReady = $false
try {
    $r = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    if ($r.StatusCode -eq 200) {
        $frontendReady = $true
    }
} catch {}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  InterviewAgent 启动完成!" -ForegroundColor Cyan
Write-Host "  后端:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  前端:  http://localhost:5173" -ForegroundColor Cyan
Write-Host "  日志:  $logDir\" -ForegroundColor Cyan
Write-Host "  关闭弹出的 PowerShell 窗口即可停止" -ForegroundColor Cyan
Write-Host "  或运行 stop-services.bat 统一停止" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($backendReady -and $frontendReady) {
    Write-Host "`n自动打开浏览器..." -ForegroundColor Green
    Start-Process "http://localhost:5173"
}
