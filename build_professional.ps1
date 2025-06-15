# VARSYS Kitchen Dashboard - Professional Build System (PowerShell)
# Creates installable Windows software with system tray integration

param(
    [string]$Version = "1.0.6",
    [switch]$SkipInstaller = $false,
    [switch]$Verbose = $false
)

# Configuration
$AppName = "VARSYS Kitchen Dashboard"
$BuildType = "Professional"
$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Type] $Message" -ForegroundColor $color
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "VARSYS Kitchen Dashboard - Professional Build System" -ForegroundColor Cyan
Write-Host "Creating installable Windows software with system tray integration" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Build Configuration:"
Write-Host "  Application: $AppName"
Write-Host "  Version: $Version"
Write-Host "  Build Type: $BuildType"
Write-Host "  Date: $(Get-Date)"
Write-Host ""

try {
    # Step 1: Check Python installation
    Write-Status "Checking Python installation..." "INFO"
    if (-not (Test-Command "python")) {
        throw "Python not found! Please install Python 3.8 or higher from https://www.python.org/downloads/"
    }
    $pythonVersion = python --version
    Write-Status "✓ $pythonVersion found" "SUCCESS"
    Write-Host ""

    # Step 2: Install dependencies
    Write-Status "Installing/updating dependencies..." "INFO"
    python -m pip install --upgrade pip | Out-Null
    
    if (Test-Path "requirements.txt") {
        Write-Status "Installing from requirements.txt..." "INFO"
        python -m pip install -r requirements.txt | Out-Null
    } else {
        Write-Status "Installing essential packages..." "INFO"
        python -m pip install pandas matplotlib openpyxl python-dotenv pillow PySide6 cx_Freeze pywin32 | Out-Null
    }
    Write-Status "✓ Dependencies installed" "SUCCESS"
    Write-Host ""

    # Step 3: Clean previous builds
    Write-Status "Cleaning previous builds..." "INFO"
    $dirsToClean = @("build", "dist", "installer_output")
    foreach ($dir in $dirsToClean) {
        if (Test-Path $dir) {
            Remove-Item $dir -Recurse -Force
            Write-Status "Removed old $dir directory" "INFO"
        }
    }
    
    # Remove old ZIP files
    Get-ChildItem "*.zip" -ErrorAction SilentlyContinue | Remove-Item -Force
    Write-Status "✓ Build directories cleaned" "SUCCESS"
    Write-Host ""

    # Step 4: Verify required files
    Write-Status "Verifying required files..." "INFO"
    $requiredFiles = @(
        "kitchen_app.py",
        "system_tray_service.py", 
        "setup_cx_freeze.py",
        "assets\icons\vasanthkitchen.ico"
    )
    
    $missingFiles = @()
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        throw "Required files missing: $($missingFiles -join ', ')"
    }
    Write-Status "✓ All required files found" "SUCCESS"
    Write-Host ""

    # Step 5: Build executable
    Write-Status "Building executable with cx_Freeze..." "INFO"
    Write-Status "This may take several minutes..." "INFO"
    
    $buildResult = python setup_cx_freeze.py build
    if ($LASTEXITCODE -ne 0) {
        throw "Executable build failed!"
    }
    
    # Find build directory
    $buildDirs = Get-ChildItem "build\exe.*" -Directory -ErrorAction SilentlyContinue
    if ($buildDirs.Count -eq 0) {
        throw "Build directory not found!"
    }
    $buildDir = $buildDirs[0].FullName
    Write-Status "✓ Executable built in: $buildDir" "SUCCESS"
    Write-Host ""

    # Step 6: Verify executables
    Write-Status "Verifying built executables..." "INFO"
    $mainExe = Join-Path $buildDir "VARSYS_Kitchen_Dashboard.exe"
    $serviceExe = Join-Path $buildDir "VARSYS_Kitchen_Service.exe"
    
    if (-not (Test-Path $mainExe)) {
        throw "Main executable not found!"
    }
    if (-not (Test-Path $serviceExe)) {
        throw "Service executable not found!"
    }
    
    $mainSize = [math]::Round((Get-Item $mainExe).Length / 1MB, 1)
    $serviceSize = [math]::Round((Get-Item $serviceExe).Length / 1MB, 1)
    
    Write-Status "✓ Main executable: $mainSize MB" "SUCCESS"
    Write-Status "✓ Service executable: $serviceSize MB" "SUCCESS"
    Write-Host ""

    # Step 7: Create distribution packages
    Write-Status "Creating distribution packages..." "INFO"
    New-Item -ItemType Directory -Path "dist" -Force | Out-Null
    
    # Copy executables to dist
    Copy-Item $mainExe "dist\" -Force
    Copy-Item $serviceExe "dist\" -Force
    
    # Create portable package
    $portableDir = "dist\VARSYS_Kitchen_Dashboard_v${Version}_Portable"
    New-Item -ItemType Directory -Path $portableDir -Force | Out-Null
    New-Item -ItemType Directory -Path "$portableDir\app" -Force | Out-Null
    
    # Copy all build files
    Copy-Item "$buildDir\*" "$portableDir\app\" -Recurse -Force
    
    # Create portable launcher
    $launcherContent = @"
@echo off
title VARSYS Kitchen Dashboard v$Version
echo Starting VARSYS Kitchen Dashboard...
cd /d "%~dp0\app"
start "" "VARSYS_Kitchen_Service.exe"
echo Kitchen Dashboard started in system tray.
echo You can close this window.
pause
"@
    Set-Content "$portableDir\Start_Kitchen_Dashboard.bat" $launcherContent
    
    # Copy documentation
    $docs = @("README.md", "LICENSE", "RELEASE_NOTES.md")
    foreach ($doc in $docs) {
        if (Test-Path $doc) {
            Copy-Item $doc $portableDir -Force
        }
    }
    
    Write-Status "✓ Portable package created" "SUCCESS"
    Write-Host ""

    # Step 8: Create installer (if not skipped)
    if (-not $SkipInstaller) {
        Write-Status "Creating professional installer..." "INFO"
        
        # Check for Inno Setup
        $innoSetupPaths = @(
            "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            "C:\Program Files\Inno Setup 6\ISCC.exe",
            "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            "C:\Program Files\Inno Setup 5\ISCC.exe"
        )
        
        $innoSetupPath = $null
        foreach ($path in $innoSetupPaths) {
            if (Test-Path $path) {
                $innoSetupPath = $path
                break
            }
        }
        
        if ($innoSetupPath) {
            Write-Status "✓ Inno Setup found: $innoSetupPath" "SUCCESS"
            
            if (Test-Path "installer_script.iss") {
                Write-Status "Creating Windows installer..." "INFO"
                & $innoSetupPath "installer_script.iss"
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Status "✓ Professional installer created successfully" "SUCCESS"
                    
                    # Find installer file
                    $installerFiles = Get-ChildItem "installer_output\*.exe" -ErrorAction SilentlyContinue
                    if ($installerFiles) {
                        $installerFile = $installerFiles[0]
                        $installerSize = [math]::Round($installerFile.Length / 1MB, 1)
                        Write-Status "✓ Installer: $($installerFile.Name) ($installerSize MB)" "SUCCESS"
                    }
                } else {
                    Write-Status "⚠ Installer creation failed" "WARNING"
                }
            } else {
                Write-Status "⚠ Installer script not found - skipping installer creation" "WARNING"
            }
        } else {
            Write-Status "⚠ Inno Setup not found - skipping installer creation" "WARNING"
            Write-Status "  Download from: https://jrsoftware.org/isinfo.php" "INFO"
        }
    } else {
        Write-Status "Skipping installer creation (--SkipInstaller specified)" "INFO"
    }
    Write-Host ""

    # Create ZIP archive
    Write-Status "Creating ZIP archive..." "INFO"
    $zipPath = "dist\VARSYS_Kitchen_Dashboard_v${Version}_Portable.zip"
    Compress-Archive -Path "$portableDir\*" -DestinationPath $zipPath -Force
    $zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
    Write-Status "✓ ZIP archive created: $zipSize MB" "SUCCESS"
    Write-Host ""

    # Build summary
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host "🎉 PROFESSIONAL BUILD COMPLETED SUCCESSFULLY! 🎉" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Build Summary:"
    Write-Host "  Application: $AppName v$Version"
    Write-Host "  Build Type: $BuildType"
    Write-Host "  Build Date: $(Get-Date)"
    Write-Host ""
    Write-Host "Files Created:"
    Write-Host "  📁 Build Directory: $buildDir"
    Write-Host "  📁 Distribution: dist\"
    Write-Host "  🎯 Main Executable: VARSYS_Kitchen_Dashboard.exe ($mainSize MB)"
    Write-Host "  🔧 Service Executable: VARSYS_Kitchen_Service.exe ($serviceSize MB)"
    Write-Host "  📦 Portable Package: VARSYS_Kitchen_Dashboard_v${Version}_Portable.zip ($zipSize MB)"
    
    $installerFiles = Get-ChildItem "installer_output\*.exe" -ErrorAction SilentlyContinue
    if ($installerFiles) {
        $installerFile = $installerFiles[0]
        $installerSize = [math]::Round($installerFile.Length / 1MB, 1)
        Write-Host "  💿 Professional Installer: $($installerFile.Name) ($installerSize MB)"
    }
    
    Write-Host ""
    Write-Host "Features Included:"
    Write-Host "  ✓ System tray integration"
    Write-Host "  ✓ Auto-startup capability"
    Write-Host "  ✓ Enhanced auto-updater"
    Write-Host "  ✓ Firebase cloud sync"
    Write-Host "  ✓ Professional Windows integration"
    Write-Host "  ✓ Subscription-based access"
    Write-Host ""
    Write-Host "Your VARSYS Kitchen Dashboard is now ready for distribution!" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host "❌ BUILD FAILED" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the error messages above and try again." -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    exit 1
}

Write-Host ""
Read-Host "Press Enter to continue"
