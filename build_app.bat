@echo off
echo ========================================
echo VARSYS Kitchen Dashboard Build Script
echo ========================================
echo.

REM Check if Python 3.12 is available
py -3.12 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using Python 3.12 for build...
    set PYTHON_CMD=py -3.12
) else (
    echo Python 3.12 not found, checking for Python 3.13...
    python --version | findstr "3.13" >nul 2>&1
    if %errorlevel% == 0 (
        echo Using Python 3.13 for build...
        set PYTHON_CMD=python
    ) else (
        echo ERROR: Neither Python 3.12 nor 3.13 found!
        echo Please install Python 3.12 or 3.13
        pause
        exit /b 1
    )
)

echo.
echo Step 1: Installing/Updating build dependencies...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install --upgrade cx_Freeze
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo Step 2: Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Step 3: Building executable...
%PYTHON_CMD% setup_cx_freeze.py build

echo.
echo Step 4: Creating MSI installer...
%PYTHON_CMD% setup_cx_freeze.py bdist_msi

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: build\exe.win-amd64-*\VARSYS_Kitchen_Dashboard.exe
echo MSI installer location: dist\*.msi
echo.
echo To test the executable:
echo 1. Navigate to the build directory
echo 2. Run VARSYS_Kitchen_Dashboard.exe
echo.
echo To install using MSI:
echo 1. Navigate to the dist directory
echo 2. Run the .msi file as administrator
echo.
pause
