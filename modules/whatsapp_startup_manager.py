#!/usr/bin/env python3
"""
WhatsApp Startup Manager
Handles automatic WhatsApp connection and Abiram's Kitchen detection during application startup
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# Enhanced fallback with proper UTF-8 encoding for Windows
def safe_print(*args, **kwargs):
    try:
        # Force UTF-8 encoding for output
        import sys
        if sys.platform.startswith('win'):
            try:
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                elif hasattr(sys.stdout, 'buffer'):
                    message = ' '.join(str(arg) for arg in args) + '\n'
                    sys.stdout.buffer.write(message.encode('utf-8', errors='replace'))
                    sys.stdout.buffer.flush()
                    return
            except:
                pass
        
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: Replace problematic Unicode characters
        safe_args = []
        for arg in args:
            try:
                arg_str = str(arg)
                replacements = {
                    '✅': '[OK]', '❌': '[ERROR]', '⚠️': '[WARNING]', '🔄': '[REFRESH]',
                    '📱': '[PHONE]', '🔍': '[SEARCH]', '🎯': '[TARGET]', '🚀': '[START]',
                    '💬': '[MESSAGE]', '👤': '[CONTACT]', '👥': '[GROUP]', '🔗': '[CONNECT]'
                }
                for unicode_char, replacement in replacements.items():
                    arg_str = arg_str.replace(unicode_char, replacement)
                safe_args.append(arg_str.encode('ascii', errors='replace').decode('ascii'))
            except:
                safe_args.append('[UNPRINTABLE]')
        print(*safe_args, **kwargs)
    except Exception as e:
        try:
            print(f"[LOGGING ERROR: {e}]")
        except:
            pass

class WhatsAppStartupManager:
    """Manages automatic WhatsApp connection and Abiram's Kitchen detection during startup"""
    
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.preferences_file = Path("data/whatsapp_preferences.json")
        self.preferences = self.load_preferences()
        self.startup_thread = None
        self.abirams_kitchen_found = False
        self.connection_status = "disconnected"  # disconnected, connecting, connected, failed
        self.startup_callbacks = []
        
    def load_preferences(self):
        """Load WhatsApp preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    safe_print(f"[OK] Loaded WhatsApp preferences: {prefs}")
                    return prefs
            else:
                # Default preferences for new installation
                default_prefs = {
                    "auto_connect": True,
                    "setup_completed": False,
                    "skip_setup": False,
                    "last_connection": None,
                    "abirams_kitchen_enabled": True
                }
                safe_print("[INFO] Using default WhatsApp preferences (new installation)")
                return default_prefs
        except Exception as e:
            safe_print(f"[ERROR] Error loading WhatsApp preferences: {e}")
            return {
                "auto_connect": True,
                "setup_completed": False,
                "skip_setup": False,
                "last_connection": None,
                "abirams_kitchen_enabled": True
            }
    
    def save_preferences(self):
        """Save WhatsApp preferences to file"""
        try:
            # Ensure data directory exists
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            safe_print("[OK] WhatsApp preferences saved")
        except Exception as e:
            safe_print(f"[ERROR] Error saving WhatsApp preferences: {e}")
    
    def is_first_time_setup(self):
        """Check if this is a first-time setup"""
        return not self.preferences.get("setup_completed", False)
    
    def should_auto_connect(self):
        """Check if automatic connection should be attempted"""
        return (
            self.preferences.get("auto_connect", True) and 
            not self.preferences.get("skip_setup", False) and
            self.preferences.get("abirams_kitchen_enabled", True)
        )
    
    def add_startup_callback(self, callback):
        """Add callback to be called when startup process completes"""
        self.startup_callbacks.append(callback)
    
    def notify_startup_complete(self, success, message=""):
        """Notify all callbacks that startup process is complete"""
        for callback in self.startup_callbacks:
            try:
                callback(success, message)
            except Exception as e:
                safe_print(f"[ERROR] Error in startup callback: {e}")
    
    def start_automatic_connection(self):
        """Start automatic WhatsApp connection process"""
        if not self.should_auto_connect():
            safe_print("[INFO] Automatic WhatsApp connection disabled by user preferences")
            self.notify_startup_complete(False, "Auto-connect disabled")
            return False
        
        if self.startup_thread and self.startup_thread.is_alive():
            safe_print("[WARNING] WhatsApp startup process already running")
            return False
        
        safe_print("[START] Starting automatic WhatsApp connection...")
        self.connection_status = "connecting"
        
        # Start connection in background thread
        self.startup_thread = threading.Thread(
            target=self._connection_thread,
            daemon=True,
            name="WhatsAppStartup"
        )
        self.startup_thread.start()
        return True
    
    def _connection_thread(self):
        """Background thread for WhatsApp connection process"""
        try:
            safe_print("[CONNECT] WhatsApp startup thread started")
            
            # Step 1: Check if WhatsApp integration is available
            if not self._check_whatsapp_availability():
                self.connection_status = "failed"
                self.notify_startup_complete(False, "WhatsApp integration not available")
                return
            
            # Step 2: Attempt to connect to WhatsApp Web
            if not self._attempt_whatsapp_connection():
                self.connection_status = "failed"
                if self.is_first_time_setup():
                    safe_print("[INFO] First-time setup required - will show setup dialog")
                    self.notify_startup_complete(False, "First-time setup required")
                else:
                    self.notify_startup_complete(False, "Connection failed")
                return
            
            # Step 3: Search for Abiram's Kitchen group
            if not self._find_abirams_kitchen():
                safe_print("[WARNING] Abiram's Kitchen group not found, but connection successful")
                self.connection_status = "connected"
                self.notify_startup_complete(True, "Connected but group not found")
                return
            
            # Step 4: Success - everything ready
            self.connection_status = "connected"
            self.abirams_kitchen_found = True
            self.preferences["setup_completed"] = True
            self.preferences["last_connection"] = datetime.now().isoformat()
            self.save_preferences()
            
            safe_print("[SUCCESS] WhatsApp startup completed successfully")
            self.notify_startup_complete(True, "Abiram's Kitchen ready for messaging")
            
        except Exception as e:
            safe_print(f"[ERROR] WhatsApp startup thread error: {e}")
            self.connection_status = "failed"
            self.notify_startup_complete(False, f"Startup error: {e}")
    
    def _check_whatsapp_availability(self):
        """Check if WhatsApp integration components are available"""
        try:
            # Check if selenium is available
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                safe_print("[OK] Selenium WebDriver available")
            except ImportError:
                safe_print("[ERROR] Selenium not available - WhatsApp integration disabled")
                return False

            # Check if Chrome is available
            try:
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                safe_print("[OK] Chrome WebDriver components available")
            except ImportError:
                safe_print("[ERROR] Chrome WebDriver components not available")
                return False

            # Check if Chrome browser is installed
            if not self._check_chrome_installation():
                safe_print("[ERROR] Chrome browser not found - WhatsApp integration disabled")
                return False

            return True

        except Exception as e:
            safe_print(f"[ERROR] Error checking WhatsApp availability: {e}")
            return False

    def _check_chrome_installation(self):
        """Check if Chrome browser is installed and accessible"""
        try:
            from modules.whatsapp_integration import WhatsAppWebDriver

            # Create temporary driver instance to check Chrome
            temp_driver = WhatsAppWebDriver()
            chrome_paths = temp_driver.get_chrome_paths()

            # Check if Chrome exists in any of the standard locations
            for path in chrome_paths:
                if os.path.exists(path):
                    safe_print(f"[OK] Chrome found at: {path}")
                    return True

            # Check system PATH
            import shutil
            chrome_names = ["chrome", "google-chrome", "google-chrome-stable", "chromium"]
            for name in chrome_names:
                if shutil.which(name):
                    safe_print(f"[OK] Chrome found in PATH: {name}")
                    return True

            safe_print("[WARNING] Chrome browser not found in standard locations")
            safe_print("[HELP] Please install Chrome from: https://www.google.com/chrome/")
            return False

        except Exception as e:
            safe_print(f"[ERROR] Error checking Chrome installation: {e}")
            return False
    
    def _attempt_whatsapp_connection(self):
        """Attempt to connect to WhatsApp Web with automatic Chrome startup"""
        try:
            safe_print("[CONNECT] Attempting WhatsApp Web connection...")

            # Import WhatsApp integration
            from modules.whatsapp_integration import WhatsAppWebDriver

            # Create driver instance
            self.whatsapp_driver = WhatsAppWebDriver()

            # Enhanced connection process with Chrome startup handling
            safe_print("[CHROME] Preparing Chrome for automatic startup...")

            # Step 1: Ensure Chrome is ready for startup
            chrome_ready = self.whatsapp_driver.ensure_chrome_startup_ready()
            if not chrome_ready:
                safe_print("[ERROR] Chrome not ready for startup")
                return False

            # Step 2: Setup driver (this will start Chrome automatically)
            driver_setup_success = self.whatsapp_driver.setup_driver()
            if not driver_setup_success:
                safe_print("[ERROR] Failed to setup Chrome WebDriver")
                return False

            safe_print("[OK] Chrome WebDriver setup successful")

            # Step 2: Connect to WhatsApp Web
            safe_print("[WHATSAPP] Connecting to WhatsApp Web...")
            connection_success = self.whatsapp_driver.connect_to_whatsapp_web()

            if connection_success:
                safe_print("[OK] WhatsApp Web connection successful")
                return True
            else:
                safe_print("[ERROR] WhatsApp Web connection failed")
                return False

        except Exception as e:
            safe_print(f"[ERROR] Error attempting WhatsApp connection: {e}")
            # Provide specific guidance based on error type
            error_str = str(e).lower()
            if "chrome" in error_str:
                safe_print("[HELP] Chrome-related error - ensure Chrome is installed")
            elif "webdriver" in error_str:
                safe_print("[HELP] WebDriver error - Chrome may need to be updated")
            elif "timeout" in error_str:
                safe_print("[HELP] Connection timeout - check internet connection")
            return False
    
    def _find_abirams_kitchen(self):
        """Search for Abiram's Kitchen group specifically"""
        try:
            safe_print("[SEARCH] Searching for Abiram's Kitchen group...")
            
            if not hasattr(self, 'whatsapp_driver') or not self.whatsapp_driver:
                safe_print("[ERROR] WhatsApp driver not available")
                return False
            
            # Use the specialized find function
            target_group = self.whatsapp_driver.find_abirams_kitchen()
            
            if target_group:
                safe_print(f"[SUCCESS] Found Abiram's Kitchen: {target_group['name']}")
                return True
            else:
                safe_print("[WARNING] Abiram's Kitchen group not found")
                return False
                
        except Exception as e:
            safe_print(f"[ERROR] Error searching for Abiram's Kitchen: {e}")
            return False
    
    def get_status(self):
        """Get current connection status"""
        return {
            "status": self.connection_status,
            "abirams_kitchen_found": self.abirams_kitchen_found,
            "is_first_time": self.is_first_time_setup(),
            "auto_connect_enabled": self.should_auto_connect()
        }
    
    def skip_setup(self):
        """Mark setup as skipped by user choice"""
        self.preferences["skip_setup"] = True
        self.preferences["auto_connect"] = False
        self.save_preferences()
        safe_print("[INFO] WhatsApp setup skipped by user")
    
    def enable_whatsapp_later(self):
        """Enable WhatsApp integration after initial skip"""
        self.preferences["skip_setup"] = False
        self.preferences["auto_connect"] = True
        self.save_preferences()
        safe_print("[INFO] WhatsApp integration enabled by user")
        return self.start_automatic_connection()
    
    def send_message_to_abirams_kitchen(self, message):
        """Send message to Abiram's Kitchen if available"""
        try:
            if not hasattr(self, 'whatsapp_driver') or not self.whatsapp_driver:
                safe_print("[ERROR] WhatsApp not connected")
                return False

            if not self.abirams_kitchen_found:
                safe_print("[ERROR] Abiram's Kitchen group not available")
                return False

            return self.whatsapp_driver.send_message_to_abirams_kitchen(message)

        except Exception as e:
            safe_print(f"[ERROR] Error sending message: {e}")
            return False

    def show_setup_dialog_if_needed(self, parent=None):
        """Show setup dialog if this is first-time setup"""
        try:
            if self.is_first_time_setup() and not self.preferences.get("skip_setup", False):
                safe_print("[INFO] First-time setup detected - showing setup dialog")

                from modules.whatsapp_setup_dialog import show_setup_dialog
                success, message = show_setup_dialog(parent)

                if success:
                    safe_print("[SUCCESS] Setup dialog completed successfully")
                    return True
                else:
                    safe_print(f"[INFO] Setup dialog result: {message}")
                    return False
            else:
                safe_print("[INFO] Setup dialog not needed")
                return True

        except Exception as e:
            safe_print(f"[ERROR] Error showing setup dialog: {e}")
            return False

    def get_whatsapp_driver(self):
        """Get the WhatsApp driver instance if available"""
        return getattr(self, 'whatsapp_driver', None)

    def is_connected(self):
        """Check if WhatsApp is currently connected"""
        return (
            self.connection_status == "connected" and
            hasattr(self, 'whatsapp_driver') and
            self.whatsapp_driver and
            getattr(self.whatsapp_driver, 'is_connected', False)
        )

    def reset_preferences(self):
        """Reset all preferences to defaults"""
        self.preferences = {
            "auto_connect": True,
            "setup_completed": False,
            "skip_setup": False,
            "last_connection": None,
            "abirams_kitchen_enabled": True
        }
        self.save_preferences()
        safe_print("[INFO] WhatsApp preferences reset to defaults")
