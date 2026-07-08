@echo off
title Project Falcon GitHub Push
cd /d "%~dp0"
echo ===================================================
echo   Pushing code to GitHub...
echo ===================================================
echo.
git remote remove origin 2>nul
git remote add origin https://github.com/chamarapethum058-cmd/chamara-binance-bot.git
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed. 
    echo If GitHub asks you to log in, please complete the login in your web browser.
) else (
    echo.
    echo [SUCCESS] Code pushed successfully to GitHub!
)
pause
