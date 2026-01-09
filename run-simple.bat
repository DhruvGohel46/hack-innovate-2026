@echo off
echo ========================================
echo Quick Start - Video Restoration App
echo ========================================
echo.
echo Starting Backend and Frontend...
echo.

REM Start Backend
start "Flask Backend Server" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================
echo Both servers are starting...
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Close the server windows to stop them.
echo Press any key to close this window...
pause >nul
