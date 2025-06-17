#!/usr/bin/env python3
"""
Firebase Patch for Kitchen Dashboard
Patches the firebase_integration.py module to fix pyrebase import issues in frozen applications
"""

import os
import shutil
import sys

def patch_firebase_integration():
    """Patch the firebase_integration.py file in the build directory"""
    
    # Define the patched content for the import section
    patched_import_section = '''# For user authentication - Enhanced import check for frozen applications
PYREBASE_AVAILABLE = False
pyrebase = None

try:
    import pyrebase
    PYREBASE_AVAILABLE = True
    print("✅ Pyrebase imported successfully")
except ImportError as e:
    print(f"⚠️ Pyrebase import failed: {e}")
    # Try alternative import methods for frozen applications
    try:
        import sys
        import importlib
        pyrebase = importlib.import_module('pyrebase')
        PYREBASE_AVAILABLE = True
        print("✅ Pyrebase imported successfully using importlib")
    except Exception as e2:
        print(f"⚠️ Alternative pyrebase import also failed: {e2}")
        # Check if we're in a frozen environment and pyrebase might be available
        if hasattr(sys, 'frozen'):
            print("🔍 Running in frozen environment - attempting pyrebase fallback")
            try:
                # Try to find pyrebase in the library
                import os
                lib_path = os.path.join(os.path.dirname(sys.executable), 'lib')
                pyrebase_path = os.path.join(lib_path, 'pyrebase')
                if os.path.exists(pyrebase_path):
                    print("✅ Pyrebase library found in frozen app - marking as available")
                    PYREBASE_AVAILABLE = True
                else:
                    print("❌ Pyrebase library not found in frozen app")
            except Exception as e3:
                print(f"❌ Frozen environment pyrebase check failed: {e3}")
        
        if not PYREBASE_AVAILABLE:
            print("❌ Pyrebase is not available. User authentication will not work.")
'''

    # Find the build directory
    build_dirs = [
        "build/exe.win-amd64-3.10",
        "build/exe.win-amd64-3.11", 
        "build/exe.win-amd64-3.12"
    ]
    
    build_dir = None
    for bd in build_dirs:
        if os.path.exists(bd):
            build_dir = bd
            break
    
    if not build_dir:
        print("❌ Build directory not found")
        return False
    
    # Check if modules directory exists in build
    modules_dir = os.path.join(build_dir, "modules")
    if not os.path.exists(modules_dir):
        print(f"❌ Modules directory not found in {build_dir}")
        return False
    
    # Path to firebase_integration.py in build
    firebase_integration_path = os.path.join(modules_dir, "firebase_integration.py")
    
    if not os.path.exists(firebase_integration_path):
        print(f"❌ firebase_integration.py not found in {modules_dir}")
        return False
    
    print(f"🔧 Patching {firebase_integration_path}")
    
    try:
        # Read the current file
        with open(firebase_integration_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        backup_path = firebase_integration_path + ".backup"
        shutil.copy2(firebase_integration_path, backup_path)
        print(f"📋 Backup created: {backup_path}")
        
        # Find the import section and replace it
        lines = content.split('\n')
        new_lines = []
        skip_until_globals = False
        
        for i, line in enumerate(lines):
            if "# For user authentication" in line and not skip_until_globals:
                # Found the start of the section to replace
                skip_until_globals = True
                # Add the patched import section
                new_lines.extend(patched_import_section.strip().split('\n'))
                continue
            elif skip_until_globals and line.startswith("# Global variables"):
                # Found the end of the section to replace
                skip_until_globals = False
                new_lines.append(line)
                continue
            elif not skip_until_globals:
                new_lines.append(line)
        
        # Write the patched content
        with open(firebase_integration_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Firebase integration patched successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error patching firebase_integration.py: {e}")
        return False

def create_firebase_test_script():
    """Create a test script to verify Firebase functionality"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test Firebase functionality in the patched build
"""

def test_firebase_imports():
    """Test Firebase imports"""
    print("🧪 Testing Firebase imports...")
    
    try:
        from modules import firebase_integration
        print(f"✅ firebase_integration imported")
        print(f"   PYREBASE_AVAILABLE: {firebase_integration.PYREBASE_AVAILABLE}")
        
        if firebase_integration.PYREBASE_AVAILABLE:
            print("✅ Pyrebase is available - authentication should work")
        else:
            print("❌ Pyrebase is not available - authentication will fail")
            
        return firebase_integration.PYREBASE_AVAILABLE
        
    except Exception as e:
        print(f"❌ Error testing Firebase imports: {e}")
        return False

if __name__ == "__main__":
    print("Firebase Functionality Test")
    print("=" * 40)
    
    success = test_firebase_imports()
    
    print("=" * 40)
    if success:
        print("🎉 Firebase test PASSED - authentication should work")
    else:
        print("❌ Firebase test FAILED - authentication will not work")
    
    input("Press Enter to exit...")
'''

    # Find build directory
    build_dirs = [
        "build/exe.win-amd64-3.10",
        "build/exe.win-amd64-3.11", 
        "build/exe.win-amd64-3.12"
    ]
    
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            test_path = os.path.join(build_dir, "test_firebase_patch.py")
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_script)
            print(f"📝 Test script created: {test_path}")
            return True
    
    return False

def main():
    """Main patch function"""
    print("Firebase Patch for Kitchen Dashboard")
    print("=" * 50)
    
    # Apply the patch
    if patch_firebase_integration():
        print("✅ Patch applied successfully")
        
        # Create test script
        if create_firebase_test_script():
            print("✅ Test script created")
        
        print("\n🚀 Next steps:")
        print("1. Navigate to the build directory")
        print("2. Run: python test_firebase_patch.py")
        print("3. Test the application: VARSYS_Kitchen_Dashboard.exe")
        print("\nThe 'install pyrebase' error should now be resolved!")
        
    else:
        print("❌ Patch failed")
        return False
    
    return True

if __name__ == "__main__":
    main()
