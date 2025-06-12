@echo off
echo ========================================
echo VARSYS Kitchen Dashboard Build Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo.
echo Installing/Updating dependencies...
pip install --upgrade pip
if exist "requirements.txt" (
    echo Installing from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found, installing essential packages...
    pip install pandas matplotlib openpyxl python-dotenv pillow PySide6 pyinstaller
)
pip install pyinstaller
pip install pillow

echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"
if exist "*.zip" del "*.zip"

echo.
echo Creating application icon...
if not exist "assets" mkdir assets
if not exist "assets\icons" mkdir assets\icons
echo Icon directory created

echo.
echo Building EXE with cx_Freeze...
echo Checking cx_Freeze installation...
python.exe -c "import cx_Freeze; print('cx_Freeze found')" 2>nul
if %errorlevel% neq 0 (
    echo Installing cx_Freeze...
    pip install cx_Freeze
)

echo Building executable...
python setup_cx_freeze.py build

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Creating release package...
mkdir release
copy "dist\VARSYS_Kitchen_Dashboard.exe" "release\"
if exist "README.md" copy "README.md" "release\"
if exist "RELEASE_NOTES.md" copy "RELEASE_NOTES.md" "release\"
if exist "requirements.txt" copy "requirements.txt" "release\"

echo.
echo Checking build results...
if exist "build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe" (
    echo SUCCESS: EXE created successfully!
    for %%I in ("build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe") do echo Size: %%~zI bytes

    REM Copy to dist folder for consistency
    if not exist "dist" mkdir dist
    copy "build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe" "dist\" >nul
    echo Copied to dist folder for consistency
) else (
    echo ERROR: EXE not found!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Files created:
echo    - build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe (main executable)
echo    - dist\VARSYS_Kitchen_Dashboard.exe (copy for convenience)
echo    - release\ (distribution folder)
echo.
echo Ready for distribution!
echo.
echo NOTE: cx_Freeze was used instead of PyInstaller due to compatibility issues with pandas 2.x
echo.
pause
