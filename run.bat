@echo off
echo ========================================
echo Starting Video Restoration Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo [1/4] Checking backend dependencies...
cd /d "%~dp0backend"
if errorlevel 1 (
    echo ERROR: Backend directory not found!
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
    timeout /t 2 /nobreak >nul
)

REM Check if dependencies are installed
if not exist "venv\Lib\site-packages\flask" (
    echo Installing backend dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install backend dependencies
        cd ..
        pause
        exit /b 1
    )
    echo Backend dependencies installed successfully
) else (
    echo Backend dependencies already installed
)

echo.
echo [2/4] Starting Flask Backend Server...
echo Backend will run on: http://localhost:5000
echo.

REM Start Flask server in a new window
start "Flask Backend Server" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python app.py"

REM Wait a moment for Flask to start
timeout /t 3 /nobreak >nul

cd /d "%~dp0frontend"
if errorlevel 1 (
    echo ERROR: Frontend directory not found!
    pause
    exit /b 1
)

echo.
echo [3/4] Checking frontend dependencies...
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies check passed
)

echo.
echo [4/4] Starting React Frontend...
echo Frontend will run on: http://localhost:3000
echo.

REM Start React app in a new window
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Both windows are now open. Close them to stop the servers.
echo Press any key to exit this window (servers will keep running)...
pause >nul
