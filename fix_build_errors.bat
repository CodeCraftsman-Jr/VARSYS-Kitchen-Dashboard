@echo off
echo ========================================
echo Fix Build Errors for v1.1.1
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
echo The issue: pandas and urllib import errors in cx_Freeze
echo Solution: Install compatible package versions and use minimal build
echo.

echo Step 1: Cleaning build environment...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo Step 2: Installing compatible pandas version...
%PYTHON_CMD% -m pip install "pandas>=1.5.0,<2.1.0" --force-reinstall
if %errorlevel% neq 0 (
    echo ❌ Failed to install compatible pandas
    goto :error
)

echo.
echo Step 3: Installing compatible numpy...
%PYTHON_CMD% -m pip install "numpy>=1.21.0,<1.25.0" --force-reinstall

echo.
echo Step 4: Installing compatible urllib3...
%PYTHON_CMD% -m pip install "urllib3>=1.26.0,<2.0" --force-reinstall

echo.
echo Step 5: Installing compatible matplotlib...
%PYTHON_CMD% -m pip install "matplotlib>=3.5.0,<3.8.0" --force-reinstall

echo.
echo Step 6: Updating cx_Freeze...
%PYTHON_CMD% -m pip install --upgrade cx_Freeze setuptools wheel

echo.
echo Step 7: Testing pandas imports...
%PYTHON_CMD% -c "import pandas; print('✓ pandas:', pandas.__version__)"
if %errorlevel% neq 0 (
    echo ❌ pandas import failed
    goto :error
)

%PYTHON_CMD% -c "import numpy; print('✓ numpy:', numpy.__version__)"
if %errorlevel% neq 0 (
    echo ❌ numpy import failed
    goto :error
)

echo.
echo Step 8: Running comprehensive fix...
%PYTHON_CMD% fix_pandas_build_error.py
if %errorlevel% neq 0 (
    echo ⚠️ Comprehensive fix had issues, trying manual build...
)

echo.
echo Step 9: Attempting minimal build...
%PYTHON_CMD% -c "
import sys, os
from cx_Freeze import setup, Executable

build_exe_options = {
    'packages': ['PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui', 'pandas', 'numpy'],
    'include_files': [('data/', 'data/'), ('modules/', 'modules/'), ('utils/', 'utils/'), ('__version__.py', '__version__.py')],
    'excludes': ['tkinter', 'unittest', 'test', 'email', 'html', 'http', 'urllib', 'xml'],
    'build_exe': f'build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}',
    'optimize': 1,
    'zip_exclude_packages': ['*']
}

executable = Executable(
    script='kitchen_app.py',
    base='Win32GUI',
    target_name='VARSYS_Kitchen_Dashboard.exe'
)

setup(
    name='VARSYS Kitchen Dashboard',
    version='1.1.1',
    options={'build_exe': build_exe_options},
    executables=[executable]
)
" build

if %errorlevel% == 0 (
    echo ✅ Minimal build succeeded!
    goto :success
) else (
    echo ❌ Minimal build failed
    goto :error
)

:success
echo.
echo ========================================
echo ✅ BUILD SUCCESSFUL!
echo ========================================
echo.

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
    
    echo.
    echo Build completed successfully!
    echo Location: %BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo To test: cd %BUILD_DIR% && VARSYS_Kitchen_Dashboard.exe
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
    goto :error
)

goto :end

:error
echo.
echo ========================================
echo ❌ BUILD FAILED
echo ========================================
echo.
echo The pandas/urllib import errors are complex.
echo.
echo Alternative solutions:
echo 1. Try Python 3.11: py -3.11 -m pip install cx_Freeze
echo 2. Use PyInstaller: pip install pyinstaller
echo 3. Use virtual environment: python -m venv build_env
echo 4. Check the build_report.txt for details
echo.
echo Manual fix steps:
echo 1. pip uninstall pandas numpy matplotlib cx_Freeze
echo 2. pip install "pandas==1.5.3" "numpy==1.24.3" cx_Freeze
echo 3. python setup_minimal_fixed.py build
echo.

:end
pause
