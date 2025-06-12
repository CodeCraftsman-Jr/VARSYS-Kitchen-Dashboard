"""
Global table styling utilities for consistent table appearance across the application
"""

from PySide6.QtWidgets import QTableWidget, QHeaderView
from PySide6.QtCore import Qt

def apply_modern_table_styling(table_widget: QTableWidget, row_height: int = 50):
    """
    Apply modern styling to a QTableWidget with proper row heights and column widths
    
    Args:
        table_widget: The QTableWidget to style
        row_height: Height for table rows (default: 50px)
    """
    
    # Set modern table styling
    table_widget.setStyleSheet("""
        QTableWidget {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            gridline-color: #f1f5f9;
            selection-background-color: #fef2f2;
            font-size: 13px;
            alternate-background-color: #f8fafc;
        }
        QTableWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid #f1f5f9;
            min-height: 40px;
        }
        QTableWidget::item:selected {
            background-color: #dbeafe;
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
    
    # Set table properties for better display
    table_widget.setAlternatingRowColors(True)
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
    """Apply specific styling for inventory tables"""
    apply_modern_table_styling(table_widget, row_height=55)
    
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
    """Apply specific styling for shopping list tables"""
    apply_modern_table_styling(table_widget, row_height=50)
    
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
            alternate-background-color: #f8fafc;
        }}
        QTableWidget::item {{
            padding: 12px 8px;
            border-bottom: 1px solid #f1f5f9;
            min-height: {row_height - 10}px;
        }}
        QTableWidget::item:selected {{
            background-color: {colors['selection']};
            color: #1e40af;
        }}
        QTableWidget::item:hover {{
            background-color: {colors['row_hover']};
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
    
    # Apply common table properties
    table_widget.setAlternatingRowColors(True)
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
