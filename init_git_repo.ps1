# Initialize Git Repository for VARSYS Kitchen Dashboard
# This script sets up the repository for GitHub distribution

Write-Host "🚀 Initializing VARSYS Kitchen Dashboard Git Repository..." -ForegroundColor Green
Write-Host ""

# Check if git is installed
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/windows"
    Read-Host "Press Enter to exit"
    exit 1
}

# Initialize git repository if not already initialized
if (!(Test-Path ".git")) {
    Write-Host "📁 Initializing Git repository..."
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Yellow
}

# Add all files to git
Write-Host "📝 Adding files to Git..."
git add .

# Create initial commit
Write-Host "💾 Creating initial commit..."
$commitMessage = "Initial commit: VARSYS Kitchen Dashboard v1.0.0

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

git commit -m $commitMessage

Write-Host "✅ Initial commit created" -ForegroundColor Green
Write-Host ""

# Instructions for GitHub setup
Write-Host "🌐 Next Steps for GitHub Setup:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Create a new repository on GitHub:" -ForegroundColor White
Write-Host "   - Go to https://github.com/new"
Write-Host "   - Repository name: VARSYS-Kitchen-Dashboard"
Write-Host "   - Description: Professional Kitchen Management Dashboard"
Write-Host "   - Make it Public for open source distribution"
Write-Host "   - Don't initialize with README (we already have one)"
Write-Host ""

Write-Host "2. Connect to GitHub repository:" -ForegroundColor White
Write-Host "   Replace 'your-username' with your actual GitHub username:"
Write-Host "   git remote add origin https://github.com/your-username/VARSYS-Kitchen-Dashboard.git"
Write-Host ""

Write-Host "3. Push to GitHub:" -ForegroundColor White
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host ""

Write-Host "4. Create first release:" -ForegroundColor White
Write-Host "   - Build the executable: .\build.ps1"
Write-Host "   - Go to your GitHub repository"
Write-Host "   - Click 'Releases' → 'Create a new release'"
Write-Host "   - Tag version: v1.0.0"
Write-Host "   - Release title: VARSYS Kitchen Dashboard v1.0.0"
Write-Host "   - Upload the VARSYS_Kitchen_Dashboard.exe file"
Write-Host "   - Publish release"
Write-Host ""

Write-Host "5. Update version.py with your GitHub username:" -ForegroundColor White
Write-Host "   - Edit version.py"
Write-Host "   - Change GITHUB_OWNER = 'your-username' to your actual username"
Write-Host ""

Write-Host "🎉 Repository setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Repository Contents:" -ForegroundColor Cyan
Write-Host "   ✅ Source code with version control"
Write-Host "   ✅ Automatic update system"
Write-Host "   ✅ Professional README.md"
Write-Host "   ✅ MIT License"
Write-Host "   ✅ GitHub Actions for automated builds"
Write-Host "   ✅ Contributing guidelines"
Write-Host "   ✅ .gitignore for Python projects"
Write-Host ""

Write-Host "🔗 After GitHub setup, users can:" -ForegroundColor Cyan
Write-Host "   • Download releases directly from GitHub"
Write-Host "   • Get automatic update notifications"
Write-Host "   • Report issues and request features"
Write-Host "   • Contribute to the project"
Write-Host ""

# Offer to open GitHub
$openGitHub = Read-Host "Would you like to open GitHub in your browser? (y/n)"
if ($openGitHub -eq 'y' -or $openGitHub -eq 'Y') {
    Start-Process "https://github.com/new"
}

Write-Host ""
Write-Host "🍳 VARSYS Kitchen Dashboard is ready for distribution!" -ForegroundColor Green
Read-Host "Press Enter to continue"
