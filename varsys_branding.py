"""
VARSYS Solutions - Kitchen Dashboard
Company Branding and Metadata

Professional branding system for VARSYS Solutions ecosystem
"""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QDesktopServices

from __version__ import get_version_info

class VARSYSBranding:
    """VARSYS Solutions branding system"""
    
    # Company colors
    PRIMARY_COLOR = "#667eea"      # Professional blue
    SECONDARY_COLOR = "#764ba2"    # Purple accent
    SUCCESS_COLOR = "#48bb78"      # Green
    WARNING_COLOR = "#ed8936"      # Orange
    ERROR_COLOR = "#f56565"        # Red
    TEXT_PRIMARY = "#2d3748"       # Dark gray
    TEXT_SECONDARY = "#718096"     # Medium gray
    BACKGROUND = "#f7fafc"         # Light background
    
    # Company information
    COMPANY_NAME = "VARSYS Solutions"
    COMPANY_TAGLINE = "Innovative Software Solutions for Modern Business"
    COMPANY_WEBSITE = "https://github.com/VARSYS-Solutions"
    SUPPORT_EMAIL = "support@varsys-solutions.com"
    
    # Product information
    PRODUCT_NAME = "Kitchen Dashboard"
    PRODUCT_DESCRIPTION = "Professional Kitchen Management System"
    PRODUCT_CATEGORY = "Business Management Software"
    
    @staticmethod
    def get_company_logo_pixmap(size=64):
        """Create company logo pixmap"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(VARSYSBranding.PRIMARY_COLOR))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw stylized "V" logo
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QColor(255, 255, 255))
        
        # Create V shape
        font = painter.font()
        font.setPointSize(size // 2)
        font.setBold(True)
        painter.setFont(font)
        
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "V")
        painter.end()
        
        return pixmap
    
    @staticmethod
    def get_about_text():
        """Get formatted about text"""
        version_info = get_version_info()
        
        return f"""
<h2 style="color: {VARSYSBranding.PRIMARY_COLOR};">{VARSYSBranding.PRODUCT_NAME}</h2>
<p><strong>Version:</strong> {version_info['version']}</p>
<p><strong>Build:</strong> {version_info['build']}</p>
<p><strong>Company:</strong> {VARSYSBranding.COMPANY_NAME}</p>
<p><strong>Description:</strong> {VARSYSBranding.PRODUCT_DESCRIPTION}</p>

<h3 style="color: {VARSYSBranding.SECONDARY_COLOR};">About VARSYS Solutions</h3>
<p>{VARSYSBranding.COMPANY_TAGLINE}</p>
<p>This is the first software in the VARSYS Solutions ecosystem. More integrated 
business solutions will be released to work seamlessly with this application.</p>

<h3 style="color: {VARSYSBranding.SECONDARY_COLOR};">License & Support</h3>
<p><strong>License:</strong> Proprietary - Free for limited testing period</p>
<p><strong>Support:</strong> {VARSYSBranding.SUPPORT_EMAIL}</p>
<p><strong>Website:</strong> {VARSYSBranding.COMPANY_WEBSITE}</p>

<p style="color: {VARSYSBranding.TEXT_SECONDARY}; font-size: 12px;">
{version_info['copyright']}
</p>
        """.strip()
    
    @staticmethod
    def get_splash_text():
        """Get splash screen text"""
        return f"""
{VARSYSBranding.COMPANY_NAME}
{VARSYSBranding.PRODUCT_NAME}
Professional Kitchen Management System
        """.strip()

class AboutDialog(QWidget):
    """Professional about dialog with VARSYS branding"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {VARSYSBranding.PRODUCT_NAME}")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        self.apply_styling()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with logo and company name
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = VARSYSBranding.get_company_logo_pixmap(64)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)
        
        # Company info
        company_layout = QVBoxLayout()
        
        company_name = QLabel(VARSYSBranding.COMPANY_NAME)
        company_name.setFont(QFont("Segoe UI", 18, QFont.Bold))
        company_name.setStyleSheet(f"color: {VARSYSBranding.PRIMARY_COLOR};")
        company_layout.addWidget(company_name)
        
        tagline = QLabel(VARSYSBranding.COMPANY_TAGLINE)
        tagline.setFont(QFont("Segoe UI", 10))
        tagline.setStyleSheet(f"color: {VARSYSBranding.TEXT_SECONDARY};")
        tagline.setWordWrap(True)
        company_layout.addWidget(tagline)
        
        header_layout.addLayout(company_layout)
        layout.addWidget(header_frame)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"color: {VARSYSBranding.TEXT_SECONDARY};")
        layout.addWidget(separator)
        
        # About text
        about_label = QLabel(VARSYSBranding.get_about_text())
        about_label.setWordWrap(True)
        about_label.setTextFormat(Qt.RichText)
        about_label.setAlignment(Qt.AlignTop)
        layout.addWidget(about_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        website_btn = QPushButton("Visit Website")
        website_btn.clicked.connect(self.open_website)
        website_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VARSYSBranding.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {VARSYSBranding.SECONDARY_COLOR};
            }}
        """)
        
        support_btn = QPushButton("Contact Support")
        support_btn.clicked.connect(self.open_support)
        support_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VARSYSBranding.SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e2e8f0;
                color: #4a5568;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cbd5e0;
            }
        """)
        
        button_layout.addWidget(website_btn)
        button_layout.addWidget(support_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def apply_styling(self):
        """Apply professional styling"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {VARSYSBranding.BACKGROUND};
                color: {VARSYSBranding.TEXT_PRIMARY};
            }}
            QLabel {{
                color: {VARSYSBranding.TEXT_PRIMARY};
            }}
        """)
    
    def open_website(self):
        """Open company website"""
        QDesktopServices.openUrl(QUrl(VARSYSBranding.COMPANY_WEBSITE))
    
    def open_support(self):
        """Open support email"""
        QDesktopServices.openUrl(QUrl(f"mailto:{VARSYSBranding.SUPPORT_EMAIL}"))

def show_about_dialog(parent=None):
    """Show the about dialog"""
    dialog = AboutDialog(parent)
    dialog.show()
    return dialog
