@echo off
title VARSYS Kitchen Dashboard - Release Manager

:: Check if we're in the right directory
if not exist "update_version.py" (
    echo Error: Please run this from the release_tools directory
    echo Current directory: %CD%
    echo.
    echo Expected files: update_version.py, release_automation.py
    pause
    exit /b 1
)

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.x and try again
    pause
    exit /b 1
)

:: Launch the interactive menu
call release_menu.bat
