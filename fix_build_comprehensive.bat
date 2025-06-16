@echo off
echo ========================================
echo Kitchen Dashboard v1.1.1 - Comprehensive Build Fix
echo ========================================
echo Addresses pandas, urllib3, and import errors
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
echo Step 1: Cleaning previous builds and cache...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d %%i in (modules\__pycache__) do if exist "%%i" rmdir /s /q "%%i"
for /d %%i in (utils\__pycache__) do if exist "%%i" rmdir /s /q "%%i"

echo.
echo Step 2: Running comprehensive import error fix...
%PYTHON_CMD% fix_import_errors.py
if %errorlevel% neq 0 (
    echo ❌ Import error fix failed
    echo Please check the output above for specific issues
    pause
    exit /b 1
)

echo.
echo Step 3: Verifying package installations...
echo Checking pandas...
%PYTHON_CMD% -c "import pandas; print('✓ pandas version:', pandas.__version__)"
if %errorlevel% neq 0 (
    echo ❌ pandas verification failed
    goto :error
)

echo Checking numpy...
%PYTHON_CMD% -c "import numpy; print('✓ numpy version:', numpy.__version__)"
if %errorlevel% neq 0 (
    echo ❌ numpy verification failed
    goto :error
)

echo Checking urllib3...
%PYTHON_CMD% -c "import urllib3; print('✓ urllib3 version:', urllib3.__version__)"
if %errorlevel% neq 0 (
    echo ❌ urllib3 verification failed
    goto :error
)

echo Checking PySide6...
%PYTHON_CMD% -c "import PySide6; print('✓ PySide6 available')"
if %errorlevel% neq 0 (
    echo ❌ PySide6 verification failed
    goto :error
)

echo Checking matplotlib...
%PYTHON_CMD% -c "import matplotlib; print('✓ matplotlib version:', matplotlib.__version__)"
if %errorlevel% neq 0 (
    echo ❌ matplotlib verification failed
    goto :error
)

echo.
echo ✅ All package verifications passed!

echo.
echo Step 4: Attempting builds with different methods...

echo.
echo Method 1: Ultra-minimal setup (best for import errors)...
%PYTHON_CMD% setup_ultra_minimal.py build
if %errorlevel% == 0 (
    echo ✅ Ultra-minimal build succeeded!
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
echo ❌ All cx_Freeze methods failed!
echo.
echo Trying alternative build method...
echo Method 5: Nuitka (if available)...
%PYTHON_CMD% -m pip install nuitka >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Nuitka installed, attempting build...
    nuitka --standalone --windows-disable-console --output-dir=build_nuitka kitchen_app.py
    if %errorlevel% == 0 (
        echo ✅ Nuitka build succeeded!
        echo Executable location: build_nuitka\kitchen_app.dist\kitchen_app.exe
        goto :success
    )
)

goto :error

:test_build
echo.
echo Step 5: Testing the build...

REM Find the build directory
set BUILD_DIR=
if exist "build\exe.win-amd64-3.12" set BUILD_DIR=build\exe.win-amd64-3.12
if exist "build\exe.win-amd64-3.13" set BUILD_DIR=build\exe.win-amd64-3.13

if "%BUILD_DIR%"=="" (
    echo ❌ Build directory not found!
    goto :error
)

if exist "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" (
    echo ✅ Executable found: %BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe
    
    REM Get file size
    for %%A in ("%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe") do (
        set /a SIZE_MB=%%~zA/1024/1024
    )
    echo ✅ File size: %SIZE_MB% MB
    goto :success
) else (
    echo ❌ Executable not found in %BUILD_DIR%
    goto :error
)

:success
echo.
echo ========================================
echo ✅ BUILD SUCCESSFUL!
echo ========================================
echo.
echo The build completed successfully after fixing import errors.
echo.
echo Fixes applied:
echo ✓ Compatible package versions installed
echo ✓ Import errors resolved
echo ✓ Build configuration optimized
echo.
if defined BUILD_DIR (
    echo Executable location: %BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo To test the application:
    echo 1. cd %BUILD_DIR%
    echo 2. VARSYS_Kitchen_Dashboard.exe
    echo.
    set /p test_now="Test the executable now? (y/N): "
    if /i "%test_now%"=="y" (
        echo Starting application...
        cd "%BUILD_DIR%"
        start VARSYS_Kitchen_Dashboard.exe
        cd ..\..\
    )
)
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo ❌ BUILD FAILED
echo ========================================
echo.
echo All build methods failed. This could be due to:
echo.
echo 1. Package compatibility issues:
echo    - Try: %PYTHON_CMD% -m pip install "pandas==1.5.3" --force-reinstall
echo    - Try: %PYTHON_CMD% -m pip install "urllib3==1.26.18" --force-reinstall
echo.
echo 2. Missing dependencies:
echo    - Check: %PYTHON_CMD% -c "import pandas, numpy, PySide6, matplotlib"
echo.
echo 3. cx_Freeze compatibility:
echo    - Try: %PYTHON_CMD% -m pip install --upgrade cx_Freeze
echo    - Consider using PyInstaller or Nuitka instead
echo.
echo 4. Python version issues:
echo    - Try using Python 3.11 if available
echo    - Avoid Python 3.13 if possible (newer, less tested)
echo.
echo For detailed troubleshooting, check:
echo - PANDAS_BUILD_ERROR_GUIDE.md
echo - BUILD_TROUBLESHOOTING_GUIDE.md
echo.
pause
exit /b 1
