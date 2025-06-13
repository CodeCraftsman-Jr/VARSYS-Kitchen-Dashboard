#!/usr/bin/env python3
"""
Complete Build Script for VARSYS Kitchen Dashboard
Creates a full, standalone executable with all dependencies
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",      # Blue
        "SUCCESS": "\033[92m",   # Green
        "WARNING": "\033[93m",   # Yellow
        "ERROR": "\033[91m",     # Red
        "RESET": "\033[0m"       # Reset
    }
    
    color = colors.get(status, colors["INFO"])
    reset = colors["RESET"]
    timestamp = time.strftime("%H:%M:%S")
    
    print(f"{color}[{timestamp}] {status}: {message}{reset}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_status("Checking dependencies...", "INFO")
    
    required_packages = [
        'cx_Freeze', 'PySide6', 'pandas', 'numpy', 'matplotlib', 
        'openpyxl', 'Pillow', 'requests', 'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
            print_status(f"✅ {package} found", "SUCCESS")
        except ImportError:
            missing_packages.append(package)
            print_status(f"❌ {package} missing", "ERROR")
    
    if missing_packages:
        print_status(f"Installing missing packages: {', '.join(missing_packages)}", "WARNING")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print_status(f"✅ Installed {package}", "SUCCESS")
            except subprocess.CalledProcessError:
                print_status(f"❌ Failed to install {package}", "ERROR")
                return False
    
    return True

def clean_build_directory():
    """Clean previous build artifacts"""
    print_status("Cleaning build directory...", "INFO")
    
    build_dirs = ['build', 'dist']
    
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
                print_status(f"✅ Removed {build_dir}/", "SUCCESS")
            except Exception as e:
                print_status(f"⚠️ Could not remove {build_dir}/: {e}", "WARNING")

def verify_files():
    """Verify all required files exist"""
    print_status("Verifying required files...", "INFO")
    
    required_files = [
        'kitchen_app.py',
        'setup_cx_freeze.py',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'modules',
        'data',
        'assets'
    ]
    
    missing_files = []
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print_status(f"✅ {file_path} found", "SUCCESS")
        else:
            missing_files.append(file_path)
            print_status(f"❌ {file_path} missing", "ERROR")
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_status(f"✅ {dir_path}/ found", "SUCCESS")
        else:
            print_status(f"⚠️ {dir_path}/ missing (will be created)", "WARNING")
            os.makedirs(dir_path, exist_ok=True)
    
    return len(missing_files) == 0

def build_executable():
    """Build the executable using cx_Freeze"""
    print_status("Building executable...", "INFO")
    
    try:
        # Run cx_Freeze build
        result = subprocess.run([
            sys.executable, 'setup_cx_freeze.py', 'build'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_status("✅ Build completed successfully", "SUCCESS")
            return True
        else:
            print_status(f"❌ Build failed: {result.stderr}", "ERROR")
            print("STDOUT:", result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print_status("❌ Build timed out after 5 minutes", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Build error: {e}", "ERROR")
        return False

def verify_executable():
    """Verify the built executable"""
    print_status("Verifying executable...", "INFO")
    
    exe_path = Path("build/exe.win-amd64-3.10/VARSYS_Kitchen_Dashboard.exe")
    
    if not exe_path.exists():
        print_status("❌ Executable not found", "ERROR")
        return False
    
    # Check file size
    file_size = exe_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    
    print_status(f"📦 Executable size: {size_mb:.1f} MB", "INFO")
    
    if size_mb < 50:  # Should be at least 50MB with all dependencies
        print_status("⚠️ Executable seems too small - dependencies might be missing", "WARNING")
        return False
    elif size_mb > 500:  # Shouldn't be more than 500MB
        print_status("⚠️ Executable seems too large - might include unnecessary files", "WARNING")
    else:
        print_status("✅ Executable size looks good", "SUCCESS")
    
    return True

def create_distribution_package():
    """Create a distribution package"""
    print_status("Creating distribution package...", "INFO")
    
    try:
        # Create distribution directory
        dist_dir = Path("distribution")
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        dist_dir.mkdir()
        
        # Copy executable
        exe_source = Path("build/exe.win-amd64-3.10/VARSYS_Kitchen_Dashboard.exe")
        exe_dest = dist_dir / "VARSYS_Kitchen_Dashboard.exe"
        shutil.copy2(exe_source, exe_dest)
        
        # Copy documentation
        docs_to_copy = [
            'README.md',
            'LICENSE',
            'COMMERCIAL_SETUP_GUIDE.md',
            'INSTALLATION.md'
        ]
        
        for doc in docs_to_copy:
            if os.path.exists(doc):
                shutil.copy2(doc, dist_dir / doc)
        
        # Create installation guide
        installation_guide = dist_dir / "INSTALLATION.md"
        with open(installation_guide, 'w', encoding='utf-8') as f:
            f.write("""# 🍳 VARSYS Kitchen Dashboard Installation Guide

## Quick Start
1. Download VARSYS_Kitchen_Dashboard.exe
2. Run the executable (no installation required)
3. Activate with your license key
4. Start managing your kitchen!

## System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space
- Internet connection for cloud features

## Getting a License
📧 Email: sales@varsys.com
📱 WhatsApp: +91-XXXXX-XXXXX
🌐 Website: www.varsys.com

## Support
- Documentation: https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/wiki
- Issues: https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/issues
- Email: support@varsys.com

## Troubleshooting
- If Windows Defender blocks the app, click "More info" → "Run anyway"
- For firewall issues, allow the application through Windows Firewall
- For license issues, contact support@varsys.com
""")
        
        print_status(f"✅ Distribution package created in {dist_dir}/", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"❌ Failed to create distribution package: {e}", "ERROR")
        return False

def main():
    """Main build process"""
    print_status("🚀 Starting VARSYS Kitchen Dashboard build process", "INFO")
    print_status("=" * 60, "INFO")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print_status("❌ Dependency check failed", "ERROR")
        return False
    
    # Step 2: Verify files
    if not verify_files():
        print_status("❌ File verification failed", "ERROR")
        return False
    
    # Step 3: Clean build directory
    clean_build_directory()
    
    # Step 4: Build executable
    if not build_executable():
        print_status("❌ Build process failed", "ERROR")
        return False
    
    # Step 5: Verify executable
    if not verify_executable():
        print_status("❌ Executable verification failed", "ERROR")
        return False
    
    # Step 6: Create distribution package
    if not create_distribution_package():
        print_status("❌ Distribution package creation failed", "ERROR")
        return False
    
    print_status("=" * 60, "INFO")
    print_status("🎉 Build completed successfully!", "SUCCESS")
    print_status("📦 Your executable is ready for distribution:", "INFO")
    print_status("   📁 Location: distribution/VARSYS_Kitchen_Dashboard.exe", "INFO")
    print_status("   📋 Documentation: distribution/", "INFO")
    print_status("🚀 Ready for GitHub release!", "SUCCESS")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print_status("❌ BUILD FAILED!", "ERROR")
        print_status("Please fix the errors above and try again.", "ERROR")
        sys.exit(1)
    else:
        print_status("✅ BUILD SUCCESSFUL!", "SUCCESS")
        sys.exit(0)
