"""
WhatsApp Automated Notifications System
Handles automated notifications for various kitchen management scenarios
"""

import os
import sys
import pandas as pd
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from modules.whatsapp_integration import WhatsAppIntegrationWidget
    from notification_templates import notify_low_stock, notify_out_of_stock
    WHATSAPP_AVAILABLE = True
except ImportError as e:
    print(f"WhatsApp integration not available: {e}")
    WHATSAPP_AVAILABLE = False

class WhatsAppAutomatedNotifications:
    """Automated notification system for WhatsApp integration"""
    
    def __init__(self, data=None, whatsapp_widget=None, main_app=None):
        self.data = data or {}
        self.whatsapp_widget = whatsapp_widget
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Notification settings
        self.notification_settings = {
            'low_stock_enabled': True,
            'cleaning_reminders_enabled': True,
            'packing_materials_enabled': True,
            'gas_level_warnings_enabled': True,
            'check_interval_minutes': 30,  # Check every 30 minutes
            'last_notification_times': {}  # Track when notifications were last sent
        }
        
        # Monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Load settings
        self.load_settings()
        
    def load_settings(self):
        """Load notification settings from file"""
        try:
            settings_file = os.path.join('data', 'whatsapp_notification_settings.json')
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.notification_settings.update(saved_settings)
        except Exception as e:
            self.logger.warning(f"Could not load notification settings: {e}")
    
    def save_settings(self):
        """Save notification settings to file"""
        try:
            import json
            os.makedirs('data', exist_ok=True)
            settings_file = os.path.join('data', 'whatsapp_notification_settings.json')
            with open(settings_file, 'w') as f:
                json.dump(self.notification_settings, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Could not save notification settings: {e}")
    
    def start_monitoring(self):
        """Start the automated monitoring system"""
        if self.monitoring_active:
            self.logger.info("Monitoring already active")
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="WhatsAppNotificationMonitor"
        )
        self.monitoring_thread.start()
        self.logger.info("WhatsApp automated notifications monitoring started")
    
    def stop_monitoring(self):
        """Stop the automated monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("WhatsApp automated notifications monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check all notification types
                if self.notification_settings.get('low_stock_enabled', True):
                    self.check_low_stock_notifications()
                
                if self.notification_settings.get('cleaning_reminders_enabled', True):
                    self.check_cleaning_reminders()
                
                if self.notification_settings.get('packing_materials_enabled', True):
                    self.check_packing_materials_alerts()
                
                if self.notification_settings.get('gas_level_warnings_enabled', True):
                    self.check_gas_level_warnings()
                
                # Wait for next check
                check_interval = self.notification_settings.get('check_interval_minutes', 30)
                time.sleep(check_interval * 60)  # Convert to seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def check_low_stock_notifications(self):
        """Check for low stock items and send notifications"""
        try:
            if 'inventory' not in self.data or self.data['inventory'].empty:
                return
            
            inventory_df = self.data['inventory']
            low_stock_items = []
            
            for _, item in inventory_df.iterrows():
                item_name = item.get('item_name', '')
                if not item_name:
                    continue
                
                # Calculate current quantity
                current_qty = self._get_current_quantity(item)
                reorder_level = float(item.get('reorder_level', 10))
                unit = item.get('unit', 'units')
                
                # Check if item is low stock
                if current_qty <= reorder_level and current_qty > 0:
                    low_stock_items.append({
                        'name': item_name,
                        'current_qty': current_qty,
                        'reorder_level': reorder_level,
                        'unit': unit
                    })
                elif current_qty <= 0:
                    # Out of stock
                    low_stock_items.append({
                        'name': item_name,
                        'current_qty': 0,
                        'reorder_level': reorder_level,
                        'unit': unit,
                        'out_of_stock': True
                    })
            
            # Send notifications for low stock items
            for item in low_stock_items:
                if self._should_send_notification(f"low_stock_{item['name']}"):
                    self._send_low_stock_notification(item)
                    
        except Exception as e:
            self.logger.error(f"Error checking low stock notifications: {e}")
    
    def _get_current_quantity(self, item):
        """Calculate current quantity from inventory item"""
        # Try different quantity fields
        if 'qty_purchased' in item and pd.notna(item['qty_purchased']) and 'qty_used' in item and pd.notna(item['qty_used']):
            return float(item['qty_purchased']) - float(item['qty_used'])
        elif 'qty_left' in item and pd.notna(item['qty_left']):
            return float(item['qty_left'])
        elif 'quantity' in item and pd.notna(item['quantity']):
            return float(item['quantity'])
        else:
            return 0
    
    def _should_send_notification(self, notification_key, cooldown_hours=4):
        """Check if enough time has passed since last notification"""
        last_sent = self.notification_settings['last_notification_times'].get(notification_key)
        if not last_sent:
            return True
        
        try:
            last_sent_time = datetime.fromisoformat(last_sent)
            cooldown_time = timedelta(hours=cooldown_hours)
            return datetime.now() - last_sent_time > cooldown_time
        except:
            return True
    
    def _record_notification_sent(self, notification_key):
        """Record that a notification was sent"""
        self.notification_settings['last_notification_times'][notification_key] = datetime.now().isoformat()
        self.save_settings()
    
    def _send_low_stock_notification(self, item):
        """Send low stock notification to Abiram's Kitchen"""
        try:
            if item.get('out_of_stock'):
                message = f"🚨 OUT OF STOCK ALERT 🚨\n\n" \
                         f"Item: {item['name']}\n" \
                         f"Status: COMPLETELY OUT OF STOCK\n" \
                         f"Reorder Level: {item['reorder_level']} {item['unit']}\n\n" \
                         f"⚠️ URGENT: Please restock immediately!\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            else:
                message = f"⚠️ LOW STOCK ALERT ⚠️\n\n" \
                         f"Item: {item['name']}\n" \
                         f"Current Stock: {item['current_qty']} {item['unit']}\n" \
                         f"Reorder Level: {item['reorder_level']} {item['unit']}\n\n" \
                         f"📋 Please consider restocking soon.\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            success = self._send_whatsapp_message(message)
            if success:
                self._record_notification_sent(f"low_stock_{item['name']}")
                self.logger.info(f"Sent low stock notification for {item['name']}")
            else:
                self.logger.warning(f"Failed to send low stock notification for {item['name']}")
                
        except Exception as e:
            self.logger.error(f"Error sending low stock notification: {e}")
    
    def _send_whatsapp_message(self, message):
        """Send message to Abiram's Kitchen WhatsApp group"""
        try:
            if not WHATSAPP_AVAILABLE:
                self.logger.warning("WhatsApp integration not available")
                return False

            if not self.whatsapp_widget:
                self.logger.warning("WhatsApp widget not available")
                return False

            # Check if WhatsApp is connected
            if not hasattr(self.whatsapp_widget, 'whatsapp_driver') or not self.whatsapp_widget.whatsapp_driver:
                self.logger.warning("WhatsApp driver not available")
                return False

            if not self.whatsapp_widget.whatsapp_driver.is_connected:
                self.logger.warning("WhatsApp not connected")
                return False

            # Sanitize message for ChromeDriver compatibility
            try:
                from modules.whatsapp_integration import sanitize_message_for_chrome
                sanitized_message = sanitize_message_for_chrome(message)
            except ImportError:
                # Fallback sanitization if function not available
                sanitized_message = message.encode('ascii', 'replace').decode('ascii')

            # Send message to Abiram's Kitchen
            success = self.whatsapp_widget.whatsapp_driver.send_message_to_abirams_kitchen(sanitized_message)
            return success

        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {e}")
            return False

    def _send_cleaning_reminder(self, due_tasks):
        """Send cleaning task reminders to Abiram's Kitchen"""
        try:
            if len(due_tasks) == 1:
                task = due_tasks[0]
                message = f"🧹 CLEANING TASK REMINDER 🧹\n\n" \
                         f"Task: {task['name']}\n" \
                         f"Assigned to: {task['assigned_to']}\n" \
                         f"Location: {task['location']}\n" \
                         f"Due Date: {task['due_date']}\n\n" \
                         f"⏰ Please complete this task today!\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            else:
                message = f"🧹 DAILY CLEANING TASKS 🧹\n\n" \
                         f"Tasks due today ({len(due_tasks)} tasks):\n\n"

                for i, task in enumerate(due_tasks, 1):
                    message += f"{i}. {task['name']}\n" \
                              f"   👤 {task['assigned_to']}\n" \
                              f"   📍 {task['location']}\n\n"

                message += f"⏰ Please complete all tasks today!\n" \
                          f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            success = self._send_whatsapp_message(message)
            if success:
                self._record_notification_sent("cleaning_tasks_today")
                self.logger.info(f"Sent cleaning reminder for {len(due_tasks)} tasks")
            else:
                self.logger.warning(f"Failed to send cleaning reminder")

        except Exception as e:
            self.logger.error(f"Error sending cleaning reminder: {e}")

    def _send_packing_material_alert(self, material):
        """Send packing material alert to Abiram's Kitchen"""
        try:
            if material.get('out_of_stock'):
                message = f"📦 PACKING MATERIAL OUT OF STOCK 📦\n\n" \
                         f"Material: {material['name']}\n" \
                         f"Status: COMPLETELY OUT OF STOCK\n" \
                         f"Minimum Required: {material['minimum_stock']} {material['unit']}\n\n" \
                         f"🚨 URGENT: Cannot pack orders without this material!\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            else:
                message = f"📦 PACKING MATERIAL LOW STOCK 📦\n\n" \
                         f"Material: {material['name']}\n" \
                         f"Current Stock: {material['current_stock']} {material['unit']}\n" \
                         f"Minimum Required: {material['minimum_stock']} {material['unit']}\n\n" \
                         f"⚠️ Please restock soon to avoid order delays!\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            success = self._send_whatsapp_message(message)
            if success:
                self._record_notification_sent(f"packing_material_{material['name']}")
                self.logger.info(f"Sent packing material alert for {material['name']}")
            else:
                self.logger.warning(f"Failed to send packing material alert for {material['name']}")

        except Exception as e:
            self.logger.error(f"Error sending packing material alert: {e}")

    def _send_gas_warning(self, cylinder_id, days_remaining, severity):
        """Send gas level warning to Abiram's Kitchen"""
        try:
            if severity == "CRITICAL":
                message = f"🔥 CRITICAL GAS ALERT 🔥\n\n" \
                         f"Cylinder ID: {cylinder_id}\n" \
                         f"Days Remaining: {days_remaining}\n\n" \
                         f"🚨 URGENT: Gas will run out very soon!\n" \
                         f"🛒 Order new cylinder IMMEDIATELY!\n" \
                         f"⚠️ Kitchen operations may stop!\n\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            else:
                message = f"⛽ GAS LEVEL WARNING ⛽\n\n" \
                         f"Cylinder ID: {cylinder_id}\n" \
                         f"Days Remaining: {days_remaining}\n\n" \
                         f"⚠️ Gas level is getting low.\n" \
                         f"📋 Please arrange for new cylinder soon.\n\n" \
                         f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            success = self._send_whatsapp_message(message)
            if success:
                notification_key = "gas_critical" if severity == "CRITICAL" else "gas_warning"
                self._record_notification_sent(notification_key)
                self.logger.info(f"Sent gas {severity.lower()} warning")
            else:
                self.logger.warning(f"Failed to send gas {severity.lower()} warning")

        except Exception as e:
            self.logger.error(f"Error sending gas warning: {e}")
    
    def check_cleaning_reminders(self):
        """Check for cleaning tasks due today and send reminders"""
        try:
            if 'cleaning_maintenance' not in self.data or self.data['cleaning_maintenance'].empty:
                return

            cleaning_df = self.data['cleaning_maintenance']
            today = datetime.now().date()
            due_tasks = []

            for _, task in cleaning_df.iterrows():
                task_name = task.get('task_name', '')
                if not task_name:
                    continue

                # Check if task is due today
                next_due = task.get('next_due')
                if pd.notna(next_due):
                    try:
                        due_date = pd.to_datetime(next_due).date()
                        if due_date <= today:
                            assigned_to = task.get('assigned_to', 'Kitchen Staff')
                            location = task.get('location', 'Kitchen')
                            due_tasks.append({
                                'name': task_name,
                                'assigned_to': assigned_to,
                                'location': location,
                                'due_date': due_date
                            })
                    except:
                        continue

            # Send notifications for due tasks
            if due_tasks and self._should_send_notification("cleaning_tasks_today", cooldown_hours=12):
                self._send_cleaning_reminder(due_tasks)

        except Exception as e:
            self.logger.error(f"Error checking cleaning reminders: {e}")

    def check_packing_materials_alerts(self):
        """Check for low packing materials and send alerts"""
        try:
            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                return

            materials_df = self.data['packing_materials']
            low_materials = []

            for _, material in materials_df.iterrows():
                material_name = material.get('material_name', '')
                if not material_name:
                    continue

                current_stock = int(material.get('current_stock', 0))
                minimum_stock = int(material.get('minimum_stock', 0))
                unit = material.get('unit', 'pieces')

                if current_stock <= 0:
                    low_materials.append({
                        'name': material_name,
                        'current_stock': 0,
                        'minimum_stock': minimum_stock,
                        'unit': unit,
                        'out_of_stock': True
                    })
                elif current_stock <= minimum_stock:
                    low_materials.append({
                        'name': material_name,
                        'current_stock': current_stock,
                        'minimum_stock': minimum_stock,
                        'unit': unit
                    })

            # Send notifications for low materials
            for material in low_materials:
                if self._should_send_notification(f"packing_material_{material['name']}"):
                    self._send_packing_material_alert(material)

        except Exception as e:
            self.logger.error(f"Error checking packing materials alerts: {e}")

    def check_gas_level_warnings(self):
        """Check for low gas levels and send warnings"""
        try:
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
                    self._send_gas_warning(cylinder_id, days_remaining, "CRITICAL")
            elif days_remaining <= warning_threshold:
                if self._should_send_notification("gas_warning", cooldown_hours=12):
                    self._send_gas_warning(cylinder_id, days_remaining, "WARNING")

        except Exception as e:
            self.logger.error(f"Error checking gas level warnings: {e}")
    
    def send_test_notification(self):
        """Send a test notification to verify the system works"""
        try:
            message = f"🧪 TEST NOTIFICATION 🧪\n\n" \
                     f"This is a test message from VARSYS Kitchen Dashboard.\n" \
                     f"Automated notifications are working correctly!\n\n" \
                     f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            success = self._send_whatsapp_message(message)
            return success

        except Exception as e:
            self.logger.error(f"Error sending test notification: {e}")
            return False

    # Real-time notification triggers
    def on_inventory_updated(self, item_name=None):
        """Trigger immediate check when inventory is updated"""
        try:
            if item_name:
                # Check specific item
                self._check_specific_item_stock(item_name)
            else:
                # Check all items
                self.check_low_stock_notifications()
        except Exception as e:
            self.logger.error(f"Error in inventory update trigger: {e}")

    def on_cleaning_task_updated(self):
        """Trigger immediate check when cleaning tasks are updated"""
        try:
            self.check_cleaning_reminders()
        except Exception as e:
            self.logger.error(f"Error in cleaning task update trigger: {e}")

    def on_packing_material_updated(self, material_name=None):
        """Trigger immediate check when packing materials are updated"""
        try:
            if material_name:
                self._check_specific_packing_material(material_name)
            else:
                self.check_packing_materials_alerts()
        except Exception as e:
            self.logger.error(f"Error in packing material update trigger: {e}")

    def on_gas_level_updated(self):
        """Trigger immediate check when gas levels are updated"""
        try:
            self.check_gas_level_warnings()
        except Exception as e:
            self.logger.error(f"Error in gas level update trigger: {e}")

    def _check_specific_item_stock(self, item_name):
        """Check stock for a specific inventory item"""
        try:
            if 'inventory' not in self.data or self.data['inventory'].empty:
                return

            inventory_df = self.data['inventory']
            item_row = inventory_df[inventory_df['item_name'].str.lower() == item_name.lower()]

            if item_row.empty:
                return

            item = item_row.iloc[0]
            current_qty = self._get_current_quantity(item)
            reorder_level = float(item.get('reorder_level', 10))
            unit = item.get('unit', 'units')

            # Check if immediate notification needed
            if current_qty <= reorder_level:
                item_data = {
                    'name': item_name,
                    'current_qty': current_qty,
                    'reorder_level': reorder_level,
                    'unit': unit,
                    'out_of_stock': current_qty <= 0
                }

                # Send immediate notification (bypass cooldown for real-time updates)
                self._send_low_stock_notification(item_data)

        except Exception as e:
            self.logger.error(f"Error checking specific item stock: {e}")

    def _check_specific_packing_material(self, material_name):
        """Check stock for a specific packing material"""
        try:
            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                return

            materials_df = self.data['packing_materials']
            material_row = materials_df[materials_df['material_name'].str.lower() == material_name.lower()]

            if material_row.empty:
                return

            material = material_row.iloc[0]
            current_stock = int(material.get('current_stock', 0))
            minimum_stock = int(material.get('minimum_stock', 0))
            unit = material.get('unit', 'pieces')

            # Check if immediate notification needed
            if current_stock <= minimum_stock:
                material_data = {
                    'name': material_name,
                    'current_stock': current_stock,
                    'minimum_stock': minimum_stock,
                    'unit': unit,
                    'out_of_stock': current_stock <= 0
                }

                # Send immediate notification (bypass cooldown for real-time updates)
                self._send_packing_material_alert(material_data)

        except Exception as e:
            self.logger.error(f"Error checking specific packing material: {e}")

    def force_check_all(self):
        """Force immediate check of all notification types"""
        try:
            self.logger.info("Forcing immediate check of all notification types")
            self.check_low_stock_notifications()
            self.check_cleaning_reminders()
            self.check_packing_materials_alerts()
            self.check_gas_level_warnings()
        except Exception as e:
            self.logger.error(f"Error in force check all: {e}")

    def get_status(self):
        """Get current status of the notification system"""
        return {
            'monitoring_active': self.monitoring_active,
            'settings': self.notification_settings,
            'whatsapp_connected': self._is_whatsapp_connected()
        }

    def _is_whatsapp_connected(self):
        """Check if WhatsApp is connected"""
        try:
            if not self.whatsapp_widget or not hasattr(self.whatsapp_widget, 'whatsapp_driver'):
                return False
            return self.whatsapp_widget.whatsapp_driver and self.whatsapp_widget.whatsapp_driver.is_connected
        except:
            return False
