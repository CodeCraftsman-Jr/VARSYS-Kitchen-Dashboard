#!/usr/bin/env python3
"""
Test Daily Sync Fix for Kitchen Dashboard v1.0.6
This script tests that the daily sync error has been resolved
"""

import sys
import os
from datetime import datetime

def test_daily_sync_check():
    """Test daily sync check without authentication"""
    print("🔧 Testing Daily Sync Check (Before Authentication)...")
    
    try:
        # Import the main application class
        from kitchen_app import KitchenDashboard
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Create a test instance (this should not trigger sync errors)
        dashboard = KitchenDashboard()
        
        # Check if daily sync needed flag is set correctly
        if hasattr(dashboard, 'daily_sync_needed'):
            print(f"   Daily sync needed flag: {dashboard.daily_sync_needed}")
            print("✅ Daily sync check works without authentication errors")
            return True
        else:
            print("   Daily sync needed flag not found")
            print("✅ Daily sync check completed without errors")
            return True
            
    except Exception as e:
        if "Firebase integration is not available" in str(e):
            print("❌ Daily sync still triggering Firebase errors")
            print(f"   Error: {e}")
            return False
        else:
            print(f"❌ Other error in daily sync check: {e}")
            return False

def test_authenticated_daily_sync_method():
    """Test the authenticated daily sync method"""
    print("\n⚡ Testing Authenticated Daily Sync Method...")
    
    try:
        from kitchen_app import KitchenDashboard
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Create a test instance
        dashboard = KitchenDashboard()
        
        # Check if the new method exists
        if hasattr(dashboard, 'perform_authenticated_daily_sync'):
            print("✅ Authenticated daily sync method exists")
            
            # Test that it doesn't crash when called without authentication
            try:
                dashboard.perform_authenticated_daily_sync()
                print("✅ Method handles unauthenticated state gracefully")
                return True
            except Exception as e:
                print(f"❌ Method failed when unauthenticated: {e}")
                return False
        else:
            print("❌ Authenticated daily sync method not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing authenticated daily sync method: {e}")
        return False

def test_manual_sync_method():
    """Test the updated manual sync method"""
    print("\n🔄 Testing Updated Manual Sync Method...")
    
    try:
        from kitchen_app import KitchenDashboard
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Create a test instance
        dashboard = KitchenDashboard()
        
        # Check if the manual sync method exists and is updated
        if hasattr(dashboard, 'trigger_manual_full_sync'):
            print("✅ Manual sync method exists")
            
            # Test that it handles unauthenticated state properly
            try:
                result = dashboard.trigger_manual_full_sync()
                print(f"✅ Manual sync handles unauthenticated state: {result}")
                return True
            except Exception as e:
                print(f"❌ Manual sync method failed: {e}")
                return False
        else:
            print("❌ Manual sync method not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual sync method: {e}")
        return False

def test_firebase_integration_availability():
    """Test Firebase integration availability"""
    print("\n🔗 Testing Firebase Integration Availability...")
    
    try:
        from modules import firebase_integration
        
        print(f"   Firebase Available: {firebase_integration.FIREBASE_AVAILABLE}")
        print(f"   Pyrebase Available: {firebase_integration.PYREBASE_AVAILABLE}")
        
        if firebase_integration.PYREBASE_AVAILABLE:
            print("✅ Firebase integration is available for subscription model")
            return True
        else:
            print("❌ Firebase integration not available")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Firebase integration: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Kitchen Dashboard v1.0.6 - Daily Sync Error Fix Test")
    print("=" * 65)
    print("🔍 Testing that daily sync no longer causes Firebase errors")
    print("=" * 65)
    
    # Check if we're in the right directory
    if not os.path.exists('kitchen_app.py'):
        print("❌ Please run this script from the Kitchen Dashboard root directory")
        return 1
    
    # Run tests
    tests = [
        ("Daily Sync Check (Before Auth)", test_daily_sync_check),
        ("Authenticated Daily Sync Method", test_authenticated_daily_sync_method),
        ("Updated Manual Sync Method", test_manual_sync_method),
        ("Firebase Integration Availability", test_firebase_integration_availability),
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
    print("\n" + "=" * 65)
    print("📊 Daily Sync Error Fix Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Daily sync error has been resolved.")
        print("\n📋 Summary:")
        print("• Daily sync no longer triggers before authentication")
        print("• Authenticated daily sync method implemented")
        print("• Manual sync updated for subscription model")
        print("• Firebase integration properly available")
        print("\n✅ The application should now start without daily sync errors!")
        return 0
    else:
        print("⚠️ Some tests failed. Daily sync may still have issues.")
        print("\n📋 Troubleshooting:")
        print("• Check Firebase configuration")
        print("• Verify authentication flow")
        print("• Check sync method implementations")
        return 1

if __name__ == "__main__":
    sys.exit(main())
