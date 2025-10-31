#!/usr/bin/env pwsh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Full Project Setup and Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if Python is installed
if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
if (-not (Test-Command "node")) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setting up Backend Environment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Navigate to backend directory
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
if ($IsWindows -or $env:OS) {
    & ".\venv\Scripts\Activate.ps1"
} else {
    & "./venv/bin/Activate.ps1"
}

# Upgrade pip and install wheel first
Write-Host "Upgrading pip and installing wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip wheel setuptools

# Install core dependencies first for Python 3.13 compatibility
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
pip install numpy pandas

# Install backend requirements
Write-Host "Installing remaining Python requirements..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python requirements" -ForegroundColor Red
    Write-Host "You may need to install Microsoft Visual C++ Build Tools" -ForegroundColor Yellow
    Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Go back to root directory
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setting up Frontend Environment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Navigate to frontend directory
Set-Location frontend

# Install npm dependencies
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install npm dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Update npm dependencies
Write-Host "Updating npm dependencies..." -ForegroundColor Yellow
npm update

# Run npm audit fix
Write-Host "Running npm audit fix..." -ForegroundColor Yellow
npm audit fix

# Go back to root directory
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Starting Both Services" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# Start backend in a new window
Write-Host "Starting backend server..." -ForegroundColor Yellow
$backendPath = Join-Path $PWD "backend"
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList "-Command", "cd '$backendPath'; .\venv\Scripts\Activate.ps1; python main.py; Read-Host 'Press Enter to close'"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend development server..." -ForegroundColor Yellow
$frontendPath = Join-Path $PWD "frontend"
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList "-Command", "cd '$frontendPath'; npm run dev; Read-Host 'Press Enter to close'"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Project Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend server is starting in a separate window..." -ForegroundColor Cyan
Write-Host "Frontend development server is starting in a separate window..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:5173 (or similar)" -ForegroundColor Yellow
Write-Host "Close the command windows to stop the servers" -ForegroundColor Yellow