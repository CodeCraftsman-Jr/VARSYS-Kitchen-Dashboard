@echo off
echo ========================================
echo Quick Build Fix for v1.1.1
echo ========================================
echo.

REM Check Python version
py -3.12 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Using Python 3.12
    set PYTHON_CMD=py -3.12
) else (
    python --version | findstr "3.13" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✓ Using Python 3.13
        set PYTHON_CMD=python
    ) else (
        echo ❌ ERROR: Python 3.12 or 3.13 required!
        pause
        exit /b 1
    )
)

echo.
echo Step 1: Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo Step 2: Installing compatible packages to fix import errors...
echo Installing compatible pandas version...
%PYTHON_CMD% -m pip install "pandas>=1.5.0,<2.1.0" --force-reinstall
echo Installing compatible numpy version...
%PYTHON_CMD% -m pip install "numpy>=1.21.0,<1.25.0" --force-reinstall
echo Installing compatible urllib3 version...
%PYTHON_CMD% -m pip install "urllib3>=1.26.0,<2.0" --force-reinstall
echo Installing compatible matplotlib version...
%PYTHON_CMD% -m pip install "matplotlib>=3.5.0,<3.8.0" --force-reinstall
echo Installing compatible PySide6 version...
%PYTHON_CMD% -m pip install "PySide6>=6.4.0,<6.6.0" --force-reinstall
echo Installing updated cx_Freeze...
%PYTHON_CMD% -m pip install --upgrade cx_Freeze setuptools wheel

echo.
echo Step 3: Testing pandas imports before build...
%PYTHON_CMD% -c "import pandas; print('✓ pandas:', pandas.__version__)"
if %errorlevel% neq 0 (
    echo ❌ pandas import failed - build will likely fail
    echo Please check pandas installation
)

%PYTHON_CMD% -c "import numpy; print('✓ numpy:', numpy.__version__)"
%PYTHON_CMD% -c "import PySide6; print('✓ PySide6 available')"

echo.
echo Step 4: Trying different build methods...

echo.
echo Method 1: Ultra-minimal setup (addresses import errors)...
%PYTHON_CMD% setup_ultra_minimal.py build
if %errorlevel% == 0 (
    echo ✅ Ultra-minimal setup succeeded!
    goto :test_build
)

echo.
echo Method 2: Fixed setup...
%PYTHON_CMD% setup_cx_freeze_fixed.py build
if %errorlevel% == 0 (
    echo ✅ Fixed setup succeeded!
    goto :test_build
)

echo.
echo Method 3: Minimal setup...
%PYTHON_CMD% setup_cx_freeze_minimal.py build
if %errorlevel% == 0 (
    echo ✅ Minimal setup succeeded!
    goto :test_build
)

echo.
echo Method 4: Simple build script...
%PYTHON_CMD% build_simple.py
if %errorlevel% == 0 (
    echo ✅ Simple build succeeded!
    goto :test_build
)

echo.
echo ❌ All build methods failed!
echo.
echo Troubleshooting suggestions for import errors:
echo 1. Install compatible package versions:
echo    %PYTHON_CMD% -m pip install "pandas>=1.5.0,<2.1.0" --force-reinstall
echo    %PYTHON_CMD% -m pip install "urllib3>=1.26.0,<2.0" --force-reinstall
echo    %PYTHON_CMD% -m pip install "numpy>=1.21.0,<1.25.0" --force-reinstall
echo.
echo 2. Check for missing modules:
echo    %PYTHON_CMD% -c "import pandas, numpy, PySide6, matplotlib"
echo.
echo 3. Try alternative build tools:
echo    %PYTHON_CMD% -m pip install nuitka
echo    nuitka --standalone --windows-disable-console kitchen_app.py
echo.
echo 4. Check the PANDAS_BUILD_ERROR_GUIDE.md for detailed solutions
echo.
pause
exit /b 1

:test_build
echo.
echo Step 5: Testing the build...

REM Find the build directory
set BUILD_DIR=
if exist "build\exe.win-amd64-3.12" set BUILD_DIR=build\exe.win-amd64-3.12
if exist "build\exe.win-amd64-3.13" set BUILD_DIR=build\exe.win-amd64-3.13

if "%BUILD_DIR%"=="" (
    echo ❌ Build directory not found!
    pause
    exit /b 1
)

if exist "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" (
    echo ✅ Executable found: %BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe
    
    REM Get file size
    for %%A in ("%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe") do (
        set /a SIZE_MB=%%~zA/1024/1024
    )
    echo ✅ File size: %SIZE_MB% MB
    
    echo.
    echo ========================================
    echo ✅ BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: %BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo To test the application:
    echo 1. cd %BUILD_DIR%
    echo 2. VARSYS_Kitchen_Dashboard.exe
    echo.
    echo To create installer:
    echo 1. Install Inno Setup 6
    echo 2. Run: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VARSYS_Kitchen_Dashboard_Setup.iss
    echo.
    
    set /p test_now="Test the executable now? (y/N): "
    if /i "%test_now%"=="y" (
        echo Starting application...
        cd "%BUILD_DIR%"
        start VARSYS_Kitchen_Dashboard.exe
        cd ..\..\
    )
    
) else (
    echo ❌ Executable not found in %BUILD_DIR%
    echo Build may have failed silently.
)

echo.
pause
