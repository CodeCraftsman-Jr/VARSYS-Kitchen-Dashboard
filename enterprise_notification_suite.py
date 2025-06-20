#!/usr/bin/env python3
"""
Enterprise Notification Suite
Complete integration of all advanced notification features
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import threading
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    print("⚠️ PySide6 not available - using fallback implementations")

# Import all notification system components
from modules.enhanced_notification_system import (
    get_notification_manager, NotificationPanel,
    notify_emergency, notify_critical, notify_error, notify_warning,
    notify_success, notify_info, notify_inventory, notify_staff,
    notify_schedule, notify_budget, notify_recipe, notify_maintenance
)

from notification_templates import NotificationTemplateManager
from advanced_notification_features import AdvancedNotificationManager
from notification_dashboard import NotificationDashboard

# Import performance and security components
try:
    from notification_performance_optimizer import OptimizedNotificationManager, PerformanceMonitor
    from notification_security_compliance import NotificationSecurityManager, SecurityPolicy
except ImportError:
    print("⚠️ Some advanced modules not available - using basic implementations")
    OptimizedNotificationManager = None
    NotificationSecurityManager = None

class EnterpriseNotificationSuite:
    """Complete enterprise notification suite with all features"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.components = {}
        self.metrics = {
            'total_notifications': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'security_validations': 0,
            'performance_optimizations': 0,
            'template_usage': 0
        }
        
        self._initialize_components()
        self._setup_integration()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default enterprise configuration"""
        return {
            'performance_optimization': True,
            'security_compliance': True,
            'template_system': True,
            'advanced_features': True,
            'dashboard_enabled': True,
            'audit_logging': True,
            'encryption_enabled': True,
            'rate_limiting': True,
            'max_notifications_per_minute': 100,
            'data_retention_days': 90,
            'cache_size': 2000,
            'worker_threads': 3,
            'delivery_channels': ['gui', 'email', 'push'],
            'security_level': 'standard'
        }
    
    def _initialize_components(self):
        """Initialize all notification system components"""
        try:
            # Core notification system
            self.components['core'] = get_notification_manager()
            print("✅ Core notification system initialized")
            
            # Template system
            if self.config.get('template_system', True):
                self.components['templates'] = NotificationTemplateManager()
                print("✅ Template system initialized")
            
            # Advanced features
            if self.config.get('advanced_features', True):
                self.components['advanced'] = AdvancedNotificationManager()
                print("✅ Advanced features initialized")
            
            # Performance optimization
            if self.config.get('performance_optimization', True) and OptimizedNotificationManager:
                self.components['performance'] = OptimizedNotificationManager()
                print("✅ Performance optimization initialized")
            
            # Security and compliance
            if self.config.get('security_compliance', True) and NotificationSecurityManager:
                security_policy = SecurityPolicy(
                    encryption_required=self.config.get('encryption_enabled', True),
                    audit_logging=self.config.get('audit_logging', True),
                    rate_limiting=self.config.get('rate_limiting', True),
                    max_notifications_per_minute=self.config.get('max_notifications_per_minute', 100)
                )
                self.components['security'] = NotificationSecurityManager(security_policy)
                print("✅ Security and compliance initialized")
            
            # Dashboard (if GUI available)
            if self.config.get('dashboard_enabled', True):
                try:
                    self.components['dashboard'] = NotificationDashboard()
                    print("✅ Dashboard initialized")
                except Exception as e:
                    print(f"⚠️ Dashboard initialization failed: {e}")
            
        except Exception as e:
            print(f"❌ Component initialization error: {e}")
    
    def _setup_integration(self):
        """Setup integration between components"""
        try:
            # Create integration hooks
            self.notification_hooks = []
            
            # Add performance monitoring hook
            if 'performance' in self.components:
                self.notification_hooks.append(self._performance_hook)
            
            # Add security validation hook
            if 'security' in self.components:
                self.notification_hooks.append(self._security_hook)
            
            # Add analytics hook
            self.notification_hooks.append(self._analytics_hook)
            
            print(f"✅ Integration setup complete with {len(self.notification_hooks)} hooks")
            
        except Exception as e:
            print(f"❌ Integration setup error: {e}")
    
    def send_notification(self, title: str, message: str, category: str = "info",
                         priority: int = 10, source: str = "System", 
                         user_context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Send notification through the enterprise suite"""
        
        result = {
            'success': False,
            'notification_id': f"{category}_{int(time.time() * 1000)}",
            'timestamp': datetime.now().isoformat(),
            'hooks_executed': [],
            'performance_metrics': {},
            'security_validation': {},
            'delivery_channels': [],
            'errors': []
        }
        
        try:
            # Create notification object
            notification = {
                'id': result['notification_id'],
                'title': title,
                'message': message,
                'category': category,
                'priority': priority,
                'source': source,
                'timestamp': result['timestamp'],
                'metadata': kwargs
            }
            
            # Execute pre-send hooks
            for hook in self.notification_hooks:
                try:
                    hook_result = hook(notification, user_context, 'pre_send')
                    result['hooks_executed'].append(hook.__name__)
                    
                    # Merge hook results
                    if isinstance(hook_result, dict):
                        for key, value in hook_result.items():
                            if key in result:
                                if isinstance(result[key], dict) and isinstance(value, dict):
                                    result[key].update(value)
                                else:
                                    result[key] = value
                            else:
                                result[key] = value
                
                except Exception as e:
                    result['errors'].append(f"Hook {hook.__name__}: {str(e)}")
            
            # Send through appropriate system
            if 'performance' in self.components:
                # Use optimized manager
                success = self.components['performance'].send_notification(
                    title, message, category, priority, source, **kwargs
                )
            else:
                # Use core manager
                success = self.components['core'].notify(
                    title, message, category, priority, source, True, True, 5000
                )
            
            result['success'] = success
            
            # Execute post-send hooks
            for hook in self.notification_hooks:
                try:
                    hook(notification, user_context, 'post_send')
                except Exception as e:
                    result['errors'].append(f"Post-hook {hook.__name__}: {str(e)}")
            
            # Update metrics
            self.metrics['total_notifications'] += 1
            if success:
                self.metrics['successful_deliveries'] += 1
            else:
                self.metrics['failed_deliveries'] += 1
            
        except Exception as e:
            result['errors'].append(f"Send error: {str(e)}")
        
        return result
    
    def _performance_hook(self, notification: Dict[str, Any], 
                         user_context: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Performance monitoring hook"""
        if phase == 'pre_send':
            start_time = time.time()
            notification['_perf_start'] = start_time
            
            # Get performance metrics if available
            if hasattr(self.components.get('performance'), 'get_performance_metrics'):
                metrics = self.components['performance'].get_performance_metrics()
                self.metrics['performance_optimizations'] += 1
                return {'performance_metrics': metrics}
        
        elif phase == 'post_send':
            if '_perf_start' in notification:
                processing_time = time.time() - notification['_perf_start']
                return {'processing_time_ms': processing_time * 1000}
        
        return {}
    
    def _security_hook(self, notification: Dict[str, Any], 
                      user_context: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Security validation hook"""
        if phase == 'pre_send' and 'security' in self.components:
            try:
                validation = self.components['security'].validate_notification(
                    notification, user_context
                )
                self.metrics['security_validations'] += 1
                return {'security_validation': validation}
            except Exception as e:
                return {'security_validation': {'error': str(e)}}
        
        return {}
    
    def _analytics_hook(self, notification: Dict[str, Any], 
                       user_context: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Analytics collection hook"""
        if phase == 'post_send':
            # Collect analytics data
            analytics = {
                'category': notification.get('category'),
                'priority': notification.get('priority'),
                'source': notification.get('source'),
                'timestamp': notification.get('timestamp'),
                'user_id': user_context.get('user_id') if user_context else None
            }
            
            # Store analytics (in production, this would go to a database)
            return {'analytics': analytics}
        
        return {}
    
    def send_template_notification(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Send notification using template"""
        if 'templates' not in self.components:
            return {'success': False, 'error': 'Template system not available'}
        
        try:
            success = self.components['templates'].send_from_template(template_id, **kwargs)
            self.metrics['template_usage'] += 1
            
            return {
                'success': success,
                'template_id': template_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all components"""
        metrics = {
            'suite_metrics': self.metrics.copy(),
            'timestamp': datetime.now().isoformat(),
            'components_active': list(self.components.keys()),
            'configuration': self.config.copy()
        }
        
        # Add component-specific metrics
        if 'performance' in self.components:
            try:
                if hasattr(self.components['performance'], 'get_performance_metrics'):
                    metrics['performance_metrics'] = self.components['performance'].get_performance_metrics()
            except:
                pass
        
        if 'advanced' in self.components:
            try:
                if hasattr(self.components['advanced'], 'get_analytics_summary'):
                    metrics['advanced_analytics'] = self.components['advanced'].get_analytics_summary()
            except:
                pass
        
        return metrics
    
    def show_dashboard(self):
        """Show the notification dashboard"""
        if 'dashboard' in self.components:
            try:
                self.components['dashboard'].show()
                return True
            except Exception as e:
                print(f"❌ Error showing dashboard: {e}")
                return False
        else:
            print("⚠️ Dashboard not available")
            return False
    
    def shutdown(self):
        """Shutdown the enterprise suite"""
        print("🔄 Shutting down Enterprise Notification Suite...")
        
        # Shutdown components in reverse order
        for component_name in reversed(list(self.components.keys())):
            try:
                component = self.components[component_name]
                if hasattr(component, 'shutdown'):
                    component.shutdown()
                print(f"✅ {component_name} shutdown complete")
            except Exception as e:
                print(f"⚠️ Error shutting down {component_name}: {e}")
        
        print("✅ Enterprise Notification Suite shutdown complete")

def create_enterprise_demo():
    """Create comprehensive enterprise demo"""
    print("🚀 Enterprise Notification Suite Demo")
    print("=" * 60)
    
    # Create enterprise suite with custom configuration
    config = {
        'performance_optimization': True,
        'security_compliance': True,
        'template_system': True,
        'advanced_features': True,
        'dashboard_enabled': True,
        'max_notifications_per_minute': 50,
        'security_level': 'high'
    }
    
    suite = EnterpriseNotificationSuite(config)
    
    print(f"🎯 Enterprise suite initialized with {len(suite.components)} components")
    
    # Test various notification scenarios
    test_scenarios = [
        {
            'title': 'System Startup',
            'message': 'Enterprise notification suite is now operational',
            'category': 'system',
            'priority': 10,
            'source': 'Enterprise Suite'
        },
        {
            'title': 'Critical Alert',
            'message': 'Database connection lost - immediate attention required',
            'category': 'critical',
            'priority': 2,
            'source': 'Database Monitor'
        },
        {
            'title': 'Security Event',
            'message': 'Multiple failed login attempts detected',
            'category': 'security',
            'priority': 4,
            'source': 'Security System'
        },
        {
            'title': 'Performance Alert',
            'message': 'High CPU usage detected on server cluster',
            'category': 'warning',
            'priority': 6,
            'source': 'Performance Monitor'
        }
    ]
    
    user_context = {
        'user_id': 'enterprise_admin',
        'role': 'administrator',
        'ip_address': '192.168.1.100'
    }
    
    print("\n📤 Testing enterprise notification scenarios:")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['title']}")
        
        result = suite.send_notification(
            **scenario,
            user_context=user_context
        )
        
        print(f"   ✅ Success: {result['success']}")
        print(f"   🔗 Hooks: {len(result['hooks_executed'])}")
        
        if result.get('performance_metrics'):
            print(f"   ⚡ Performance: Optimized")
        
        if result.get('security_validation'):
            validation = result['security_validation']
            if validation.get('valid', True):
                print(f"   🔒 Security: Validated")
            else:
                print(f"   ⚠️ Security: {len(validation.get('security_warnings', []))} warnings")
        
        if result.get('errors'):
            print(f"   ❌ Errors: {len(result['errors'])}")
    
    # Test template notifications
    print(f"\n📋 Testing template notifications:")
    
    template_tests = [
        ('low_stock', {'item_name': 'Coffee Beans', 'current_quantity': 2, 'minimum_quantity': 10, 'unit': 'kg'}),
        ('daily_summary', {'sales_count': 75, 'revenue_amount': 35000, 'efficiency_percent': 94})
    ]
    
    for template_id, params in template_tests:
        result = suite.send_template_notification(template_id, **params)
        print(f"   📋 {template_id}: {'✅ Success' if result['success'] else '❌ Failed'}")
    
    # Show comprehensive metrics
    print(f"\n📊 Comprehensive Enterprise Metrics:")
    metrics = suite.get_comprehensive_metrics()
    
    print(f"   🎯 Suite Metrics:")
    for key, value in metrics['suite_metrics'].items():
        print(f"      • {key.replace('_', ' ').title()}: {value}")
    
    print(f"   🔧 Active Components: {', '.join(metrics['components_active'])}")
    
    # Show dashboard if available
    print(f"\n📊 Opening enterprise dashboard...")
    dashboard_shown = suite.show_dashboard()
    
    if dashboard_shown:
        print("   ✅ Dashboard opened successfully")
    else:
        print("   ⚠️ Dashboard not available in this environment")
    
    print(f"\n✅ Enterprise demo completed successfully!")
    print(f"📈 Total notifications processed: {metrics['suite_metrics']['total_notifications']}")
    print(f"🎯 Success rate: {(metrics['suite_metrics']['successful_deliveries'] / max(metrics['suite_metrics']['total_notifications'], 1)) * 100:.1f}%")
    
    return suite

if __name__ == "__main__":
    suite = create_enterprise_demo()
    
    print(f"\n🎮 Enterprise suite is running...")
    print(f"💡 Press Ctrl+C to shutdown gracefully")
    
    try:
        # Keep running for demonstration
        time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n🔄 Graceful shutdown initiated...")
    finally:
        suite.shutdown()
