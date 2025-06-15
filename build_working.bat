@echo off
echo ========================================
echo VARSYS Kitchen Dashboard - Working Build
echo Avoiding numpy import issues
echo ========================================
echo.

echo [1/5] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo ✓ Python found
echo.

echo [2/5] Installing required packages...
echo Installing cx_Freeze and PySide6...
pip install cx_Freeze PySide6 pandas matplotlib openpyxl
echo ✓ Packages installed
echo.

echo [3/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo ✓ Cleaned
echo.

echo [4/5] Building with working setup (avoiding numpy issues)...
echo This should work without numpy import errors...
python setup_working.py build

if %errorlevel% neq 0 (
    echo.
    echo ❌ BUILD FAILED
    echo Check the error above for details.
    pause
    exit /b 1
)

echo.
echo [5/5] Creating distribution...
for /d %%i in (build\exe.*) do (
    set BUILD_DIR=%%i
    goto :found_build
)

echo ❌ No build directory found
pause
exit /b 1

:found_build
if exist "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" (
    for %%I in ("%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe") do set SIZE=%%~zI
    set /a SIZE_MB=%SIZE%/1048576
    echo ✓ Executable created: !SIZE_MB! MB
    
    echo Creating distribution folder...
    if not exist "dist" mkdir dist
    copy "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" "dist\" >nul
    
    REM Copy all dependencies
    echo Copying dependencies...
    xcopy /E /I /Y "%BUILD_DIR%\*" "dist\" >nul
    
    echo.
    echo ========================================
    echo 🎉 WORKING BUILD SUCCESSFUL! 🎉
    echo ========================================
    echo.
    echo Files created:
    echo   📁 Build: %BUILD_DIR%
    echo   📁 Dist: dist\ (complete package)
    echo   🎯 Main: dist\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo Test it by running:
    echo   dist\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo If this works, your auto-update system is also fixed!
    echo ========================================
) else (
    echo ❌ Executable not found in build directory
    pause
    exit /b 1
)

echo.
pause
