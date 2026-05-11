@echo off
chcp 65001 >nul 2>&1
title InterviewAgent - Start All

echo ========================================
echo   InterviewAgent - 启动全部服务
echo ========================================
echo.

set "BASE=%~dp0"
set "BACKEND=%BASE%backend"
set "FRONTEND=%BASE%frontend"
set "LOGDIR=%BASE%logs"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM ---- Kill existing processes on ports ----
echo [1/4] 清理旧进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo   终止后端进程 PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do (
    echo   终止前端进程 PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM ---- Start Backend in new persistent window ----
echo [2/4] 启动后端 (FastAPI on :8000)...
start "InterviewAgent-Backend" cmd /k "cd /d %BACKEND% && echo [Backend] Starting uvicorn... && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | tee %LOGDIR%\backend.log"

echo   等待后端启动...
timeout /t 5 /nobreak >nul

REM ---- Health check loop ----
set BACKEND_OK=0
for /L %%i in (1,1,10) do (
    if !BACKEND_OK! equ 0 (
        curl -s http://localhost:8000/api/health >nul 2>&1
        if !errorlevel! equ 0 (
            set BACKEND_OK=1
            echo   [OK] 后端已就绪
        ) else (
            echo   等待后端响应... (%%i/10^)
            timeout /t 2 /nobreak >nul
        )
    )
)
if %BACKEND_OK% equ 0 (
    echo   [WARN] 后端可能未就绪，请检查 InterviewAgent-Backend 窗口
)

REM ---- Start Frontend in new persistent window ----
echo [3/4] 启动前端 (Vite on :5173)...
start "InterviewAgent-Frontend" cmd /k "cd /d %FRONTEND% && echo [Frontend] Starting Vite dev server... && npx vite --host 2>&1 | tee %LOGDIR%\frontend.log"

timeout /t 4 /nobreak >nul

REM ---- Verify ----
echo [4/4] 验证服务状态...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] Backend  http://localhost:8000
) else (
    echo   [FAIL] Backend 未响应
)
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] Frontend http://localhost:5173
) else (
    echo   [FAIL] Frontend 未响应
)

echo.
echo ========================================
echo   服务已在独立窗口中运行
echo   关闭对应窗口即可停止服务
echo   或运行 stop-services.bat 统一停止
echo ========================================
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:5173
