"""
Responsive Table Utilities
Utilities for making QTableWidget responsive across different screen sizes
"""

from PySide6.QtWidgets import QTableWidget, QHeaderView, QWidget
from PySide6.QtCore import Qt
from typing import Dict, Optional
import logging

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

class ResponsiveTableManager:
    """Manager for making tables responsive"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.responsive_manager = get_responsive_manager()
        
    def make_table_responsive(self, table_widget: QTableWidget, column_config: Dict = None):
        """
        Make a table widget responsive to different screen sizes
        
        Args:
            table_widget: QTableWidget to make responsive
            column_config: Dict with column configuration
                {
                    'priorities': {col_index: priority},  # 1=highest, 5=lowest
                    'widths': {col_index: width},          # Fixed widths for columns
                    'min_widths': {col_index: min_width},  # Minimum widths
                    'stretch_columns': [col_indices],      # Columns that should stretch
                }
        """
        if not isinstance(table_widget, QTableWidget):
            self.logger.warning("Invalid table widget provided")
            return
            
        if not self.responsive_manager:
            self.logger.warning("Responsive manager not available")
            return
            
        # Set default configuration if not provided
        if column_config is None:
            column_config = self._get_default_column_config(table_widget)
            
        # Store configuration on the table widget
        table_widget.setProperty("responsive_config", column_config)
        
        # Apply initial responsive behavior
        self._apply_responsive_behavior(table_widget)
        
        # Set up responsive styling
        self._apply_responsive_styling(table_widget)
        
        self.logger.info(f"Made table responsive with {table_widget.columnCount()} columns")
        
    def _get_default_column_config(self, table_widget: QTableWidget) -> Dict:
        """Get default column configuration for a table"""
        column_count = table_widget.columnCount()
        
        # Default priorities: first 3 columns are high priority, rest are medium/low
        priorities = {}
        for i in range(column_count):
            if i < 2:  # First 2 columns are highest priority
                priorities[i] = 1
            elif i < 4:  # Next 2 columns are high priority
                priorities[i] = 2
            elif i < 6:  # Next 2 columns are medium priority
                priorities[i] = 3
            else:  # Rest are low priority
                priorities[i] = 4
                
        return {
            'priorities': priorities,
            'widths': {},
            'min_widths': {},
            'stretch_columns': list(range(min(3, column_count)))  # First 3 columns stretch
        }
        
    def _apply_responsive_behavior(self, table_widget: QTableWidget):
        """Apply responsive behavior based on current device type"""
        if not self.responsive_manager:
            return
            
        config = table_widget.property("responsive_config") or {}
        priorities = config.get('priorities', {})
        widths = config.get('widths', {})
        min_widths = config.get('min_widths', {})
        stretch_columns = config.get('stretch_columns', [])
        
        device_type = self.responsive_manager.current_device_type
        header = table_widget.horizontalHeader()
        
        if device_type == DeviceType.MOBILE:
            self._apply_mobile_behavior(table_widget, header, priorities, widths, min_widths, stretch_columns)
        elif device_type == DeviceType.TABLET:
            self._apply_tablet_behavior(table_widget, header, priorities, widths, min_widths, stretch_columns)
        else:  # Desktop and large desktop
            self._apply_desktop_behavior(table_widget, header, priorities, widths, min_widths, stretch_columns)
            
    def _apply_mobile_behavior(self, table_widget, header, priorities, widths, min_widths, stretch_columns):
        """Apply mobile-specific table behavior"""
        # Hide low priority columns (priority 4 and 5)
        for col_index, priority in priorities.items():
            if priority >= 4:
                table_widget.setColumnHidden(col_index, True)
            else:
                table_widget.setColumnHidden(col_index, False)
                
        # Set all visible columns to stretch
        for i in range(table_widget.columnCount()):
            if not table_widget.isColumnHidden(i):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
                
        # Enable horizontal scrolling
        table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set larger row height for touch
        table_widget.verticalHeader().setDefaultSectionSize(60)
        
    def _apply_tablet_behavior(self, table_widget, header, priorities, widths, min_widths, stretch_columns):
        """Apply tablet-specific table behavior"""
        # Hide only lowest priority columns (priority 5)
        for col_index, priority in priorities.items():
            if priority >= 5:
                table_widget.setColumnHidden(col_index, True)
            else:
                table_widget.setColumnHidden(col_index, False)
                
        # Mix of fixed and stretch columns
        for i in range(table_widget.columnCount()):
            if not table_widget.isColumnHidden(i):
                priority = priorities.get(i, 3)
                if i in stretch_columns or priority <= 2:
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.Fixed)
                    if i in widths:
                        table_widget.setColumnWidth(i, widths[i])
                        
        # Set medium row height
        table_widget.verticalHeader().setDefaultSectionSize(55)
        
    def _apply_desktop_behavior(self, table_widget, header, priorities, widths, min_widths, stretch_columns):
        """Apply desktop-specific table behavior"""
        # Show all columns
        for col_index in priorities.keys():
            table_widget.setColumnHidden(col_index, False)

        # Set appropriate resize modes - prefer Interactive for manual resizing
        for i in range(table_widget.columnCount()):
            priority = priorities.get(i, 3)
            if i in stretch_columns and len(stretch_columns) > 0:
                # Only apply stretch if stretch_columns is not empty
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                # Default to Interactive for manual resizing on desktop
                header.setSectionResizeMode(i, QHeaderView.Interactive)
                if i in widths:
                    table_widget.setColumnWidth(i, widths[i])
                    
        # Set standard row height
        table_widget.verticalHeader().setDefaultSectionSize(50)
        
    def _apply_responsive_styling(self, table_widget: QTableWidget):
        """Apply responsive styling to the table"""
        if not self.responsive_manager:
            return
            
        styles = self.responsive_manager.get_responsive_styles()
        device_type = self.responsive_manager.current_device_type
        
        # Base table styling
        table_style = f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: {styles['border_radius']};
                gridline-color: #f1f5f9;
                selection-background-color: #dbeafe;
                font-size: {styles['font_size_normal']};
                alternate-background-color: #f8fafc;
            }}
            QTableWidget::item {{
                padding: {styles['spacing_normal']};
                border-bottom: 1px solid #f1f5f9;
            }}
            QTableWidget::item:selected {{
                background-color: #dbeafe;
                color: #1e40af;
            }}
            QHeaderView::section {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                padding: {styles['spacing_normal']};
                font-weight: 600;
                font-size: {styles['font_size_normal']};
                color: #374151;
            }}
        """
        
        # Add device-specific styling
        if device_type == DeviceType.MOBILE:
            table_style += f"""
                QTableWidget::item {{
                    min-height: 44px;
                    padding: {styles['spacing_large']};
                }}
                QHeaderView::section {{
                    min-height: 48px;
                    padding: {styles['spacing_large']};
                }}
            """
        elif device_type == DeviceType.TABLET:
            table_style += f"""
                QTableWidget::item {{
                    min-height: 40px;
                }}
                QHeaderView::section {{
                    min-height: 44px;
                }}
            """
            
        table_widget.setStyleSheet(table_style)
        
    def update_table_responsiveness(self, table_widget: QTableWidget):
        """Update table responsiveness when device type changes"""
        if not isinstance(table_widget, QTableWidget):
            return
            
        config = table_widget.property("responsive_config")
        if config:
            self._apply_responsive_behavior(table_widget)
            self._apply_responsive_styling(table_widget)

# Global instance
_responsive_table_manager = None

def get_responsive_table_manager():
    """Get the global responsive table manager instance"""
    global _responsive_table_manager
    if _responsive_table_manager is None:
        _responsive_table_manager = ResponsiveTableManager()
    return _responsive_table_manager

def make_table_responsive(table_widget: QTableWidget, column_config: Dict = None):
    """Convenience function to make a table responsive"""
    manager = get_responsive_table_manager()
    return manager.make_table_responsive(table_widget, column_config)
