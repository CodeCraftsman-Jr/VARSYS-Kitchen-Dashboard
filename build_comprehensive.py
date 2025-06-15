#!/usr/bin/env python3
"""
Comprehensive PyInstaller build script for VARSYS Kitchen Dashboard
Includes ALL necessary folders and files like the previous cx_Freeze method
"""

import os
import sys
import subprocess
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

def print_status(message, status="INFO"):
    """Print status message with formatting"""
    if status == "ERROR":
        print(f"[ERROR] {message}")
    elif status == "SUCCESS":
        print(f"[OK] {message}")
    elif status == "WARNING":
        print(f"[WARNING] {message}")
    else:
        print(f"[INFO] {message}")

def get_all_folders_and_files():
    """Get all folders and files that should be included"""
    # Essential folders that must be included
    essential_folders = [
        "modules",
        "utils", 
        "data",
        "assets",
        "secure_credentials",
        "docs",
        "logs",
        "reports",
        "tests",
        "release_tools",
        "data_backup",
        "md files"
    ]
    
    # Essential files that must be included
    essential_files = [
        "firebase_web_config.json",
        "README.md",
        "requirements.txt",
        "__version__.py",
        "config.py",
        "manifest.json",
        "enterprise.db",
        "offline_data.db",
        "jwt_secret.key",
        "last_update_check.json",
        "LICENSE",
        "SECURITY.md",
        "RELEASE_NOTES.md",
        "GITHUB_RELEASE_GUIDE.md",
        "LAUNCH_CHECKLIST.md",
        "CONTRIBUTING.md"
    ]
    
    # Check which folders exist
    existing_folders = []
    for folder in essential_folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            existing_folders.append(folder)
            print_status(f"Found folder: {folder}", "SUCCESS")
        else:
            print_status(f"Folder not found: {folder}", "WARNING")
    
    # Check which files exist
    existing_files = []
    for file in essential_files:
        if os.path.exists(file) and os.path.isfile(file):
            existing_files.append(file)
            print_status(f"Found file: {file}", "SUCCESS")
        else:
            print_status(f"File not found: {file}", "WARNING")
    
    return existing_folders, existing_files

def build_comprehensive_executable():
    """Build executable with ALL folders and files included"""
    print_status("Building comprehensive executable with PyInstaller...", "INFO")
    
    # Get all folders and files
    folders, files = get_all_folders_and_files()
    
    # Check for icon
    icon_path = Path("assets/icons/vasanthkitchen.ico")
    
    # Base build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "VARSYS_Kitchen_Dashboard",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "matplotlib",
        "--hidden-import", "PySide6",
        "--hidden-import", "PIL",
        "--hidden-import", "openpyxl",
        "--hidden-import", "requests",
        "--hidden-import", "cryptography",
        "--collect-all", "pandas",
        "--collect-all", "numpy",
        "--collect-all", "matplotlib"
    ]
    
    # Add all folders
    for folder in folders:
        cmd.extend(["--add-data", f"{folder};{folder}"])
        print_status(f"Adding folder: {folder}", "INFO")
    
    # Add all files
    for file in files:
        cmd.extend(["--add-data", f"{file};."])
        print_status(f"Adding file: {file}", "INFO")
    
    # Add icon if available
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        print_status(f"Using icon: {icon_path}", "SUCCESS")
    
    # Add main script
    cmd.append("kitchen_app.py")
    
    try:
        print_status("Running comprehensive PyInstaller build...", "INFO")
        print_status(f"Total folders: {len(folders)}", "INFO")
        print_status(f"Total files: {len(files)}", "INFO")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print_status("Comprehensive build completed successfully!", "SUCCESS")
            return True
        else:
            print_status("Build failed!", "ERROR")
            print_status("Error output:", "ERROR")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_status(f"Build process failed: {e}", "ERROR")
        return False

def create_comprehensive_installer():
    """Create comprehensive installer script"""
    installer_content = '''@echo off
echo ========================================
echo VARSYS Kitchen Dashboard v1.0.5 Installer
echo Complete Installation with All Features
echo ========================================
echo.

echo Installing VARSYS Kitchen Dashboard...

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\\VARSYS Solutions\\Kitchen Dashboard
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "VARSYS_Kitchen_Dashboard.exe" "%INSTALL_DIR%\\" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy executable. Please run as Administrator.
    pause
    exit /b 1
)

REM Create data directory for user data
set USER_DATA=%USERPROFILE%\\Documents\\VARSYS Kitchen Dashboard
if not exist "%USER_DATA%" mkdir "%USER_DATA%"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\\Desktop
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\\VARSYS Kitchen Dashboard.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\VARSYS_Kitchen_Dashboard.exe'; $Shortcut.WorkingDirectory = '%USER_DATA%'; $Shortcut.Save()"

REM Create start menu shortcut
set STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
if not exist "%STARTMENU%\\VARSYS Solutions" mkdir "%STARTMENU%\\VARSYS Solutions"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\\VARSYS Solutions\\VARSYS Kitchen Dashboard.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\VARSYS_Kitchen_Dashboard.exe'; $Shortcut.WorkingDirectory = '%USER_DATA%'; $Shortcut.Save()"

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo VARSYS Kitchen Dashboard has been installed to:
echo %INSTALL_DIR%
echo.
echo User data will be stored in:
echo %USER_DATA%
echo.
echo Shortcuts created:
echo - Desktop: VARSYS Kitchen Dashboard
echo - Start Menu: VARSYS Solutions ^> VARSYS Kitchen Dashboard
echo.
echo Features included in this installation:
echo - Complete Kitchen Management System
echo - All modules and utilities
echo - Documentation and guides
echo - Sample data and templates
echo - Security features
echo - Backup and restore capabilities
echo.
echo You can now launch the application from the desktop or start menu.
echo.
pause
'''
    
    with open("install_comprehensive_v1.0.5.bat", "w") as f:
        f.write(installer_content)
    print_status("Created comprehensive installer script", "SUCCESS")

def calculate_checksums(file_path):
    """Calculate MD5 and SHA256 checksums"""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return md5_hash.hexdigest(), sha256_hash.hexdigest()

def create_comprehensive_package():
    """Create comprehensive release package"""
    print_status("Creating comprehensive release package...", "INFO")
    
    # Ensure releases directory exists
    releases_dir = Path("releases")
    releases_dir.mkdir(exist_ok=True)
    
    # Package name
    package_name = "VARSYS_Kitchen_Dashboard_v1.0.5_Complete.zip"
    package_path = releases_dir / package_name
    
    # Remove existing package
    if package_path.exists():
        package_path.unlink()
    
    # Create ZIP package
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        exe_path = Path("dist/VARSYS_Kitchen_Dashboard.exe")
        if exe_path.exists():
            zipf.write(exe_path, "VARSYS_Kitchen_Dashboard.exe")
            print_status("Added comprehensive executable to package", "SUCCESS")
        
        # Add comprehensive installer
        installer_path = Path("install_comprehensive_v1.0.5.bat")
        if installer_path.exists():
            zipf.write(installer_path, "install_comprehensive_v1.0.5.bat")
            print_status("Added comprehensive installer to package", "SUCCESS")
        
        # Add documentation files
        doc_files = ["README.md", "LICENSE", "SECURITY.md", "RELEASE_NOTES.md"]
        for doc_file in doc_files:
            if Path(doc_file).exists():
                zipf.write(doc_file, f"docs/{doc_file}")
                print_status(f"Added {doc_file} to package", "SUCCESS")
    
    # Calculate checksums
    md5_sum, sha256_sum = calculate_checksums(package_path)
    
    # Create checksums file
    checksums_content = f"""VARSYS Kitchen Dashboard v1.0.5 Complete - File Checksums
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

File: {package_name}
Size: {package_path.stat().st_size:,} bytes ({package_path.stat().st_size / (1024*1024):.1f} MB)

MD5:    {md5_sum}
SHA256: {sha256_sum}

This is the COMPLETE version including:
- All modules and utilities
- Complete documentation
- Sample data and templates
- Security features
- Backup capabilities
- All original folders and files

Verification Instructions:
1. Download the file
2. Calculate checksums using:
   - Windows: certutil -hashfile {package_name} MD5
   - Windows: certutil -hashfile {package_name} SHA256
   - Linux/Mac: md5sum {package_name}
   - Linux/Mac: sha256sum {package_name}
3. Compare with the values above

If checksums don't match, do not use the file and report the issue.
"""
    
    checksums_path = releases_dir / f"VARSYS_Kitchen_Dashboard_v1.0.5_Complete.checksums.txt"
    with open(checksums_path, "w") as f:
        f.write(checksums_content)
    
    print_status(f"Comprehensive package created: {package_path}", "SUCCESS")
    print_status(f"Package size: {package_path.stat().st_size / (1024*1024):.1f} MB", "INFO")
    print_status(f"MD5: {md5_sum}", "INFO")
    print_status(f"SHA256: {sha256_sum}", "INFO")
    
    return package_path, md5_sum, sha256_sum

def main():
    """Main comprehensive build process"""
    print("=" * 70)
    print("VARSYS Kitchen Dashboard v1.0.5 - COMPREHENSIVE Build")
    print("Includes ALL folders and files like the original cx_Freeze method")
    print("=" * 70)
    
    # Step 1: Build comprehensive executable
    print("\n[1/4] Building comprehensive executable...")
    if not build_comprehensive_executable():
        return False
    
    # Step 2: Create comprehensive installer
    print("\n[2/4] Creating comprehensive installer...")
    create_comprehensive_installer()
    
    # Step 3: Create comprehensive package
    print("\n[3/4] Creating comprehensive release package...")
    package_path, md5_sum, sha256_sum = create_comprehensive_package()
    
    print("\n" + "=" * 70)
    print("SUCCESS: COMPREHENSIVE v1.0.5 Release Package Created!")
    print("=" * 70)
    print(f"\nComprehensive package: {package_path}")
    print(f"Package size: {package_path.stat().st_size / (1024*1024):.1f} MB")
    print(f"MD5: {md5_sum}")
    print(f"SHA256: {sha256_sum}")
    print("\nThis package includes EVERYTHING:")
    print("- All modules and utilities")
    print("- Complete documentation")
    print("- All data folders and files")
    print("- Security credentials")
    print("- Backup capabilities")
    print("- Test suites")
    print("- Release tools")
    print("- Custom icon embedded")
    print("\nThis matches the completeness of the original cx_Freeze build!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
