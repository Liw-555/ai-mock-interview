@echo off
chcp 65001 >nul 2>&1
title InterviewAgent - 停止服务

echo 正在停止 InterviewAgent 服务...

REM Kill processes on port 8000 (backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo   停止后端 PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill processes on port 5173 (frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do (
    echo   停止前端 PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

REM Close the named windows
taskkill /FI "WINDOWTITLE eq InterviewAgent-Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq InterviewAgent-Frontend" /F >nul 2>&1

echo 完成。
timeout /t 2 /nobreak >nul
