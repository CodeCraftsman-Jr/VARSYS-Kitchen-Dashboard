@echo off
setlocal enabledelayedexpansion

echo ========================================
echo VARSYS Kitchen Dashboard Installer Builder
echo ========================================
echo.

REM Check if Inno Setup is installed
set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "!INNO_SETUP_PATH!" (
    echo ERROR: Inno Setup 6 not found at: !INNO_SETUP_PATH!
    echo.
    echo Please install Inno Setup 6 from: https://jrsoftware.org/isinfo.php
    echo Or update the INNO_SETUP_PATH variable in this script.
    echo.
    pause
    exit /b 1
)

REM Check if build directory exists
if not exist "build\exe.win-amd64-3.13" (
    echo ERROR: Build directory not found: build\exe.win-amd64-3.13
    echo.
    echo Please run the cx_Freeze build first:
    echo   python setup_fixed.py build
    echo.
    pause
    exit /b 1
)

REM Check if main executable exists
if not exist "build\exe.win-amd64-3.13\VARSYS_Kitchen_Dashboard.exe" (
    echo ERROR: Main executable not found: build\exe.win-amd64-3.13\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo Please ensure the cx_Freeze build completed successfully.
    echo.
    pause
    exit /b 1
)

REM Create installer output directory
if not exist "installer_output" (
    mkdir installer_output
    echo Created installer_output directory
)

echo Building installer with Inno Setup...
echo.

REM Run Inno Setup compiler
"!INNO_SETUP_PATH!" "VARSYS_Kitchen_Dashboard_Setup.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ INSTALLER BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Installer created in: installer_output\
    echo.
    dir installer_output\*.exe
    echo.
    echo The installer is ready for distribution!
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ INSTALLER BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
