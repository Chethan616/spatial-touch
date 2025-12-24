# Spatial Touch Launcher (PowerShell)
# Starts the Python backend with API and the Flutter app

Write-Host "========================================"
Write-Host "  Spatial Touch - Complete System"
Write-Host "========================================"
Write-Host ""

$PythonDir = Join-Path $PSScriptRoot "spatial-touch-windows"
$FlutterDir = Join-Path $PSScriptRoot "spatial-touch-app"

# Check if Python venv exists
if (-not (Test-Path (Join-Path $PythonDir "venv\Scripts\Activate.ps1"))) {
    Write-Host "[ERROR] Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run:"
    Write-Host "  cd spatial-touch-windows"
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\Activate.ps1"
    Write-Host "  pip install -e ."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Starting Python Backend with API..." -ForegroundColor Cyan
$pythonProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PythonDir'; .\venv\Scripts\Activate.ps1; python -m spatial_touch --api" -PassThru

Write-Host "[2/3] Waiting for API to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host "[3/3] Starting Flutter Settings App..." -ForegroundColor Cyan
$flutterProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FlutterDir'; flutter run -d windows" -PassThru

Write-Host ""
Write-Host "========================================"
Write-Host "  Both applications are starting!"
Write-Host "========================================"
Write-Host ""
Write-Host "Python Backend: http://localhost:8765" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8765/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit this launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
