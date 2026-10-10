@echo off
title Project Falcon Server Orchestrator
cd /d "%~dp0"
echo ===================================================
echo   Starting Project Falcon (Frontend + Backend)...
echo   Working Directory: %CD%
echo ===================================================
echo.
echo   Cleaning up any orphaned backend/frontend processes...
powershell -Command "Get-NetTCPConnection -LocalPort 8000,3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo.
call npm.cmd run dev
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start servers.
)
pause
