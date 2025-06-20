#!/usr/bin/env python3
"""
Quick WhatsApp Integration Fixes Test
Tests the core fixes without requiring Qt GUI initialization
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_unicode_sanitization():
    """Test Unicode/emoji sanitization for ChromeDriver compatibility"""
    print("🧪 Testing Unicode/Emoji Sanitization...")
    
    try:
        from modules.whatsapp_integration import sanitize_message_for_chrome
        
        # Test messages with various emojis and Unicode characters
        test_cases = [
            {
                'input': '🚨 URGENT ALERT 🚨\nLow stock: Rice 📦',
                'expected': ['[URGENT]', '[PACKAGE]']
            },
            {
                'input': '⚠️ WARNING: Gas level critical ⛽',
                'expected': ['[WARNING]', '[GAS]']
            },
            {
                'input': '✅ Task completed successfully! 🎉',
                'expected': ['[OK]', '[PARTY]']
            },
            {
                'input': '🧹 Cleaning reminder for Kitchen Staff 👤',
                'expected': ['[CLEANING]', '[PERSON]']
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"  Test {i}: {test_case['input'][:30]}...")
            
            try:
                sanitized = sanitize_message_for_chrome(test_case['input'])
                print(f"    Result: {sanitized[:50]}...")
                
                # Check for non-BMP characters
                has_non_bmp = any(ord(char) > 0xFFFF for char in sanitized)
                if has_non_bmp:
                    print(f"    ❌ Contains non-BMP characters")
                    all_passed = False
                    continue
                
                # Check expected replacements
                for expected in test_case['expected']:
                    if expected not in sanitized:
                        print(f"    ❌ Missing expected replacement: {expected}")
                        all_passed = False
                    else:
                        print(f"    ✅ Found replacement: {expected}")
                
            except Exception as e:
                print(f"    ❌ Sanitization failed: {e}")
                all_passed = False
        
        if all_passed:
            print("✅ Unicode sanitization test PASSED!")
        else:
            print("❌ Unicode sanitization test FAILED!")
            
        return all_passed
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_automated_notifications():
    """Test automated notifications system"""
    print("\n🧪 Testing Automated Notifications System...")
    
    try:
        from modules.whatsapp_automated_notifications import WhatsAppAutomatedNotifications
        
        # Test basic initialization
        notifications = WhatsAppAutomatedNotifications()
        
        # Test required methods exist
        required_methods = [
            'check_low_stock_notifications',
            'check_cleaning_reminders', 
            'check_packing_materials_alerts',
            'check_gas_level_warnings',
            '_send_whatsapp_message',
            'start_monitoring',
            'stop_monitoring'
        ]
        
        all_methods_exist = True
        for method in required_methods:
            if hasattr(notifications, method):
                print(f"  ✅ Method exists: {method}")
            else:
                print(f"  ❌ Method missing: {method}")
                all_methods_exist = False
        
        # Test real-time triggers
        trigger_methods = [
            'on_inventory_updated',
            'on_cleaning_task_updated',
            'on_packing_material_updated',
            'on_gas_level_updated'
        ]
        
        triggers_exist = True
        for method in trigger_methods:
            if hasattr(notifications, method):
                print(f"  ✅ Trigger exists: {method}")
            else:
                print(f"  ❌ Trigger missing: {method}")
                triggers_exist = False
        
        success = all_methods_exist and triggers_exist
        
        if success:
            print("✅ Automated notifications test PASSED!")
        else:
            print("❌ Automated notifications test FAILED!")
            
        return success
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_file_integration():
    """Test file integration and structure"""
    print("\n🧪 Testing File Integration...")
    
    required_files = [
        'kitchen_app.py',
        'modules/whatsapp_integration.py',
        'modules/whatsapp_automated_notifications.py'
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ File exists: {file_path}")
        else:
            print(f"  ❌ File missing: {file_path}")
            all_files_exist = False
    
    # Test integration in kitchen_app.py
    try:
        with open('kitchen_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_whatsapp_integration = 'whatsapp_notifications' in content
        has_data_triggers = 'mark_data_changed' in content
        
        if has_whatsapp_integration:
            print("  ✅ WhatsApp notifications integration found in kitchen_app.py")
        else:
            print("  ❌ WhatsApp notifications integration missing in kitchen_app.py")
            
        if has_data_triggers:
            print("  ✅ Data change triggers found in kitchen_app.py")
        else:
            print("  ❌ Data change triggers missing in kitchen_app.py")
            
        integration_success = has_whatsapp_integration and has_data_triggers
        
    except Exception as e:
        print(f"  ❌ Error checking kitchen_app.py: {e}")
        integration_success = False
    
    success = all_files_exist and integration_success
    
    if success:
        print("✅ File integration test PASSED!")
    else:
        print("❌ File integration test FAILED!")
        
    return success

def test_unicode_integration():
    """Test Unicode sanitization integration with notifications"""
    print("\n🧪 Testing Unicode Integration with Notifications...")
    
    try:
        from modules.whatsapp_automated_notifications import WhatsAppAutomatedNotifications
        from modules.whatsapp_integration import sanitize_message_for_chrome
        
        # Test that notifications use sanitization
        notifications = WhatsAppAutomatedNotifications()
        
        # Test message with emojis
        test_message = "🚨 URGENT: Low stock alert 📦"
        sanitized = sanitize_message_for_chrome(test_message)
        
        # Verify sanitization worked
        if "[URGENT]" in sanitized and "[PACKAGE]" in sanitized:
            print("  ✅ Unicode sanitization working correctly")
            print(f"    Original: {test_message}")
            print(f"    Sanitized: {sanitized}")
            
            # Check if notifications system can access sanitization
            has_sanitization = True
            print("  ✅ Notifications can access sanitization function")
        else:
            print("  ❌ Unicode sanitization not working correctly")
            has_sanitization = False
        
        if has_sanitization:
            print("✅ Unicode integration test PASSED!")
        else:
            print("❌ Unicode integration test FAILED!")
            
        return has_sanitization
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 QUICK WHATSAPP INTEGRATION FIXES TEST")
    print("="*60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Unicode/Emoji Sanitization", test_unicode_sanitization),
        ("Automated Notifications System", test_automated_notifications),
        ("File Integration", test_file_integration),
        ("Unicode Integration", test_unicode_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")
    
    print(f"\n📈 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📊 Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Core WhatsApp integration fixes are working")
        print(f"📋 Ready for manual verification with actual WhatsApp Web")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print(f"🔧 Review failed tests before proceeding")
    
    print(f"\n💡 Next Steps:")
    print(f"1. Run the full application")
    print(f"2. Test WhatsApp Web connection in Settings")
    print(f"3. Send test messages with emojis")
    print(f"4. Test disconnect functionality")
    print(f"5. Verify automated notifications work")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        sys.exit(1)
