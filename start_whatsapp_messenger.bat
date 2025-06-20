@echo off
echo ========================================
echo    WhatsApp Messenger - Standalone
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

echo Python found. Starting WhatsApp Messenger...
echo.

REM Start the GUI version by default
echo Starting GUI version...
echo Press Ctrl+C to stop the messenger
echo.

python whatsapp_messenger_gui.py

echo.
echo WhatsApp Messenger stopped.
pause
