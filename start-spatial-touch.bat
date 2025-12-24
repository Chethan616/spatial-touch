@echo off
REM Spatial Touch Launcher
REM Starts the Python backend with API and optionally the Flutter app

echo ========================================
echo   Spatial Touch - Complete System
echo ========================================
echo.

set PYTHON_DIR=%~dp0spatial-touch-windows
set FLUTTER_DIR=%~dp0spatial-touch-app

REM Check if Python venv exists
if not exist "%PYTHON_DIR%\venv\Scripts\activate.bat" (
    echo [ERROR] Python virtual environment not found!
    echo Please run: cd spatial-touch-windows ^&^& python -m venv venv ^&^& .\venv\Scripts\activate ^&^& pip install -e .
    pause
    exit /b 1
)

echo [1/3] Starting Python Backend with API...
start "Spatial Touch Backend" cmd /k "cd /d %PYTHON_DIR% && .\venv\Scripts\activate && python -m spatial_touch --api"

echo [2/3] Waiting for API to start...
timeout /t 3 /nobreak > nul

echo [3/3] Starting Flutter Settings App...
start "Spatial Touch App" cmd /k "cd /d %FLUTTER_DIR% && flutter run -d windows"

echo.
echo ========================================
echo   Both applications are starting!
echo ========================================
echo.
echo Python Backend: http://localhost:8765
echo API Docs: http://localhost:8765/docs
echo.
echo Close this window to continue...
pause
