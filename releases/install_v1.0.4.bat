@echo off
echo VARSYS Kitchen Dashboard v1.0.4 Installer
echo ==========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\VARSYS_Kitchen_Dashboard"

echo Installing to: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo Copying files...
xcopy /E /I /Y * "%INSTALL_DIR%\" >nul

echo.
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\Desktop\VARSYS Kitchen Dashboard.lnk"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\VARSYS_Kitchen_Dashboard.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo You can now run VARSYS Kitchen Dashboard from:
echo - Desktop shortcut
echo - %INSTALL_DIR%\VARSYS_Kitchen_Dashboard.exe
echo.
pause
