#!/usr/bin/env python3
"""
Notification Security and Compliance Module
Enterprise-grade security and compliance features for notifications
"""

import sys
import os
import hashlib
import hmac
import secrets
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SecurityLevel(Enum):
    """Security levels for notifications"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    encryption_required: bool = True
    audit_logging: bool = True
    data_retention_days: int = 90
    pii_detection: bool = True
    content_filtering: bool = True
    access_control: bool = True
    rate_limiting: bool = True
    ip_whitelisting: bool = False
    allowed_ips: List[str] = None
    max_notifications_per_minute: int = 60
    require_authentication: bool = True

class NotificationSecurityManager:
    """Manages security and compliance for notifications"""
    
    def __init__(self, policy: SecurityPolicy = None):
        self.policy = policy or SecurityPolicy()
        self.audit_logger = self._setup_audit_logging()
        self.encryption_key = self._generate_encryption_key()
        self.pii_patterns = self._load_pii_patterns()
        self.content_filters = self._load_content_filters()
        self.rate_limiter = {}
        self.access_tokens = {}
        
    def _setup_audit_logging(self) -> logging.Logger:
        """Setup audit logging"""
        logger = logging.getLogger('notification_audit')
        logger.setLevel(logging.INFO)
        
        # Create file handler for audit logs
        handler = logging.FileHandler('notification_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key"""
        return secrets.token_bytes(32)
    
    def _load_pii_patterns(self) -> List[re.Pattern]:
        """Load PII detection patterns"""
        patterns = [
            # Email addresses
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            # Phone numbers
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            # Credit card numbers (simplified)
            re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            # Social security numbers (US format)
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            # IP addresses
            re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
        ]
        return patterns
    
    def _load_content_filters(self) -> List[str]:
        """Load content filtering keywords"""
        return [
            'password', 'secret', 'token', 'key', 'credential',
            'confidential', 'private', 'restricted', 'classified'
        ]
    
    def validate_notification(self, notification: Dict[str, Any], 
                            user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate notification for security and compliance"""
        validation_result = {
            'valid': True,
            'security_level': SecurityLevel.PUBLIC,
            'compliance_issues': [],
            'security_warnings': [],
            'sanitized_content': notification.copy(),
            'audit_required': False
        }
        
        try:
            # Check authentication if required
            if self.policy.require_authentication and not user_context:
                validation_result['valid'] = False
                validation_result['security_warnings'].append("Authentication required")
                return validation_result
            
            # Rate limiting check
            if self.policy.rate_limiting:
                if not self._check_rate_limit(user_context):
                    validation_result['valid'] = False
                    validation_result['security_warnings'].append("Rate limit exceeded")
                    return validation_result
            
            # IP whitelisting check
            if self.policy.ip_whitelisting:
                if not self._check_ip_whitelist(user_context):
                    validation_result['valid'] = False
                    validation_result['security_warnings'].append("IP not whitelisted")
                    return validation_result
            
            # PII detection
            if self.policy.pii_detection:
                pii_found = self._detect_pii(notification)
                if pii_found:
                    validation_result['security_level'] = SecurityLevel.CONFIDENTIAL
                    validation_result['security_warnings'].extend(pii_found)
                    validation_result['audit_required'] = True
            
            # Content filtering
            if self.policy.content_filtering:
                filtered_content = self._filter_content(notification)
                validation_result['sanitized_content'] = filtered_content
                
                if filtered_content != notification:
                    validation_result['security_warnings'].append("Content filtered")
                    validation_result['audit_required'] = True
            
            # Determine security level
            validation_result['security_level'] = self._determine_security_level(notification)
            
            # Check compliance requirements
            compliance_issues = self._check_compliance(notification, validation_result['security_level'])
            validation_result['compliance_issues'] = compliance_issues
            
            if compliance_issues:
                validation_result['audit_required'] = True
            
            # Audit logging
            if self.policy.audit_logging and validation_result['audit_required']:
                self._log_audit_event(notification, validation_result, user_context)
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['security_warnings'].append(f"Validation error: {str(e)}")
            self.audit_logger.error(f"Validation error: {e}")
        
        return validation_result
    
    def _check_rate_limit(self, user_context: Dict[str, Any]) -> bool:
        """Check rate limiting"""
        if not user_context:
            return False
        
        user_id = user_context.get('user_id', 'anonymous')
        current_time = datetime.now()
        minute_key = current_time.strftime('%Y-%m-%d-%H-%M')
        
        rate_key = f"{user_id}_{minute_key}"
        
        if rate_key not in self.rate_limiter:
            self.rate_limiter[rate_key] = 0
        
        self.rate_limiter[rate_key] += 1
        
        # Cleanup old entries
        self._cleanup_rate_limiter()
        
        return self.rate_limiter[rate_key] <= self.policy.max_notifications_per_minute
    
    def _cleanup_rate_limiter(self):
        """Cleanup old rate limiter entries"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=2)
        
        keys_to_remove = []
        for key in self.rate_limiter:
            try:
                key_time = datetime.strptime(key.split('_', 1)[1], '%Y-%m-%d-%H-%M')
                if key_time < cutoff_time:
                    keys_to_remove.append(key)
            except:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.rate_limiter[key]
    
    def _check_ip_whitelist(self, user_context: Dict[str, Any]) -> bool:
        """Check IP whitelisting"""
        if not self.policy.allowed_ips:
            return True
        
        user_ip = user_context.get('ip_address')
        if not user_ip:
            return False
        
        return user_ip in self.policy.allowed_ips
    
    def _detect_pii(self, notification: Dict[str, Any]) -> List[str]:
        """Detect personally identifiable information"""
        pii_found = []
        
        # Check title and message
        text_fields = [
            notification.get('title', ''),
            notification.get('message', '')
        ]
        
        for text in text_fields:
            for pattern in self.pii_patterns:
                if pattern.search(text):
                    pii_found.append(f"PII detected: {pattern.pattern}")
        
        return pii_found
    
    def _filter_content(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive content"""
        filtered = notification.copy()
        
        # Filter title and message
        for field in ['title', 'message']:
            if field in filtered:
                original_text = filtered[field]
                filtered_text = original_text
                
                # Replace sensitive keywords
                for keyword in self.content_filters:
                    if keyword.lower() in filtered_text.lower():
                        filtered_text = re.sub(
                            re.escape(keyword), 
                            '*' * len(keyword), 
                            filtered_text, 
                            flags=re.IGNORECASE
                        )
                
                # Mask PII
                for pattern in self.pii_patterns:
                    filtered_text = pattern.sub('[REDACTED]', filtered_text)
                
                filtered[field] = filtered_text
        
        return filtered
    
    def _determine_security_level(self, notification: Dict[str, Any]) -> SecurityLevel:
        """Determine security level based on content"""
        category = notification.get('category', '').lower()
        priority = notification.get('priority', 10)
        
        # High priority or security-related categories
        if priority <= 3 or category in ['security', 'emergency', 'critical']:
            return SecurityLevel.RESTRICTED
        
        # Financial or sensitive categories
        if category in ['budget', 'financial', 'staff']:
            return SecurityLevel.CONFIDENTIAL
        
        # Internal operations
        if category in ['maintenance', 'inventory', 'schedule']:
            return SecurityLevel.INTERNAL
        
        return SecurityLevel.PUBLIC
    
    def _check_compliance(self, notification: Dict[str, Any], 
                         security_level: SecurityLevel) -> List[str]:
        """Check compliance requirements"""
        issues = []
        
        # GDPR compliance
        if self._has_personal_data(notification):
            issues.append("GDPR: Personal data detected - consent and retention policies apply")
        
        # Data retention
        if security_level in [SecurityLevel.CONFIDENTIAL, SecurityLevel.RESTRICTED]:
            issues.append(f"Data retention: Must be deleted after {self.policy.data_retention_days} days")
        
        # Encryption requirement
        if self.policy.encryption_required and security_level != SecurityLevel.PUBLIC:
            issues.append("Encryption required for non-public notifications")
        
        return issues
    
    def _has_personal_data(self, notification: Dict[str, Any]) -> bool:
        """Check if notification contains personal data"""
        text_content = f"{notification.get('title', '')} {notification.get('message', '')}"
        
        # Simple check for personal data indicators
        personal_indicators = ['name', 'email', 'phone', 'address', 'employee', 'customer']
        
        return any(indicator in text_content.lower() for indicator in personal_indicators)
    
    def _log_audit_event(self, notification: Dict[str, Any], 
                        validation_result: Dict[str, Any],
                        user_context: Dict[str, Any] = None):
        """Log audit event"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'notification_validation',
            'notification_id': notification.get('id', 'unknown'),
            'user_id': user_context.get('user_id', 'anonymous') if user_context else 'system',
            'ip_address': user_context.get('ip_address', 'unknown') if user_context else 'local',
            'security_level': validation_result['security_level'].value,
            'validation_result': validation_result['valid'],
            'security_warnings': validation_result['security_warnings'],
            'compliance_issues': validation_result['compliance_issues'],
            'notification_category': notification.get('category', 'unknown'),
            'notification_priority': notification.get('priority', 10)
        }
        
        self.audit_logger.info(json.dumps(audit_entry))
    
    def encrypt_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive notification data"""
        if not self.policy.encryption_required:
            return notification
        
        try:
            # Simple encryption simulation (in production, use proper encryption)
            encrypted = notification.copy()
            
            for field in ['title', 'message']:
                if field in encrypted:
                    # In production, use proper encryption like AES
                    encrypted_data = hashlib.sha256(
                        (encrypted[field] + str(self.encryption_key)).encode()
                    ).hexdigest()
                    encrypted[f"{field}_encrypted"] = encrypted_data
                    encrypted[f"{field}_original_length"] = len(encrypted[field])
                    encrypted[field] = "[ENCRYPTED]"
            
            encrypted['encrypted'] = True
            return encrypted
            
        except Exception as e:
            self.audit_logger.error(f"Encryption error: {e}")
            return notification
    
    def generate_compliance_report(self, start_date: datetime, 
                                 end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report"""
        report = {
            'report_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_notifications': 0,
            'security_levels': {level.value: 0 for level in SecurityLevel},
            'compliance_violations': 0,
            'pii_detections': 0,
            'rate_limit_violations': 0,
            'encryption_usage': 0,
            'recommendations': []
        }
        
        # In production, this would analyze actual audit logs
        # For now, provide a template structure
        
        report['recommendations'] = [
            "Implement regular security training for users",
            "Review and update PII detection patterns quarterly",
            "Consider implementing data loss prevention (DLP) tools",
            "Establish regular compliance audits",
            "Update security policies based on regulatory changes"
        ]
        
        return report

def create_security_demo():
    """Demonstrate security and compliance features"""
    print("🔒 Notification Security & Compliance Demo")
    print("=" * 50)
    
    # Create security manager with strict policy
    policy = SecurityPolicy(
        encryption_required=True,
        audit_logging=True,
        pii_detection=True,
        content_filtering=True,
        rate_limiting=True,
        max_notifications_per_minute=5
    )
    
    security_manager = NotificationSecurityManager(policy)
    
    # Test notifications with various security concerns
    test_notifications = [
        {
            'id': 'test_1',
            'title': 'System Alert',
            'message': 'Normal system notification',
            'category': 'info',
            'priority': 10
        },
        {
            'id': 'test_2',
            'title': 'Security Breach',
            'message': 'Unauthorized access detected from IP 192.168.1.100',
            'category': 'security',
            'priority': 1
        },
        {
            'id': 'test_3',
            'title': 'Employee Data',
            'message': 'Employee john.doe@company.com phone 555-123-4567 needs attention',
            'category': 'staff',
            'priority': 5
        },
        {
            'id': 'test_4',
            'title': 'Password Reset',
            'message': 'Password reset token: abc123secret456',
            'category': 'system',
            'priority': 8
        }
    ]
    
    user_context = {
        'user_id': 'demo_user',
        'ip_address': '192.168.1.50',
        'role': 'admin'
    }
    
    print("🧪 Testing notifications for security compliance:")
    
    for notification in test_notifications:
        print(f"\n📋 Testing: {notification['title']}")
        
        validation = security_manager.validate_notification(notification, user_context)
        
        print(f"   ✅ Valid: {validation['valid']}")
        print(f"   🔒 Security Level: {validation['security_level'].value}")
        
        if validation['security_warnings']:
            print(f"   ⚠️ Warnings: {', '.join(validation['security_warnings'])}")
        
        if validation['compliance_issues']:
            print(f"   📋 Compliance: {', '.join(validation['compliance_issues'])}")
        
        if validation['audit_required']:
            print(f"   📝 Audit: Required")
        
        # Test encryption
        if validation['security_level'] != SecurityLevel.PUBLIC:
            encrypted = security_manager.encrypt_notification(notification)
            print(f"   🔐 Encrypted: {encrypted.get('encrypted', False)}")
    
    # Generate compliance report
    print(f"\n📊 Generating compliance report...")
    report = security_manager.generate_compliance_report(
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    
    print(f"📋 Compliance Report Summary:")
    print(f"   • Report Period: {report['report_period']['start'][:10]} to {report['report_period']['end'][:10]}")
    print(f"   • Security Levels: {len(report['security_levels'])} levels tracked")
    print(f"   • Recommendations: {len(report['recommendations'])} items")
    
    print(f"\n✅ Security and compliance demo completed!")
    return security_manager

class NotificationDeliverySystem:
    """Advanced notification delivery with multiple channels"""

    def __init__(self, security_manager: NotificationSecurityManager):
        self.security_manager = security_manager
        self.delivery_channels = {
            'gui': self._deliver_gui,
            'email': self._deliver_email,
            'sms': self._deliver_sms,
            'webhook': self._deliver_webhook,
            'push': self._deliver_push,
            'slack': self._deliver_slack
        }
        self.delivery_rules = []
        self.delivery_stats = {
            'total_sent': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'channel_stats': {channel: 0 for channel in self.delivery_channels}
        }

    def add_delivery_rule(self, condition: Dict[str, Any], channels: List[str], priority: int = 10):
        """Add delivery rule"""
        rule = {
            'condition': condition,
            'channels': channels,
            'priority': priority,
            'created_at': datetime.now().isoformat()
        }
        self.delivery_rules.append(rule)
        self.delivery_rules.sort(key=lambda x: x['priority'])

    def deliver_notification(self, notification: Dict[str, Any],
                           user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Deliver notification through appropriate channels"""
        delivery_result = {
            'notification_id': notification.get('id', 'unknown'),
            'channels_attempted': [],
            'successful_channels': [],
            'failed_channels': [],
            'delivery_time': datetime.now().isoformat(),
            'total_recipients': 0
        }

        try:
            # Validate notification security
            validation = self.security_manager.validate_notification(notification, user_context)

            if not validation['valid']:
                delivery_result['error'] = 'Security validation failed'
                return delivery_result

            # Use sanitized content
            safe_notification = validation['sanitized_content']

            # Determine delivery channels based on rules
            channels = self._determine_channels(safe_notification, user_context)

            # Deliver to each channel
            for channel in channels:
                delivery_result['channels_attempted'].append(channel)

                try:
                    if channel in self.delivery_channels:
                        success = self.delivery_channels[channel](safe_notification, user_context)

                        if success:
                            delivery_result['successful_channels'].append(channel)
                            self.delivery_stats['successful_deliveries'] += 1
                        else:
                            delivery_result['failed_channels'].append(channel)
                            self.delivery_stats['failed_deliveries'] += 1

                        self.delivery_stats['channel_stats'][channel] += 1

                except Exception as e:
                    delivery_result['failed_channels'].append(f"{channel}: {str(e)}")
                    self.delivery_stats['failed_deliveries'] += 1

            self.delivery_stats['total_sent'] += 1

        except Exception as e:
            delivery_result['error'] = str(e)

        return delivery_result

    def _determine_channels(self, notification: Dict[str, Any],
                          user_context: Dict[str, Any] = None) -> List[str]:
        """Determine delivery channels based on rules"""
        channels = ['gui']  # Default channel

        category = notification.get('category', '')
        priority = notification.get('priority', 10)

        # Apply delivery rules
        for rule in self.delivery_rules:
            condition = rule['condition']

            if self._matches_condition(notification, condition, user_context):
                channels.extend(rule['channels'])

        # Remove duplicates while preserving order
        return list(dict.fromkeys(channels))

    def _matches_condition(self, notification: Dict[str, Any],
                          condition: Dict[str, Any],
                          user_context: Dict[str, Any] = None) -> bool:
        """Check if notification matches delivery condition"""
        # Category matching
        if 'category' in condition:
            if notification.get('category') not in condition['category']:
                return False

        # Priority matching
        if 'priority_max' in condition:
            if notification.get('priority', 10) > condition['priority_max']:
                return False

        # Time-based conditions
        if 'time_range' in condition:
            current_hour = datetime.now().hour
            start_hour, end_hour = condition['time_range']
            if not (start_hour <= current_hour <= end_hour):
                return False

        # User-based conditions
        if user_context and 'user_role' in condition:
            if user_context.get('role') not in condition['user_role']:
                return False

        return True

    def _deliver_gui(self, notification: Dict[str, Any],
                    user_context: Dict[str, Any] = None) -> bool:
        """Deliver to GUI (default implementation)"""
        try:
            # This would integrate with the existing GUI notification system
            print(f"📱 GUI: {notification['title']}")
            return True
        except Exception as e:
            print(f"❌ GUI delivery failed: {e}")
            return False

    def _deliver_email(self, notification: Dict[str, Any],
                      user_context: Dict[str, Any] = None) -> bool:
        """Deliver via email"""
        try:
            # Email delivery implementation would go here
            print(f"📧 EMAIL: {notification['title']}")
            return True
        except Exception as e:
            print(f"❌ Email delivery failed: {e}")
            return False

    def _deliver_sms(self, notification: Dict[str, Any],
                    user_context: Dict[str, Any] = None) -> bool:
        """Deliver via SMS"""
        try:
            # SMS delivery implementation would go here
            print(f"📱 SMS: {notification['title']}")
            return True
        except Exception as e:
            print(f"❌ SMS delivery failed: {e}")
            return False

    def _deliver_webhook(self, notification: Dict[str, Any],
                        user_context: Dict[str, Any] = None) -> bool:
        """Deliver via webhook"""
        try:
            # Webhook delivery implementation would go here
            print(f"🔗 WEBHOOK: {notification['title']}")
            return True
        except Exception as e:
            print(f"❌ Webhook delivery failed: {e}")
            return False

    def _deliver_push(self, notification: Dict[str, Any],
                     user_context: Dict[str, Any] = None) -> bool:
        """Deliver via push notification"""
        try:
            # Push notification implementation would go here
            print(f"📲 PUSH: {notification['title']}")
            return True
        except Exception as e:
            print(f"❌ Push delivery failed: {e}")
            return False

    def _deliver_slack(self, notification: Dict[str, Any],
                      user_context: Dict[str, Any] = None) -> bool:
        """Deliver via Slack"""
        try:
            # Slack delivery implementation would go here
            print(f"💬 SLACK: {notification['title']}")
            return True
        except Exception as e:
            print(f"❌ Slack delivery failed: {e}")
            return False

    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        total_attempts = self.delivery_stats['successful_deliveries'] + self.delivery_stats['failed_deliveries']
        success_rate = (self.delivery_stats['successful_deliveries'] / max(total_attempts, 1)) * 100

        return {
            'total_notifications_sent': self.delivery_stats['total_sent'],
            'total_delivery_attempts': total_attempts,
            'successful_deliveries': self.delivery_stats['successful_deliveries'],
            'failed_deliveries': self.delivery_stats['failed_deliveries'],
            'success_rate_percent': round(success_rate, 2),
            'channel_statistics': self.delivery_stats['channel_stats'].copy()
        }

def create_delivery_demo():
    """Demonstrate advanced delivery system"""
    print("🚀 Advanced Notification Delivery Demo")
    print("=" * 50)

    # Create security manager and delivery system
    security_manager = NotificationSecurityManager()
    delivery_system = NotificationDeliverySystem(security_manager)

    # Add delivery rules
    delivery_system.add_delivery_rule(
        condition={'category': ['emergency', 'critical'], 'priority_max': 3},
        channels=['gui', 'email', 'sms', 'push'],
        priority=1
    )

    delivery_system.add_delivery_rule(
        condition={'category': ['security'], 'user_role': ['admin', 'security']},
        channels=['gui', 'email', 'slack'],
        priority=2
    )

    delivery_system.add_delivery_rule(
        condition={'time_range': (22, 6)},  # Night hours
        channels=['gui', 'push'],
        priority=5
    )

    # Test notifications
    test_notifications = [
        {
            'id': 'delivery_test_1',
            'title': 'Critical System Failure',
            'message': 'Database server is down',
            'category': 'critical',
            'priority': 1
        },
        {
            'id': 'delivery_test_2',
            'title': 'Security Alert',
            'message': 'Suspicious login detected',
            'category': 'security',
            'priority': 3
        },
        {
            'id': 'delivery_test_3',
            'title': 'Daily Report',
            'message': 'Daily operations summary',
            'category': 'info',
            'priority': 12
        }
    ]

    user_contexts = [
        {'user_id': 'admin_user', 'role': 'admin'},
        {'user_id': 'security_user', 'role': 'security'},
        {'user_id': 'regular_user', 'role': 'user'}
    ]

    print("📤 Testing multi-channel delivery:")

    for notification in test_notifications:
        print(f"\n📋 Delivering: {notification['title']}")

        for user_context in user_contexts:
            result = delivery_system.deliver_notification(notification, user_context)

            print(f"   👤 User: {user_context['role']}")
            print(f"      📡 Channels: {', '.join(result['successful_channels'])}")

            if result['failed_channels']:
                print(f"      ❌ Failed: {', '.join(result['failed_channels'])}")

    # Show delivery statistics
    stats = delivery_system.get_delivery_stats()
    print(f"\n📊 Delivery Statistics:")
    print(f"   • Total Notifications: {stats['total_notifications_sent']}")
    print(f"   • Success Rate: {stats['success_rate_percent']}%")
    print(f"   • Channel Usage:")

    for channel, count in stats['channel_statistics'].items():
        if count > 0:
            print(f"     - {channel.upper()}: {count} deliveries")

    print(f"\n✅ Advanced delivery demo completed!")
    return delivery_system

if __name__ == "__main__":
    create_security_demo()
    print("\n" + "=" * 50)
    create_delivery_demo()
