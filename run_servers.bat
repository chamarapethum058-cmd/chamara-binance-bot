@echo off
title Project Falcon Server Orchestrator
cd /d "%~dp0"
echo ===================================================
echo   Starting Project Falcon (Frontend + Backend)...
echo   Working Directory: %CD%
echo ===================================================
echo.
echo   Cleaning up any orphaned Python backend processes...
taskkill /f /im python.exe >nul 2>&1
echo.
call "C:\Program Files\nodejs\npm.cmd" run dev
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start servers.
)
pause
