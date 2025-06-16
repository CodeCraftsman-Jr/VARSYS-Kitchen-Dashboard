# VARSYS Kitchen Dashboard Installer Builder (PowerShell)
# Professional Windows Installer Builder Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VARSYS Kitchen Dashboard Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$BuildDir = "build\exe.win-amd64-3.13"
$MainExe = "$BuildDir\VARSYS_Kitchen_Dashboard.exe"
$SetupScript = "VARSYS_Kitchen_Dashboard_Setup.iss"
$OutputDir = "installer_output"

# Function to check if a path exists
function Test-PathExists {
    param([string]$Path, [string]$Description)
    
    if (-not (Test-Path $Path)) {
        Write-Host "ERROR: $Description not found at: $Path" -ForegroundColor Red
        return $false
    }
    return $true
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Inno Setup installation
if (-not (Test-PathExists $InnoSetupPath "Inno Setup 6")) {
    Write-Host ""
    Write-Host "Please install Inno Setup 6 from: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
    Write-Host "Or update the InnoSetupPath variable in this script." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check build directory
if (-not (Test-PathExists $BuildDir "Build directory")) {
    Write-Host ""
    Write-Host "Please run the cx_Freeze build first:" -ForegroundColor Yellow
    Write-Host "  python setup_fixed.py build" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check main executable
if (-not (Test-PathExists $MainExe "Main executable")) {
    Write-Host ""
    Write-Host "Please ensure the cx_Freeze build completed successfully." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check setup script
if (-not (Test-PathExists $SetupScript "Inno Setup script")) {
    Write-Host ""
    Write-Host "Setup script not found. Please ensure $SetupScript exists." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ All prerequisites found!" -ForegroundColor Green
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "Created installer output directory: $OutputDir" -ForegroundColor Green
}

# Build installer
Write-Host "Building installer with Inno Setup..." -ForegroundColor Yellow
Write-Host "Script: $SetupScript" -ForegroundColor Gray
Write-Host "Output: $OutputDir" -ForegroundColor Gray
Write-Host ""

try {
    # Run Inno Setup compiler
    $process = Start-Process -FilePath $InnoSetupPath -ArgumentList "`"$SetupScript`"" -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✅ INSTALLER BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        
        # List created installers
        $installers = Get-ChildItem -Path $OutputDir -Filter "*.exe" | Sort-Object LastWriteTime -Descending
        
        if ($installers.Count -gt 0) {
            Write-Host "Installer(s) created:" -ForegroundColor Cyan
            foreach ($installer in $installers) {
                $sizeKB = [math]::Round($installer.Length / 1024, 2)
                $sizeMB = [math]::Round($installer.Length / 1048576, 2)
                Write-Host "  📦 $($installer.Name)" -ForegroundColor White
                Write-Host "     Size: $sizeMB MB ($sizeKB KB)" -ForegroundColor Gray
                Write-Host "     Path: $($installer.FullName)" -ForegroundColor Gray
                Write-Host ""
            }
            
            Write-Host "🎉 The installer is ready for distribution!" -ForegroundColor Green
            
            # Ask if user wants to open the output directory
            $openDir = Read-Host "Open installer directory? (y/n)"
            if ($openDir -eq 'y' -or $openDir -eq 'Y') {
                Start-Process -FilePath "explorer.exe" -ArgumentList $OutputDir
            }
        } else {
            Write-Host "⚠️  No installer files found in output directory." -ForegroundColor Yellow
        }
        
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "❌ INSTALLER BUILD FAILED!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "Please check the error messages above." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ INSTALLER BUILD ERROR!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
