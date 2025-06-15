#!/usr/bin/env python3
"""
Quick test to build the Kitchen Dashboard with minimal setup
"""

import subprocess
import sys
import os
from pathlib import Path

def test_simple_build():
    """Test the simple build process"""
    print("🧪 Testing simple build process...")
    print("=" * 50)
    
    # Check if we have the required files
    required_files = [
        "kitchen_app.py",
        "setup_simple.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Required files found")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Try the simple build
    print("\n🔨 Running simple build...")
    try:
        result = subprocess.run([
            sys.executable, "setup_simple.py", "build"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            
            # Look for the executable
            build_dirs = list(Path("build").glob("exe.*"))
            if build_dirs:
                exe_path = build_dirs[0] / "VARSYS_Kitchen_Dashboard.exe"
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    print(f"✅ Executable created: {exe_path} ({size_mb:.1f} MB)")
                    return True
                else:
                    print("❌ Executable not found in build directory")
            else:
                print("❌ No build directory found")
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Build error: {e}")
    
    return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing module imports...")
    
    modules_to_test = [
        'pandas', 'numpy', 'matplotlib', 'PySide6', 'openpyxl', 
        'PIL', 'requests', 'cx_Freeze'
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        print("   Run: pip install " + " ".join(failed_imports))
        return False
    
    print("✅ All modules imported successfully")
    return True

def main():
    """Main test function"""
    print("VARSYS Kitchen Dashboard - Build Test")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import test failed. Please install missing packages.")
        return 1
    
    # Test build
    if test_simple_build():
        print("\n🎉 SUCCESS! The simple build works!")
        print("\nNext steps:")
        print("1. Test the executable in build/exe.*/")
        print("2. If it works, we can add more features")
        print("3. Then create the professional installer")
        return 0
    else:
        print("\n❌ Build test failed.")
        print("\nTroubleshooting:")
        print("1. Check that all required packages are installed")
        print("2. Make sure kitchen_app.py exists and is working")
        print("3. Try running: python setup_simple.py build")
        return 1

if __name__ == "__main__":
    sys.exit(main())
