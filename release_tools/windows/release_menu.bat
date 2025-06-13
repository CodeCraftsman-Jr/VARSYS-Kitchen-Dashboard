@echo off
:menu
cls
echo.
echo ========================================
echo  VARSYS Kitchen Dashboard - Release Manager
echo ========================================
echo.
echo Current Status:
for /f "tokens=*" %%a in ('python update_version.py current 2^>nul') do echo   %%a
echo.
echo Available Options:
echo.
echo  1. Show Current Version
echo  2. Increment Patch Version (1.0.3 -> 1.0.4)
echo  3. Increment Minor Version (1.0.3 -> 1.1.0)
echo  4. Increment Major Version (1.0.3 -> 2.0.0)
echo  5. Set Specific Version
echo  6. Build Application Only
echo  7. Create Full Release
echo  8. Clean Build Directory
echo  9. Help
echo  0. Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="0" goto :exit
if "%choice%"=="1" goto :current
if "%choice%"=="2" goto :patch
if "%choice%"=="3" goto :minor
if "%choice%"=="4" goto :major
if "%choice%"=="5" goto :setversion
if "%choice%"=="6" goto :build
if "%choice%"=="7" goto :fullrelease
if "%choice%"=="8" goto :clean
if "%choice%"=="9" goto :help

echo Invalid choice. Please try again.
pause
goto :menu

:current
echo.
echo ========================================
echo Current Version Information
echo ========================================
python update_version.py current
echo.
pause
goto :menu

:patch
echo.
echo ========================================
echo Incrementing Patch Version
echo ========================================
python update_version.py increment patch
echo.
echo Version updated successfully!
pause
goto :menu

:minor
echo.
echo ========================================
echo Incrementing Minor Version
echo ========================================
python update_version.py increment minor
echo.
echo Version updated successfully!
pause
goto :menu

:major
echo.
echo ========================================
echo Incrementing Major Version
echo ========================================
python update_version.py increment major
echo.
echo Version updated successfully!
pause
goto :menu

:setversion
echo.
echo ========================================
echo Set Specific Version
echo ========================================
set /p newversion="Enter new version (e.g., 1.2.0): "
if "%newversion%"=="" (
    echo No version entered. Returning to menu.
    pause
    goto :menu
)
python update_version.py set %newversion%
echo.
echo Version set to %newversion% successfully!
pause
goto :menu

:build
echo.
echo ========================================
echo Building Application
echo ========================================
python release_automation.py build
echo.
echo Build completed! Check the build folder.
pause
goto :menu

:fullrelease
echo.
echo ========================================
echo Create Full Release
echo ========================================
set /p releaseversion="Enter release version (e.g., 1.0.4): "
if "%releaseversion%"=="" (
    echo No version entered. Returning to menu.
    pause
    goto :menu
)
echo.
echo Starting full release process for version %releaseversion%...
echo This will take a few minutes...
echo.
python release_automation.py full %releaseversion%
echo.
echo ========================================
echo Release Process Completed!
echo ========================================
echo.
echo Generated files are in the 'releases' folder:
echo - VARSYS_Kitchen_Dashboard_v%releaseversion%.zip
echo - install_v%releaseversion%.bat
echo - Checksums and release info files
echo.
echo Next Steps:
echo 1. Test the ZIP file in the releases folder
echo 2. Edit RELEASE_NOTES_v%releaseversion%.md if needed
echo 3. Commit and push to GitHub
echo 4. Create GitHub release with the ZIP file
echo.
pause
goto :menu

:clean
echo.
echo ========================================
echo Cleaning Build Directory
echo ========================================
python release_automation.py clean
echo.
echo Build directory cleaned!
pause
goto :menu

:help
echo.
echo ========================================
echo Help - How to Use This Tool
echo ========================================
echo.
echo This tool helps you manage versions and create releases for
echo the VARSYS Kitchen Dashboard application.
echo.
echo Version Types:
echo - Patch (1.0.3 -> 1.0.4): Bug fixes, small improvements
echo - Minor (1.0.3 -> 1.1.0): New features, backward compatible  
echo - Major (1.0.3 -> 2.0.0): Breaking changes, major overhauls
echo.
echo Typical Workflow:
echo 1. Make your code changes
echo 2. Choose option 2, 3, or 4 to update version
echo 3. Choose option 7 to create full release
echo 4. Test the generated ZIP file
echo 5. Upload to GitHub releases
echo.
echo Files Updated Automatically:
echo - __version__.py (version information)
echo - setup_cx_freeze.py (build configuration)
echo - manifest.json (application manifest)
echo.
echo Files Generated:
echo - ZIP package with your application
echo - Installer batch file
echo - Checksums for verification
echo - Release notes template
echo.
pause
goto :menu

:exit
echo.
echo Thank you for using VARSYS Release Manager!
echo.
exit /b 0
