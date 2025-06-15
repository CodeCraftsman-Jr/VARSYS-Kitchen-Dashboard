"""
Firebase Configuration Widget
UI widget for configuring Firebase settings in Kitchen Dashboard v1.0.6
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLineEdit, QLabel, QPushButton, QGroupBox,
                              QCheckBox, QSpinBox, QComboBox, QTextEdit,
                              QMessageBox, QTabWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class FirebaseConfigWidget(QWidget):
    """
    Firebase Configuration Widget for Kitchen Dashboard v1.0.6
    
    Provides UI for configuring:
    - Firebase project settings
    - Authentication settings
    - Cloud sync settings
    - Security settings
    """
    
    # Signals
    configuration_changed = Signal()
    
    def __init__(self, firebase_config_manager=None, parent=None):
        super().__init__(parent)
        self.firebase_config_manager = firebase_config_manager
        
        # Initialize UI
        self.init_ui()
        
        # Load current configuration
        if self.firebase_config_manager:
            self.load_current_configuration()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Firebase Configuration")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_label.setStyleSheet("color: #0f172a; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Create tabs for different configuration sections
        self.config_tabs = QTabWidget()
        
        # Firebase Project tab
        self.create_firebase_project_tab()
        
        # Features tab
        self.create_features_tab()
        
        # Sync Settings tab
        self.create_sync_settings_tab()
        
        # Security Settings tab
        self.create_security_settings_tab()
        
        layout.addWidget(self.config_tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.test_connection_btn.clicked.connect(self.test_firebase_connection)
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.save_btn.clicked.connect(self.save_configuration)
        
        button_layout.addWidget(self.test_connection_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def create_firebase_project_tab(self):
        """Create Firebase project configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Firebase project settings
        project_group = QGroupBox("Firebase Project Settings")
        project_layout = QFormLayout(project_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Your Firebase API Key")
        project_layout.addRow("API Key:", self.api_key_input)
        
        self.auth_domain_input = QLineEdit()
        self.auth_domain_input.setPlaceholderText("your-project.firebaseapp.com")
        project_layout.addRow("Auth Domain:", self.auth_domain_input)
        
        self.database_url_input = QLineEdit()
        self.database_url_input.setPlaceholderText("https://your-project-default-rtdb.firebaseio.com")
        project_layout.addRow("Database URL:", self.database_url_input)
        
        self.project_id_input = QLineEdit()
        self.project_id_input.setPlaceholderText("your-project-id")
        project_layout.addRow("Project ID:", self.project_id_input)
        
        self.storage_bucket_input = QLineEdit()
        self.storage_bucket_input.setPlaceholderText("your-project.appspot.com")
        project_layout.addRow("Storage Bucket:", self.storage_bucket_input)
        
        self.messaging_sender_id_input = QLineEdit()
        self.messaging_sender_id_input.setPlaceholderText("123456789")
        project_layout.addRow("Messaging Sender ID:", self.messaging_sender_id_input)
        
        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("1:123456789:web:abcdef123456")
        project_layout.addRow("App ID:", self.app_id_input)
        
        self.measurement_id_input = QLineEdit()
        self.measurement_id_input.setPlaceholderText("G-ABCDEF123")
        project_layout.addRow("Measurement ID:", self.measurement_id_input)
        
        layout.addWidget(project_group)
        layout.addStretch()
        
        self.config_tabs.addTab(tab, "Firebase Project")
    
    def create_features_tab(self):
        """Create features configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        features_group = QGroupBox("Feature Settings")
        features_layout = QVBoxLayout(features_group)
        
        self.auth_enabled_cb = QCheckBox("Enable Authentication")
        self.auth_enabled_cb.setChecked(True)
        features_layout.addWidget(self.auth_enabled_cb)
        
        self.cloud_sync_enabled_cb = QCheckBox("Enable Cloud Sync")
        self.cloud_sync_enabled_cb.setChecked(True)
        features_layout.addWidget(self.cloud_sync_enabled_cb)
        
        self.realtime_sync_enabled_cb = QCheckBox("Enable Real-time Sync")
        self.realtime_sync_enabled_cb.setChecked(True)
        features_layout.addWidget(self.realtime_sync_enabled_cb)
        
        self.offline_support_enabled_cb = QCheckBox("Enable Offline Support (Disabled - Online-Only Mode)")
        self.offline_support_enabled_cb.setChecked(False)
        self.offline_support_enabled_cb.setEnabled(False)  # Disable offline support
        self.offline_support_enabled_cb.setStyleSheet("color: #9ca3af;")  # Gray out the text
        features_layout.addWidget(self.offline_support_enabled_cb)
        
        self.analytics_enabled_cb = QCheckBox("Enable Analytics")
        self.analytics_enabled_cb.setChecked(True)
        features_layout.addWidget(self.analytics_enabled_cb)
        
        layout.addWidget(features_group)
        layout.addStretch()
        
        self.config_tabs.addTab(tab, "Features")
    
    def create_sync_settings_tab(self):
        """Create sync settings configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        sync_group = QGroupBox("Sync Settings")
        sync_layout = QFormLayout(sync_group)
        
        self.auto_sync_enabled_cb = QCheckBox("Enable Auto Sync")
        self.auto_sync_enabled_cb.setChecked(True)
        sync_layout.addRow("", self.auto_sync_enabled_cb)
        
        self.sync_interval_input = QSpinBox()
        self.sync_interval_input.setRange(1, 60)
        self.sync_interval_input.setValue(5)
        self.sync_interval_input.setSuffix(" minutes")
        sync_layout.addRow("Sync Interval:", self.sync_interval_input)
        
        self.batch_size_input = QSpinBox()
        self.batch_size_input.setRange(10, 1000)
        self.batch_size_input.setValue(100)
        sync_layout.addRow("Batch Size:", self.batch_size_input)
        
        self.max_retries_input = QSpinBox()
        self.max_retries_input.setRange(1, 10)
        self.max_retries_input.setValue(3)
        sync_layout.addRow("Max Retries:", self.max_retries_input)
        
        self.conflict_resolution_combo = QComboBox()
        self.conflict_resolution_combo.addItems([
            "ask_user", "local_wins", "remote_wins", "merge"
        ])
        sync_layout.addRow("Conflict Resolution:", self.conflict_resolution_combo)
        
        layout.addWidget(sync_group)
        layout.addStretch()
        
        self.config_tabs.addTab(tab, "Sync Settings")
    
    def create_security_settings_tab(self):
        """Create security settings configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        security_group = QGroupBox("Security Settings")
        security_layout = QFormLayout(security_group)
        
        self.require_auth_cb = QCheckBox("Require Authentication")
        self.require_auth_cb.setChecked(True)
        security_layout.addRow("", self.require_auth_cb)
        
        self.session_timeout_input = QSpinBox()
        self.session_timeout_input.setRange(1, 168)  # 1 hour to 1 week
        self.session_timeout_input.setValue(24)
        self.session_timeout_input.setSuffix(" hours")
        security_layout.addRow("Session Timeout:", self.session_timeout_input)
        
        self.auto_logout_cb = QCheckBox("Auto Logout on Idle")
        self.auto_logout_cb.setChecked(True)
        security_layout.addRow("", self.auto_logout_cb)
        
        self.idle_timeout_input = QSpinBox()
        self.idle_timeout_input.setRange(5, 120)
        self.idle_timeout_input.setValue(30)
        self.idle_timeout_input.setSuffix(" minutes")
        security_layout.addRow("Idle Timeout:", self.idle_timeout_input)
        
        layout.addWidget(security_group)
        layout.addStretch()
        
        self.config_tabs.addTab(tab, "Security")
    
    def load_current_configuration(self):
        """Load current configuration into the UI"""
        if not self.firebase_config_manager:
            return
        
        # Load Firebase config
        if self.firebase_config_manager.firebase_config:
            config = self.firebase_config_manager.firebase_config
            self.api_key_input.setText(config.api_key)
            self.auth_domain_input.setText(config.auth_domain)
            self.database_url_input.setText(config.database_url)
            self.project_id_input.setText(config.project_id)
            self.storage_bucket_input.setText(config.storage_bucket)
            self.messaging_sender_id_input.setText(config.messaging_sender_id)
            self.app_id_input.setText(config.app_id)
            self.measurement_id_input.setText(config.measurement_id)
        
        # Load features
        features = self.firebase_config_manager.features
        self.auth_enabled_cb.setChecked(features.get('authentication', True))
        self.cloud_sync_enabled_cb.setChecked(features.get('cloud_sync', True))
        self.realtime_sync_enabled_cb.setChecked(features.get('real_time_sync', True))
        self.offline_support_enabled_cb.setChecked(features.get('offline_support', True))
        self.analytics_enabled_cb.setChecked(features.get('analytics', True))
        
        # Load sync settings
        if self.firebase_config_manager.sync_settings:
            sync = self.firebase_config_manager.sync_settings
            self.auto_sync_enabled_cb.setChecked(sync.auto_sync_enabled)
            self.sync_interval_input.setValue(sync.sync_interval_minutes)
            self.batch_size_input.setValue(sync.batch_size)
            self.max_retries_input.setValue(sync.max_retries)
            
            # Set conflict resolution
            index = self.conflict_resolution_combo.findText(sync.conflict_resolution)
            if index >= 0:
                self.conflict_resolution_combo.setCurrentIndex(index)
        
        # Load security settings
        if self.firebase_config_manager.security_settings:
            security = self.firebase_config_manager.security_settings
            self.require_auth_cb.setChecked(security.require_authentication)
            self.session_timeout_input.setValue(security.session_timeout_hours)
            self.auto_logout_cb.setChecked(security.auto_logout_on_idle)
            self.idle_timeout_input.setValue(security.idle_timeout_minutes)
    
    def save_configuration(self) -> bool:
        """Save the current configuration"""
        if not self.firebase_config_manager:
            QMessageBox.warning(self, "Error", "No configuration manager available")
            return False
        
        try:
            # Update Firebase config
            from modules.firebase_config_manager import FirebaseConfig, SyncSettings, SecuritySettings
            
            self.firebase_config_manager.firebase_config = FirebaseConfig(
                api_key=self.api_key_input.text().strip(),
                auth_domain=self.auth_domain_input.text().strip(),
                database_url=self.database_url_input.text().strip(),
                project_id=self.project_id_input.text().strip(),
                storage_bucket=self.storage_bucket_input.text().strip(),
                messaging_sender_id=self.messaging_sender_id_input.text().strip(),
                app_id=self.app_id_input.text().strip(),
                measurement_id=self.measurement_id_input.text().strip()
            )
            
            # Update features (ONLINE-ONLY MODE)
            self.firebase_config_manager.features = {
                'authentication': self.auth_enabled_cb.isChecked(),
                'cloud_sync': self.cloud_sync_enabled_cb.isChecked(),
                'real_time_sync': self.realtime_sync_enabled_cb.isChecked(),
                'offline_support': False,  # Always false for online-only mode
                'analytics': self.analytics_enabled_cb.isChecked()
            }
            
            # Update sync settings
            self.firebase_config_manager.sync_settings = SyncSettings(
                auto_sync_enabled=self.auto_sync_enabled_cb.isChecked(),
                sync_interval_minutes=self.sync_interval_input.value(),
                batch_size=self.batch_size_input.value(),
                max_retries=self.max_retries_input.value(),
                conflict_resolution=self.conflict_resolution_combo.currentText()
            )
            
            # Update security settings
            self.firebase_config_manager.security_settings = SecuritySettings(
                require_authentication=self.require_auth_cb.isChecked(),
                session_timeout_hours=self.session_timeout_input.value(),
                auto_logout_on_idle=self.auto_logout_cb.isChecked(),
                idle_timeout_minutes=self.idle_timeout_input.value()
            )
            
            # Save to file
            if self.firebase_config_manager.save_configuration():
                QMessageBox.information(self, "Success", "Configuration saved successfully!")
                self.configuration_changed.emit()
                return True
            else:
                QMessageBox.warning(self, "Error", "Failed to save configuration")
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving configuration: {str(e)}")
            return False
    
    def test_firebase_connection(self):
        """Test Firebase connection with current settings"""
        try:
            # Validate required fields
            if not all([
                self.api_key_input.text().strip(),
                self.auth_domain_input.text().strip(),
                self.project_id_input.text().strip()
            ]):
                QMessageBox.warning(self, "Validation Error", 
                                  "Please fill in at least API Key, Auth Domain, and Project ID")
                return
            
            # Test connection (simplified)
            QMessageBox.information(self, "Connection Test", 
                                  "Configuration appears valid. Save and restart to test full connection.")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Test Failed", f"Error: {str(e)}")
