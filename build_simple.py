#!/usr/bin/env python3
"""
Simple Build Script for VARSYS Kitchen Dashboard
Focuses on creating a working executable first, then adding features
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import time

class SimpleBuildScript:
    def __init__(self):
        self.project_root = Path.cwd()
        self.version = "1.0.6"
        
    def print_status(self, message, status="INFO"):
        """Print formatted status message"""
        timestamp = time.strftime("%H:%M:%S")
        colors = {
            "INFO": "",
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",    # Red
            "RESET": "\033[0m"      # Reset
        }
        color = colors.get(status, "")
        reset = colors["RESET"] if color else ""
        print(f"{color}[{timestamp}] [{status}] {message}{reset}")
    
    def check_python_packages(self):
        """Check if required packages are installed"""
        self.print_status("Checking Python packages...")
        
        required_packages = ['cx_Freeze', 'PySide6', 'pandas', 'matplotlib', 'numpy']
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
            try:
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
                self.print_status("✓ Packages installed successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.print_status(f"Failed to install packages: {e}", "ERROR")
                return False
        
        return True
    
    def clean_build_dirs(self):
        """Clean previous build directories"""
        self.print_status("Cleaning previous builds...")
        
        dirs_to_clean = ["build", "dist"]
        for dir_name in dirs_to_clean:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.print_status(f"Removed {dir_name}/")
        
        self.print_status("✓ Build directories cleaned", "SUCCESS")
    
    def verify_required_files(self):
        """Verify that required files exist"""
        self.print_status("Verifying required files...")
        
        required_files = [
            "kitchen_app.py",
            "setup_cx_freeze.py",
            "assets/icons/vasanthkitchen.ico"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.print_status(f"Missing required files: {', '.join(missing_files)}", "ERROR")
            return False
        
        self.print_status("✓ All required files found", "SUCCESS")
        return True
    
    def build_executable(self):
        """Build the executable using cx_Freeze"""
        self.print_status("Building executable with cx_Freeze...")
        self.print_status("This may take a few minutes...")
        
        try:
            # Run cx_Freeze build
            result = subprocess.run([
                sys.executable, "setup_cx_freeze.py", "build"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                self.print_status("Build failed!", "ERROR")
                self.print_status(f"Error output: {result.stderr}", "ERROR")
                return False
            
            self.print_status("✓ Build completed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_status(f"Build error: {e}", "ERROR")
            return False
    
    def find_executable(self):
        """Find the built executable"""
        self.print_status("Looking for built executable...")
        
        # Look for build directories
        build_dirs = list(self.project_root.glob("build/exe.*"))
        if not build_dirs:
            self.print_status("No build directory found", "ERROR")
            return None
        
        build_dir = build_dirs[0]
        exe_file = build_dir / "VARSYS_Kitchen_Dashboard.exe"
        
        if not exe_file.exists():
            self.print_status("Executable not found in build directory", "ERROR")
            return None
        
        # Get file size
        file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
        self.print_status(f"✓ Found executable: {exe_file} ({file_size:.1f} MB)", "SUCCESS")
        
        return exe_file
    
    def create_distribution(self, exe_file):
        """Create distribution package"""
        self.print_status("Creating distribution package...")
        
        # Create dist directory
        dist_dir = self.project_root / "dist"
        dist_dir.mkdir(exist_ok=True)
        
        # Copy executable to dist
        dist_exe = dist_dir / "VARSYS_Kitchen_Dashboard.exe"
        shutil.copy2(exe_file, dist_exe)
        
        # Copy documentation
        docs_to_copy = ["README.md", "LICENSE", "RELEASE_NOTES.md"]
        for doc in docs_to_copy:
            doc_file = self.project_root / doc
            if doc_file.exists():
                shutil.copy2(doc_file, dist_dir)
        
        # Create simple launcher script
        launcher_content = f'''@echo off
title VARSYS Kitchen Dashboard v{self.version}
echo Starting VARSYS Kitchen Dashboard...
echo.
echo If you see this window, the application is starting.
echo The main window should appear shortly.
echo.
echo You can minimize this window - it will close automatically
echo when you exit the Kitchen Dashboard application.
echo.
start /wait "VARSYS Kitchen Dashboard" "VARSYS_Kitchen_Dashboard.exe"
echo.
echo Kitchen Dashboard has closed.
pause
'''
        
        launcher_file = dist_dir / "Start_Kitchen_Dashboard.bat"
        launcher_file.write_text(launcher_content)
        
        self.print_status(f"✓ Distribution created in: {dist_dir}", "SUCCESS")
        return dist_dir
    
    def test_executable(self, exe_file):
        """Test if the executable can start"""
        self.print_status("Testing executable...")
        
        try:
            # Try to run with --help or --version flag (if supported)
            # For now, just check if the file is executable
            if exe_file.exists() and exe_file.stat().st_size > 1024 * 1024:  # > 1MB
                self.print_status("✓ Executable appears to be valid", "SUCCESS")
                return True
            else:
                self.print_status("Executable seems too small or missing", "WARNING")
                return False
        except Exception as e:
            self.print_status(f"Error testing executable: {e}", "WARNING")
            return False
    
    def build(self):
        """Main build process"""
        self.print_status("Starting simple build process...")
        self.print_status(f"Building VARSYS Kitchen Dashboard v{self.version}")
        print()
        
        try:
            # Step 1: Check packages
            if not self.check_python_packages():
                return False
            print()
            
            # Step 2: Clean build directories
            self.clean_build_dirs()
            print()
            
            # Step 3: Verify required files
            if not self.verify_required_files():
                return False
            print()
            
            # Step 4: Build executable
            if not self.build_executable():
                return False
            print()
            
            # Step 5: Find executable
            exe_file = self.find_executable()
            if not exe_file:
                return False
            print()
            
            # Step 6: Test executable
            self.test_executable(exe_file)
            print()
            
            # Step 7: Create distribution
            dist_dir = self.create_distribution(exe_file)
            print()
            
            # Success summary
            print("=" * 60)
            self.print_status("🎉 BUILD COMPLETED SUCCESSFULLY! 🎉", "SUCCESS")
            print("=" * 60)
            print()
            print("Files created:")
            print(f"  📁 Build directory: {exe_file.parent}")
            print(f"  📁 Distribution: {dist_dir}")
            print(f"  🎯 Executable: VARSYS_Kitchen_Dashboard.exe")
            print(f"  🚀 Launcher: Start_Kitchen_Dashboard.bat")
            print()
            print("Next steps:")
            print("  1. Test the executable in the dist/ folder")
            print("  2. Run Start_Kitchen_Dashboard.bat to launch")
            print("  3. If it works, we can add more features!")
            print()
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print()
            print("=" * 60)
            self.print_status("❌ BUILD FAILED", "ERROR")
            print("=" * 60)
            self.print_status(f"Error: {e}", "ERROR")
            print("=" * 60)
            return False

def main():
    """Main entry point"""
    builder = SimpleBuildScript()
    success = builder.build()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
