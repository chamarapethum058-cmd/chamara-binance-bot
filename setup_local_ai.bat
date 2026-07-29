@echo off
title Project Falcon - Local AI Setup
color 0A
echo ===================================================
echo Project Falcon - Local AI (Ollama) Setup
echo ===================================================
echo.
echo Google Gemini API is rate-limiting your key (limit: 0).
echo This script will set up Ollama Local AI so you can use
echo Falcon 100%% FREE without any API keys or Bank Cards!
echo.
echo Step 1: Downloading Ollama Setup...
powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
echo Download completed successfully!
echo.
echo Step 2: Running Ollama Installer...
echo Please complete the installation window that pops up.
start /wait OllamaSetup.exe
echo.
echo Step 3: Starting Ollama background service...
start "" "%LOCALAPPDATA%\Ollama\ollama app.exe"
echo Waiting for Ollama service to boot...
timeout /t 8
echo.
echo Step 4: Downloading AI Model (qwen2.5-coder:7b)...
echo This will take a few minutes depending on your internet. Please wait.
ollama pull qwen2.5-coder:7b
echo.
echo Step 5: Configuring Project Falcon to use Local AI...
cd backend
.\.venv\Scripts\python.exe -c "from app.database import SessionLocal; from app.models import PreferenceModel; db = SessionLocal(); p = db.query(PreferenceModel).filter(PreferenceModel.key == 'llm_provider').first(); p.value = 'LOCAL'; db.commit(); print('Falcon Configured to Local LLM!')"
echo.
echo ===================================================
echo SUCCESS: Local AI configured! Please reload the web page.
echo ===================================================
pause
