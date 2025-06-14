@echo off
echo Kitchen Dashboard - Test Suite Runner
echo =====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Running comprehensive tests...
echo.

REM Run the test suite
python run_tests.py

echo.
echo Test execution completed!
echo Check the test reports for detailed results.
echo.
pause
