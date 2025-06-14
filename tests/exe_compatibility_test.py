"""
EXE Compatibility Test
Tests that all test modules work when compiled to EXE
"""

import sys
import os
import importlib.util
from test_utils import setup_module_imports, get_project_root

def test_exe_compatibility():
    """Test that all test modules can be imported and used in EXE"""
    print("Testing EXE Compatibility...")
    print("=" * 50)
    
    # Setup imports
    setup_module_imports()
    
    # Test modules that need to be available in EXE
    test_modules = [
        'sample_data_generator',
        'comprehensive_test_suite', 
        'module_tester',
        'data_operation_tester',
        'ui_component_tester',
        'performance_tester',
        'test_utils',
        'test_config'
    ]
    
    results = []
    
    for module_name in test_modules:
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            
            # Test basic functionality
            if hasattr(module, '__version__'):
                version = getattr(module, '__version__')
            else:
                version = "unknown"
                
            result = f"✅ {module_name}: OK (version: {version})"
            results.append(('PASS', module_name))
            
        except ImportError as e:
            result = f"❌ {module_name}: IMPORT ERROR - {e}"
            results.append(('FAIL', module_name))
            
        except Exception as e:
            result = f"⚠️  {module_name}: ERROR - {e}"
            results.append(('ERROR', module_name))
            
        print(result)
    
    # Test data directory access
    try:
        project_root = get_project_root()
        data_dir = os.path.join(project_root, 'data')
        
        if os.path.exists(data_dir):
            data_files = os.listdir(data_dir)
            print(f"✅ Data directory accessible: {len(data_files)} files found")
            results.append(('PASS', 'data_directory'))
        else:
            print("⚠️  Data directory not found (will be created)")
            results.append(('WARN', 'data_directory'))
            
    except Exception as e:
        print(f"❌ Data directory access error: {e}")
        results.append(('FAIL', 'data_directory'))
    
    # Test file creation (important for EXE)
    try:
        test_file = os.path.join(get_project_root(), 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Read it back
        with open(test_file, 'r') as f:
            content = f.read()
            
        # Clean up
        os.remove(test_file)
        
        if content == "test":
            print("✅ File I/O operations working")
            results.append(('PASS', 'file_io'))
        else:
            print("❌ File I/O operations failed")
            results.append(('FAIL', 'file_io'))
            
    except Exception as e:
        print(f"❌ File I/O error: {e}")
        results.append(('FAIL', 'file_io'))
    
    # Summary
    print("\nEXE Compatibility Summary:")
    print("-" * 30)
    
    passed = len([r for r in results if r[0] == 'PASS'])
    failed = len([r for r in results if r[0] == 'FAIL'])
    errors = len([r for r in results if r[0] == 'ERROR'])
    warnings = len([r for r in results if r[0] == 'WARN'])
    
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if failed == 0 and errors == 0:
        print("\n🎉 All tests passed! EXE compilation should work.")
        return True
    else:
        print(f"\n⚠️  {failed + errors} issues found. Fix before EXE compilation.")
        return False

def create_exe_spec_file():
    """Create PyInstaller spec file for EXE compilation"""
    project_root = get_project_root()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Include all test files
test_files = [
    ('tests/*.py', 'tests'),
    ('tests/TESTING_GUIDE.md', 'tests'),
    ('data/*.csv', 'data'),
    ('modules/*.py', 'modules'),
    ('utils/*.py', 'utils'),
]

a = Analysis(
    ['kitchen_app.py'],
    pathex=['{project_root}'],
    binaries=[],
    datas=test_files,
    hiddenimports=[
        'tests.sample_data_generator',
        'tests.comprehensive_test_suite',
        'tests.module_tester',
        'tests.data_operation_tester',
        'tests.ui_component_tester',
        'tests.performance_tester',
        'tests.test_utils',
        'tests.test_config',
        'tests.exe_compatibility_test',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KitchenDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_file = os.path.join(project_root, 'kitchen_dashboard.spec')
    
    try:
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ PyInstaller spec file created: {spec_file}")
        print("To build EXE, run: pyinstaller kitchen_dashboard.spec")
        return True
        
    except Exception as e:
        print(f"❌ Error creating spec file: {e}")
        return False

if __name__ == "__main__":
    print("Kitchen Dashboard - EXE Compatibility Test")
    print("=" * 60)
    
    # Run compatibility test
    success = test_exe_compatibility()
    
    if success:
        print("\nCreating PyInstaller spec file...")
        create_exe_spec_file()
    
    print("\nEXE Compatibility Test Complete!")
    sys.exit(0 if success else 1)
