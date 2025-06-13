"""
Custom resizable header widget with proper cursor support for column resizing
"""

from PySide6.QtWidgets import QHeaderView, QTableWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor, QMouseEvent


class ResizableHeaderView(QHeaderView):
    """
    Custom header view that properly handles resize cursors for column resizing
    """
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)  # Enable mouse tracking for cursor changes
        self._resize_cursor_active = False
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events to show appropriate cursor"""
        try:
            # CRITICAL: Call parent implementation FIRST to ensure resize functionality works
            super().mouseMoveEvent(event)

            # Only handle horizontal headers
            if self.orientation() != Qt.Horizontal:
                return

            # Get the logical index at the mouse position
            logical_index = self.logicalIndexAt(event.pos())

            if logical_index >= 0 and logical_index < self.count() - 1:
                # Get the section position and size
                section_pos = self.sectionPosition(logical_index)
                section_size = self.sectionSize(logical_index)

                # Check if mouse is near the right edge of the section (within 8 pixels)
                mouse_x = event.pos().x()
                right_edge = section_pos + section_size

                # Check if we're in the resize zone
                in_resize_zone = abs(mouse_x - right_edge) <= 8

                if in_resize_zone and self.sectionResizeMode(logical_index) == QHeaderView.Interactive:
                    # Mouse is near column border and column is resizable, show resize cursor
                    if not self._resize_cursor_active:
                        self.setCursor(Qt.SizeHorCursor)
                        self._resize_cursor_active = True
                        print(f"🔧 Resize cursor activated for column {logical_index}")
                else:
                    # Mouse is not near border or column is not resizable, show default cursor
                    if self._resize_cursor_active:
                        self.setCursor(Qt.ArrowCursor)
                        self._resize_cursor_active = False
                        print("🔧 Resize cursor deactivated")
            else:
                # Invalid position, show default cursor
                if self._resize_cursor_active:
                    self.setCursor(Qt.ArrowCursor)
                    self._resize_cursor_active = False
                    print("🔧 Resize cursor deactivated (invalid position)")

        except Exception as e:
            # Fallback to default cursor on any error
            print(f"❌ Error in mouseMoveEvent: {e}")
            self.setCursor(Qt.ArrowCursor)
            self._resize_cursor_active = False
    
    def mousePressEvent(self, event):
        """Handle mouse press events - ensure resize functionality works"""
        # CRITICAL: Call parent implementation to enable resize functionality
        super().mousePressEvent(event)
        print(f"🔧 Mouse pressed at position {event.pos().x()}")

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        # CRITICAL: Call parent implementation to complete resize functionality
        super().mouseReleaseEvent(event)
        print(f"🔧 Mouse released at position {event.pos().x()}")

    def leaveEvent(self, event):
        """Reset cursor when mouse leaves the header"""
        super().leaveEvent(event)
        if self._resize_cursor_active:
            self.setCursor(Qt.ArrowCursor)
            self._resize_cursor_active = False
            print("🔧 Mouse left header - cursor reset")

    def enterEvent(self, event):
        """Handle mouse enter event"""
        super().enterEvent(event)
        # Reset cursor state
        self._resize_cursor_active = False
        print("🔧 Mouse entered header")


def apply_resizable_header(table_widget: QTableWidget):
    """
    Apply a custom resizable header to a table widget
    
    Args:
        table_widget: The QTableWidget to apply the resizable header to
    """
    if not isinstance(table_widget, QTableWidget):
        return
    
    # Create and set the custom header
    custom_header = ResizableHeaderView(Qt.Horizontal, table_widget)
    table_widget.setHorizontalHeader(custom_header)
    
    # Configure header properties
    custom_header.setStretchLastSection(False)
    custom_header.setDefaultAlignment(Qt.AlignLeft)
    custom_header.setMinimumSectionSize(30)
    
    # Set tooltip
    custom_header.setToolTip(
        "💡 Column Resizing Tips:\n"
        "• Hover over column borders to see the resize cursor (↔)\n"
        "• Click and drag to resize columns\n"
        "• Double-click borders to auto-fit content\n"
        "• Your column widths are automatically saved"
    )
    
    return custom_header


def enable_interactive_column_resizing(table_widget: QTableWidget, column_widths: dict = None):
    """
    Enable interactive column resizing with proper cursor support

    Args:
        table_widget: The QTableWidget to configure
        column_widths: Optional dict of column indices to default widths
    """
    if not isinstance(table_widget, QTableWidget):
        return

    print("🔧 Setting up interactive column resizing...")

    # Try the custom resizable header first
    try:
        header = apply_resizable_header(table_widget)
        print("✅ Applied custom resizable header")
    except Exception as e:
        print(f"⚠️ Custom header failed, using standard header: {e}")
        # Fallback to standard header with manual configuration
        header = table_widget.horizontalHeader()
        header.setMouseTracking(True)

    # CRITICAL: Set all columns to interactive mode
    print(f"🔧 Setting {table_widget.columnCount()} columns to Interactive mode...")
    for i in range(table_widget.columnCount()):
        header.setSectionResizeMode(i, QHeaderView.Interactive)
        print(f"   Column {i}: Interactive mode set")

    # Configure header properties for optimal resizing
    header.setStretchLastSection(False)
    header.setDefaultAlignment(Qt.AlignLeft)
    header.setMinimumSectionSize(30)
    header.setDefaultSectionSize(100)

    # Apply column widths if provided
    if column_widths:
        print("🔧 Applying column widths...")
        for col_index, width in column_widths.items():
            if 0 <= col_index < table_widget.columnCount():
                table_widget.setColumnWidth(col_index, width)
                print(f"   Column {col_index}: {width}px")

    # Enable sorting
    table_widget.setSortingEnabled(True)

    # Test resize functionality
    print("🔧 Testing resize functionality...")
    for i in range(min(3, table_widget.columnCount())):
        mode = header.sectionResizeMode(i)
        print(f"   Column {i} resize mode: {mode}")

    print("✅ Interactive column resizing setup complete!")
    return header


def create_enhanced_table_with_resizing(parent=None, column_count=0, column_headers=None):
    """
    Create a new table widget with enhanced resizing capabilities
    
    Args:
        parent: Parent widget
        column_count: Number of columns
        column_headers: List of column header labels
        
    Returns:
        QTableWidget with enhanced resizing capabilities
    """
    table = QTableWidget(parent)
    
    if column_count > 0:
        table.setColumnCount(column_count)
    
    if column_headers:
        table.setHorizontalHeaderLabels(column_headers)
        if column_count == 0:
            table.setColumnCount(len(column_headers))
    
    # Apply enhanced resizing
    enable_interactive_column_resizing(table)
    
    return table
