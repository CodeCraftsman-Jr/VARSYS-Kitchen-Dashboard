#!/usr/bin/env python3
"""
Ultimate Performance Benchmark
Comprehensive performance testing and optimization for the ultimate notification system
"""

import sys
import os
import time
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import gc

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner(title: str, width: int = 80):
    """Print a formatted banner"""
    print("=" * width)
    print(f" {title} ".center(width))
    print("=" * width)

def print_section(title: str, emoji: str = "🔹"):
    """Print a section header"""
    print(f"\n{emoji} {title}")
    print("-" * (len(title) + 4))

class UltimatePerformanceBenchmark:
    """Comprehensive performance benchmark for the ultimate notification system"""
    
    def __init__(self):
        self.results = {}
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmarking context"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def benchmark_core_system(self) -> Dict[str, Any]:
        """Benchmark the enhanced core notification system"""
        print_section("⚡ Benchmarking Enhanced Core System")
        
        try:
            from modules.enhanced_notification_system import (
                get_notification_manager, notify_emergency, notify_critical,
                notify_success, notify_info, notify_inventory, notify_staff
            )
            
            # Test notification functions
            functions = [notify_emergency, notify_critical, notify_success, 
                        notify_info, notify_inventory, notify_staff]
            
            # Warm-up
            for func in functions:
                func("Warmup", "Warmup message", "Benchmark")
            
            # Benchmark each function
            results = {}
            for i, func in enumerate(functions):
                func_name = func.__name__
                
                # Single notification timing
                start_time = time.perf_counter()
                func(f"Benchmark {i+1}", f"Performance test message {i+1}", "Benchmark")
                single_time = time.perf_counter() - start_time
                
                # Batch timing (100 notifications)
                start_time = time.perf_counter()
                for j in range(100):
                    func(f"Batch {j+1}", f"Batch test message {j+1}", "Benchmark")
                batch_time = time.perf_counter() - start_time
                
                results[func_name] = {
                    'single_time_ms': single_time * 1000,
                    'batch_time_ms': batch_time * 1000,
                    'batch_avg_ms': (batch_time / 100) * 1000,
                    'notifications_per_second': 100 / batch_time
                }
                
                print(f"   ✅ {func_name}: {results[func_name]['notifications_per_second']:.0f} notifications/sec")
            
            # Overall core system performance
            total_notifications = len(functions) * 101  # 1 warmup + 100 batch per function
            total_time = sum(r['batch_time_ms'] for r in results.values()) / 1000
            overall_performance = total_notifications / total_time
            
            core_results = {
                'individual_functions': results,
                'total_notifications': total_notifications,
                'total_time_seconds': total_time,
                'overall_notifications_per_second': overall_performance,
                'average_processing_time_ms': (total_time / total_notifications) * 1000
            }
            
            print(f"🎯 Core System Overall: {overall_performance:.0f} notifications/second")
            return core_results
            
        except Exception as e:
            print(f"❌ Core system benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_ai_intelligence(self) -> Dict[str, Any]:
        """Benchmark AI intelligence features"""
        print_section("🤖 Benchmarking AI Intelligence")
        
        try:
            from notification_ai_intelligence import NotificationAI
            
            ai = NotificationAI()
            
            # Test notifications for AI analysis
            test_notifications = [
                {
                    'title': 'Critical System Failure',
                    'message': 'Database server has crashed and requires immediate attention',
                    'category': 'critical',
                    'priority': 1
                },
                {
                    'title': 'Low Stock Alert',
                    'message': 'Coffee beans inventory is running low',
                    'category': 'inventory',
                    'priority': 8
                },
                {
                    'title': 'Security Warning',
                    'message': 'Multiple failed login attempts detected',
                    'category': 'security',
                    'priority': 4
                },
                {
                    'title': 'Backup Completed',
                    'message': 'Daily backup process completed successfully',
                    'category': 'success',
                    'priority': 12
                },
                {
                    'title': 'Budget Exceeded',
                    'message': 'Monthly food budget has been exceeded by 15%',
                    'category': 'budget',
                    'priority': 6
                }
            ]
            
            # Warm-up
            for notification in test_notifications[:2]:
                ai.analyze_notification(notification)
            
            # Benchmark AI analysis
            analysis_times = []
            analysis_results = []
            
            for notification in test_notifications:
                start_time = time.perf_counter()
                analysis = ai.analyze_notification(notification)
                analysis_time = time.perf_counter() - start_time
                
                analysis_times.append(analysis_time * 1000)  # Convert to ms
                analysis_results.append({
                    'title': notification['title'],
                    'sentiment': analysis.sentiment.value,
                    'intent': analysis.intent.value,
                    'urgency_score': analysis.urgency_score,
                    'confidence': analysis.confidence,
                    'processing_time_ms': analysis_time * 1000
                })
                
                print(f"   ✅ {notification['title']}: {analysis_time*1000:.2f}ms")
            
            # Batch analysis benchmark
            start_time = time.perf_counter()
            for _ in range(100):
                for notification in test_notifications:
                    ai.analyze_notification(notification)
            batch_time = time.perf_counter() - start_time
            
            ai_results = {
                'individual_analyses': analysis_results,
                'average_analysis_time_ms': statistics.mean(analysis_times),
                'min_analysis_time_ms': min(analysis_times),
                'max_analysis_time_ms': max(analysis_times),
                'batch_analyses_per_second': (100 * len(test_notifications)) / batch_time,
                'total_batch_time_seconds': batch_time
            }
            
            print(f"🎯 AI Intelligence: {ai_results['batch_analyses_per_second']:.0f} analyses/second")
            return ai_results
            
        except Exception as e:
            print(f"❌ AI intelligence benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_template_system(self) -> Dict[str, Any]:
        """Benchmark template system performance"""
        print_section("📋 Benchmarking Template System")
        
        try:
            from notification_templates import (
                notify_low_stock, notify_daily_summary, notify_system_startup,
                notify_shift_reminder, notify_budget_exceeded, notify_maintenance_due
            )
            
            # Template functions to test
            template_tests = [
                ('low_stock', lambda: notify_low_stock("Test Item", 5, 20, "units")),
                ('daily_summary', lambda: notify_daily_summary(100, 50000, 95)),
                ('system_startup', lambda: notify_system_startup("Benchmark System")),
                ('shift_reminder', lambda: notify_shift_reminder("Test User", 30, "Kitchen")),
                ('budget_exceeded', lambda: notify_budget_exceeded("Test Category", 15000, 12000)),
                ('maintenance_due', lambda: notify_maintenance_due("Test Equipment", "2025-06-20"))
            ]
            
            # Warm-up
            for name, func in template_tests[:2]:
                func()
            
            # Benchmark each template
            template_results = {}
            for name, func in template_tests:
                # Single template timing
                start_time = time.perf_counter()
                func()
                single_time = time.perf_counter() - start_time
                
                # Batch timing (50 templates)
                start_time = time.perf_counter()
                for _ in range(50):
                    func()
                batch_time = time.perf_counter() - start_time
                
                template_results[name] = {
                    'single_time_ms': single_time * 1000,
                    'batch_time_ms': batch_time * 1000,
                    'templates_per_second': 50 / batch_time
                }
                
                print(f"   ✅ {name}: {template_results[name]['templates_per_second']:.0f} templates/sec")
            
            # Overall template performance
            total_templates = len(template_tests) * 51  # 1 single + 50 batch per template
            total_time = sum(r['batch_time_ms'] for r in template_results.values()) / 1000
            overall_performance = total_templates / total_time
            
            template_system_results = {
                'individual_templates': template_results,
                'total_templates': total_templates,
                'total_time_seconds': total_time,
                'overall_templates_per_second': overall_performance
            }
            
            print(f"🎯 Template System: {overall_performance:.0f} templates/second")
            return template_system_results
            
        except Exception as e:
            print(f"❌ Template system benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_mobile_integration(self) -> Dict[str, Any]:
        """Benchmark mobile integration performance"""
        print_section("📱 Benchmarking Mobile Integration")
        
        try:
            from notification_mobile_integration import MobileNotificationManager, MobileDevice, MobilePlatform
            
            mobile_manager = MobileNotificationManager()
            
            # Create test devices
            test_devices = []
            platforms = [MobilePlatform.IOS, MobilePlatform.ANDROID, MobilePlatform.WEB]
            
            for i, platform in enumerate(platforms):
                device = MobileDevice(
                    device_id=f"benchmark_device_{i+1}",
                    user_id=f"benchmark_user_{i+1}",
                    platform=platform,
                    push_token=f"benchmark_token_{i+1}",
                    app_version="2.0.0",
                    os_version="Latest",
                    device_model="Benchmark Device",
                    timezone="UTC",
                    language="en",
                    registered_at=datetime.now(),
                    last_active=datetime.now(),
                    notification_settings={'push': True, 'email': True}
                )
                test_devices.append(device)
                mobile_manager.register_device(device)
            
            # Benchmark device registration
            start_time = time.perf_counter()
            for _ in range(100):
                for i, platform in enumerate(platforms):
                    device = MobileDevice(
                        device_id=f"batch_device_{i+1}_{time.time()}",
                        user_id=f"batch_user_{i+1}",
                        platform=platform,
                        push_token=f"batch_token_{i+1}_{time.time()}",
                        app_version="2.0.0",
                        os_version="Latest",
                        device_model="Batch Device",
                        timezone="UTC",
                        language="en",
                        registered_at=datetime.now(),
                        last_active=datetime.now(),
                        notification_settings={'push': True}
                    )
                    mobile_manager.register_device(device)
            registration_time = time.perf_counter() - start_time
            
            # Benchmark cross-platform notifications
            start_time = time.perf_counter()
            for i in range(50):
                mobile_manager.send_cross_platform_notification(
                    title=f"Benchmark Notification {i+1}",
                    body=f"Performance test message {i+1}",
                    category="benchmark",
                    priority=10
                )
            notification_time = time.perf_counter() - start_time
            
            mobile_results = {
                'device_registrations_per_second': (100 * len(platforms)) / registration_time,
                'cross_platform_notifications_per_second': 50 / notification_time,
                'total_devices_registered': len(test_devices) + (100 * len(platforms)),
                'registration_time_seconds': registration_time,
                'notification_time_seconds': notification_time
            }
            
            print(f"🎯 Mobile Integration: {mobile_results['cross_platform_notifications_per_second']:.0f} notifications/sec")
            return mobile_results
            
        except Exception as e:
            print(f"❌ Mobile integration benchmark failed: {e}")
            return {'error': str(e)}
    
    def benchmark_performance_optimizer(self) -> Dict[str, Any]:
        """Benchmark the performance optimizer"""
        print_section("⚡ Benchmarking Performance Optimizer")
        
        try:
            from notification_performance_optimizer import OptimizedNotificationManager
            
            optimizer = OptimizedNotificationManager()
            
            # Benchmark optimized notifications
            start_time = time.perf_counter()
            for i in range(1000):
                optimizer.send_notification(
                    f"Optimized Test {i+1}",
                    f"Performance optimization test message {i+1}",
                    "performance",
                    10,
                    "Benchmark"
                )
            optimization_time = time.perf_counter() - start_time
            
            # Get performance metrics
            if hasattr(optimizer, 'get_performance_metrics'):
                metrics = optimizer.get_performance_metrics()
            else:
                metrics = {}
            
            optimizer_results = {
                'optimized_notifications_per_second': 1000 / optimization_time,
                'total_time_seconds': optimization_time,
                'average_time_per_notification_ms': (optimization_time / 1000) * 1000,
                'performance_metrics': metrics
            }
            
            print(f"🎯 Performance Optimizer: {optimizer_results['optimized_notifications_per_second']:.0f} notifications/sec")
            return optimizer_results
            
        except Exception as e:
            print(f"❌ Performance optimizer benchmark failed: {e}")
            return {'error': str(e)}
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark of all systems"""
        print_banner("🚀 ULTIMATE PERFORMANCE BENCHMARK")
        
        print(f"📅 Benchmark Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️ System: {self.system_info['platform']}")
        print(f"🐍 Python: {self.system_info['python_version']}")
        print(f"💾 Memory: {self.system_info['memory_available_gb']:.1f}GB available")
        print(f"⚙️ CPU Cores: {self.system_info['cpu_count']}")
        
        # Run all benchmarks
        benchmark_start = time.perf_counter()
        
        self.results['core_system'] = self.benchmark_core_system()
        self.results['ai_intelligence'] = self.benchmark_ai_intelligence()
        self.results['template_system'] = self.benchmark_template_system()
        self.results['mobile_integration'] = self.benchmark_mobile_integration()
        self.results['performance_optimizer'] = self.benchmark_performance_optimizer()
        
        total_benchmark_time = time.perf_counter() - benchmark_start
        
        # Calculate overall performance score
        performance_scores = []
        
        if 'overall_notifications_per_second' in self.results.get('core_system', {}):
            performance_scores.append(min(100, self.results['core_system']['overall_notifications_per_second'] / 1000))
        
        if 'batch_analyses_per_second' in self.results.get('ai_intelligence', {}):
            performance_scores.append(min(100, self.results['ai_intelligence']['batch_analyses_per_second'] / 100))
        
        if 'overall_templates_per_second' in self.results.get('template_system', {}):
            performance_scores.append(min(100, self.results['template_system']['overall_templates_per_second'] / 1000))
        
        if 'optimized_notifications_per_second' in self.results.get('performance_optimizer', {}):
            performance_scores.append(min(100, self.results['performance_optimizer']['optimized_notifications_per_second'] / 1000))
        
        overall_score = statistics.mean(performance_scores) if performance_scores else 0
        
        # Compile final results
        final_results = {
            'system_info': self.system_info,
            'benchmark_results': self.results,
            'total_benchmark_time_seconds': total_benchmark_time,
            'overall_performance_score': overall_score,
            'performance_grade': self._get_performance_grade(overall_score),
            'summary': self._generate_performance_summary()
        }
        
        return final_results
    
    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score"""
        if score >= 90:
            return "A+ (Exceptional)"
        elif score >= 80:
            return "A (Excellent)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Average)"
        else:
            return "D (Needs Improvement)"
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        summary = {}
        
        # Core system summary
        if 'core_system' in self.results and 'overall_notifications_per_second' in self.results['core_system']:
            summary['core_system_performance'] = f"{self.results['core_system']['overall_notifications_per_second']:.0f} notifications/sec"
        
        # AI intelligence summary
        if 'ai_intelligence' in self.results and 'batch_analyses_per_second' in self.results['ai_intelligence']:
            summary['ai_performance'] = f"{self.results['ai_intelligence']['batch_analyses_per_second']:.0f} analyses/sec"
        
        # Template system summary
        if 'template_system' in self.results and 'overall_templates_per_second' in self.results['template_system']:
            summary['template_performance'] = f"{self.results['template_system']['overall_templates_per_second']:.0f} templates/sec"
        
        # Mobile integration summary
        if 'mobile_integration' in self.results and 'cross_platform_notifications_per_second' in self.results['mobile_integration']:
            summary['mobile_performance'] = f"{self.results['mobile_integration']['cross_platform_notifications_per_second']:.0f} notifications/sec"
        
        # Performance optimizer summary
        if 'performance_optimizer' in self.results and 'optimized_notifications_per_second' in self.results['performance_optimizer']:
            summary['optimizer_performance'] = f"{self.results['performance_optimizer']['optimized_notifications_per_second']:.0f} notifications/sec"
        
        return summary

def main():
    """Main benchmark function"""
    benchmark = UltimatePerformanceBenchmark()
    
    try:
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark()
        
        # Display results
        print_banner("🏆 BENCHMARK RESULTS")
        
        print(f"📊 Overall Performance Score: {results['overall_performance_score']:.1f}/100")
        print(f"🎯 Performance Grade: {results['performance_grade']}")
        print(f"⏱️ Total Benchmark Time: {results['total_benchmark_time_seconds']:.2f} seconds")
        
        print_section("📈 Performance Summary")
        for component, performance in results['summary'].items():
            component_name = component.replace('_', ' ').title()
            print(f"   • {component_name}: {performance}")
        
        print_section("🎯 Key Achievements")
        
        # Extract key performance metrics
        core_perf = results['benchmark_results'].get('core_system', {}).get('overall_notifications_per_second', 0)
        ai_perf = results['benchmark_results'].get('ai_intelligence', {}).get('batch_analyses_per_second', 0)
        optimizer_perf = results['benchmark_results'].get('performance_optimizer', {}).get('optimized_notifications_per_second', 0)
        
        print(f"   🚀 Core System: {core_perf:.0f} notifications/second")
        print(f"   🤖 AI Intelligence: {ai_perf:.0f} analyses/second")
        print(f"   ⚡ Performance Optimizer: {optimizer_perf:.0f} notifications/second")
        
        # Save results to file
        with open('ultimate_benchmark_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: ultimate_benchmark_results.json")
        
        # Final assessment
        if results['overall_performance_score'] >= 80:
            print(f"\n🎉 BENCHMARK SUCCESS: Exceptional performance achieved!")
            print(f"🚀 The ultimate notification system exceeds enterprise standards!")
        elif results['overall_performance_score'] >= 60:
            print(f"\n✅ BENCHMARK PASSED: Good performance achieved!")
            print(f"🎯 The ultimate notification system meets production requirements!")
        else:
            print(f"\n⚠️ BENCHMARK NEEDS IMPROVEMENT: Performance below expectations")
            print(f"🔧 Consider optimization before production deployment")
        
        return results
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return None

if __name__ == "__main__":
    results = main()
    
    if results and results.get('overall_performance_score', 0) >= 60:
        print(f"\n✅ Ultimate notification system benchmark completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Benchmark did not meet minimum requirements")
        sys.exit(1)
