# VARSYS Kitchen Dashboard - Release Manager (PowerShell)
param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Version
)

function Show-Help {
    Write-Host "VARSYS Kitchen Dashboard - Release Manager" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\release.ps1 [command] [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  current           - Show current version"
    Write-Host "  patch             - Increment patch version (1.0.0 -> 1.0.1)"
    Write-Host "  minor             - Increment minor version (1.0.0 -> 1.1.0)"
    Write-Host "  major             - Increment major version (1.0.0 -> 2.0.0)"
    Write-Host "  set [version]     - Set specific version (e.g., 1.2.0)"
    Write-Host "  build             - Build application only"
    Write-Host "  release [version] - Prepare release with notes"
    Write-Host "  full [version]    - Complete release process"
    Write-Host "  help              - Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\release.ps1 current"
    Write-Host "  .\release.ps1 patch"
    Write-Host "  .\release.ps1 set 1.1.0"
    Write-Host "  .\release.ps1 full 1.1.0"
    Write-Host ""
}

function Invoke-PythonScript {
    param(
        [string]$Script,
        [string[]]$Arguments
    )
    
    try {
        $process = Start-Process -FilePath "python" -ArgumentList ($Script + " " + ($Arguments -join " ")) -Wait -PassThru -NoNewWindow
        return $process.ExitCode -eq 0
    }
    catch {
        Write-Host "Error running Python script: $_" -ForegroundColor Red
        return $false
    }
}

function Show-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Show-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Show-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Main script logic
if (-not $Command -or $Command -eq "help" -or $Command -eq "-h" -or $Command -eq "--help") {
    Show-Help
    exit 0
}

Write-Host "VARSYS Kitchen Dashboard - Release Manager" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

switch ($Command.ToLower()) {
    "current" {
        Show-Info "Getting current version..."
        Invoke-PythonScript "update_version.py" @("current")
    }
    
    "patch" {
        Show-Info "Incrementing patch version..."
        if (Invoke-PythonScript "update_version.py" @("increment", "patch")) {
            Show-Success "Patch version incremented successfully"
        } else {
            Show-Error "Failed to increment patch version"
        }
    }
    
    "minor" {
        Show-Info "Incrementing minor version..."
        if (Invoke-PythonScript "update_version.py" @("increment", "minor")) {
            Show-Success "Minor version incremented successfully"
        } else {
            Show-Error "Failed to increment minor version"
        }
    }
    
    "major" {
        Show-Info "Incrementing major version..."
        if (Invoke-PythonScript "update_version.py" @("increment", "major")) {
            Show-Success "Major version incremented successfully"
        } else {
            Show-Error "Failed to increment major version"
        }
    }
    
    "set" {
        if (-not $Version) {
            Show-Error "Version number required"
            Write-Host "Usage: .\release.ps1 set 1.2.0" -ForegroundColor Yellow
            exit 1
        }
        Show-Info "Setting version to $Version..."
        if (Invoke-PythonScript "update_version.py" @("set", $Version)) {
            Show-Success "Version set to $Version successfully"
        } else {
            Show-Error "Failed to set version"
        }
    }
    
    "build" {
        Show-Info "Building application..."
        if (Invoke-PythonScript "release_automation.py" @("build")) {
            Show-Success "Application built successfully"
        } else {
            Show-Error "Build failed"
        }
    }
    
    "release" {
        if (-not $Version) {
            Show-Error "Version number required"
            Write-Host "Usage: .\release.ps1 release 1.2.0" -ForegroundColor Yellow
            exit 1
        }
        Show-Info "Preparing release $Version..."
        if (Invoke-PythonScript "update_version.py" @("release", $Version)) {
            Show-Success "Release $Version prepared successfully"
        } else {
            Show-Error "Failed to prepare release"
        }
    }
    
    "full" {
        if (-not $Version) {
            Show-Error "Version number required"
            Write-Host "Usage: .\release.ps1 full 1.2.0" -ForegroundColor Yellow
            exit 1
        }
        Show-Info "Starting full release process for version $Version..."
        if (Invoke-PythonScript "release_automation.py" @("full", $Version)) {
            Show-Success "Full release process completed successfully"
            Write-Host ""
            Write-Host "🎉 Release v$Version is ready!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "1. Test the release package in the 'releases' folder"
            Write-Host "2. Update release notes if needed"
            Write-Host "3. Commit and push changes to GitHub"
            Write-Host "4. Create GitHub release with the package"
        } else {
            Show-Error "Full release process failed"
        }
    }
    
    default {
        Show-Error "Invalid command: $Command"
        Write-Host "Use '.\release.ps1 help' for available commands" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
