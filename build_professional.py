#!/usr/bin/env python3
"""
Professional Build Script for VARSYS Kitchen Dashboard
Creates executable with cx_Freeze and professional installer with Inno Setup
Includes system tray integration, auto-startup, and proper update mechanism
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
import time

class ProfessionalBuilder:
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.installer_dir = self.project_root / "installer_output"
        self.exe_dir = self.build_dir / "exe"
        
        # Version info
        self.version = "1.0.6"
        self.app_name = "VARSYS Kitchen Dashboard"
        
    def print_status(self, message, status="INFO"):
        """Print formatted status message"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
    
    def clean_build_directories(self):
        """Clean previous build artifacts"""
        self.print_status("Cleaning previous build artifacts...")
        
        directories_to_clean = [
            self.build_dir,
            self.dist_dir,
            self.installer_dir
        ]
        
        for directory in directories_to_clean:
            if directory.exists():
                shutil.rmtree(directory)
                self.print_status(f"Removed {directory}")
        
        # Create fresh directories
        for directory in directories_to_clean:
            directory.mkdir(parents=True, exist_ok=True)
            self.print_status(f"Created {directory}")
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        self.print_status("Checking build dependencies...")
        
        # Check Python packages
        required_packages = [
            'cx_Freeze', 'PySide6', 'pandas', 'matplotlib', 
            'numpy', 'openpyxl', 'requests', 'cryptography'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').lower())
                self.print_status(f"✓ {package} found")
            except ImportError:
                missing_packages.append(package)
                self.print_status(f"✗ {package} missing", "ERROR")
        
        if missing_packages:
            self.print_status(f"Installing missing packages: {', '.join(missing_packages)}")
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
        
        # Check for Inno Setup
        inno_setup_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe"
        ]
        
        self.inno_setup_path = None
        for path in inno_setup_paths:
            if os.path.exists(path):
                self.inno_setup_path = path
                self.print_status(f"✓ Inno Setup found at {path}")
                break
        
        if not self.inno_setup_path:
            self.print_status("⚠ Inno Setup not found - installer creation will be skipped", "WARNING")
            self.print_status("Download from: https://jrsoftware.org/isinfo.php", "INFO")
    
    def update_version_info(self):
        """Update version information in relevant files"""
        self.print_status("Updating version information...")
        
        # Update __version__.py
        version_file = self.project_root / "__version__.py"
        if version_file.exists():
            content = version_file.read_text()
            content = content.replace('__version__ = "1.0.5"', f'__version__ = "{self.version}"')
            content = content.replace('VERSION_PATCH = 5', f'VERSION_PATCH = 6')
            version_file.write_text(content)
            self.print_status("Updated __version__.py")
    
    def build_executable(self):
        """Build the executable using cx_Freeze"""
        self.print_status("Building executable with cx_Freeze...")
        
        # Run cx_Freeze build
        try:
            result = subprocess.run([
                sys.executable, "setup_cx_freeze.py", "build"
            ], capture_output=True, text=True, check=True)
            
            self.print_status("cx_Freeze build completed successfully")
            
            # Find the actual build directory (it might have a different name)
            build_subdirs = list(self.build_dir.glob("exe.*"))
            if build_subdirs:
                actual_exe_dir = build_subdirs[0]
                self.print_status(f"Executable built in: {actual_exe_dir}")
                
                # Copy to standardized location
                if actual_exe_dir != self.exe_dir:
                    if self.exe_dir.exists():
                        shutil.rmtree(self.exe_dir)
                    shutil.copytree(actual_exe_dir, self.exe_dir)
                    self.print_status(f"Copied to standardized location: {self.exe_dir}")
                
                return True
            else:
                self.print_status("No executable directory found", "ERROR")
                return False
                
        except subprocess.CalledProcessError as e:
            self.print_status(f"cx_Freeze build failed: {e}", "ERROR")
            self.print_status(f"stdout: {e.stdout}", "ERROR")
            self.print_status(f"stderr: {e.stderr}", "ERROR")
            return False
    
    def verify_executable(self):
        """Verify that the executable was built correctly"""
        self.print_status("Verifying executable...")
        
        main_exe = self.exe_dir / "VARSYS_Kitchen_Dashboard.exe"
        service_exe = self.exe_dir / "VARSYS_Kitchen_Service.exe"
        
        if not main_exe.exists():
            self.print_status("Main executable not found", "ERROR")
            return False
        
        if not service_exe.exists():
            self.print_status("Service executable not found", "ERROR")
            return False
        
        # Check file sizes
        main_size = main_exe.stat().st_size / (1024 * 1024)  # MB
        service_size = service_exe.stat().st_size / (1024 * 1024)  # MB
        
        self.print_status(f"Main executable: {main_size:.1f} MB")
        self.print_status(f"Service executable: {service_size:.1f} MB")
        
        if main_size < 10:  # Less than 10MB seems too small
            self.print_status("Main executable seems too small", "WARNING")
        
        return True
    
    def create_installer(self):
        """Create professional installer using Inno Setup"""
        if not self.inno_setup_path:
            self.print_status("Skipping installer creation - Inno Setup not found", "WARNING")
            return False
        
        self.print_status("Creating professional installer with Inno Setup...")
        
        # Update installer script with current version
        installer_script = self.project_root / "installer_script.iss"
        if installer_script.exists():
            content = installer_script.read_text()
            content = content.replace('#define MyAppVersion "1.0.6"', f'#define MyAppVersion "{self.version}"')
            installer_script.write_text(content)
        
        try:
            result = subprocess.run([
                self.inno_setup_path, 
                str(installer_script)
            ], capture_output=True, text=True, check=True)
            
            self.print_status("Installer created successfully")
            
            # Find the created installer
            installer_files = list(self.installer_dir.glob("*.exe"))
            if installer_files:
                installer_file = installer_files[0]
                installer_size = installer_file.stat().st_size / (1024 * 1024)  # MB
                self.print_status(f"Installer: {installer_file.name} ({installer_size:.1f} MB)")
                return True
            else:
                self.print_status("Installer file not found", "ERROR")
                return False
                
        except subprocess.CalledProcessError as e:
            self.print_status(f"Installer creation failed: {e}", "ERROR")
            self.print_status(f"stdout: {e.stdout}", "ERROR")
            self.print_status(f"stderr: {e.stderr}", "ERROR")
            return False
    
    def create_portable_package(self):
        """Create a portable package for users without installer"""
        self.print_status("Creating portable package...")
        
        portable_dir = self.dist_dir / f"VARSYS_Kitchen_Dashboard_v{self.version}_Portable"
        portable_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy executable files
        shutil.copytree(self.exe_dir, portable_dir / "app", dirs_exist_ok=True)
        
        # Create portable launcher
        launcher_content = f'''@echo off
title VARSYS Kitchen Dashboard v{self.version}
echo Starting VARSYS Kitchen Dashboard...
cd /d "%~dp0\\app"
start "" "VARSYS_Kitchen_Service.exe"
echo Kitchen Dashboard started in system tray.
echo You can close this window.
pause
'''
        
        launcher_file = portable_dir / "Start_Kitchen_Dashboard.bat"
        launcher_file.write_text(launcher_content)
        
        # Copy documentation
        docs_to_copy = ["README.md", "LICENSE", "RELEASE_NOTES.md"]
        for doc in docs_to_copy:
            doc_file = self.project_root / doc
            if doc_file.exists():
                shutil.copy2(doc_file, portable_dir)
        
        # Create ZIP archive
        zip_file = self.dist_dir / f"VARSYS_Kitchen_Dashboard_v{self.version}_Portable.zip"
        shutil.make_archive(str(zip_file.with_suffix('')), 'zip', portable_dir)
        
        zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
        self.print_status(f"Portable package: {zip_file.name} ({zip_size:.1f} MB)")
        
        return True
    
    def generate_build_info(self):
        """Generate build information file"""
        self.print_status("Generating build information...")
        
        build_info = {
            "version": self.version,
            "build_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "build_type": "professional",
            "features": [
                "System tray integration",
                "Auto-startup capability", 
                "Professional installer",
                "Enhanced auto-updater",
                "Firebase cloud sync",
                "Subscription-based access"
            ],
            "files": {
                "main_executable": "VARSYS_Kitchen_Dashboard.exe",
                "service_executable": "VARSYS_Kitchen_Service.exe",
                "installer": f"VARSYS_Kitchen_Dashboard_v{self.version}_Setup.exe",
                "portable": f"VARSYS_Kitchen_Dashboard_v{self.version}_Portable.zip"
            }
        }
        
        build_info_file = self.dist_dir / "BUILD_INFO.json"
        with open(build_info_file, 'w') as f:
            json.dump(build_info, f, indent=2)
        
        self.print_status(f"Build info saved to {build_info_file}")
    
    def build(self):
        """Main build process"""
        self.print_status(f"Starting professional build for {self.app_name} v{self.version}")
        
        try:
            # Step 1: Check dependencies
            self.check_dependencies()
            
            # Step 2: Clean build directories
            self.clean_build_directories()
            
            # Step 3: Update version info
            self.update_version_info()
            
            # Step 4: Build executable
            if not self.build_executable():
                return False
            
            # Step 5: Verify executable
            if not self.verify_executable():
                return False
            
            # Step 6: Create installer
            self.create_installer()
            
            # Step 7: Create portable package
            self.create_portable_package()
            
            # Step 8: Generate build info
            self.generate_build_info()
            
            self.print_status("Professional build completed successfully!", "SUCCESS")
            self.print_status(f"Output directory: {self.dist_dir}")
            
            return True
            
        except Exception as e:
            self.print_status(f"Build failed with error: {e}", "ERROR")
            return False

def main():
    """Main entry point"""
    builder = ProfessionalBuilder()
    success = builder.build()
    
    if success:
        print("\n" + "="*60)
        print("🎉 PROFESSIONAL BUILD COMPLETED SUCCESSFULLY! 🎉")
        print("="*60)
        print("Your VARSYS Kitchen Dashboard is now ready for distribution!")
        print("\nFiles created:")
        print("- Professional Windows Installer")
        print("- Portable ZIP package")
        print("- System tray service")
        print("- Auto-startup integration")
        print("- Enhanced auto-updater")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("❌ BUILD FAILED")
        print("="*60)
        print("Please check the error messages above and try again.")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
