#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VARSYS Kitchen Dashboard - Release Automation Script
Automates the complete release process including building, packaging, and GitHub release
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
import datetime
from pathlib import Path
from update_version import VersionUpdater

class ReleaseAutomation:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent  # Go up two levels from release_tools/scripts
        self.build_dir = self.base_dir / "build"
        self.dist_dir = self.base_dir / "dist"
        self.releases_dir = self.base_dir / "releases"
        
        # Ensure directories exist
        self.releases_dir.mkdir(exist_ok=True)
        
    def clean_build_directories(self):
        """Clean previous build artifacts"""
        print("Cleaning build directories...")

        directories_to_clean = [self.build_dir, self.dist_dir]

        for directory in directories_to_clean:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"   Cleaned: {directory}")

        print("SUCCESS: Build directories cleaned")
    
    def build_application(self):
        """Build the application using cx_Freeze with icon"""
        print("Building application...")

        try:
            # Check if icon-enabled build script exists
            icon_build_script = self.base_dir / "build_with_icon.py"
            if icon_build_script.exists():
                print("Using icon-enabled build script...")
                result = subprocess.run([
                    sys.executable, "build_with_icon.py"
                ], cwd=self.base_dir, capture_output=True, text=True)
            else:
                print("Using standard build script...")
                result = subprocess.run([
                    sys.executable, "setup_cx_freeze.py", "build"
                ], cwd=self.base_dir, capture_output=True, text=True)

            if result.returncode == 0:
                print("SUCCESS: Application built successfully")
                return True
            else:
                print(f"ERROR: Build failed:")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"ERROR: Build error: {e}")
            return False
    
    def copy_additional_files(self, build_path):
        """Copy additional files to the build directory"""
        print("Copying additional files...")
        
        additional_files = [
            "README.md",
            "LICENSE",
            "RELEASE_NOTES.md",
            "requirements.txt"
        ]
        
        for file_name in additional_files:
            source_file = self.base_dir / file_name
            if source_file.exists():
                dest_file = build_path / file_name
                shutil.copy2(source_file, dest_file)
                print(f"   Copied: {file_name}")
        
        # Copy documentation
        docs_dir = self.base_dir / "docs"
        if docs_dir.exists():
            dest_docs = build_path / "docs"
            shutil.copytree(docs_dir, dest_docs, dirs_exist_ok=True)
            print("   Copied: docs directory")
        
        print("SUCCESS: Additional files copied")
    
    def create_release_package(self, version):
        """Create a ZIP package for release"""
        print("Creating release package...")

        # Find the build directory
        build_path = None
        if self.build_dir.exists():
            for item in self.build_dir.iterdir():
                if item.is_dir() and "exe." in item.name:
                    build_path = item
                    break

        if not build_path or not build_path.exists():
            print("ERROR: Build directory not found")
            return None
        
        # Copy additional files
        self.copy_additional_files(build_path)
        
        # Create ZIP package
        package_name = f"VARSYS_Kitchen_Dashboard_v{version}.zip"
        package_path = self.releases_dir / package_name
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(build_path):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(build_path)
                    zipf.write(file_path, arc_name)
        
        print(f"SUCCESS: Release package created: {package_path}")
        return package_path
    
    def create_installer_script(self, version):
        """Create a simple installer script"""
        installer_content = f'''@echo off
echo VARSYS Kitchen Dashboard v{version} Installer
echo ==========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\\VARSYS_Kitchen_Dashboard"

echo Installing to: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo Copying files...
xcopy /E /I /Y * "%INSTALL_DIR%\\" >nul

echo.
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\\Desktop\\VARSYS Kitchen Dashboard.lnk"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\VARSYS_Kitchen_Dashboard.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo You can now run VARSYS Kitchen Dashboard from:
echo - Desktop shortcut
echo - %INSTALL_DIR%\\VARSYS_Kitchen_Dashboard.exe
echo.
pause
'''
        
        installer_path = self.releases_dir / f"install_v{version}.bat"
        with open(installer_path, 'w') as f:
            f.write(installer_content)
        
        print(f"SUCCESS: Installer script created: {installer_path}")
        return installer_path
    
    def generate_checksums(self, package_path):
        """Generate checksums for the release package"""
        print("Generating checksums...")
        
        import hashlib
        
        checksums = {}
        
        # Generate MD5 and SHA256 checksums
        with open(package_path, 'rb') as f:
            content = f.read()
            checksums['md5'] = hashlib.md5(content).hexdigest()
            checksums['sha256'] = hashlib.sha256(content).hexdigest()
        
        # Save checksums to file
        checksum_file = package_path.with_suffix('.checksums.txt')
        with open(checksum_file, 'w') as f:
            f.write(f"VARSYS Kitchen Dashboard v{package_path.stem.split('_v')[1]} Checksums\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"File: {package_path.name}\n")
            f.write(f"MD5:    {checksums['md5']}\n")
            f.write(f"SHA256: {checksums['sha256']}\n")
        
        print(f"SUCCESS: Checksums saved: {checksum_file}")
        return checksums
    
    def create_release_info(self, version, package_path, checksums):
        """Create release information JSON"""
        release_info = {
            "version": version,
            "release_date": datetime.datetime.now().isoformat(),
            "package_name": package_path.name,
            "package_size": package_path.stat().st_size,
            "checksums": checksums,
            "download_url": f"https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/releases/download/v{version}/{package_path.name}",
            "system_requirements": {
                "os": ["Windows 10", "Windows 11"],
                "architecture": ["x64"],
                "ram": "4GB minimum",
                "disk_space": "500MB"
            }
        }
        
        info_file = self.releases_dir / f"release_info_v{version}.json"
        with open(info_file, 'w') as f:
            json.dump(release_info, f, indent=2)
        
        print(f"SUCCESS: Release info created: {info_file}")
        return release_info
    
    def full_release_process(self, version, release_type="stable"):
        """Execute the complete release process"""
        print(f"Starting full release process for version {version}")
        print("=" * 60)
        
        # Step 1: Update version
        print("\n[1/8] Updating version...")
        updater = VersionUpdater()
        updater.update_version(version, release_type)

        # Step 2: Clean build directories
        print("\n[2/8] Cleaning build directories...")
        self.clean_build_directories()

        # Step 3: Build application
        print("\n[3/8] Building application...")
        if not self.build_application():
            print("ERROR: Release process failed at build step")
            return False

        # Step 4: Create release package
        print("\n[4/8] Creating release package...")
        package_path = self.create_release_package(version)
        if not package_path:
            print("ERROR: Release process failed at packaging step")
            return False

        # Step 5: Create installer
        print("\n[5/8] Creating installer...")
        installer_path = self.create_installer_script(version)

        # Step 6: Generate checksums
        print("\n[6/8] Generating checksums...")
        checksums = self.generate_checksums(package_path)

        # Step 7: Create release info
        print("\n[7/8] Creating release information...")
        release_info = self.create_release_info(version, package_path, checksums)

        # Step 8: Create release notes
        print("\n[8/8] Creating release notes...")
        updater.create_release_notes(version)
        
        print("\n" + "=" * 60)
        print(f"SUCCESS: Release v{version} completed successfully!")
        print("\nGenerated files:")
        print(f"   Package: {package_path}")
        print(f"   Installer: {installer_path}")
        print(f"   Checksums: {package_path.with_suffix('.checksums.txt')}")
        print(f"   Release Info: {self.releases_dir / f'release_info_v{version}.json'}")
        
        print("\nNext steps:")
        print("1. Test the release package")
        print("2. Update release notes if needed")
        print("3. Commit and push changes to GitHub")
        print("4. Create GitHub release with the package")
        print("5. Update download links in documentation")
        
        return True

def main():
    automation = ReleaseAutomation()
    
    if len(sys.argv) < 2:
        print("VARSYS Kitchen Dashboard - Release Automation")
        print("\nUsage:")
        print("  python release_automation.py <command> [options]")
        print("\nCommands:")
        print("  build                     - Build application only")
        print("  package <version>         - Create release package")
        print("  full <version> [type]     - Complete release process")
        print("  clean                     - Clean build directories")
        print("\nExamples:")
        print("  python release_automation.py build")
        print("  python release_automation.py package 1.1.0")
        print("  python release_automation.py full 1.1.0 stable")
        return
    
    command = sys.argv[1].lower()
    
    if command == "build":
        automation.clean_build_directories()
        automation.build_application()
        
    elif command == "package" and len(sys.argv) >= 3:
        version = sys.argv[2]
        automation.create_release_package(version)
        
    elif command == "full" and len(sys.argv) >= 3:
        version = sys.argv[2]
        release_type = sys.argv[3] if len(sys.argv) >= 4 else "stable"
        automation.full_release_process(version, release_type)
        
    elif command == "clean":
        automation.clean_build_directories()
        
    else:
        print("ERROR: Invalid command or missing arguments")
        print("Use 'python release_automation.py' for help")

if __name__ == "__main__":
    main()
