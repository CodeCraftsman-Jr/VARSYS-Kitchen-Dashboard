#!/usr/bin/env python3
"""
Mobile and Cross-Platform Notification Integration
Advanced mobile push notifications and cross-platform synchronization
"""

import sys
import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
import hashlib

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.enhanced_notification_system import get_notification_manager

class MobilePlatform(Enum):
    """Supported mobile platforms"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    DESKTOP = "desktop"
    TABLET = "tablet"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"

@dataclass
class MobileDevice:
    """Mobile device registration"""
    device_id: str
    user_id: str
    platform: MobilePlatform
    push_token: str
    app_version: str
    os_version: str
    device_model: str
    timezone: str
    language: str
    registered_at: datetime
    last_active: datetime
    notification_settings: Dict[str, Any]
    is_active: bool = True

@dataclass
class CrossPlatformMessage:
    """Cross-platform notification message"""
    message_id: str
    title: str
    body: str
    category: str
    priority: int
    data: Dict[str, Any]
    target_platforms: List[MobilePlatform]
    channels: List[NotificationChannel]
    created_at: datetime
    expires_at: Optional[datetime] = None
    delivery_status: Dict[str, str] = None

class MobileNotificationManager:
    """Manages mobile and cross-platform notifications"""
    
    def __init__(self):
        self.devices: Dict[str, MobileDevice] = {}
        self.notification_manager = get_notification_manager()
        self.delivery_stats = {
            'total_sent': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'platform_stats': {platform.value: 0 for platform in MobilePlatform},
            'channel_stats': {channel.value: 0 for channel in NotificationChannel}
        }
        self.message_history: List[CrossPlatformMessage] = []
        
        # Platform-specific configurations
        self.platform_configs = {
            MobilePlatform.IOS: {
                'max_title_length': 50,
                'max_body_length': 200,
                'supports_rich_media': True,
                'supports_actions': True,
                'badge_support': True
            },
            MobilePlatform.ANDROID: {
                'max_title_length': 65,
                'max_body_length': 240,
                'supports_rich_media': True,
                'supports_actions': True,
                'badge_support': False
            },
            MobilePlatform.WEB: {
                'max_title_length': 100,
                'max_body_length': 300,
                'supports_rich_media': True,
                'supports_actions': True,
                'badge_support': True
            }
        }
        
        # Channel configurations
        self.channel_configs = {
            NotificationChannel.PUSH: {
                'max_retries': 3,
                'retry_delay': 300,  # 5 minutes
                'batch_size': 100
            },
            NotificationChannel.SMS: {
                'max_retries': 2,
                'retry_delay': 600,  # 10 minutes
                'max_length': 160
            },
            NotificationChannel.EMAIL: {
                'max_retries': 3,
                'retry_delay': 900,  # 15 minutes
                'supports_html': True
            }
        }
    
    def register_device(self, device: MobileDevice) -> bool:
        """Register a mobile device"""
        try:
            # Validate device data
            if not device.device_id or not device.user_id or not device.push_token:
                return False
            
            # Store device
            self.devices[device.device_id] = device
            
            print(f"📱 Device registered: {device.device_id} ({device.platform.value})")
            return True
            
        except Exception as e:
            print(f"❌ Device registration failed: {e}")
            return False
    
    def unregister_device(self, device_id: str) -> bool:
        """Unregister a mobile device"""
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.is_active = False
                print(f"📱 Device unregistered: {device_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Device unregistration failed: {e}")
            return False
    
    def send_cross_platform_notification(self, title: str, body: str, 
                                       category: str = "general",
                                       priority: int = 5,
                                       target_users: List[str] = None,
                                       target_platforms: List[MobilePlatform] = None,
                                       channels: List[NotificationChannel] = None,
                                       data: Dict[str, Any] = None) -> CrossPlatformMessage:
        """Send notification across multiple platforms"""
        
        # Create message
        message = CrossPlatformMessage(
            message_id=str(uuid.uuid4()),
            title=title,
            body=body,
            category=category,
            priority=priority,
            data=data or {},
            target_platforms=target_platforms or list(MobilePlatform),
            channels=channels or [NotificationChannel.PUSH, NotificationChannel.IN_APP],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            delivery_status={}
        )
        
        # Store message
        self.message_history.append(message)
        
        # Get target devices
        target_devices = self._get_target_devices(target_users, target_platforms)
        
        print(f"📤 Sending cross-platform notification to {len(target_devices)} devices")
        
        # Send to each device
        for device in target_devices:
            self._send_to_device(message, device)
        
        # Update stats
        self.delivery_stats['total_sent'] += 1
        
        return message
    
    def _get_target_devices(self, target_users: List[str] = None, 
                          target_platforms: List[MobilePlatform] = None) -> List[MobileDevice]:
        """Get devices matching target criteria"""
        devices = []
        
        for device in self.devices.values():
            if not device.is_active:
                continue
            
            # Filter by users
            if target_users and device.user_id not in target_users:
                continue
            
            # Filter by platforms
            if target_platforms and device.platform not in target_platforms:
                continue
            
            devices.append(device)
        
        return devices
    
    def _send_to_device(self, message: CrossPlatformMessage, device: MobileDevice):
        """Send message to a specific device"""
        try:
            # Adapt message for platform
            adapted_message = self._adapt_message_for_platform(message, device.platform)
            
            # Send through each channel
            for channel in message.channels:
                success = self._send_through_channel(adapted_message, device, channel)
                
                # Update delivery status
                status_key = f"{device.device_id}_{channel.value}"
                message.delivery_status[status_key] = "success" if success else "failed"
                
                # Update stats
                if success:
                    self.delivery_stats['successful_deliveries'] += 1
                else:
                    self.delivery_stats['failed_deliveries'] += 1
                
                self.delivery_stats['platform_stats'][device.platform.value] += 1
                self.delivery_stats['channel_stats'][channel.value] += 1
        
        except Exception as e:
            print(f"❌ Error sending to device {device.device_id}: {e}")
    
    def _adapt_message_for_platform(self, message: CrossPlatformMessage, 
                                   platform: MobilePlatform) -> Dict[str, Any]:
        """Adapt message for specific platform"""
        config = self.platform_configs.get(platform, {})
        
        # Truncate title and body if needed
        title = message.title
        body = message.body
        
        if 'max_title_length' in config:
            title = title[:config['max_title_length']]
        
        if 'max_body_length' in config:
            body = body[:config['max_body_length']]
        
        adapted = {
            'title': title,
            'body': body,
            'category': message.category,
            'priority': message.priority,
            'data': message.data.copy(),
            'platform_specific': {}
        }
        
        # Add platform-specific features
        if platform == MobilePlatform.IOS:
            adapted['platform_specific'] = {
                'badge': 1,
                'sound': 'default',
                'content_available': True
            }
        elif platform == MobilePlatform.ANDROID:
            adapted['platform_specific'] = {
                'icon': 'notification_icon',
                'color': '#2196F3',
                'channel_id': f"channel_{message.category}"
            }
        elif platform == MobilePlatform.WEB:
            adapted['platform_specific'] = {
                'icon': '/static/notification-icon.png',
                'badge': '/static/notification-badge.png',
                'vibrate': [200, 100, 200]
            }
        
        return adapted
    
    def _send_through_channel(self, message: Dict[str, Any], 
                            device: MobileDevice, 
                            channel: NotificationChannel) -> bool:
        """Send message through specific channel"""
        try:
            if channel == NotificationChannel.PUSH:
                return self._send_push_notification(message, device)
            elif channel == NotificationChannel.SMS:
                return self._send_sms_notification(message, device)
            elif channel == NotificationChannel.EMAIL:
                return self._send_email_notification(message, device)
            elif channel == NotificationChannel.IN_APP:
                return self._send_in_app_notification(message, device)
            elif channel == NotificationChannel.WEBHOOK:
                return self._send_webhook_notification(message, device)
            else:
                print(f"⚠️ Unsupported channel: {channel.value}")
                return False
                
        except Exception as e:
            print(f"❌ Channel {channel.value} error: {e}")
            return False
    
    def _send_push_notification(self, message: Dict[str, Any], device: MobileDevice) -> bool:
        """Send push notification (simulated)"""
        print(f"📲 PUSH to {device.platform.value}: {message['title']}")
        
        # In production, this would integrate with:
        # - Apple Push Notification Service (APNs) for iOS
        # - Firebase Cloud Messaging (FCM) for Android
        # - Web Push Protocol for web browsers
        
        # Simulate delivery
        time.sleep(0.1)  # Simulate network delay
        return True
    
    def _send_sms_notification(self, message: Dict[str, Any], device: MobileDevice) -> bool:
        """Send SMS notification (simulated)"""
        print(f"📱 SMS to {device.user_id}: {message['title']}")
        
        # In production, this would integrate with SMS providers like:
        # - Twilio, AWS SNS, Azure Communication Services
        
        time.sleep(0.1)
        return True
    
    def _send_email_notification(self, message: Dict[str, Any], device: MobileDevice) -> bool:
        """Send email notification (simulated)"""
        print(f"📧 EMAIL to {device.user_id}: {message['title']}")
        
        # In production, this would integrate with email services like:
        # - SendGrid, AWS SES, Azure Communication Services
        
        time.sleep(0.1)
        return True
    
    def _send_in_app_notification(self, message: Dict[str, Any], device: MobileDevice) -> bool:
        """Send in-app notification"""
        print(f"📱 IN-APP to {device.device_id}: {message['title']}")
        
        # Send through the core notification system
        return self.notification_manager.notify(
            title=message['title'],
            message=message['body'],
            category=message['category'],
            priority=message['priority'],
            source="Mobile Integration",
            show_toast=True,
            show_bell=True
        )
    
    def _send_webhook_notification(self, message: Dict[str, Any], device: MobileDevice) -> bool:
        """Send webhook notification (simulated)"""
        print(f"🔗 WEBHOOK to {device.user_id}: {message['title']}")
        
        # In production, this would send HTTP POST to configured webhooks
        
        time.sleep(0.1)
        return True
    
    def get_device_statistics(self) -> Dict[str, Any]:
        """Get device and delivery statistics"""
        active_devices = sum(1 for device in self.devices.values() if device.is_active)
        
        platform_breakdown = {}
        for platform in MobilePlatform:
            count = sum(1 for device in self.devices.values() 
                       if device.is_active and device.platform == platform)
            platform_breakdown[platform.value] = count
        
        return {
            'total_devices': len(self.devices),
            'active_devices': active_devices,
            'platform_breakdown': platform_breakdown,
            'delivery_stats': self.delivery_stats.copy(),
            'recent_messages': len([m for m in self.message_history 
                                  if m.created_at > datetime.now() - timedelta(hours=24)])
        }
    
    def sync_notifications_for_user(self, user_id: str) -> Dict[str, Any]:
        """Sync notifications across all user devices"""
        user_devices = [device for device in self.devices.values() 
                       if device.user_id == user_id and device.is_active]
        
        if not user_devices:
            return {'synced': False, 'reason': 'No active devices found'}
        
        # Get recent notifications from core system
        notifications = self.notification_manager.get_notifications()
        recent_notifications = notifications[-20:]  # Last 20 notifications
        
        sync_message = CrossPlatformMessage(
            message_id=str(uuid.uuid4()),
            title="Notification Sync",
            body=f"Syncing {len(recent_notifications)} notifications",
            category="sync",
            priority=15,
            data={'notifications': recent_notifications},
            target_platforms=[device.platform for device in user_devices],
            channels=[NotificationChannel.IN_APP],
            created_at=datetime.now()
        )
        
        # Send sync to all user devices
        for device in user_devices:
            self._send_to_device(sync_message, device)
        
        return {
            'synced': True,
            'devices_synced': len(user_devices),
            'notifications_synced': len(recent_notifications)
        }

def create_mobile_demo():
    """Create mobile integration demo"""
    print("📱 Mobile and Cross-Platform Notification Demo")
    print("=" * 60)
    
    mobile_manager = MobileNotificationManager()
    
    # Register sample devices
    sample_devices = [
        MobileDevice(
            device_id="ios_device_001",
            user_id="user_alice",
            platform=MobilePlatform.IOS,
            push_token="ios_token_abc123",
            app_version="1.2.0",
            os_version="iOS 17.0",
            device_model="iPhone 14 Pro",
            timezone="America/New_York",
            language="en",
            registered_at=datetime.now(),
            last_active=datetime.now(),
            notification_settings={'push': True, 'email': True, 'sms': False}
        ),
        MobileDevice(
            device_id="android_device_002",
            user_id="user_bob",
            platform=MobilePlatform.ANDROID,
            push_token="android_token_def456",
            app_version="1.2.0",
            os_version="Android 14",
            device_model="Samsung Galaxy S24",
            timezone="Europe/London",
            language="en",
            registered_at=datetime.now(),
            last_active=datetime.now(),
            notification_settings={'push': True, 'email': True, 'sms': True}
        ),
        MobileDevice(
            device_id="web_device_003",
            user_id="user_alice",
            platform=MobilePlatform.WEB,
            push_token="web_token_ghi789",
            app_version="1.2.0",
            os_version="Chrome 120",
            device_model="Desktop",
            timezone="America/New_York",
            language="en",
            registered_at=datetime.now(),
            last_active=datetime.now(),
            notification_settings={'push': True, 'email': False, 'sms': False}
        )
    ]
    
    print(f"📱 Registering {len(sample_devices)} sample devices:")
    
    for device in sample_devices:
        success = mobile_manager.register_device(device)
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {status}: {device.device_id} ({device.platform.value})")
    
    # Test cross-platform notifications
    test_notifications = [
        {
            'title': 'Kitchen Alert',
            'body': 'Oven temperature has exceeded safe limits',
            'category': 'safety',
            'priority': 2,
            'channels': [NotificationChannel.PUSH, NotificationChannel.SMS, NotificationChannel.IN_APP]
        },
        {
            'title': 'Order Ready',
            'body': 'Order #1234 is ready for pickup',
            'category': 'order',
            'priority': 8,
            'channels': [NotificationChannel.PUSH, NotificationChannel.IN_APP]
        },
        {
            'title': 'Inventory Low',
            'body': 'Tomatoes are running low (5 units remaining)',
            'category': 'inventory',
            'priority': 6,
            'channels': [NotificationChannel.PUSH, NotificationChannel.EMAIL, NotificationChannel.IN_APP]
        }
    ]
    
    print(f"\n📤 Sending {len(test_notifications)} cross-platform notifications:")
    
    for i, notification in enumerate(test_notifications, 1):
        print(f"\n{i}. Sending: {notification['title']}")
        
        message = mobile_manager.send_cross_platform_notification(**notification)
        
        print(f"   📨 Message ID: {message.message_id}")
        print(f"   🎯 Platforms: {len(message.target_platforms)}")
        print(f"   📡 Channels: {len(message.channels)}")
        print(f"   📊 Delivery Status: {len(message.delivery_status)} attempts")
    
    # Test user sync
    print(f"\n🔄 Testing notification sync for user_alice:")
    sync_result = mobile_manager.sync_notifications_for_user("user_alice")
    
    if sync_result['synced']:
        print(f"   ✅ Sync successful")
        print(f"   📱 Devices synced: {sync_result['devices_synced']}")
        print(f"   📨 Notifications synced: {sync_result['notifications_synced']}")
    else:
        print(f"   ❌ Sync failed: {sync_result['reason']}")
    
    # Show statistics
    stats = mobile_manager.get_device_statistics()
    
    print(f"\n📊 Mobile Integration Statistics:")
    print(f"   📱 Total Devices: {stats['total_devices']}")
    print(f"   ✅ Active Devices: {stats['active_devices']}")
    print(f"   📤 Messages Sent: {stats['delivery_stats']['total_sent']}")
    print(f"   ✅ Successful Deliveries: {stats['delivery_stats']['successful_deliveries']}")
    print(f"   ❌ Failed Deliveries: {stats['delivery_stats']['failed_deliveries']}")
    
    print(f"\n📱 Platform Breakdown:")
    for platform, count in stats['platform_breakdown'].items():
        if count > 0:
            print(f"   • {platform.upper()}: {count} devices")
    
    print(f"\n📡 Channel Usage:")
    for channel, count in stats['delivery_stats']['channel_stats'].items():
        if count > 0:
            print(f"   • {channel.upper()}: {count} deliveries")
    
    print(f"\n✅ Mobile integration demo completed!")
    print(f"📱 Features: Cross-platform delivery, device management, sync")
    print(f"🔄 Capabilities: Multi-channel, platform adaptation, real-time sync")
    
    return mobile_manager

if __name__ == "__main__":
    create_mobile_demo()
