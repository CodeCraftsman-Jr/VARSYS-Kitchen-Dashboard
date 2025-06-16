"""
Responsive Design Manager
Mobile-responsive design system with adaptive layouts and touch optimization
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QFrame, QGridLayout,
                             QSizePolicy, QSpacerItem, QStackedWidget, QHeaderView)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QRect, QPropertyAnimation, QEasingCurve, QObject
from PySide6.QtGui import QFont, QFontMetrics, QScreen, QGuiApplication

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_system_event
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

class DeviceType(Enum):
    """Device type classification"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LARGE_DESKTOP = "large_desktop"

class LayoutMode(Enum):
    """Layout mode options"""
    COMPACT = "compact"
    NORMAL = "normal"
    EXPANDED = "expanded"

class ResponsiveBreakpoints:
    """Responsive design breakpoints"""
    MOBILE_MAX = 768
    TABLET_MAX = 1024
    DESKTOP_MAX = 1440
    
    @classmethod
    def get_device_type(cls, width: int) -> DeviceType:
        """Determine device type based on screen width"""
        if width <= cls.MOBILE_MAX:
            return DeviceType.MOBILE
        elif width <= cls.TABLET_MAX:
            return DeviceType.TABLET
        elif width <= cls.DESKTOP_MAX:
            return DeviceType.DESKTOP
        else:
            return DeviceType.LARGE_DESKTOP

class ResponsiveWidget(QWidget):
    """Base responsive widget that adapts to screen size"""
    
    device_type_changed = Signal(DeviceType)
    layout_mode_changed = Signal(LayoutMode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_device_type = DeviceType.DESKTOP
        self.current_layout_mode = LayoutMode.NORMAL
        self.responsive_manager = None
        
        # Setup resize detection
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize_complete)
        
    def set_responsive_manager(self, manager):
        """Set the responsive design manager"""
        self.responsive_manager = manager
        if manager:
            manager.device_type_changed.connect(self.on_device_type_changed)
            manager.layout_mode_changed.connect(self.on_layout_mode_changed)
    
    def resizeEvent(self, event):
        """Handle resize events with debouncing"""
        super().resizeEvent(event)
        self.resize_timer.start(100)  # Debounce resize events
    
    def handle_resize_complete(self):
        """Handle completed resize"""
        if self.responsive_manager:
            self.responsive_manager.update_layout(self.size())
    
    def on_device_type_changed(self, device_type: DeviceType):
        """Handle device type change"""
        if device_type != self.current_device_type:
            self.current_device_type = device_type
            self.adapt_to_device_type(device_type)
            self.device_type_changed.emit(device_type)
    
    def on_layout_mode_changed(self, layout_mode: LayoutMode):
        """Handle layout mode change"""
        if layout_mode != self.current_layout_mode:
            self.current_layout_mode = layout_mode
            self.adapt_to_layout_mode(layout_mode)
            self.layout_mode_changed.emit(layout_mode)
    
    def adapt_to_device_type(self, device_type: DeviceType):
        """Override in subclasses to adapt to device type"""
        pass
    
    def adapt_to_layout_mode(self, layout_mode: LayoutMode):
        """Override in subclasses to adapt to layout mode"""
        pass

class ResponsiveDesignManager(QObject):
    """
    Responsive design manager that:
    - Detects device type and screen size
    - Manages responsive breakpoints
    - Provides adaptive styling
    - Handles touch optimization
    - Manages layout transitions
    """

    device_type_changed = Signal(DeviceType)
    layout_mode_changed = Signal(LayoutMode)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Current state
        self.current_device_type = DeviceType.DESKTOP
        self.current_layout_mode = LayoutMode.NORMAL
        self.screen_size = QSize(1920, 1080)
        
        # Responsive widgets registry
        self.responsive_widgets = []
        
        # Touch optimization settings
        self.touch_enabled = False
        self.touch_target_size = 44  # Minimum touch target size in pixels
        
        # Initialize
        self.detect_initial_state()
        
        self.logger.info("Responsive Design Manager initialized")
        track_system_event("responsive_manager", "initialized", "Responsive design manager started")
    
    def detect_initial_state(self):
        """Detect initial device state"""
        try:
            # Get primary screen
            screen = QGuiApplication.primaryScreen()
            if screen:
                geometry = screen.geometry()
                self.screen_size = geometry.size()
                
                # Determine device type
                width = geometry.width()
                self.current_device_type = ResponsiveBreakpoints.get_device_type(width)
                
                # Determine layout mode based on device type
                if self.current_device_type == DeviceType.MOBILE:
                    self.current_layout_mode = LayoutMode.COMPACT
                elif self.current_device_type == DeviceType.LARGE_DESKTOP:
                    self.current_layout_mode = LayoutMode.EXPANDED
                else:
                    self.current_layout_mode = LayoutMode.NORMAL
                
                # Enable touch for mobile devices
                self.touch_enabled = self.current_device_type == DeviceType.MOBILE
                
                self.logger.info(f"Detected device: {self.current_device_type.value}, "
                               f"layout: {self.current_layout_mode.value}, "
                               f"screen: {width}x{geometry.height()}")
                
        except Exception as e:
            self.logger.error(f"Error detecting initial state: {e}")
    
    def register_responsive_widget(self, widget: ResponsiveWidget):
        """Register a widget for responsive updates"""
        if widget not in self.responsive_widgets:
            self.responsive_widgets.append(widget)
            widget.set_responsive_manager(self)
            
            # Apply current state
            widget.on_device_type_changed(self.current_device_type)
            widget.on_layout_mode_changed(self.current_layout_mode)
    
    def unregister_responsive_widget(self, widget: ResponsiveWidget):
        """Unregister a responsive widget"""
        if widget in self.responsive_widgets:
            self.responsive_widgets.remove(widget)
    
    def update_layout(self, size: QSize):
        """Update layout based on new size"""
        width = size.width()
        new_device_type = ResponsiveBreakpoints.get_device_type(width)
        
        # Determine new layout mode
        if new_device_type == DeviceType.MOBILE:
            new_layout_mode = LayoutMode.COMPACT
        elif new_device_type == DeviceType.LARGE_DESKTOP:
            new_layout_mode = LayoutMode.EXPANDED
        else:
            new_layout_mode = LayoutMode.NORMAL
        
        # Update if changed
        if new_device_type != self.current_device_type:
            self.current_device_type = new_device_type
            self.touch_enabled = new_device_type == DeviceType.MOBILE
            
            # Notify all responsive widgets
            for widget in self.responsive_widgets:
                widget.on_device_type_changed(new_device_type)
            
            self.device_type_changed.emit(new_device_type)
            track_user_action("responsive_manager", "device_type_changed", f"Device type changed to {new_device_type.value}")
        
        if new_layout_mode != self.current_layout_mode:
            self.current_layout_mode = new_layout_mode
            
            # Notify all responsive widgets
            for widget in self.responsive_widgets:
                widget.on_layout_mode_changed(new_layout_mode)
            
            self.layout_mode_changed.emit(new_layout_mode)
            track_user_action("responsive_manager", "layout_mode_changed", f"Layout mode changed to {new_layout_mode.value}")
    
    def get_responsive_styles(self, device_type: DeviceType = None) -> Dict[str, str]:
        """Get responsive CSS styles for current or specified device type"""
        if device_type is None:
            device_type = self.current_device_type
        
        base_styles = {
            "font_size_small": "11px",
            "font_size_normal": "13px",
            "font_size_large": "16px",
            "font_size_xlarge": "20px",
            "spacing_small": "4px",
            "spacing_normal": "8px",
            "spacing_large": "16px",
            "spacing_xlarge": "24px",
            "border_radius": "8px",
            "button_height": "36px",
            "input_height": "40px",
        }
        
        if device_type == DeviceType.MOBILE:
            return {
                **base_styles,
                "font_size_small": "12px",
                "font_size_normal": "14px",
                "font_size_large": "18px",
                "font_size_xlarge": "24px",
                "spacing_normal": "12px",
                "spacing_large": "20px",
                "spacing_xlarge": "32px",
                "button_height": "44px",  # Touch-friendly
                "input_height": "48px",   # Touch-friendly
                "border_radius": "12px",
            }
        elif device_type == DeviceType.TABLET:
            return {
                **base_styles,
                "font_size_normal": "14px",
                "font_size_large": "17px",
                "spacing_large": "20px",
                "button_height": "40px",
                "input_height": "44px",
                "border_radius": "10px",
            }
        elif device_type == DeviceType.LARGE_DESKTOP:
            return {
                **base_styles,
                "font_size_normal": "14px",
                "font_size_large": "18px",
                "font_size_xlarge": "24px",
                "spacing_large": "20px",
                "spacing_xlarge": "32px",
            }
        
        return base_styles
    
    def get_responsive_layout_config(self, device_type: DeviceType = None) -> Dict[str, Any]:
        """Get responsive layout configuration"""
        if device_type is None:
            device_type = self.current_device_type
        
        base_config = {
            "sidebar_width": 250,
            "content_margin": 20,
            "grid_columns": 4,
            "card_min_width": 200,
            "navigation_style": "sidebar",
            "show_labels": True,
            "compact_mode": False,
        }
        
        if device_type == DeviceType.MOBILE:
            return {
                **base_config,
                "sidebar_width": 0,  # Hidden on mobile
                "content_margin": 12,
                "grid_columns": 1,
                "card_min_width": 280,
                "navigation_style": "bottom_tabs",
                "show_labels": False,
                "compact_mode": True,
            }
        elif device_type == DeviceType.TABLET:
            return {
                **base_config,
                "sidebar_width": 200,
                "content_margin": 16,
                "grid_columns": 2,
                "card_min_width": 240,
                "navigation_style": "sidebar",
                "compact_mode": True,
            }
        elif device_type == DeviceType.LARGE_DESKTOP:
            return {
                **base_config,
                "sidebar_width": 300,
                "content_margin": 32,
                "grid_columns": 6,
                "card_min_width": 180,
            }
        
        return base_config
    
    def apply_touch_optimization(self, widget: QWidget):
        """Apply touch optimization to a widget"""
        if not self.touch_enabled:
            return

        # Increase minimum size for touch targets
        if isinstance(widget, QPushButton):
            widget.setMinimumHeight(self.touch_target_size)
            widget.setMinimumWidth(self.touch_target_size)

        # Add touch-friendly styling
        current_style = widget.styleSheet()
        touch_style = f"""
            {current_style}
            QPushButton {{
                padding: 12px 16px;
                margin: 4px;
            }}
            QPushButton:pressed {{
                background-color: rgba(59, 130, 246, 0.1);
            }}
            QLineEdit {{
                padding: 12px;
                margin: 4px;
            }}
            QComboBox {{
                padding: 12px;
                margin: 4px;
            }}
        """
        widget.setStyleSheet(touch_style)

    def make_table_responsive(self, table_widget, column_priorities=None):
        """Make a table widget responsive to different screen sizes

        Args:
            table_widget: QTableWidget to make responsive
            column_priorities: Dict mapping column index to priority (1=highest, 5=lowest)
                              Columns with lower priority will be hidden on smaller screens
        """
        from PySide6.QtWidgets import QTableWidget, QHeaderView

        if not isinstance(table_widget, QTableWidget):
            return

        # Set default column priorities if not provided
        if column_priorities is None:
            column_priorities = {}
            for i in range(table_widget.columnCount()):
                column_priorities[i] = 3  # Medium priority by default

        # Store priorities for later use
        table_widget.setProperty("column_priorities", column_priorities)

        # Apply responsive behavior based on current device type
        self.apply_table_responsive_behavior(table_widget)

        # Enable horizontal scrolling for mobile
        if self.current_device_type == DeviceType.MOBILE:
            table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set responsive row heights
        row_height = self.get_responsive_row_height()
        table_widget.verticalHeader().setDefaultSectionSize(row_height)

        # Apply touch optimization
        self.apply_touch_optimization(table_widget)

    def apply_table_responsive_behavior(self, table_widget):
        """Apply responsive behavior to table based on current device type"""
        column_priorities = table_widget.property("column_priorities") or {}

        if self.current_device_type == DeviceType.MOBILE:
            # Hide low priority columns on mobile
            for col_index, priority in column_priorities.items():
                if priority >= 4:  # Hide priority 4 and 5 columns
                    table_widget.setColumnHidden(col_index, True)
                else:
                    table_widget.setColumnHidden(col_index, False)

            # Set column resize mode for mobile
            header = table_widget.horizontalHeader()
            for i in range(table_widget.columnCount()):
                if not table_widget.isColumnHidden(i):
                    header.setSectionResizeMode(i, QHeaderView.Stretch)

        elif self.current_device_type == DeviceType.TABLET:
            # Hide only lowest priority columns on tablet
            for col_index, priority in column_priorities.items():
                if priority >= 5:  # Hide only priority 5 columns
                    table_widget.setColumnHidden(col_index, True)
                else:
                    table_widget.setColumnHidden(col_index, False)

            # Set mixed resize modes for tablet
            header = table_widget.horizontalHeader()
            for i in range(table_widget.columnCount()):
                if not table_widget.isColumnHidden(i):
                    priority = column_priorities.get(i, 3)
                    if priority <= 2:  # High priority columns get fixed width
                        header.setSectionResizeMode(i, QHeaderView.Fixed)
                    else:  # Others stretch
                        header.setSectionResizeMode(i, QHeaderView.Stretch)

        else:  # Desktop and large desktop
            # Show all columns
            for col_index in column_priorities.keys():
                table_widget.setColumnHidden(col_index, False)

            # Set appropriate resize modes for desktop
            header = table_widget.horizontalHeader()
            for i in range(table_widget.columnCount()):
                priority = column_priorities.get(i, 3)
                if priority <= 2:  # High priority columns get interactive resize
                    header.setSectionResizeMode(i, QHeaderView.Interactive)
                else:  # Others get fixed width
                    header.setSectionResizeMode(i, QHeaderView.Fixed)

    def get_responsive_row_height(self):
        """Get appropriate row height based on device type"""
        if self.current_device_type == DeviceType.MOBILE:
            return 60  # Larger for touch
        elif self.current_device_type == DeviceType.TABLET:
            return 55
        else:
            return 50  # Standard desktop height
    
    def create_responsive_button(self, text: str, icon: str = None) -> QPushButton:
        """Create a responsive button with touch optimization"""
        button = QPushButton(text)
        
        # Apply responsive styling
        styles = self.get_responsive_styles()
        button_style = f"""
            QPushButton {{
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: {styles['border_radius']};
                padding: {styles['spacing_normal']} {styles['spacing_large']};
                font-size: {styles['font_size_normal']};
                font-weight: 500;
                min-height: {styles['button_height']};
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
            QPushButton:disabled {{
                background-color: #9ca3af;
            }}
        """
        button.setStyleSheet(button_style)
        
        # Apply touch optimization
        self.apply_touch_optimization(button)
        
        return button
    
    def create_responsive_grid_layout(self, parent: QWidget) -> QGridLayout:
        """Create a responsive grid layout"""
        layout = QGridLayout(parent)
        
        config = self.get_responsive_layout_config()
        styles = self.get_responsive_styles()
        
        # Set spacing based on device type
        spacing = int(styles['spacing_normal'].replace('px', ''))
        layout.setSpacing(spacing)
        
        # Set margins
        margin = config['content_margin']
        layout.setContentsMargins(margin, margin, margin, margin)
        
        return layout

    def make_chart_responsive(self, figure, canvas_widget=None):
        """Make a matplotlib chart responsive to different screen sizes

        Args:
            figure: matplotlib Figure object
            canvas_widget: Optional FigureCanvas widget
        """
        try:
            import matplotlib.pyplot as plt

            # Get responsive styles
            styles = self.get_responsive_styles()
            config = self.get_responsive_layout_config()

            # Adjust figure size based on device type
            if self.current_device_type == DeviceType.MOBILE:
                figure.set_size_inches(6, 4)
                figure.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
            elif self.current_device_type == DeviceType.TABLET:
                figure.set_size_inches(8, 5)
                figure.subplots_adjust(left=0.12, right=0.95, top=0.9, bottom=0.12)
            else:  # Desktop and large desktop
                figure.set_size_inches(10, 6)
                figure.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)

            # Adjust font sizes for all text elements
            font_size_map = {
                DeviceType.MOBILE: {'title': 12, 'label': 10, 'tick': 8},
                DeviceType.TABLET: {'title': 14, 'label': 11, 'tick': 9},
                DeviceType.DESKTOP: {'title': 16, 'label': 12, 'tick': 10},
                DeviceType.LARGE_DESKTOP: {'title': 18, 'label': 14, 'tick': 12}
            }

            font_sizes = font_size_map.get(self.current_device_type, font_size_map[DeviceType.DESKTOP])

            # Apply font sizes to all axes
            for ax in figure.get_axes():
                # Title
                if ax.get_title():
                    ax.set_title(ax.get_title(), fontsize=font_sizes['title'])

                # Labels
                if ax.get_xlabel():
                    ax.set_xlabel(ax.get_xlabel(), fontsize=font_sizes['label'])
                if ax.get_ylabel():
                    ax.set_ylabel(ax.get_ylabel(), fontsize=font_sizes['label'])

                # Tick labels
                ax.tick_params(axis='both', which='major', labelsize=font_sizes['tick'])

                # Legend
                legend = ax.get_legend()
                if legend:
                    legend.set_fontsize(font_sizes['tick'])

            # Adjust layout
            figure.tight_layout()

            # Update canvas if provided
            if canvas_widget:
                canvas_widget.draw()

        except Exception as e:
            self.logger.error(f"Error making chart responsive: {e}")

    def create_responsive_dialog(self, title: str, parent=None):
        """Create a responsive dialog that adapts to screen size

        Args:
            title: Dialog title
            parent: Parent widget

        Returns:
            QDialog: Configured responsive dialog
        """
        from PySide6.QtWidgets import QDialog

        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setModal(True)

        # Set responsive size based on device type
        if self.current_device_type == DeviceType.MOBILE:
            # Full screen on mobile
            if parent:
                dialog.resize(parent.size())
                dialog.move(parent.pos())
            else:
                screen = QGuiApplication.primaryScreen()
                if screen:
                    dialog.resize(screen.size())
        elif self.current_device_type == DeviceType.TABLET:
            # 90% of screen on tablet
            if parent:
                parent_size = parent.size()
                dialog.resize(int(parent_size.width() * 0.9), int(parent_size.height() * 0.9))
            else:
                dialog.resize(800, 600)
        else:  # Desktop
            # Fixed size on desktop
            dialog.resize(600, 400)

        # Apply responsive styling
        styles = self.get_responsive_styles()
        dialog_style = f"""
            QDialog {{
                background-color: white;
                border-radius: {styles['border_radius']};
            }}
            QLabel {{
                font-size: {styles['font_size_normal']};
                color: #374151;
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

        return dialog

    def create_responsive_card(self, title: str, content: QWidget = None) -> QFrame:
        """Create a responsive card widget"""
        card = QFrame()
        
        styles = self.get_responsive_styles()
        config = self.get_responsive_layout_config()
        
        # Set minimum width
        card.setMinimumWidth(config['card_min_width'])
        
        # Apply responsive styling
        card_style = f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: {styles['border_radius']};
                margin: {styles['spacing_small']};
            }}
            QFrame:hover {{
                border-color: #cbd5e1;
                background-color: rgba(59, 130, 246, 0.05);
            }}
        """
        card.setStyleSheet(card_style)
        
        # Create layout
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            int(styles['spacing_large'].replace('px', '')),
            int(styles['spacing_normal'].replace('px', '')),
            int(styles['spacing_large'].replace('px', '')),
            int(styles['spacing_normal'].replace('px', ''))
        )
        layout.setSpacing(int(styles['spacing_normal'].replace('px', '')))
        
        # Add title
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: #0f172a;
                    font-size: {styles['font_size_large']};
                    font-weight: 600;
                    margin-bottom: {styles['spacing_small']};
                }}
            """)
            layout.addWidget(title_label)
        
        # Add content
        if content:
            layout.addWidget(content)
        
        return card
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get current device information"""
        return {
            "device_type": self.current_device_type.value,
            "layout_mode": self.current_layout_mode.value,
            "screen_size": {
                "width": self.screen_size.width(),
                "height": self.screen_size.height()
            },
            "touch_enabled": self.touch_enabled,
            "touch_target_size": self.touch_target_size,
            "responsive_widgets_count": len(self.responsive_widgets)
        }

# Global responsive design manager instance
_responsive_manager = None

def get_responsive_manager():
    """Get global responsive design manager instance"""
    global _responsive_manager
    if _responsive_manager is None:
        _responsive_manager = ResponsiveDesignManager()
    return _responsive_manager
