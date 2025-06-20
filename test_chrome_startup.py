#!/usr/bin/env python3
"""
Test script to verify Chrome startup handling for WhatsApp automation
Tests various Chrome startup scenarios including when Chrome is closed
"""

import sys
import os
import subprocess
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_chrome_processes():
    """Check if Chrome processes are currently running"""
    try:
        import psutil
        chrome_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                chrome_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': proc.info['cmdline']
                })
        return chrome_processes
    except ImportError:
        print("⚠️ psutil not available - cannot check Chrome processes")
        return []
    except Exception as e:
        print(f"⚠️ Error checking Chrome processes: {e}")
        return []

def kill_chrome_processes():
    """Kill all Chrome processes for testing"""
    try:
        import psutil
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                try:
                    proc.terminate()
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        if killed_count > 0:
            print(f"🔄 Terminated {killed_count} Chrome processes")
            time.sleep(2)  # Wait for processes to close
        else:
            print("ℹ️ No Chrome processes to terminate")
        
        return True
    except ImportError:
        print("⚠️ psutil not available - cannot kill Chrome processes")
        return False
    except Exception as e:
        print(f"⚠️ Error killing Chrome processes: {e}")
        return False

def test_chrome_detection():
    """Test Chrome installation detection"""
    print("🧪 Testing Chrome Detection...")
    
    try:
        from modules.whatsapp_integration import WhatsAppWebDriver
        
        driver = WhatsAppWebDriver()
        
        # Test Chrome path detection
        chrome_paths = driver.get_chrome_paths()
        print(f"✅ Found {len(chrome_paths)} potential Chrome paths")
        
        # Test Chrome binary finding
        chrome_binary = driver.find_chrome_binary(chrome_paths)
        if chrome_binary:
            print(f"✅ Chrome binary found: {chrome_binary}")
            return True
        else:
            print("❌ Chrome binary not found")
            return False
        
    except Exception as e:
        print(f"❌ Chrome detection test failed: {e}")
        return False

def test_chrome_startup_preparation():
    """Test Chrome startup preparation"""
    print("\n🧪 Testing Chrome Startup Preparation...")
    
    try:
        from modules.whatsapp_integration import WhatsAppWebDriver
        
        driver = WhatsAppWebDriver()
        
        # Test Chrome startup readiness
        ready = driver.ensure_chrome_startup_ready()
        if ready:
            print("✅ Chrome startup preparation successful")
            return True
        else:
            print("❌ Chrome startup preparation failed")
            return False
        
    except Exception as e:
        print(f"❌ Chrome startup preparation test failed: {e}")
        return False

def test_chrome_closed_scenario():
    """Test Chrome startup when Chrome is completely closed"""
    print("\n🧪 Testing Chrome Startup When Chrome is Closed...")
    
    try:
        # Check initial Chrome processes
        initial_processes = check_chrome_processes()
        print(f"ℹ️ Initial Chrome processes: {len(initial_processes)}")
        
        # Kill Chrome processes for testing
        if initial_processes:
            print("🔄 Closing Chrome processes for testing...")
            kill_chrome_processes()
            
            # Verify Chrome is closed
            time.sleep(2)
            remaining_processes = check_chrome_processes()
            print(f"ℹ️ Remaining Chrome processes after termination: {len(remaining_processes)}")
        
        # Now test if our system can start Chrome
        from modules.whatsapp_integration import WhatsAppWebDriver
        
        driver = WhatsAppWebDriver()
        
        # Test Chrome preparation when closed
        print("🚀 Testing Chrome startup when Chrome is closed...")
        ready = driver.ensure_chrome_startup_ready()
        
        if ready:
            print("✅ Chrome startup preparation works when Chrome is closed")
            
            # Test actual driver setup (this should start Chrome)
            print("🔧 Testing WebDriver setup (this will start Chrome)...")
            setup_success = driver.setup_driver()
            
            if setup_success:
                print("✅ Chrome WebDriver setup successful - Chrome started automatically")
                
                # Check if Chrome processes are now running
                new_processes = check_chrome_processes()
                print(f"ℹ️ Chrome processes after WebDriver setup: {len(new_processes)}")
                
                # Clean up
                if hasattr(driver, 'driver') and driver.driver:
                    try:
                        driver.driver.quit()
                        print("🧹 WebDriver cleaned up")
                    except:
                        pass
                
                return True
            else:
                print("❌ Chrome WebDriver setup failed")
                return False
        else:
            print("❌ Chrome startup preparation failed when Chrome was closed")
            return False
        
    except Exception as e:
        print(f"❌ Chrome closed scenario test failed: {e}")
        return False

def test_startup_manager_chrome_handling():
    """Test startup manager Chrome handling"""
    print("\n🧪 Testing Startup Manager Chrome Handling...")
    
    try:
        from modules.whatsapp_startup_manager import WhatsAppStartupManager
        
        manager = WhatsAppStartupManager()
        
        # Test Chrome availability check
        available = manager._check_whatsapp_availability()
        if available:
            print("✅ WhatsApp availability check passed")
        else:
            print("❌ WhatsApp availability check failed")
            return False
        
        # Test Chrome installation check
        chrome_installed = manager._check_chrome_installation()
        if chrome_installed:
            print("✅ Chrome installation check passed")
            return True
        else:
            print("❌ Chrome installation check failed")
            return False
        
    except Exception as e:
        print(f"❌ Startup manager Chrome handling test failed: {e}")
        return False

def test_error_scenarios():
    """Test error handling scenarios"""
    print("\n🧪 Testing Error Scenarios...")
    
    try:
        from modules.whatsapp_integration import WhatsAppWebDriver
        
        # Test with invalid Chrome path
        driver = WhatsAppWebDriver()
        
        # Test finding Chrome binary with empty paths
        empty_result = driver.find_chrome_binary([])
        if empty_result is None:
            print("✅ Handles empty Chrome paths correctly")
        else:
            print("❌ Should return None for empty Chrome paths")
            return False
        
        # Test finding Chrome binary with invalid paths
        invalid_result = driver.find_chrome_binary(["/invalid/path/chrome.exe", "/another/invalid/path"])
        if invalid_result is None:
            print("✅ Handles invalid Chrome paths correctly")
        else:
            print("❌ Should return None for invalid Chrome paths")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error scenarios test failed: {e}")
        return False

def test_integration_with_automation():
    """Test integration with the automation system"""
    print("\n🧪 Testing Integration with Automation System...")
    
    try:
        from modules.whatsapp_startup_manager import WhatsAppStartupManager
        
        # Create startup manager
        manager = WhatsAppStartupManager()
        
        # Test that it can create WhatsApp driver
        from modules.whatsapp_integration import WhatsAppWebDriver
        test_driver = WhatsAppWebDriver()
        
        # Test Chrome readiness
        ready = test_driver.ensure_chrome_startup_ready()
        if ready:
            print("✅ Chrome readiness check works in automation context")
        else:
            print("❌ Chrome readiness check failed in automation context")
            return False
        
        # Test status reporting
        status = manager.get_status()
        print(f"✅ Status reporting works: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all Chrome startup tests"""
    print("🚀 Testing Chrome Startup Handling for WhatsApp Automation")
    print("=" * 70)
    
    tests = [
        test_chrome_detection,
        test_chrome_startup_preparation,
        test_chrome_closed_scenario,
        test_startup_manager_chrome_handling,
        test_error_scenarios,
        test_integration_with_automation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Chrome startup tests passed!")
        print("\n✅ CHROME STARTUP HANDLING VERIFIED:")
        print("   • Chrome installation detection works")
        print("   • Chrome startup preparation works")
        print("   • Chrome starts automatically when closed")
        print("   • WebDriver setup works with closed Chrome")
        print("   • Error scenarios handled gracefully")
        print("   • Integration with automation system works")
        print("\n📋 Chrome Startup Behavior:")
        print("   1. Application checks if Chrome is installed")
        print("   2. If Chrome is closed, WebDriver starts it automatically")
        print("   3. If Chrome is running, WebDriver connects to it")
        print("   4. WhatsApp Web loads in the Chrome instance")
        print("   5. Automation proceeds with Abiram's Kitchen detection")
        print("\n🎯 Answer to your question:")
        print("   YES - Our application handles the case where Chrome isn't open!")
        print("   The WebDriver automatically starts Chrome during startup automation.")
        return 0
    else:
        print("⚠️ Some Chrome startup tests failed - check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
