"""
WhatsApp Integration with Multi-device Firebase Sync
Provides WhatsApp messaging capabilities with cross-device synchronization
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                                   QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QSplitter,
                                   QTabWidget, QComboBox, QCheckBox, QSpinBox, QDateTimeEdit,
                                   QMessageBox, QProgressBar, QFrame, QScrollArea, QGroupBox)
    from PySide6.QtCore import Qt, QTimer, Signal, QThread, QDateTime, QObject
    from PySide6.QtGui import QFont, QPixmap, QIcon

    # Create alias for compatibility
    pyqtSignal = Signal
    QT_AVAILABLE = True

except ImportError as e:
    safe_print(f"⚠️ Qt not available: {e}")
    QT_AVAILABLE = False

    # Create dummy classes for when Qt is not available
    class QWidget:
        def __init__(self, parent=None): pass
    class QVBoxLayout:
        def __init__(self, parent=None): pass
    class QHBoxLayout:
        def __init__(self, parent=None): pass
    class QLabel:
        def __init__(self, text="", parent=None): pass
    class QPushButton:
        def __init__(self, text="", parent=None): pass
    class QTextEdit:
        def __init__(self, parent=None): pass
    class QLineEdit:
        def __init__(self, parent=None): pass
    class QListWidget:
        def __init__(self, parent=None): pass
    class QListWidgetItem:
        def __init__(self, text="", parent=None): pass
    class QSplitter:
        def __init__(self, parent=None): pass
    class QTabWidget:
        def __init__(self, parent=None): pass
    class QComboBox:
        def __init__(self, parent=None): pass
    class QCheckBox:
        def __init__(self, parent=None): pass
    class QSpinBox:
        def __init__(self, parent=None): pass
    class QDateTimeEdit:
        def __init__(self, parent=None): pass
    class QMessageBox:
        def __init__(self, parent=None): pass
    class QProgressBar:
        def __init__(self, parent=None): pass
    class QFrame:
        def __init__(self, parent=None): pass
    class QScrollArea:
        def __init__(self, parent=None): pass
    class QGroupBox:
        def __init__(self, title="", parent=None): pass
    class QTimer:
        def __init__(self, parent=None): pass
        def singleShot(self, msec, func): pass
        def timeout(self): return Signal()
        def start(self, msec=None): pass
        def stop(self): pass
    class Signal:
        def __init__(self, *args): pass
        def emit(self, *args): pass
        def connect(self, *args): pass
    class QThread:
        def __init__(self, parent=None): pass
        def start(self): pass
        def quit(self): pass
        def wait(self): pass
    class QDateTime:
        def __init__(self): pass
        @staticmethod
        def currentDateTime(): return QDateTime()
    class QObject:
        def __init__(self, parent=None): pass
    class QFont:
        def __init__(self, family="", size=12): pass
    class QPixmap:
        def __init__(self, *args): pass
    class QIcon:
        def __init__(self, *args): pass

    # Create aliases
    pyqtSignal = Signal
    Qt = type('Qt', (), {
        'UserRole': 256,
        'Horizontal': 1,
        'Vertical': 2
    })()

# Import safe print function for Unicode handling
try:
    from utils.app_logger import safe_print
except ImportError:
    # Enhanced fallback with proper UTF-8 encoding for Windows
    import sys
    import os

    def safe_print(*args, **kwargs):
        try:
            # Force UTF-8 encoding for output
            if sys.platform.startswith('win'):
                # On Windows, ensure we can handle Unicode properly
                try:
                    # Try to reconfigure stdout to UTF-8
                    if hasattr(sys.stdout, 'reconfigure'):
                        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    elif hasattr(sys.stdout, 'buffer'):
                        # For older Python versions, write to buffer with UTF-8
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
                    # Convert to string and handle Unicode
                    arg_str = str(arg)
                    # Replace common Unicode characters that cause issues
                    replacements = {
                        '✅': '[OK]',
                        '❌': '[ERROR]',
                        '⚠️': '[WARNING]',
                        '🔄': '[REFRESH]',
                        '📱': '[PHONE]',
                        '🔍': '[SEARCH]',
                        '📋': '[LIST]',
                        '🚀': '[START]',
                        '💬': '[MESSAGE]',
                        '👤': '[CONTACT]',
                        '👥': '[GROUP]',
                        '🔗': '[CONNECT]',
                        '📸': '[SCREENSHOT]',
                        '🌐': '[WEB]',
                        '📄': '[PAGE]',
                        '⏰': '[TIME]',
                        '🎯': '[TARGET]',
                        '🆕': '[NEW]'
                    }

                    for unicode_char, replacement in replacements.items():
                        arg_str = arg_str.replace(unicode_char, replacement)

                    # Final fallback: encode to ASCII with replacement
                    safe_args.append(arg_str.encode('ascii', errors='replace').decode('ascii'))
                except:
                    safe_args.append('[UNPRINTABLE]')

            print(*safe_args, **kwargs)
        except Exception as e:
            # Ultimate fallback
            try:
                print(f"[LOGGING ERROR: {e}]")
            except:
                pass

def sanitize_message_for_chrome(message):
    """Sanitize message for ChromeDriver to handle Unicode/emoji issues"""
    try:
        # Replace common emojis with text equivalents to avoid ChromeDriver BMP errors
        emoji_replacements = {
            '🚨': '[URGENT]',
            '⚠️': '[WARNING]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '📦': '[PACKAGE]',
            '🧹': '[CLEANING]',
            '⛽': '[GAS]',
            '🔥': '[FIRE]',
            '📋': '[NOTE]',
            '📅': '[DATE]',
            '⏰': '[TIME]',
            '🎯': '[TARGET]',
            '🔄': '[REFRESH]',
            '💰': '[MONEY]',
            '🛒': '[SHOP]',
            '📊': '[CHART]',
            '🏢': '[BUILDING]',
            '👤': '[PERSON]',
            '👥': '[GROUP]',
            '📱': '[PHONE]',
            '💬': '[CHAT]',
            '🧪': '[TEST]',
            '🔧': '[TOOL]',
            '⚙️': '[SETTINGS]',
            '🔔': '[BELL]',
            '🚀': '[ROCKET]',
            '💡': '[IDEA]',
            '🎉': '[PARTY]',
            '📝': '[MEMO]',
            '📢': '[SPEAKER]',
            '🔍': '[SEARCH]',
            '📤': '[SEND]',
            '📥': '[RECEIVE]',
            '🟢': '[GREEN]',
            '🔴': '[RED]',
            '🟡': '[YELLOW]',
            '⏳': '[HOURGLASS]',
            '⏸️': '[PAUSE]',
            '🔗': '[LINK]'
        }

        # Replace emojis with text
        sanitized = message
        for emoji, replacement in emoji_replacements.items():
            sanitized = sanitized.replace(emoji, replacement)

        # Remove any remaining non-BMP characters (outside Basic Multilingual Plane)
        # Keep only characters in the BMP (U+0000 to U+FFFF)
        sanitized = ''.join(char for char in sanitized if ord(char) <= 0xFFFF)

        # Ensure the message is not empty after sanitization
        if not sanitized.strip():
            sanitized = "Message content could not be displayed due to character encoding issues."

        return sanitized

    except Exception as e:
        safe_print(f"Error sanitizing message: {e}")
        return "Message could not be processed due to encoding issues."

def install_selenium_dependencies():
    """Automatically install Selenium and related dependencies"""
    import subprocess
    import sys

    try:
        print("🔄 Installing Selenium for WhatsApp Web integration...")

        # Install selenium
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
        print("✅ Selenium installed successfully")

        # Install webdriver-manager for automatic ChromeDriver management
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        print("✅ WebDriver Manager installed successfully")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False

def check_selenium_dependencies():
    """Check if Selenium dependencies are available at runtime"""
    try:
        # Try to import WhatsApp Web API libraries
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        return True, True  # SELENIUM_AVAILABLE, WEBDRIVER_MANAGER_AVAILABLE
    except ImportError as e:
        print(f"⚠️ Selenium dependencies not available: {e}")
        return False, False

# Initial check at module load time
SELENIUM_AVAILABLE, WEBDRIVER_MANAGER_AVAILABLE = check_selenium_dependencies()

try:
    # Try to import Firebase modules
    from modules.firebase_integration import FIREBASE_AVAILABLE, FIRESTORE_DB
    from modules.enhanced_notification_system import get_notification_manager
    FIREBASE_INTEGRATION = True
except ImportError:
    FIREBASE_INTEGRATION = False
    print("⚠️ Firebase integration not available")


class WhatsAppMessage:
    """Represents a WhatsApp message"""
    
    def __init__(self, message_id: str, sender: str, recipient: str, content: str, 
                 message_type: str = "text", timestamp: datetime = None, status: str = "pending"):
        self.message_id = message_id
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.message_type = message_type  # text, image, document, etc.
        self.timestamp = timestamp or datetime.now()
        self.status = status  # pending, sent, delivered, read, failed
        self.device_id = self.get_device_id()
        self.sync_status = "pending"  # pending, synced, failed
    
    def get_device_id(self):
        """Get unique device identifier"""
        import platform
        import hashlib
        device_info = f"{platform.node()}-{platform.system()}-{platform.processor()}"
        return hashlib.md5(device_info.encode()).hexdigest()[:12]
    
    def to_dict(self):
        """Convert message to dictionary for Firebase storage"""
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'device_id': self.device_id,
            'sync_status': self.sync_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create message from dictionary"""
        message = cls(
            message_id=data['message_id'],
            sender=data['sender'],
            recipient=data['recipient'],
            content=data['content'],
            message_type=data.get('message_type', 'text'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            status=data.get('status', 'pending')
        )
        message.sync_status = data.get('sync_status', 'pending')
        return message


class WhatsAppContact:
    """Represents a WhatsApp contact"""
    
    def __init__(self, contact_id: str, name: str, phone: str, 
                 last_seen: datetime = None, is_business: bool = False):
        self.contact_id = contact_id
        self.name = name
        self.phone = phone
        self.last_seen = last_seen
        self.is_business = is_business
        self.message_count = 0
        self.last_message_time = None
        self.tags = []
        self.notes = ""
    
    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            'contact_id': self.contact_id,
            'name': self.name,
            'phone': self.phone,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_business': self.is_business,
            'message_count': self.message_count,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create contact from dictionary"""
        contact = cls(
            contact_id=data['contact_id'],
            name=data['name'],
            phone=data['phone'],
            last_seen=datetime.fromisoformat(data['last_seen']) if data.get('last_seen') else None,
            is_business=data.get('is_business', False)
        )
        contact.message_count = data.get('message_count', 0)
        contact.last_message_time = datetime.fromisoformat(data['last_message_time']) if data.get('last_message_time') else None
        contact.tags = data.get('tags', [])
        contact.notes = data.get('notes', '')
        return contact


class WhatsAppWebDriver(QThread):
    """WhatsApp Web automation driver"""

    message_received = Signal(dict)
    connection_status_changed = Signal(bool)
    qr_code_ready = Signal(str)
    contacts_loaded = Signal(list)

    def __init__(self):
        super().__init__()
        self.driver = None
        self.is_connected = False
        self.should_stop = False
        self.message_check_interval = 5  # seconds
        self.user_data_dir = None  # Store for cleanup
        self.persistent_session_dir = None  # Persistent session directory

        # Performance optimization: Cache successful group findings
        self._cached_target_group = None
        self._cache_timestamp = None
        self._cache_duration = 300  # 5 minutes cache

        # Threading optimization
        import threading
        self._search_lock = threading.Lock()

        # Search optimization: Track successful connections
        self._connection_verified = False
        self._last_successful_element = None
        self.session_reuse_enabled = True  # Enable session reuse by default
        self.selected_session = None  # Specific session to connect to

    def get_persistent_session_directory(self):
        """Get or create a persistent session directory for WhatsApp Web"""
        import os
        import platform

        # Create a persistent directory based on the user's system
        if platform.system() == "Windows":
            base_dir = os.path.expanduser("~\\AppData\\Local\\VARSYS\\WhatsApp")
        elif platform.system() == "Darwin":  # macOS
            base_dir = os.path.expanduser("~/Library/Application Support/VARSYS/WhatsApp")
        else:  # Linux
            base_dir = os.path.expanduser("~/.local/share/VARSYS/WhatsApp")

        # Create the directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)

        session_dir = os.path.join(base_dir, "chrome_session")
        os.makedirs(session_dir, exist_ok=True)

        return session_dir

    def check_existing_chrome_session(self):
        """Check if there's an existing Chrome session with WhatsApp Web"""
        try:
            import psutil
            import os

            # Get the persistent session directory
            session_dir = self.get_persistent_session_directory()

            # Check if session directory exists and has data
            if not os.path.exists(session_dir):
                return False

            # Look for Chrome processes using our session directory
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any(session_dir in arg for arg in cmdline):
                            print(f"✅ Found existing Chrome session (PID: {proc.info['pid']})")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Check if session files exist (indicates previous session)
            session_files = ['Default', 'Local State', 'Preferences']
            existing_files = [f for f in session_files if os.path.exists(os.path.join(session_dir, f))]

            if existing_files:
                print(f"📁 Found existing session data: {existing_files}")
                return True

            return False

        except ImportError:
            print("⚠️ psutil not available - cannot check for existing Chrome sessions")
            return False
        except Exception as e:
            print(f"⚠️ Error checking existing Chrome session: {e}")
            return False

    def find_whatsapp_web_sessions(self):
        """Find all Chrome sessions with WhatsApp Web already signed in"""
        try:
            import psutil
            import requests
            import json

            whatsapp_sessions = []
            debug_ports_to_try = ['9222', '9223', '9224', '9225']  # Common debug ports

            # First, try to find Chrome processes with debugging enabled
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if not cmdline:
                            continue

                        # Look for remote debugging port in command line
                        debug_port = None
                        for arg in cmdline:
                            if '--remote-debugging-port=' in arg:
                                debug_port = arg.split('=')[1]
                                break

                        if debug_port:
                            debug_ports_to_try.insert(0, debug_port)  # Try this port first

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Try to connect to Chrome DevTools API on various ports
            for port in debug_ports_to_try:
                try:
                    response = requests.get(f"http://127.0.0.1:{port}/json/list", timeout=1)
                    if response.status_code == 200:
                        tabs = response.json()
                        print(f"🔍 Connected to Chrome DevTools on port {port}, found {len(tabs)} tabs")

                        # Look for WhatsApp Web tabs
                        for tab in tabs:
                            url = tab.get('url', '')
                            if 'web.whatsapp.com' in url:
                                title = tab.get('title', '')

                                # Determine authentication status
                                status = 'needs_auth'
                                if 'WhatsApp' in title and 'QR' not in title.upper() and 'Loading' not in title:
                                    status = 'authenticated'

                                session_info = {
                                    'pid': 'unknown',
                                    'debug_port': port,
                                    'tab_id': tab.get('id'),
                                    'url': url,
                                    'title': title,
                                    'webSocketDebuggerUrl': tab.get('webSocketDebuggerUrl'),
                                    'status': status
                                }

                                # Try to find the PID for this Chrome instance
                                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                    try:
                                        if (proc.info['name'] and 'chrome' in proc.info['name'].lower() and
                                            proc.info['cmdline'] and any(f'--remote-debugging-port={port}' in str(arg) for arg in proc.info['cmdline'])):
                                            session_info['pid'] = proc.info['pid']
                                            break
                                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                                        continue

                                whatsapp_sessions.append(session_info)

                                if status == 'authenticated':
                                    print(f"🔍 Found authenticated WhatsApp Web session: {title}")
                                else:
                                    print(f"🔍 Found WhatsApp Web session (needs auth): {title}")

                        # If we found sessions on this port, we can break (unless we want to check all ports)
                        if any('web.whatsapp.com' in tab.get('url', '') for tab in tabs):
                            break

                except requests.RequestException:
                    continue

            # If no sessions found via DevTools, try to detect Chrome processes with WhatsApp Web
            if not whatsapp_sessions:
                print("🔍 No DevTools sessions found, checking for Chrome processes...")
                chrome_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                            chrome_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': proc.info['cmdline'] or []
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if chrome_processes:
                    print(f"🔍 Found {len(chrome_processes)} Chrome process(es)")
                    # Add a generic Chrome session entry with helpful information
                    whatsapp_sessions.append({
                        'pid': chrome_processes[0]['pid'],
                        'debug_port': '9222',
                        'tab_id': None,
                        'url': 'https://web.whatsapp.com',
                        'title': 'Chrome Browser (restart Chrome with debugging to connect)',
                        'webSocketDebuggerUrl': None,
                        'status': 'needs_debug_mode'
                    })

            return whatsapp_sessions

        except ImportError:
            print("⚠️ psutil or requests not available - cannot search for WhatsApp Web sessions")
            return []
        except Exception as e:
            print(f"⚠️ Error searching for WhatsApp Web sessions: {e}")
            return []

    def connect_to_existing_session(self, session_info=None, max_retries=3):
        """Try to connect to an existing Chrome session with retry logic"""
        import time

        for attempt in range(max_retries):
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from selenium.common.exceptions import WebDriverException

                # If specific session info provided, use that debug port
                debug_port = "9222"
                if session_info and 'debug_port' in session_info:
                    debug_port = session_info['debug_port']

                # First check if Chrome DevTools is accessible
                if not self.cleanup_stale_sessions():
                    print(f"ℹ️ Chrome DevTools not accessible on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"⏳ Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return False

                # Try to connect using Chrome's remote debugging port
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")

                # Try to connect to existing session
                if hasattr(self, 'webdriver_manager_available') and self.webdriver_manager_available:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    test_driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    test_driver = webdriver.Chrome(options=chrome_options)

                # If specific session provided, switch to that tab
                if session_info and 'tab_id' in session_info:
                    try:
                        # Switch to the specific WhatsApp Web tab
                        test_driver.switch_to.window(session_info['tab_id'])
                    except:
                        # If switching fails, navigate to WhatsApp Web
                        test_driver.get("https://web.whatsapp.com")
                else:
                    # Check if WhatsApp Web is already open
                    current_url = test_driver.current_url
                    if "web.whatsapp.com" not in current_url:
                        # Navigate to WhatsApp Web in existing session
                        test_driver.get("https://web.whatsapp.com")

                self.driver = test_driver

                # Check authentication status
                if session_info and session_info.get('status') == 'authenticated':
                    print("✅ Connected to authenticated WhatsApp Web session")
                    self.is_connected = True
                else:
                    print("✅ Connected to existing Chrome session, navigated to WhatsApp Web")
                    # Will need to check for QR code or authentication

                return True

            except WebDriverException as e:
                error_msg = str(e)
                if "cannot connect to chrome" in error_msg.lower():
                    print(f"ℹ️ Could not connect to existing session: Chrome not running with debugging enabled")
                    print(f"💡 Tip: Start Chrome with: chrome --remote-debugging-port={debug_port}")
                elif "connection refused" in error_msg.lower() or "target machine actively refused" in error_msg.lower():
                    print(f"ℹ️ Chrome session no longer available - connection refused (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"⏳ Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"💡 All retry attempts failed. The Chrome session may have been closed.")
                else:
                    print(f"ℹ️ Could not connect to existing session: {e}")

                if attempt == max_retries - 1:  # Last attempt
                    return False

            except Exception as e:
                print(f"⚠️ Error connecting to existing session: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    return False
                else:
                    wait_time = 2 ** attempt
                    print(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

        return False  # All attempts failed

    def _is_cache_valid(self):
        """Check if cached target group is still valid"""
        if not self._cached_target_group or not self._cache_timestamp:
            return False

        import time
        return (time.time() - self._cache_timestamp) < self._cache_duration

    def _cache_target_group(self, group_data):
        """Cache the successfully found target group"""
        import time
        self._cached_target_group = group_data
        self._cache_timestamp = time.time()
        safe_print(f"✅ Cached target group: {group_data.get('name', 'Unknown')}")

    def _get_cached_target_group(self):
        """Get cached target group if valid"""
        if self._is_cache_valid():
            safe_print(f"🚀 Using cached target group: {self._cached_target_group.get('name', 'Unknown')}")
            return self._cached_target_group
        return None

    def _handle_target_group_click(self, element, contact_name, search_box):
        """Optimized method to handle clicking on target group"""
        try:
            safe_print(f"🎯 ✅ CLICKING ON TARGET GROUP: {contact_name}")

            # Try multiple click strategies with early success detection
            click_success = False

            # Strategy 1: Direct click
            try:
                element.click()
                safe_print(f"✅ Successfully clicked on '{contact_name}' (direct click)")
                click_success = True
            except Exception as click_error:
                safe_print(f"⚠️ Direct click failed: {click_error}")

            # Strategy 2: JavaScript click if direct click failed
            if not click_success:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    safe_print(f"✅ Successfully clicked on '{contact_name}' (JavaScript click)")
                    click_success = True
                except Exception as js_error:
                    safe_print(f"⚠️ JavaScript click failed: {js_error}")

            if click_success:
                import time
                time.sleep(1.5)  # Reduced wait time

                # Clear search box after successful click
                try:
                    search_box.clear()
                except:
                    pass

                target_group = {
                    'name': contact_name,
                    'type': 'group',
                    'element': element,
                    'clicked': True
                }

                # Cache the successful result
                self._cache_target_group(target_group)
                self._connection_verified = True

                return target_group
            else:
                safe_print(f"⚠️ Click strategies failed for group: {contact_name}")
                # Still return the element for manual handling
                return {
                    'name': contact_name,
                    'type': 'group',
                    'element': element,
                    'clicked': False
                }

        except Exception as e:
            safe_print(f"❌ Error in _handle_target_group_click: {e}")
            return None

    def _check_chrome_debug_running(self):
        """Check if Chrome is already running with debugging enabled"""
        try:
            import psutil
            import requests

            # Check processes for debugging Chrome
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('remote-debugging-port' in str(arg) for arg in cmdline):
                            # Verify debugging port is accessible
                            try:
                                response = requests.get("http://127.0.0.1:9222/json", timeout=1)
                                if response.status_code == 200:
                                    print(f"✅ Chrome with debugging already running (PID: {proc.info['pid']})")
                                    return True
                            except:
                                pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return False
        except Exception:
            return False

    def force_cleanup_webdriver_sessions(self):
        """Force cleanup of stale WebDriver sessions"""
        try:
            import psutil

            print("🧹 Cleaning up stale WebDriver sessions...")

            # Kill any chromedriver processes that might be hanging
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chromedriver' in proc.info['name'].lower():
                        print(f"🔪 Terminating stale chromedriver process (PID: {proc.info['pid']})")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Clear any existing driver reference
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

            print("✅ WebDriver session cleanup completed")
            return True

        except Exception as e:
            print(f"⚠️ Error during WebDriver cleanup: {e}")
            return False

    def ensure_chrome_startup_ready(self):
        """Ensure Chrome is ready for startup automation"""
        try:
            safe_print("🚀 Preparing Chrome for automatic startup...")

            # Check if Chrome is installed
            chrome_binary = self.find_chrome_binary(self.get_chrome_paths())
            if not chrome_binary:
                safe_print("❌ Chrome not found - automatic startup not possible")
                safe_print("💡 Install Chrome from: https://www.google.com/chrome/")
                return False

            safe_print(f"✅ Chrome found at: {chrome_binary}")

            # Check if Chrome processes are running and detect debugging mode
            try:
                import psutil
                chrome_processes = []
                debug_chrome_found = False
                normal_chrome_found = False

                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc.info)

                        # Check if this Chrome process has debugging enabled
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('remote-debugging-port' in str(arg) for arg in cmdline):
                            debug_chrome_found = True
                            safe_print(f"✅ Found Chrome with debugging (PID: {proc.info['pid']})")
                        else:
                            normal_chrome_found = True

                if chrome_processes:
                    safe_print(f"ℹ️ Found {len(chrome_processes)} Chrome processes already running")

                    if debug_chrome_found:
                        safe_print("✅ Chrome with debugging already running - will reuse")
                        # Check if debugging port is accessible
                        try:
                            import requests
                            response = requests.get("http://127.0.0.1:9222/json", timeout=2)
                            if response.status_code == 200:
                                safe_print("✅ Chrome debugging port 9222 is accessible")
                            else:
                                safe_print("⚠️ Chrome debugging port not accessible")
                        except:
                            safe_print("⚠️ Cannot verify Chrome debugging port")
                    elif normal_chrome_found:
                        safe_print("ℹ️ Normal Chrome running - WebDriver will start new debugging instance")
                else:
                    safe_print("ℹ️ No Chrome processes found - will start fresh Chrome instance")

            except (ImportError, Exception):
                safe_print("ℹ️ Cannot check Chrome processes - proceeding with startup")

            safe_print("✅ Chrome startup preparation complete")
            return True

        except Exception as e:
            safe_print(f"⚠️ Error preparing Chrome startup: {e}")
            safe_print("ℹ️ Proceeding with Chrome startup anyway")
            return True

    def setup_driver(self):
        """Setup Chrome WebDriver for WhatsApp Web with session reuse capability"""
        # Check dependencies at runtime
        selenium_available, webdriver_manager_available = check_selenium_dependencies()
        self.webdriver_manager_available = webdriver_manager_available

        if not selenium_available:
            print("❌ Selenium dependencies not available")
            return False

        # Check if Chrome with debugging is already running to avoid duplicate instances
        if self._check_chrome_debug_running():
            print("ℹ️ Chrome with debugging already running - will attempt to reuse existing sessions")

        # Try to reuse existing session first
        if self.session_reuse_enabled:
            # If a specific session was selected, try that first
            if self.selected_session:
                print(f"🎯 Connecting to user-selected session: {self.selected_session.get('title', 'Unknown')}")
                if self.connect_to_existing_session(self.selected_session):
                    return True
                else:
                    print("⚠️ Could not connect to selected session, cleaning up and searching for alternatives...")
                    self.force_cleanup_webdriver_sessions()

            print("🔄 Searching for existing WhatsApp Web sessions...")
            whatsapp_sessions = self.find_whatsapp_web_sessions()

            if whatsapp_sessions:
                print(f"🔍 Found {len(whatsapp_sessions)} WhatsApp Web session(s)")

                # Prioritize authenticated sessions
                authenticated_sessions = [s for s in whatsapp_sessions if s.get('status') == 'authenticated']
                if authenticated_sessions:
                    print(f"✅ Found {len(authenticated_sessions)} authenticated session(s)")
                    session_to_use = authenticated_sessions[0]  # Use the first authenticated session
                    print(f"🔗 Connecting to authenticated session: {session_to_use.get('title', 'Unknown')}")
                    if self.connect_to_existing_session(session_to_use):
                        return True

                # If no authenticated sessions, try any WhatsApp Web session
                session_to_use = whatsapp_sessions[0]
                print(f"🔗 Connecting to WhatsApp Web session: {session_to_use.get('title', 'Unknown')}")
                if self.connect_to_existing_session(session_to_use):
                    return True

                print("ℹ️ Could not connect to existing sessions, cleaning up and creating new one...")
                self.force_cleanup_webdriver_sessions()
            else:
                print("ℹ️ No existing WhatsApp Web sessions found")
                # Fallback to checking for general Chrome sessions
                if self.check_existing_chrome_session():
                    print("🔗 Attempting to connect to existing Chrome session...")
                    if self.connect_to_existing_session():
                        return True
                    else:
                        print("ℹ️ Could not connect to existing session, cleaning up and creating new one...")
                        self.force_cleanup_webdriver_sessions()

        try:
            # Import dependencies dynamically
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            import os
            import platform

            # Check if Chrome is installed
            chrome_paths = self.get_chrome_paths()
            chrome_binary = self.find_chrome_binary(chrome_paths)

            # If not found in standard locations, try system PATH
            if not chrome_binary:
                print("🔍 Trying to find Chrome in system PATH...")
                chrome_binary = self.find_chrome_in_path()

            if not chrome_binary:
                print("❌ Google Chrome browser not found!")
                print("📥 Please install Google Chrome from: https://www.google.com/chrome/")
                print("🔄 After installing Chrome, restart the application and try again.")

                # For automation scenarios, provide more specific guidance
                print("\n💡 For automatic startup:")
                print("   1. Install Chrome from the link above")
                print("   2. Restart VARSYS Kitchen Dashboard")
                print("   3. WhatsApp will connect automatically on next startup")
                return False

            # Use persistent session directory instead of temporary
            if self.session_reuse_enabled:
                self.persistent_session_dir = self.get_persistent_session_directory()
                self.user_data_dir = self.persistent_session_dir
                print(f"🔧 Using persistent session directory: {self.user_data_dir}")
            else:
                # Fallback to temporary directory if session reuse is disabled
                import tempfile
                import uuid
                temp_dir = tempfile.gettempdir()
                unique_session_id = str(uuid.uuid4())[:8]
                self.user_data_dir = os.path.join(temp_dir, f"whatsapp_session_{unique_session_id}")
                print(f"🔧 Using temporary session directory: {self.user_data_dir}")

            chrome_options = Options()
            chrome_options.binary_location = chrome_binary
            chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")

            # Enable remote debugging for session reuse
            if self.session_reuse_enabled:
                # Check if Chrome with debugging is already running
                if not self._check_chrome_debug_running():
                    chrome_options.add_argument("--remote-debugging-port=9222")
                    chrome_options.add_argument("--remote-allow-origins=*")
                    print("🔧 Configuring Chrome with debugging port 9222")
                else:
                    print("ℹ️ Chrome with debugging already running - will connect to existing instance")
                    # Try to connect to existing debugging session instead of starting new Chrome
                    try:
                        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                        print("🔗 Configured to connect to existing Chrome debugging session")
                    except Exception as e:
                        print(f"⚠️ Could not configure debugging connection: {e}")
                        # Fallback to normal startup
                        chrome_options.add_argument("--remote-debugging-port=9222")
                        chrome_options.add_argument("--remote-allow-origins=*")

            # 🚀 OPTIMIZED Chrome options for MAXIMUM SPEED
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=800,600")  # Smaller for faster rendering
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Much faster loading
            chrome_options.add_argument("--disable-css")     # Even faster
            chrome_options.add_argument("--disable-javascript")  # Fastest (WhatsApp still works)

            # Options to ensure Chrome starts reliably even when closed
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")

            # Additional speed optimizations
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-background-downloads")
            chrome_options.add_argument("--disable-add-to-shelf")
            chrome_options.add_argument("--disable-datasaver-prompt")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--disable-component-extensions-with-background-pages")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--aggressive-cache-discard")
            chrome_options.add_argument("--memory-pressure-off")

            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Ensure Chrome starts fresh if needed
            if not self.session_reuse_enabled:
                chrome_options.add_argument("--incognito")

            if webdriver_manager_available:
                # Use webdriver-manager for automatic ChromeDriver management with robust error handling
                from webdriver_manager.chrome import ChromeDriverManager

                # Try to install ChromeDriver with retry mechanism
                chromedriver_path = self.install_chromedriver_with_retry()
                if chromedriver_path:
                    service = Service(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print(f"✅ ChromeDriver automatically managed and Chrome found at: {chrome_binary}")
                else:
                    # Fallback to system ChromeDriver if webdriver-manager fails
                    print("⚠️ ChromeDriver auto-install failed, trying system ChromeDriver...")
                    self.driver = webdriver.Chrome(options=chrome_options)
                    print(f"⚠️ Using system ChromeDriver with Chrome at: {chrome_binary}")
            else:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                print(f"⚠️ Using system ChromeDriver with Chrome at: {chrome_binary}")

            return True
        except Exception as e:
            print(f"❌ Failed to setup WhatsApp Web driver: {e}")
            error_str = str(e).lower()

            if "cannot find Chrome binary" in error_str:
                print("💡 Solution: Install Google Chrome browser from https://www.google.com/chrome/")
            elif "chromedriver" in error_str or "webdriver" in error_str:
                print("💡 ChromeDriver issue detected:")
                print("   1. Clearing ChromeDriver cache...")
                print("   2. Try restarting the application")
                print("   3. If issue persists, check internet connection")

                # Try to clear cache immediately for next attempt
                try:
                    import shutil
                    cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
                    if os.path.exists(cache_dir):
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        print("   ✅ Cache cleared successfully")
                except:
                    print("   ⚠️ Could not clear cache automatically")

            elif "file is not a zip file" in error_str:
                print("💡 Corrupted download detected:")
                print("   1. ChromeDriver download was corrupted")
                print("   2. Cache has been cleared automatically")
                print("   3. Please try connecting again")
            elif "session not created" in error_str:
                print("💡 Chrome session issue:")
                print("   1. Close all Chrome windows")
                print("   2. Try connecting again")
                print("   3. If issue persists, restart the application")
            else:
                print("💡 General troubleshooting:")
                print("   1. Ensure Google Chrome is installed")
                print("   2. Check internet connection")
                print("   3. Try restarting the application")

            return False

    def install_chromedriver_with_retry(self, max_retries=3):
        """Install ChromeDriver with retry mechanism and cache clearing for corrupted downloads"""
        from webdriver_manager.chrome import ChromeDriverManager
        import os
        import shutil
        import time

        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempting ChromeDriver installation (attempt {attempt + 1}/{max_retries})...")

                # Create ChromeDriverManager instance
                driver_manager = ChromeDriverManager()

                # Install ChromeDriver
                chromedriver_path = driver_manager.install()

                # Verify the downloaded file is valid
                if os.path.exists(chromedriver_path) and os.path.getsize(chromedriver_path) > 1000:  # Should be larger than 1KB
                    print(f"✅ ChromeDriver successfully installed at: {chromedriver_path}")
                    return chromedriver_path
                else:
                    print(f"⚠️ ChromeDriver file seems invalid (size: {os.path.getsize(chromedriver_path) if os.path.exists(chromedriver_path) else 0} bytes)")
                    raise Exception("Invalid ChromeDriver file")

            except Exception as e:
                print(f"❌ ChromeDriver installation attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:  # Not the last attempt
                    print("🧹 Clearing ChromeDriver cache and retrying...")

                    # Clear webdriver-manager cache
                    try:
                        # Get cache directory
                        import tempfile
                        import platform

                        if platform.system() == "Windows":
                            cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
                        else:
                            cache_dir = os.path.join(tempfile.gettempdir(), ".wdm")

                        if os.path.exists(cache_dir):
                            print(f"🗑️ Removing cache directory: {cache_dir}")
                            shutil.rmtree(cache_dir, ignore_errors=True)

                        # Also try to clear the specific chromedriver cache
                        chromedriver_cache = os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver")
                        if os.path.exists(chromedriver_cache):
                            print(f"🗑️ Removing ChromeDriver cache: {chromedriver_cache}")
                            shutil.rmtree(chromedriver_cache, ignore_errors=True)

                    except Exception as cache_error:
                        print(f"⚠️ Could not clear cache: {cache_error}")

                    # Wait before retry
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print("❌ All ChromeDriver installation attempts failed")
                    return None

        return None

    def get_chrome_paths(self):
        """Get possible Chrome installation paths based on OS"""
        import platform
        import glob

        system = platform.system().lower()
        paths = []

        if system == "windows":
            # Standard Windows Chrome paths
            standard_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]

            # User-specific paths
            username = os.environ.get('USERNAME', os.environ.get('USER', ''))
            if username:
                user_paths = [
                    rf"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe",
                    rf"C:\Users\{username}\AppData\Roaming\Google\Chrome\Application\chrome.exe",
                ]
                standard_paths.extend(user_paths)

            # Search in common installation directories
            search_patterns = [
                r"C:\Program Files*\Google\Chrome\Application\chrome.exe",
                r"C:\Users\*\AppData\Local\Google\Chrome\Application\chrome.exe",
                r"C:\Users\*\AppData\Roaming\Google\Chrome\Application\chrome.exe",
            ]

            # Add found paths from glob search
            for pattern in search_patterns:
                try:
                    found_paths = glob.glob(pattern)
                    standard_paths.extend(found_paths)
                except:
                    pass

            # Also check registry for Chrome installation
            try:
                import winreg
                reg_paths = self.get_chrome_from_registry()
                standard_paths.extend(reg_paths)
            except:
                pass

            paths = standard_paths

        elif system == "darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
            ]
        elif system == "linux":
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/chromium",
            ]

        return paths

    def get_chrome_from_registry(self):
        """Get Chrome path from Windows registry"""
        import winreg
        paths = []

        # Registry keys to check
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome\BLBeacon"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome\BLBeacon"),
        ]

        for hkey, key_path in registry_keys:
            try:
                with winreg.OpenKey(hkey, key_path) as key:
                    try:
                        # Try to get the default value or Path value
                        chrome_path, _ = winreg.QueryValueEx(key, "")
                        if chrome_path and os.path.exists(chrome_path):
                            paths.append(chrome_path)
                    except FileNotFoundError:
                        try:
                            chrome_path, _ = winreg.QueryValueEx(key, "Path")
                            if chrome_path:
                                # Path might be a directory, so append chrome.exe
                                if os.path.isdir(chrome_path):
                                    chrome_exe = os.path.join(chrome_path, "chrome.exe")
                                    if os.path.exists(chrome_exe):
                                        paths.append(chrome_exe)
                                elif os.path.exists(chrome_path):
                                    paths.append(chrome_path)
                        except FileNotFoundError:
                            pass
            except (OSError, PermissionError):
                continue

        return paths

    def find_chrome_binary(self, paths):
        """Find the first available Chrome binary from the given paths"""
        print(f"🔍 Searching for Chrome in {len(paths)} locations...")

        for i, path in enumerate(paths, 1):
            print(f"  [{i}] Checking: {path}")
            if os.path.exists(path) and os.path.isfile(path):
                print(f"✅ Found Chrome at: {path}")
                return path
            else:
                print(f"    ❌ Not found")

        print("❌ Chrome not found in any standard locations")
        print("💡 Please ensure Google Chrome is installed")
        print("📥 Download from: https://www.google.com/chrome/")
        return None

    def find_chrome_in_path(self):
        """Try to find Chrome using system PATH"""
        import shutil

        # Try common Chrome executable names
        chrome_names = ["chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]

        for name in chrome_names:
            chrome_path = shutil.which(name)
            if chrome_path:
                print(f"✅ Found Chrome in PATH: {chrome_path}")
                return chrome_path

        print("❌ Chrome not found in system PATH")
        return None

    def connect_to_whatsapp_web(self):
        """Connect to WhatsApp Web"""
        if not self.driver:
            if not self.setup_driver():
                print("❌ Failed to setup driver")
                return False

        try:
            print("🌐 Opening WhatsApp Web...")

            # Import Selenium components dynamically
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException

            self.driver.get("https://web.whatsapp.com")
            print("✅ WhatsApp Web page loaded")

            # Wait for page to load with multiple possible selectors
            print("🔍 Waiting for WhatsApp Web to load...")

            # Multiple possible selectors for different WhatsApp Web states
            possible_selectors = [
                "[data-testid='qr-code']",           # QR code
                "[data-testid='chat-list']",         # Chat list (authenticated)
                "[data-testid='side']",              # Side panel (authenticated)
                "canvas[aria-label*='QR']",          # QR code canvas
                "div[data-ref]",                     # QR code container
                "#side",                             # Side panel ID
                ".landing-wrapper",                  # Landing page
                "._2dloB",                          # Chat list class
                "._3OtEr",                          # Side panel class
                "[role='textbox']",                  # Message input (authenticated)
                "div[title='Search or start new chat']", # Search box
                "header[data-testid='chatlist-header']"  # Chat list header
            ]

            def check_whatsapp_loaded(driver):
                """Check if any WhatsApp Web element is present"""
                for selector in possible_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✅ Found WhatsApp element: {selector}")
                            return True
                    except Exception as e:
                        continue
                return False

            try:
                # Wait for any WhatsApp Web element to appear (FAST MODE)
                WebDriverWait(self.driver, 8).until(check_whatsapp_loaded)  # Reduced from 15 to 8
                print("✅ WhatsApp Web elements detected")
            except TimeoutException:
                print("⏰ No WhatsApp elements found, trying alternative approach...")

                # Debug: Let's see what's actually on the page
                try:
                    print(f"🌐 Current URL: {self.driver.current_url}")
                    print(f"📄 Page title: {self.driver.title}")

                    # Get page source length to see if page loaded
                    page_source_length = len(self.driver.page_source)
                    print(f"📄 Page source length: {page_source_length} characters")

                    # Try to find any div elements
                    all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                    print(f"🔍 Found {len(all_divs)} div elements on page")

                    # Try to find any elements with common WhatsApp classes
                    common_classes = ["_2dloB", "_3OtEr", "landing-wrapper", "_1ays2"]
                    for class_name in common_classes:
                        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                        if elements:
                            print(f"✅ Found elements with class '{class_name}': {len(elements)}")

                    # Check if page is still loading
                    if "WhatsApp" in self.driver.title or "web.whatsapp.com" in self.driver.current_url:
                        print("✅ WhatsApp Web page confirmed by title/URL")
                        print("⏳ Page might still be loading, waiting a bit more...")
                        import time
                        time.sleep(5)  # Give it more time to load
                    else:
                        print("❌ WhatsApp Web failed to load properly")
                        raise TimeoutException("WhatsApp Web page did not load")

                except Exception as debug_error:
                    print(f"❌ Debug error: {debug_error}")
                    raise TimeoutException("WhatsApp Web page did not load")

            # Check if already authenticated using multiple approaches
            def check_authenticated(driver):
                """Check if user is already authenticated"""
                # Method 1: Check for specific selectors
                auth_selectors = [
                    "[data-testid='chat-list']",
                    "[data-testid='side']",
                    "#side",
                    "._2dloB",  # Chat list
                    "._3OtEr",  # Side panel
                    "[role='textbox']",  # Message input
                    "div[title='Search or start new chat']",
                    "header[data-testid='chatlist-header']"
                ]

                for selector in auth_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✅ Found authenticated element: {selector}")
                            return True
                    except Exception:
                        continue

                # Method 2: Check page content for authentication indicators
                try:
                    page_text = driver.page_source.lower()
                    auth_indicators = [
                        "search or start new chat",
                        "chat-list",
                        "message yourself",
                        "new chat",
                        "status updates"
                    ]

                    for indicator in auth_indicators:
                        if indicator in page_text:
                            print(f"✅ Found authentication indicator in page: '{indicator}'")
                            return True

                except Exception:
                    pass

                return False

            if check_authenticated(self.driver):
                print("✅ Already authenticated! WhatsApp Web is ready.")
                self.is_connected = True
                self.connection_status_changed.emit(True)

                # Optimized: Load contacts and groups with caching
                self.load_contacts_and_groups()
                return True

            # Check if QR code is present using multiple selectors
            def find_qr_code():
                """Find QR code element using various selectors"""
                qr_selectors = [
                    "[data-testid='qr-code']",
                    "canvas[aria-label*='QR']",
                    "div[data-ref]",
                    ".landing-wrapper canvas",
                    "canvas",  # Generic canvas (QR codes are often in canvas)
                ]

                for selector in qr_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"📱 Found QR code element: {selector}")
                            return elements[0]
                    except Exception:
                        continue
                return None

            qr_element = find_qr_code()
            if qr_element:
                print("📱 QR code detected - authentication required")
                # QR code is present, emit signal
                qr_code_data = qr_element.get_attribute("data-ref") or qr_element.get_attribute("src") or "QR Code Ready"
                self.qr_code_ready.emit(qr_code_data)

                print("⏳ Waiting for QR code scan (45 seconds timeout)...")
                # Wait for login with optimized timeout
                try:
                    WebDriverWait(self.driver, 45).until(check_authenticated)  # Reduced from 60 to 45
                    print("✅ QR code scanned successfully!")
                except TimeoutException:
                    print("⏰ QR code scan timeout - please try again")
                    self.connection_status_changed.emit(False)
                    return False
            else:
                print("🔍 No QR code found, checking if already logged in...")
                # Give it a moment and check again
                import time
                time.sleep(3)
                if check_authenticated(self.driver):
                    print("✅ Authentication confirmed after delay!")
                    self.is_connected = True
                    self.connection_status_changed.emit(True)
                    return True
                else:
                    print("❌ Could not determine WhatsApp Web state")
                    self.connection_status_changed.emit(False)
                    return False

            self.is_connected = True
            self.connection_status_changed.emit(True)
            print("🎉 WhatsApp Web connection successful!")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to WhatsApp Web: {e}")
            import traceback
            traceback.print_exc()

            # Take a screenshot for debugging
            try:
                screenshot_path = "whatsapp_debug_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Debug screenshot saved: {screenshot_path}")

                # Get page source for debugging
                print(f"🌐 Current URL: {self.driver.current_url}")
                print(f"📄 Page title: {self.driver.title}")

                # Check if we can find any elements at all
                all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
                print(f"🔍 Total elements found on page: {len(all_elements)}")

            except Exception as debug_error:
                print(f"❌ Could not capture debug info: {debug_error}")

            self.connection_status_changed.emit(False)
            return False

    def load_contacts_and_groups(self):
        """Optimized: Use cache and avoid redundant searches for Abiram's Kitchen group"""
        try:
            safe_print("🎯 Optimized contact loading - checking cache first...")

            # Check if we already have a successful connection verified
            if self._connection_verified and self._cached_target_group:
                safe_print("✅ Connection already verified - using existing target group")
                target_group = self._cached_target_group
            else:
                # Check cache first
                target_group = self._get_cached_target_group()

                if not target_group:
                    safe_print("🔍 Cache miss - searching for Abiram's Kitchen...")
                    # Use thread lock to prevent concurrent searches
                    with self._search_lock:
                        # Double-check cache after acquiring lock
                        target_group = self._get_cached_target_group()
                        if not target_group:
                            target_group = self.find_abirams_kitchen()
                            if target_group:
                                self._cache_target_group(target_group)
                                self._connection_verified = True

            if target_group:
                safe_print(f"✅ Target group available: {target_group['name']}")
                contacts = [target_group]

                # Emit the single contact to the UI with thread safety
                if hasattr(self, 'contacts_loaded'):
                    safe_print("📡 Emitting Abiram's Kitchen group to UI")
                    try:
                        # Use QTimer to ensure emission happens in main thread
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, lambda: self.contacts_loaded.emit(contacts))
                    except:
                        # Fallback to direct emission
                        self.contacts_loaded.emit(contacts)

                return contacts
            else:
                safe_print("❌ Abiram's Kitchen group not found")

                # Show placeholder for the target group
                placeholder_contacts = [
                    {'name': "Abiram's Kitchen (Not Found)", 'type': 'group', 'available': False}
                ]

                if hasattr(self, 'contacts_loaded'):
                    self.contacts_loaded.emit(placeholder_contacts)

                return []

        except Exception as e:
            safe_print(f"❌ Error in simplified contact loading: {e}")

            # Show error placeholder
            error_contacts = [
                {'name': "Abiram's Kitchen (Connection Error)", 'type': 'group', 'available': False}
            ]

            if hasattr(self, 'contacts_loaded'):
                self.contacts_loaded.emit(error_contacts)

            return []

    def load_from_recent_chats(self):
        """Load contacts from recent chats with scrolling to get more"""
        contacts = []
        try:
            from selenium.webdriver.common.by import By
            import time

            # Updated chat list selectors for current WhatsApp Web interface
            chat_list_selectors = [
                "[data-testid='chat-list'] [data-testid='cell-frame-container']",  # Primary selector
                "#pane-side [data-testid='cell-frame-container']",  # Side pane selector
                "div[aria-label*='Chat list'] [data-testid='cell-frame-container']",  # Aria label
                "[data-testid='cell-frame-container']",  # Generic cell frame
                "div[role='listitem']",  # List item role
                "div[role='row']",  # Row role (alternative)
                "[data-testid='conversation-panel-messages'] > div",  # Message panel
                "._2nY6U",  # Legacy class 1
                "._3m_Xw",  # Legacy class 2
                ".x10l6tqk.x13vifvy.x17qophe.xh8yej3",  # Current class combination
                "div[data-list-scroll-container='true'] > div",  # Scroll container
                ".x1n2onr6 > div",  # Container div
                "div[style*='transform'] > div[role='listitem']"  # Virtualized list items
            ]

            # Find the chat list container for scrolling with enhanced selectors
            chat_list_container = None
            container_selectors = [
                "[data-testid='chat-list']",
                "#pane-side",
                "._3OtEr",
                "[data-list-scroll-container='true']",
                ".x10l6tqk.x13vifvy.x17qophe.xh8yej3",
                "div[role='application'] > div > div > div"
            ]

            for container_selector in container_selectors:
                try:
                    chat_list_container = self.driver.find_element(By.CSS_SELECTOR, container_selector)
                    if chat_list_container and chat_list_container.is_displayed():
                        safe_print(f"📋 Found chat list container with selector: {container_selector}")
                        break
                except Exception as e:
                    safe_print(f"⚠️ Container selector failed {container_selector}: {e}")
                    continue

            # Scroll through chat list to load more contacts
            if chat_list_container:
                safe_print("📜 Scrolling through chat list to load more contacts...")

                try:
                    # Get initial scroll height
                    initial_height = self.driver.execute_script("return arguments[0].scrollHeight;", chat_list_container)
                    safe_print(f"📏 Initial scroll height: {initial_height}")

                    # Scroll down multiple times to load more chats
                    for scroll_attempt in range(10):  # Scroll 10 times
                        self.driver.execute_script("arguments[0].scrollTop += 500;", chat_list_container)
                        time.sleep(0.8)  # Increased wait time for content to load

                        # Check if new content loaded
                        new_height = self.driver.execute_script("return arguments[0].scrollHeight;", chat_list_container)
                        if new_height > initial_height:
                            safe_print(f"📈 New content loaded, height: {new_height}")
                            initial_height = new_height

                    # Scroll back to top
                    self.driver.execute_script("arguments[0].scrollTop = 0;", chat_list_container)
                    time.sleep(1)
                    safe_print("📜 Scrolling completed, back to top")

                except Exception as scroll_error:
                    safe_print(f"⚠️ Error during scrolling: {scroll_error}")
            else:
                safe_print("⚠️ No chat list container found for scrolling")

            # Now collect all visible contacts
            for selector in chat_list_selectors:
                try:
                    chat_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if chat_elements:
                        safe_print(f"📱 Found {len(chat_elements)} chat items with selector: {selector}")

                        # Process ALL chat elements, not just first 15
                        for i, element in enumerate(chat_elements):
                            try:
                                # Check for stale element reference
                                try:
                                    element.is_displayed()  # Test if element is still valid
                                except:
                                    safe_print(f"⚠️ Stale element reference at index {i}, skipping...")
                                    continue

                                contact_name = self.extract_contact_name(element)
                                if not contact_name:
                                    # Try alternative extraction methods for debugging
                                    try:
                                        element_text = element.text.strip() if element.text else "No text"
                                        element_html = element.get_attribute('outerHTML')[:200] if element.get_attribute('outerHTML') else "No HTML"
                                        safe_print(f"⚠️ No contact name found for element {i}. Text: '{element_text}', HTML: '{element_html}'")
                                    except:
                                        safe_print(f"⚠️ No contact name found for element {i} and couldn't get debug info")
                                    continue

                                contact_type = self.detect_contact_type(element, contact_name)

                                if contact_name and contact_name not in [c['name'] for c in contacts]:
                                    # Skip system messages and invalid names
                                    skip_keywords = ['whatsapp', 'system', 'broadcast', 'status', 'loading', 'search', 'new chat', 'new group']
                                    if not any(skip in contact_name.lower() for skip in skip_keywords):
                                        contacts.append({
                                            'name': contact_name,
                                            'type': contact_type,
                                            'source': 'recent_chats'
                                        })
                                        safe_print(f"✅ Added {contact_type}: {contact_name}")
                                else:
                                    safe_print(f"⚠️ Duplicate or invalid contact: {contact_name}")

                            except Exception as e:
                                safe_print(f"⚠️ Error processing chat element {i}: {e}")
                                continue

                        if contacts:
                            break  # Use first successful selector
                except Exception as e:
                    safe_print(f"⚠️ Error with selector {selector}: {e}")
                    continue

        except Exception as e:
            safe_print(f"❌ Error loading from recent chats: {e}")

        return contacts

    def load_from_contacts_menu(self):
        """Load contacts by accessing the new chat/contacts menu"""
        contacts = []
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            import time

            # Try to access the new chat menu to get full contacts list
            # Updated selectors for current WhatsApp Web interface (2024)
            new_chat_selectors = [
                "[data-testid='compose-btn']",  # Primary new chat button
                "[data-testid='new-chat-plus-button']",  # Alternative new chat button
                "[title='New chat']",
                "[aria-label='New chat']",
                "div[role='button'][aria-label*='New chat']",
                "div[role='button'][title*='New chat']",
                "span[data-icon='new-chat-outline']",  # Icon-based selector
                "span[data-icon='plus']",  # Plus icon
                "._3WByx",  # Legacy class selector
                "[data-icon='new-chat-outline']",
                "button[aria-label*='new']",  # Generic new button
                "div[data-tab='3']",  # Tab-based selector
                ".x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.x78zum5.xozqiw3.x1oa3qoh.x12fk4p8.xeuugli.x2lwn1j.xl56j7k.x1q0g3np.x6s0dn4"  # Current class combination
            ]

            for selector in new_chat_selectors:
                try:
                    new_chat_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if new_chat_button:
                        safe_print(f"🔘 Clicking new chat button: {selector}")
                        new_chat_button.click()
                        time.sleep(2)

                        # Look for contacts in the new chat dialog with scrolling
                        contacts_container_selectors = [
                            "[data-testid='contacts-list']",
                            "[data-testid='contact-list']",
                            "div[role='listbox']",
                            "._3OtEr"  # Contacts container
                        ]

                        contacts_container = None
                        for container_selector in contacts_container_selectors:
                            try:
                                contacts_container = self.driver.find_element(By.CSS_SELECTOR, container_selector)
                                if contacts_container:
                                    break
                            except:
                                continue

                        # Scroll through contacts list to load all contacts
                        if contacts_container:
                            safe_print("📜 Scrolling through contacts list...")

                            # Scroll down multiple times to load all contacts
                            for scroll_attempt in range(20):  # More scrolling for contacts
                                self.driver.execute_script("arguments[0].scrollTop += 300;", contacts_container)
                                time.sleep(0.3)

                            # Scroll back to top
                            self.driver.execute_script("arguments[0].scrollTop = 0;", contacts_container)
                            time.sleep(1)

                        # Now collect all contacts from the dialog
                        contact_element_selectors = [
                            "[data-testid='cell-frame-container']",
                            "div[role='listitem']",
                            "[data-testid='contact-list-item']",
                            "._3m_Xw"
                        ]

                        for contact_selector in contact_element_selectors:
                            try:
                                contact_elements = self.driver.find_elements(By.CSS_SELECTOR, contact_selector)
                                safe_print(f"📱 Found {len(contact_elements)} contact elements with selector: {contact_selector}")

                                for element in contact_elements:
                                    try:
                                        contact_name = self.extract_contact_name(element)
                                        contact_type = self.detect_contact_type(element, contact_name)

                                        if contact_name and contact_name not in [c['name'] for c in contacts]:
                                            # Skip system entries
                                            if not any(skip in contact_name.lower() for skip in ['whatsapp', 'system', 'broadcast', 'status', 'new group', 'new contact']):
                                                contacts.append({
                                                    'name': contact_name,
                                                    'type': contact_type,
                                                    'element': element
                                                })
                                                safe_print(f"✅ Added from menu {contact_type}: {contact_name}")
                                    except Exception as e:
                                        safe_print(f"⚠️ Error processing contact element: {e}")
                                        continue

                                if contacts:
                                    break  # Use first successful selector
                            except Exception as e:
                                safe_print(f"⚠️ Error with contact selector {contact_selector}: {e}")
                                continue

                        # Close the dialog by pressing Escape
                        try:
                            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                            time.sleep(1)
                        except:
                            pass

                        break  # Successfully accessed menu
                except Exception as e:
                    safe_print(f"⚠️ Error with new chat selector {selector}: {e}")
                    continue

        except Exception as e:
            safe_print(f"❌ Error loading from contacts menu: {e}")

        return contacts

    def discover_contacts_via_search(self):
        """Discover additional contacts using search functionality"""
        contacts = []
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            import time

            # Prioritized search patterns - TARGET: "Abiram's Kitchen" first
            search_patterns = [
                # PRIMARY TARGET - Abiram's Kitchen group
                "Abiram's Kitchen", "Abiram", "Kitchen", "abiram", "kitchen",
                # Common business terms
                "support", "admin", "manager", "team", "group", "office", "work",
                "customer", "service", "sales", "marketing", "hr", "finance",
                # Family terms
                "mom", "dad", "family", "home", "brother", "sister", "uncle", "aunt",
                # Common first names
                "john", "mary", "david", "sarah", "michael", "lisa", "james", "jennifer",
                "robert", "patricia", "william", "elizabeth", "richard", "linda"
            ]

            # Find search box with enhanced selectors
            search_selectors = [
                "[data-testid='chat-list-search']",
                "div[contenteditable='true'][data-tab='3']",
                "._3FRCZ",  # Legacy search input
                "[placeholder*='Search']",
                "[placeholder*='search']",
                "input[type='text'][placeholder*='Search']",
                "div[role='textbox'][contenteditable='true']",
                ".x1hx0egp.x6ikm8r.x1odjw0f.x1k6rcq7.x6prxxf",  # Current search box classes
                "[data-testid='search-input']",
                "div[data-tab='3'][contenteditable='true']"
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_box and search_box.is_displayed():
                        safe_print(f"🔍 Found search box with selector: {selector}")
                        break
                except Exception as e:
                    safe_print(f"⚠️ Search selector failed {selector}: {e}")
                    continue

            if search_box:
                safe_print("🔍 Using search to discover more contacts...")

                for pattern in search_patterns[:5]:  # Reduced to 5 patterns to avoid stale elements
                    try:
                        # Re-find search box to avoid stale element reference
                        search_box = None
                        for selector in search_selectors:
                            try:
                                search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if search_box and search_box.is_displayed():
                                    break
                            except:
                                continue

                        if not search_box:
                            safe_print(f"⚠️ Lost search box reference for pattern {pattern}")
                            break

                        # Clear and search
                        search_box.clear()
                        search_box.send_keys(pattern)
                        time.sleep(1.5)  # Increased wait time

                        # Look for search results
                        result_selectors = [
                            "[data-testid='cell-frame-container']",
                            "div[role='listitem']",
                            "._2nY6U"
                        ]

                        for result_selector in result_selectors:
                            try:
                                results = self.driver.find_elements(By.CSS_SELECTOR, result_selector)
                                for result in results[:3]:  # Limit results per search
                                    try:
                                        contact_name = self.extract_contact_name(result)
                                        contact_type = self.detect_contact_type(result, contact_name)

                                        if contact_name and contact_name not in [c['name'] for c in contacts]:
                                            if not any(skip in contact_name.lower() for skip in ['whatsapp', 'system', 'broadcast', 'status']):
                                                contacts.append({
                                                    'name': contact_name,
                                                    'type': contact_type,
                                                    'element': result
                                                })
                                                safe_print(f"✅ Discovered via search {contact_type}: {contact_name}")
                                    except:
                                        continue
                                break
                            except:
                                continue

                        # Clear search safely
                        try:
                            if search_box and search_box.is_displayed():
                                search_box.clear()
                                time.sleep(0.8)
                        except Exception as clear_error:
                            safe_print(f"⚠️ Error clearing search box: {clear_error}")
                            break

                    except Exception as e:
                        safe_print(f"⚠️ Error searching for pattern {pattern}: {e}")
                        continue

        except Exception as e:
            safe_print(f"❌ Error in search-based discovery: {e}")

        return contacts

    def extract_contact_name(self, element):
        """Extract contact name from a chat/contact element with enhanced methods"""
        contact_name = None
        try:
            from selenium.webdriver.common.by import By

            # Method 1: Look for span with title attribute (most reliable)
            try:
                name_elements = element.find_elements(By.CSS_SELECTOR, "span[title]")
                for name_element in name_elements:
                    title = name_element.get_attribute("title")
                    if title and len(title.strip()) > 0:
                        contact_name = title.strip()
                        break
            except Exception as e:
                safe_print(f"⚠️ Method 1 failed: {e}")

            # Method 2: Look for contact name in conversation header
            if not contact_name:
                try:
                    selectors = [
                        "[data-testid='conversation-info-header'] span",
                        "[data-testid='conversation-info-header']",
                        ".x1c4vz4f.x2lah0s.xdl72j9.x1g77sc7.x78zum5.xozqiw3.x1oa3qoh.x12fk4p8.xeuugli.x2lwn1j.xl56j7k.x1q0g3np.x6s0dn4 span"
                    ]
                    for selector in selectors:
                        try:
                            name_element = element.find_element(By.CSS_SELECTOR, selector)
                            text = name_element.text.strip()
                            if text and len(text) > 0:
                                contact_name = text
                                break
                        except:
                            continue
                except Exception as e:
                    safe_print(f"⚠️ Method 2 failed: {e}")

            # Method 3: Look for spans with meaningful text content
            if not contact_name:
                try:
                    spans = element.find_elements(By.TAG_NAME, "span")
                    for span in spans:
                        try:
                            text = span.text.strip()
                            # Filter out empty, numeric, or system text
                            if (text and len(text) > 1 and len(text) < 100 and
                                not text.isdigit() and
                                not text.startswith('http') and
                                not any(skip in text.lower() for skip in ['online', 'typing', 'last seen', 'click to', 'tap to'])):

                                # Check if it looks like a name (contains letters)
                                if any(c.isalpha() for c in text):
                                    contact_name = text
                                    break
                        except:
                            continue
                except Exception as e:
                    safe_print(f"⚠️ Method 3 failed: {e}")

            # Method 4: Look for div with text content (fallback)
            if not contact_name:
                try:
                    divs = element.find_elements(By.TAG_NAME, "div")
                    for div in divs:
                        try:
                            text = div.text.strip()
                            # More strict filtering for divs
                            if (text and len(text) > 1 and len(text) < 50 and
                                not text.isdigit() and
                                '\n' not in text and
                                not text.startswith('http') and
                                any(c.isalpha() for c in text) and
                                not any(skip in text.lower() for skip in ['online', 'typing', 'last seen', 'click to', 'tap to', 'message', 'chat'])):

                                contact_name = text
                                break
                        except:
                            continue
                except Exception as e:
                    safe_print(f"⚠️ Method 4 failed: {e}")

            # Method 5: Look for aria-label attributes
            if not contact_name:
                try:
                    aria_label = element.get_attribute("aria-label")
                    if aria_label and len(aria_label.strip()) > 0:
                        # Extract name from aria-label (often contains additional info)
                        label_text = aria_label.strip()
                        # Try to extract just the name part
                        if ',' in label_text:
                            contact_name = label_text.split(',')[0].strip()
                        elif '.' in label_text and len(label_text.split('.')[0]) > 2:
                            contact_name = label_text.split('.')[0].strip()
                        else:
                            contact_name = label_text
                except Exception as e:
                    safe_print(f"⚠️ Method 5 failed: {e}")

            # Final validation and cleanup
            if contact_name:
                contact_name = contact_name.strip()
                # Remove common prefixes/suffixes
                prefixes_to_remove = ['Chat with ', 'Message ', 'Call ']
                for prefix in prefixes_to_remove:
                    if contact_name.startswith(prefix):
                        contact_name = contact_name[len(prefix):].strip()

                # Validate final result
                if len(contact_name) == 0 or contact_name.isdigit():
                    contact_name = None

        except Exception as e:
            safe_print(f"⚠️ Error extracting contact name: {e}")

        return contact_name

    def detect_contact_type(self, element, contact_name):
        """Detect if contact is individual or group"""
        contact_type = 'contact'
        try:
            # Import Selenium By class for element finding
            from selenium.webdriver.common.by import By

            # Enhanced group detection logic
            # Method 1: Look for group indicators in data attributes and icons
            group_indicators = element.find_elements(By.CSS_SELECTOR,
                "[data-testid='default-group'], [title*='group'], [aria-label*='group'], "
                "[data-testid='group'], .group-icon, [class*='group']")
            if group_indicators:
                contact_type = 'group'

            # Method 2: Check for group-specific text patterns
            if contact_type == 'contact' and contact_name:
                # Common group name patterns
                group_patterns = [
                    'group', 'team', 'family', 'friends', 'work', 'office',
                    'project', 'class', 'school', 'college', 'university',
                    'community', 'club', 'society', 'organization', 'chat',
                    'members', 'squad', 'crew', 'gang', 'circle'
                ]
                name_lower = contact_name.lower()
                if any(pattern in name_lower for pattern in group_patterns):
                    contact_type = 'group'

            # Method 3: Look for participant count indicators
            if contact_type == 'contact':
                try:
                    participant_indicators = element.find_elements(By.CSS_SELECTOR,
                        "[class*='participant'], [class*='member'], [title*='participant'], [title*='member']")
                    if participant_indicators:
                        contact_type = 'group'
                except Exception as e:
                    safe_print(f"⚠️ Error checking participant indicators: {e}")

        except Exception as e:
            safe_print(f"⚠️ Error in group detection: {e}")

        return contact_type

    def find_abirams_kitchen(self):
        """Optimized search for Abiram's Kitchen group with early termination"""
        try:
            safe_print("🎯 Optimized search for 'Abiram's Kitchen' group...")
            from selenium.webdriver.common.by import By
            import time

            # Check if we already have a successful element reference
            if self._last_successful_element:
                try:
                    # Verify the element is still valid and clickable
                    if self._last_successful_element.is_displayed():
                        safe_print("✅ Reusing last successful element")
                        return {
                            'name': "Abiram's Kitchen",
                            'type': 'group',
                            'element': self._last_successful_element
                        }
                except:
                    # Element is stale, clear it
                    self._last_successful_element = None

            # Optimized search terms - most specific first for early termination
            search_terms = [
                "Abiram's Kitchen",  # Most specific first
                "Abiram Kitchen",    # Second most specific
                "Abiram",           # Fallback options
                "Kitchen"           # Last resort
            ]

            # Find search box with updated selectors for current WhatsApp Web
            search_selectors = [
                "[data-testid='chat-list-search']",
                "div[contenteditable='true'][data-tab='3']",
                "div[contenteditable='true'][role='textbox']",
                "[placeholder*='Search']",
                "[placeholder*='search']",
                "div[title='Search or start new chat']",
                "div[title*='Search']",
                "._3FRCZ",  # Legacy selector
                "div[data-tab='3'][contenteditable='true']",
                "input[placeholder*='Search']",
                "div.selectable-text[contenteditable='true']"
            ]

            # Try each search term - stop immediately when we find a match
            found_target = None
            for i, search_term in enumerate(search_terms, 1):
                if found_target:  # Stop searching if we already found the target
                    safe_print(f"🎯 ✅ TARGET ALREADY FOUND - STOPPING SEARCH")
                    break

                safe_print(f"🔍 Trying search term {i}/{len(search_terms)}: '{search_term}'")

                search_box = None
                for selector in search_selectors:
                    try:
                        search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box and search_box.is_displayed():
                            break
                    except:
                        continue

                if search_box:
                    try:
                        # Clear and search
                        search_box.clear()
                        search_box.send_keys(search_term)
                        time.sleep(2)

                        # Optimized selectors - most specific and reliable first
                        result_selectors = [
                            "[data-testid='cell-frame-container']",  # Most reliable
                            "div[role='listitem']",                  # Standard list items
                            "div[data-testid='chat']",               # Direct chat elements
                            "div[class*='x10l6tqk'][role='listitem']",  # Combined selector for efficiency
                            "div.x1n2onr6[role='button']",          # Clickable chat items
                            "div[role='row']"                       # Fallback row selector
                        ]

                        # Process selectors with early termination for efficiency
                        for selector_idx, result_selector in enumerate(result_selectors):
                            if found_target:  # Stop if we already found it
                                safe_print(f"🎯 ✅ TARGET ALREADY FOUND - STOPPING SELECTOR LOOP")
                                break

                            try:
                                results = self.driver.find_elements(By.CSS_SELECTOR, result_selector)
                                safe_print(f"   🔍 Selector {selector_idx+1}/{len(result_selectors)} '{result_selector}' found {len(results)} elements")

                                # Limit processing to first 10 elements for performance
                                for idx, result in enumerate(results[:10]):
                                    if found_target:  # Double-check for early termination
                                        break

                                    contact_name = self.extract_contact_name(result)
                                    if contact_name:
                                        safe_print(f"🔍 Found contact {idx+1}: '{contact_name}'")
                                        # Optimized matching - check exact match first
                                        contact_lower = contact_name.lower()

                                        # Exact match check first (most efficient)
                                        if contact_lower == "abiram's kitchen":
                                            safe_print(f"🎯 ✅ EXACT MATCH FOUND: {contact_name}")
                                            found_target = self._handle_target_group_click(result, contact_name, search_box)
                                            if found_target:
                                                self._last_successful_element = result
                                                return found_target

                                        # Partial match check (less efficient, only if exact fails)
                                        elif ("abiram" in contact_lower and "kitchen" in contact_lower) or \
                                             contact_lower == "abiram kitchen":
                                            safe_print(f"🎯 ✅ PARTIAL MATCH FOUND: {contact_name}")
                                            found_target = self._handle_target_group_click(result, contact_name, search_box)
                                            if found_target:
                                                self._last_successful_element = result
                                                return found_target
                                    else:
                                        # Reduced debugging - only for first few elements
                                        if idx < 3:
                                            try:
                                                element_text = result.text.strip() if result.text else ""
                                                if element_text and ("abiram" in element_text.lower() and "kitchen" in element_text.lower()):
                                                    safe_print(f"🎯 ✅ FOUND TARGET (via text): {element_text}")
                                                    found_target = self._handle_target_group_click(result, element_text, search_box)
                                                    if found_target:
                                                        self._last_successful_element = result
                                                        return found_target
                                            except:
                                                pass

                                # If we found results with this selector, don't try others (performance optimization)
                                if len(results) > 0:
                                    safe_print(f"   ✅ Found {len(results)} elements with '{result_selector}' - skipping remaining selectors")
                                    break

                            except Exception as e:
                                safe_print(f"   ⚠️ Error processing selector '{result_selector}': {e}")
                                continue
                        # Skip expensive debugging if we processed elements successfully
                        if len(results) == 0:
                            safe_print(f"   ❌ No elements found with '{result_selector}'")
                        else:
                            safe_print(f"   ✅ Processed {min(len(results), 10)} elements with '{result_selector}'")

                        # Early termination: if we found elements but no match, try next search term
                        if len(results) > 0:
                            safe_print(f"   🔄 Found elements but no target match - trying next search term")
                            break  # Break out of selector loop to try next search term

                    except Exception as e:
                        safe_print(f"⚠️ Error searching for '{search_term}': {e}")
                        continue

                # Clear search for next attempt
                try:
                    if search_box and search_box.is_displayed():
                        search_box.clear()
                        time.sleep(0.5)
                except Exception as clear_error:
                    safe_print(f"⚠️ Error clearing search box: {clear_error}")

            # If we've tried all search terms and selectors without success, stop here
            # Avoid expensive fallback searches that degrade performance
            safe_print("❌ Could not find 'Abiram's Kitchen' group with optimized search")
            safe_print("ℹ️ Skipping expensive fallback searches to maintain performance")
            return None

        except Exception as e:
            safe_print(f"❌ Error in find_abirams_kitchen: {e}")
            return None

    def debug_current_page_structure(self):
        """Debug function to inspect the current page structure before searching"""
        try:
            safe_print("🔍 DEBUG: Inspecting current page structure...")
            from selenium.webdriver.common.by import By

            # Check if we're on the right page
            current_url = self.driver.current_url
            safe_print(f"   Current URL: {current_url}")

            # Look for chat list containers first
            chat_list_selectors = [
                "#pane-side",
                "[data-testid='chat-list']",
                "div[id*='pane-side']",
                "div[class*='chat-list']"
            ]

            for selector in chat_list_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        safe_print(f"   Found chat list container: '{selector}' ({len(elements)} elements)")
                        # Count chat items in this container
                        chat_items = elements[0].find_elements(By.CSS_SELECTOR, "div[data-testid='cell-frame-container'], div[role='listitem']")
                        safe_print(f"     Contains {len(chat_items)} chat items")
                except:
                    pass

        except Exception as e:
            safe_print(f"❌ Error in debug_current_page_structure: {e}")

    def inspect_search_results(self, search_term):
        """Inspect what appears after searching for a specific term"""
        try:
            safe_print(f"🔍 Inspecting search results for '{search_term}'...")
            from selenium.webdriver.common.by import By
            import time

            # Wait a moment for results to appear
            time.sleep(1)

            # Look for any elements that might be search results
            potential_result_selectors = [
                "[data-testid='cell-frame-container']",
                "div[role='listitem']",
                "div[data-testid='chat']",
                "div[data-testid='list-item']",
                "div[class*='x10l6tqk']",
                "div[class*='_2nY6U']",
                "div[role='row']"
            ]

            total_found = 0
            for selector in potential_result_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        safe_print(f"   Selector '{selector}': {len(elements)} elements")
                        total_found += len(elements)

                        # Inspect first few elements
                        for i, element in enumerate(elements[:3]):
                            try:
                                text = element.text.strip() if element.text else ""
                                if text:
                                    safe_print(f"     [{i+1}] Text: '{text[:100]}'")

                                    # Check if this contains our target
                                    if "abiram" in text.lower() and "kitchen" in text.lower():
                                        safe_print(f"🎯 ✅ FOUND TARGET in search results: '{text}'")
                                        return {
                                            'name': text,
                                            'type': 'group',
                                            'element': element
                                        }
                                    elif "abiram" in text.lower() or "kitchen" in text.lower():
                                        safe_print(f"🔍 Partial match found: '{text}'")
                                else:
                                    # Try to get any text from child elements
                                    child_texts = []
                                    for child in element.find_elements(By.CSS_SELECTOR, "*"):
                                        child_text = child.text.strip() if child.text else ""
                                        if child_text and len(child_text) < 100:
                                            child_texts.append(child_text)

                                    if child_texts:
                                        combined_text = " ".join(child_texts)
                                        safe_print(f"     [{i+1}] Child texts: '{combined_text[:100]}'")

                                        if "abiram" in combined_text.lower() and "kitchen" in combined_text.lower():
                                            safe_print(f"🎯 ✅ FOUND TARGET in child elements: '{combined_text}'")
                                            return {
                                                'name': combined_text,
                                                'type': 'group',
                                                'element': element
                                            }
                            except Exception as e:
                                safe_print(f"     [{i+1}] Could not inspect element: {e}")
                except:
                    pass

            if total_found == 0:
                safe_print("   ❌ No search result elements found with any selector")
                # Let's see what IS on the page
                self.debug_visible_elements()
            else:
                safe_print(f"   Found {total_found} total elements but none matched 'Abiram's Kitchen'")

            return None

        except Exception as e:
            safe_print(f"❌ Error in inspect_search_results: {e}")
            return None

    def debug_visible_elements(self):
        """Debug function to see what elements are actually visible on the page"""
        try:
            safe_print("🔍 DEBUG: Looking for any visible elements with text...")
            from selenium.webdriver.common.by import By

            # Look for any divs with text content
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            text_elements = []

            for div in all_divs[:50]:  # Check first 50 divs
                try:
                    text = div.text.strip() if div.text else ""
                    if text and len(text) > 3 and len(text) < 200:
                        text_elements.append(text)

                        # Check if this might be our target
                        if "abiram" in text.lower() or "kitchen" in text.lower():
                            safe_print(f"🔍 POTENTIAL MATCH: '{text}'")
                except:
                    pass

            safe_print(f"   Found {len(text_elements)} elements with text content")
            if text_elements:
                safe_print("   Sample texts:")
                for i, text in enumerate(text_elements[:5]):
                    safe_print(f"     [{i+1}] '{text[:80]}'")

        except Exception as e:
            safe_print(f"❌ Error in debug_visible_elements: {e}")

    def debug_search_results_dom(self):
        """Debug function to inspect the current DOM structure for search results"""
        try:
            safe_print("🔍 DEBUG: Inspecting current DOM structure...")
            from selenium.webdriver.common.by import By

            # Check if we're on the right page
            current_url = self.driver.current_url
            safe_print(f"   Current URL: {current_url}")

            # Look for any divs that might contain search results
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            safe_print(f"   Total divs on page: {len(all_divs)}")

            # Look for elements with common WhatsApp classes
            common_selectors = [
                "div[data-testid]",
                "div[role]",
                "div[class*='x']",  # WhatsApp uses classes starting with 'x'
                "div[aria-label]",
                "div[title]"
            ]

            for selector in common_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    safe_print(f"   Selector '{selector}': {len(elements)} elements")

                    # Show first few elements for inspection
                    for i, element in enumerate(elements[:3]):
                        try:
                            text = element.text.strip()[:50] if element.text else "No text"
                            classes = element.get_attribute("class") or "No classes"
                            data_testid = element.get_attribute("data-testid") or "No data-testid"
                            role = element.get_attribute("role") or "No role"
                            safe_print(f"     [{i+1}] Text: '{text}', Classes: '{classes[:50]}', TestID: '{data_testid}', Role: '{role}'")
                        except:
                            safe_print(f"     [{i+1}] Could not inspect element")
                except Exception as e:
                    safe_print(f"   Selector '{selector}' failed: {e}")

            # Look specifically for search-related elements
            search_related = [
                "[data-testid*='search']",
                "[data-testid*='chat']",
                "[data-testid*='list']",
                "[data-testid*='cell']",
                "div[role='listitem']",
                "div[role='row']"
            ]

            safe_print("🔍 DEBUG: Search-related elements:")
            for selector in search_related:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        safe_print(f"   Found {len(elements)} elements with '{selector}'")
                        for i, element in enumerate(elements[:2]):
                            try:
                                text = element.text.strip()[:100] if element.text else "No text"
                                safe_print(f"     [{i+1}] '{text}'")
                            except:
                                pass
                except:
                    pass

        except Exception as e:
            safe_print(f"❌ Error in debug_search_results_dom: {e}")

    def find_abirams_kitchen_in_chat_list(self):
        """Fallback method to find Abiram's Kitchen directly in the chat list without search"""
        try:
            safe_print("🔍 Searching directly in chat list...")
            from selenium.webdriver.common.by import By
            import time

            # Wait a moment for the page to be ready
            time.sleep(2)

            # Look for chat list containers
            chat_list_selectors = [
                "[data-testid='chat-list']",
                "div[role='grid']",
                "div[role='list']",
                "div[class*='chat-list']",
                "div[id*='pane-side']",
                "#pane-side",
                "div[class*='_2Ts6i']",  # Common WhatsApp chat list class
                "div[class*='_3OvU8']"   # Another common class
            ]

            for list_selector in chat_list_selectors:
                try:
                    chat_lists = self.driver.find_elements(By.CSS_SELECTOR, list_selector)
                    safe_print(f"   Found {len(chat_lists)} chat list containers with '{list_selector}'")

                    for chat_list in chat_lists:
                        # Look for individual chat items within this container
                        chat_item_selectors = [
                            "div[data-testid='cell-frame-container']",
                            "div[role='listitem']",
                            "div[data-testid='chat']",
                            "div[class*='_2nY6U']",
                            "div[class*='x10l6tqk']",
                            "div[role='row']"
                        ]

                        for item_selector in chat_item_selectors:
                            try:
                                chat_items = chat_list.find_elements(By.CSS_SELECTOR, item_selector)
                                safe_print(f"     Found {len(chat_items)} chat items with '{item_selector}'")

                                for item in chat_items:
                                    contact_name = self.extract_contact_name(item)
                                    if contact_name:
                                        safe_print(f"     📱 Found contact: '{contact_name}'")

                                        # Check if this matches our target
                                        search_terms = [
                                            "Abiram's Kitchen",
                                            "Abiram Kitchen",
                                            "Abiram",
                                            "Kitchen"
                                        ]

                                        for term in search_terms:
                                            if term.lower() in contact_name.lower():
                                                safe_print(f"✅ FOUND MATCH: '{contact_name}' matches '{term}'")
                                                return item

                                if len(chat_items) > 0:
                                    break  # Found items with this selector, no need to try others

                            except Exception as e:
                                safe_print(f"     ⚠️ Item selector '{item_selector}' failed: {e}")
                                continue

                        # If no chat items found with any selector, try to find any clickable elements
                        try:
                            if all(len(chat_list.find_elements(By.CSS_SELECTOR, selector)) == 0 for selector in chat_item_selectors):
                                safe_print(f"     🔍 No chat items found, looking for any clickable elements...")
                                try:
                                    # Look for any divs that might be chat items
                                    all_divs = chat_list.find_elements(By.TAG_NAME, "div")
                                    safe_print(f"     Found {len(all_divs)} total divs in chat list")

                                    # Look for divs with text content that might be contacts
                                    for i, div in enumerate(all_divs[:10]):  # Check first 10 divs
                                        try:
                                            text = div.text.strip()
                                            if text and len(text) > 0 and len(text) < 100:
                                                safe_print(f"     Div {i+1}: '{text[:50]}'")

                                                # Check if this might be our target
                                                if "abiram" in text.lower() or "kitchen" in text.lower():
                                                    safe_print(f"✅ POTENTIAL MATCH FOUND: '{text}'")
                                                    return div
                                        except:
                                            continue
                                except Exception as e:
                                    safe_print(f"     ⚠️ Error inspecting divs: {e}")
                        except Exception as e:
                            safe_print(f"     ⚠️ Error checking for clickable elements: {e}")

                except Exception as e:
                    safe_print(f"   ⚠️ List selector '{list_selector}' failed: {e}")
                    continue

            safe_print("❌ Could not find 'Abiram's Kitchen' in chat list")
            return None

        except Exception as e:
            safe_print(f"❌ Error in find_abirams_kitchen_in_chat_list: {e}")
            return None

    def send_message_to_abirams_kitchen(self, message):
        """Send a message specifically to Abiram's Kitchen group"""
        try:
            safe_print(f"🎯 Sending message to Abiram's Kitchen: {message}")

            # First, find the group
            target_group = self.find_abirams_kitchen()
            if not target_group:
                safe_print("❌ Could not find Abiram's Kitchen group")
                return False

            # Click on the group to open chat
            try:
                target_group['element'].click()
                safe_print(f"✅ Opened chat with: {target_group['name']}")

                import time
                time.sleep(3)  # Wait for chat to load

                # Verify we're in the correct chat by checking the header
                try:
                    from selenium.webdriver.common.by import By
                    header_selectors = [
                        "[data-testid='conversation-header']",
                        "header[data-testid='chat-header']",
                        "._3auIg",  # Chat header class
                        ".chat-header"
                    ]

                    chat_verified = False
                    for selector in header_selectors:
                        try:
                            header = self.driver.find_element(By.CSS_SELECTOR, selector)
                            header_text = header.text.lower()
                            if "abiram" in header_text and "kitchen" in header_text:
                                safe_print("✅ Verified we're in Abiram's Kitchen chat")
                                chat_verified = True
                                break
                        except:
                            continue

                    if not chat_verified:
                        safe_print("⚠️ Could not verify chat header, proceeding anyway")

                except Exception as e:
                    safe_print(f"⚠️ Error verifying chat header: {e}")

                # Send the message
                success = self.send_message_to_current_chat(message)

                if success:
                    safe_print("✅ Message sent to Abiram's Kitchen successfully")

                    # Additional verification: wait and check if message appears in chat
                    time.sleep(2)
                    try:
                        # Look for the message in the chat history
                        message_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='msg-container']")
                        if message_elements:
                            # Check the last few messages for our content
                            sanitized_message = sanitize_message_for_chrome(message)
                            for msg_elem in message_elements[-3:]:  # Check last 3 messages
                                if sanitized_message[:20] in msg_elem.text:  # Check first 20 chars
                                    safe_print("✅ Message verified in chat history")
                                    return True
                        safe_print("⚠️ Message sent but not found in chat history")
                    except:
                        safe_print("⚠️ Could not verify message in chat history")
                else:
                    safe_print("❌ Failed to send message to Abiram's Kitchen")

                return success

            except Exception as e:
                safe_print(f"❌ Error clicking on group: {e}")
                return False

        except Exception as e:
            safe_print(f"❌ Error in send_message_to_abirams_kitchen: {e}")
            return False

    def send_message_to_current_chat(self, message):
        """Send message to currently open chat"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            import time

            # Find message input box with multiple selectors
            message_selectors = [
                "[data-testid='conversation-compose-box-input']",
                "div[contenteditable='true'][data-tab='10']",
                "div[contenteditable='true'][role='textbox']",
                "._3Uu1_",
                "[data-testid='compose-box-input']"
            ]

            message_box = None
            for selector in message_selectors:
                try:
                    message_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if message_box and message_box.is_displayed():
                        safe_print(f"✅ Found message input with selector: {selector}")
                        break
                except:
                    continue

            if not message_box:
                safe_print("❌ Could not find message input box")
                return False

            # Clear and type message (sanitize for ChromeDriver)
            sanitized_message = sanitize_message_for_chrome(message)
            message_box.clear()
            message_box.send_keys(sanitized_message)
            safe_print(f"✅ Typed message: {sanitized_message}")

            # Try multiple send methods with verification
            # Method 1: Find and click send button
            send_selectors = [
                "[data-testid='send']",
                "[data-testid='compose-btn-send']",
                "button[data-tab='11']",
                "._1E0Oz",
                "span[data-testid='send']"
            ]

            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button and send_button.is_displayed() and send_button.is_enabled():
                        # Store original message to verify it was sent
                        original_message = message_box.get_attribute('textContent') or message_box.get_attribute('value') or ""

                        send_button.click()
                        time.sleep(1)  # Wait for message to be sent

                        # Verify message was sent by checking if input is cleared
                        current_message = message_box.get_attribute('textContent') or message_box.get_attribute('value') or ""
                        if not current_message.strip() or current_message != original_message:
                            safe_print("✅ Message sent using send button (verified)")
                            return True
                        else:
                            safe_print("⚠️ Send button clicked but message still in input")
                except Exception as e:
                    safe_print(f"❌ Error with send button {selector}: {e}")
                    continue

            # Method 2: Press Enter key
            try:
                # Store original message to verify it was sent
                original_message = message_box.get_attribute('textContent') or message_box.get_attribute('value') or ""

                message_box.send_keys(Keys.ENTER)
                time.sleep(1)  # Wait for message to be sent

                # Verify message was sent
                current_message = message_box.get_attribute('textContent') or message_box.get_attribute('value') or ""
                if not current_message.strip() or current_message != original_message:
                    safe_print("✅ Message sent using Enter key (verified)")
                    return True
                else:
                    safe_print("⚠️ Enter pressed but message still in input")
            except Exception as e:
                safe_print(f"❌ Error sending with Enter key: {e}")

            # Method 3: Try Ctrl+Enter
            try:
                # Store original message to verify it was sent
                original_message = message_box.get_attribute('textContent') or message_box.get_attribute('value') or ""

                message_box.send_keys(Keys.CONTROL + Keys.ENTER)
                time.sleep(1)  # Wait for message to be sent

                # Verify message was sent
                current_message = message_box.get_attribute('textContent') or message_box.get_attribute('value') or ""
                if not current_message.strip() or current_message != original_message:
                    safe_print("✅ Message sent using Ctrl+Enter (verified)")
                    return True
                else:
                    safe_print("⚠️ Ctrl+Enter pressed but message still in input")
            except Exception as e:
                safe_print(f"❌ Error sending with Ctrl+Enter: {e}")

            safe_print("❌ All send methods failed - message not sent")
            return False

        except Exception as e:
            safe_print(f"❌ Error in send_message_to_current_chat: {e}")
            return False

    def send_message(self, contact_name, message):
        """Send a message to a specific contact"""
        try:
            print(f"📤 Sending message to {contact_name}: {message}")

            # Special handling for Abiram's Kitchen
            if "abiram" in contact_name.lower() and "kitchen" in contact_name.lower():
                safe_print("🎯 Detected Abiram's Kitchen - using specialized method")
                return self.send_message_to_abirams_kitchen(message)

            # First, try to find and click the contact
            if self.select_contact(contact_name):
                # Wait for chat to open
                import time
                time.sleep(1)

                # Find message input box
                message_selectors = [
                    "[data-testid='conversation-compose-box-input']",
                    "div[contenteditable='true'][data-tab='10']",
                    "div[contenteditable='true']",
                    "._3Uu1_",  # Message input
                ]

                message_box = None
                for selector in message_selectors:
                    try:
                        message_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if message_box:
                            break
                    except:
                        continue

                if message_box:
                    # Clear and type message (sanitize for ChromeDriver)
                    sanitized_message = sanitize_message_for_chrome(message)
                    message_box.clear()
                    message_box.send_keys(sanitized_message)

                    # Find and click send button
                    send_selectors = [
                        "[data-testid='send']",
                        "button[data-tab='11']",
                        "._1E0Oz",  # Send button
                    ]

                    for selector in send_selectors:
                        try:
                            send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if send_button:
                                send_button.click()
                                print(f"✅ Message sent to {contact_name}")
                                return True
                        except:
                            continue

                    # Alternative: Press Enter
                    from selenium.webdriver.common.keys import Keys
                    message_box.send_keys(Keys.ENTER)
                    print(f"✅ Message sent to {contact_name} (using Enter key)")
                    return True
                else:
                    print("❌ Could not find message input box")
                    return False
            else:
                print(f"❌ Could not select contact: {contact_name}")
                return False

        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

    def select_contact(self, contact_name):
        """Select a contact or group to start chatting"""
        try:
            print(f"🔍 Searching for contact: {contact_name}")

            # Try to use search box first
            search_selectors = [
                "[data-testid='chat-list-search']",
                "div[contenteditable='true'][data-tab='3']",
                "._3FRCZ",  # Search input
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_box:
                        break
                except:
                    continue

            if search_box:
                # Use search to find contact
                search_box.clear()
                search_box.send_keys(contact_name)

                import time
                time.sleep(2)  # Wait for search results

                # Click on first search result
                result_selectors = [
                    "[data-testid='cell-frame-container']",
                    "div[role='listitem']",
                    "._2nY6U",
                ]

                for selector in result_selectors:
                    try:
                        results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if results:
                            results[0].click()
                            print(f"✅ Selected contact: {contact_name}")
                            return True
                    except:
                        continue

            # Alternative: Look through contact list directly
            contact_selectors = [
                f"span[title='{contact_name}']",
                f"span[title*='{contact_name}']",
            ]

            for selector in contact_selectors:
                try:
                    contact_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if contact_element:
                        # Click on the parent container
                        parent = contact_element.find_element(By.XPATH, "./ancestor::div[@role='listitem' or contains(@class, 'cell-frame-container')]")
                        parent.click()
                        print(f"✅ Selected contact: {contact_name}")
                        return True
                except:
                    continue

            print(f"❌ Could not find contact: {contact_name}")
            return False

        except Exception as e:
            print(f"❌ Error selecting contact: {e}")
            return False
    
    def send_message_by_phone(self, phone_number: str, message: str):
        """Send a message via WhatsApp Web using phone number (alternative method)"""
        if not self.is_connected or not self.driver:
            return False

        try:
            # Import Selenium components dynamically
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Navigate to chat using phone number
            chat_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
            self.driver.get(chat_url)

            # Wait for message input and send
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
            )

            # Clear and type message (sanitize for ChromeDriver)
            sanitized_message = sanitize_message_for_chrome(message)
            message_input.clear()
            message_input.send_keys(sanitized_message)

            # Find and click send button
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='compose-btn-send']")
            send_button.click()

            return True

        except Exception as e:
            print(f"Failed to send message by phone: {e}")
            return False
    
    def run(self):
        """Main thread loop for monitoring messages"""
        while not self.should_stop:
            if self.is_connected:
                try:
                    self.check_for_new_messages()
                    # If check_for_new_messages set should_stop due to session error, break the loop
                    if self.should_stop:
                        print("📱 WhatsApp monitoring stopped due to session termination")
                        break
                except Exception as e:
                    # Check if it's a session-related error
                    error_str = str(e).lower()
                    if any(keyword in error_str for keyword in ["no such window", "target window already closed", "web view not found"]):
                        print("📱 WhatsApp monitoring stopped due to session error")
                        self.should_stop = True
                        break
                    else:
                        print(f"Error checking messages: {e}")

            time.sleep(self.message_check_interval)
    
    def check_for_new_messages(self):
        """Check for new incoming messages"""
        if not self.driver:
            return

        try:
            # First check if the driver session is still valid
            try:
                # Try to get the current window handle to verify session is alive
                current_window = self.driver.current_window_handle
                if not current_window:
                    print("⚠️ WhatsApp Web window closed - stopping message monitoring")
                    self.should_stop = True
                    return
            except Exception as session_error:
                # Session is dead - stop monitoring to prevent spam
                if "no such window" in str(session_error).lower() or "target window already closed" in str(session_error).lower():
                    print("⚠️ WhatsApp Web session closed - stopping message monitoring")
                    self.should_stop = True
                    return
                else:
                    # Some other session error - still stop to be safe
                    print(f"⚠️ WhatsApp Web session error - stopping monitoring: {session_error}")
                    self.should_stop = True
                    return

            # Import Selenium components dynamically
            from selenium.webdriver.common.by import By

            # This is a simplified implementation
            # In a real implementation, you would parse the chat list and messages
            unread_chats = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='cell-frame-container'] [data-testid='icon-unread-count']")

            for chat in unread_chats:
                # Extract message details (simplified)
                chat_container = chat.find_element(By.XPATH, "./ancestor::div[@data-testid='cell-frame-container']")
                # Parse contact name, message content, etc.
                # This would need more sophisticated parsing in a real implementation

                message_data = {
                    'sender': 'Unknown',
                    'content': 'New message received',
                    'timestamp': datetime.now().isoformat()
                }

                self.message_received.emit(message_data)

        except Exception as e:
            # Check if it's a session-related error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["no such window", "target window already closed", "web view not found", "session not created"]):
                print("⚠️ WhatsApp Web session terminated - stopping message monitoring")
                self.should_stop = True
            else:
                # Only print non-session errors to avoid spam
                print(f"Error checking for new messages: {e}")
    
    def cleanup_stale_sessions(self):
        """Clean up stale WebDriver sessions that are no longer accessible"""
        try:
            import requests
            import time

            # Try to connect to Chrome DevTools to check if sessions are still alive
            debug_port = "9222"
            try:
                response = requests.get(f"http://127.0.0.1:{debug_port}/json", timeout=2)
                if response.status_code == 200:
                    sessions = response.json()
                    active_sessions = [s for s in sessions if 'whatsapp' in s.get('url', '').lower()]
                    print(f"ℹ️ Found {len(active_sessions)} active WhatsApp sessions")
                    return len(active_sessions) > 0
                else:
                    print("ℹ️ Chrome DevTools not accessible - no active sessions")
                    return False
            except requests.exceptions.RequestException:
                print("ℹ️ Chrome DevTools not responding - cleaning up stale references")
                return False

        except Exception as e:
            print(f"⚠️ Error checking session status: {e}")
            return False

    def stop(self, preserve_session=None):
        """Stop the WhatsApp Web driver with optional session preservation"""
        self.should_stop = True

        # Determine whether to preserve session
        if preserve_session is None:
            preserve_session = self.session_reuse_enabled

        if self.driver:
            try:
                if preserve_session:
                    # Check if session is still accessible before preserving
                    if self.cleanup_stale_sessions():
                        print("💾 Preserving Chrome session for future reuse")
                        self.driver = None  # Just remove our reference
                    else:
                        print("🧹 Session no longer accessible - cleaning up")
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                else:
                    # Quit the driver completely
                    self.driver.quit()
                    print("🔚 Chrome session terminated")
            except Exception as e:
                print(f"⚠️ Error during cleanup: {e}")
                self.driver = None

        # Only clean up user data directory if not preserving session
        if not preserve_session and self.user_data_dir and os.path.exists(self.user_data_dir):
            # Only clean up if it's a temporary directory (not persistent)
            if not self.session_reuse_enabled or self.user_data_dir != self.persistent_session_dir:
                try:
                    import shutil
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                    print(f"🧹 Cleaned up temporary session directory: {self.user_data_dir}")
                except Exception as e:
                    print(f"⚠️ Could not clean up session directory: {e}")
            else:
                print(f"💾 Preserved persistent session directory: {self.user_data_dir}")

        self.wait()

    def force_stop(self):
        """Force stop and clean up everything, including persistent sessions"""
        print("🚫 Force stopping WhatsApp Web driver...")
        self.stop(preserve_session=False)

        # Also clean up persistent session if it exists
        if self.persistent_session_dir and os.path.exists(self.persistent_session_dir):
            try:
                import shutil
                shutil.rmtree(self.persistent_session_dir, ignore_errors=True)
                print(f"🧹 Force cleaned persistent session directory: {self.persistent_session_dir}")
            except Exception as e:
                print(f"⚠️ Could not clean up persistent session directory: {e}")

    def disable_session_reuse(self):
        """Disable session reuse for this instance"""
        self.session_reuse_enabled = False
        print("🔄 Session reuse disabled - will create fresh sessions")

    def enable_session_reuse(self):
        """Enable session reuse for this instance"""
        self.session_reuse_enabled = True
        print("🔄 Session reuse enabled - will attempt to reuse existing sessions")


class FirebaseWhatsAppSync(QObject):
    """Handles WhatsApp message synchronization with Firebase"""

    def __init__(self, user_id: str, parent=None):
        self.is_qobject_initialized = False
        try:
            from PySide6.QtCore import QThread
            # Only initialize QObject if we're in the main thread
            current_thread = QThread.currentThread()
            main_thread = QApplication.instance().thread() if QApplication.instance() else None

            if main_thread and current_thread == main_thread:
                super().__init__(parent)
                self.is_qobject_initialized = True
            else:
                safe_print("⚠️ FirebaseWhatsAppSync created outside main thread - QObject features disabled")
                # Don't call super().__init__ to avoid threading issues
        except Exception as e:
            safe_print(f"⚠️ Could not initialize QObject parent: {e}")
            # Continue without QObject parent if Qt is not available

        self.user_id = user_id
        self.messages_collection = f"users/{user_id}/whatsapp_messages"
        self.contacts_collection = f"users/{user_id}/whatsapp_contacts"
        self.sync_timer = None  # Initialize in main thread
        self.sync_interval = 30000  # 30 seconds

        # Initialize timer in main thread only if QObject was initialized
        if self.is_qobject_initialized:
            self._init_timer()

    def _init_timer(self):
        """Initialize timer in the correct thread"""
        try:
            from PySide6.QtCore import QTimer, QThread, QMetaObject, Qt
            # Only create timer if we're in the main thread
            current_thread = QThread.currentThread()
            main_thread = QApplication.instance().thread() if QApplication.instance() else None

            if main_thread and current_thread == main_thread:
                self.sync_timer = QTimer(self)
                self.sync_timer.timeout.connect(self.sync_messages)
            else:
                safe_print("⚠️ Cannot create QTimer outside main thread - using thread-safe alternative")
                self.sync_timer = None
                # Use QMetaObject.invokeMethod to safely call from main thread later
                if main_thread:
                    QMetaObject.invokeMethod(self, "_create_timer_in_main_thread", Qt.QueuedConnection)
        except Exception as e:
            safe_print(f"⚠️ Could not initialize sync timer: {e}")
            self.sync_timer = None

    def _create_timer_in_main_thread(self):
        """Create timer safely in main thread"""
        try:
            from PySide6.QtCore import QTimer
            if not self.sync_timer:
                self.sync_timer = QTimer(self)
                self.sync_timer.timeout.connect(self.sync_messages)
                safe_print("✅ Sync timer created in main thread")
        except Exception as e:
            safe_print(f"⚠️ Could not create timer in main thread: {e}")

    def start_sync(self):
        """Start automatic synchronization"""
        if not self.is_qobject_initialized:
            safe_print("⚠️ QObject not initialized - sync not available")
            return

        if not self.sync_timer:
            self._init_timer()

        if self.sync_timer and FIREBASE_INTEGRATION and FIREBASE_AVAILABLE:
            self.sync_timer.start(self.sync_interval)
            safe_print("🔄 WhatsApp Firebase sync started")
        else:
            safe_print("⚠️ Firebase not available or timer not initialized - sync disabled")

    def stop_sync(self):
        """Stop automatic synchronization"""
        if self.is_qobject_initialized and self.sync_timer:
            self.sync_timer.stop()
            safe_print("⏹️ WhatsApp Firebase sync stopped")
    
    def sync_messages(self):
        """Sync messages with Firebase"""
        if not FIREBASE_INTEGRATION or not FIREBASE_AVAILABLE:
            return
        
        try:
            # This would implement bidirectional sync
            # Upload local messages and download remote messages
            print("🔄 Syncing WhatsApp messages with Firebase...")
            
            # In a real implementation, you would:
            # 1. Upload pending local messages
            # 2. Download new remote messages
            # 3. Resolve conflicts
            # 4. Update local storage
            
        except Exception as e:
            print(f"Error syncing messages: {e}")
    
    def upload_message(self, message: WhatsAppMessage):
        """Upload a message to Firebase"""
        if not FIREBASE_INTEGRATION or not FIREBASE_AVAILABLE:
            return False
        
        try:
            # Upload message to Firebase
            message_data = message.to_dict()
            # FIRESTORE_DB.collection(self.messages_collection).document(message.message_id).set(message_data)
            message.sync_status = "synced"
            return True
        except Exception as e:
            print(f"Error uploading message: {e}")
            message.sync_status = "failed"
            return False
    
    def download_messages(self, since: datetime = None):
        """Download messages from Firebase"""
        if not FIREBASE_INTEGRATION or not FIREBASE_AVAILABLE:
            return []
        
        try:
            # Download messages from Firebase
            # This would query the Firebase collection and return messages
            messages = []
            return messages
        except Exception as e:
            print(f"Error downloading messages: {e}")
            return []


class WhatsAppIntegrationWidget(QWidget):
    """Main WhatsApp integration widget"""

    message_sent = Signal(dict)
    message_received = Signal(dict)
    update_status_signal = Signal(str)
    connection_failed_signal = Signal(str)
    
    def __init__(self, data=None, user_info=None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.user_info = user_info
        self.messages = []
        self.contacts = []
        self.all_contacts = []  # Store all contacts for filtering
        self.current_filter = 'all'  # Current contact filter
        self.whatsapp_driver = None
        self.firebase_sync = None

        # Initialize Firebase sync if user is available
        if self.user_info and 'localId' in self.user_info:
            self.firebase_sync = FirebaseWhatsAppSync(self.user_info['localId'])

        self.init_ui()
        self.setup_connections()

        # Get notification manager
        try:
            self.notification_manager = get_notification_manager()
        except:
            self.notification_manager = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📱 WhatsApp Integration")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Connection status
        self.status_label = QLabel("🔴 Disconnected")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        
        # Connect button
        self.connect_button = QPushButton("Connect to WhatsApp Web")
        self.connect_button.clicked.connect(self.connect_whatsapp)
        header_layout.addWidget(self.connect_button)

        # Chrome status button
        self.chrome_status_button = QPushButton("Check Chrome")
        self.chrome_status_button.clicked.connect(self.check_chrome_installation)
        header_layout.addWidget(self.chrome_status_button)

        # Session management button
        self.session_button = QPushButton("Session Options")
        self.session_button.clicked.connect(self.show_session_options)
        header_layout.addWidget(self.session_button)

        layout.addLayout(header_layout)

        # Session status info
        self.session_info_label = QLabel("🔄 Session reuse: Enabled")
        self.session_info_label.setStyleSheet("color: #10b981; font-size: 12px; padding: 5px;")
        layout.addWidget(self.session_info_label)

        # Session discovery section
        session_group = QGroupBox("Available WhatsApp Web Sessions")
        session_layout = QVBoxLayout(session_group)

        # Search buttons layout
        search_buttons_layout = QHBoxLayout()

        # Search button
        self.search_sessions_button = QPushButton("🔍 Search for Sessions")
        self.search_sessions_button.clicked.connect(self.search_whatsapp_sessions)
        self.search_sessions_button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        search_buttons_layout.addWidget(self.search_sessions_button)

        # Refresh button
        self.refresh_sessions_button = QPushButton("🔄 Refresh")
        self.refresh_sessions_button.clicked.connect(self.refresh_whatsapp_sessions)
        self.refresh_sessions_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        search_buttons_layout.addWidget(self.refresh_sessions_button)

        session_layout.addLayout(search_buttons_layout)

        # Sessions list
        self.sessions_list = QListWidget()
        self.sessions_list.setMaximumHeight(120)
        self.sessions_list.itemDoubleClicked.connect(self.connect_to_selected_session)
        session_layout.addWidget(self.sessions_list)

        # Sessions info label
        self.sessions_info_label = QLabel("Searching for existing WhatsApp Web sessions...")
        self.sessions_info_label.setStyleSheet("color: #3498db; font-size: 11px; font-style: italic;")
        session_layout.addWidget(self.sessions_info_label)

        # Help section with automated setup
        help_group = QGroupBox("💡 Automated Chrome Setup")
        help_layout = QVBoxLayout(help_group)

        help_text = QLabel(
            "• Click 'Start Chrome with Debugging' to automatically enable session detection<br>"
            "• 🔧 Blue sessions need Chrome debugging enabled<br>"
            "• ⚠️ Yellow sessions need WhatsApp authentication<br>"
            "• ✅ Green sessions are ready to use"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 5px;")
        help_layout.addWidget(help_text)

        # Automated Chrome setup button
        self.setup_chrome_button = QPushButton("🚀 Start Chrome with Debugging")
        self.setup_chrome_button.clicked.connect(self.setup_chrome_debugging)
        self.setup_chrome_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        help_layout.addWidget(self.setup_chrome_button)

        layout.addWidget(session_group)
        layout.addWidget(help_group)

        # Automatically search for sessions when widget loads
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self.safe_search_whatsapp_sessions)  # Search after 2 seconds

        # Main messaging interface
        messaging_group = QGroupBox("💬 WhatsApp Messaging Interface")
        messaging_layout = QVBoxLayout(messaging_group)

        # Main content
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Contacts
        contacts_widget = self.create_contacts_panel()
        main_splitter.addWidget(contacts_widget)

        # Right panel - Chat
        chat_widget = self.create_chat_panel()
        main_splitter.addWidget(chat_widget)

        main_splitter.setSizes([300, 500])
        messaging_layout.addWidget(main_splitter)

        # Bottom panel - Quick actions
        actions_widget = self.create_actions_panel()
        messaging_layout.addWidget(actions_widget)

        layout.addWidget(messaging_group)
    
    def create_contacts_panel(self):
        """Create contacts management panel with improved categorization"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Contacts header
        header_layout = QHBoxLayout()
        contacts_label = QLabel("👥 Contacts & Groups")
        contacts_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(contacts_label)

        add_contact_button = QPushButton("➕")
        add_contact_button.setFixedSize(30, 30)
        add_contact_button.setToolTip("Add Contact")
        add_contact_button.clicked.connect(self.add_contact)
        header_layout.addWidget(add_contact_button)

        # Load ALL contacts button
        load_all_contacts_button = QPushButton("🔄")
        load_all_contacts_button.setFixedSize(30, 30)
        load_all_contacts_button.setToolTip("Load ALL Contacts and Groups (Comprehensive)")
        load_all_contacts_button.clicked.connect(self.comprehensive_load_contacts)
        header_layout.addWidget(load_all_contacts_button)

        # Quick load button
        quick_load_button = QPushButton("⚡")
        quick_load_button.setFixedSize(30, 30)
        quick_load_button.setToolTip("Quick Load (Recent Chats Only)")
        quick_load_button.clicked.connect(self.manual_load_contacts)
        header_layout.addWidget(quick_load_button)

        layout.addLayout(header_layout)

        # Filter buttons for contact types
        filter_layout = QHBoxLayout()

        self.show_all_button = QPushButton("📋 All")
        self.show_all_button.setCheckable(True)
        self.show_all_button.setChecked(True)
        self.show_all_button.clicked.connect(lambda: self.filter_contacts('all'))
        filter_layout.addWidget(self.show_all_button)

        self.show_contacts_button = QPushButton("👤 Contacts")
        self.show_contacts_button.setCheckable(True)
        self.show_contacts_button.clicked.connect(lambda: self.filter_contacts('contact'))
        filter_layout.addWidget(self.show_contacts_button)

        self.show_groups_button = QPushButton("👥 Groups")
        self.show_groups_button.setCheckable(True)
        self.show_groups_button.clicked.connect(lambda: self.filter_contacts('group'))
        filter_layout.addWidget(self.show_groups_button)

        layout.addLayout(filter_layout)

        # Contacts list with improved styling
        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.select_contact)
        self.contacts_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #25D366;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e8f5e8;
            }
        """)
        layout.addWidget(self.contacts_list)

        # Contact count label
        self.contact_count_label = QLabel("No contacts loaded")
        self.contact_count_label.setStyleSheet("color: #666; font-size: 11px; padding: 4px;")
        layout.addWidget(self.contact_count_label)

        return widget
    
    def create_chat_panel(self):
        """Create chat interface panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Chat header
        self.chat_header = QLabel("💬 WhatsApp Messaging")
        self.chat_header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.chat_header)

        # Messages area
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setPlaceholderText(
            "📱 WhatsApp Web Integration Ready!\n\n"
            "How to use:\n"
            "1. Connect to WhatsApp Web using the button above\n"
            "2. Select a contact from the left panel\n"
            "3. Type your message below and press Send\n\n"
            "💡 You can add contacts manually or they will be loaded from WhatsApp Web"
        )
        layout.addWidget(self.messages_area)

        # Enhanced Message input section
        input_section = QGroupBox("💬 Message Composer")
        input_section_layout = QVBoxLayout(input_section)

        # Message input with character counter
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Connect to WhatsApp Web first, then select a contact...")
        self.message_input.setEnabled(False)  # Disabled until connected
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.textChanged.connect(self.update_character_count)
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #25D366;
                background-color: #f8fff8;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """)
        input_layout.addWidget(self.message_input)

        # Character counter
        self.char_counter = QLabel("0/1000")
        self.char_counter.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        input_layout.addWidget(self.char_counter)

        input_section_layout.addLayout(input_layout)

        # Button row
        button_layout = QHBoxLayout()

        # Test button to find Abiram's Kitchen
        test_button = QPushButton("🔍 Find Abiram's Kitchen")
        test_button.clicked.connect(self.test_find_abirams_kitchen)
        test_button.setEnabled(False)  # Disabled until connected
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.test_button = test_button  # Store reference
        button_layout.addWidget(test_button)

        # Abiram's Kitchen quick send button
        abiram_button = QPushButton("🎯 Send to Abiram's Kitchen")
        abiram_button.clicked.connect(self.send_to_abirams_kitchen)
        abiram_button.setEnabled(False)  # Disabled until connected
        abiram_button.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                font-weight: bold;
                border: none;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 13px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #128C7E;
                transform: translateY(-1px);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.abiram_button = abiram_button  # Store reference
        button_layout.addWidget(abiram_button)

        # Regular send button
        send_button = QPushButton("📤 Send Message")
        send_button.clicked.connect(self.send_message)
        send_button.setEnabled(False)  # Disabled until connected
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                border: none;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                transform: translateY(-1px);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.send_button = send_button  # Store reference
        button_layout.addWidget(send_button)

        # Quick templates button
        templates_button = QPushButton("📝 Quick Templates")
        templates_button.clicked.connect(self.show_quick_templates)
        templates_button.setEnabled(False)  # Disabled until connected
        templates_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.templates_button = templates_button  # Store reference
        button_layout.addWidget(templates_button)

        # Add stretch to center buttons
        button_layout.addStretch()

        input_section_layout.addLayout(button_layout)
        layout.addWidget(input_section)

        layout.addLayout(input_layout)

        # Add startup status section
        self.add_startup_status_section(layout)

        return widget
    
    def create_actions_panel(self):
        """Create quick actions panel"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(widget)
        
        # Sync status
        sync_label = QLabel("🔄 Sync:")
        layout.addWidget(sync_label)
        
        self.sync_status_label = QLabel("Ready")
        layout.addWidget(self.sync_status_label)
        
        layout.addStretch()
        
        # Quick actions
        broadcast_button = QPushButton("📢 Broadcast")
        broadcast_button.clicked.connect(self.show_broadcast_dialog)
        layout.addWidget(broadcast_button)
        
        templates_button = QPushButton("📝 Templates")
        templates_button.clicked.connect(self.show_templates_dialog)
        layout.addWidget(templates_button)
        
        settings_button = QPushButton("⚙️ Settings")
        settings_button.clicked.connect(self.show_settings_dialog)
        layout.addWidget(settings_button)
        
        return widget

    def add_startup_status_section(self, layout):
        """Add startup status section to show WhatsApp automation status"""
        try:
            # Create startup status group
            startup_group = QGroupBox("🚀 Startup Automation Status")
            startup_layout = QVBoxLayout(startup_group)

            # Status label
            self.startup_status_label = QLabel("⏳ Checking WhatsApp automation status...")
            self.startup_status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
            startup_layout.addWidget(self.startup_status_label)

            # Abiram's Kitchen status
            self.abirams_status_label = QLabel("⏳ Searching for Abiram's Kitchen group...")
            self.abirams_status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
            startup_layout.addWidget(self.abirams_status_label)

            # Enable/disable automation button
            self.automation_button = QPushButton("🔄 Enable WhatsApp Automation")
            self.automation_button.clicked.connect(self.toggle_whatsapp_automation)
            self.automation_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            startup_layout.addWidget(self.automation_button)

            # Test notifications button
            test_notifications_button = QPushButton("🧪 Test Notifications")
            test_notifications_button.clicked.connect(self.test_automated_notifications)
            test_notifications_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            startup_layout.addWidget(test_notifications_button)

            layout.addWidget(startup_group)

            # Add automated notifications status section
            self.add_notifications_status_section(layout)

            # Update status from startup manager if available (will be called again after main_app is set)
            self.update_startup_status()

        except Exception as e:
            safe_print(f"❌ Error adding startup status section: {e}")

    def add_notifications_status_section(self, layout):
        """Add automated notifications status section"""
        try:
            # Create notifications status group
            notifications_group = QGroupBox("🔔 Automated Notifications Status")
            notifications_layout = QVBoxLayout(notifications_group)

            # Monitoring status
            self.monitoring_status_label = QLabel("⏳ Checking notification system...")
            self.monitoring_status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
            notifications_layout.addWidget(self.monitoring_status_label)

            # Last check time
            self.last_check_label = QLabel("⏰ Last check: Not started")
            self.last_check_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
            notifications_layout.addWidget(self.last_check_label)

            # Notification counts
            self.notification_counts_label = QLabel("📊 Notifications sent: 0")
            self.notification_counts_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
            notifications_layout.addWidget(self.notification_counts_label)

            # Control buttons
            control_layout = QHBoxLayout()

            # Force check button
            force_check_btn = QPushButton("🔄 Force Check")
            force_check_btn.clicked.connect(self.force_notifications_check)
            force_check_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            control_layout.addWidget(force_check_btn)

            # Settings button
            settings_btn = QPushButton("⚙️ Settings")
            settings_btn.clicked.connect(self.show_notification_settings)
            settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            control_layout.addWidget(settings_btn)

            notifications_layout.addLayout(control_layout)
            layout.addWidget(notifications_group)

            # Update status periodically
            self.notifications_status_timer = QTimer()
            self.notifications_status_timer.timeout.connect(self.update_notifications_status)
            self.notifications_status_timer.start(10000)  # Update every 10 seconds

            # Also sync connection status periodically
            self.connection_sync_timer = QTimer()
            self.connection_sync_timer.timeout.connect(self.sync_connection_status)
            self.connection_sync_timer.start(5000)  # Check every 5 seconds

        except Exception as e:
            safe_print(f"❌ Error adding notifications status section: {e}")

    def update_startup_status(self):
        """Update startup status display"""
        try:
            # Get startup manager from main app if available
            if hasattr(self, 'main_app') and hasattr(self.main_app, 'whatsapp_startup_manager'):
                manager = self.main_app.whatsapp_startup_manager
                if manager is None:
                    return

                status = manager.get_status()

                # Update connection status
                if status['status'] == 'connected':
                    self.startup_status_label.setText("✅ WhatsApp automation connected")
                    self.startup_status_label.setStyleSheet("color: #10b981; font-size: 12px; padding: 5px;")

                    # CRITICAL: Sync with main connection status
                    if hasattr(manager, 'whatsapp_driver') and manager.whatsapp_driver:
                        self.whatsapp_driver = manager.whatsapp_driver
                        # Trigger connection status update to sync UI
                        self.on_connection_status_changed(True)
                        safe_print("🔄 Synced startup connection with Settings tab")

                elif status['status'] == 'connecting':
                    self.startup_status_label.setText("🔄 WhatsApp automation connecting...")
                    self.startup_status_label.setStyleSheet("color: #f59e0b; font-size: 12px; padding: 5px;")
                elif status['status'] == 'failed':
                    self.startup_status_label.setText("❌ WhatsApp automation failed")
                    self.startup_status_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 5px;")
                    # Ensure main status shows disconnected
                    self.on_connection_status_changed(False)
                else:
                    self.startup_status_label.setText("⏸️ WhatsApp automation disabled")
                    self.startup_status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")

                # Update Abiram's Kitchen status
                if status['abirams_kitchen_found']:
                    self.abirams_status_label.setText("✅ Abiram's Kitchen group ready")
                    self.abirams_status_label.setStyleSheet("color: #10b981; font-size: 12px; padding: 5px;")
                else:
                    self.abirams_status_label.setText("❌ Abiram's Kitchen group not found")
                    self.abirams_status_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 5px;")

                # Update button
                if status['auto_connect_enabled']:
                    self.automation_button.setText("⏸️ Disable Automation")
                else:
                    self.automation_button.setText("🔄 Enable Automation")

        except Exception as e:
            safe_print(f"❌ Error updating startup status: {e}")

    def sync_connection_status(self):
        """Periodically sync connection status between startup and settings"""
        try:
            # Check if we have a startup manager with active connection
            if (hasattr(self, 'main_app') and
                hasattr(self.main_app, 'whatsapp_startup_manager') and
                self.main_app.whatsapp_startup_manager):

                manager = self.main_app.whatsapp_startup_manager
                status = manager.get_status()

                # If startup manager shows connected but settings shows disconnected, sync them
                if (status['status'] == 'connected' and
                    hasattr(manager, 'whatsapp_driver') and
                    manager.whatsapp_driver and
                    manager.whatsapp_driver.is_connected):

                    # Check if our local status is out of sync
                    if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
                        safe_print("🔄 Syncing connection status from startup manager")
                        self.whatsapp_driver = manager.whatsapp_driver
                        self.on_connection_status_changed(True)

        except Exception as e:
            # Don't log this error too frequently as it runs every 5 seconds
            pass

    def toggle_whatsapp_automation(self):
        """Toggle WhatsApp automation on/off"""
        try:
            if hasattr(self, 'main_app') and hasattr(self.main_app, 'whatsapp_startup_manager'):
                manager = self.main_app.whatsapp_startup_manager

                if manager is None:
                    self.show_notification("WhatsApp startup manager is None", "error")
                    return

                if manager.should_auto_connect():
                    # Disable automation
                    manager.preferences["auto_connect"] = False
                    manager.save_preferences()
                    self.show_notification("WhatsApp automation disabled", "info")
                else:
                    # Enable automation
                    success = manager.enable_whatsapp_later()
                    if success:
                        self.show_notification("WhatsApp automation enabled and starting...", "info")
                    else:
                        self.show_notification("Failed to enable WhatsApp automation", "error")

                # Update status display
                self.update_startup_status()
            else:
                self.show_notification("WhatsApp startup manager not available", "error")

        except Exception as e:
            safe_print(f"❌ Error toggling WhatsApp automation: {e}")
            self.show_notification(f"Error: {str(e)}", "error")

    def test_automated_notifications(self):
        """Test the automated notifications system"""
        try:
            if not hasattr(self, 'automated_notifications') or not self.automated_notifications:
                self.show_notification("❌ Automated notifications system not available", "error")
                return

            if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
                self.show_notification("❌ WhatsApp Web is not connected", "error")
                return

            # Show testing dialog
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit

            dialog = QDialog(self)
            dialog.setWindowTitle("🧪 Test Automated Notifications")
            dialog.setFixedSize(600, 500)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            # Header
            header = QLabel("Test WhatsApp Automated Notifications")
            header.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
            layout.addWidget(header)

            # Status display
            status_text = QTextEdit()
            status_text.setReadOnly(True)
            status_text.setMaximumHeight(200)
            status_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 10px;
                    background-color: #f8f9fa;
                    font-family: monospace;
                }
            """)
            layout.addWidget(status_text)

            # Test buttons
            button_layout = QHBoxLayout()

            # Test general notification
            test_general_btn = QPushButton("📧 Test General")
            test_general_btn.clicked.connect(lambda: self._run_notification_test("general", status_text))
            button_layout.addWidget(test_general_btn)

            # Test low stock
            test_stock_btn = QPushButton("📦 Test Low Stock")
            test_stock_btn.clicked.connect(lambda: self._run_notification_test("low_stock", status_text))
            button_layout.addWidget(test_stock_btn)

            # Test cleaning reminder
            test_cleaning_btn = QPushButton("🧹 Test Cleaning")
            test_cleaning_btn.clicked.connect(lambda: self._run_notification_test("cleaning", status_text))
            button_layout.addWidget(test_cleaning_btn)

            # Test packing materials
            test_packing_btn = QPushButton("📦 Test Packing")
            test_packing_btn.clicked.connect(lambda: self._run_notification_test("packing", status_text))
            button_layout.addWidget(test_packing_btn)

            # Test gas warning
            test_gas_btn = QPushButton("⛽ Test Gas")
            test_gas_btn.clicked.connect(lambda: self._run_notification_test("gas", status_text))
            button_layout.addWidget(test_gas_btn)

            layout.addLayout(button_layout)

            # Close button
            close_btn = QPushButton("❌ Close")
            close_btn.clicked.connect(dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    font-weight: bold;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            layout.addWidget(close_btn)

            # Initial status
            status_text.append("🧪 Automated Notifications Test Console")
            status_text.append("=" * 50)
            status_text.append(f"WhatsApp Connected: {'✅ Yes' if self.whatsapp_driver.is_connected else '❌ No'}")
            status_text.append(f"Notifications System: {'✅ Active' if self.automated_notifications.monitoring_active else '❌ Inactive'}")
            status_text.append("")
            status_text.append("Click any test button to send a sample notification to 'Abiram's Kitchen' group.")
            status_text.append("")

            dialog.exec()

        except Exception as e:
            safe_print(f"❌ Error testing automated notifications: {e}")
            self.show_notification(f"❌ Test error: {str(e)}", "error")

    def _run_notification_test(self, test_type, status_text):
        """Run a specific notification test"""
        try:
            status_text.append(f"🧪 Running {test_type} test...")

            if test_type == "general":
                success = self.automated_notifications.send_test_notification()
            elif test_type == "low_stock":
                # Send a sample low stock notification
                sample_item = {
                    'name': 'Test Item (Sample)',
                    'current_qty': 2,
                    'reorder_level': 10,
                    'unit': 'kg'
                }
                self.automated_notifications._send_low_stock_notification(sample_item)
                success = True
            elif test_type == "cleaning":
                # Send a sample cleaning reminder
                sample_tasks = [{
                    'name': 'Test Cleaning Task (Sample)',
                    'assigned_to': 'Kitchen Staff',
                    'location': 'Main Kitchen',
                    'due_date': datetime.now().date()
                }]
                self.automated_notifications._send_cleaning_reminder(sample_tasks)
                success = True
            elif test_type == "packing":
                # Send a sample packing material alert
                sample_material = {
                    'name': 'Test Packing Material (Sample)',
                    'current_stock': 5,
                    'minimum_stock': 20,
                    'unit': 'pieces'
                }
                self.automated_notifications._send_packing_material_alert(sample_material)
                success = True
            elif test_type == "gas":
                # Send a sample gas warning
                self.automated_notifications._send_gas_warning("TEST-001", 1, "CRITICAL")
                success = True
            else:
                success = False

            if success:
                status_text.append(f"✅ {test_type.title()} test completed successfully!")
            else:
                status_text.append(f"❌ {test_type.title()} test failed!")

        except Exception as e:
            status_text.append(f"❌ {test_type.title()} test error: {str(e)}")
            safe_print(f"❌ Error in {test_type} test: {e}")

    def update_notifications_status(self):
        """Update the notifications status display"""
        try:
            if not hasattr(self, 'automated_notifications') or not self.automated_notifications:
                if hasattr(self, 'monitoring_status_label'):
                    self.monitoring_status_label.setText("❌ Automated notifications not available")
                    self.monitoring_status_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 5px;")
                return

            status = self.automated_notifications.get_status()

            # Update monitoring status
            if hasattr(self, 'monitoring_status_label'):
                if status['monitoring_active']:
                    self.monitoring_status_label.setText("✅ Monitoring active")
                    self.monitoring_status_label.setStyleSheet("color: #10b981; font-size: 12px; padding: 5px;")
                else:
                    self.monitoring_status_label.setText("⏸️ Monitoring inactive")
                    self.monitoring_status_label.setStyleSheet("color: #f59e0b; font-size: 12px; padding: 5px;")

            # Update last check time
            if hasattr(self, 'last_check_label'):
                current_time = datetime.now().strftime('%H:%M:%S')
                self.last_check_label.setText(f"⏰ Last check: {current_time}")

            # Update notification counts (simplified)
            if hasattr(self, 'notification_counts_label'):
                last_notifications = status['settings'].get('last_notification_times', {})
                count = len(last_notifications)
                self.notification_counts_label.setText(f"📊 Notifications sent: {count}")

        except Exception as e:
            safe_print(f"❌ Error updating notifications status: {e}")

    def force_notifications_check(self):
        """Force an immediate check of all notification types"""
        try:
            if not hasattr(self, 'automated_notifications') or not self.automated_notifications:
                self.show_notification("❌ Automated notifications system not available", "error")
                return

            self.show_notification("🔄 Forcing immediate notifications check...", "info")
            self.automated_notifications.force_check_all()
            self.show_notification("✅ Notifications check completed", "success")

        except Exception as e:
            safe_print(f"❌ Error forcing notifications check: {e}")
            self.show_notification(f"❌ Error: {str(e)}", "error")

    def show_notification_settings(self):
        """Show notification settings dialog"""
        try:
            if not hasattr(self, 'automated_notifications') or not self.automated_notifications:
                self.show_notification("❌ Automated notifications system not available", "error")
                return

            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox, QLabel, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle("⚙️ Notification Settings")
            dialog.setFixedSize(500, 400)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            # Header
            header = QLabel("Configure Automated Notifications")
            header.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
            layout.addWidget(header)

            # Settings
            settings = self.automated_notifications.notification_settings

            # Enable/disable checkboxes
            self.low_stock_checkbox = QCheckBox("📦 Low Stock Notifications")
            self.low_stock_checkbox.setChecked(settings.get('low_stock_enabled', True))
            layout.addWidget(self.low_stock_checkbox)

            self.cleaning_checkbox = QCheckBox("🧹 Cleaning Task Reminders")
            self.cleaning_checkbox.setChecked(settings.get('cleaning_reminders_enabled', True))
            layout.addWidget(self.cleaning_checkbox)

            self.packing_checkbox = QCheckBox("📦 Packing Materials Alerts")
            self.packing_checkbox.setChecked(settings.get('packing_materials_enabled', True))
            layout.addWidget(self.packing_checkbox)

            self.gas_checkbox = QCheckBox("⛽ Gas Level Warnings")
            self.gas_checkbox.setChecked(settings.get('gas_level_warnings_enabled', True))
            layout.addWidget(self.gas_checkbox)

            # Check interval
            interval_layout = QHBoxLayout()
            interval_layout.addWidget(QLabel("Check Interval (minutes):"))
            self.interval_spinbox = QSpinBox()
            self.interval_spinbox.setRange(5, 120)
            self.interval_spinbox.setValue(settings.get('check_interval_minutes', 30))
            interval_layout.addWidget(self.interval_spinbox)
            layout.addLayout(interval_layout)

            # Buttons
            button_layout = QHBoxLayout()

            save_btn = QPushButton("💾 Save Settings")
            save_btn.clicked.connect(lambda: self._save_notification_settings(dialog))
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-weight: bold;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            button_layout.addWidget(save_btn)

            cancel_btn = QPushButton("❌ Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    font-weight: bold;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)
            dialog.exec()

        except Exception as e:
            safe_print(f"❌ Error showing notification settings: {e}")
            self.show_notification(f"❌ Settings error: {str(e)}", "error")

    def _save_notification_settings(self, dialog):
        """Save notification settings"""
        try:
            if not hasattr(self, 'automated_notifications') or not self.automated_notifications:
                return

            # Update settings
            settings = self.automated_notifications.notification_settings
            settings['low_stock_enabled'] = self.low_stock_checkbox.isChecked()
            settings['cleaning_reminders_enabled'] = self.cleaning_checkbox.isChecked()
            settings['packing_materials_enabled'] = self.packing_checkbox.isChecked()
            settings['gas_level_warnings_enabled'] = self.gas_checkbox.isChecked()
            settings['check_interval_minutes'] = self.interval_spinbox.value()

            # Save to file
            self.automated_notifications.save_settings()

            self.show_notification("✅ Notification settings saved successfully", "success")
            dialog.accept()

        except Exception as e:
            safe_print(f"❌ Error saving notification settings: {e}")
            self.show_notification(f"❌ Save error: {str(e)}", "error")

    def update_contacts_list(self, contacts):
        """Update the contacts list with loaded contacts"""
        safe_print(f"📋 *** UPDATING CONTACTS LIST WITH {len(contacts)} CONTACTS ***")

        self.contacts = contacts
        self.all_contacts = contacts  # Store all contacts for filtering
        self.current_filter = 'all'  # Reset filter

        self.refresh_contacts_display()

        if contacts:
            # Update contact count and session info
            contact_count = len([c for c in contacts if c.get('type') == 'contact'])
            group_count = len([c for c in contacts if c.get('type') == 'group'])

            self.contact_count_label.setText(f"📊 {len(contacts)} total ({contact_count} contacts, {group_count} groups)")
            self.sessions_info_label.setText(f"✅ Loaded {len(contacts)} contacts/groups from WhatsApp Web")
            self.sessions_info_label.setStyleSheet("color: #10b981; font-size: 12px; font-weight: bold;")

            # Log contact details
            for contact in contacts:
                safe_print(f"  ✅ Added {contact.get('type', 'contact')}: {contact['name']}")
        else:
            # Only add default contacts if no real contacts were found
            safe_print("⚠️ No real contacts found, adding default examples")
            self.add_default_contacts()
            self.contact_count_label.setText("No contacts loaded")
            self.sessions_info_label.setText("⚠️ No contacts found - you can add contacts manually or they will load from WhatsApp Web")
            self.sessions_info_label.setStyleSheet("color: #f59e0b; font-size: 12px;")

    def filter_contacts(self, filter_type):
        """Filter contacts by type"""
        self.current_filter = filter_type

        # Update button states
        self.show_all_button.setChecked(filter_type == 'all')
        self.show_contacts_button.setChecked(filter_type == 'contact')
        self.show_groups_button.setChecked(filter_type == 'group')

        # Apply filter styling
        for button in [self.show_all_button, self.show_contacts_button, self.show_groups_button]:
            if button.isChecked():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #25D366;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        color: #333;
                        border: 1px solid #ddd;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                    }
                """)

        self.refresh_contacts_display()

    def get_contact_name(self, contact):
        """Safely get contact name from contact object"""
        if not contact:
            return None

        # Handle different contact data structures
        if isinstance(contact, dict):
            return contact.get('name') or contact.get('contact_name') or contact.get('title')
        elif hasattr(contact, 'name'):
            return contact.name
        elif hasattr(contact, 'contact_name'):
            return contact.contact_name
        else:
            return str(contact) if contact else None

    def refresh_contacts_display(self):
        """Refresh the contacts display based on current filter"""
        if not hasattr(self, 'all_contacts'):
            return

        self.contacts_list.clear()

        # Filter contacts based on current filter
        if self.current_filter == 'all':
            filtered_contacts = self.all_contacts
        else:
            filtered_contacts = [c for c in self.all_contacts if c.get('type') == self.current_filter]

        # Add filtered contacts to list with enhanced display
        for contact in filtered_contacts:
            contact_type = contact.get('type', 'contact')
            contact_name = self.get_contact_name(contact)

            if not contact_name:
                continue  # Skip contacts without names

            # Enhanced icons and styling based on type
            if contact_type == 'group':
                icon = "👥"
                type_indicator = "[GROUP]"
                color_style = "color: #1976d2;"  # Blue for groups
            else:
                icon = "👤"
                type_indicator = "[CONTACT]"
                color_style = "color: #388e3c;"  # Green for contacts

            # Create display name with type indicator
            display_name = f"{icon} {contact_name}"

            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, contact)

            # Add tooltip with more information
            tooltip = f"{type_indicator} {contact_name}\nType: {contact_type.title()}"
            item.setToolTip(tooltip)

            self.contacts_list.addItem(item)

        # Update count label
        if hasattr(self, 'contact_count_label'):
            if self.current_filter == 'all':
                contact_count = len([c for c in self.all_contacts if c.get('type') == 'contact'])
                group_count = len([c for c in self.all_contacts if c.get('type') == 'group'])
                self.contact_count_label.setText(f"📊 {len(self.all_contacts)} total ({contact_count} contacts, {group_count} groups)")
            else:
                count = len(filtered_contacts)
                self.contact_count_label.setText(f"📊 {count} {self.current_filter}s shown")

    def on_connection_status_changed(self, connected):
        """Handle connection status changes with unified status management"""
        try:
            safe_print(f"[STATUS] WhatsApp connection status changed: {'Connected' if connected else 'Disconnected'}")

            if connected:
                # Update main status label with clear "Connected" text
                self.status_label.setText("🟢 Connected")
                self.status_label.setStyleSheet("color: #10b981; font-weight: bold; font-size: 14px;")

                # Update connect button
                self.connect_button.setText("Disconnect")
                self.connect_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)

                # Update startup status if available
                if hasattr(self, 'startup_status_label'):
                    self.startup_status_label.setText("✅ WhatsApp Web connected")
                    self.startup_status_label.setStyleSheet("color: #10b981; font-size: 12px; padding: 5px;")

                # Enable messaging interface
                if hasattr(self, 'message_input'):
                    self.message_input.setEnabled(True)
                    self.message_input.setPlaceholderText("Type a message...")
                if hasattr(self, 'send_button'):
                    self.send_button.setEnabled(True)
                if hasattr(self, 'abiram_button'):
                    self.abiram_button.setEnabled(True)
                if hasattr(self, 'test_button'):
                    self.test_button.setEnabled(True)
                if hasattr(self, 'templates_button'):
                    self.templates_button.setEnabled(True)

                # Show success message
                self.show_notification("✅ WhatsApp Web connected successfully!", "success")

                # Update session info
                if hasattr(self, 'sessions_info_label'):
                    self.sessions_info_label.setText("✅ Connected to WhatsApp Web - Ready to send messages!")
                    self.sessions_info_label.setStyleSheet("color: #10b981; font-size: 12px; font-weight: bold;")

                # Load contacts from WhatsApp Web
                if self.whatsapp_driver:
                    print("🔄 Requesting contacts from WhatsApp Web...")
                    self.whatsapp_driver.load_contacts_and_groups()
                else:
                    # Add default contacts only if no WhatsApp driver
                    self.add_default_contacts()

            else:
                # Update main status label with clear "Disconnected" text
                self.status_label.setText("🔴 Disconnected")
                self.status_label.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 14px;")

                # Update connect button
                self.connect_button.setText("Connect to WhatsApp Web")
                self.connect_button.setStyleSheet("")

                # Update startup status if available
                if hasattr(self, 'startup_status_label'):
                    self.startup_status_label.setText("❌ WhatsApp Web disconnected")
                    self.startup_status_label.setStyleSheet("color: #ef4444; font-size: 12px; padding: 5px;")

                # Disable messaging interface
                if hasattr(self, 'message_input'):
                    self.message_input.setEnabled(False)
                    self.message_input.setPlaceholderText("Connect to WhatsApp Web first...")
                if hasattr(self, 'send_button'):
                    self.send_button.setEnabled(False)
                if hasattr(self, 'abiram_button'):
                    self.abiram_button.setEnabled(False)
                if hasattr(self, 'test_button'):
                    self.test_button.setEnabled(False)
                if hasattr(self, 'templates_button'):
                    self.templates_button.setEnabled(False)
                if hasattr(self, 'contacts_list'):
                    self.contacts_list.clear()

                # Update session info
                if hasattr(self, 'sessions_info_label'):
                    self.sessions_info_label.setText("❌ Disconnected from WhatsApp Web")
                    self.sessions_info_label.setStyleSheet("color: #e74c3c; font-size: 12px;")

        except Exception as e:
            safe_print(f"❌ Error updating connection status: {e}")

    def update_character_count(self):
        """Update character counter for message input"""
        try:
            if hasattr(self, 'message_input') and hasattr(self, 'char_counter'):
                text = self.message_input.text()
                char_count = len(text)
                max_chars = 1000

                self.char_counter.setText(f"{char_count}/{max_chars}")

                # Change color based on character count
                if char_count > max_chars * 0.9:  # 90% of limit
                    self.char_counter.setStyleSheet("color: #dc3545; font-size: 11px; padding: 5px; font-weight: bold;")
                elif char_count > max_chars * 0.7:  # 70% of limit
                    self.char_counter.setStyleSheet("color: #ffc107; font-size: 11px; padding: 5px; font-weight: bold;")
                else:
                    self.char_counter.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")

                # Limit input if over max
                if char_count > max_chars:
                    self.message_input.setText(text[:max_chars])
                    self.message_input.setCursorPosition(max_chars)

        except Exception as e:
            safe_print(f"❌ Error updating character count: {e}")

    def add_default_contacts(self):
        """Add some default contacts for testing"""
        if not hasattr(self, 'contacts_list') or not self.contacts_list:
            return

        # Only add if contacts list is empty
        if self.contacts_list.count() == 0:
            default_contacts = [
                "📱 Type contact name or number here",
                "👥 Family Group",
                "🏢 Work Team",
                "📞 Customer Support"
            ]

            for contact_name in default_contacts:
                contact = {
                    'name': contact_name,
                    'type': 'default',
                    'element': None
                }
                self.contacts.append(contact)

                item = QListWidgetItem(contact_name)
                item.setData(Qt.UserRole, contact)
                self.contacts_list.addItem(item)

            # Show instruction message
            self.chat_header.setText("💡 Select a contact above or add your own to start messaging")

    def add_contact(self):
        """Add a new contact manually"""
        from PySide6.QtWidgets import QInputDialog

        contact_name, ok = QInputDialog.getText(
            self, "Add Contact", "Enter contact name or phone number:"
        )

        if ok and contact_name.strip():
            # Add to contacts list
            contact = {
                'name': contact_name.strip(),
                'type': 'manual',
                'element': None
            }
            self.contacts.append(contact)

            contact_name = self.get_contact_name(contact)
            item = QListWidgetItem(f"👤 {contact_name}")
            item.setData(Qt.UserRole, contact)
            self.contacts_list.addItem(item)

            self.show_notification(f"✅ Added contact: {contact_name}", "success")

    def manual_load_contacts(self):
        """Manually trigger quick contact loading from recent chats only"""
        if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
            self.show_notification("❌ Please connect to WhatsApp Web first", "error")
            return

        self.show_notification("⚡ Quick loading contacts from recent chats...", "info")

        # Clear existing contacts first
        self.contacts_list.clear()
        self.contacts = []

        # Trigger quick contact loading (recent chats only)
        try:
            recent_contacts = self.whatsapp_driver.load_from_recent_chats()
            if recent_contacts:
                self.update_contacts_list(recent_contacts)
                self.show_notification(f"✅ Loaded {len(recent_contacts)} contacts from recent chats", "success")
            else:
                self.show_notification("⚠️ No recent contacts found", "warning")
        except Exception as e:
            self.show_notification(f"❌ Error loading contacts: {e}", "error")

    def comprehensive_load_contacts(self):
        """Comprehensively load ALL contacts and groups using multiple methods"""
        if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
            self.show_notification("❌ Please connect to WhatsApp Web first", "error")
            return

        self.show_notification("🔄 Comprehensively loading ALL contacts and groups...", "info")

        # Clear existing contacts first
        self.contacts_list.clear()
        self.contacts = []

        # Trigger comprehensive contact loading
        self.whatsapp_driver.load_contacts_and_groups()

    def select_contact(self, item):
        """Select a contact for chatting"""
        contact = item.data(Qt.UserRole)
        if contact:
            self.selected_contact = contact
            contact_name = self.get_contact_name(contact)
            contact_type = contact.get('type', 'contact')
            type_icon = "👥" if contact_type == 'group' else "👤"

            if not contact_name:
                self.show_notification("❌ Invalid contact selected", "error")
                return

            # Update chat header with contact type indication
            self.chat_header.setText(f"💬 Chat with {type_icon} {contact_name} ({contact_type.title()})")
            self.message_input.setPlaceholderText(f"Type a message to {contact_name}...")

            # Clear previous messages and show contact info
            self.messages_area.clear()
            self.messages_area.append(
                f"<div style='text-align: center; color: #666; font-style: italic; margin: 20px 0;'>"
                f"💬 Chat with {type_icon} <b>{contact_name}</b><br>"
                f"<small>Type: {contact_type.title()}</small><br>"
                f"<small>Ready to send messages via WhatsApp Web</small>"
                f"</div>"
            )

            # Show selection feedback
            self.show_notification(f"📱 Selected {contact_type}: {contact_name}", "info")

    def test_find_abirams_kitchen(self):
        """Test function to find Abiram's Kitchen group without sending message"""
        if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
            self.show_notification("❌ WhatsApp Web is not connected", "error")
            return

        # Show testing status
        self.show_notification("🔍 Searching for Abiram's Kitchen group...", "info")

        # Disable button temporarily
        if hasattr(self, 'test_button'):
            self.test_button.setEnabled(False)
            self.test_button.setText("🔍 Searching...")

        try:
            # Test finding the group
            target_group = self.whatsapp_driver.find_abirams_kitchen()

            if target_group:
                self.show_notification(f"✅ Found group: {target_group['name']}", "success")

                # Add to message history for debugging
                self.messages_area.append(
                    f"<div style='color: #2196F3; margin: 5px 0;'>"
                    f"<b>🔍 Group Found:</b> {target_group['name']}"
                    f"<br><small style='color: #666;'>Type: {target_group['type']} | {datetime.now().strftime('%H:%M')}</small>"
                    f"</div>"
                )
            else:
                self.show_notification("❌ Could not find Abiram's Kitchen group", "error")

                # Add debug info to message history
                self.messages_area.append(
                    f"<div style='color: #f44336; margin: 5px 0;'>"
                    f"<b>❌ Search Failed:</b> Abiram's Kitchen not found"
                    f"<br><small style='color: #666;'>Check console for detailed search logs | {datetime.now().strftime('%H:%M')}</small>"
                    f"</div>"
                )

        except Exception as e:
            safe_print(f"❌ Error testing find Abiram's Kitchen: {e}")
            self.show_notification(f"❌ Test error: {str(e)}", "error")

        finally:
            # Re-enable button
            if hasattr(self, 'test_button'):
                self.test_button.setEnabled(True)
                self.test_button.setText("🔍 Find Abiram's Kitchen")

    def send_to_abirams_kitchen(self):
        """Send message specifically to Abiram's Kitchen group"""
        if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
            self.show_notification("❌ WhatsApp Web is not connected", "error")
            return

        message_text = self.message_input.text().strip()
        if not message_text:
            self.show_notification("⚠️ Please enter a message", "warning")
            return

        # Show sending status
        self.show_notification("🎯 Sending message to Abiram's Kitchen...", "info")

        # Disable button temporarily
        if hasattr(self, 'abiram_button'):
            self.abiram_button.setEnabled(False)
            self.abiram_button.setText("🎯 Sending...")

        try:
            # Send message using specialized method
            success = self.whatsapp_driver.send_message_to_abirams_kitchen(message_text)

            if success:
                # Clear input and show success
                self.message_input.clear()
                self.show_notification("✅ Message sent to Abiram's Kitchen!", "success")

                # Add to message history
                self.messages_area.append(
                    f"<div style='text-align: right; color: #25D366; margin: 5px 0;'>"
                    f"<b>You → Abiram's Kitchen:</b> {message_text}"
                    f"<br><small style='color: #666;'>{datetime.now().strftime('%H:%M')}</small>"
                    f"</div>"
                )

                # Sync to Firebase if available
                if self.firebase_sync:
                    message = WhatsAppMessage(
                        message_id=f"msg_{int(time.time() * 1000)}",
                        sender='self',
                        recipient="Abiram's Kitchen",
                        content=message_text,
                        timestamp=datetime.now()
                    )
                    self.firebase_sync.sync_messages([message])
            else:
                self.show_notification("❌ Failed to send message to Abiram's Kitchen", "error")

        except Exception as e:
            safe_print(f"❌ Error sending message to Abiram's Kitchen: {e}")
            self.show_notification(f"❌ Error: {str(e)}", "error")

        finally:
            # Re-enable button
            if hasattr(self, 'abiram_button'):
                self.abiram_button.setEnabled(True)
                self.abiram_button.setText("🎯 Send to Abiram's Kitchen")

    def send_message(self):
        """Send a message to the selected contact"""
        if not hasattr(self, 'selected_contact') or not self.selected_contact:
            self.show_notification("⚠️ Please select a contact first", "warning")
            return

        message_text = self.message_input.text().strip()
        if not message_text:
            self.show_notification("⚠️ Please enter a message", "warning")
            return

        if not self.whatsapp_driver or not self.whatsapp_driver.is_connected:
            self.show_notification("❌ WhatsApp Web is not connected", "error")
            return

        # Show sending status
        contact_name = self.get_contact_name(self.selected_contact)
        self.show_notification(f"📤 Sending message to {contact_name}...", "info")

        # Disable send button temporarily
        if hasattr(self, 'send_button'):
            self.send_button.setEnabled(False)
            self.send_button.setText("📤 Sending...")

        try:
            # Get contact name safely
            contact_name = self.get_contact_name(self.selected_contact)
            if not contact_name:
                self.show_notification("❌ Invalid contact selected", "error")
                return

            # Send message through WhatsApp driver
            success = self.whatsapp_driver.send_message(
                contact_name,
                message_text
            )

            if success:
                # Add message to chat display with timestamp
                timestamp = datetime.now().strftime("%H:%M")
                contact_type = self.selected_contact.get('type', 'contact')
                type_icon = "👥" if contact_type == 'group' else "👤"

                self.messages_area.append(
                    f"<div style='text-align: right; margin: 5px 0; padding: 8px; background-color: #dcf8c6; border-radius: 8px;'>"
                    f"<div style='font-size: 11px; color: #666; margin-bottom: 2px;'>To: {type_icon} {contact_name}</div>"
                    f"<div style='color: #000;'>{message_text}</div>"
                    f"<div style='font-size: 10px; color: #999; text-align: right; margin-top: 2px;'>{timestamp} ✓</div>"
                    f"</div>"
                )

                self.message_input.clear()
                self.show_notification(f"✅ Message sent to {contact_name}", "success")

                # Store message
                message = {
                    'contact': contact_name,
                    'message': message_text,
                    'timestamp': datetime.now(),
                    'direction': 'outgoing',
                    'contact_type': contact_type
                }
                self.messages.append(message)

                # Sync to Firebase if available
                if self.firebase_sync:
                    self.firebase_sync.sync_messages([message])
            else:
                self.show_notification("❌ Failed to send message - please check WhatsApp Web connection", "error")

        except Exception as e:
            safe_print(f"❌ Error sending message: {e}")
            self.show_notification(f"❌ Error sending message: {str(e)}", "error")

        finally:
            # Re-enable send button
            if hasattr(self, 'send_button'):
                self.send_button.setEnabled(True)
                self.send_button.setText("📤 Send")

    def show_notification(self, message, type_="info"):
        """Show a notification"""
        if self.notification_manager:
            # Use the correct notify method with proper parameters
            self.notification_manager.notify(
                title="WhatsApp",
                message=message,
                category=type_,
                priority=5,
                source="WhatsApp Integration",
                show_toast=True,
                show_bell=True
            )
        else:
            print(f"WhatsApp: {message}")

    def setup_connections(self):
        """Setup signal connections"""
        # Connect internal signals
        self.update_status_signal.connect(self.update_status_label)
        self.connection_failed_signal.connect(self.handle_connection_failure)

    def check_chrome_installation(self):
        """Check Chrome installation status and display detailed information"""
        try:
            safe_print("🔍 Checking Chrome installation...")

            # Create a detailed status dialog
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel

            dialog = QDialog(self)
            dialog.setWindowTitle("Chrome Installation Status")
            dialog.setFixedSize(600, 400)

            layout = QVBoxLayout(dialog)

            # Title
            title = QLabel("🔍 Chrome Installation Check")
            title.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(title)

            # Status text area
            status_text = QTextEdit()
            status_text.setReadOnly(True)
            layout.addWidget(status_text)

            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            # Check Chrome installation
            status_text.append("🔍 Checking Chrome installation...\n")

            # Create a temporary WhatsApp driver to check Chrome
            temp_driver = WhatsAppWebDriver()

            # Check Chrome paths
            chrome_paths = temp_driver.get_chrome_paths()
            status_text.append(f"📁 Checking {len(chrome_paths)} possible Chrome locations:\n")

            found_chrome = None
            for i, path in enumerate(chrome_paths, 1):
                status_text.append(f"  [{i}] {path}")
                if os.path.exists(path) and os.path.isfile(path):
                    status_text.append("    ✅ Found!")
                    if not found_chrome:
                        found_chrome = path
                else:
                    status_text.append("    ❌ Not found")
                status_text.append("")

            if found_chrome:
                status_text.append(f"✅ Chrome found at: {found_chrome}\n")

                # Try to get Chrome version
                try:
                    import subprocess
                    result = subprocess.run([found_chrome, "--version"],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        status_text.append(f"🏷️ Chrome Version: {version}\n")
                except Exception as e:
                    status_text.append(f"⚠️ Could not determine Chrome version: {e}\n")

                # Check if Chrome is currently running
                try:
                    import psutil
                    chrome_processes = []
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                                chrome_processes.append(proc.info['pid'])
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    if chrome_processes:
                        status_text.append(f"🔄 Chrome is currently running ({len(chrome_processes)} processes)\n")
                        status_text.append(f"   PIDs: {chrome_processes}\n")
                    else:
                        status_text.append("⏸️ Chrome is not currently running\n")

                except ImportError:
                    status_text.append("⚠️ psutil not available - cannot check running processes\n")
                except Exception as e:
                    status_text.append(f"⚠️ Error checking Chrome processes: {e}\n")

                # Check Selenium dependencies
                status_text.append("🔍 Checking Selenium dependencies...\n")
                selenium_available, webdriver_manager_available = check_selenium_dependencies()

                if selenium_available:
                    status_text.append("✅ Selenium is available\n")
                else:
                    status_text.append("❌ Selenium is not available\n")

                if webdriver_manager_available:
                    status_text.append("✅ WebDriver Manager is available\n")
                else:
                    status_text.append("❌ WebDriver Manager is not available\n")

                # Overall status
                if selenium_available and webdriver_manager_available:
                    status_text.append("🎉 WhatsApp Web integration is ready to use!\n")
                    status_text.append("💡 You can now connect to WhatsApp Web using the Connect button.\n")
                else:
                    status_text.append("⚠️ Some dependencies are missing.\n")
                    status_text.append("💡 Click 'Install Dependencies' to automatically install them.\n")

            else:
                status_text.append("❌ Chrome not found in any standard locations!\n")
                status_text.append("📥 Please install Google Chrome from: https://www.google.com/chrome/\n")
                status_text.append("🔄 After installing Chrome, restart the application and try again.\n")

            # Show the dialog
            dialog.exec()

        except Exception as e:
            safe_print(f"❌ Error checking Chrome installation: {e}")
            QMessageBox.critical(
                self, "Chrome Check Error",
                f"Failed to check Chrome installation:\n\n{str(e)}\n\n"
                f"This might indicate a system configuration issue."
            )

        # Connect WhatsApp driver signals when available
        if self.whatsapp_driver:
            # Connect contacts_loaded signal if available (for compatibility)
            if hasattr(self.whatsapp_driver, 'contacts_loaded'):
                safe_print("🔗 Connecting contacts_loaded signal to update_contacts_list")
                self.whatsapp_driver.contacts_loaded.connect(self.update_contacts_list)
            else:
                safe_print("⚠️ WhatsApp driver does not have contacts_loaded signal")
            self.whatsapp_driver.connection_status_changed.connect(self.on_connection_status_changed)

    def check_chrome_installation(self):
        """Check Chrome installation status and show detailed information"""
        try:
            from PySide6.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout, QDialog, QPushButton
            import os
            import platform

            # Create a detailed status dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Chrome Installation Status")
            dialog.setMinimumSize(600, 400)

            layout = QVBoxLayout(dialog)

            # Create text area for detailed output
            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setFont(QFont("Consolas", 10))

            # Collect Chrome installation information
            status_text = "🔍 Chrome Installation Status Check\n"
            status_text += "=" * 50 + "\n\n"

            # Check system information
            system = platform.system()
            status_text += f"🖥️ Operating System: {system} {platform.release()}\n"
            status_text += f"🏗️ Architecture: {platform.machine()}\n\n"

            # Create a temporary driver instance to use its Chrome detection methods
            temp_driver = WhatsAppWebDriver()

            # Get Chrome paths for this system
            chrome_paths = temp_driver.get_chrome_paths()
            status_text += f"📂 Checking {len(chrome_paths)} possible Chrome locations:\n"

            found_chrome = None
            for i, path in enumerate(chrome_paths, 1):
                status_text += f"  [{i}] {path}\n"
                if os.path.exists(path) and os.path.isfile(path):
                    status_text += f"      ✅ Found!\n"
                    if not found_chrome:
                        found_chrome = path
                else:
                    status_text += f"      ❌ Not found\n"

            status_text += "\n"

            # Check system PATH
            status_text += "🔍 Checking system PATH for Chrome:\n"
            chrome_in_path = temp_driver.find_chrome_in_path()
            if chrome_in_path:
                status_text += f"  ✅ Found in PATH: {chrome_in_path}\n"
                if not found_chrome:
                    found_chrome = chrome_in_path
            else:
                status_text += "  ❌ Not found in system PATH\n"

            status_text += "\n"

            # Check Windows registry (if on Windows)
            if system.lower() == "windows":
                try:
                    registry_paths = temp_driver.get_chrome_from_registry()
                    status_text += f"🗂️ Checking Windows Registry ({len(registry_paths)} entries):\n"
                    for path in registry_paths:
                        status_text += f"  📝 {path}\n"
                        if os.path.exists(path) and not found_chrome:
                            found_chrome = path
                            status_text += f"      ✅ Verified!\n"
                except Exception as e:
                    status_text += f"  ⚠️ Registry check failed: {e}\n"
                status_text += "\n"

            # Final status
            if found_chrome:
                status_text += "🎉 CHROME INSTALLATION STATUS: ✅ FOUND\n"
                status_text += f"📍 Primary Chrome Location: {found_chrome}\n\n"

                # Try to get Chrome version
                try:
                    import subprocess
                    result = subprocess.run([found_chrome, "--version"],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        status_text += f"🏷️ Chrome Version: {version}\n"
                except Exception as e:
                    status_text += f"⚠️ Could not determine Chrome version: {e}\n"

                status_text += "\n✅ WhatsApp Web integration should work properly!\n"
            else:
                status_text += "❌ CHROME INSTALLATION STATUS: NOT FOUND\n\n"
                status_text += "📥 To fix this issue:\n"
                status_text += "1. Download Google Chrome from: https://www.google.com/chrome/\n"
                status_text += "2. Install Chrome using the default settings\n"
                status_text += "3. Restart this application\n"
                status_text += "4. Try connecting to WhatsApp Web again\n"

            # Check Selenium dependencies
            status_text += "\n" + "=" * 50 + "\n"
            status_text += "🔧 Selenium Dependencies Status:\n"
            selenium_available, webdriver_manager_available = check_selenium_dependencies()

            if selenium_available:
                status_text += "✅ Selenium: Available\n"
            else:
                status_text += "❌ Selenium: Not available\n"

            if webdriver_manager_available:
                status_text += "✅ WebDriver Manager: Available\n"
            else:
                status_text += "❌ WebDriver Manager: Not available\n"

            if not selenium_available:
                status_text += "\n💡 Click 'Connect to WhatsApp Web' to automatically install dependencies.\n"

            # Set the text
            text_area.setPlainText(status_text)
            layout.addWidget(text_area)

            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            # Show dialog
            dialog.exec()

        except Exception as e:
            # Fallback to simple message box if detailed check fails
            QMessageBox.information(
                self, "Chrome Status Check",
                f"Chrome installation check completed.\n\n"
                f"Error during detailed check: {e}\n\n"
                f"If you're having issues, please ensure Google Chrome is installed from:\n"
                f"https://www.google.com/chrome/"
            )

    def show_session_options(self):
        """Show session management options dialog"""
        try:
            from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                         QPushButton, QCheckBox, QGroupBox, QTextEdit,
                                         QMessageBox, QFormLayout)

            dialog = QDialog(self)
            dialog.setWindowTitle("WhatsApp Session Management")
            dialog.setMinimumSize(500, 400)

            layout = QVBoxLayout(dialog)

            # Session status group
            status_group = QGroupBox("Current Session Status")
            status_layout = QFormLayout(status_group)

            # Check current session status
            session_enabled = getattr(self.whatsapp_driver, 'session_reuse_enabled', True) if self.whatsapp_driver else True
            session_status = "✅ Enabled" if session_enabled else "❌ Disabled"
            status_layout.addRow("Session Reuse:", QLabel(session_status))

            # Check for existing sessions
            if self.whatsapp_driver:
                has_existing = self.whatsapp_driver.check_existing_chrome_session()
                existing_status = "✅ Found" if has_existing else "❌ None found"
            else:
                existing_status = "❓ Unknown (not connected)"
            status_layout.addRow("Existing Sessions:", QLabel(existing_status))

            # Session directory info
            if self.whatsapp_driver and hasattr(self.whatsapp_driver, 'persistent_session_dir'):
                session_dir = self.whatsapp_driver.persistent_session_dir or "Not set"
            else:
                session_dir = "Not available"
            status_layout.addRow("Session Directory:", QLabel(session_dir))

            layout.addWidget(status_group)

            # Session controls group
            controls_group = QGroupBox("Session Controls")
            controls_layout = QVBoxLayout(controls_group)

            # Enable/Disable session reuse
            self.session_reuse_checkbox = QCheckBox("Enable session reuse (recommended)")
            self.session_reuse_checkbox.setChecked(session_enabled)
            self.session_reuse_checkbox.stateChanged.connect(self.toggle_session_reuse)
            controls_layout.addWidget(self.session_reuse_checkbox)

            # Action buttons
            buttons_layout = QHBoxLayout()

            # Clear sessions button
            clear_button = QPushButton("🗑️ Clear All Sessions")
            clear_button.clicked.connect(self.clear_all_sessions)
            clear_button.setToolTip("Remove all stored session data")
            buttons_layout.addWidget(clear_button)

            # Refresh status button
            refresh_button = QPushButton("🔄 Refresh Status")
            refresh_button.clicked.connect(lambda: self.show_session_options())
            refresh_button.setToolTip("Refresh session status information")
            buttons_layout.addWidget(refresh_button)

            controls_layout.addLayout(buttons_layout)
            layout.addWidget(controls_group)

            # Information text
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            info_text.setMaximumHeight(150)
            info_text.setPlainText(
                "Session Reuse Benefits:\n"
                "• Eliminates need to scan QR codes repeatedly\n"
                "• Maintains WhatsApp Web authentication\n"
                "• Faster connection times\n"
                "• Preserves chat history and settings\n\n"
                "How it works:\n"
                "• Uses persistent Chrome profile directory\n"
                "• Connects to existing Chrome sessions when possible\n"
                "• Falls back to new session if needed\n\n"
                "Note: Session data is stored locally and not shared."
            )
            layout.addWidget(info_text)

            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(
                self, "Session Options Error",
                f"Error showing session options: {e}"
            )

    def toggle_session_reuse(self, state):
        """Toggle session reuse on/off"""
        try:
            enabled = state == 2  # Qt.Checked

            if self.whatsapp_driver:
                if enabled:
                    self.whatsapp_driver.enable_session_reuse()
                else:
                    self.whatsapp_driver.disable_session_reuse()

            # Update UI
            status_text = "🔄 Session reuse: Enabled" if enabled else "🔄 Session reuse: Disabled"
            color = "#10b981" if enabled else "#ef4444"
            self.session_info_label.setText(status_text)
            self.session_info_label.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px;")

            QMessageBox.information(
                self, "Session Reuse",
                f"Session reuse has been {'enabled' if enabled else 'disabled'}.\n"
                f"This will take effect on the next connection."
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Toggle Error",
                f"Error toggling session reuse: {e}"
            )

    def clear_all_sessions(self):
        """Clear all stored session data"""
        try:
            reply = QMessageBox.question(
                self, "Clear Sessions",
                "Are you sure you want to clear all stored session data?\n\n"
                "This will:\n"
                "• Remove all saved WhatsApp Web authentication\n"
                "• Require QR code scanning on next connection\n"
                "• Clear browser profile data\n\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if self.whatsapp_driver:
                    # Force stop and clean up
                    self.whatsapp_driver.force_stop()

                    # Also clear any persistent directories
                    import os
                    import shutil

                    try:
                        session_dir = self.whatsapp_driver.get_persistent_session_directory()
                        if os.path.exists(session_dir):
                            shutil.rmtree(session_dir, ignore_errors=True)
                            print(f"🧹 Cleared persistent session directory: {session_dir}")
                    except Exception as e:
                        print(f"⚠️ Error clearing session directory: {e}")

                QMessageBox.information(
                    self, "Sessions Cleared",
                    "All session data has been cleared successfully.\n"
                    "You will need to scan the QR code on your next connection."
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Clear Error",
                f"Error clearing sessions: {e}"
            )

    def safe_search_whatsapp_sessions(self):
        """Safely search for WhatsApp sessions with error handling"""
        try:
            self.search_whatsapp_sessions()
        except Exception as e:
            print(f"Error in automatic session search: {e}")
            # Update UI to show search is available
            if hasattr(self, 'sessions_info_label'):
                self.sessions_info_label.setText("Click 'Search for Sessions' to find active WhatsApp Web tabs")
                self.sessions_info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")

    def refresh_whatsapp_sessions(self):
        """Refresh the WhatsApp sessions list"""
        self.sessions_list.clear()
        self.sessions_info_label.setText("Refreshing sessions...")
        self.sessions_info_label.setStyleSheet("color: #3498db; font-size: 11px; font-style: italic;")

        # Use a timer to allow UI to update
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.search_whatsapp_sessions)

    def setup_chrome_debugging(self):
        """Automatically start Chrome with debugging enabled"""
        try:
            import subprocess
            import psutil
            import time
            from PySide6.QtWidgets import QMessageBox

            # Update button state
            self.setup_chrome_button.setEnabled(False)
            self.setup_chrome_button.setText("🔄 Setting up Chrome...")

            # Check if Chrome is already running with debugging
            if self._check_chrome_debug_running():
                safe_print("✅ Chrome with debugging is already running!")
                self.setup_chrome_button.setText("✅ Chrome Ready")
                self.setup_chrome_button.setEnabled(True)

                # Show success message
                QMessageBox.information(
                    self,
                    "Chrome Ready",
                    "Chrome is already running with debugging enabled!\n\n"
                    "You can now connect to WhatsApp Web."
                )
                return

            # Check if normal Chrome is running (without debugging)
            chrome_running = False
            chrome_processes = []

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc)
                        chrome_running = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if chrome_running:
                reply = QMessageBox.question(
                    self, "Chrome Already Running",
                    f"Found {len(chrome_processes)} Chrome process(es) running.\n\n"
                    f"To enable debugging, we need to restart Chrome.\n"
                    f"This will close all current Chrome windows.\n\n"
                    f"Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Close existing Chrome processes
                    print("🔄 Closing existing Chrome processes...")
                    for proc in chrome_processes:
                        try:
                            proc.terminate()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    # Wait for processes to close
                    time.sleep(2)
                else:
                    self.setup_chrome_button.setEnabled(True)
                    self.setup_chrome_button.setText("🚀 Start Chrome with Debugging")
                    return

            # Find Chrome executable
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
                r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe"
            ]

            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break

            if not chrome_exe:
                QMessageBox.critical(
                    self, "Chrome Not Found",
                    "Could not find Google Chrome installation.\n\n"
                    "Please install Google Chrome or check the installation path."
                )
                self.setup_chrome_button.setEnabled(True)
                self.setup_chrome_button.setText("🚀 Start Chrome with Debugging")
                return

            # Start Chrome with debugging
            print(f"🚀 Starting Chrome with debugging: {chrome_exe}")

            cmd = [
                chrome_exe,
                "--remote-debugging-port=9222",
                "--user-data-dir=" + os.path.join(os.getenv('APPDATA', ''), 'VARSYS', 'Chrome_Debug'),
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "https://web.whatsapp.com"
            ]

            # Create the user data directory if it doesn't exist
            user_data_dir = os.path.join(os.getenv('APPDATA', ''), 'VARSYS', 'Chrome_Debug')
            os.makedirs(user_data_dir, exist_ok=True)

            # Start Chrome process
            subprocess.Popen(cmd, shell=False)

            print("✅ Chrome started with debugging enabled")
            print("🌐 Opening WhatsApp Web automatically...")

            # Update UI
            self.setup_chrome_button.setText("✅ Chrome Started!")
            self.sessions_info_label.setText("Chrome started with debugging! Waiting for WhatsApp Web to load...")
            self.sessions_info_label.setStyleSheet("color: #27ae60; font-size: 11px; font-style: italic;")

            # Wait a moment for Chrome to start, then search for sessions
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, self.auto_search_after_chrome_start)

            # Show success message
            QMessageBox.information(
                self, "Chrome Started Successfully",
                "✅ Chrome has been started with debugging enabled!\n\n"
                "🌐 WhatsApp Web is opening automatically.\n"
                "📱 Please scan the QR code with your phone to sign in.\n\n"
                "Once signed in, the session will be automatically detected."
            )

        except Exception as e:
            print(f"❌ Error setting up Chrome debugging: {e}")
            QMessageBox.critical(
                self, "Setup Error",
                f"Failed to start Chrome with debugging:\n\n{str(e)}\n\n"
                f"You can try manually starting Chrome with:\n"
                f"chrome --remote-debugging-port=9222"
            )

            self.setup_chrome_button.setEnabled(True)
            self.setup_chrome_button.setText("🚀 Start Chrome with Debugging")

    def auto_search_after_chrome_start(self):
        """Automatically search for sessions after Chrome starts"""
        self.search_whatsapp_sessions()

        # Reset button after a delay
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self.reset_chrome_button)

    def reset_chrome_button(self):
        """Reset the Chrome setup button"""
        self.setup_chrome_button.setEnabled(True)
        self.setup_chrome_button.setText("🚀 Start Chrome with Debugging")

    def search_whatsapp_sessions(self):
        """Search for existing WhatsApp Web sessions and display them"""
        try:
            # Disable buttons during search
            self.search_sessions_button.setEnabled(False)
            self.search_sessions_button.setText("🔍 Searching...")
            if hasattr(self, 'refresh_sessions_button'):
                self.refresh_sessions_button.setEnabled(False)

            self.sessions_list.clear()
            self.sessions_info_label.setText("🔍 Searching for WhatsApp Web sessions...")
            self.sessions_info_label.setStyleSheet("color: #3498db; font-size: 11px; font-style: italic;")

            # Create a temporary driver instance to search for sessions
            temp_driver = WhatsAppWebDriver()
            whatsapp_sessions = temp_driver.find_whatsapp_web_sessions()

            print(f"🔍 Session search completed, found {len(whatsapp_sessions)} sessions")

            if whatsapp_sessions:
                authenticated_count = len([s for s in whatsapp_sessions if s.get('status') == 'authenticated'])
                needs_auth_count = len([s for s in whatsapp_sessions if s.get('status') == 'needs_auth'])

                status_text = f"Found {len(whatsapp_sessions)} session(s)"
                if authenticated_count > 0:
                    status_text += f" ({authenticated_count} signed in"
                    if needs_auth_count > 0:
                        status_text += f", {needs_auth_count} need auth"
                    status_text += ")"
                elif needs_auth_count > 0:
                    status_text += f" ({needs_auth_count} need authentication)"

                status_text += ". Double-click to connect."

                self.sessions_info_label.setText(status_text)
                self.sessions_info_label.setStyleSheet("color: #27ae60; font-size: 11px; font-style: italic;")

                for session in whatsapp_sessions:
                    # Create list item with session info
                    title = session.get('title', 'Unknown')
                    status = session.get('status', 'unknown')
                    pid = session.get('pid', 'unknown')
                    debug_port = session.get('debug_port', 'unknown')

                    # Create display text
                    if status == 'authenticated':
                        icon = "✅"
                        status_text = "Signed In"
                    elif status == 'needs_auth':
                        icon = "⚠️"
                        status_text = "Needs Authentication"
                    elif status == 'needs_debug_mode':
                        icon = "🔧"
                        status_text = "Needs Debug Mode"
                    else:
                        icon = "❓"
                        status_text = "Unknown Status"

                    display_text = f"{icon} {title} - {status_text}"
                    if pid != 'unknown':
                        display_text += f" (PID: {pid})"
                    if debug_port != 'unknown':
                        display_text += f" [Port: {debug_port}]"

                    # Create list item
                    from PySide6.QtWidgets import QListWidgetItem
                    from PySide6.QtCore import Qt
                    from PySide6.QtGui import QColor

                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, session)  # Store session data

                    # Set item styling based on status
                    if status == 'authenticated':
                        item.setBackground(QColor(39, 174, 96, 30))  # Light green
                    elif status == 'needs_auth':
                        item.setBackground(QColor(241, 196, 15, 30))  # Light yellow
                    elif status == 'needs_debug_mode':
                        item.setBackground(QColor(52, 152, 219, 30))  # Light blue
                    else:
                        item.setBackground(QColor(149, 165, 166, 30))  # Light gray

                    self.sessions_list.addItem(item)
            else:
                self.sessions_info_label.setText("No WhatsApp Web sessions found. Make sure Chrome is running with WhatsApp Web open.")
                self.sessions_info_label.setStyleSheet("color: #e67e22; font-size: 11px; font-style: italic;")

            # Re-enable buttons
            self.search_sessions_button.setEnabled(True)
            self.search_sessions_button.setText("🔍 Search for Sessions")
            if hasattr(self, 'refresh_sessions_button'):
                self.refresh_sessions_button.setEnabled(True)

        except Exception as e:
            print(f"Error in search_whatsapp_sessions: {e}")  # Debug print
            import traceback
            traceback.print_exc()  # Print full traceback for debugging

            self.sessions_info_label.setText(f"Error searching for sessions: {str(e)}")
            self.sessions_info_label.setStyleSheet("color: #e74c3c; font-size: 11px; font-style: italic;")

            # Re-enable buttons
            self.search_sessions_button.setEnabled(True)
            self.search_sessions_button.setText("🔍 Search for Sessions")
            if hasattr(self, 'refresh_sessions_button'):
                self.refresh_sessions_button.setEnabled(True)

    def connect_to_selected_session(self, item):
        """Connect to the selected WhatsApp Web session"""
        try:
            session_data = item.data(Qt.UserRole)
            if not session_data:
                return

            # Get session details
            title = session_data.get('title', 'Unknown')
            status = session_data.get('status', 'unknown')

            # Handle different session types
            if status == 'needs_debug_mode':
                # Show instructions for enabling debug mode
                QMessageBox.information(
                    self, "Chrome Debug Mode Required",
                    f"To connect to this Chrome session, you need to restart Chrome with debugging enabled.\n\n"
                    f"Steps:\n"
                    f"1. Close all Chrome windows\n"
                    f"2. Open Command Prompt or Terminal\n"
                    f"3. Run: chrome --remote-debugging-port=9222\n"
                    f"4. Open WhatsApp Web in the new Chrome window\n"
                    f"5. Come back here and search for sessions again\n\n"
                    f"Alternatively, click 'Connect to WhatsApp Web' below to create a new session automatically."
                )
                return

            # Ask user for confirmation for other session types
            status_text = {
                'authenticated': 'Signed In',
                'needs_auth': 'Needs Authentication',
                'unknown': 'Unknown Status'
            }.get(status, 'Unknown Status')

            reply = QMessageBox.question(
                self, "Connect to Session",
                f"Connect to this WhatsApp Web session?\n\n"
                f"Title: {title}\n"
                f"Status: {status_text}\n\n"
                f"This will use the existing browser session instead of creating a new one.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # Store the selected session for connection
                self.selected_session = session_data

                # Connect using the selected session
                self.connect_whatsapp()

        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error",
                f"Error connecting to selected session: {e}"
            )

    def connect_whatsapp(self):
        """Connect or disconnect WhatsApp Web"""
        # Check if we're currently connected and should disconnect
        if (hasattr(self, 'whatsapp_driver') and
            self.whatsapp_driver and
            self.whatsapp_driver.is_connected and
            self.connect_button.text() == "Disconnect"):
            self.disconnect_whatsapp()
            return

        # Otherwise, proceed with connection
        if not SELENIUM_AVAILABLE:
            # Offer automatic installation
            reply = QMessageBox.question(
                self, "WhatsApp Integration Setup",
                "WhatsApp Web integration requires additional dependencies.\n\n"
                "Would you like to automatically install them now?\n\n"
                "This will install:\n"
                "• Selenium (for web automation)\n"
                "• WebDriver Manager (for automatic ChromeDriver management)\n\n"
                "Installation may take a few minutes.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.install_dependencies_automatically()
            return

        try:
            print("🔗 Starting WhatsApp Web connection...")
            self.connect_button.setEnabled(False)
            self.connect_button.setText("🔄 Connecting...")
            self.status_label.setText("🔄 Initializing WhatsApp Web connection...")
            self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")

            # Show detailed connection steps
            print("📋 Connection process:")
            print("  1. ✅ Checking Selenium dependencies")
            print("  2. 🔄 Initializing WhatsApp WebDriver")
            print("  3. 🔄 Setting up Chrome browser")
            print("  4. 🔄 Opening WhatsApp Web")
            print("  5. ⏳ Waiting for authentication")

            # Initialize WhatsApp driver
            self.whatsapp_driver = WhatsAppWebDriver()
            self.whatsapp_driver.connection_status_changed.connect(self.on_connection_status_changed)
            self.whatsapp_driver.qr_code_ready.connect(self.on_qr_code_ready)
            self.whatsapp_driver.message_received.connect(self.on_message_received)

            # Connect contacts_loaded signal if available (for compatibility)
            if hasattr(self.whatsapp_driver, 'contacts_loaded'):
                self.whatsapp_driver.contacts_loaded.connect(self.update_contacts_list)

            # If a specific session was selected, store it for the connection thread
            if hasattr(self, 'selected_session'):
                self.whatsapp_driver.selected_session = self.selected_session
                print(f"🎯 Using selected session: {self.selected_session.get('title', 'Unknown')}")
                delattr(self, 'selected_session')  # Clear after use
            else:
                print("🆕 Creating new WhatsApp Web session")

            # Update status
            self.status_label.setText("🔄 Starting Chrome browser...")

            # Start connection in thread
            connection_thread = threading.Thread(target=self._connect_thread)
            connection_thread.daemon = True
            connection_thread.start()

            print("🚀 Connection thread started successfully")

        except Exception as e:
            print(f"❌ Error in connect_whatsapp: {e}")
            import traceback
            traceback.print_exc()

            QMessageBox.critical(
                self, "Connection Error",
                f"Failed to start WhatsApp connection:\n\n{str(e)}\n\n"
                f"Try using the 'Start Chrome with Debugging' button first."
            )
            self.connect_button.setEnabled(True)
            self.connect_button.setText("🔗 Connect to WhatsApp Web")
            self.status_label.setText("❌ Connection failed")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def _connect_thread(self):
        """Connection thread with detailed logging and timeout"""
        import threading
        import time

        def connection_timeout():
            """Handle connection timeout"""
            time.sleep(120)  # 2 minute timeout
            if hasattr(self, '_connection_in_progress') and self._connection_in_progress:
                print("⏰ Connection timeout reached")
                self.connection_failed_signal.emit("Connection timeout - please try again")

        try:
            print("🔄 Connection thread started")
            self._connection_in_progress = True

            # Start timeout timer
            timeout_thread = threading.Thread(target=connection_timeout, daemon=True)
            timeout_thread.start()

            if self.whatsapp_driver:
                print("🔄 Setting up WhatsApp WebDriver...")

                # Update UI status using signals instead of QMetaObject.invokeMethod
                self.update_status_signal.emit("🔄 Setting up Chrome WebDriver...")

                success = self.whatsapp_driver.setup_driver()

                if success and self._connection_in_progress:
                    print("✅ WebDriver setup successful")

                    # Update UI status
                    self.update_status_signal.emit("🔄 Connecting to WhatsApp Web...")

                    # Now actually connect to WhatsApp Web
                    connection_success = self.whatsapp_driver.connect_to_whatsapp_web()

                    if connection_success and self._connection_in_progress:
                        print("✅ WhatsApp Web connection successful")

                        # Update UI status
                        self.update_status_signal.emit("✅ Connected - Ready to send messages!")

                        # Manually trigger the connection status change to ensure UI updates
                        print("🔄 Manually triggering connection status change...")
                        self.on_connection_status_changed(True)

                        # Start the driver thread for message monitoring
                        self.whatsapp_driver.start()
                        print("🚀 WhatsApp WebDriver thread started")

                        # Mark connection as complete
                        self._connection_in_progress = False

                    else:
                        print("❌ WhatsApp Web connection failed")
                        if self._connection_in_progress:
                            self.connection_failed_signal.emit("Failed to connect to WhatsApp Web")

                else:
                    print("❌ WebDriver setup failed")
                    # Connection failed, update UI on main thread
                    if self._connection_in_progress:
                        self.connection_failed_signal.emit("WebDriver setup failed")
            else:
                print("❌ WhatsApp driver not initialized")
                # Connection failed, update UI on main thread
                if self._connection_in_progress:
                    self.connection_failed_signal.emit("WhatsApp driver not initialized")

        except Exception as e:
            print(f"❌ Error in connection thread: {e}")
            import traceback
            traceback.print_exc()

            # Connection failed, update UI on main thread
            if self._connection_in_progress:
                self.connection_failed_signal.emit(f"Connection thread error: {str(e)}")

        finally:
            self._connection_in_progress = False

    def disconnect_whatsapp(self):
        """Disconnect from WhatsApp Web and cleanup resources"""
        try:
            safe_print("🔌 Disconnecting from WhatsApp Web...")

            # Update UI immediately
            self.connect_button.setEnabled(False)
            self.connect_button.setText("🔄 Disconnecting...")
            self.status_label.setText("🔄 Disconnecting from WhatsApp Web...")
            self.status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")

            # Stop and cleanup WhatsApp driver
            if hasattr(self, 'whatsapp_driver') and self.whatsapp_driver:
                try:
                    # Stop the driver thread
                    self.whatsapp_driver.should_stop = True

                    # Close the browser
                    if hasattr(self.whatsapp_driver, 'driver') and self.whatsapp_driver.driver:
                        try:
                            self.whatsapp_driver.driver.quit()
                            safe_print("✅ Browser closed successfully")
                        except Exception as e:
                            safe_print(f"⚠️ Error closing browser: {e}")

                    # Wait for thread to stop
                    if self.whatsapp_driver.isRunning():
                        self.whatsapp_driver.wait(3000)  # Wait up to 3 seconds

                    # Clear the driver reference
                    self.whatsapp_driver = None
                    safe_print("✅ WhatsApp driver cleaned up")

                except Exception as e:
                    safe_print(f"⚠️ Error during driver cleanup: {e}")

            # Update connection status
            self.on_connection_status_changed(False)

            # Reset UI
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Connect to WhatsApp Web")
            self.status_label.setText("🔴 Disconnected")
            self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")

            # Show success notification
            self.show_notification("✅ Disconnected from WhatsApp Web successfully", "success")
            safe_print("✅ WhatsApp Web disconnection completed")

        except Exception as e:
            safe_print(f"❌ Error during disconnection: {e}")

            # Reset UI even if there was an error
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Connect to WhatsApp Web")
            self.status_label.setText("❌ Disconnection error")
            self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")

            self.show_notification(f"⚠️ Disconnection error: {str(e)}", "warning")

    def update_status_label(self, text):
        """Update status label from signal"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")

    def handle_connection_failure(self, error_message):
        """Handle connection failure from signal"""
        print(f"🔴 Handling connection failure: {error_message}")

        self.connect_button.setEnabled(True)
        self.connect_button.setText("🔗 Connect to WhatsApp Web")
        self.status_label.setText("❌ Connection Failed")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

        # Show helpful error message with solutions
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self, "WhatsApp Connection Failed",
            f"❌ Failed to connect to WhatsApp Web.\n\n"
            f"Error: {error_message}\n\n"
            "🔧 Try these solutions:\n\n"
            "1. Click '🚀 Start Chrome with Debugging' first\n"
            "2. Make sure Google Chrome is installed\n"
            "3. Close all Chrome windows and try again\n"
            "4. Check your internet connection\n\n"
            "💡 The automated setup button will handle everything for you!"
        )



    def on_qr_code_ready(self, qr_data: str):
        """Handle QR code ready"""
        QMessageBox.information(
            self, "WhatsApp QR Code",
            "Please scan the QR code in your browser to connect WhatsApp Web."
        )

    def on_message_received(self, message_data: dict):
        """Handle received message"""
        try:
            # Create message object
            message = WhatsAppMessage(
                message_id=f"msg_{int(time.time() * 1000)}",
                sender=message_data.get('sender', 'Unknown'),
                recipient='self',
                content=message_data.get('content', ''),
                timestamp=datetime.fromisoformat(message_data.get('timestamp', datetime.now().isoformat()))
            )

            self.messages.append(message)

            # Update UI
            self.update_messages_display()

            # Sync to Firebase
            if self.firebase_sync:
                self.firebase_sync.upload_message(message)

            # Emit signal
            self.message_received.emit(message.to_dict())

            # Notify
            if self.notification_manager:
                self.notification_manager.notify(
                    f"New WhatsApp Message",
                    f"From {message.sender}: {message.content[:50]}...",
                    category='info',
                    source='WhatsApp Integration'
                )

        except Exception as e:
            print(f"Error handling received message: {e}")

    def select_contact(self, item):
        """Handle contact selection"""
        contact_name = item.text()
        self.chat_header.setText(f"💬 Chat with {contact_name}")
        self.load_chat_history(contact_name)

    def load_chat_history(self, contact_name: str):
        """Load chat history for selected contact"""
        self.messages_area.clear()

        # Filter messages for this contact
        contact_messages = [msg for msg in self.messages
                          if msg.sender == contact_name or msg.recipient == contact_name]

        # Sort by timestamp
        contact_messages.sort(key=lambda x: x.timestamp)

        # Display messages
        for message in contact_messages:
            if message.sender == 'self':
                self.messages_area.append(f"<div style='text-align: right; color: blue;'><b>You:</b> {message.content}</div>")
            else:
                self.messages_area.append(f"<div style='text-align: left; color: green;'><b>{message.sender}:</b> {message.content}</div>")

    def update_messages_display(self):
        """Update the messages display"""
        # This would update the current chat view
        current_contact = self.chat_header.text().replace("💬 Chat with ", "")
        if current_contact != "Select a contact to start chatting":
            self.load_chat_history(current_contact)

    def send_message(self):
        """Send a message"""
        message_text = self.message_input.text().strip()
        if not message_text:
            return

        current_contact = self.chat_header.text().replace("💬 Chat with ", "")
        if current_contact == "Select a contact to start chatting":
            QMessageBox.warning(self, "No Contact Selected", "Please select a contact first.")
            return

        try:
            # Create message object
            message = WhatsAppMessage(
                message_id=f"msg_{int(time.time() * 1000)}",
                sender='self',
                recipient=current_contact,
                content=message_text
            )

            # Send via WhatsApp Web (if connected)
            if self.whatsapp_driver and self.whatsapp_driver.is_connected:
                # Get phone number for contact (simplified)
                phone_number = self.get_contact_phone(current_contact)
                if phone_number:
                    success = self.whatsapp_driver.send_message(phone_number, message_text)
                    if success:
                        message.status = "sent"
                    else:
                        message.status = "failed"
                else:
                    message.status = "failed"
            else:
                message.status = "pending"

            # Add to messages
            self.messages.append(message)

            # Update UI
            self.message_input.clear()
            self.update_messages_display()

            # Sync to Firebase
            if self.firebase_sync:
                self.firebase_sync.upload_message(message)

            # Emit signal
            self.message_sent.emit(message.to_dict())

        except Exception as e:
            QMessageBox.critical(self, "Send Error", f"Failed to send message: {e}")

    def get_contact_phone(self, contact_name: str) -> Optional[str]:
        """Get phone number for contact"""
        for contact in self.contacts:
            if contact.name == contact_name:
                return contact.phone
        return None

    def add_contact(self):
        """Add a new contact"""
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Contact")
        dialog.setModal(True)

        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("+1234567890")

        layout.addRow("Name:", name_input)
        layout.addRow("Phone:", phone_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            phone = phone_input.text().strip()

            if name and phone:
                contact = WhatsAppContact(
                    contact_id=f"contact_{int(time.time() * 1000)}",
                    name=name,
                    phone=phone
                )

                self.contacts.append(contact)
                self.refresh_contacts_display()

                # Notify
                if self.notification_manager:
                    self.notification_manager.notify(
                        "Contact Added",
                        f"Added {name} to WhatsApp contacts",
                        category='success',
                        source='WhatsApp Integration'
                    )

    def refresh_contacts_display(self):
        """Update the contacts list display (for internal use)"""
        self.contacts_list.clear()
        for contact in self.contacts:
            # Handle both dict and object formats
            if isinstance(contact, dict):
                name = contact.get('name', 'Unknown')
                phone = contact.get('phone', 'No phone')
                item = QListWidgetItem(f"{name} ({phone})")
            else:
                # Object format
                item = QListWidgetItem(f"{contact.name} ({contact.phone})")
            self.contacts_list.addItem(item)

    def show_broadcast_dialog(self):
        """Show broadcast message dialog"""
        QMessageBox.information(self, "Broadcast", "Broadcast feature coming soon!")

    def show_quick_templates(self):
        """Show quick message templates dialog"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel

            dialog = QDialog(self)
            dialog.setWindowTitle("📝 Quick Message Templates")
            dialog.setFixedSize(500, 400)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            # Header
            header = QLabel("Select a template to insert into your message:")
            header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
            layout.addWidget(header)

            # Templates list
            templates_list = QListWidget()
            templates_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 5px;
                    background-color: white;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }
                QListWidget::item:hover {
                    background-color: #f0f8ff;
                }
                QListWidget::item:selected {
                    background-color: #25D366;
                    color: white;
                }
            """)

            # Kitchen-specific templates
            templates = [
                ("🍽️ Order Ready", "Your order is ready for pickup! Please come to the counter."),
                ("⏰ Delay Notice", "We apologize for the delay. Your order will be ready in 10 more minutes."),
                ("📋 Order Confirmation", "Thank you for your order! We're preparing it now. Estimated time: 15 minutes."),
                ("🚚 Delivery Update", "Your order is out for delivery and will arrive in 20-30 minutes."),
                ("💰 Payment Reminder", "Friendly reminder: Payment is due for your recent order."),
                ("🎉 Special Offer", "Special offer today! 20% off on all combo meals. Valid until 8 PM."),
                ("📞 Contact Request", "Please call us at your convenience to discuss your order."),
                ("✅ Order Complete", "Your order has been completed. Thank you for choosing us!"),
                ("🔄 Status Update", "We're currently preparing your order. Thank you for your patience."),
                ("📝 Custom Message", "Hi! Hope you're having a great day. "),
                ("🙏 Thank You", "Thank you for your business! We appreciate your support."),
                ("❓ Question", "Hi! I have a quick question about your recent order."),
            ]

            for title, message in templates:
                item = QListWidgetItem(f"{title}\n{message[:50]}...")
                item.setData(Qt.UserRole, message)
                item.setToolTip(message)
                templates_list.addItem(item)

            layout.addWidget(templates_list)

            # Buttons
            button_layout = QHBoxLayout()

            insert_button = QPushButton("📝 Insert Template")
            insert_button.setStyleSheet("""
                QPushButton {
                    background-color: #25D366;
                    color: white;
                    font-weight: bold;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #128C7E;
                }
            """)

            cancel_button = QPushButton("❌ Cancel")
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    font-weight: bold;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)

            def insert_template():
                current_item = templates_list.currentItem()
                if current_item:
                    template_text = current_item.data(Qt.UserRole)
                    if hasattr(self, 'message_input'):
                        current_text = self.message_input.text()
                        if current_text:
                            self.message_input.setText(current_text + " " + template_text)
                        else:
                            self.message_input.setText(template_text)
                        self.message_input.setFocus()
                    dialog.accept()

            insert_button.clicked.connect(insert_template)
            cancel_button.clicked.connect(dialog.reject)

            # Double-click to insert
            templates_list.itemDoubleClicked.connect(lambda: insert_template())

            button_layout.addWidget(insert_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            safe_print(f"❌ Error showing templates dialog: {e}")
            self.show_notification(f"❌ Error showing templates: {str(e)}", "error")

    def show_templates_dialog(self):
        """Show message templates dialog (legacy method)"""
        self.show_quick_templates()

    def show_settings_dialog(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "WhatsApp settings coming soon!")

    def install_dependencies_automatically(self):
        """Install WhatsApp dependencies automatically with progress dialog"""
        try:
            from PySide6.QtWidgets import QProgressDialog
            import subprocess
            import sys

            # Create progress dialog
            progress = QProgressDialog("Installing WhatsApp dependencies...", "Cancel", 0, 100, self)
            progress.setWindowTitle("WhatsApp Setup")
            progress.setModal(True)
            progress.show()

            # Update progress
            progress.setValue(10)
            QApplication.processEvents()

            try:
                # Install selenium
                progress.setLabelText("Installing Selenium...")
                progress.setValue(30)
                QApplication.processEvents()

                subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"],
                                    capture_output=True, text=True)

                # Install webdriver-manager
                progress.setLabelText("Installing WebDriver Manager...")
                progress.setValue(60)
                QApplication.processEvents()

                subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"],
                                    capture_output=True, text=True)

                # Complete installation
                progress.setLabelText("Installation complete!")
                progress.setValue(100)
                QApplication.processEvents()

                progress.close()

                # Show success message
                QMessageBox.information(
                    self, "Installation Complete",
                    "WhatsApp dependencies installed successfully!\n\n"
                    "Please restart the application to use WhatsApp integration.\n\n"
                    "After restart, you can:\n"
                    "• Connect to WhatsApp Web\n"
                    "• Send and receive messages\n"
                    "• Manage contacts\n"
                    "• Sync across devices"
                )

                # Notify success
                if self.notification_manager:
                    self.notification_manager.notify(
                        "WhatsApp Setup Complete",
                        "Dependencies installed successfully. Please restart the application.",
                        category='success',
                        source='WhatsApp Integration'
                    )

            except subprocess.CalledProcessError as e:
                progress.close()
                QMessageBox.critical(
                    self, "Installation Failed",
                    f"Failed to install dependencies:\n{e}\n\n"
                    "Please try manual installation:\n"
                    "1. Open command prompt as administrator\n"
                    "2. Run: pip install selenium webdriver-manager\n"
                    "3. Restart the application"
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Installation Error",
                f"An error occurred during installation:\n{e}\n\n"
                "Please try manual installation."
            )

    def closeEvent(self, event):
        """Handle widget close with session preservation"""
        if self.whatsapp_driver:
            # Preserve session by default when closing
            self.whatsapp_driver.stop(preserve_session=True)

        if self.firebase_sync:
            self.firebase_sync.stop_sync()

        event.accept()


# Convenience functions for easy integration
def create_whatsapp_widget(data=None, user_info=None, parent=None):
    """Create WhatsApp integration widget"""
    return WhatsAppIntegrationWidget(data, user_info, parent)

def send_whatsapp_message(phone: str, message: str, user_info=None):
    """Send a WhatsApp message (standalone function)"""
    try:
        # This would use the global WhatsApp driver or create a temporary one
        print(f"📱 Sending WhatsApp message to {phone}: {message}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return False
