# VARSYS Kitchen Dashboard Build Script (PowerShell)
Write-Host "========================================"
Write-Host "VARSYS Kitchen Dashboard Build Script"
Write-Host "========================================"
Write-Host ""

Write-Host "Checking Python installation..."
try {
    $pythonVersion = python --version
    Write-Host $pythonVersion
} catch {
    Write-Host "ERROR: Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Installing/Updating dependencies..."
pip install --upgrade pip

if (Test-Path "requirements.txt") {
    Write-Host "Installing from requirements.txt..."
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found, installing essential packages..."
    pip install pandas matplotlib openpyxl python-dotenv pillow PySide6 pyinstaller
}

pip install pyinstaller
pip install pillow

Write-Host ""
Write-Host "Cleaning previous builds..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "release") { Remove-Item -Recurse -Force "release" }
Get-ChildItem "*.zip" -ErrorAction SilentlyContinue | Remove-Item

Write-Host ""
Write-Host "Creating application icon..."
if (!(Test-Path "assets")) { New-Item -ItemType Directory -Path "assets" }
if (!(Test-Path "assets\icons")) { New-Item -ItemType Directory -Path "assets\icons" }
Write-Host "Icon directory created"

Write-Host ""
Write-Host "Building EXE with cx_Freeze..."
Write-Host "Checking cx_Freeze installation..."

try {
    python -c "import cx_Freeze; print('cx_Freeze found')" 2>$null
    Write-Host "cx_Freeze is available"
} catch {
    Write-Host "Installing cx_Freeze..."
    pip install cx_Freeze
}

Write-Host "Building executable..."
python setup_cx_freeze.py build

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Creating release package..."
New-Item -ItemType Directory -Path "release" -Force
Copy-Item "dist\VARSYS_Kitchen_Dashboard.exe" "release\" -ErrorAction SilentlyContinue
if (Test-Path "README.md") { Copy-Item "README.md" "release\" }
if (Test-Path "RELEASE_NOTES.md") { Copy-Item "RELEASE_NOTES.md" "release\" }
if (Test-Path "requirements.txt") { Copy-Item "requirements.txt" "release\" }

Write-Host ""
Write-Host "Checking build results..."
if (Test-Path "build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe") {
    Write-Host "SUCCESS: EXE created successfully!" -ForegroundColor Green
    $fileSize = (Get-Item "build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe").Length
    Write-Host "Size: $fileSize bytes"

    # Copy to dist folder for consistency
    if (!(Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" }
    Copy-Item "build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe" "dist\" -Force
    Write-Host "Copied to dist folder for consistency"
} else {
    Write-Host "ERROR: EXE not found!" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "Files created:"
Write-Host "   - build\exe.win-amd64-3.10\VARSYS_Kitchen_Dashboard.exe (main executable)"
Write-Host "   - dist\VARSYS_Kitchen_Dashboard.exe (copy for convenience)"
Write-Host "   - release\ (distribution folder)"
Write-Host ""
Write-Host "Ready for distribution!" -ForegroundColor Green
Write-Host ""
Write-Host "NOTE: cx_Freeze was used instead of PyInstaller due to compatibility issues with pandas 2.x"
Write-Host ""
Read-Host "Press Enter to continue"
