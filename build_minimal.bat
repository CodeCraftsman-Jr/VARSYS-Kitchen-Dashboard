@echo off
echo ========================================
echo VARSYS Kitchen Dashboard - Minimal Build
echo ========================================
echo.

echo [1/4] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo ✓ Python found
echo.

echo [2/4] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo ✓ Cleaned
echo.

echo [3/4] Building with minimal setup...
echo This should be much faster...
python setup_minimal.py build

if %errorlevel% neq 0 (
    echo.
    echo ❌ BUILD FAILED
    echo Try installing missing packages:
    echo pip install cx_Freeze PySide6 pandas matplotlib numpy
    pause
    exit /b 1
)

echo.
echo [4/4] Checking results...
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
    
    echo.
    echo Creating simple distribution...
    if not exist "dist" mkdir dist
    copy "%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" "dist\" >nul
    
    echo.
    echo ========================================
    echo 🎉 MINIMAL BUILD SUCCESSFUL! 🎉
    echo ========================================
    echo.
    echo Files created:
    echo   📁 Build: %BUILD_DIR%
    echo   📁 Dist: dist\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo Test it by running:
    echo   dist\VARSYS_Kitchen_Dashboard.exe
    echo.
    echo If this works, we can add more features!
    echo ========================================
) else (
    echo ❌ Executable not found in build directory
    pause
    exit /b 1
)

echo.
pause
