"""
Global table styling utilities for consistent table appearance across the application
"""

import os
import json
from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

def apply_modern_table_styling(table_widget: QTableWidget, row_height: int = 50):
    """
    Apply modern styling to a QTableWidget with proper row heights and column widths
    
    Args:
        table_widget: The QTableWidget to style
        row_height: Height for table rows (default: 50px)
    """
    
    # Set modern table styling - MODIFIED to allow custom background colors
    table_widget.setStyleSheet("""
        QTableWidget {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            gridline-color: #f1f5f9;
            selection-background-color: #fef2f2;
            font-size: 13px;
        }
        QTableWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid #f1f5f9;
            min-height: 40px;
        }
        QTableWidget::item:selected {
            color: #1e40af;
        }
        QHeaderView::section {
            background-color: #f8fafc;
            border: none;
            border-bottom: 2px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            padding: 12px 8px;
            font-weight: 600;
            color: #374151;
            min-height: 40px;
            font-size: 13px;
        }
        QHeaderView::section:hover {
            background-color: #f1f5f9;
        }
    """)
    
    # Set table properties for better display - DISABLED alternating colors to allow custom backgrounds
    table_widget.setAlternatingRowColors(False)
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)
    table_widget.setSelectionMode(QTableWidget.SingleSelection)
    
    # Set row height
    table_widget.verticalHeader().setDefaultSectionSize(row_height)
    table_widget.verticalHeader().hide()  # Hide row numbers
    
    # Set column width behavior
    header = table_widget.horizontalHeader()
    header.setStretchLastSection(True)
    header.setDefaultSectionSize(120)
    
    # Enable sorting
    table_widget.setSortingEnabled(True)

def set_table_column_widths(table_widget: QTableWidget, column_widths: dict):
    """
    Set specific column widths for a table
    
    Args:
        table_widget: The QTableWidget to modify
        column_widths: Dictionary mapping column index to width
                      e.g., {0: 200, 1: 150, 2: 100}
    """
    header = table_widget.horizontalHeader()
    for column_index, width in column_widths.items():
        if column_index < table_widget.columnCount():
            header.resizeSection(column_index, width)

def auto_resize_table_columns(table_widget: QTableWidget):
    """
    Auto-resize table columns to fit content
    
    Args:
        table_widget: The QTableWidget to resize
    """
    table_widget.resizeColumnsToContents()
    
    # Ensure minimum column widths
    header = table_widget.horizontalHeader()
    for i in range(table_widget.columnCount()):
        if header.sectionSize(i) < 80:
            header.resizeSection(i, 80)

def apply_inventory_table_styling(table_widget: QTableWidget):
    """Apply specific styling for inventory tables with enhanced resizing"""
    # Apply enhanced styling with resize cursor support
    apply_enhanced_table_styling_with_resize_cursor(table_widget, row_height=55)

    # Inventory-specific column widths
    column_widths = {
        0: 180,  # Item Name
        1: 100,  # Quantity
        2: 80,   # Unit
        3: 120,  # Price per Unit
        4: 120,  # Total Value
        5: 100,  # Category
        6: 120,  # Expiry Date
        7: 100,  # Location
        8: 80,   # Status
    }
    set_table_column_widths(table_widget, column_widths)

def apply_shopping_table_styling(table_widget: QTableWidget):
    """Apply specific styling for shopping list tables with enhanced resizing"""
    # Apply enhanced styling with resize cursor support
    apply_enhanced_table_styling_with_resize_cursor(table_widget, row_height=50)

    # Shopping-specific column widths
    column_widths = {
        0: 180,  # Item Name
        1: 100,  # Quantity
        2: 80,   # Unit
        3: 120,  # Estimated Cost
        4: 100,  # Category
        5: 120,  # Location
        6: 100,  # Priority
        7: 80,   # Status
    }
    set_table_column_widths(table_widget, column_widths)

def apply_recipe_table_styling(table_widget: QTableWidget):
    """Apply specific styling for recipe tables"""
    apply_modern_table_styling(table_widget, row_height=60)
    
    # Recipe-specific column widths
    column_widths = {
        0: 200,  # Recipe Name
        1: 120,  # Ingredient Cost
        2: 120,  # Making Cost
        3: 120,  # Total Cost
        4: 120,  # Profit Margin
        5: 120,  # Selling Price
        6: 120,  # Efficiency Score
        7: 100,  # Actions
    }
    set_table_column_widths(table_widget, column_widths)

def apply_sales_table_styling(table_widget: QTableWidget):
    """Apply specific styling for sales tables"""
    apply_modern_table_styling(table_widget, row_height=50)
    
    # Sales-specific column widths
    column_widths = {
        0: 120,  # Date
        1: 180,  # Item Name
        2: 100,  # Quantity
        3: 120,  # Unit Price
        4: 120,  # Total Amount
        5: 100,  # Payment Method
        6: 120,  # Customer
        7: 80,   # Status
    }
    set_table_column_widths(table_widget, column_widths)

def apply_logs_table_styling(table_widget: QTableWidget):
    """Apply specific styling for logs tables"""
    apply_modern_table_styling(table_widget, row_height=45)
    
    # Logs-specific column widths
    column_widths = {
        0: 140,  # Timestamp
        1: 100,  # Type
        2: 300,  # Description
        3: 120,  # Amount
        4: 100,  # Category
        5: 80,   # Status
    }
    set_table_column_widths(table_widget, column_widths)

# Color schemes for different table types
TABLE_COLORS = {
    'inventory': {
        'header_bg': '#f0f9ff',
        'header_border': '#0ea5e9',
        'row_hover': '#f0f9ff',
        'selection': '#dbeafe'
    },
    'shopping': {
        'header_bg': '#f0fdf4',
        'header_border': '#22c55e',
        'row_hover': '#f0fdf4',
        'selection': '#dcfce7'
    },
    'recipe': {
        'header_bg': '#fef3c7',
        'header_border': '#f59e0b',
        'row_hover': '#fef3c7',
        'selection': '#fde68a'
    },
    'sales': {
        'header_bg': '#fdf2f8',
        'header_border': '#ec4899',
        'row_hover': '#fdf2f8',
        'selection': '#fce7f3'
    },
    'logs': {
        'header_bg': '#f3f4f6',
        'header_border': '#6b7280',
        'row_hover': '#f3f4f6',
        'selection': '#e5e7eb'
    }
}

def enable_column_resizing_with_cursor(table_widget: QTableWidget):
    """
    Enable proper column resizing functionality with resize cursor

    Args:
        table_widget: The QTableWidget to enable resizing for
    """

    header = table_widget.horizontalHeader()

    # Enable interactive resizing for all columns
    for i in range(table_widget.columnCount()):
        header.setSectionResizeMode(i, QHeaderView.Interactive)

    # Set minimum section size to prevent columns from becoming too small
    header.setMinimumSectionSize(30)

    # Enable resize cursor on hover over column borders
    header.setCursor(Qt.ArrowCursor)  # Default cursor

    # Connect mouse events to handle cursor changes
    def on_mouse_move(event):
        """Handle mouse move events to show resize cursor"""
        try:
            # Get the logical index at the mouse position
            logical_index = header.logicalIndexAt(event.pos())
            if logical_index >= 0:
                # Get the section position and size
                section_pos = header.sectionPosition(logical_index)
                section_size = header.sectionSize(logical_index)

                # Check if mouse is near the right edge of the section (within 5 pixels)
                mouse_x = event.pos().x()
                right_edge = section_pos + section_size

                if abs(mouse_x - right_edge) <= 5 and logical_index < table_widget.columnCount() - 1:
                    # Mouse is near column border, show resize cursor
                    header.setCursor(Qt.SizeHorCursor)
                else:
                    # Mouse is not near border, show default cursor
                    header.setCursor(Qt.ArrowCursor)
            else:
                header.setCursor(Qt.ArrowCursor)
        except Exception as e:
            # Fallback to default cursor on any error
            header.setCursor(Qt.ArrowCursor)

    # Connect the mouse move event
    header.mouseMoveEvent = on_mouse_move

    # Set tooltip to inform users about resizing
    header.setToolTip("💡 Tip: Hover over column borders to resize columns!\n"
                     "Look for the ↔ cursor to drag and resize columns.")

def apply_enhanced_table_styling_with_resize_cursor(table_widget: QTableWidget, row_height: int = 50):
    """
    Apply enhanced table styling with proper column resize cursor support

    Args:
        table_widget: The QTableWidget to style
        row_height: Height for table rows (default: 50px)
    """

    # Apply base modern styling first
    apply_modern_table_styling(table_widget, row_height)

    # Enable column resizing with cursor support
    enable_column_resizing_with_cursor(table_widget)

    # Add enhanced CSS styling that includes cursor support - MODIFIED to allow custom background colors
    enhanced_style = f"""
        QTableWidget {{
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            gridline-color: #f1f5f9;
            selection-background-color: #fef2f2;
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 12px 8px;
            border-bottom: 1px solid #f1f5f9;
            min-height: {row_height - 10}px;
        }}
        QTableWidget::item:selected {{
            color: #1e40af;
        }}
        QHeaderView {{
            background-color: transparent;
        }}
        QHeaderView::section {{
            background-color: #f8fafc;
            border: none;
            border-bottom: 2px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            padding: 12px 8px;
            font-weight: 600;
            color: #374151;
            min-height: {row_height - 10}px;
            font-size: 13px;
        }}
        QHeaderView::section:hover {{
            background-color: #f1f5f9;
        }}
        QHeaderView::section:pressed {{
            background-color: #e2e8f0;
        }}
    """

    table_widget.setStyleSheet(enhanced_style)

    # Configure table properties for optimal resizing
    table_widget.setAlternatingRowColors(True)
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)
    table_widget.setSelectionMode(QTableWidget.SingleSelection)
    table_widget.verticalHeader().setDefaultSectionSize(row_height)
    table_widget.verticalHeader().hide()
    table_widget.setSortingEnabled(True)

    # Enable horizontal scrolling when needed
    table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

def apply_colored_table_styling(table_widget: QTableWidget, table_type: str, row_height: int = 50):
    """
    Apply colored styling based on table type
    
    Args:
        table_widget: The QTableWidget to style
        table_type: Type of table ('inventory', 'shopping', 'recipe', 'sales', 'logs')
        row_height: Height for table rows
    """
    colors = TABLE_COLORS.get(table_type, TABLE_COLORS['inventory'])
    
    table_widget.setStyleSheet(f"""
        QTableWidget {{
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            gridline-color: #f1f5f9;
            selection-background-color: {colors['selection']};
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 12px 8px;
            border-bottom: 1px solid #f1f5f9;
            min-height: {row_height - 10}px;
        }}
        QTableWidget::item:selected {{
            color: #1e40af;
        }}
        QHeaderView::section {{
            background-color: {colors['header_bg']};
            border: none;
            border-bottom: 2px solid {colors['header_border']};
            border-right: 1px solid #e2e8f0;
            padding: 12px 8px;
            font-weight: 600;
            color: #374151;
            min-height: {row_height - 10}px;
            font-size: 13px;
        }}
        QHeaderView::section:hover {{
            background-color: {colors['row_hover']};
        }}
    """)
    
    # Apply common table properties - DISABLED alternating colors to allow custom backgrounds
    table_widget.setAlternatingRowColors(False)
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)
    table_widget.setSelectionMode(QTableWidget.SingleSelection)
    table_widget.verticalHeader().setDefaultSectionSize(row_height)
    table_widget.verticalHeader().hide()
    table_widget.horizontalHeader().setStretchLastSection(True)
    table_widget.setSortingEnabled(True)

def create_table_button_widget(button_text: str, button_color: str, button_size: tuple = (80, 35),
                              container_margins: tuple = (2, 3, 2, 3)) -> tuple:
    """
    Create a properly contained button widget for table cells to prevent overlap

    Args:
        button_text: Text to display on the button
        button_color: Background color for the button ('blue', 'red', 'green', or 'gray')
        button_size: Tuple of (width, height) for button size
        container_margins: Tuple of (left, top, right, bottom) margins for container

    Returns:
        Tuple of (container_widget, button_widget) for easy access
    """
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

    # Create container widget
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(*container_margins)
    layout.setSpacing(0)

    # Create button
    button = QPushButton(button_text)
    button.setFixedSize(*button_size)

    # Set button style based on color
    if button_color == "blue":
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    elif button_color == "red":
        button_style = """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
    elif button_color == "green":
        button_style = """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #229954;
                border-color: #1e8449;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
    else:
        # Default gray style
        button_style = """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
                border-color: #6c7b7d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """

    button.setStyleSheet(button_style)
    layout.addWidget(button)

    return container, button


# ============================================================================
# UNIVERSAL COLUMN RESIZING FUNCTIONALITY
# ============================================================================

class UniversalTableColumnResizer:
    """
    Universal column resizing functionality that can be applied to any table.
    Based on the proven implementation from the inventory tab.
    """

    def __init__(self, table_widget: QTableWidget, settings_file_name: str, default_column_widths: dict = None):
        """
        Initialize the column resizer for a table

        Args:
            table_widget: The QTableWidget to add resizing to
            settings_file_name: Name of the JSON file to save column settings (e.g., 'shopping_column_settings.json')
            default_column_widths: Dict of column index to default width {0: 150, 1: 100, ...}
        """
        self.table_widget = table_widget
        self.settings_file_name = settings_file_name
        self.column_settings_file = os.path.join('data', settings_file_name)
        self.default_column_widths = default_column_widths or {}
        self._resize_timer = None

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)

        # Apply the column resizing functionality
        self.setup_column_resizing()

    def setup_column_resizing(self):
        """Set up column resizing functionality using the proven inventory tab pattern"""
        try:
            print(f"🔧 Setting up column resizing for {self.settings_file_name}...")

            # Get the header
            header = self.table_widget.horizontalHeader()

            # Load saved column settings or use defaults
            saved_settings = self.load_column_settings()

            # Apply column widths FIRST
            print("🔧 Setting column widths...")
            for col in range(self.table_widget.columnCount()):
                if saved_settings and f'column_{col}_width' in saved_settings:
                    # Use saved width
                    width = saved_settings[f'column_{col}_width']
                    self.table_widget.setColumnWidth(col, width)
                    print(f"   Column {col}: Using saved width {width}px")
                else:
                    # Use default width
                    width = self.default_column_widths.get(col, 100)
                    self.table_widget.setColumnWidth(col, width)
                    print(f"   Column {col}: Using default width {width}px")

            # CRITICAL: Set ALL columns to Interactive mode for manual resizing
            print("🔧 Enabling Interactive mode for all columns...")
            for col in range(self.table_widget.columnCount()):
                header.setSectionResizeMode(col, QHeaderView.Interactive)
                print(f"   Column {col}: Interactive")

            # Basic header configuration
            header.setStretchLastSection(False)
            header.setMinimumSectionSize(30)
            header.setDefaultAlignment(Qt.AlignLeft)

            # Connect resize events for saving settings
            header.sectionResized.connect(self.on_column_resized)

            # Test that resizing is actually enabled
            print("🔧 Testing resize modes...")
            for col in range(min(5, self.table_widget.columnCount())):
                mode = header.sectionResizeMode(col)
                print(f"   Column {col} mode: {mode} (should be 1 for Interactive)")

            print(f"✅ Column resizing setup complete for {self.settings_file_name}!")

        except Exception as e:
            print(f"❌ Error setting up column resizing: {e}")

    def save_column_settings(self):
        """Save column widths to file"""
        try:
            settings = {}
            for col in range(self.table_widget.columnCount()):
                settings[f'column_{col}_width'] = self.table_widget.columnWidth(col)

            with open(self.column_settings_file, 'w') as f:
                json.dump(settings, f)
            print(f"✅ Column settings saved to {self.column_settings_file}")
        except Exception as e:
            print(f"❌ Error saving column settings: {e}")

    def load_column_settings(self):
        """Load column widths from file"""
        try:
            if os.path.exists(self.column_settings_file):
                with open(self.column_settings_file, 'r') as f:
                    settings = json.load(f)
                print(f"✅ Loading saved column settings from {self.column_settings_file}...")
                return settings
            else:
                print(f"📝 No saved column settings found for {self.column_settings_file}, using defaults")
                return None
        except Exception as e:
            print(f"❌ Error loading column settings: {e}")
            return None

    def on_column_resized(self, logical_index, old_size, new_size):
        """Handle column resize events and save settings"""
        try:
            # Save settings after a short delay to avoid too frequent saves
            if not self._resize_timer:
                self._resize_timer = QTimer()
                self._resize_timer.setSingleShot(True)
                self._resize_timer.timeout.connect(self.save_column_settings)

            self._resize_timer.start(500)  # Save after 500ms of no resizing
            print(f"📏 Column {logical_index} resized from {old_size}px to {new_size}px")
        except Exception as e:
            print(f"❌ Error handling column resize: {e}")

    def auto_fit_columns(self):
        """Auto-fit columns to available screen width"""
        try:
            print("📐 Auto-fitting columns to screen width...")

            # Get available width (table width minus scrollbar and margins)
            table_width = self.table_widget.width()
            scrollbar_width = 20  # Approximate scrollbar width
            margin_width = 40     # Margins and borders
            available_width = table_width - scrollbar_width - margin_width

            print(f"   📊 Table width: {table_width}px")
            print(f"   📊 Available width: {available_width}px")

            if available_width < 500:  # Minimum reasonable width
                print("   ⚠️ Available width too small, using minimum widths")
                available_width = 1200  # Use a reasonable default

            # Calculate proportional widths
            total_columns = self.table_widget.columnCount()
            if total_columns > 0:
                # Give each column a proportional width
                base_width = available_width // total_columns

                # Apply minimum width constraints
                min_width = 60
                base_width = max(base_width, min_width)

                print(f"   📊 Base width per column: {base_width}px")

                # Set column widths
                for col in range(total_columns):
                    self.table_widget.setColumnWidth(col, base_width)
                    print(f"   📏 Column {col}: {base_width}px")

                # Save the new settings
                self.save_column_settings()

                print("✅ Columns auto-fitted to screen width!")
                QMessageBox.information(None, "Columns Auto-Fitted",
                                      f"All columns have been auto-fitted to the available screen width.")

        except Exception as e:
            print(f"❌ Error auto-fitting columns: {e}")

    def make_columns_wider(self):
        """Make all columns wider for better data visibility"""
        try:
            print("🔍 Making columns wider...")

            # Increase all column widths by 20%
            for col in range(self.table_widget.columnCount()):
                current_width = self.table_widget.columnWidth(col)
                new_width = int(current_width * 1.2)
                # Set minimum width to ensure readability
                new_width = max(new_width, 60)
                self.table_widget.setColumnWidth(col, new_width)
                print(f"   📏 Column {col}: {current_width}px → {new_width}px")

            # Save the new settings
            self.save_column_settings()

            print("✅ All columns made wider!")
            QMessageBox.information(None, "Columns Widened",
                                  "All columns have been made 20% wider for better data visibility.")

        except Exception as e:
            print(f"❌ Error making columns wider: {e}")

    def reset_column_widths(self):
        """Reset all columns to default widths"""
        try:
            print("↩️ Resetting column widths to defaults...")

            # Apply default widths
            for col in range(self.table_widget.columnCount()):
                width = self.default_column_widths.get(col, 100)
                self.table_widget.setColumnWidth(col, width)
                print(f"   📏 Column {col}: Reset to {width}px")

            # Save the new settings
            self.save_column_settings()

            print("✅ Column widths reset to defaults!")
            QMessageBox.information(None, "Columns Reset",
                                  "All columns have been reset to their default widths.")

        except Exception as e:
            print(f"❌ Error resetting column widths: {e}")


def apply_universal_column_resizing(table_widget: QTableWidget, settings_file_name: str,
                                  default_column_widths: dict = None) -> UniversalTableColumnResizer:
    """
    Apply universal column resizing functionality to any table widget.

    Args:
        table_widget: The QTableWidget to add resizing to
        settings_file_name: Name of the JSON file to save column settings (e.g., 'shopping_column_settings.json')
        default_column_widths: Dict of column index to default width {0: 150, 1: 100, ...}

    Returns:
        UniversalTableColumnResizer instance for additional control
    """
    return UniversalTableColumnResizer(table_widget, settings_file_name, default_column_widths)
