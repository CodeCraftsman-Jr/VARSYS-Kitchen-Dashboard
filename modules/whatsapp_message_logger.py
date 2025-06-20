"""
WhatsApp Message Logger System
Handles structured logging of WhatsApp messages to a shared JSON file for standalone messaging system
"""

import os
import sys
import json
import time
import uuid
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Import file locking modules based on platform
try:
    import fcntl
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False

try:
    import msvcrt
    MSVCRT_AVAILABLE = True
except ImportError:
    MSVCRT_AVAILABLE = False

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import logger
from utils.app_logger import get_logger

class WhatsAppMessageLogger:
    """Structured logging system for WhatsApp messages"""
    
    def __init__(self, data=None, main_app=None):
        self.data = data or {}
        self.main_app = main_app
        self.logger = get_logger()
        
        # Configuration
        self.messages_file = "whatsapp_messages.json"
        self.config_file = "whatsapp_config.json"
        
        # Message settings
        self.notification_settings = {
            'low_stock_enabled': True,
            'cleaning_reminders_enabled': True,
            'packing_materials_enabled': True,
            'gas_level_warnings_enabled': True,
            'last_notification_times': {}  # Track when notifications were last sent
        }
        
        # Load configuration
        self.load_config()
        
        # Initialize message file
        self.initialize_message_file()
        
        self.logger.info("WhatsApp Message Logger initialized for standalone messaging system")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.notification_settings.update(config.get('notification_settings', {}))
                    self.logger.info("WhatsApp message logger configuration loaded")
            else:
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading WhatsApp message logger config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'notification_settings': self.notification_settings,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving WhatsApp message logger config: {e}")
    
    def initialize_message_file(self):
        """Initialize the shared message file if it doesn't exist"""
        try:
            if not os.path.exists(self.messages_file):
                initial_data = {
                    "messages": [],
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                }
                with open(self.messages_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
                self.logger.info("Initialized WhatsApp messages file")
        except Exception as e:
            self.logger.error(f"Error initializing WhatsApp messages file: {e}")
    
    def sanitize_message_content(self, content: str) -> str:
        """Sanitize message content for WhatsApp compatibility"""
        try:
            # Replace problematic Unicode characters
            sanitized = content.encode('ascii', 'ignore').decode('ascii')
            
            # Replace emojis with text equivalents
            emoji_replacements = {
                '🚨': '[URGENT]',
                '⚠️': '[WARNING]',
                '📦': '[PACKAGE]',
                '🔥': '[FIRE]',
                '⛽': '[GAS]',
                '🧹': '[CLEANING]',
                '📋': '[TASK]',
                '✅': '[DONE]',
                '❌': '[FAILED]',
                '📅': '[DATE]',
                '🛒': '[ORDER]'
            }
            
            for emoji, replacement in emoji_replacements.items():
                sanitized = sanitized.replace(emoji, replacement)
            
            return sanitized
        except Exception as e:
            self.logger.error(f"Error sanitizing message content: {e}")
            return content
    
    def log_whatsapp_message(self, message_type: str, content: str, priority: str = "MEDIUM", 
                           max_retries: int = 3) -> bool:
        """Log a WhatsApp message to the shared JSON file"""
        try:
            # Create message object
            message = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "message_type": message_type,
                "content": content,
                "sanitized_content": self.sanitize_message_content(content),
                "priority": priority,
                "sent_status": "pending",
                "retry_count": 0,
                "max_retries": max_retries,
                "created_by": "kitchen_app",
                "error_message": None
            }
            
            # Write to file with locking
            return self._write_message_to_file(message)
            
        except Exception as e:
            self.logger.error(f"Error logging WhatsApp message: {e}")
            return False
    
    def _write_message_to_file(self, message: Dict) -> bool:
        """Write message to file with proper file locking"""
        try:
            # Use file locking to prevent corruption
            with open(self.messages_file, 'r+', encoding='utf-8') as f:
                # Lock the file based on platform
                if sys.platform == 'win32' and MSVCRT_AVAILABLE:
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                elif FCNTL_AVAILABLE:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)

                try:
                    # Read current data
                    f.seek(0)
                    data = json.load(f)

                    # Add new message
                    data["messages"].append(message)
                    data["last_updated"] = datetime.now().isoformat()

                    # Write back to file
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=2, ensure_ascii=False)

                    self.logger.info(f"Logged WhatsApp message: {message['message_type']} - {message['priority']}")
                    return True

                finally:
                    # Unlock the file based on platform
                    if sys.platform == 'win32' and MSVCRT_AVAILABLE:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    elif FCNTL_AVAILABLE:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except Exception as e:
            self.logger.error(f"Error writing message to file: {e}")
            return False
    
    def _should_send_notification(self, notification_key: str, cooldown_hours: int = 1) -> bool:
        """Check if notification should be sent based on cooldown period"""
        try:
            last_sent = self.notification_settings['last_notification_times'].get(notification_key)
            if not last_sent:
                return True
            
            last_sent_time = datetime.fromisoformat(last_sent)
            cooldown_period = timedelta(hours=cooldown_hours)
            
            return datetime.now() - last_sent_time > cooldown_period
            
        except Exception as e:
            self.logger.error(f"Error checking notification cooldown: {e}")
            return True  # Default to allowing notification
    
    def _record_notification_sent(self, notification_key: str):
        """Record that a notification was sent"""
        try:
            self.notification_settings['last_notification_times'][notification_key] = datetime.now().isoformat()
            self.save_config()
        except Exception as e:
            self.logger.error(f"Error recording notification sent: {e}")
    
    def _get_current_quantity(self, item):
        """Calculate current quantity for inventory item"""
        try:
            # Get quantities from different columns
            opening_stock = float(item.get('opening_stock', 0))
            purchased_qty = float(item.get('purchased_qty', 0))
            used_qty = float(item.get('used_qty', 0))
            
            # Calculate current quantity
            current_qty = opening_stock + purchased_qty - used_qty
            return max(0, current_qty)  # Ensure non-negative
            
        except Exception as e:
            self.logger.error(f"Error calculating current quantity: {e}")
            return 0
    
    # Notification checking methods
    def check_inventory_notifications(self, item_name: str = None):
        """Check for low stock notifications and log messages"""
        try:
            if not self.notification_settings.get('low_stock_enabled', True):
                return
            
            if 'inventory' not in self.data or self.data['inventory'].empty:
                return
            
            inventory_df = self.data['inventory']
            
            # Check specific item or all items
            if item_name:
                items_to_check = inventory_df[inventory_df['item_name'] == item_name]
            else:
                items_to_check = inventory_df
            
            for _, item in items_to_check.iterrows():
                item_name_current = item.get('item_name', '')
                if not item_name_current:
                    continue
                
                # Calculate current quantity
                current_qty = self._get_current_quantity(item)
                reorder_level = float(item.get('reorder_level', 10))
                unit = item.get('unit', 'units')
                
                # Check if notification needed
                if current_qty <= reorder_level:
                    notification_key = f"low_stock_{item_name_current}"
                    
                    if self._should_send_notification(notification_key, cooldown_hours=2):
                        if current_qty <= 0:
                            # Out of stock - critical priority
                            message = f"OUT OF STOCK ALERT\n\n" \
                                     f"Item: {item_name_current}\n" \
                                     f"Status: COMPLETELY OUT OF STOCK\n" \
                                     f"Reorder Level: {reorder_level} {unit}\n\n" \
                                     f"URGENT: Please restock immediately!\n" \
                                     f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            
                            self.log_whatsapp_message("low_stock", message, "CRITICAL")
                        else:
                            # Low stock - high priority
                            message = f"LOW STOCK ALERT\n\n" \
                                     f"Item: {item_name_current}\n" \
                                     f"Current Stock: {current_qty} {unit}\n" \
                                     f"Reorder Level: {reorder_level} {unit}\n\n" \
                                     f"Please consider restocking soon.\n" \
                                     f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            
                            self.log_whatsapp_message("low_stock", message, "HIGH")
                        
                        self._record_notification_sent(notification_key)
                        
        except Exception as e:
            self.logger.error(f"Error checking inventory notifications: {e}")

    def check_cleaning_notifications(self):
        """Check for cleaning task reminders and log messages"""
        try:
            if not self.notification_settings.get('cleaning_reminders_enabled', True):
                return

            if 'cleaning_maintenance' not in self.data or self.data['cleaning_maintenance'].empty:
                return

            cleaning_df = self.data['cleaning_maintenance']
            today = datetime.now().date()

            # Find tasks due today
            due_tasks = []
            for _, task in cleaning_df.iterrows():
                try:
                    due_date_str = task.get('due_date', '')
                    if due_date_str:
                        if isinstance(due_date_str, str):
                            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        else:
                            due_date = due_date_str

                        if due_date <= today:
                            due_tasks.append({
                                'name': task.get('task_name', 'Unknown Task'),
                                'assigned_to': task.get('assigned_to', 'Unassigned'),
                                'location': task.get('location', 'Unknown Location'),
                                'due_date': due_date
                            })
                except Exception as e:
                    self.logger.error(f"Error parsing cleaning task date: {e}")
                    continue

            # Send notification if there are due tasks
            if due_tasks and self._should_send_notification("cleaning_reminder", cooldown_hours=12):
                task_list = "\n".join([f"- {task['name']} ({task['location']}) - {task['assigned_to']}"
                                     for task in due_tasks])

                message = f"CLEANING TASKS DUE TODAY\n\n" \
                         f"The following cleaning tasks are due:\n\n" \
                         f"{task_list}\n\n" \
                         f"Please ensure all tasks are completed today.\n" \
                         f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                self.log_whatsapp_message("cleaning_reminder", message, "MEDIUM")
                self._record_notification_sent("cleaning_reminder")

        except Exception as e:
            self.logger.error(f"Error checking cleaning notifications: {e}")

    def check_packing_notifications(self, material_name: str = None):
        """Check for packing material alerts and log messages"""
        try:
            if not self.notification_settings.get('packing_materials_enabled', True):
                return

            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                return

            packing_df = self.data['packing_materials']

            # Check specific material or all materials
            if material_name:
                materials_to_check = packing_df[packing_df['material_name'] == material_name]
            else:
                materials_to_check = packing_df

            for _, material in materials_to_check.iterrows():
                material_name_current = material.get('material_name', '')
                if not material_name_current:
                    continue

                current_stock = int(material.get('current_stock', 0))
                minimum_stock = int(material.get('minimum_stock', 0))
                unit = material.get('unit', 'pieces')

                # Check if notification needed
                if current_stock <= minimum_stock:
                    notification_key = f"packing_material_{material_name_current}"

                    if self._should_send_notification(notification_key, cooldown_hours=4):
                        if current_stock <= 0:
                            # Out of stock - critical priority
                            message = f"PACKING MATERIAL OUT OF STOCK\n\n" \
                                     f"Material: {material_name_current}\n" \
                                     f"Status: COMPLETELY OUT OF STOCK\n" \
                                     f"Minimum Required: {minimum_stock} {unit}\n\n" \
                                     f"URGENT: Cannot pack orders without this material!\n" \
                                     f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                            self.log_whatsapp_message("packing_materials", message, "CRITICAL")
                        else:
                            # Low stock - high priority
                            message = f"PACKING MATERIAL LOW STOCK\n\n" \
                                     f"Material: {material_name_current}\n" \
                                     f"Current Stock: {current_stock} {unit}\n" \
                                     f"Minimum Required: {minimum_stock} {unit}\n\n" \
                                     f"Please restock soon to avoid order delays!\n" \
                                     f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                            self.log_whatsapp_message("packing_materials", message, "HIGH")

                        self._record_notification_sent(notification_key)

        except Exception as e:
            self.logger.error(f"Error checking packing material notifications: {e}")

    def check_gas_notifications(self):
        """Check for gas level warnings and log messages"""
        try:
            if not self.notification_settings.get('gas_level_warnings_enabled', True):
                return

            if 'gas_tracking' not in self.data or self.data['gas_tracking'].empty:
                return

            gas_df = self.data['gas_tracking']

            # Get current active cylinder
            active_cylinders = gas_df[gas_df['status'] == 'Active']
            if active_cylinders.empty:
                return

            current_cylinder = active_cylinders.iloc[-1]
            days_remaining = current_cylinder.get('estimated_days_remaining', 0)
            cylinder_id = current_cylinder.get('cylinder_id', 'Unknown')

            # Check thresholds
            critical_threshold = 1  # 1 day
            warning_threshold = 3   # 3 days

            if days_remaining <= critical_threshold:
                if self._should_send_notification("gas_critical", cooldown_hours=6):
                    message = f"CRITICAL GAS ALERT\n\n" \
                             f"Cylinder ID: {cylinder_id}\n" \
                             f"Days Remaining: {days_remaining}\n\n" \
                             f"URGENT: Gas will run out very soon!\n" \
                             f"Order new cylinder IMMEDIATELY!\n" \
                             f"Kitchen operations may stop!\n\n" \
                             f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                    self.log_whatsapp_message("gas_warning", message, "CRITICAL")
                    self._record_notification_sent("gas_critical")

            elif days_remaining <= warning_threshold:
                if self._should_send_notification("gas_warning", cooldown_hours=12):
                    message = f"GAS LEVEL WARNING\n\n" \
                             f"Cylinder ID: {cylinder_id}\n" \
                             f"Days Remaining: {days_remaining}\n\n" \
                             f"Gas level is getting low.\n" \
                             f"Please arrange for new cylinder soon.\n\n" \
                             f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                    self.log_whatsapp_message("gas_warning", message, "HIGH")
                    self._record_notification_sent("gas_warning")

        except Exception as e:
            self.logger.error(f"Error checking gas level notifications: {e}")

    def check_all_notifications(self):
        """Check all notification types"""
        try:
            self.logger.info("Checking all WhatsApp notification types for message logging")
            self.check_inventory_notifications()
            self.check_cleaning_notifications()
            self.check_packing_notifications()
            self.check_gas_notifications()
        except Exception as e:
            self.logger.error(f"Error in check_all_notifications: {e}")

    def get_pending_messages_count(self) -> int:
        """Get count of pending messages"""
        try:
            if not os.path.exists(self.messages_file):
                return 0

            with open(self.messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pending_count = sum(1 for msg in data.get('messages', [])
                                  if msg.get('sent_status') == 'pending')
                return pending_count

        except Exception as e:
            self.logger.error(f"Error getting pending messages count: {e}")
            return 0

    def get_status(self) -> Dict:
        """Get current status of the message logger"""
        return {
            'messages_file': self.messages_file,
            'config_file': self.config_file,
            'pending_messages': self.get_pending_messages_count(),
            'settings': self.notification_settings,
            'last_updated': datetime.now().isoformat()
        }
