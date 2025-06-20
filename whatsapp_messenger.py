#!/usr/bin/env python3
"""
Standalone WhatsApp Messenger Application
Monitors shared JSON file for messages and sends them via WhatsApp Web
"""

import os
import sys
import json
import time
import argparse
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'modules'))

class WhatsAppMessenger:
    """Standalone WhatsApp messenger that processes messages from shared JSON file"""
    
    def __init__(self, config_file: str = "whatsapp_config.json", messages_file: str = "whatsapp_messages.json"):
        self.config_file = config_file
        self.messages_file = messages_file
        self.running = False
        self.whatsapp_driver = None
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize WhatsApp driver
        self.initialize_whatsapp_driver()
        
        self.logger.info("Standalone WhatsApp Messenger initialized")
    
    def setup_logging(self):
        """Setup logging for the standalone messenger"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('whatsapp_messenger.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('WhatsAppMessenger')
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            "target_group": "Abiram's Kitchen",
            "check_interval_seconds": 30,
            "max_retries": 3,
            "retry_delay_seconds": 60,
            "connection_timeout_seconds": 300,
            "message_batch_size": 5,
            "priority_order": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    default_config.update(config_data.get('messenger_settings', {}))
                    self.logger.info("Configuration loaded from file")
            else:
                self.save_config(default_config)
                self.logger.info("Created default configuration file")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
        
        return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            config_data = {
                "messenger_settings": config,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def initialize_whatsapp_driver(self):
        """Initialize WhatsApp Web driver with all our fixes"""
        try:
            from modules.whatsapp_integration import WhatsAppWebDriver
            
            self.whatsapp_driver = WhatsAppWebDriver()
            self.logger.info("WhatsApp Web driver initialized")
            
            # Attempt initial connection
            if self.connect_to_whatsapp():
                self.logger.info("✅ Successfully connected to WhatsApp Web")
            else:
                self.logger.warning("⚠️ Initial WhatsApp Web connection failed")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize WhatsApp driver: {e}")
            self.whatsapp_driver = None
    
    def connect_to_whatsapp(self) -> bool:
        """Connect to WhatsApp Web with timeout"""
        try:
            if not self.whatsapp_driver:
                return False
            
            self.logger.info("Connecting to WhatsApp Web...")
            
            # Use the enhanced connection method with Chrome startup handling
            success = self.whatsapp_driver.ensure_chrome_startup_ready()
            if not success:
                self.logger.error("Chrome startup preparation failed")
                return False
            
            # Connect to WhatsApp Web
            success = self.whatsapp_driver.connect()
            if success:
                self.logger.info("Connected to WhatsApp Web successfully")
                
                # Verify connection by finding target group
                target_group = self.whatsapp_driver.find_abirams_kitchen()
                if target_group:
                    self.logger.info(f"✅ Found target group: {self.config['target_group']}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Target group '{self.config['target_group']}' not found")
                    return False
            else:
                self.logger.error("Failed to connect to WhatsApp Web")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to WhatsApp: {e}")
            return False
    
    def read_pending_messages(self) -> List[Dict]:
        """Read pending messages from shared JSON file with file locking"""
        try:
            if not os.path.exists(self.messages_file):
                return []
            
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                # Lock the file for reading based on platform
                if sys.platform == 'win32' and MSVCRT_AVAILABLE:
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                elif FCNTL_AVAILABLE:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)

                try:
                    data = json.load(f)
                    messages = data.get('messages', [])

                    # Filter pending messages
                    pending_messages = [msg for msg in messages if msg.get('sent_status') == 'pending']

                    # Sort by priority and timestamp
                    priority_order = {p: i for i, p in enumerate(self.config['priority_order'])}
                    pending_messages.sort(key=lambda x: (
                        priority_order.get(x.get('priority', 'LOW'), 999),
                        x.get('timestamp', '')
                    ))

                    return pending_messages

                finally:
                    # Unlock the file based on platform
                    if sys.platform == 'win32' and MSVCRT_AVAILABLE:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    elif FCNTL_AVAILABLE:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        
        except Exception as e:
            self.logger.error(f"Error reading pending messages: {e}")
            return []
    
    def update_message_status(self, message_id: str, status: str, error_message: str = None):
        """Update message status in shared JSON file"""
        try:
            with open(self.messages_file, 'r+', encoding='utf-8') as f:
                # Lock the file for writing based on platform
                if sys.platform == 'win32' and MSVCRT_AVAILABLE:
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                elif FCNTL_AVAILABLE:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)

                try:
                    # Read current data
                    f.seek(0)
                    data = json.load(f)

                    # Update message status
                    for message in data.get('messages', []):
                        if message.get('id') == message_id:
                            message['sent_status'] = status
                            message['last_updated'] = datetime.now().isoformat()
                            if error_message:
                                message['error_message'] = error_message
                            if status == 'retry':
                                message['retry_count'] = message.get('retry_count', 0) + 1
                            break

                    # Write back to file
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=2, ensure_ascii=False)

                finally:
                    # Unlock the file based on platform
                    if sys.platform == 'win32' and MSVCRT_AVAILABLE:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    elif FCNTL_AVAILABLE:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        
        except Exception as e:
            self.logger.error(f"Error updating message status: {e}")
    
    def send_message_to_target_group(self, message: Dict) -> bool:
        """Send message to target WhatsApp group"""
        try:
            if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
                self.logger.error("WhatsApp driver not connected")
                return False
            
            # Use sanitized content for sending
            content = message.get('sanitized_content', message.get('content', ''))
            
            self.logger.info(f"Sending message: {message['message_type']} - {message['priority']}")
            
            # Send message using the specialized method for Abiram's Kitchen
            success = self.whatsapp_driver.send_message_to_abirams_kitchen(content)
            
            if success:
                self.logger.info(f"✅ Message sent successfully: {message['id']}")
                return True
            else:
                self.logger.error(f"❌ Failed to send message: {message['id']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message to target group: {e}")
            return False
    
    def process_pending_messages(self):
        """Process all pending messages"""
        try:
            pending_messages = self.read_pending_messages()
            
            if not pending_messages:
                return
            
            self.logger.info(f"Processing {len(pending_messages)} pending messages")
            
            # Process messages in batches
            batch_size = self.config.get('message_batch_size', 5)
            
            for i in range(0, len(pending_messages), batch_size):
                batch = pending_messages[i:i + batch_size]
                
                for message in batch:
                    message_id = message.get('id')
                    retry_count = message.get('retry_count', 0)
                    max_retries = message.get('max_retries', self.config['max_retries'])
                    
                    # Check if message has exceeded retry limit
                    if retry_count >= max_retries:
                        self.logger.warning(f"Message {message_id} exceeded retry limit, marking as failed")
                        self.update_message_status(message_id, 'failed', 'Exceeded maximum retry attempts')
                        continue
                    
                    # Attempt to send message
                    if self.send_message_to_target_group(message):
                        self.update_message_status(message_id, 'sent')
                    else:
                        # Mark for retry
                        self.update_message_status(message_id, 'retry', 'Failed to send message')
                        
                        # Wait before next retry
                        time.sleep(self.config.get('retry_delay_seconds', 60))
                
                # Small delay between batches
                if i + batch_size < len(pending_messages):
                    time.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"Error processing pending messages: {e}")
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting WhatsApp messenger monitoring loop")
        self.running = True
        
        while self.running:
            try:
                # Check connection status
                if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
                    self.logger.warning("WhatsApp connection lost, attempting to reconnect...")
                    if not self.connect_to_whatsapp():
                        self.logger.error("Failed to reconnect to WhatsApp, waiting before retry...")
                        time.sleep(self.config.get('connection_timeout_seconds', 300))
                        continue
                
                # Process pending messages
                self.process_pending_messages()
                
                # Wait for next check
                time.sleep(self.config.get('check_interval_seconds', 30))
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying
        
        self.running = False
        self.logger.info("WhatsApp messenger monitoring loop stopped")
    
    def stop(self):
        """Stop the messenger"""
        self.running = False
        if self.whatsapp_driver:
            try:
                self.whatsapp_driver.disconnect()
            except Exception as e:
                self.logger.error(f"Error disconnecting WhatsApp driver: {e}")
    
    def get_status(self) -> Dict:
        """Get current status of the messenger"""
        pending_count = len(self.read_pending_messages())
        
        return {
            'running': self.running,
            'whatsapp_connected': self.whatsapp_driver and self.whatsapp_driver.is_connected,
            'pending_messages': pending_count,
            'target_group': self.config.get('target_group'),
            'last_check': datetime.now().isoformat()
        }


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(description='Standalone WhatsApp Messenger')
    parser.add_argument('--config', default='whatsapp_config.json',
                       help='Configuration file path')
    parser.add_argument('--messages', default='whatsapp_messages.json',
                       help='Messages file path')
    parser.add_argument('--status', action='store_true',
                       help='Show status and exit')
    parser.add_argument('--test', action='store_true',
                       help='Test connection and exit')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (background process)')

    args = parser.parse_args()

    # Create messenger instance
    messenger = WhatsAppMessenger(args.config, args.messages)

    try:
        if args.status:
            # Show status and exit
            status = messenger.get_status()
            print("\n=== WhatsApp Messenger Status ===")
            print(f"Running: {status['running']}")
            print(f"WhatsApp Connected: {status['whatsapp_connected']}")
            print(f"Pending Messages: {status['pending_messages']}")
            print(f"Target Group: {status['target_group']}")
            print(f"Last Check: {status['last_check']}")
            print("================================\n")

        elif args.test:
            # Test connection and exit
            print("\n=== Testing WhatsApp Connection ===")
            if messenger.connect_to_whatsapp():
                print("✅ Connection test successful!")
            else:
                print("❌ Connection test failed!")
            print("==================================\n")

        else:
            # Run monitoring loop
            print("\n=== Starting WhatsApp Messenger ===")
            print(f"Target Group: {messenger.config.get('target_group')}")
            print(f"Check Interval: {messenger.config.get('check_interval_seconds')}s")
            print(f"Messages File: {args.messages}")
            print(f"Config File: {args.config}")
            print("===================================\n")

            if args.daemon:
                print("Running in daemon mode...")
                # TODO: Implement proper daemon mode
                messenger.run_monitoring_loop()
            else:
                print("Running in foreground mode (Ctrl+C to stop)...")
                messenger.run_monitoring_loop()

    except KeyboardInterrupt:
        print("\nShutting down WhatsApp Messenger...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        messenger.stop()
        print("WhatsApp Messenger stopped.")


if __name__ == "__main__":
    main()
