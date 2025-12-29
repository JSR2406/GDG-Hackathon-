@echo off
TITLE Eco-Sync Launcher 🌍

echo ===================================================
echo       🌍 STARTING ECO-SYNC STACK 🌍
echo ===================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH.
    pause
    exit /b
)

echo 1. Starting Backend Server...
start "Eco-Sync Backend" cmd /k "cd backend && python uvicorn_run.py"

echo 2. Waiting for Backend to initialize...
timeout /t 3 /nobreak >nul

echo 3. Starting Frontend Server...
start "Eco-Sync Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo 4. Opening Application in Browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000
start http://localhost:8000/docs

echo.
echo ✅ ALL SYSTEMS GO!
echo    - Frontend: http://localhost:3000
echo    - Backend:  http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause >nul

taskkill /FI "WINDOWTITLE eq Eco-Sync Backend" /F
taskkill /FI "WINDOWTITLE eq Eco-Sync Frontend" /F
echo 🛑 Servers stopped.
