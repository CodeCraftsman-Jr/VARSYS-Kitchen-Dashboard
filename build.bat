@echo off
REM VARSYS Kitchen Dashboard - Windows Build Script
REM Complete build process using cx_Freeze

echo ========================================
echo VARSYS Kitchen Dashboard Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if we're in the right directory
if not exist "kitchen_app.py" (
    echo ERROR: kitchen_app.py not found
    echo Please run this script from the Kitchen Dashboard directory
    pause
    exit /b 1
)

echo Starting complete build process...
echo.

REM Run the complete build script
python build_complete.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo The executable has been created in the build directory.
echo You can now test it or create an installer.
echo.

pause
