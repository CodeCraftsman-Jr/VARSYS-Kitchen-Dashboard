#!/usr/bin/env python3
"""
License Activation Dialog for VARSYS Kitchen Dashboard
Commercial licensing interface
"""

import sys
import webbrowser
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QFrame,
                             QProgressBar, QMessageBox, QTabWidget, QWidget,
                             QGridLayout, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon

from license_manager import license_manager

class LicenseActivationThread(QThread):
    """Thread for license activation to prevent UI blocking"""
    
    activation_complete = Signal(bool, str)
    
    def __init__(self, license_key, email):
        super().__init__()
        self.license_key = license_key
        self.email = email
    
    def run(self):
        try:
            success, message = license_manager.activate_license(self.license_key, self.email)
            self.activation_complete.emit(success, message)
        except Exception as e:
            self.activation_complete.emit(False, f"Activation failed: {str(e)}")

class LicenseDialog(QDialog):
    """Professional license activation dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VARSYS Kitchen Dashboard - License Activation")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # Check current license status
        self.license_valid, self.license_message, self.license_data = license_manager.verify_license()
        
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        
        # Logo and title
        title_label = QLabel("🍳 VARSYS Kitchen Dashboard")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Professional Kitchen Management System")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Tab widget for different license operations
        self.tab_widget = QTabWidget()
        
        if self.license_valid:
            self.create_license_info_tab()
        else:
            self.create_activation_tab()
            self.create_purchase_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Footer buttons
        button_layout = QHBoxLayout()
        
        if not self.license_valid:
            trial_btn = QPushButton("Start 7-Day Trial")
            trial_btn.setObjectName("trialButton")
            trial_btn.clicked.connect(self.start_trial)
            button_layout.addWidget(trial_btn)
        
        if self.license_valid:
            ok_btn = QPushButton("Continue")
            ok_btn.setObjectName("primaryButton")
            ok_btn.clicked.connect(self.accept)
            button_layout.addWidget(ok_btn)
        else:
            cancel_btn = QPushButton("Exit Application")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_activation_tab(self):
        """Create license activation tab"""
        activation_widget = QWidget()
        layout = QVBoxLayout(activation_widget)
        
        # Instructions
        instructions = QLabel("""
        <h3>Activate Your License</h3>
        <p>Enter your license key and email address to activate VARSYS Kitchen Dashboard.</p>
        <p>If you don't have a license key, please purchase one from the Purchase tab.</p>
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Activation form
        form_group = QGroupBox("License Information")
        form_layout = QGridLayout(form_group)
        
        # Email field
        form_layout.addWidget(QLabel("Email Address:"), 0, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@company.com")
        form_layout.addWidget(self.email_input, 0, 1)
        
        # License key field
        form_layout.addWidget(QLabel("License Key:"), 1, 0)
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("VARSYS-XXXX-XXXX-XXXX-XXXX")
        form_layout.addWidget(self.license_key_input, 1, 1)
        
        layout.addWidget(form_group)
        
        # Machine ID info
        machine_info = QGroupBox("Machine Information")
        machine_layout = QVBoxLayout(machine_info)
        
        machine_id_label = QLabel(f"Machine ID: {license_manager.machine_id}")
        machine_id_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        machine_layout.addWidget(machine_id_label)
        
        machine_note = QLabel("Note: Your license will be tied to this machine ID for security.")
        machine_note.setStyleSheet("color: #666; font-size: 10px;")
        machine_layout.addWidget(machine_note)
        
        layout.addWidget(machine_info)
        
        # Activation button and progress
        self.activate_btn = QPushButton("Activate License")
        self.activate_btn.setObjectName("primaryButton")
        self.activate_btn.clicked.connect(self.activate_license)
        layout.addWidget(self.activate_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.tab_widget.addTab(activation_widget, "Activate License")
    
    def create_purchase_tab(self):
        """Create license purchase tab"""
        purchase_widget = QWidget()
        layout = QVBoxLayout(purchase_widget)
        
        # Purchase information
        purchase_info = QLabel("""
        <h3>Purchase VARSYS Kitchen Dashboard</h3>
        <p>Get full access to all professional features:</p>
        <ul>
        <li>✅ Complete inventory management system</li>
        <li>✅ Advanced sales analytics and reporting</li>
        <li>✅ Budget tracking and expense management</li>
        <li>✅ Firebase cloud synchronization</li>
        <li>✅ AI-powered business insights</li>
        <li>✅ Multi-platform support</li>
        <li>✅ Priority customer support</li>
        <li>✅ Free updates for 1 year</li>
        </ul>
        """)
        purchase_info.setWordWrap(True)
        layout.addWidget(purchase_info)
        
        # Pricing
        pricing_group = QGroupBox("Pricing Plans")
        pricing_layout = QVBoxLayout(pricing_group)
        
        # Single license
        single_license = QFrame()
        single_license.setObjectName("pricingFrame")
        single_layout = QHBoxLayout(single_license)
        
        single_info = QLabel("""
        <h4>Single Restaurant License</h4>
        <p>Perfect for individual restaurants</p>
        <p><strong>₹15,000</strong> / year</p>
        """)
        single_layout.addWidget(single_info)
        
        single_btn = QPushButton("Purchase Single License")
        single_btn.setObjectName("purchaseButton")
        single_btn.clicked.connect(lambda: self.open_purchase_page("single"))
        single_layout.addWidget(single_btn)
        
        pricing_layout.addWidget(single_license)
        
        # Multi-location license
        multi_license = QFrame()
        multi_license.setObjectName("pricingFrame")
        multi_layout = QHBoxLayout(multi_license)
        
        multi_info = QLabel("""
        <h4>Multi-Location License</h4>
        <p>For restaurant chains (up to 5 locations)</p>
        <p><strong>₹45,000</strong> / year</p>
        """)
        multi_layout.addWidget(multi_info)
        
        multi_btn = QPushButton("Purchase Multi License")
        multi_btn.setObjectName("purchaseButton")
        multi_btn.clicked.connect(lambda: self.open_purchase_page("multi"))
        multi_layout.addWidget(multi_btn)
        
        pricing_layout.addWidget(multi_license)
        
        layout.addWidget(pricing_group)
        
        # Contact information
        contact_info = QLabel("""
        <h4>Need Help?</h4>
        <p>Contact us for custom pricing or enterprise solutions:</p>
        <p>📧 Email: sales@varsys.com</p>
        <p>📱 WhatsApp: +91-XXXXX-XXXXX</p>
        <p>🌐 Website: www.varsys.com</p>
        """)
        contact_info.setWordWrap(True)
        layout.addWidget(contact_info)
        
        self.tab_widget.addTab(purchase_widget, "Purchase License")
    
    def create_license_info_tab(self):
        """Create license information tab for valid licenses"""
        info_widget = QWidget()
        layout = QVBoxLayout(info_widget)
        
        # License status
        status_group = QGroupBox("License Status")
        status_layout = QVBoxLayout(status_group)
        
        status_label = QLabel("✅ License Active")
        status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        status_layout.addWidget(status_label)
        
        if self.license_data:
            info_text = f"""
            <p><strong>Email:</strong> {self.license_data.get('email', 'N/A')}</p>
            <p><strong>License Type:</strong> {self.license_data.get('license_type', 'N/A').title()}</p>
            <p><strong>Expires:</strong> {self.license_data.get('expires_at', 'N/A')[:10]}</p>
            <p><strong>Days Remaining:</strong> {(license_manager.get_license_info() or {}).get('days_remaining', 'N/A')}</p>
            """
            
            info_label = QLabel(info_text)
            status_layout.addWidget(info_label)
        
        layout.addWidget(status_group)
        
        # License management
        management_group = QGroupBox("License Management")
        management_layout = QVBoxLayout(management_group)
        
        deactivate_btn = QPushButton("Deactivate License")
        deactivate_btn.setObjectName("dangerButton")
        deactivate_btn.clicked.connect(self.deactivate_license)
        management_layout.addWidget(deactivate_btn)
        
        layout.addWidget(management_group)
        
        self.tab_widget.addTab(info_widget, "License Information")
    
    def activate_license(self):
        """Activate license with provided credentials"""
        email = self.email_input.text().strip()
        license_key = self.license_key_input.text().strip()
        
        if not email or not license_key:
            QMessageBox.warning(self, "Missing Information", 
                              "Please enter both email and license key.")
            return
        
        # Disable button and show progress
        self.activate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start activation in separate thread
        self.activation_thread = LicenseActivationThread(license_key, email)
        self.activation_thread.activation_complete.connect(self.on_activation_complete)
        self.activation_thread.start()
    
    def on_activation_complete(self, success, message):
        """Handle activation completion"""
        self.progress_bar.setVisible(False)
        self.activate_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Activation Successful", 
                                  "Your license has been activated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Activation Failed", 
                               f"License activation failed:\n\n{message}")
    
    def start_trial(self):
        """Start trial period"""
        # Implement trial license generation
        trial_key = f"VARSYS-TRIAL-{license_manager.machine_id[:8]}"
        success, message = license_manager.activate_license(trial_key, "trial@varsys.com")
        
        if success:
            QMessageBox.information(self, "Trial Started", 
                                  "7-day trial activated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Trial Failed", 
                               f"Failed to start trial:\n\n{message}")
    
    def open_purchase_page(self, license_type):
        """Open purchase page in browser"""
        # Replace with your actual purchase URL
        purchase_url = f"https://your-website.com/purchase?type={license_type}&machine_id={license_manager.machine_id}"
        webbrowser.open(purchase_url)
        
        QMessageBox.information(self, "Purchase Page Opened", 
                              "The purchase page has been opened in your browser.\n\n"
                              "After completing your purchase, you will receive a license key via email.")
    
    def deactivate_license(self):
        """Deactivate current license"""
        reply = QMessageBox.question(self, "Deactivate License", 
                                   "Are you sure you want to deactivate your license?\n\n"
                                   "This will remove access to all premium features.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if license_manager.deactivate_license():
                QMessageBox.information(self, "License Deactivated", 
                                      "Your license has been deactivated.")
                self.reject()
            else:
                QMessageBox.critical(self, "Deactivation Failed", 
                                   "Failed to deactivate license.")
    
    def apply_styles(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            
            #titleLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            
            #subtitleLabel {
                color: rgba(255,255,255,0.9);
                font-size: 14px;
            }
            
            #primaryButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            
            #primaryButton:hover {
                background-color: #218838;
            }
            
            #purchaseButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            
            #purchaseButton:hover {
                background-color: #0056b3;
            }
            
            #trialButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            
            #dangerButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            
            #pricingFrame {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                background-color: white;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            
            QLineEdit:focus {
                border-color: #80bdff;
            }
        """)

def show_license_dialog(parent=None) -> bool:
    """Show license dialog and return True if license is valid"""
    dialog = LicenseDialog(parent)
    result = dialog.exec()
    
    if result == QDialog.Accepted:
        # Verify license again after dialog
        valid, _, _ = license_manager.verify_license()
        return valid
    
    return False
