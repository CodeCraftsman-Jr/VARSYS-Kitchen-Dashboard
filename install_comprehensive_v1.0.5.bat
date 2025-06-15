@echo off
echo ========================================
echo VARSYS Kitchen Dashboard v1.0.5 Installer
echo Complete Installation with All Features
echo ========================================
echo.

echo Installing VARSYS Kitchen Dashboard...

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\VARSYS Solutions\Kitchen Dashboard
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "VARSYS_Kitchen_Dashboard.exe" "%INSTALL_DIR%\" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy executable. Please run as Administrator.
    pause
    exit /b 1
)

REM Create data directory for user data
set USER_DATA=%USERPROFILE%\Documents\VARSYS Kitchen Dashboard
if not exist "%USER_DATA%" mkdir "%USER_DATA%"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\VARSYS Kitchen Dashboard.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\VARSYS_Kitchen_Dashboard.exe'; $Shortcut.WorkingDirectory = '%USER_DATA%'; $Shortcut.Save()"

REM Create start menu shortcut
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if not exist "%STARTMENU%\VARSYS Solutions" mkdir "%STARTMENU%\VARSYS Solutions"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\VARSYS Solutions\VARSYS Kitchen Dashboard.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\VARSYS_Kitchen_Dashboard.exe'; $Shortcut.WorkingDirectory = '%USER_DATA%'; $Shortcut.Save()"

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo VARSYS Kitchen Dashboard has been installed to:
echo %INSTALL_DIR%
echo.
echo User data will be stored in:
echo %USER_DATA%
echo.
echo Shortcuts created:
echo - Desktop: VARSYS Kitchen Dashboard
echo - Start Menu: VARSYS Solutions ^> VARSYS Kitchen Dashboard
echo.
echo Features included in this installation:
echo - Complete Kitchen Management System
echo - All modules and utilities
echo - Documentation and guides
echo - Sample data and templates
echo - Security features
echo - Backup and restore capabilities
echo.
echo You can now launch the application from the desktop or start menu.
echo.
pause
