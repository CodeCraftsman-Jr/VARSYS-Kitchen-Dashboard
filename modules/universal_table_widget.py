"""
Universal Data Table Widget with Filtering and Sorting
Provides consistent filtering and sorting functionality across all modules
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QLineEdit, QPushButton, QComboBox,
                              QLabel, QHeaderView, QDateEdit, QCheckBox, QFrame)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QIcon
import pandas as pd
from datetime import datetime, timedelta
import logging


class UniversalTableWidget(QWidget):
    """Universal table widget with advanced filtering and sorting capabilities"""
    
    # Signals
    row_selected = Signal(int)  # Emitted when a row is selected
    data_filtered = Signal(int)  # Emitted when data is filtered (count of visible rows)
    
    def __init__(self, data=None, columns=None, parent=None, is_history_table=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Determine if this is a history table
        self.is_history_table = is_history_table
        if self.is_history_table is None:
            self.is_history_table = self._detect_history_table(data, columns)

        # Handle duplicates and sort data before storing
        self.original_data = data if data is not None else pd.DataFrame()
        if not self.original_data.empty:
            self.original_data = self.handle_duplicates_and_sort(self.original_data)

        self.filtered_data = self.original_data.copy()
        self.columns = columns if columns else []
        self.sort_column = None
        self.sort_order = Qt.AscendingOrder

        # Filter state
        self.active_filters = {}
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_filters)

        self.setup_ui()
        self.populate_table()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Filter controls section
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        filter_layout = QVBoxLayout(filter_frame)
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        # Search box
        search_label = QLabel("🔍 Search:")
        search_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        controls_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search across all columns...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        controls_layout.addWidget(self.search_input)
        
        # Date range filter (if applicable)
        self.date_filter_enabled = False
        if self.has_date_columns():
            self.date_filter_enabled = True
            
            date_label = QLabel("📅 Date Range:")
            date_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            controls_layout.addWidget(date_label)
            
            self.date_from = QDateEdit()
            # Set a much wider date range for inventory data (2 years ago to 2 years in future)
            self.date_from.setDate(QDate.currentDate().addYears(-2))
            self.date_from.setCalendarPopup(True)
            self.date_from.dateChanged.connect(self.on_date_filter_changed)
            controls_layout.addWidget(self.date_from)

            controls_layout.addWidget(QLabel("to"))

            self.date_to = QDateEdit()
            # Set end date to 2 years in the future to include all inventory items
            self.date_to.setDate(QDate.currentDate().addYears(2))
            self.date_to.setCalendarPopup(True)
            self.date_to.dateChanged.connect(self.on_date_filter_changed)
            controls_layout.addWidget(self.date_to)
        
        # Category/Status filter
        if self.has_categorical_columns():
            category_label = QLabel("📂 Category:")
            category_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            controls_layout.addWidget(category_label)
            
            self.category_filter = QComboBox()
            self.category_filter.addItem("All Categories")
            self.populate_category_filter()
            self.category_filter.currentTextChanged.connect(self.on_category_filter_changed)
            controls_layout.addWidget(self.category_filter)
        
        # Clear filters button
        controls_layout.addStretch()
        
        self.clear_filters_btn = QPushButton("🗑️ Clear Filters")
        self.clear_filters_btn.clicked.connect(self.clear_all_filters)
        self.clear_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        controls_layout.addWidget(self.clear_filters_btn)
        
        filter_layout.addLayout(controls_layout)
        
        # Filter status
        self.filter_status = QLabel("Showing all records")
        self.filter_status.setStyleSheet("color: #6c757d; font-size: 11px; margin-top: 5px;")
        filter_layout.addWidget(self.filter_status)
        
        layout.addWidget(filter_frame)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSortingEnabled(True)

        # Enable column resizing
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)  # Last column stretches to fill
        self.table.verticalHeader().setVisible(False)
        
        # Connect table signals
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e9ecef;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 10px;
                border: none;
                border-right: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
            QHeaderView::section:hover {
                background-color: #dee2e6;
                cursor: pointer;
            }
            QHeaderView::section:pressed {
                background-color: #ced4da;
            }
        """)
        
        layout.addWidget(self.table)

    def _detect_history_table(self, data, columns):
        """Automatically detect if this is a history table based on data structure and column names"""
        if data is None or (hasattr(data, 'empty') and data.empty):
            if columns:
                # Check column names for history indicators
                history_indicators = ['date', 'history', 'log', 'transaction', 'purchase', 'sale', 'waste', 'expense']
                column_str = ' '.join(str(col).lower() for col in columns)
                return any(indicator in column_str for indicator in history_indicators)
            return False

        # Check data columns for history indicators
        if hasattr(data, 'columns'):
            history_indicators = [
                'date', 'history', 'log', 'transaction', 'purchase_date', 'sale_date',
                'date_purchased', 'date_added', 'waste_id', 'sale_id', 'expense_id',
                'last_purchase_date', 'created_at', 'updated_at'
            ]
            column_names = [str(col).lower() for col in data.columns]

            # If it has multiple date columns or specific ID patterns, likely a history table
            date_columns = [col for col in column_names if any(indicator in col for indicator in ['date', 'time', 'created', 'updated'])]
            id_columns = [col for col in column_names if col.endswith('_id') and col != 'item_id']

            # History tables typically have date columns and transaction IDs
            if len(date_columns) >= 1 and len(id_columns) >= 1:
                return True

            # Check for specific history table patterns
            return any(indicator in ' '.join(column_names) for indicator in history_indicators)

        return False

    def handle_duplicates_and_sort(self, data):
        """Handle duplicate entries and apply default sorting based on table type"""
        if data.empty:
            return data

        try:
            print(f"📊 Processing {'history' if self.is_history_table else 'regular'} table with {len(data)} entries")

            # For history tables: preserve ALL entries, only sort
            if self.is_history_table:
                print("📜 History table detected - preserving all entries")
                return self._sort_data_intelligently(data, preserve_all=True)

            # For regular tables: remove duplicates and sort
            print("📋 Regular table detected - removing duplicates")
            return self._sort_data_intelligently(data, preserve_all=False)

        except Exception as e:
            self.logger.error(f"Error handling duplicates and sorting: {e}")
            return data

    def _sort_data_intelligently(self, data, preserve_all=True):
        """Sort data intelligently based on available columns"""
        try:
            # Find the primary key column for duplicate removal
            primary_key_col = None
            for col in data.columns:
                if col.endswith('_id') and col in data.columns:
                    primary_key_col = col
                    break

            # Handle duplicates based on table type
            if not preserve_all and primary_key_col:
                # Remove duplicates for regular tables
                original_count = len(data)
                data = data.drop_duplicates(subset=[primary_key_col], keep='last')
                removed_count = original_count - len(data)
                if removed_count > 0:
                    print(f"🗑️ Removed {removed_count} duplicate entries based on {primary_key_col}")
            elif preserve_all and primary_key_col:
                # Just report duplicates for history tables
                duplicate_entries = data[data.duplicated(subset=[primary_key_col], keep=False)]
                if not duplicate_entries.empty:
                    unique_duplicates = duplicate_entries[primary_key_col].nunique()
                    print(f"📊 Found {len(duplicate_entries)} entries with {unique_duplicates} duplicate IDs (preserved)")

            # Apply intelligent sorting
            sort_columns = []

            # Priority 1: Name columns
            name_columns = [col for col in data.columns if 'name' in col.lower()]
            if name_columns:
                sort_columns.append(name_columns[0])

            # Priority 2: Date columns (most recent first for history, oldest first for regular)
            date_columns = [col for col in data.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated'])]
            if date_columns:
                # For history tables, sort by date descending (newest first)
                # For regular tables, sort by date ascending (oldest first)
                sort_columns.append(date_columns[0])

            # Priority 3: Category columns
            if 'category' in data.columns and 'category' not in sort_columns:
                sort_columns.append('category')

            # Priority 4: Primary key as tiebreaker
            if primary_key_col and primary_key_col not in sort_columns:
                sort_columns.append(primary_key_col)

            # Apply sorting
            if sort_columns:
                # For history tables with dates, sort descending by date
                if self.is_history_table and date_columns:
                    ascending_order = [True] * len(sort_columns)
                    # Make date column descending (newest first)
                    date_col_index = next((i for i, col in enumerate(sort_columns) if col in date_columns), None)
                    if date_col_index is not None:
                        ascending_order[date_col_index] = False
                    data = data.sort_values(sort_columns, ascending=ascending_order, na_position='last')
                else:
                    data = data.sort_values(sort_columns, na_position='last')

                print(f"📋 Sorted data by: {', '.join(sort_columns)}")

            return data

        except Exception as e:
            self.logger.error(f"Error in intelligent sorting: {e}")
            return data

    def has_date_columns(self):
        """Check if the data has date columns"""
        if self.original_data.empty:
            return False
        
        date_keywords = ['date', 'time', 'created', 'updated', 'due', 'completed', 'last_']
        for col in self.original_data.columns:
            if any(keyword in col.lower() for keyword in date_keywords):
                return True
        return False
    
    def has_categorical_columns(self):
        """Check if the data has categorical columns"""
        if self.original_data.empty:
            return False
        
        categorical_keywords = ['category', 'status', 'type', 'priority', 'level']
        for col in self.original_data.columns:
            if any(keyword in col.lower() for keyword in categorical_keywords):
                return True
        return False
    
    def populate_category_filter(self):
        """Populate the category filter dropdown"""
        if self.original_data.empty:
            return
        
        # Find categorical columns
        categorical_cols = []
        categorical_keywords = ['category', 'status', 'type', 'priority', 'level']
        
        for col in self.original_data.columns:
            if any(keyword in col.lower() for keyword in categorical_keywords):
                categorical_cols.append(col)
        
        # Add unique values from categorical columns
        unique_values = set()
        for col in categorical_cols:
            if col in self.original_data.columns:
                values = self.original_data[col].dropna().unique()
                unique_values.update(str(val) for val in values)
        
        # Sort and add to combo box
        for value in sorted(unique_values):
            self.category_filter.addItem(value)
    
    def populate_table(self):
        """Populate the table with filtered data"""
        if self.filtered_data.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.update_filter_status(0)
            return
        
        # Set up table dimensions
        self.table.setRowCount(len(self.filtered_data))
        self.table.setColumnCount(len(self.filtered_data.columns))
        
        # Set headers
        if self.columns:
            self.table.setHorizontalHeaderLabels(self.columns)
        else:
            self.table.setHorizontalHeaderLabels(list(self.filtered_data.columns))
        
        # Populate data
        for row_idx, (_, row) in enumerate(self.filtered_data.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.table.setItem(row_idx, col_idx, item)
        
        # Update status
        self.update_filter_status(len(self.filtered_data))

        # Set optimal column widths
        self.set_optimal_column_widths()
        
        # Emit signal
        self.data_filtered.emit(len(self.filtered_data))
    
    def update_filter_status(self, visible_count):
        """Update the filter status label"""
        total_count = len(self.original_data)
        if visible_count == total_count:
            self.filter_status.setText(f"Showing all {total_count} records")
        else:
            self.filter_status.setText(f"Showing {visible_count} of {total_count} records")
    
    def on_search_changed(self):
        """Handle search input changes with debouncing"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay
    
    def on_date_filter_changed(self):
        """Handle date filter changes"""
        self.apply_filters()
    
    def on_category_filter_changed(self):
        """Handle category filter changes"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all active filters to the data"""
        try:
            self.filtered_data = self.original_data.copy()
            
            # Apply search filter
            search_text = self.search_input.text().strip().lower()
            if search_text:
                mask = pd.Series([False] * len(self.filtered_data))
                for col in self.filtered_data.columns:
                    mask |= self.filtered_data[col].astype(str).str.lower().str.contains(search_text, na=False)
                self.filtered_data = self.filtered_data[mask]
            
            # Apply date filter
            if self.date_filter_enabled and hasattr(self, 'date_from'):
                date_from = self.date_from.date().toPython()
                date_to = self.date_to.date().toPython()
                
                # Find date columns and apply filter
                for col in self.filtered_data.columns:
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated', 'due', 'completed']):
                        try:
                            date_series = pd.to_datetime(self.filtered_data[col], errors='coerce')
                            # Include items with missing dates (NaT) in the filter
                            mask = (date_series.dt.date >= date_from) & (date_series.dt.date <= date_to) | date_series.isna()
                            self.filtered_data = self.filtered_data[mask]
                            break  # Apply to first date column found
                        except:
                            continue
            
            # Apply category filter
            if hasattr(self, 'category_filter') and self.category_filter.currentText() != "All Categories":
                category_value = self.category_filter.currentText()
                
                # Find categorical columns and apply filter
                categorical_keywords = ['category', 'status', 'type', 'priority', 'level']
                for col in self.filtered_data.columns:
                    if any(keyword in col.lower() for keyword in categorical_keywords):
                        mask = self.filtered_data[col].astype(str) == category_value
                        if mask.any():
                            self.filtered_data = self.filtered_data[mask]
                            break
            
            # Repopulate table
            self.populate_table()
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
    
    def clear_all_filters(self):
        """Clear all active filters"""
        self.search_input.clear()
        
        if hasattr(self, 'date_from'):
            # Reset to wide date range for inventory data
            self.date_from.setDate(QDate.currentDate().addYears(-2))
            self.date_to.setDate(QDate.currentDate().addYears(2))
        
        if hasattr(self, 'category_filter'):
            self.category_filter.setCurrentIndex(0)
        
        self.apply_filters()
    
    def on_header_clicked(self, logical_index):
        """Handle header clicks for sorting"""
        if logical_index == self.sort_column:
            # Toggle sort order
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            # New column, default to ascending
            self.sort_column = logical_index
            self.sort_order = Qt.AscendingOrder
        
        # Apply sorting
        self.sort_data()
    
    def sort_data(self):
        """Sort the filtered data"""
        if self.sort_column is None or self.filtered_data.empty:
            return
        
        try:
            col_name = self.filtered_data.columns[self.sort_column]
            ascending = self.sort_order == Qt.AscendingOrder
            
            # Try numeric sort first, fall back to string sort
            try:
                self.filtered_data = self.filtered_data.sort_values(
                    by=col_name, 
                    ascending=ascending, 
                    key=lambda x: pd.to_numeric(x, errors='coerce')
                )
            except:
                self.filtered_data = self.filtered_data.sort_values(
                    by=col_name, 
                    ascending=ascending
                )
            
            self.populate_table()
            
        except Exception as e:
            self.logger.error(f"Error sorting data: {e}")
    
    def on_row_selected(self):
        """Handle row selection"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.row_selected.emit(current_row)
    
    def update_data(self, new_data, is_history_table=None):
        """Update the table with new data"""
        self.original_data = new_data if new_data is not None else pd.DataFrame()

        # Update history table detection if provided
        if is_history_table is not None:
            self.is_history_table = is_history_table
        elif self.is_history_table is None:
            self.is_history_table = self._detect_history_table(new_data, self.columns)

        # Handle duplicates and sort new data
        if not self.original_data.empty:
            self.original_data = self.handle_duplicates_and_sort(self.original_data)

        self.filtered_data = self.original_data.copy()

        # Repopulate category filter if it exists
        if hasattr(self, 'category_filter'):
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")
            self.populate_category_filter()

        self.populate_table()
    
    def get_selected_row_data(self):
        """Get the data for the currently selected row"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            return self.filtered_data.iloc[current_row]
        return None
    
    def get_filtered_data(self):
        """Get the currently filtered data"""
        return self.filtered_data.copy()

    def set_optimal_column_widths(self):
        """Set optimal column widths based on content and column names"""
        if self.original_data is None or self.table.columnCount() == 0:
            return

        # Define optimal widths for common column types
        column_width_map = {
            # ID columns
            'id': 80, 'item_id': 80, 'recipe_id': 80, 'staff_id': 80,

            # Name columns
            'name': 200, 'item_name': 200, 'recipe_name': 200, 'staff_name': 150,
            'category_name': 150, 'material_name': 180,

            # Category columns
            'category': 120, 'type': 100, 'status': 100,

            # Quantity and measurement columns
            'quantity': 80, 'qty_purchased': 100, 'qty_used': 80, 'qty_left': 80,
            'amount': 100, 'weight': 80, 'volume': 80,

            # Unit columns
            'unit': 60, 'units': 60,

            # Price and money columns
            'price': 100, 'price_per_unit': 100, 'avg_price': 100, 'cost': 100,
            'total_value': 120, 'total_cost': 120, 'total_spent': 120,
            'last_purchase_price': 120, 'default_cost': 100,

            # Location columns
            'location': 120, 'store': 100, 'supplier': 150,

            # Date columns
            'date': 100, 'expiry_date': 110, 'purchase_date': 110,
            'last_purchase_date': 130, 'last_updated': 120, 'created_date': 110,

            # Count columns
            'count': 80, 'purchase_count': 100, 'reorder_level': 100,

            # Description columns
            'description': 200, 'notes': 150, 'instructions': 250,

            # Boolean/status columns
            'active': 70, 'enabled': 70, 'available': 80,
        }

        # Set column widths
        for col_idx in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col_idx)
            if header_item:
                column_name = header_item.text().lower().replace(' ', '_').replace('/', '_')

                # Try exact match first
                if column_name in column_width_map:
                    width = column_width_map[column_name]
                else:
                    # Try partial matches for common patterns
                    width = 120  # Default width
                    for key, value in column_width_map.items():
                        if key in column_name:
                            width = value
                            break

                self.table.setColumnWidth(col_idx, width)

        print(f"✅ Column widths set for {self.table.columnCount()} columns")
