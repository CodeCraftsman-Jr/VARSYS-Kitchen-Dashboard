"""
Mobile Navigation System
Touch-optimized navigation with bottom tabs and gesture support
"""

import logging
from typing import Dict, List, Optional, Callable
from enum import Enum
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QStackedWidget, QScrollArea,
                             QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QTimer, QPoint
from PySide6.QtGui import QFont, QIcon, QPainter, QColor, QPen, QBrush

# Import responsive design manager
try:
    from .responsive_design_manager import ResponsiveWidget, DeviceType, LayoutMode, get_responsive_manager
    from .activity_tracker import track_user_action
except ImportError:
    ResponsiveWidget = QWidget
    DeviceType = None
    LayoutMode = None
    def get_responsive_manager(): return None
    def track_user_action(*args, **kwargs): pass

class NavigationStyle(Enum):
    """Navigation style options"""
    SIDEBAR = "sidebar"
    BOTTOM_TABS = "bottom_tabs"
    HAMBURGER = "hamburger"
    DRAWER = "drawer"

class MobileTabButton(QPushButton):
    """Mobile-optimized tab button with touch feedback"""
    
    def __init__(self, text: str, icon: str, parent=None):
        super().__init__(parent)
        self.text_label = text
        self.icon_text = icon
        self.is_active = False
        
        # Setup button
        self.setCheckable(True)
        self.setMinimumHeight(60)
        self.setMinimumWidth(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Apply mobile styling
        self.apply_mobile_styling()
        
        # Touch feedback animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def apply_mobile_styling(self):
        """Apply mobile-optimized styling"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #6b7280;
                font-size: 10px;
                font-weight: 500;
                padding: 8px 4px;
                text-align: center;
            }
            QPushButton:checked {
                color: #3b82f6;
                background-color: rgba(59, 130, 246, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(59, 130, 246, 0.2);
            }
        """)
    
    def paintEvent(self, event):
        """Custom paint event for icon and text"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        
        # Set colors based on state
        if self.isChecked():
            icon_color = QColor("#3b82f6")
            text_color = QColor("#3b82f6")
        else:
            icon_color = QColor("#6b7280")
            text_color = QColor("#6b7280")
        
        # Draw background if checked
        if self.isChecked():
            painter.setBrush(QBrush(QColor(59, 130, 246, 25)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 8, 8)
        
        # Draw icon
        icon_font = QFont()
        icon_font.setPointSize(18)
        painter.setFont(icon_font)
        painter.setPen(QPen(icon_color))
        
        icon_rect = QRect(rect.x(), rect.y() + 8, rect.width(), 24)
        painter.drawText(icon_rect, Qt.AlignCenter, self.icon_text)
        
        # Draw text
        text_font = QFont()
        text_font.setPointSize(9)
        text_font.setWeight(QFont.Medium)
        painter.setFont(text_font)
        painter.setPen(QPen(text_color))
        
        text_rect = QRect(rect.x(), rect.y() + 32, rect.width(), 20)
        painter.drawText(text_rect, Qt.AlignCenter, self.text_label)
    
    def mousePressEvent(self, event):
        """Handle touch press with animation"""
        super().mousePressEvent(event)
        
        # Animate press feedback
        current_rect = self.geometry()
        pressed_rect = current_rect.adjusted(2, 2, -2, -2)
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(pressed_rect)
        self.animation.start()
    
    def mouseReleaseEvent(self, event):
        """Handle touch release with animation"""
        super().mouseReleaseEvent(event)
        
        # Animate release feedback
        current_rect = self.geometry()
        normal_rect = current_rect.adjusted(-2, -2, 2, 2)
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(normal_rect)
        self.animation.start()

class BottomTabNavigation(QFrame):
    """Bottom tab navigation for mobile devices"""
    
    tab_changed = Signal(str)  # tab_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs = {}
        self.current_tab = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e5e7eb;
            }
        """)
        
        # Create horizontal layout for tabs
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(0)
    
    def add_tab(self, tab_id: str, text: str, icon: str, callback: Callable = None):
        """Add a tab to the navigation"""
        button = MobileTabButton(text, icon)
        button.clicked.connect(lambda: self.select_tab(tab_id, callback))
        
        self.tabs[tab_id] = {
            "button": button,
            "callback": callback,
            "text": text,
            "icon": icon
        }
        
        self.layout.addWidget(button)
        
        # Select first tab by default
        if len(self.tabs) == 1:
            self.select_tab(tab_id, callback)
    
    def select_tab(self, tab_id: str, callback: Callable = None):
        """Select a specific tab"""
        if tab_id not in self.tabs:
            return
        
        # Deselect all tabs
        for tid, tab_data in self.tabs.items():
            tab_data["button"].setChecked(tid == tab_id)
        
        # Update current tab
        old_tab = self.current_tab
        self.current_tab = tab_id
        
        # Execute callback
        if callback:
            callback()
        
        # Emit signal
        self.tab_changed.emit(tab_id)
        
        # Track user action
        track_user_action("mobile_navigation", "tab_selected", f"Selected tab: {tab_id}")
    
    def get_current_tab(self) -> Optional[str]:
        """Get currently selected tab"""
        return self.current_tab
    
    def update_tab_badge(self, tab_id: str, count: int):
        """Update badge count for a tab"""
        # This could be implemented to show notification badges
        pass

class HamburgerMenu(QFrame):
    """Hamburger menu for mobile navigation"""
    
    menu_item_selected = Signal(str)  # item_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu_items = {}
        self.is_open = False
        
        self.init_ui()
        self.setup_animations()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-right: 1px solid #e5e7eb;
            }
        """)
        
        # Create scroll area for menu items
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Menu content widget
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(0, 20, 0, 20)
        self.menu_layout.setSpacing(4)
        
        scroll_area.setWidget(self.menu_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # Initially hidden
        self.hide()
    
    def setup_animations(self):
        """Setup slide animations"""
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(300)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def add_menu_item(self, item_id: str, text: str, icon: str, callback: Callable = None):
        """Add a menu item"""
        button = QPushButton(f"{icon}  {text}")
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #374151;
                font-size: 14px;
                font-weight: 500;
                padding: 16px 20px;
                text-align: left;
                min-height: 48px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
            }
        """)
        
        button.clicked.connect(lambda: self.select_item(item_id, callback))
        
        self.menu_items[item_id] = {
            "button": button,
            "callback": callback,
            "text": text,
            "icon": icon
        }
        
        self.menu_layout.addWidget(button)
    
    def select_item(self, item_id: str, callback: Callable = None):
        """Select a menu item"""
        if callback:
            callback()
        
        self.menu_item_selected.emit(item_id)
        self.close_menu()
        
        track_user_action("mobile_navigation", "menu_item_selected", f"Selected menu item: {item_id}")
    
    def open_menu(self):
        """Open the hamburger menu"""
        if self.is_open:
            return
        
        self.show()
        self.is_open = True
        
        # Animate slide in
        start_rect = QRect(-self.width(), 0, self.width(), self.parent().height())
        end_rect = QRect(0, 0, self.width(), self.parent().height())
        
        self.setGeometry(start_rect)
        self.slide_animation.setStartValue(start_rect)
        self.slide_animation.setEndValue(end_rect)
        self.slide_animation.start()
        
        track_user_action("mobile_navigation", "hamburger_opened", "Hamburger menu opened")
    
    def close_menu(self):
        """Close the hamburger menu"""
        if not self.is_open:
            return
        
        self.is_open = False
        
        # Animate slide out
        start_rect = self.geometry()
        end_rect = QRect(-self.width(), 0, self.width(), self.parent().height())
        
        self.slide_animation.setStartValue(start_rect)
        self.slide_animation.setEndValue(end_rect)
        self.slide_animation.finished.connect(self.hide)
        self.slide_animation.start()
        
        track_user_action("mobile_navigation", "hamburger_closed", "Hamburger menu closed")

class MobileNavigationManager(ResponsiveWidget):
    """
    Mobile navigation manager that:
    - Adapts navigation style based on device type
    - Provides touch-optimized controls
    - Manages navigation state
    - Handles gesture navigation
    """
    
    navigation_changed = Signal(str)  # page_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Navigation components
        self.bottom_tabs = None
        self.hamburger_menu = None
        self.current_style = NavigationStyle.SIDEBAR
        
        # Navigation items
        self.navigation_items = []
        
        # Get responsive manager
        self.responsive_manager = get_responsive_manager()
        if self.responsive_manager:
            self.set_responsive_manager(self.responsive_manager)
        
        self.init_ui()
        
        self.logger.info("Mobile Navigation Manager initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Content area
        self.content_area = QWidget()
        self.layout.addWidget(self.content_area)
        
        # Initially create sidebar-style navigation
        self.create_sidebar_navigation()
    
    def add_navigation_item(self, item_id: str, text: str, icon: str, callback: Callable = None):
        """Add a navigation item"""
        item = {
            "id": item_id,
            "text": text,
            "icon": icon,
            "callback": callback
        }
        
        self.navigation_items.append(item)
        
        # Add to current navigation style
        if self.bottom_tabs:
            self.bottom_tabs.add_tab(item_id, text, icon, callback)
        
        if self.hamburger_menu:
            self.hamburger_menu.add_menu_item(item_id, text, icon, callback)
    
    def create_bottom_tabs_navigation(self):
        """Create bottom tabs navigation for mobile"""
        if self.bottom_tabs:
            return
        
        self.bottom_tabs = BottomTabNavigation(self)
        self.bottom_tabs.tab_changed.connect(self.navigation_changed.emit)
        
        # Add existing navigation items
        for item in self.navigation_items:
            self.bottom_tabs.add_tab(item["id"], item["text"], item["icon"], item["callback"])
        
        self.layout.addWidget(self.bottom_tabs)
        
        self.logger.info("Created bottom tabs navigation")
    
    def create_hamburger_navigation(self):
        """Create hamburger menu navigation"""
        if self.hamburger_menu:
            return
        
        self.hamburger_menu = HamburgerMenu(self)
        self.hamburger_menu.menu_item_selected.connect(self.navigation_changed.emit)
        
        # Add existing navigation items
        for item in self.navigation_items:
            self.hamburger_menu.add_menu_item(item["id"], item["text"], item["icon"], item["callback"])
        
        # Position hamburger menu
        self.hamburger_menu.setParent(self)
        self.hamburger_menu.hide()
        
        self.logger.info("Created hamburger menu navigation")
    
    def create_sidebar_navigation(self):
        """Create sidebar navigation for desktop"""
        # This would integrate with the existing sidebar
        self.logger.info("Using existing sidebar navigation")
    
    def adapt_to_device_type(self, device_type: DeviceType):
        """Adapt navigation to device type"""
        if device_type == DeviceType.MOBILE:
            self.switch_to_bottom_tabs()
        elif device_type == DeviceType.TABLET:
            self.switch_to_hamburger()
        else:
            self.switch_to_sidebar()
    
    def switch_to_bottom_tabs(self):
        """Switch to bottom tabs navigation"""
        if self.current_style == NavigationStyle.BOTTOM_TABS:
            return
        
        # Hide other navigation styles
        if self.hamburger_menu:
            self.hamburger_menu.hide()
        
        # Create and show bottom tabs
        self.create_bottom_tabs_navigation()
        self.bottom_tabs.show()
        
        self.current_style = NavigationStyle.BOTTOM_TABS
        self.logger.info("Switched to bottom tabs navigation")
    
    def switch_to_hamburger(self):
        """Switch to hamburger menu navigation"""
        if self.current_style == NavigationStyle.HAMBURGER:
            return
        
        # Hide other navigation styles
        if self.bottom_tabs:
            self.bottom_tabs.hide()
        
        # Create hamburger menu
        self.create_hamburger_navigation()
        
        self.current_style = NavigationStyle.HAMBURGER
        self.logger.info("Switched to hamburger menu navigation")
    
    def switch_to_sidebar(self):
        """Switch to sidebar navigation"""
        if self.current_style == NavigationStyle.SIDEBAR:
            return
        
        # Hide mobile navigation styles
        if self.bottom_tabs:
            self.bottom_tabs.hide()
        if self.hamburger_menu:
            self.hamburger_menu.hide()
        
        self.current_style = NavigationStyle.SIDEBAR
        self.logger.info("Switched to sidebar navigation")
    
    def toggle_hamburger_menu(self):
        """Toggle hamburger menu open/close"""
        if self.hamburger_menu:
            if self.hamburger_menu.is_open:
                self.hamburger_menu.close_menu()
            else:
                self.hamburger_menu.open_menu()
    
    def get_current_navigation_style(self) -> NavigationStyle:
        """Get current navigation style"""
        return self.current_style
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        
        # Update hamburger menu position if it exists
        if self.hamburger_menu:
            self.hamburger_menu.setGeometry(0, 0, self.hamburger_menu.width(), self.height())

# Global mobile navigation manager instance
_mobile_navigation_manager = None

def get_mobile_navigation_manager():
    """Get global mobile navigation manager instance"""
    global _mobile_navigation_manager
    if _mobile_navigation_manager is None:
        _mobile_navigation_manager = MobileNavigationManager()
    return _mobile_navigation_manager
