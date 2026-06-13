@echo off
title EMR4 Master Launcher
echo ====================================================================
echo 🚀 STARTING EMR4 CLINICAL COPILOT ENVIRONMENT
echo ====================================================================
echo.

:: --------------------------------------------------------------------
:: CONFIGURATION: Update these paths to match your actual folders
:: --------------------------------------------------------------------
set WINDOWS_FRONTEND_PATH=C:\Users\YuriFrusin\Documents\EMR4\EMR4 Sidebar
set WSL_BACKEND_DIR=/mnt/c/Users/YuriFrusin/Documents/EMR4
:: --------------------------------------------------------------------

echo [1/4] 🐳 Booting PostgreSQL Container natively on Windows...
docker start gp-pms-postgres
echo     ✅ Database container signaled to start.
echo.

echo [2/4] 🐍 Launching FastAPI Backend in a new window...
start "EMR4 Backend (FastAPI)" cmd /k "cd /d C:\Users\YuriFrusin\Documents\EMR4 && .\.venv\Scripts\activate.bat && set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YuriFrusin\Documents\EMR4\gcp-key.json && uvicorn main:app --reload --port 8001"
timeout /t 2 >nul

echo [3/4] 🌐 Launching Ngrok Cloud Tunnel...
start "EMR4 Tunnel (Ngrok)" cmd /k "ngrok http 8001"
timeout /t 2 >nul

echo [4/4] 📄 Launching Word Add-in Frontend (Node.js) & Word Desktop...
cd /d "%WINDOWS_FRONTEND_PATH%"
start "EMR4 Frontend (Node)" cmd /k "npm start"
echo.

echo ====================================================================
echo 🎉 ALL ENGINES INITIATED!
echo ====================================================================
echo Keep this window open if you want to inspect or close everything together.
echo Individual service logs are streaming in their respective windows.
echo ====================================================================
pause