"""
Responsive Dialog Utilities
Utilities for making QDialog responsive across different screen sizes
"""

import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                              QPushButton, QLabel, QLineEdit, QComboBox, 
                              QTextEdit, QScrollArea, QWidget, QSizePolicy,
                              QDialogButtonBox, QFormLayout, QGroupBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QGuiApplication

# Import responsive design manager
try:
    from .responsive_design_manager import get_responsive_manager, DeviceType
except ImportError:
    def get_responsive_manager():
        return None
    
    class DeviceType:
        MOBILE = "mobile"
        TABLET = "tablet"
        DESKTOP = "desktop"
        LARGE_DESKTOP = "large_desktop"

class ResponsiveDialog(QDialog):
    """A responsive dialog that adapts to different screen sizes"""
    
    def __init__(self, title: str = "", parent=None, modal: bool = True):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.responsive_manager = get_responsive_manager()
        
        # Setup dialog properties
        self.setWindowTitle(title)
        self.setModal(modal)
        
        # Apply responsive behavior
        self.apply_responsive_behavior()
        
    def apply_responsive_behavior(self):
        """Apply responsive behavior based on current device type"""
        if not self.responsive_manager:
            return
            
        device_type = self.responsive_manager.current_device_type
        
        # Set responsive size
        self.set_responsive_size(device_type)
        
        # Apply responsive styling
        self.apply_responsive_styling(device_type)
        
    def set_responsive_size(self, device_type: DeviceType):
        """Set dialog size based on device type"""
        if device_type == DeviceType.MOBILE:
            # Full screen on mobile
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                self.resize(screen_geometry.size())
                self.move(screen_geometry.topLeft())
            else:
                self.resize(400, 600)
                
        elif device_type == DeviceType.TABLET:
            # 90% of parent or screen on tablet
            if self.parent():
                parent_size = self.parent().size()
                new_width = int(parent_size.width() * 0.9)
                new_height = int(parent_size.height() * 0.9)
                self.resize(new_width, new_height)
                
                # Center on parent
                parent_pos = self.parent().pos()
                parent_size = self.parent().size()
                x = parent_pos.x() + (parent_size.width() - new_width) // 2
                y = parent_pos.y() + (parent_size.height() - new_height) // 2
                self.move(x, y)
            else:
                self.resize(800, 600)
                
        else:  # Desktop and large desktop
            # Fixed size on desktop
            if device_type == DeviceType.LARGE_DESKTOP:
                self.resize(800, 600)
            else:
                self.resize(600, 400)
                
            # Center on screen
            if self.parent():
                self.move(self.parent().geometry().center() - self.rect().center())
                
    def apply_responsive_styling(self, device_type: DeviceType):
        """Apply responsive styling to the dialog"""
        if not self.responsive_manager:
            return
            
        styles = self.responsive_manager.get_responsive_styles(device_type)
        
        dialog_style = f"""
            QDialog {{
                background-color: white;
                border-radius: {styles['border_radius']};
            }}
            QLabel {{
                font-size: {styles['font_size_normal']};
                color: #374151;
                margin: {styles['spacing_small']};
            }}
            QPushButton {{
                min-height: {styles['button_height']};
                font-size: {styles['font_size_normal']};
                padding: {styles['spacing_normal']} {styles['spacing_large']};
                border-radius: {styles['border_radius']};
                background-color: #3b82f6;
                color: white;
                border: none;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                min-height: {styles['input_height']};
                font-size: {styles['font_size_normal']};
                padding: {styles['spacing_normal']};
                border: 1px solid #d1d5db;
                border-radius: {styles['border_radius']};
                background-color: white;
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border-color: #3b82f6;
                outline: none;
            }}
            QGroupBox {{
                font-weight: 600;
                font-size: {styles['font_size_normal']};
                color: #374151;
                border: 1px solid #e5e7eb;
                border-radius: {styles['border_radius']};
                margin-top: {styles['spacing_large']};
                padding-top: {styles['spacing_normal']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {styles['spacing_normal']};
                padding: 0 {styles['spacing_small']} 0 {styles['spacing_small']};
                background-color: white;
            }}
        """
        
        self.setStyleSheet(dialog_style)

class ResponsiveDialogManager:
    """Manager for creating responsive dialogs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.responsive_manager = get_responsive_manager()
        
    def create_dialog(self, title: str = "", parent=None, modal: bool = True) -> ResponsiveDialog:
        """Create a new responsive dialog"""
        return ResponsiveDialog(title, parent, modal)
        
    def create_form_dialog(self, title: str, fields: Dict[str, str], parent=None) -> ResponsiveDialog:
        """
        Create a responsive form dialog
        
        Args:
            title: Dialog title
            fields: Dict mapping field names to field types ('text', 'combo', 'textarea')
            parent: Parent widget
            
        Returns:
            ResponsiveDialog with form layout
        """
        dialog = ResponsiveDialog(title, parent)
        
        # Create main layout
        main_layout = QVBoxLayout(dialog)
        
        # Create scroll area for mobile compatibility
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(scroll_area.NoFrame)
        
        # Create form widget
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Store field widgets for later access
        dialog.field_widgets = {}
        
        # Create form fields
        for field_name, field_type in fields.items():
            label = QLabel(field_name + ":")
            
            if field_type == 'text':
                widget = QLineEdit()
            elif field_type == 'combo':
                widget = QComboBox()
            elif field_type == 'textarea':
                widget = QTextEdit()
                widget.setMaximumHeight(100)  # Limit height
            else:
                widget = QLineEdit()  # Default to text
                
            form_layout.addRow(label, widget)
            dialog.field_widgets[field_name] = widget
            
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)
        
        # Create button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        main_layout.addWidget(button_box)
        
        return dialog
        
    def create_confirmation_dialog(self, title: str, message: str, parent=None) -> ResponsiveDialog:
        """Create a responsive confirmation dialog"""
        dialog = ResponsiveDialog(title, parent)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        return dialog
        
    def create_info_dialog(self, title: str, content: str, parent=None) -> ResponsiveDialog:
        """Create a responsive information dialog"""
        dialog = ResponsiveDialog(title, parent)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Create scroll area for long content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(scroll_area.NoFrame)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Add content
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content_layout.addWidget(content_label)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        return dialog
        
    def make_dialog_responsive(self, dialog: QDialog):
        """Make an existing dialog responsive"""
        if not isinstance(dialog, QDialog) or not self.responsive_manager:
            return
            
        device_type = self.responsive_manager.current_device_type
        
        # Apply responsive sizing
        if device_type == DeviceType.MOBILE:
            # Full screen on mobile
            screen = QGuiApplication.primaryScreen()
            if screen:
                dialog.resize(screen.size())
                dialog.move(screen.geometry().topLeft())
                
        elif device_type == DeviceType.TABLET:
            # 90% of screen on tablet
            if dialog.parent():
                parent_size = dialog.parent().size()
                dialog.resize(int(parent_size.width() * 0.9), int(parent_size.height() * 0.9))
            else:
                dialog.resize(800, 600)
                
        # Apply responsive styling
        styles = self.responsive_manager.get_responsive_styles(device_type)
        
        dialog_style = f"""
            QDialog {{
                background-color: white;
                border-radius: {styles['border_radius']};
            }}
            QPushButton {{
                min-height: {styles['button_height']};
                font-size: {styles['font_size_normal']};
                padding: {styles['spacing_normal']} {styles['spacing_large']};
            }}
            QLineEdit, QComboBox {{
                min-height: {styles['input_height']};
                font-size: {styles['font_size_normal']};
                padding: {styles['spacing_normal']};
            }}
        """
        
        dialog.setStyleSheet(dialog_style)

# Global instance
_responsive_dialog_manager = None

def get_responsive_dialog_manager():
    """Get the global responsive dialog manager instance"""
    global _responsive_dialog_manager
    if _responsive_dialog_manager is None:
        _responsive_dialog_manager = ResponsiveDialogManager()
    return _responsive_dialog_manager

def create_responsive_dialog(title: str = "", parent=None, modal: bool = True) -> ResponsiveDialog:
    """Convenience function to create a responsive dialog"""
    manager = get_responsive_dialog_manager()
    return manager.create_dialog(title, parent, modal)

def make_dialog_responsive(dialog: QDialog):
    """Convenience function to make an existing dialog responsive"""
    manager = get_responsive_dialog_manager()
    return manager.make_dialog_responsive(dialog)
