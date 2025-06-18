# VARSYS Kitchen Dashboard Professional Build Script
# Compatible with Python 3.12 and 3.13

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VARSYS Kitchen Dashboard Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Determine Python command to use
$pythonCmd = $null

# Check for Python 3.12
try {
    $version = & py -3.12 --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Found Python 3.12: $version" -ForegroundColor Green
        $pythonCmd = "py -3.12"
    }
} catch {
    # Python 3.12 not available
}

# If Python 3.12 not found, check for Python 3.13
if (-not $pythonCmd) {
    try {
        $version = & python --version 2>$null
        if ($version -match "3\.13") {
            Write-Host "✓ Found Python 3.13: $version" -ForegroundColor Green
            $pythonCmd = "python"
        }
    } catch {
        # Python 3.13 not available
    }
}

# If no compatible Python found, exit
if (-not $pythonCmd) {
    Write-Host "❌ ERROR: Neither Python 3.12 nor 3.13 found!" -ForegroundColor Red
    Write-Host "Please install Python 3.12 or 3.13" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Installing/Updating build dependencies..." -ForegroundColor Yellow

try {
    # Upgrade pip
    & $pythonCmd -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip" }
    
    # Install cx_Freeze
    & $pythonCmd -m pip install --upgrade cx_Freeze
    if ($LASTEXITCODE -ne 0) { throw "Failed to install cx_Freeze" }
    
    # Install application dependencies
    & $pythonCmd -m pip install -r requirements_build.txt
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements" }
    
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Cleaning previous build..." -ForegroundColor Yellow

# Clean build directories
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "✓ Cleaned build directory" -ForegroundColor Green
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "✓ Cleaned dist directory" -ForegroundColor Green
}

if (Test-Path "installer_output") {
    Remove-Item -Recurse -Force "installer_output"
    Write-Host "✓ Cleaned installer_output directory" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: Building executable..." -ForegroundColor Yellow

try {
    & $pythonCmd setup_cx_freeze.py build
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
    
    Write-Host "✓ Executable built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 4: Creating MSI installer..." -ForegroundColor Yellow

try {
    & $pythonCmd setup_cx_freeze.py bdist_msi
    if ($LASTEXITCODE -ne 0) { throw "MSI creation failed" }
    
    Write-Host "✓ MSI installer created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 5: Creating professional installer (if Inno Setup available)..." -ForegroundColor Yellow

# Check for Inno Setup
$innoSetupPaths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)

$innoSetupExe = $null
foreach ($path in $innoSetupPaths) {
    if (Test-Path $path) {
        $innoSetupExe = $path
        break
    }
}

if ($innoSetupExe) {
    try {
        # Create installer output directory
        if (-not (Test-Path "installer_output")) {
            New-Item -ItemType Directory -Path "installer_output" | Out-Null
        }
        
        & $innoSetupExe "installer_professional.iss"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Professional installer created successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠ Professional installer creation had issues" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Professional installer creation failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Inno Setup not found - skipping professional installer" -ForegroundColor Yellow
    Write-Host "  Install from: https://jrsoftware.org/isinfo.php" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find and display output files
$buildDirs = Get-ChildItem -Path "build" -Directory -Name "exe.win-amd64-*" -ErrorAction SilentlyContinue
if ($buildDirs) {
    $exePath = "build\$($buildDirs[0])\VARSYS_Kitchen_Dashboard.exe"
    Write-Host "Executable: $exePath" -ForegroundColor White
}

$msiFiles = Get-ChildItem -Path "dist" -Filter "*.msi" -ErrorAction SilentlyContinue
if ($msiFiles) {
    Write-Host "MSI Installer: dist\$($msiFiles[0].Name)" -ForegroundColor White
}

$setupFiles = Get-ChildItem -Path "installer_output" -Filter "*.exe" -ErrorAction SilentlyContinue
if ($setupFiles) {
    Write-Host "Professional Installer: installer_output\$($setupFiles[0].Name)" -ForegroundColor White
}

Write-Host ""
Write-Host "To test the executable:" -ForegroundColor Yellow
Write-Host "1. Navigate to the build directory" -ForegroundColor Gray
Write-Host "2. Run VARSYS_Kitchen_Dashboard.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "To install using MSI:" -ForegroundColor Yellow
Write-Host "1. Navigate to the dist directory" -ForegroundColor Gray
Write-Host "2. Run the .msi file as administrator" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"
