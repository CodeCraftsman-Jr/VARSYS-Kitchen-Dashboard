"""
Responsive Home Dashboard
Mobile-optimized home dashboard with adaptive layouts
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea, QSizePolicy,
                             QPushButton, QProgressBar)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

# Import responsive design components
try:
    from .responsive_design_manager import ResponsiveWidget, DeviceType, LayoutMode, get_responsive_manager
    from .activity_tracker import track_user_action, track_system_event
except ImportError:
    ResponsiveWidget = QWidget
    DeviceType = None
    LayoutMode = None
    def get_responsive_manager(): return None
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

class ResponsiveMetricCard(ResponsiveWidget):
    """Responsive metric card that adapts to screen size"""
    
    def __init__(self, title: str, value: str, change: str = "", trend: str = "stable", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.change = change
        self.trend = trend
        
        self.init_ui()
        
        # Get responsive manager
        responsive_manager = get_responsive_manager()
        if responsive_manager:
            self.set_responsive_manager(responsive_manager)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 700;")
        layout.addWidget(self.value_label)
        
        # Change indicator
        if self.change:
            change_layout = QHBoxLayout()
            
            # Trend indicator
            trend_indicator = QLabel("↗" if self.trend == "up" else "↘" if self.trend == "down" else "→")
            trend_indicator.setStyleSheet(f"color: {self.get_trend_color()}; font-size: 16px; font-weight: 600;")
            change_layout.addWidget(trend_indicator)
            
            # Change text
            self.change_label = QLabel(self.change)
            self.change_label.setStyleSheet(f"color: {self.get_trend_color()}; font-size: 12px; font-weight: 500;")
            change_layout.addWidget(self.change_label)
            
            change_layout.addStretch()
            layout.addLayout(change_layout)
        
        layout.addStretch()
        
        # Apply initial styling
        self.apply_card_styling()
    
    def apply_card_styling(self):
        """Apply responsive card styling"""
        responsive_manager = get_responsive_manager()
        if responsive_manager:
            styles = responsive_manager.get_responsive_styles()
            
            card_style = f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: {styles['border_radius']};
                    margin: {styles['spacing_small']};
                }}
                QFrame:hover {{
                    border-color: #cbd5e1;
                    background-color: #f8fafc;
                }}
            """
            
            if self.trend == "up":
                card_style += "QFrame { border-left: 4px solid #10b981; }"
            elif self.trend == "down":
                card_style += "QFrame { border-left: 4px solid #ef4444; }"
            else:
                card_style += "QFrame { border-left: 4px solid #6b7280; }"
            
            self.setStyleSheet(card_style)
    
    def get_trend_color(self):
        """Get color for trend"""
        colors = {
            "up": "#10b981",
            "down": "#ef4444",
            "stable": "#6b7280"
        }
        return colors.get(self.trend, "#6b7280")
    
    def adapt_to_device_type(self, device_type: DeviceType):
        """Adapt card to device type"""
        if device_type == DeviceType.MOBILE:
            # Mobile optimizations
            self.setMinimumHeight(100)
            self.value_label.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 700;")
            self.title_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500;")
        elif device_type == DeviceType.TABLET:
            # Tablet optimizations
            self.setMinimumHeight(110)
            self.value_label.setStyleSheet("color: #0f172a; font-size: 22px; font-weight: 700;")
            self.title_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        else:
            # Desktop optimizations
            self.setMinimumHeight(120)
            self.value_label.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 700;")
            self.title_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        
        self.apply_card_styling()
    
    def update_values(self, value: str, change: str = "", trend: str = "stable"):
        """Update card values"""
        self.value = value
        self.change = change
        self.trend = trend
        
        self.value_label.setText(value)
        if hasattr(self, 'change_label'):
            self.change_label.setText(change)
            self.change_label.setStyleSheet(f"color: {self.get_trend_color()}; font-size: 12px; font-weight: 500;")
        
        self.apply_card_styling()

class ResponsiveQuickActionButton(ResponsiveWidget):
    """Responsive quick action button"""
    
    clicked = Signal()
    
    def __init__(self, title: str, icon: str, description: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.description = description
        
        self.init_ui()
        
        # Get responsive manager
        responsive_manager = get_responsive_manager()
        if responsive_manager:
            self.set_responsive_manager(responsive_manager)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel(self.icon)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 32px; margin-bottom: 8px;")
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #0f172a; font-size: 14px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        # Description
        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setAlignment(Qt.AlignCenter)
            self.desc_label.setStyleSheet("color: #6b7280; font-size: 11px;")
            self.desc_label.setWordWrap(True)
            layout.addWidget(self.desc_label)
        
        # Apply styling
        self.apply_button_styling()
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
    
    def apply_button_styling(self):
        """Apply responsive button styling"""
        responsive_manager = get_responsive_manager()
        if responsive_manager:
            styles = responsive_manager.get_responsive_styles()

            button_style = f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: {styles['border_radius']};
                    margin: {styles['spacing_small']};
                }}
                QFrame:hover {{
                    border-color: #3b82f6;
                    background-color: #f0f9ff;
                }}
            """

            self.setStyleSheet(button_style)
    
    def adapt_to_device_type(self, device_type: DeviceType):
        """Adapt button to device type"""
        if device_type == DeviceType.MOBILE:
            # Mobile optimizations
            self.setMinimumHeight(80)
            self.setMinimumWidth(120)
            self.icon_label.setStyleSheet("font-size: 28px; margin-bottom: 6px;")
            self.title_label.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 600;")
        elif device_type == DeviceType.TABLET:
            # Tablet optimizations
            self.setMinimumHeight(90)
            self.setMinimumWidth(140)
            self.icon_label.setStyleSheet("font-size: 30px; margin-bottom: 7px;")
            self.title_label.setStyleSheet("color: #0f172a; font-size: 13px; font-weight: 600;")
        else:
            # Desktop optimizations
            self.setMinimumHeight(100)
            self.setMinimumWidth(160)
            self.icon_label.setStyleSheet("font-size: 32px; margin-bottom: 8px;")
            self.title_label.setStyleSheet("color: #0f172a; font-size: 14px; font-weight: 600;")
        
        self.apply_button_styling()
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            track_user_action("responsive_home", "quick_action_clicked", f"Quick action clicked: {self.title}")

class ResponsiveHomeDashboard(ResponsiveWidget):
    """
    Responsive home dashboard that:
    - Adapts layout based on screen size
    - Provides touch-optimized controls
    - Shows key metrics and quick actions
    - Supports mobile, tablet, and desktop layouts
    """
    
    quick_action_clicked = Signal(str)  # action_name
    
    def __init__(self, data: Dict[str, pd.DataFrame], parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data = data
        
        # Dashboard components
        self.metric_cards = []
        self.quick_action_buttons = []
        
        self.init_ui()
        
        # Get responsive manager
        responsive_manager = get_responsive_manager()
        if responsive_manager:
            self.set_responsive_manager(responsive_manager)
        
        # Setup data refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial data load
        self.refresh_data()
        
        self.logger.info("Responsive Home Dashboard initialized")
        track_system_event("responsive_home", "initialized", "Responsive home dashboard started")
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main scroll area for mobile compatibility
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # Content widget
        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Welcome section
        self.create_welcome_section()
        
        # Metrics section
        self.create_metrics_section()
        
        # Quick actions section
        self.create_quick_actions_section()
        
        # Recent activity section
        self.create_recent_activity_section()
        
        scroll_area.setWidget(self.content_widget)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
    
    def create_welcome_section(self):
        """Create welcome section"""
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 12px;
                color: white;
                padding: 20px;
            }
        """)
        
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome text
        welcome_label = QLabel("Welcome to Kitchen Dashboard")
        welcome_label.setStyleSheet("color: white; font-size: 24px; font-weight: 700; margin-bottom: 8px;")
        welcome_layout.addWidget(welcome_label)
        
        # Subtitle
        subtitle_label = QLabel(f"Today is {datetime.now().strftime('%A, %B %d, %Y')}")
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14px;")
        welcome_layout.addWidget(subtitle_label)
        
        self.main_layout.addWidget(welcome_frame)
    
    def create_metrics_section(self):
        """Create metrics section"""
        metrics_label = QLabel("Key Metrics")
        metrics_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px;")
        self.main_layout.addWidget(metrics_label)
        
        # Metrics grid
        self.metrics_frame = QFrame()
        self.metrics_layout = QGridLayout(self.metrics_frame)
        self.metrics_layout.setSpacing(16)
        
        # Create metric cards
        self.create_metric_cards()
        
        self.main_layout.addWidget(self.metrics_frame)
    
    def create_metric_cards(self):
        """Create metric cards with sample data"""
        # Sample metrics - in a real app, these would come from data analysis
        metrics_data = [
            ("Total Revenue", "$12,450", "+8.2%", "up"),
            ("Active Recipes", "133", "+5", "up"),
            ("Inventory Items", "96", "-2", "down"),
            ("Monthly Orders", "247", "+12%", "up"),
        ]
        
        for i, (title, value, change, trend) in enumerate(metrics_data):
            card = ResponsiveMetricCard(title, value, change, trend)
            self.metric_cards.append(card)
            
            # Add to grid layout
            row = i // 2
            col = i % 2
            self.metrics_layout.addWidget(card, row, col)
    
    def create_quick_actions_section(self):
        """Create quick actions section"""
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px;")
        self.main_layout.addWidget(actions_label)
        
        # Quick actions grid
        self.actions_frame = QFrame()
        self.actions_layout = QGridLayout(self.actions_frame)
        self.actions_layout.setSpacing(16)
        
        # Create quick action buttons
        self.create_quick_action_buttons()
        
        self.main_layout.addWidget(self.actions_frame)
    
    def create_quick_action_buttons(self):
        """Create quick action buttons"""
        actions_data = [
            ("Add Recipe", "🍽️", "Create new recipe"),
            ("Update Inventory", "📦", "Manage stock levels"),
            ("View Sales", "📊", "Check sales data"),
            ("Generate Report", "📄", "Create reports"),
        ]
        
        for i, (title, icon, description) in enumerate(actions_data):
            button = ResponsiveQuickActionButton(title, icon, description)
            button.clicked.connect(lambda t=title: self.quick_action_clicked.emit(t.lower().replace(' ', '_')))
            self.quick_action_buttons.append(button)
            
            # Add to grid layout
            row = i // 2
            col = i % 2
            self.actions_layout.addWidget(button, row, col)
    
    def create_recent_activity_section(self):
        """Create recent activity section"""
        activity_label = QLabel("Recent Activity")
        activity_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px;")
        self.main_layout.addWidget(activity_label)
        
        # Activity frame
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        activity_layout = QVBoxLayout(activity_frame)
        
        # Sample activity items
        activities = [
            "📦 Updated inventory for Tomatoes",
            "🍽️ Added new recipe: Pasta Carbonara",
            "📊 Generated monthly sales report",
            "💰 Processed 15 orders today",
        ]
        
        for activity in activities:
            activity_label = QLabel(activity)
            activity_label.setStyleSheet("color: #374151; font-size: 13px; padding: 4px 0;")
            activity_layout.addWidget(activity_label)
        
        self.main_layout.addWidget(activity_frame)
    
    def adapt_to_device_type(self, device_type: DeviceType):
        """Adapt dashboard to device type"""
        responsive_manager = get_responsive_manager()
        if not responsive_manager:
            return
        
        config = responsive_manager.get_responsive_layout_config(device_type)
        
        # Update grid columns for metrics and actions
        if device_type == DeviceType.MOBILE:
            # Single column layout for mobile
            self.reorganize_grid(self.metrics_layout, self.metric_cards, 1)
            self.reorganize_grid(self.actions_layout, self.quick_action_buttons, 2)
            
            # Adjust margins
            self.main_layout.setContentsMargins(12, 12, 12, 12)
            self.main_layout.setSpacing(16)
            
        elif device_type == DeviceType.TABLET:
            # Two column layout for tablet
            self.reorganize_grid(self.metrics_layout, self.metric_cards, 2)
            self.reorganize_grid(self.actions_layout, self.quick_action_buttons, 2)
            
            # Adjust margins
            self.main_layout.setContentsMargins(16, 16, 16, 16)
            self.main_layout.setSpacing(18)
            
        else:
            # Multi-column layout for desktop
            self.reorganize_grid(self.metrics_layout, self.metric_cards, 4)
            self.reorganize_grid(self.actions_layout, self.quick_action_buttons, 4)
            
            # Adjust margins
            self.main_layout.setContentsMargins(20, 20, 20, 20)
            self.main_layout.setSpacing(20)
    
    def reorganize_grid(self, layout: QGridLayout, widgets: List[QWidget], columns: int):
        """Reorganize grid layout with specified number of columns"""
        # Remove all widgets from layout
        for widget in widgets:
            layout.removeWidget(widget)
        
        # Re-add widgets with new column count
        for i, widget in enumerate(widgets):
            row = i // columns
            col = i % columns
            layout.addWidget(widget, row, col)
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            # Update metric cards with real data
            if self.data:
                # Calculate real metrics from data
                self.update_metrics_from_data()
            
            track_user_action("responsive_home", "data_refreshed", "Dashboard data refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard data: {e}")
    
    def update_metrics_from_data(self):
        """Update metrics from actual data"""
        try:
            # Revenue from sales data
            if 'sales' in self.data and not self.data['sales'].empty:
                sales_df = self.data['sales']
                if 'total_amount' in sales_df.columns:
                    total_revenue = sales_df['total_amount'].sum()
                    if len(self.metric_cards) > 0:
                        self.metric_cards[0].update_values(f"${total_revenue:,.0f}", "+8.2%", "up")
            
            # Recipe count
            if 'recipes' in self.data and not self.data['recipes'].empty:
                recipe_count = len(self.data['recipes'])
                if len(self.metric_cards) > 1:
                    self.metric_cards[1].update_values(str(recipe_count), "+5", "up")
            
            # Inventory count
            if 'inventory' in self.data and not self.data['inventory'].empty:
                inventory_count = len(self.data['inventory'])
                if len(self.metric_cards) > 2:
                    self.metric_cards[2].update_values(str(inventory_count), "-2", "down")
            
            # Order count (from sales)
            if 'sales' in self.data and not self.data['sales'].empty:
                order_count = len(self.data['sales'])
                if len(self.metric_cards) > 3:
                    self.metric_cards[3].update_values(str(order_count), "+12%", "up")
                    
        except Exception as e:
            self.logger.error(f"Error updating metrics from data: {e}")
