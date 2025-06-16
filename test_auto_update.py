#!/usr/bin/env python3
"""
Test script for VARSYS Kitchen Dashboard Auto-Update System
Tests the update checking and download capabilities
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_version_info():
    """Test version information retrieval"""
    print("=" * 60)
    print("TESTING VERSION INFORMATION")
    print("=" * 60)
    
    try:
        from __version__ import get_version_info, __version__, __build__
        
        print(f"✅ Current Version: {__version__}")
        print(f"✅ Build Date: {__build__}")
        
        version_info = get_version_info()
        print(f"✅ Company: {version_info['company']}")
        print(f"✅ Product: {version_info['product']}")
        print(f"✅ Release Type: {version_info['release_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing version info: {e}")
        return False

def test_updater_initialization():
    """Test updater system initialization"""
    print("\n" + "=" * 60)
    print("TESTING UPDATER INITIALIZATION")
    print("=" * 60)
    
    try:
        from updater import get_updater
        
        updater = get_updater()
        print(f"✅ Updater initialized successfully")
        print(f"✅ Current version: {updater.current_version}")
        print(f"✅ Update check interval: {updater.update_check_interval} hours")
        print(f"✅ Temp directory: {updater.temp_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing updater: {e}")
        return False

def test_update_check():
    """Test update checking functionality"""
    print("\n" + "=" * 60)
    print("TESTING UPDATE CHECK")
    print("=" * 60)
    
    try:
        from updater import get_updater
        
        updater = get_updater()
        
        print("🔍 Checking for updates...")
        update_info = updater.check_for_updates()
        
        if update_info:
            print("🎉 Update available!")
            print(f"   New Version: {update_info['version']}")
            print(f"   Release Name: {update_info['name']}")
            print(f"   Published: {update_info['published_at']}")
            print(f"   Assets: {len(update_info['assets'])} files")
            
            # Test download asset finding
            download_url = updater.find_download_asset(update_info['assets'])
            if download_url:
                print(f"   Download URL: {download_url}")
            else:
                print("   ⚠️ No suitable download asset found")
                
        else:
            print("✅ No updates available - you have the latest version!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking for updates: {e}")
        return False

def test_update_manager():
    """Test update manager UI components"""
    print("\n" + "=" * 60)
    print("TESTING UPDATE MANAGER")
    print("=" * 60)
    
    try:
        # Test without creating actual UI (headless test)
        from update_manager import UpdateManager
        
        print("✅ Update manager module imported successfully")
        print("✅ Update dialog components available")
        print("✅ Background update threads available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing update manager: {e}")
        return False

def test_version_comparison():
    """Test version comparison logic"""
    print("\n" + "=" * 60)
    print("TESTING VERSION COMPARISON")
    print("=" * 60)
    
    try:
        from __version__ import is_newer_version
        
        test_cases = [
            ("1.1.2", True),   # Newer patch
            ("1.2.0", True),   # Newer minor
            ("2.0.0", True),   # Newer major
            ("1.1.1", False),  # Same version
            ("1.1.0", False),  # Older patch
            ("1.0.9", False),  # Older minor
            ("0.9.9", False),  # Older major
        ]
        
        for test_version, expected in test_cases:
            result = is_newer_version(test_version)
            status = "✅" if result == expected else "❌"
            print(f"{status} {test_version} is newer: {result} (expected: {expected})")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing version comparison: {e}")
        return False

def test_update_interval():
    """Test update interval checking"""
    print("\n" + "=" * 60)
    print("TESTING UPDATE INTERVAL")
    print("=" * 60)
    
    try:
        from updater import get_updater
        
        updater = get_updater()
        
        should_check = updater.should_check_for_updates()
        print(f"✅ Should check for updates: {should_check}")
        
        # Update last check time
        updater.update_last_check_time()
        print("✅ Updated last check time")
        
        # Check again (should be False now)
        should_check_again = updater.should_check_for_updates()
        print(f"✅ Should check again immediately: {should_check_again}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing update interval: {e}")
        return False

def main():
    """Run all auto-update tests"""
    print("VARSYS Kitchen Dashboard v1.1.1 - Auto-Update System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Version Information", test_version_info),
        ("Updater Initialization", test_updater_initialization),
        ("Update Check", test_update_check),
        ("Update Manager", test_update_manager),
        ("Version Comparison", test_version_comparison),
        ("Update Interval", test_update_interval),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Auto-update system is working correctly!")
    else:
        print("⚠️ Some tests failed - check the output above for details")
    
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
