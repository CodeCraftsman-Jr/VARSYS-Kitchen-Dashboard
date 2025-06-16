@echo off
echo ========================================
echo Installing Dependencies for v1.1.1
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
echo Step 1: Updating pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo Step 2: Installing core build dependencies...
%PYTHON_CMD% -m pip install --upgrade cx_Freeze
%PYTHON_CMD% -m pip install --upgrade setuptools wheel

echo.
echo Step 3: Installing core application dependencies...
%PYTHON_CMD% -m pip install pandas>=1.5.0
%PYTHON_CMD% -m pip install matplotlib>=3.5.0
%PYTHON_CMD% -m pip install PySide6>=6.0.0
%PYTHON_CMD% -m pip install numpy>=1.22.0
%PYTHON_CMD% -m pip install openpyxl>=3.0.0
%PYTHON_CMD% -m pip install Pillow>=9.0.0

echo.
echo Step 4: Installing network and utility dependencies...
%PYTHON_CMD% -m pip install requests>=2.28.0
%PYTHON_CMD% -m pip install urllib3>=1.26.0
%PYTHON_CMD% -m pip install certifi>=2022.12.7
%PYTHON_CMD% -m pip install python-dateutil>=2.8.2

echo.
echo Step 5: Installing optional dependencies...
%PYTHON_CMD% -m pip install seaborn>=0.12.0
%PYTHON_CMD% -m pip install tqdm>=4.64.0
%PYTHON_CMD% -m pip install python-dotenv>=1.0.0

echo.
echo Step 6: Installing Firebase dependencies (optional)...
%PYTHON_CMD% -m pip install firebase-admin>=6.0.0
if %errorlevel% neq 0 (
    echo ⚠️ Firebase Admin failed - continuing without it
)

%PYTHON_CMD% -m pip install pyrebase4>=4.5.0
if %errorlevel% neq 0 (
    echo ⚠️ Pyrebase4 failed - continuing without it
)

echo.
echo Step 7: Installing security and AI dependencies...
%PYTHON_CMD% -m pip install PyJWT>=2.8.0
%PYTHON_CMD% -m pip install cryptography>=41.0.0
%PYTHON_CMD% -m pip install scikit-learn>=1.3.0

echo.
echo Step 8: Installing Windows-specific dependencies...
%PYTHON_CMD% -m pip install pywin32>=305
%PYTHON_CMD% -m pip install pywin32-ctypes>=0.2.0

echo.
echo ========================================
echo ✅ DEPENDENCY INSTALLATION COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run: build_release_v1.1.1.bat
echo 2. Or run: python setup_cx_freeze.py build
echo.
pause
