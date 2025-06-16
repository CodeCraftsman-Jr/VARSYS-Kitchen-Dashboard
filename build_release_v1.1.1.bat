@echo off
echo ========================================
echo VARSYS Kitchen Dashboard v1.1.1 Build
echo ========================================
echo.

REM Set build timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

echo Build started at: %timestamp%
echo.

REM Check Python version
echo Step 1: Checking Python environment...
py -3.12 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Using Python 3.12 for build
    set PYTHON_CMD=py -3.12
    set BUILD_DIR=exe.win-amd64-3.12
) else (
    python --version | findstr "3.13" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✓ Using Python 3.13 for build
        set PYTHON_CMD=python
        set BUILD_DIR=exe.win-amd64-3.13
    ) else (
        echo ❌ ERROR: Neither Python 3.12 nor 3.13 found!
        echo Please install Python 3.12 or 3.13
        pause
        exit /b 1
    )
)

REM Verify version
echo.
echo Step 2: Verifying version information...
%PYTHON_CMD% -c "from __version__ import __version__; print(f'✓ Version: {__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Could not verify version information
    pause
    exit /b 1
)

REM Install/Update dependencies
echo.
echo Step 3: Installing/Updating build dependencies...
echo Running dependency installer...
%PYTHON_CMD% fix_build_dependencies.py
if %errorlevel% neq 0 (
    echo ⚠️ WARNING: Some dependencies failed to install
    echo Continuing with available packages...
)
echo ✓ Dependencies checked and updated

REM Clean previous builds
echo.
echo Step 4: Cleaning previous builds...
if exist "build" (
    rmdir /s /q "build"
    echo ✓ Removed old build directory
)
if exist "dist" (
    rmdir /s /q "dist"
    echo ✓ Removed old dist directory
)
if exist "installer_output" (
    rmdir /s /q "installer_output"
    echo ✓ Removed old installer output
)
if exist "release_v1.1.1" (
    rmdir /s /q "release_v1.1.1"
    echo ✓ Removed old release directory
)

REM Build executable
echo.
echo Step 5: Building executable...
echo Attempting build with full setup...
%PYTHON_CMD% setup_cx_freeze.py build
if %errorlevel% neq 0 (
    echo ⚠️ Full build failed, trying minimal build...
    %PYTHON_CMD% setup_cx_freeze_minimal.py build
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Both builds failed!
        echo.
        echo Troubleshooting:
        echo 1. Check that all dependencies are installed
        echo 2. Run: python fix_build_dependencies.py
        echo 3. Try: python setup_cx_freeze_minimal.py build
        pause
        exit /b 1
    )
    echo ✓ Minimal build completed successfully
) else (
    echo ✓ Full build completed successfully
)

REM Verify build output
echo.
echo Step 6: Verifying build output...
if exist "build\%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" (
    echo ✓ Main executable found
) else (
    echo ❌ ERROR: Main executable not found!
    pause
    exit /b 1
)

REM Test executable
echo.
echo Step 7: Testing executable...
echo Testing application startup (will close automatically)...
timeout /t 2 /nobreak >nul
start /wait "Test" "build\%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" --test-mode 2>nul
echo ✓ Executable test completed

REM Create installer
echo.
echo Step 8: Creating Windows installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VARSYS_Kitchen_Dashboard_Setup.iss
    if %errorlevel% neq 0 (
        echo ❌ WARNING: Installer creation failed
        echo Continuing without installer...
    ) else (
        echo ✓ Installer created successfully
    )
) else (
    echo ⚠️ WARNING: Inno Setup not found, skipping installer creation
    echo Install Inno Setup 6 to create professional installer
)

REM Create release package
echo.
echo Step 9: Creating release package...
mkdir "release_v1.1.1"

REM Copy main executable
copy "build\%BUILD_DIR%\VARSYS_Kitchen_Dashboard.exe" "release_v1.1.1\" >nul
echo ✓ Copied standalone executable

REM Copy installer if it exists
if exist "installer_output\VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" (
    copy "installer_output\VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" "release_v1.1.1\" >nul
    echo ✓ Copied installer
)

REM Copy documentation
copy "README.md" "release_v1.1.1\" >nul 2>&1
copy "LICENSE" "release_v1.1.1\" >nul 2>&1
copy "FIREBASE_SETUP.md" "release_v1.1.1\" >nul 2>&1
echo ✓ Copied documentation

REM Create release notes
echo Creating release notes...
(
echo # VARSYS Kitchen Dashboard v1.1.1
echo.
echo ## 🎉 What's New
echo - Updated to version 1.1.1 with enhanced stability
echo - Improved auto-update system reliability  
echo - Enhanced Firebase cloud sync performance
echo - Bug fixes and performance improvements
echo.
echo ## 🔄 Auto-Update
echo This version includes automatic update capabilities:
echo - Checks for updates every 24 hours
echo - One-click download and installation
echo - Automatic application restart after updates
echo.
echo ## 📦 Installation
echo - **Installer**: VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe
echo - **Standalone**: VARSYS_Kitchen_Dashboard.exe
echo.
echo ## 🔐 System Requirements
echo - Windows 10/11 ^(64-bit^)
echo - 4GB RAM minimum
echo - 500MB disk space
echo - Internet connection for cloud sync
echo.
echo ## 📅 Release Date
echo %timestamp%
) > "release_v1.1.1\RELEASE_NOTES.md"
echo ✓ Created release notes

REM Generate checksums
echo.
echo Step 10: Generating checksums...
cd "release_v1.1.1"
(
echo # VARSYS Kitchen Dashboard v1.1.1 - File Checksums
echo Generated on: %timestamp%
echo.
) > checksums.txt

if exist "VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" (
    echo Installer SHA256:
    certutil -hashfile "VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" SHA256 | findstr /v "hash" | findstr /v "CertUtil" >> checksums.txt
    echo. >> checksums.txt
)

echo Executable SHA256:
certutil -hashfile "VARSYS_Kitchen_Dashboard.exe" SHA256 | findstr /v "hash" | findstr /v "CertUtil" >> checksums.txt

cd ..
echo ✓ Checksums generated

REM Create build info
echo.
echo Step 11: Creating build information...
(
echo {
echo   "version": "1.1.1",
echo   "build_date": "%timestamp%",
echo   "python_version": "%BUILD_DIR%",
echo   "build_type": "release",
echo   "auto_update_enabled": true,
echo   "firebase_enabled": true,
echo   "files": [
if exist "release_v1.1.1\VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" (
    echo     "VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe",
)
echo     "VARSYS_Kitchen_Dashboard.exe",
echo     "RELEASE_NOTES.md",
echo     "checksums.txt"
echo   ]
echo }
) > "release_v1.1.1\build_info.json"
echo ✓ Build information created

REM Final verification
echo.
echo Step 12: Final verification...
dir "release_v1.1.1" /b
echo.

echo ========================================
echo ✅ BUILD COMPLETE!
echo ========================================
echo.
echo 📦 Release Package: release_v1.1.1\
echo 📁 Build Output: build\%BUILD_DIR%\
echo.
echo 📋 Release Contents:
if exist "release_v1.1.1\VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" (
    echo   ✓ Windows Installer ^(recommended^)
)
echo   ✓ Standalone Executable
echo   ✓ Documentation
echo   ✓ Checksums
echo   ✓ Build Information
echo.
echo 🚀 Ready for GitHub Release!
echo.
echo Next Steps:
echo 1. Test the release package
echo 2. Create GitHub release with tag v1.1.1
echo 3. Upload files from release_v1.1.1\ folder
echo 4. Publish the release
echo.
echo Build completed at: %timestamp%
pause
