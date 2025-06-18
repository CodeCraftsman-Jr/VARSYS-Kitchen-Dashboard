@echo off
echo Building VARSYS Kitchen Dashboard Installer...
echo.

REM Simple path check - try common Inno Setup locations
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :found
)

if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
    goto :found
)

echo ERROR: Inno Setup 6 not found!
echo Please install from: https://jrsoftware.org/isinfo.php
pause
exit /b 1

:found
echo Found Inno Setup at: %ISCC%

REM Check build directory
if not exist "build\exe.win-amd64-3.13\VARSYS_Kitchen_Dashboard.exe" (
    echo ERROR: Build not found! Run: python setup_fixed.py build
    pause
    exit /b 1
)

REM Create output directory
if not exist "installer_output" mkdir installer_output

echo Building installer...
%ISCC% VARSYS_Kitchen_Dashboard_Setup.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Installer created in installer_output\
    dir installer_output\*.exe
) else (
    echo.
    echo BUILD FAILED! Check errors above.
)

pause
