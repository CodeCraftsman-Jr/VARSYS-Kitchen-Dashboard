#!/usr/bin/env python3
"""
Simple Performance Test
Quick performance validation for the ultimate notification system
"""

import sys
import os
import time
import platform
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner(title: str, width: int = 70):
    """Print a formatted banner"""
    print("=" * width)
    print(f" {title} ".center(width))
    print("=" * width)

def print_section(title: str):
    """Print a section header"""
    print(f"\n🔹 {title}")
    print("-" * (len(title) + 4))

def test_core_performance():
    """Test core notification system performance"""
    print_section("Testing Enhanced Core System Performance")
    
    try:
        from modules.enhanced_notification_system import notify_info, notify_success, notify_warning
        
        # Warm-up
        notify_info("Warmup", "Warmup message", "Test")
        
        # Performance test
        start_time = time.perf_counter()
        
        for i in range(100):
            notify_info(f"Performance Test {i+1}", f"Test message {i+1}", "Performance Test")
            if i % 10 == 0:
                notify_success(f"Success {i+1}", f"Success message {i+1}", "Performance Test")
            if i % 20 == 0:
                notify_warning(f"Warning {i+1}", f"Warning message {i+1}", "Performance Test")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        notifications_per_second = 110 / total_time  # 100 + 10 + 5 notifications
        
        print(f"✅ Core System Performance:")
        print(f"   • Total notifications: 110")
        print(f"   • Total time: {total_time:.3f} seconds")
        print(f"   • Performance: {notifications_per_second:.0f} notifications/second")
        print(f"   • Average time: {(total_time/110)*1000:.2f}ms per notification")
        
        return {
            'notifications_per_second': notifications_per_second,
            'total_time': total_time,
            'average_time_ms': (total_time/110)*1000
        }
        
    except Exception as e:
        print(f"❌ Core system test failed: {e}")
        return None

def test_ai_performance():
    """Test AI intelligence performance"""
    print_section("Testing AI Intelligence Performance")
    
    try:
        from notification_ai_intelligence import NotificationAI
        
        ai = NotificationAI()
        
        test_notification = {
            'title': 'Performance Test Notification',
            'message': 'This is a test notification for AI performance analysis',
            'category': 'test',
            'priority': 10
        }
        
        # Warm-up
        ai.analyze_notification(test_notification)
        
        # Performance test
        start_time = time.perf_counter()
        
        for i in range(50):
            test_notification['title'] = f'AI Test {i+1}'
            test_notification['message'] = f'AI performance test message {i+1}'
            analysis = ai.analyze_notification(test_notification)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        analyses_per_second = 50 / total_time
        
        print(f"✅ AI Intelligence Performance:")
        print(f"   • Total analyses: 50")
        print(f"   • Total time: {total_time:.3f} seconds")
        print(f"   • Performance: {analyses_per_second:.0f} analyses/second")
        print(f"   • Average time: {(total_time/50)*1000:.2f}ms per analysis")
        print(f"   • Last analysis: Sentiment={analysis.sentiment.value}, Intent={analysis.intent.value}")
        
        return {
            'analyses_per_second': analyses_per_second,
            'total_time': total_time,
            'average_time_ms': (total_time/50)*1000
        }
        
    except Exception as e:
        print(f"❌ AI intelligence test failed: {e}")
        return None

def test_template_performance():
    """Test template system performance"""
    print_section("Testing Template System Performance")
    
    try:
        from notification_templates import notify_low_stock, notify_daily_summary, notify_system_startup
        
        # Warm-up
        notify_low_stock("Test Item", 5, 20, "units")
        
        # Performance test
        start_time = time.perf_counter()
        
        for i in range(30):
            notify_low_stock(f"Item {i+1}", 5, 20, "units")
            if i % 3 == 0:
                notify_daily_summary(100 + i, 50000 + (i*1000), 90 + (i%10))
            if i % 5 == 0:
                notify_system_startup(f"System {i+1}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        templates_per_second = 42 / total_time  # 30 + 10 + 6 templates
        
        print(f"✅ Template System Performance:")
        print(f"   • Total templates: 42")
        print(f"   • Total time: {total_time:.3f} seconds")
        print(f"   • Performance: {templates_per_second:.0f} templates/second")
        print(f"   • Average time: {(total_time/42)*1000:.2f}ms per template")
        
        return {
            'templates_per_second': templates_per_second,
            'total_time': total_time,
            'average_time_ms': (total_time/42)*1000
        }
        
    except Exception as e:
        print(f"❌ Template system test failed: {e}")
        return None

def test_mobile_performance():
    """Test mobile integration performance"""
    print_section("Testing Mobile Integration Performance")
    
    try:
        from notification_mobile_integration import MobileNotificationManager, MobileDevice, MobilePlatform
        
        mobile_manager = MobileNotificationManager()
        
        # Register test device
        device = MobileDevice(
            device_id="performance_test_device",
            user_id="performance_test_user",
            platform=MobilePlatform.DESKTOP,
            push_token="performance_test_token",
            app_version="2.0.0",
            os_version="Test OS",
            device_model="Test Device",
            timezone="UTC",
            language="en",
            registered_at=datetime.now(),
            last_active=datetime.now(),
            notification_settings={'push': True, 'in_app': True}
        )
        
        mobile_manager.register_device(device)
        
        # Performance test
        start_time = time.perf_counter()
        
        for i in range(20):
            mobile_manager.send_cross_platform_notification(
                title=f"Mobile Test {i+1}",
                body=f"Mobile performance test message {i+1}",
                category="test",
                priority=10
            )
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        notifications_per_second = 20 / total_time
        
        print(f"✅ Mobile Integration Performance:")
        print(f"   • Total notifications: 20")
        print(f"   • Total time: {total_time:.3f} seconds")
        print(f"   • Performance: {notifications_per_second:.0f} notifications/second")
        print(f"   • Average time: {(total_time/20)*1000:.2f}ms per notification")
        
        return {
            'notifications_per_second': notifications_per_second,
            'total_time': total_time,
            'average_time_ms': (total_time/20)*1000
        }
        
    except Exception as e:
        print(f"❌ Mobile integration test failed: {e}")
        return None

def test_performance_optimizer():
    """Test performance optimizer"""
    print_section("Testing Performance Optimizer")
    
    try:
        from notification_performance_optimizer import OptimizedNotificationManager
        
        optimizer = OptimizedNotificationManager()
        
        # Performance test
        start_time = time.perf_counter()
        
        for i in range(100):
            optimizer.send_notification(
                f"Optimizer Test {i+1}",
                f"Performance optimizer test message {i+1}",
                "performance",
                10,
                "Performance Test"
            )
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        notifications_per_second = 100 / total_time
        
        print(f"✅ Performance Optimizer:")
        print(f"   • Total notifications: 100")
        print(f"   • Total time: {total_time:.3f} seconds")
        print(f"   • Performance: {notifications_per_second:.0f} notifications/second")
        print(f"   • Average time: {(total_time/100)*1000:.2f}ms per notification")
        
        return {
            'notifications_per_second': notifications_per_second,
            'total_time': total_time,
            'average_time_ms': (total_time/100)*1000
        }
        
    except Exception as e:
        print(f"❌ Performance optimizer test failed: {e}")
        return None

def main():
    """Main performance test function"""
    print_banner("🚀 ULTIMATE NOTIFICATION SYSTEM - PERFORMANCE TEST")
    
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Platform: {platform.platform()}")
    print(f"🐍 Python: {platform.python_version()}")
    
    # Run all performance tests
    test_start = time.perf_counter()
    
    results = {}
    results['core_system'] = test_core_performance()
    results['ai_intelligence'] = test_ai_performance()
    results['template_system'] = test_template_performance()
    results['mobile_integration'] = test_mobile_performance()
    results['performance_optimizer'] = test_performance_optimizer()
    
    test_end = time.perf_counter()
    total_test_time = test_end - test_start
    
    # Calculate overall performance
    print_banner("🏆 PERFORMANCE TEST RESULTS")
    
    successful_tests = sum(1 for result in results.values() if result is not None)
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"📊 Test Summary:")
    print(f"   • Total Tests: {total_tests}")
    print(f"   • Successful: {successful_tests}")
    print(f"   • Success Rate: {success_rate:.1f}%")
    print(f"   • Total Test Time: {total_test_time:.2f} seconds")
    
    print(f"\n📈 Performance Results:")
    
    # Core system
    if results['core_system']:
        core_perf = results['core_system']['notifications_per_second']
        print(f"   🔔 Core System: {core_perf:.0f} notifications/second")
    
    # AI intelligence
    if results['ai_intelligence']:
        ai_perf = results['ai_intelligence']['analyses_per_second']
        print(f"   🤖 AI Intelligence: {ai_perf:.0f} analyses/second")
    
    # Template system
    if results['template_system']:
        template_perf = results['template_system']['templates_per_second']
        print(f"   📋 Template System: {template_perf:.0f} templates/second")
    
    # Mobile integration
    if results['mobile_integration']:
        mobile_perf = results['mobile_integration']['notifications_per_second']
        print(f"   📱 Mobile Integration: {mobile_perf:.0f} notifications/second")
    
    # Performance optimizer
    if results['performance_optimizer']:
        optimizer_perf = results['performance_optimizer']['notifications_per_second']
        print(f"   ⚡ Performance Optimizer: {optimizer_perf:.0f} notifications/second")
    
    # Calculate performance score
    performance_scores = []
    if results['core_system']:
        performance_scores.append(min(100, results['core_system']['notifications_per_second'] / 100))
    if results['ai_intelligence']:
        performance_scores.append(min(100, results['ai_intelligence']['analyses_per_second'] / 10))
    if results['performance_optimizer']:
        performance_scores.append(min(100, results['performance_optimizer']['notifications_per_second'] / 100))
    
    if performance_scores:
        overall_score = sum(performance_scores) / len(performance_scores)
        print(f"\n🎯 Overall Performance Score: {overall_score:.1f}/100")
        
        if overall_score >= 80:
            grade = "A (Excellent)"
            status = "🎉 EXCEPTIONAL PERFORMANCE!"
        elif overall_score >= 60:
            grade = "B (Good)"
            status = "✅ GOOD PERFORMANCE!"
        elif overall_score >= 40:
            grade = "C (Average)"
            status = "⚠️ AVERAGE PERFORMANCE"
        else:
            grade = "D (Needs Improvement)"
            status = "❌ NEEDS IMPROVEMENT"
        
        print(f"🏆 Performance Grade: {grade}")
        print(f"📊 Status: {status}")
    
    # Final assessment
    if success_rate >= 80 and (not performance_scores or sum(performance_scores)/len(performance_scores) >= 40):
        print(f"\n🚀 PERFORMANCE TEST: SUCCESS!")
        print(f"✅ The ultimate notification system meets performance requirements!")
        print(f"🌟 Ready for production deployment!")
        return True
    else:
        print(f"\n⚠️ PERFORMANCE TEST: NEEDS ATTENTION")
        print(f"🔧 Some components may need optimization")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ Performance test completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Performance test indicates issues")
        sys.exit(1)
