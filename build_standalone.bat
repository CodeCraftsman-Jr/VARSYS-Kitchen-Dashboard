@echo off
echo ========================================
echo VARSYS Kitchen Dashboard - Standalone EXE
echo Creating single executable file
echo ========================================
echo.

echo [1/4] Checking Python and packages...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo Installing/updating required packages...
pip install cx_Freeze PySide6 pandas matplotlib openpyxl
echo ✓ Packages ready
echo.

echo [2/4] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "VARSYS_Kitchen_Dashboard_Standalone.exe" del "VARSYS_Kitchen_Dashboard_Standalone.exe"
echo ✓ Cleaned
echo.

echo [3/4] Building standalone executable...
echo This creates a single .exe file with everything included...
echo Please wait, this may take several minutes...

python setup_standalone.py build

if %errorlevel% neq 0 (
    echo.
    echo ❌ STANDALONE BUILD FAILED
    echo Check the error above for details.
    pause
    exit /b 1
)

echo.
echo [4/4] Extracting standalone executable...

REM Find the build directory
for /d %%i in (build\exe.*) do (
    set BUILD_DIR=%%i
    goto :found_build
)

echo ❌ No build directory found
pause
exit /b 1

:found_build
if exist "%BUILD_DIR%\VARSYS_Kitchen_Dashboard_Standalone.exe" (
    REM Copy the standalone executable to root directory
    copy "%BUILD_DIR%\VARSYS_Kitchen_Dashboard_Standalone.exe" "." >nul
    
    REM Get file size
    for %%I in ("VARSYS_Kitchen_Dashboard_Standalone.exe") do set SIZE=%%~zI
    set /a SIZE_MB=%SIZE%/1048576
    
    echo.
    echo ========================================
    echo 🎉 STANDALONE EXECUTABLE CREATED! 🎉
    echo ========================================
    echo.
    echo File created:
    echo   🎯 VARSYS_Kitchen_Dashboard_Standalone.exe (!SIZE_MB! MB)
    echo.
    echo This is a single file that contains everything:
    echo   ✓ Python runtime
    echo   ✓ All dependencies
    echo   ✓ Your application code
    echo   ✓ Data files and assets
    echo   ✓ Fixed auto-updater system
    echo.
    echo You can now:
    echo   1. Run: VARSYS_Kitchen_Dashboard_Standalone.exe
    echo   2. Copy this file to any Windows computer
    echo   3. Distribute it without installation
    echo   4. The auto-update system will work properly
    echo.
    echo ========================================
    
    REM Also create a dist folder for consistency
    if not exist "dist" mkdir dist
    copy "VARSYS_Kitchen_Dashboard_Standalone.exe" "dist\" >nul
    echo ✓ Also copied to dist\ folder
    
) else (
    echo ❌ Standalone executable not found in build directory
    echo Available files in build directory:
    dir "%BUILD_DIR%"
    pause
    exit /b 1
)

echo.
echo Test the standalone executable:
echo   VARSYS_Kitchen_Dashboard_Standalone.exe
echo.
pause
