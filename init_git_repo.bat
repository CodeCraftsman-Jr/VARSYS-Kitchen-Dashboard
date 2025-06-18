@echo off
REM Initialize Git Repository for VARSYS Kitchen Dashboard
REM This script sets up the repository for GitHub distribution

echo.
echo 🚀 Initializing VARSYS Kitchen Dashboard Git Repository...
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/download/windows
    pause
    exit /b 1
)
echo ✅ Git is installed

REM Initialize git repository if not already initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
    echo ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

REM Add all files to git
echo 📝 Adding files to Git...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit: VARSYS Kitchen Dashboard v1.0.0

Features:
- Professional kitchen management dashboard
- Inventory management with low stock alerts
- Budget and expense tracking
- Sales monitoring and analytics
- Automatic update system with GitHub integration
- Modern responsive UI design
- Firebase cloud sync capabilities
- AI-powered insights and recommendations

Built with Python, PySide6, pandas, matplotlib
Uses cx_Freeze for Windows executable generation"

echo ✅ Initial commit created
echo.

REM Instructions for GitHub setup
echo 🌐 Next Steps for GitHub Setup:
echo.
echo 1. Create a new repository on GitHub:
echo    - Go to https://github.com/new
echo    - Repository name: VARSYS-Kitchen-Dashboard
echo    - Description: Professional Kitchen Management Dashboard
echo    - Make it Public for open source distribution
echo    - Don't initialize with README (we already have one)
echo.

echo 2. Connect to GitHub repository:
echo    Replace 'your-username' with your actual GitHub username:
echo    git remote add origin https://github.com/your-username/VARSYS-Kitchen-Dashboard.git
echo.

echo 3. Push to GitHub:
echo    git branch -M main
echo    git push -u origin main
echo.

echo 4. Create first release:
echo    - Build the executable: build.bat
echo    - Go to your GitHub repository
echo    - Click 'Releases' → 'Create a new release'
echo    - Tag version: v1.0.0
echo    - Release title: VARSYS Kitchen Dashboard v1.0.0
echo    - Upload the VARSYS_Kitchen_Dashboard.exe file
echo    - Publish release
echo.

echo 5. Update version.py with your GitHub username:
echo    - Edit version.py
echo    - Change GITHUB_OWNER = 'your-username' to your actual username
echo.

echo 🎉 Repository setup complete!
echo.
echo 📋 Repository Contents:
echo    ✅ Source code with version control
echo    ✅ Automatic update system
echo    ✅ Professional README.md
echo    ✅ MIT License
echo    ✅ GitHub Actions for automated builds
echo    ✅ Contributing guidelines
echo    ✅ .gitignore for Python projects
echo.

echo 🔗 After GitHub setup, users can:
echo    • Download releases directly from GitHub
echo    • Get automatic update notifications
echo    • Report issues and request features
echo    • Contribute to the project
echo.

REM Offer to open GitHub
set /p openGitHub="Would you like to open GitHub in your browser? (y/n): "
if /i "%openGitHub%"=="y" (
    start https://github.com/new
)

echo.
echo 🍳 VARSYS Kitchen Dashboard is ready for distribution!
pause
