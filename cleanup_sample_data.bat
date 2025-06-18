@echo off
echo Kitchen Dashboard - Sample Data Cleanup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo This will remove sample data generated during testing.
echo.
set /p choice="Do you want to continue? (y/N): "

if /i "%choice%"=="y" (
    echo.
    echo Running cleanup...
    python quick_cleanup.py
) else (
    echo Cleanup cancelled.
)

echo.
pause
