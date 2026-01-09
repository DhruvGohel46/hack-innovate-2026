@echo off
echo ========================================
echo Stopping Video Restoration Application
echo ========================================
echo.

echo Stopping Flask Backend Server...
taskkill /FI "WindowTitle eq Flask Backend Server*" /F >nul 2>&1
taskkill /FI "WindowTitle eq React Frontend*" /F >nul 2>&1

REM Also kill by process name if window title method doesn't work
taskkill /IM python.exe /FI "WINDOWTITLE eq Flask Backend Server*" /F >nul 2>&1
taskkill /IM node.exe /FI "WINDOWTITLE eq React Frontend*" /F >nul 2>&1

REM Kill processes on ports if still running
echo Checking for processes on ports 5000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo Killing process on port 5000 (PID: %%a)...
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Killing process on port 3000 (PID: %%a)...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Application stopped successfully!
timeout /t 2 /nobreak >nul
