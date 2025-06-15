@echo off
setlocal enabledelayedexpansion

echo ========================================================================
echo VARSYS Kitchen Dashboard - Professional Build System
echo Creating installable Windows software with system tray integration
echo ========================================================================
echo.

REM Set build configuration
set APP_NAME=VARSYS Kitchen Dashboard
set APP_VERSION=1.0.6
set BUILD_TYPE=Professional

echo Build Configuration:
echo   Application: %APP_NAME%
echo   Version: %APP_VERSION%
echo   Build Type: %BUILD_TYPE%
echo   Date: %DATE% %TIME%
echo.

REM Check Python installation
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✓ Python found
echo.

REM Check and install dependencies
echo [2/8] Installing/updating dependencies...
pip install --upgrade pip
if exist "requirements.txt" (
    echo Installing from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing essential packages...
    pip install pandas matplotlib openpyxl python-dotenv pillow PySide6 cx_Freeze
)

REM Install additional build dependencies
pip install cx_Freeze
pip install pywin32
echo ✓ Dependencies installed
echo.

REM Clean previous builds
echo [3/8] Cleaning previous builds...
if exist "build" (
    echo Removing old build directory...
    rmdir /s /q "build"
)
if exist "dist" (
    echo Removing old dist directory...
    rmdir /s /q "dist"
)
if exist "installer_output" (
    echo Removing old installer output...
    rmdir /s /q "installer_output"
)
if exist "*.zip" (
    echo Removing old ZIP files...
    del "*.zip"
)
echo ✓ Build directories cleaned
echo.

REM Verify required files
echo [4/8] Verifying required files...
set MISSING_FILES=0

if not exist "kitchen_app.py" (
    echo ERROR: kitchen_app.py not found!
    set MISSING_FILES=1
)

if not exist "system_tray_service.py" (
    echo ERROR: system_tray_service.py not found!
    set MISSING_FILES=1
)

if not exist "setup_cx_freeze.py" (
    echo ERROR: setup_cx_freeze.py not found!
    set MISSING_FILES=1
)

if not exist "assets\icons\vasanthkitchen.ico" (
    echo ERROR: Application icon not found!
    set MISSING_FILES=1
)

if %MISSING_FILES% equ 1 (
    echo ERROR: Required files missing. Cannot continue build.
    pause
    exit /b 1
)
echo ✓ All required files found
echo.

REM Build executable with cx_Freeze
echo [5/8] Building executable with cx_Freeze...
echo This may take several minutes...
python setup_cx_freeze.py build

if %errorlevel% neq 0 (
    echo ERROR: Executable build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

REM Find the build directory (it might have different names on different systems)
set BUILD_FOUND=0
for /d %%i in (build\exe.*) do (
    set BUILD_DIR=%%i
    set BUILD_FOUND=1
    goto :build_found
)

:build_found
if %BUILD_FOUND% equ 0 (
    echo ERROR: Build directory not found!
    pause
    exit /b 1
)

echo ✓ Executable built in: %BUILD_DIR%
echo.

REM Verify executables
echo [6/8] Verifying built executables...
if not exist "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" (
    echo ERROR: Main executable not found!
    pause
    exit /b 1
)

if not exist "%BUILD_DIR%\VARSYS_Kitchen_Service.exe" (
    echo ERROR: Service executable not found!
    pause
    exit /b 1
)

REM Get file sizes
for %%i in ("%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe") do set MAIN_SIZE=%%~zi
for %%i in ("%BUILD_DIR%\VARSYS_Kitchen_Service.exe") do set SERVICE_SIZE=%%~zi

set /a MAIN_SIZE_MB=%MAIN_SIZE%/1048576
set /a SERVICE_SIZE_MB=%SERVICE_SIZE%/1048576

echo ✓ Main executable: %MAIN_SIZE_MB% MB
echo ✓ Service executable: %SERVICE_SIZE_MB% MB
echo.

REM Create distribution directory
echo [7/8] Creating distribution packages...
if not exist "dist" mkdir dist

REM Copy executables to dist for easy access
copy "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" "dist\" >nul
copy "%BUILD_DIR%\VARSYS_Kitchen_Service.exe" "dist\" >nul

REM Create portable package
echo Creating portable package...
set PORTABLE_DIR=dist\VARSYS_Kitchen_Dashboard_v%APP_VERSION%_Portable
if not exist "%PORTABLE_DIR%" mkdir "%PORTABLE_DIR%"

REM Copy all build files to portable directory
xcopy /E /I /Y "%BUILD_DIR%\*" "%PORTABLE_DIR%\app\" >nul

REM Create portable launcher
echo @echo off > "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo title VARSYS Kitchen Dashboard v%APP_VERSION% >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo echo Starting VARSYS Kitchen Dashboard... >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo cd /d "%%~dp0\app" >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo start "" "VARSYS_Kitchen_Service.exe" >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo echo Kitchen Dashboard started in system tray. >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo echo You can close this window. >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"
echo pause >> "%PORTABLE_DIR%\Start_Kitchen_Dashboard.bat"

REM Copy documentation
if exist "README.md" copy "README.md" "%PORTABLE_DIR%\" >nul
if exist "LICENSE" copy "LICENSE" "%PORTABLE_DIR%\" >nul
if exist "RELEASE_NOTES.md" copy "RELEASE_NOTES.md" "%PORTABLE_DIR%\" >nul

echo ✓ Portable package created
echo.

REM Check for Inno Setup and create installer
echo [8/8] Creating professional installer...
set INNO_SETUP_FOUND=0
set INNO_SETUP_PATH=

REM Check common Inno Setup installation paths
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
    set INNO_SETUP_FOUND=1
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
    set INNO_SETUP_FOUND=1
)
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe
    set INNO_SETUP_FOUND=1
)

if %INNO_SETUP_FOUND% equ 1 (
    echo ✓ Inno Setup found: %INNO_SETUP_PATH%
    
    if exist "installer_script.iss" (
        echo Creating Windows installer...
        "%INNO_SETUP_PATH%" "installer_script.iss"
        
        if %errorlevel% equ 0 (
            echo ✓ Professional installer created successfully
            
            REM Find and display installer info
            for %%i in (installer_output\*.exe) do (
                set INSTALLER_FILE=%%i
                for %%j in ("%%i") do set INSTALLER_SIZE=%%~zj
                set /a INSTALLER_SIZE_MB=!INSTALLER_SIZE!/1048576
                echo ✓ Installer: %%~ni.exe (!INSTALLER_SIZE_MB! MB)
            )
        ) else (
            echo ⚠ Installer creation failed
        )
    ) else (
        echo ⚠ Installer script not found - skipping installer creation
    )
) else (
    echo ⚠ Inno Setup not found - skipping installer creation
    echo   Download from: https://jrsoftware.org/isinfo.php
    echo   Install Inno Setup to create professional installers
)
echo.

REM Create ZIP archive of portable package
echo Creating ZIP archive...
powershell -command "Compress-Archive -Path '%PORTABLE_DIR%\*' -DestinationPath 'dist\VARSYS_Kitchen_Dashboard_v%APP_VERSION%_Portable.zip' -Force"
if %errorlevel% equ 0 (
    echo ✓ ZIP archive created
) else (
    echo ⚠ ZIP creation failed
)
echo.

REM Build summary
echo ========================================================================
echo 🎉 PROFESSIONAL BUILD COMPLETED SUCCESSFULLY! 🎉
echo ========================================================================
echo.
echo Build Summary:
echo   Application: %APP_NAME% v%APP_VERSION%
echo   Build Type: %BUILD_TYPE%
echo   Build Date: %DATE% %TIME%
echo.
echo Files Created:
echo   📁 Build Directory: %BUILD_DIR%
echo   📁 Distribution: dist\
echo   🎯 Main Executable: VARSYS_Kitchen_Dashboard.exe (%MAIN_SIZE_MB% MB)
echo   🔧 Service Executable: VARSYS_Kitchen_Service.exe (%SERVICE_SIZE_MB% MB)
echo   📦 Portable Package: VARSYS_Kitchen_Dashboard_v%APP_VERSION%_Portable.zip
if %INNO_SETUP_FOUND% equ 1 (
    echo   💿 Professional Installer: installer_output\VARSYS_Kitchen_Dashboard_v%APP_VERSION%_Setup.exe
)
echo.
echo Features Included:
echo   ✓ System tray integration
echo   ✓ Auto-startup capability
echo   ✓ Enhanced auto-updater
echo   ✓ Firebase cloud sync
echo   ✓ Professional Windows integration
echo   ✓ Subscription-based access
echo.
echo Your VARSYS Kitchen Dashboard is now ready for distribution!
echo ========================================================================
echo.
pause
