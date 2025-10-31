@echo off
echo ========================================
echo Starting Full Project Setup and Launch
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setting up Backend Environment
echo ========================================

:: Navigate to backend directory
cd backend

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip and install wheel first
echo Upgrading pip and installing wheel...
python -m pip install --upgrade pip wheel setuptools

:: Install core dependencies first for Python 3.13 compatibility
echo Installing core dependencies...
pip install numpy pandas

:: Install backend requirements
echo Installing remaining Python requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python requirements
    echo You may need to install Microsoft Visual C++ Build Tools
    echo Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    pause
    exit /b 1
)

:: Go back to root directory
cd ..

echo.
echo ========================================
echo Setting up Frontend Environment
echo ========================================

:: Navigate to frontend directory
cd frontend

:: Install npm dependencies
echo Installing npm dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install npm dependencies
    pause
    exit /b 1
)

:: Update npm dependencies
echo Updating npm dependencies...
npm update

:: Run npm audit fix
echo Running npm audit fix...
npm audit fix

:: Go back to root directory
cd ..

echo.
echo ========================================
echo Starting Both Services
echo ========================================

:: Start backend in a new window
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
echo Starting frontend development server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Project Started Successfully!
echo ========================================
echo Backend server is running in a separate window
echo Frontend development server is running in a separate window
echo.
echo Press any key to exit this script...
pause >nul