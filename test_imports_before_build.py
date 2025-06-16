#!/usr/bin/env python3
"""
Test imports before building to identify potential issues
"""

import sys
import os

def test_critical_imports():
    """Test all critical imports that cx_Freeze needs"""
    print("Testing critical imports for cx_Freeze build...")
    print("=" * 60)
    
    # Test basic Python modules
    basic_modules = [
        'os', 'sys', 'json', 'sqlite3', 'datetime', 'logging', 
        'pathlib', 'tempfile', 'threading', 'time'
    ]
    
    print("\n1. Testing basic Python modules:")
    for module in basic_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            return False
    
    # Test numpy with specific components
    print("\n2. Testing NumPy components:")
    numpy_components = [
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.core.multiarray',
        'numpy.core.umath',
        'numpy.lib',
        'numpy.lib.format',
        'numpy.linalg'
    ]
    
    for component in numpy_components:
        try:
            __import__(component)
            print(f"   ✅ {component}")
        except ImportError as e:
            print(f"   ❌ {component}: {e}")
            if component == 'numpy':
                print("   🔧 Try: pip install --force-reinstall numpy")
                return False
    
    # Test pandas with specific components
    print("\n3. Testing Pandas components:")
    pandas_components = [
        'pandas',
        'pandas.core',
        'pandas.core.common',
        'pandas.core.ops',
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.base'
    ]
    
    for component in pandas_components:
        try:
            __import__(component)
            print(f"   ✅ {component}")
        except ImportError as e:
            print(f"   ❌ {component}: {e}")
            if component == 'pandas':
                print("   🔧 Try: pip install --force-reinstall pandas")
                return False
    
    # Test matplotlib components
    print("\n4. Testing Matplotlib components:")
    matplotlib_components = [
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qtagg'
    ]
    
    for component in matplotlib_components:
        try:
            __import__(component)
            print(f"   ✅ {component}")
        except ImportError as e:
            print(f"   ❌ {component}: {e}")
            if component == 'matplotlib':
                print("   🔧 Try: pip install --force-reinstall matplotlib")
                return False
    
    # Test PySide6 components
    print("\n5. Testing PySide6 components:")
    pyside_components = [
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets'
    ]
    
    for component in pyside_components:
        try:
            __import__(component)
            print(f"   ✅ {component}")
        except ImportError as e:
            print(f"   ❌ {component}: {e}")
            if component == 'PySide6':
                print("   🔧 Try: pip install --force-reinstall PySide6")
                return False
    
    # Test other required modules
    print("\n6. Testing other required modules:")
    other_modules = [
        'openpyxl',
        'PIL',
        'requests',
        'cx_Freeze'
    ]
    
    for module in other_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            print(f"   🔧 Try: pip install {module}")
    
    print("\n" + "=" * 60)
    print("✅ All critical imports successful!")
    print("✅ Ready for cx_Freeze build")
    return True

def test_version_compatibility():
    """Test version compatibility"""
    print("\n7. Testing version compatibility:")
    
    try:
        import numpy
        print(f"   NumPy version: {numpy.__version__}")
        
        import pandas
        print(f"   Pandas version: {pandas.__version__}")
        
        import matplotlib
        print(f"   Matplotlib version: {matplotlib.__version__}")
        
        import PySide6
        print(f"   PySide6 version: {PySide6.__version__}")
        
        import cx_Freeze
        print(f"   cx_Freeze version: {cx_Freeze.__version__}")
        
    except Exception as e:
        print(f"   ❌ Version check failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("VARSYS Kitchen Dashboard - Import Test")
    print("Testing all dependencies before cx_Freeze build")
    
    if not test_critical_imports():
        print("\n❌ Import test failed!")
        print("Please fix the import issues before building.")
        return False
    
    if not test_version_compatibility():
        print("\n❌ Version compatibility test failed!")
        return False
    
    print("\n🎉 All tests passed!")
    print("🚀 Ready to build with cx_Freeze")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
