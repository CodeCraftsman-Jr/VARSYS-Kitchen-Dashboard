@echo off
echo ========================================
echo GitHub Release Creator for v1.1.1
echo ========================================
echo.

REM Check if GitHub CLI is installed
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: GitHub CLI not found!
    echo.
    echo Please install GitHub CLI:
    echo 1. Download from: https://cli.github.com/
    echo 2. Install and restart command prompt
    echo 3. Run: gh auth login
    echo.
    pause
    exit /b 1
)

REM Check if user is authenticated
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Not authenticated with GitHub!
    echo.
    echo Please run: gh auth login
    echo.
    pause
    exit /b 1
)

REM Check if release package exists
if not exist "release_v1.1.1" (
    echo ❌ ERROR: Release package not found!
    echo.
    echo Please run build_release_v1.1.1.bat first
    echo.
    pause
    exit /b 1
)

echo ✓ GitHub CLI found and authenticated
echo ✓ Release package found
echo.

REM Show release contents
echo 📦 Release Package Contents:
dir "release_v1.1.1" /b
echo.

REM Confirm release creation
set /p confirm="Create GitHub release v1.1.1? (y/N): "
if /i not "%confirm%"=="y" (
    echo Release creation cancelled.
    pause
    exit /b 0
)

echo.
echo Creating GitHub release...

REM Create the release
cd release_v1.1.1

gh release create v1.1.1 ^
  --title "VARSYS Kitchen Dashboard v1.1.1" ^
  --notes-file RELEASE_NOTES.md ^
  --latest ^
  VARSYS_Kitchen_Dashboard.exe ^
  checksums.txt ^
  build_info.json

REM Add installer if it exists
if exist "VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" (
    echo Adding installer to release...
    gh release upload v1.1.1 VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe
)

cd ..

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo ✅ RELEASE CREATED SUCCESSFULLY!
    echo ========================================
    echo.
    echo 🎉 GitHub release v1.1.1 is now live!
    echo.
    echo 🔗 View release: https://github.com/your-username/VARSYS-Kitchen-Dashboard/releases/tag/v1.1.1
    echo.
    echo 📊 Release includes:
    if exist "release_v1.1.1\VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" (
        echo   ✓ Windows Installer
    )
    echo   ✓ Standalone Executable  
    echo   ✓ Checksums
    echo   ✓ Build Information
    echo.
    echo 🔄 Auto-update system will now detect this release!
    echo.
) else (
    echo.
    echo ❌ ERROR: Failed to create GitHub release
    echo.
    echo Please check:
    echo 1. Repository permissions
    echo 2. Network connection
    echo 3. GitHub CLI authentication
    echo.
)

pause
