#!/usr/bin/env python3
"""
Professional build script for VARSYS Kitchen Dashboard
Supports both Python 3.12 and 3.13
Includes comprehensive error handling and logging
"""

import sys
import os
import subprocess
import shutil
import platform
from pathlib import Path
import time

class KitchenDashboardBuilder:
    def __init__(self):
        self.app_name = "VARSYS Kitchen Dashboard"
        self.app_version = "1.0.6"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.installer_dir = Path("installer_output")
        
        print(f"=== {self.app_name} Professional Build System ===")
        print(f"Python Version: {self.python_version}")
        print(f"Platform: {platform.system()} {platform.architecture()[0]}")
        print(f"Build Tool: cx_Freeze")
        print("=" * 50)
    
    def check_requirements(self):
        """Check if all required files and dependencies are available"""
        print("\n[1/7] Checking build requirements...")
        
        required_files = [
            "kitchen_app.py",
            "setup_cx_freeze.py", 
            "requirements_build.txt",
            "assets/icons/vasanthkitchen.ico"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"ERROR: Missing required files: {missing_files}")
            return False
        
        # Check Python version compatibility
        if sys.version_info[:2] not in [(3, 12), (3, 13)]:
            print(f"WARNING: Python {self.python_version} may not be fully tested")
            print("Recommended: Python 3.12 or 3.13")
        
        print("✓ All requirements check passed")
        return True
    
    def install_dependencies(self):
        """Install build dependencies"""
        print("\n[2/7] Installing build dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install cx_Freeze specifically
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "cx_Freeze"], 
                         check=True, capture_output=True)
            
            # Install application dependencies
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_build.txt"], 
                         check=True, capture_output=True)
            
            print("✓ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install dependencies: {e}")
            return False
    
    def clean_previous_builds(self):
        """Clean up previous build artifacts"""
        print("\n[3/7] Cleaning previous builds...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir, self.installer_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    print(f"✓ Cleaned {dir_path}")
                except Exception as e:
                    print(f"WARNING: Could not clean {dir_path}: {e}")
        
        print("✓ Build cleanup completed")
    
    def build_executable(self):
        """Build the executable using cx_Freeze"""
        print("\n[4/7] Building executable...")
        
        try:
            # Run cx_Freeze build
            result = subprocess.run([sys.executable, "setup_cx_freeze.py", "build"], 
                                  capture_output=True, text=True, check=True)
            
            print("✓ Executable built successfully")
            
            # Find the built executable
            build_pattern = f"exe.win-amd64-{self.python_version}"
            exe_dir = self.build_dir / build_pattern
            
            if exe_dir.exists():
                exe_file = exe_dir / "VARSYS_Kitchen_Dashboard.exe"
                if exe_file.exists():
                    print(f"✓ Executable location: {exe_file}")
                    return True
            
            print("WARNING: Executable built but location not found")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Build failed: {e}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
    
    def create_msi_installer(self):
        """Create MSI installer"""
        print("\n[5/7] Creating MSI installer...")
        
        try:
            result = subprocess.run([sys.executable, "setup_cx_freeze.py", "bdist_msi"], 
                                  capture_output=True, text=True, check=True)
            
            print("✓ MSI installer created successfully")
            
            # Find the MSI file
            if self.dist_dir.exists():
                msi_files = list(self.dist_dir.glob("*.msi"))
                if msi_files:
                    print(f"✓ MSI installer: {msi_files[0]}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"ERROR: MSI creation failed: {e}")
            return False
    
    def create_inno_setup_installer(self):
        """Create professional Inno Setup installer (if available)"""
        print("\n[6/7] Creating professional installer...")
        
        # Check if Inno Setup is available
        inno_setup_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            "iscc.exe"  # If in PATH
        ]
        
        inno_setup_exe = None
        for path in inno_setup_paths:
            if Path(path).exists() or shutil.which(path):
                inno_setup_exe = path
                break
        
        if not inno_setup_exe:
            print("⚠ Inno Setup not found - skipping professional installer")
            print("  Install Inno Setup from https://jrsoftware.org/isinfo.php")
            return True
        
        try:
            # Create installer output directory
            self.installer_dir.mkdir(exist_ok=True)
            
            # Run Inno Setup
            result = subprocess.run([inno_setup_exe, "installer_professional.iss"], 
                                  capture_output=True, text=True, check=True)
            
            print("✓ Professional installer created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"WARNING: Professional installer creation failed: {e}")
            return True  # Not critical
    
    def verify_build(self):
        """Verify the build output"""
        print("\n[7/7] Verifying build output...")
        
        # Check for executable
        build_pattern = f"exe.win-amd64-{self.python_version}"
        exe_dir = self.build_dir / build_pattern
        exe_file = exe_dir / "VARSYS_Kitchen_Dashboard.exe"
        
        if not exe_file.exists():
            print("ERROR: Executable not found")
            return False
        
        # Check file size (should be reasonable)
        exe_size = exe_file.stat().st_size / (1024 * 1024)  # MB
        print(f"✓ Executable size: {exe_size:.1f} MB")
        
        if exe_size < 50:
            print("WARNING: Executable seems too small - may be missing dependencies")
        elif exe_size > 500:
            print("WARNING: Executable seems very large - consider optimization")
        
        # Check for MSI
        if self.dist_dir.exists():
            msi_files = list(self.dist_dir.glob("*.msi"))
            if msi_files:
                msi_size = msi_files[0].stat().st_size / (1024 * 1024)  # MB
                print(f"✓ MSI installer size: {msi_size:.1f} MB")
        
        print("✓ Build verification completed")
        return True
    
    def build(self):
        """Main build process"""
        start_time = time.time()
        
        steps = [
            self.check_requirements,
            self.install_dependencies,
            self.clean_previous_builds,
            self.build_executable,
            self.create_msi_installer,
            self.create_inno_setup_installer,
            self.verify_build
        ]
        
        for step in steps:
            if not step():
                print(f"\n❌ Build failed at step: {step.__name__}")
                return False
        
        build_time = time.time() - start_time
        
        print(f"\n🎉 BUILD SUCCESSFUL! 🎉")
        print(f"Build time: {build_time:.1f} seconds")
        print(f"\nOutput files:")
        print(f"  Executable: build/exe.win-amd64-{self.python_version}/VARSYS_Kitchen_Dashboard.exe")
        print(f"  MSI Installer: dist/*.msi")
        print(f"  Professional Installer: installer_output/*.exe")
        print(f"\nTo test: Run the executable from the build directory")
        print(f"To distribute: Use the MSI or professional installer")
        
        return True

if __name__ == "__main__":
    builder = KitchenDashboardBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)
