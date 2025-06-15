#!/usr/bin/env python3
"""
Test Firebase Error Fix for Kitchen Dashboard v1.0.6
This script tests that the Firebase integration error has been resolved
"""

import sys
import os

def test_firebase_sync_initialization():
    """Test FirebaseSync initialization"""
    print("🔧 Testing FirebaseSync Initialization...")
    
    try:
        from modules.firebase_sync import FirebaseSync
        import pandas as pd
        
        # Create sample data
        sample_data = {
            'test_table': pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Test Item 1', 'Test Item 2', 'Test Item 3']
            })
        }
        
        # Initialize FirebaseSync (this was causing the error)
        firebase_sync = FirebaseSync(parent=None, data=sample_data, data_dir="data")
        
        if firebase_sync:
            print("✅ FirebaseSync initialized successfully")
            
            # Test Firebase availability check
            is_available = firebase_sync.is_firebase_available()
            print(f"   Firebase available: {is_available}")
            
            return True
        else:
            print("❌ Failed to initialize FirebaseSync")
            return False
            
    except Exception as e:
        print(f"❌ Error testing FirebaseSync initialization: {e}")
        return False

def test_firebase_integration_module():
    """Test Firebase integration module"""
    print("\n🔗 Testing Firebase Integration Module...")
    
    try:
        from modules import firebase_integration
        
        print(f"   Pyrebase Available: {firebase_integration.PYREBASE_AVAILABLE}")
        print(f"   Firebase Available: {firebase_integration.FIREBASE_AVAILABLE}")
        
        if firebase_integration.PYREBASE_AVAILABLE:
            print("✅ Firebase integration module is working")
            return True
        else:
            print("❌ Firebase integration module has issues")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase integration module: {e}")
        return False

def test_firebase_config_manager():
    """Test Firebase configuration manager"""
    print("\n⚙️ Testing Firebase Configuration Manager...")
    
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        
        config_manager = get_firebase_config_manager()
        
        if config_manager:
            print("✅ Firebase configuration manager is working")
            
            is_configured = config_manager.is_configured()
            print(f"   Firebase configured: {is_configured}")
            
            if is_configured:
                firebase_config = config_manager.firebase_config
                if firebase_config:
                    print(f"   Project ID: {firebase_config.project_id}")
            
            return True
        else:
            print("❌ Failed to get Firebase configuration manager")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase configuration manager: {e}")
        return False

def test_optimized_firebase_manager():
    """Test optimized Firebase manager"""
    print("\n⚡ Testing Optimized Firebase Manager...")
    
    try:
        from modules.optimized_firebase_manager import get_optimized_firebase_manager
        
        firebase_manager = get_optimized_firebase_manager()
        
        if firebase_manager:
            print("✅ Optimized Firebase manager is working")
            return True
        else:
            print("❌ Failed to get optimized Firebase manager")
            return False
            
    except Exception as e:
        print(f"❌ Error testing optimized Firebase manager: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Kitchen Dashboard v1.0.6 - Firebase Error Fix Test")
    print("=" * 60)
    print("🔍 Testing that Firebase integration error has been resolved")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('kitchen_app.py'):
        print("❌ Please run this script from the Kitchen Dashboard root directory")
        return 1
    
    # Run tests
    tests = [
        ("FirebaseSync Initialization", test_firebase_sync_initialization),
        ("Firebase Integration Module", test_firebase_integration_module),
        ("Firebase Configuration Manager", test_firebase_config_manager),
        ("Optimized Firebase Manager", test_optimized_firebase_manager),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Firebase Error Fix Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Firebase integration error has been resolved.")
        print("\n📋 Summary:")
        print("• FirebaseSync initializes without errors")
        print("• Firebase integration module is working")
        print("• Configuration manager is functional")
        print("• Optimized Firebase manager is ready")
        print("\n✅ The application should now start without Firebase errors!")
        return 0
    else:
        print("⚠️ Some tests failed. Firebase integration may still have issues.")
        print("\n📋 Troubleshooting:")
        print("• Check Firebase configuration files")
        print("• Verify pyrebase4 installation")
        print("• Check internet connection")
        return 1

if __name__ == "__main__":
    sys.exit(main())
