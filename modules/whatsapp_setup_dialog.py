#!/usr/bin/env python3
"""
WhatsApp Setup Dialog
Handles first-time setup and user guidance for WhatsApp integration
"""

try:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QPushButton, QTextEdit, QProgressBar, QFrame,
                                   QCheckBox, QGroupBox, QMessageBox)
    from PySide6.QtCore import Qt, QTimer, Signal, QThread
    from PySide6.QtGui import QFont, QPixmap, QIcon
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Create dummy classes
    class QDialog: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QTextEdit: pass
    class QProgressBar: pass
    class QFrame: pass
    class QCheckBox: pass
    class QGroupBox: pass
    class QMessageBox: pass
    class Signal: 
        def __init__(self, *args): pass
        def emit(self, *args): pass
    class QThread: pass
    class QTimer: pass
    class QFont: pass
    class QPixmap: pass
    class QIcon: pass
    Qt = type('Qt', (), {'AlignCenter': 0, 'AlignLeft': 0})()

import threading
import time
from pathlib import Path

# Enhanced fallback with proper UTF-8 encoding for Windows
def safe_print(*args, **kwargs):
    try:
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

class WhatsAppSetupDialog(QDialog):
    """Dialog for first-time WhatsApp setup with skip option"""
    
    setup_completed = Signal(bool, str)  # success, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_thread = None
        self.setup_result = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the setup dialog UI"""
        self.setWindowTitle("WhatsApp Integration Setup")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("WhatsApp Integration Setup")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "VARSYS Kitchen Dashboard can integrate with WhatsApp to send messages "
            "directly to 'Abiram's Kitchen' group.\n\n"
            "This setup will:\n"
            "• Connect to WhatsApp Web in your browser\n"
            "• Find the 'Abiram's Kitchen' group\n"
            "• Enable one-click messaging from the dashboard"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(desc_label)
        
        # Setup options group
        options_group = QGroupBox("Setup Options")
        options_layout = QVBoxLayout(options_group)
        
        # Auto-connect checkbox
        self.auto_connect_checkbox = QCheckBox("Automatically connect to WhatsApp on startup")
        self.auto_connect_checkbox.setChecked(True)
        options_layout.addWidget(self.auto_connect_checkbox)
        
        # Remember choice checkbox
        self.remember_choice_checkbox = QCheckBox("Remember my choice")
        self.remember_choice_checkbox.setChecked(True)
        options_layout.addWidget(self.remember_choice_checkbox)
        
        layout.addWidget(options_group)
        
        # Progress area
        self.progress_group = QGroupBox("Setup Progress")
        progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        self.status_text.setVisible(False)
        progress_layout.addWidget(self.status_text)
        
        layout.addWidget(self.progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.setup_button = QPushButton("🔗 Setup WhatsApp Integration")
        self.setup_button.setStyleSheet("""
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
        self.setup_button.clicked.connect(self.start_setup)
        button_layout.addWidget(self.setup_button)
        
        self.skip_button = QPushButton("⏭️ Skip Setup")
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #666;
                border: 1px solid #ccc;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.skip_button.clicked.connect(self.skip_setup)
        button_layout.addWidget(self.skip_button)
        
        self.close_button = QPushButton("✅ Done")
        self.close_button.setVisible(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addWidget(QFrame())  # Spacer
        layout.addLayout(button_layout)
        
    def start_setup(self):
        """Start the WhatsApp setup process"""
        if self.setup_thread and self.setup_thread.is_alive():
            safe_print("[WARNING] Setup already in progress")
            return
            
        safe_print("[START] Starting WhatsApp setup process...")
        
        # Show progress UI
        self.progress_bar.setVisible(True)
        self.status_text.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Disable setup button
        self.setup_button.setEnabled(False)
        self.setup_button.setText("🔄 Setting up...")
        
        # Clear status
        self.status_text.clear()
        self.add_status("Starting WhatsApp integration setup...")
        
        # Start setup in background thread
        self.setup_thread = threading.Thread(
            target=self._setup_thread,
            daemon=True,
            name="WhatsAppSetup"
        )
        self.setup_thread.start()
        
    def _setup_thread(self):
        """Background thread for setup process"""
        try:
            self.add_status("Checking WhatsApp integration components...")
            
            # Step 1: Check if components are available
            if not self._check_components():
                self.setup_result = (False, "Required components not available")
                return
                
            self.add_status("✅ Components available")
            
            # Step 2: Attempt WhatsApp connection
            self.add_status("Connecting to WhatsApp Web...")
            if not self._attempt_connection():
                self.setup_result = (False, "Failed to connect to WhatsApp Web")
                return
                
            self.add_status("✅ Connected to WhatsApp Web")
            
            # Step 3: Search for Abiram's Kitchen
            self.add_status("Searching for 'Abiram's Kitchen' group...")
            if not self._find_target_group():
                self.setup_result = (False, "Could not find 'Abiram's Kitchen' group")
                return
                
            self.add_status("✅ Found 'Abiram's Kitchen' group")
            self.add_status("🎉 Setup completed successfully!")
            
            # Save preferences
            self._save_setup_preferences()
            
            self.setup_result = (True, "WhatsApp integration ready")
            
        except Exception as e:
            safe_print(f"[ERROR] Setup thread error: {e}")
            self.setup_result = (False, f"Setup error: {e}")
        finally:
            # Update UI on main thread
            QTimer.singleShot(100, self._setup_finished)
    
    def _check_components(self):
        """Check if required components are available"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            return True
        except ImportError:
            self.add_status("❌ Selenium WebDriver not available")
            return False
    
    def _attempt_connection(self):
        """Attempt to connect to WhatsApp Web"""
        try:
            from modules.whatsapp_integration import WhatsAppWebDriver
            
            self.whatsapp_driver = WhatsAppWebDriver()
            success = self.whatsapp_driver.connect_to_whatsapp()
            
            if not success:
                self.add_status("❌ Connection failed - please ensure Chrome is installed")
                
            return success
            
        except Exception as e:
            self.add_status(f"❌ Connection error: {e}")
            return False
    
    def _find_target_group(self):
        """Search for Abiram's Kitchen group"""
        try:
            if not hasattr(self, 'whatsapp_driver'):
                return False
                
            target_group = self.whatsapp_driver.find_abirams_kitchen()
            return target_group is not None
            
        except Exception as e:
            self.add_status(f"❌ Search error: {e}")
            return False
    
    def _save_setup_preferences(self):
        """Save setup preferences"""
        try:
            from modules.whatsapp_startup_manager import WhatsAppStartupManager
            
            manager = WhatsAppStartupManager()
            manager.preferences["setup_completed"] = True
            manager.preferences["auto_connect"] = self.auto_connect_checkbox.isChecked()
            manager.preferences["skip_setup"] = False
            manager.save_preferences()
            
        except Exception as e:
            safe_print(f"[ERROR] Error saving preferences: {e}")
    
    def _setup_finished(self):
        """Called when setup thread finishes"""
        self.progress_bar.setVisible(False)
        
        if self.setup_result:
            success, message = self.setup_result
            
            if success:
                self.setup_button.setVisible(False)
                self.skip_button.setVisible(False)
                self.close_button.setVisible(True)
                self.add_status(f"✅ {message}")
            else:
                self.setup_button.setEnabled(True)
                self.setup_button.setText("🔄 Retry Setup")
                self.add_status(f"❌ {message}")
            
            # Emit result
            self.setup_completed.emit(success, message)
    
    def skip_setup(self):
        """Skip WhatsApp setup"""
        if self.remember_choice_checkbox.isChecked():
            try:
                from modules.whatsapp_startup_manager import WhatsAppStartupManager
                
                manager = WhatsAppStartupManager()
                manager.skip_setup()
                
                safe_print("[INFO] WhatsApp setup skipped and saved to preferences")
            except Exception as e:
                safe_print(f"[ERROR] Error saving skip preference: {e}")
        
        self.setup_completed.emit(False, "Setup skipped by user")
        self.reject()
    
    def add_status(self, message):
        """Add status message to the text area"""
        try:
            self.status_text.append(message)
            self.status_text.ensureCursorVisible()
        except:
            safe_print(f"[STATUS] {message}")

def show_setup_dialog(parent=None):
    """Show the WhatsApp setup dialog"""
    if not QT_AVAILABLE:
        safe_print("[ERROR] Qt not available - cannot show setup dialog")
        return False, "Qt not available"
    
    dialog = WhatsAppSetupDialog(parent)
    result = dialog.exec()
    
    return result == QDialog.Accepted, "Setup dialog completed"
