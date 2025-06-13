from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                             QMessageBox, QHeaderView, QSplitter, QDialog, QScrollArea,
                             QCheckBox, QFrame)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import datetime
import os
import json

# Import notification system
try:
    from .notification_system import notify_info, notify_success, notify_warning, notify_error
except ImportError:
    def notify_info(title, message, **kwargs): pass
    def notify_success(title, message, **kwargs): pass
    def notify_warning(title, message, **kwargs): pass
    def notify_error(title, message, **kwargs): pass

# Import table styling utility
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.table_styling import apply_inventory_table_styling, apply_modern_table_styling
except ImportError:
    print("Warning: Could not import table styling utility")
    apply_inventory_table_styling = None
    apply_modern_table_styling = None

class InventoryWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.inventory_df = data['inventory'].copy()

        # Column settings file path
        self.column_settings_file = 'data/inventory_column_settings.json'

        # Debug: Check data received
        print(f"🔍 INVENTORY WIDGET INIT DEBUG:")
        print(f"  Data keys: {list(data.keys()) if data else 'None'}")
        print(f"  Inventory shape: {data['inventory'].shape if 'inventory' in data else 'No inventory key'}")
        print(f"  Inventory DF shape: {self.inventory_df.shape}")
        print(f"  First 3 items: {list(self.inventory_df['item_name'].head(3)) if 'item_name' in self.inventory_df.columns else 'No item_name column'}")
        print(f"  📊 TOTAL INVENTORY RECORDS: {len(self.inventory_df)}")
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title and refresh button layout
        title_layout = QHBoxLayout()

        title_label = QLabel("Inventory Management")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Add refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        refresh_button.clicked.connect(self.refresh_data)
        title_layout.addWidget(refresh_button)

        self.layout.addLayout(title_layout)
    
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for different inventory views
        self.current_inventory_tab = QWidget()
        self.items_tab = QWidget()
        self.categories_tab = QWidget()
        self.add_edit_tab = QWidget()
        self.expiry_tab = QWidget()
        self.category_analysis_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.current_inventory_tab, "Current Inventory")
        self.tabs.addTab(self.items_tab, "Items")
        self.tabs.addTab(self.categories_tab, "Categories")
        self.tabs.addTab(self.add_edit_tab, "Add/Edit Items")
        self.tabs.addTab(self.expiry_tab, "Expiry Tracking")
        self.tabs.addTab(self.category_analysis_tab, "Category Analysis")
        
        # Set up each tab
        self.setup_current_inventory_tab()
        self.setup_items_tab()
        self.setup_categories_tab()
        self.setup_add_edit_tab()
        self.setup_expiry_tab()
        self.setup_category_analysis_tab()

        # Connect tab change event to refresh data
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def save_column_settings(self):
        """Save column widths to file"""
        try:
            if hasattr(self, 'inventory_table'):
                settings = {}
                for col in range(self.inventory_table.columnCount()):
                    settings[f'column_{col}_width'] = self.inventory_table.columnWidth(col)

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

                print(f"✅ Loading saved column settings...")
                return settings
            else:
                print(f"📝 No saved column settings found, using defaults")
                return None
        except Exception as e:
            print(f"❌ Error loading column settings: {e}")
            return None

    def on_tab_changed(self, index):
        """Handle tab change events to refresh data"""
        try:
            tab_name = self.tabs.tabText(index)
            print(f"🔄 Switched to {tab_name} tab")

            # Force reload data from CSV files
            self.reload_data_from_files()

            if tab_name == "Categories":
                # Refresh categories data
                if 'categories' in self.data:
                    self.categories_df = self.data['categories'].copy()
                    self.update_categories_table()

            elif tab_name == "Items":
                # Refresh items data
                if 'items' in self.data:
                    self.items_df = self.data['items'].copy()
                    self.update_items_table()

            elif tab_name == "Current Inventory":
                # Refresh inventory data
                if 'inventory' in self.data:
                    self.inventory_df = self.data['inventory'].copy()
                    self.apply_filters()

        except Exception as e:
            print(f"Error refreshing tab data: {e}")

    def reload_data_from_files(self):
        """Force reload data from CSV files"""
        try:
            import pandas as pd
            import os

            # Reload items data
            items_file = 'data/items.csv'
            if os.path.exists(items_file):
                self.data['items'] = pd.read_csv(items_file)
                self.items_df = self.data['items'].copy()
                print(f"🔄 Reloaded items data: {len(self.data['items'])} items")
            else:
                self.data['items'] = pd.DataFrame(columns=['item_id', 'item_name', 'category', 'description', 'unit'])
                self.items_df = self.data['items'].copy()
                print("🔄 Items file not found, created empty dataframe")

            # Reload inventory data
            inventory_file = 'data/inventory.csv'
            if os.path.exists(inventory_file):
                self.data['inventory'] = pd.read_csv(inventory_file)
                self.inventory_df = self.data['inventory'].copy()
                print(f"🔄 Reloaded inventory data: {len(self.data['inventory'])} items")
            else:
                # Create empty inventory with proper columns
                self.data['inventory'] = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'price_per_unit',
                    'location', 'expiry_date', 'reorder_level', 'total_value', 'price',
                    'qty_purchased', 'qty_used', 'avg_price', 'description', 'default_cost',
                    'purchase_count', 'total_spent', 'last_purchase_date', 'last_purchase_price'
                ])
                self.inventory_df = self.data['inventory'].copy()
                print("🔄 Inventory file not found, created empty dataframe")

            # Reload categories data
            categories_file = 'data/categories.csv'
            if os.path.exists(categories_file):
                self.data['categories'] = pd.read_csv(categories_file)
                self.categories_df = self.data['categories'].copy()
                print(f"🔄 Reloaded categories data: {len(self.data['categories'])} categories")

        except Exception as e:
            print(f"Error reloading data from files: {e}")

    def refresh_all_data(self):
        """Force refresh all data from CSV files"""
        try:
            # Reload data from CSV files
            import pandas as pd
            import os

            if os.path.exists('data/categories.csv'):
                self.data['categories'] = pd.read_csv('data/categories.csv')
                self.categories_df = self.data['categories'].copy()

            if os.path.exists('data/items.csv'):
                self.data['items'] = pd.read_csv('data/items.csv')
                self.items_df = self.data['items'].copy()

            if os.path.exists('data/inventory.csv'):
                self.data['inventory'] = pd.read_csv('data/inventory.csv')
                self.inventory_df = self.data['inventory'].copy()

            # Update all tables
            self.update_categories_table()
            self.update_items_table()
            self.apply_filters()

            print("Inventory data refreshed successfully")

        except Exception as e:
            print(f"Error refreshing inventory data: {e}")

    def setup_current_inventory_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.current_inventory_tab)
        layout.setContentsMargins(10, 5, 10, 10)  # Reduce margins to save space
        
        # Add compact subheader
        header = QLabel("Current Inventory")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setMaximumHeight(25)  # Limit header height
        layout.addWidget(header)
        
        # Check if there's data in the items tab
        if 'items' not in self.data or len(self.data['items']) == 0:
            # Show message when no items exist
            no_items_label = QLabel("No items available. Please add items in the Items tab first.")
            no_items_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_items_label)
            return
        
        # Filters section
        filters_widget = QWidget()
        filters_layout = QHBoxLayout(filters_widget)
        
        # Category filter
        category_label = QLabel("Filter by Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        if 'category' in self.inventory_df.columns:
            # Filter out NaN values and convert to strings before sorting
            categories = self.inventory_df['category'].dropna().unique()
            category_strings = [str(cat) for cat in categories if pd.notna(cat)]
            if category_strings:
                self.category_combo.addItems(sorted(category_strings))
        self.category_combo.currentIndexChanged.connect(self.apply_filters)
        
        # Location filter
        location_label = QLabel("Filter by Location:")
        self.location_combo = QComboBox()
        self.location_combo.addItem("All Locations")
        if 'location' in self.inventory_df.columns:
            # Filter out NaN values and convert to strings before sorting
            locations = self.inventory_df['location'].dropna().unique()
            location_strings = [str(loc) for loc in locations if pd.notna(loc)]
            if location_strings:
                self.location_combo.addItems(sorted(location_strings))
        self.location_combo.currentIndexChanged.connect(self.apply_filters)
        
        # Search box
        search_label = QLabel("Search Items:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter search term...")
        self.search_box.textChanged.connect(self.apply_filters)
        
        # Add widgets to filters layout
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(self.category_combo)
        filters_layout.addWidget(location_label)
        filters_layout.addWidget(self.location_combo)
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.search_box)
        filters_layout.addStretch(1)  # Add stretch to push widgets to the left
        
        layout.addWidget(filters_widget)

        # Create a fixed header area for action buttons that stays at the top
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px 0;
            }
        """)
        header_frame.setFixedHeight(60)  # Fixed height to prevent resizing

        # Action buttons section (fixed at top)
        buttons_layout = QHBoxLayout(header_frame)
        buttons_layout.setContentsMargins(10, 8, 10, 8)  # Consistent margins

        # Edit Selected Item button
        self.edit_inventory_button = QPushButton("Edit Selected Item")
        self.edit_inventory_button.setFixedHeight(40)  # Fixed button height
        self.edit_inventory_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.edit_inventory_button.clicked.connect(self.edit_selected_inventory_item)

        # Refresh Data button
        self.refresh_inventory_button = QPushButton("Refresh Data")
        self.refresh_inventory_button.setFixedHeight(40)  # Fixed button height
        self.refresh_inventory_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.refresh_inventory_button.clicked.connect(self.force_refresh_inventory)

        # Show All Items button
        self.show_all_button = QPushButton("Show All Items")
        self.show_all_button.setFixedHeight(40)  # Fixed button height
        self.show_all_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 110px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.show_all_button.clicked.connect(self.show_all_items)

        # Auto-fit columns button
        self.autofit_button = QPushButton("📐 Auto-Fit Columns")
        self.autofit_button.setFixedHeight(40)  # Fixed button height
        self.autofit_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.autofit_button.clicked.connect(self.auto_fit_columns)
        self.autofit_button.setToolTip("Automatically resize columns to fit screen width")

        # Add buttons to layout with proper spacing
        buttons_layout.addWidget(self.edit_inventory_button)
        buttons_layout.addSpacing(10)  # Add space between buttons
        buttons_layout.addWidget(self.refresh_inventory_button)
        buttons_layout.addSpacing(10)  # Add space between buttons
        buttons_layout.addWidget(self.show_all_button)
        buttons_layout.addSpacing(10)  # Add space between buttons
        buttons_layout.addWidget(self.autofit_button)
        buttons_layout.addStretch()  # Push buttons to the left

        # Add the fixed header to the layout
        layout.addWidget(header_frame)

        # Create a container for the table with proper scrolling
        table_container = QWidget()
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        table_container_layout.setSpacing(0)

        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(17)  # Added purchase tracking columns
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Name", "Category", "Total Qty", "Used Qty", "Available Qty", "Unit",
            "Avg Price", "Price/Unit", "Total Value", "Location", "Purchase Count",
            "Total Spent", "Last Purchase Date", "Last Purchase Price", "Expiry Date", "Days Left"
        ])

        # Configure table scrolling and sizing
        self.inventory_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.inventory_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.inventory_table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)

        # Ensure the table shows horizontal scrollbar when content is wider than view
        self.inventory_table.setMinimumWidth(800)  # Minimum width to trigger horizontal scroll

        # Set column resize modes - each column independently resizable
        header = self.inventory_table.horizontalHeader()

        # Set all columns to fixed width initially to prevent auto-resizing
        for i in range(17):
            header.setSectionResizeMode(i, QHeaderView.Fixed)

        # Optimized column widths to fit screen perfectly (total ~1100px)
        default_column_widths = {
            0: 35,   # ID - minimal space
            1: 110,  # Name - essential but compact
            2: 75,   # Category - compact
            3: 65,   # Total Qty - compact
            4: 60,   # Used Qty - compact
            5: 70,   # Available Qty - compact
            6: 40,   # Unit - minimal
            7: 70,   # Avg Price - compact
            8: 75,   # Price/Unit - compact
            9: 80,   # Total Value - compact
            10: 80,  # Location - compact
            11: 65,  # Purchase Count - compact
            12: 80,  # Total Spent - compact
            13: 95,  # Last Purchase Date - reduced
            14: 95,  # Last Purchase Price - reduced
            15: 85,  # Expiry Date - compact
            16: 70   # Days Left - compact
        }

        # Load saved column settings or use defaults
        saved_settings = self.load_column_settings()

        # Set global minimum section size to prevent columns from becoming too small
        header.setMinimumSectionSize(30)

        # Make ALL columns user-resizable and independent
        for col in range(17):
            header.setSectionResizeMode(col, QHeaderView.Interactive)

        # Apply column widths (saved or default)
        for col in range(17):
            if saved_settings and f'column_{col}_width' in saved_settings:
                # Use saved width
                width = saved_settings[f'column_{col}_width']
                self.inventory_table.setColumnWidth(col, width)
                print(f"📏 Column {col}: Using saved width {width}px")
            else:
                # Use default width
                width = default_column_widths.get(col, 100)
                self.inventory_table.setColumnWidth(col, width)
                print(f"📏 Column {col}: Using default width {width}px")

        # Connect column resize event to save settings
        header.sectionResized.connect(self.on_column_resized)

        print(f"✅ All columns are now user-resizable and will remember their positions!")

        # Keep other columns fixed to prevent unwanted resizing
        # This ensures that resizing one column doesn't affect others

        # Apply responsive table functionality
        try:
            from modules.responsive_table_utils import make_table_responsive

            # Define column priorities for responsive behavior
            column_priorities = {
                0: 5,   # ID - lowest priority (hide on mobile)
                1: 1,   # Name - highest priority (always show)
                2: 2,   # Category - high priority
                3: 3,   # Total Qty - medium priority
                4: 4,   # Used Qty - low priority
                5: 2,   # Available Qty - high priority
                6: 3,   # Unit - medium priority
                7: 4,   # Avg Price - low priority
                8: 3,   # Price/Unit - medium priority
                9: 2,   # Total Value - high priority
                10: 3,  # Location - medium priority
                11: 5,  # Purchase Count - lowest priority
                12: 4,  # Total Spent - low priority
                13: 5,  # Last Purchase Date - lowest priority
                14: 5,  # Last Purchase Price - lowest priority
                15: 3,  # Expiry Date - medium priority
                16: 3   # Days Left - medium priority
            }

            # Configure responsive table
            column_config = {
                'priorities': column_priorities,
                'widths': default_column_widths,
                'stretch_columns': [1, 2, 5, 9]  # Name, Category, Available Qty, Total Value
            }

            make_table_responsive(self.inventory_table, column_config)
            print("✅ Applied responsive table functionality")

        except ImportError:
            print("⚠️ Responsive table utilities not available, using standard styling")

        # Apply modern table styling
        if apply_inventory_table_styling:
            apply_inventory_table_styling(self.inventory_table)
        else:
            # Enhanced fallback styling
            self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.inventory_table.setAlternatingRowColors(True)
            self.inventory_table.verticalHeader().setDefaultSectionSize(55)  # Set row height
            self.inventory_table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    gridline-color: #f1f5f9;
                    selection-background-color: #dbeafe;
                    font-size: 13px;
                    alternate-background-color: #f8fafc;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #f1f5f9;
                    min-height: 40px;
                }
                QTableWidget::item:selected {
                    background-color: #dbeafe;
                    color: #1e40af;
                }
                QHeaderView::section {
                    background-color: #f0f9ff;
                    border: none;
                    border-bottom: 2px solid #0ea5e9;
                    border-right: 1px solid #e2e8f0;
                    padding: 12px 8px;
                    font-weight: 600;
                    color: #374151;
                    min-height: 40px;
                    font-size: 13px;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #f1f5f9;
                    height: 14px;
                    margin: 0px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background: #cbd5e1;
                    min-width: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #94a3b8;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                }
            """)

        # Add the table to the container
        table_container_layout.addWidget(self.inventory_table)

        # Add the table container to the main layout
        # This ensures the table takes up remaining space and scrolls properly
        layout.addWidget(table_container, 1)  # Stretch factor of 1 to take remaining space

        # Apply initial filters
        self.apply_filters()

        # Auto-fit columns on initial load (with a small delay to ensure table is rendered)
        from PySide6.QtCore import QTimer
        self.initial_autofit_timer = QTimer()
        self.initial_autofit_timer.setSingleShot(True)
        self.initial_autofit_timer.timeout.connect(self.auto_fit_columns_on_load)
        self.initial_autofit_timer.start(500)  # 500ms delay

    def on_column_resized(self, logical_index, old_size, new_size):
        """Handle column resize events and save settings"""
        try:
            # Save settings after a short delay to avoid too frequent saves
            if not hasattr(self, '_resize_timer'):
                from PySide6.QtCore import QTimer
                self._resize_timer = QTimer()
                self._resize_timer.setSingleShot(True)
                self._resize_timer.timeout.connect(self.save_column_settings)

            self._resize_timer.start(500)  # Save after 500ms of no resizing
            print(f"📏 Column {logical_index} resized from {old_size}px to {new_size}px")
        except Exception as e:
            print(f"❌ Error handling column resize: {e}")

    def force_refresh_inventory(self):
        """Force refresh inventory data from CSV file"""
        try:
            print("🔄 Force refreshing inventory data...")

            # Reload inventory data from CSV
            import pandas as pd
            inventory_path = 'data/inventory.csv'
            if os.path.exists(inventory_path):
                # Debug: Check file before loading
                file_size = os.path.getsize(inventory_path)
                print(f"🔍 REFRESH DEBUG: File size: {file_size} bytes")

                # Load the data
                loaded_data = pd.read_csv(inventory_path)
                print(f"🔍 REFRESH DEBUG: Loaded {len(loaded_data)} rows from CSV")
                print(f"🔍 REFRESH DEBUG: Columns: {list(loaded_data.columns)}")

                # Update data
                self.data['inventory'] = loaded_data
                self.inventory_df = self.data['inventory'].copy()
                print(f"🔍 REFRESH DEBUG: inventory_df now has {len(self.inventory_df)} items")
                print(f"✅ Reloaded {len(self.inventory_df)} items from CSV")
            else:
                print("❌ inventory.csv not found")
                return

            # Reset filters to show all data
            self.category_combo.setCurrentText("All Categories")
            self.location_combo.setCurrentText("All Locations")
            self.search_box.clear()

            # Refresh filter options
            self.refresh_filter_options()

            # Apply filters to update display
            self.apply_filters()

            print("✅ Inventory data refreshed successfully")
            QMessageBox.information(self, "Success", f"Inventory data refreshed! Showing {len(self.inventory_df)} items.")

        except Exception as e:
            print(f"❌ Error refreshing inventory data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to refresh inventory data: {str(e)}")

    def refresh_filter_options(self):
        """Refresh the filter dropdown options"""
        try:
            # Save current selections
            current_category = self.category_combo.currentText()
            current_location = self.location_combo.currentText()

            # Clear and repopulate category filter
            self.category_combo.clear()
            self.category_combo.addItem("All Categories")
            if 'category' in self.inventory_df.columns:
                categories = self.inventory_df['category'].dropna().unique()
                category_strings = [str(cat) for cat in categories if pd.notna(cat)]
                if category_strings:
                    self.category_combo.addItems(sorted(category_strings))

            # Clear and repopulate location filter
            self.location_combo.clear()
            self.location_combo.addItem("All Locations")
            if 'location' in self.inventory_df.columns:
                locations = self.inventory_df['location'].dropna().unique()
                location_strings = [str(loc) for loc in locations if pd.notna(loc)]
                if location_strings:
                    self.location_combo.addItems(sorted(location_strings))

            # Restore selections if they still exist
            category_index = self.category_combo.findText(current_category)
            if category_index >= 0:
                self.category_combo.setCurrentIndex(category_index)

            location_index = self.location_combo.findText(current_location)
            if location_index >= 0:
                self.location_combo.setCurrentIndex(location_index)

        except Exception as e:
            print(f"Error refreshing filter options: {e}")

    def show_all_items(self):
        """Reset all filters and show all items"""
        try:
            print("🔄 Showing all items...")

            # Reset all filters
            self.category_combo.setCurrentText("All Categories")
            self.location_combo.setCurrentText("All Locations")
            self.search_box.clear()

            # Force apply filters to update display
            self.apply_filters()

            # Show success message
            total_items = len(self.inventory_df)
            print(f"✅ Showing all {total_items} items")
            QMessageBox.information(self, "Show All Items", f"Filters reset! Now showing all {total_items} items.")

        except Exception as e:
            print(f"❌ Error showing all items: {e}")
            QMessageBox.warning(self, "Error", f"Failed to show all items: {str(e)}")

    def auto_fit_columns(self):
        """Automatically resize columns to fit the available screen width"""
        try:
            print("📐 Auto-fitting columns to screen width...")

            # Get available width (table width minus scrollbar and margins)
            table_width = self.inventory_table.width()
            scrollbar_width = 20  # Approximate scrollbar width
            margin_width = 40     # Margins and borders
            available_width = table_width - scrollbar_width - margin_width

            print(f"   📊 Table width: {table_width}px")
            print(f"   📊 Available width: {available_width}px")

            if available_width < 500:  # Minimum reasonable width
                print("   ⚠️ Available width too small, using minimum widths")
                available_width = 1200  # Use a reasonable default

            # Define column priorities and minimum widths
            column_info = {
                0: {"name": "ID", "min_width": 40, "priority": 1},
                1: {"name": "Name", "min_width": 100, "priority": 5},
                2: {"name": "Category", "min_width": 70, "priority": 4},
                3: {"name": "Total Qty", "min_width": 60, "priority": 3},
                4: {"name": "Used Qty", "min_width": 60, "priority": 3},
                5: {"name": "Available Qty", "min_width": 70, "priority": 4},
                6: {"name": "Unit", "min_width": 40, "priority": 2},
                7: {"name": "Avg Price", "min_width": 70, "priority": 3},
                8: {"name": "Price/Unit", "min_width": 75, "priority": 3},
                9: {"name": "Total Value", "min_width": 80, "priority": 4},
                10: {"name": "Location", "min_width": 80, "priority": 4},
                11: {"name": "Purchase Count", "min_width": 70, "priority": 2},
                12: {"name": "Total Spent", "min_width": 80, "priority": 3},
                13: {"name": "Last Purchase Date", "min_width": 100, "priority": 2},
                14: {"name": "Last Purchase Price", "min_width": 100, "priority": 2},
                15: {"name": "Expiry Date", "min_width": 90, "priority": 3},
                16: {"name": "Days Left", "min_width": 70, "priority": 3}
            }

            # Calculate minimum total width needed
            min_total_width = sum(info["min_width"] for info in column_info.values())

            if available_width >= min_total_width:
                # Distribute extra space proportionally based on priority
                extra_space = available_width - min_total_width

                # Calculate total priority weight
                total_priority = sum(info["priority"] for info in column_info.values())

                # Distribute widths
                for col, info in column_info.items():
                    base_width = info["min_width"]
                    extra_width = int((extra_space * info["priority"]) / total_priority)
                    final_width = base_width + extra_width

                    self.inventory_table.setColumnWidth(col, final_width)
                    print(f"   📏 Column {col} ({info['name']}): {final_width}px")
            else:
                # Use minimum widths if screen is too small
                for col, info in column_info.items():
                    self.inventory_table.setColumnWidth(col, info["min_width"])
                    print(f"   📏 Column {col} ({info['name']}): {info['min_width']}px (minimum)")

            # Save the new column settings
            self.save_column_settings()

            print("✅ Columns auto-fitted to screen width!")
            QMessageBox.information(self, "Auto-Fit Complete",
                                  f"Columns have been resized to fit the available screen width ({available_width}px).")

        except Exception as e:
            print(f"❌ Error auto-fitting columns: {e}")
            QMessageBox.warning(self, "Error", f"Failed to auto-fit columns: {str(e)}")

    def edit_selected_inventory_item(self):
        """Edit the selected inventory item from the table"""
        # Check if an item is selected
        selected_items = self.inventory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an item from the inventory table to edit.")
            return

        # Get the selected row
        selected_row = self.inventory_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an item to edit.")
            return

        # Get item name from the table
        item_name = self.inventory_table.item(selected_row, 1).text()  # Name is in column 1

        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Inventory Item: {item_name}")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(500)

        # Main layout
        layout = QVBoxLayout(dialog)

        # Form layout
        form_layout = QFormLayout()

        # Find the item in the inventory dataframe
        item_data = self.inventory_df[self.inventory_df['item_name'] == item_name]
        if len(item_data) == 0:
            QMessageBox.warning(self, "Error", f"Item '{item_name}' not found in inventory.")
            return

        item = item_data.iloc[0]

        # Category
        category_combo = QComboBox()
        category_combo.setEditable(True)
        if 'categories' in self.data and len(self.data['categories']) > 0:
            categories = sorted(self.data['categories']['category_name'].unique())
            category_combo.addItems(categories)
        if 'category' in item and pd.notna(item['category']):
            category_combo.setCurrentText(str(item['category']))
        form_layout.addRow("Category:", category_combo)

        # Quantity Purchased
        qty_purchased_spin = QDoubleSpinBox()
        qty_purchased_spin.setDecimals(2)
        qty_purchased_spin.setMinimum(0.01)
        qty_purchased_spin.setMaximum(10000.0)
        qty_purchased_spin.setSingleStep(0.5)
        if 'qty_purchased' in item and pd.notna(item['qty_purchased']):
            qty_purchased_spin.setValue(float(item['qty_purchased']))
        elif 'quantity' in item and pd.notna(item['quantity']):
            qty_purchased_spin.setValue(float(item['quantity']))
        form_layout.addRow("Quantity Purchased:", qty_purchased_spin)

        # Quantity Used
        qty_used_spin = QDoubleSpinBox()
        qty_used_spin.setDecimals(2)
        qty_used_spin.setMinimum(0.0)
        qty_used_spin.setMaximum(10000.0)
        qty_used_spin.setSingleStep(0.5)
        if 'qty_used' in item and pd.notna(item['qty_used']):
            qty_used_spin.setValue(float(item['qty_used']))
        form_layout.addRow("Quantity Used:", qty_used_spin)

        # Unit
        unit_combo = QComboBox()
        unit_combo.addItems(["kg", "g", "L", "ml", "units", "pcs", "tbsp", "tsp"])
        unit_combo.setEditable(True)
        if 'unit' in item and pd.notna(item['unit']):
            unit_combo.setCurrentText(str(item['unit']))
        form_layout.addRow("Unit:", unit_combo)

        # Price
        price_spin = QDoubleSpinBox()
        price_spin.setMinimum(0.01)
        price_spin.setMaximum(100000.0)
        price_spin.setSingleStep(1.0)
        price_spin.setDecimals(2)
        if 'price' in item and pd.notna(item['price']):
            price_spin.setValue(float(item['price']))
        elif 'avg_price' in item and pd.notna(item['avg_price']):
            price_spin.setValue(float(item['avg_price']))
        form_layout.addRow("Price (₹):", price_spin)

        # Location
        location_combo = QComboBox()
        location_combo.setEditable(True)
        if 'location' in self.inventory_df.columns:
            locations = self.inventory_df['location'].dropna().unique()
            location_strings = [str(loc) for loc in locations if pd.notna(loc) and str(loc).strip()]
            if location_strings:
                location_combo.addItems(sorted(location_strings))
        location_combo.addItems(["Pantry", "Refrigerator", "Freezer", "Storage", "Supermarket", "Vegetable Market"])
        if 'location' in item and pd.notna(item['location']):
            location_combo.setCurrentText(str(item['location']))
        form_layout.addRow("Location:", location_combo)

        # Expiry Date
        expiry_date_edit = QDateEdit()
        expiry_date_edit.setCalendarPopup(True)
        if 'expiry_date' in item and pd.notna(item['expiry_date']):
            try:
                if isinstance(item['expiry_date'], str):
                    # Try to parse the date string
                    try:
                        date_obj = datetime.datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            date_obj = datetime.datetime.strptime(item['expiry_date'], '%d-%m-%Y').date()
                        except ValueError:
                            date_obj = QDate.currentDate().addDays(30).toPython()
                    expiry_date_edit.setDate(QDate(date_obj))
                else:
                    expiry_date_edit.setDate(QDate.currentDate().addDays(30))
            except:
                expiry_date_edit.setDate(QDate.currentDate().addDays(30))
        else:
            expiry_date_edit.setDate(QDate.currentDate().addDays(30))
        form_layout.addRow("Expiry Date:", expiry_date_edit)

        layout.addLayout(form_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)

        # Connect signals
        cancel_btn.clicked.connect(dialog.reject)

        def save_changes():
            try:
                # Validate quantities
                qty_purchased = qty_purchased_spin.value()
                qty_used = qty_used_spin.value()

                if qty_used > qty_purchased:
                    QMessageBox.warning(dialog, "Input Error", "Quantity used cannot be more than quantity purchased.")
                    return

                # Update the inventory dataframe
                item_index = self.inventory_df[self.inventory_df['item_name'] == item_name].index[0]

                self.inventory_df.loc[item_index, 'category'] = category_combo.currentText()
                self.inventory_df.loc[item_index, 'qty_purchased'] = qty_purchased
                self.inventory_df.loc[item_index, 'qty_used'] = qty_used
                self.inventory_df.loc[item_index, 'quantity'] = qty_purchased - qty_used  # Update available quantity
                self.inventory_df.loc[item_index, 'unit'] = unit_combo.currentText()
                self.inventory_df.loc[item_index, 'price'] = price_spin.value()
                self.inventory_df.loc[item_index, 'avg_price'] = price_spin.value()  # Update avg_price too
                self.inventory_df.loc[item_index, 'location'] = location_combo.currentText()
                self.inventory_df.loc[item_index, 'expiry_date'] = expiry_date_edit.date().toString('yyyy-MM-dd')

                # Calculate total value
                total_value = (qty_purchased - qty_used) * price_spin.value()
                self.inventory_df.loc[item_index, 'total_value'] = total_value

                # Update data dictionary
                self.data['inventory'] = self.inventory_df

                # Save to CSV
                self.inventory_df.to_csv('data/inventory.csv', index=False)

                # Refresh the table
                self.apply_filters()

                # Close dialog and show success message
                dialog.accept()
                QMessageBox.information(self, "Success", f"Item '{item_name}' updated successfully!")

            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to update item: {str(e)}")

        save_btn.clicked.connect(save_changes)

        # Show dialog
        dialog.exec_()

    def calculate_average_price_from_purchases(self, item_name):
        """Calculate average price from shopping history purchases"""
        try:
            if 'shopping_list' not in self.data or self.data['shopping_list'].empty:
                return 0

            shopping_df = self.data['shopping_list']

            # Find all purchased items with this name
            purchased_items = shopping_df[
                (shopping_df['item_name'] == item_name) &
                (shopping_df['status'] == 'Purchased') &
                (shopping_df['quantity'].notna())
            ]

            if len(purchased_items) == 0:
                return 0

            # Calculate weighted average price
            total_cost = 0
            total_quantity = 0

            for _, purchase in purchased_items.iterrows():
                # Use current_price if available, otherwise last_price, otherwise avg_price
                cost = 0
                if 'current_price' in purchase and pd.notna(purchase['current_price']):
                    cost = float(purchase['current_price'])
                elif 'last_price' in purchase and pd.notna(purchase['last_price']):
                    cost = float(purchase['last_price'])
                elif 'avg_price' in purchase and pd.notna(purchase['avg_price']):
                    cost = float(purchase['avg_price'])

                if cost > 0:
                    qty = float(purchase['quantity'])
                    total_cost += cost
                    total_quantity += qty

            if total_quantity > 0:
                return total_cost / total_quantity
            else:
                return 0

        except Exception as e:
            print(f"Error calculating average price for {item_name}: {str(e)}")
            return 0

    def get_purchase_count(self, item_name):
        """Get number of times this item was purchased"""
        try:
            if 'shopping_list' not in self.data or self.data['shopping_list'].empty:
                return 0

            shopping_df = self.data['shopping_list']
            purchased_items = shopping_df[
                (shopping_df['item_name'] == item_name) &
                (shopping_df['status'] == 'Purchased')
            ]
            return len(purchased_items)
        except:
            return 0

    def get_total_spent(self, item_name):
        """Get total amount spent on this item"""
        try:
            if 'shopping_list' not in self.data or self.data['shopping_list'].empty:
                return 0

            shopping_df = self.data['shopping_list']
            purchased_items = shopping_df[
                (shopping_df['item_name'] == item_name) &
                (shopping_df['status'] == 'Purchased')
            ]

            # Use current_price if available, otherwise last_price
            if not purchased_items.empty:
                if 'current_price' in purchased_items.columns:
                    total = purchased_items['current_price'].sum()
                elif 'last_price' in purchased_items.columns:
                    total = purchased_items['last_price'].sum()
                else:
                    total = 0
            else:
                total = 0
            return float(total) if pd.notna(total) else 0
        except:
            return 0

    def get_last_purchase_date(self, item_name):
        """Get the date of last purchase"""
        try:
            if 'shopping_list' not in self.data or self.data['shopping_list'].empty:
                return ""

            shopping_df = self.data['shopping_list']
            purchased_items = shopping_df[
                (shopping_df['item_name'] == item_name) &
                (shopping_df['status'] == 'Purchased') &
                (shopping_df['date_purchased'].notna())
            ]

            if len(purchased_items) == 0:
                return ""

            # Get the most recent purchase date
            latest_purchase = purchased_items.loc[purchased_items['date_purchased'].idxmax()]
            return str(latest_purchase['date_purchased'])
        except:
            return ""

    def get_last_purchase_price(self, item_name):
        """Get the price of last purchase"""
        try:
            if 'shopping_list' not in self.data or self.data['shopping_list'].empty:
                return 0

            shopping_df = self.data['shopping_list']
            purchased_items = shopping_df[
                (shopping_df['item_name'] == item_name) &
                (shopping_df['status'] == 'Purchased') &
                (shopping_df['date_purchased'].notna())
            ]

            if len(purchased_items) == 0:
                return 0

            # Get the most recent purchase
            latest_purchase = purchased_items.loc[purchased_items['date_purchased'].idxmax()]

            # Use current_price if available, otherwise last_price, otherwise avg_price
            if 'current_price' in latest_purchase and pd.notna(latest_purchase['current_price']):
                return float(latest_purchase['current_price'])
            elif 'last_price' in latest_purchase and pd.notna(latest_purchase['last_price']):
                return float(latest_purchase['last_price'])
            elif 'avg_price' in latest_purchase and pd.notna(latest_purchase['avg_price']):
                return float(latest_purchase['avg_price'])
            else:
                return 0
        except:
            return 0

    def apply_filters(self):
        # Get filter values
        category = self.category_combo.currentText()
        location = self.location_combo.currentText()
        search_text = self.search_box.text().lower().strip()

        # Apply filters
        filtered_df = self.inventory_df.copy()

        # Enhanced debug info
        print(f"\n🔍 INVENTORY FILTER DEBUG:")
        print(f"   📊 Original inventory_df: {len(self.inventory_df)} items")
        print(f"   🔧 Filters - Category: '{category}', Location: '{location}', Search: '{search_text}'")
        print(f"   📋 Starting with {len(filtered_df)} items")

        # Show sample of data being filtered
        if len(filtered_df) > 0:
            print(f"   📝 Sample items: {list(filtered_df['item_name'].head(5))}")
            print(f"   📂 Available categories: {list(filtered_df['category'].dropna().unique()[:5])}")
            print(f"   📍 Available locations: {list(filtered_df['location'].dropna().unique()[:5])}")

        # Category filter - only filter if not "All Categories"
        if category != "All Categories" and category.strip():
            # Only filter by exact category match, don't include missing categories
            filtered_df = filtered_df[filtered_df['category'] == category]
            print(f"   ✂️ After category filter '{category}': {len(filtered_df)} items")

        # Location filter - only filter if not "All Locations"
        if location != "All Locations" and location.strip():
            # Only filter by exact location match, don't include missing locations
            filtered_df = filtered_df[filtered_df['location'] == location]
            print(f"   ✂️ After location filter '{location}': {len(filtered_df)} items")

        # Search filter - handle missing data gracefully
        if search_text:
            # Create boolean masks for each column, handling NaN values
            name_match = filtered_df['item_name'].fillna('').str.lower().str.contains(search_text, na=False)
            category_match = filtered_df['category'].fillna('').str.lower().str.contains(search_text, na=False)
            location_match = filtered_df['location'].fillna('').str.lower().str.contains(search_text, na=False)

            # Combine all matches
            filtered_df = filtered_df[name_match | category_match | location_match]
            print(f"   ✂️ After search filter '{search_text}': {len(filtered_df)} items")

        print(f"   ✅ FINAL RESULT: {len(filtered_df)} items will be displayed")

        # Show which items will be displayed
        if len(filtered_df) > 0:
            print(f"   📋 Items to display: {list(filtered_df['item_name'].head(10))}")
        else:
            print(f"   ⚠️ NO ITEMS TO DISPLAY!")

        # Update the table
        self.update_inventory_table(filtered_df)
    
    def update_inventory_table(self, df):
        # Enhanced debug info
        print(f"\n📊 UPDATE_INVENTORY_TABLE DEBUG:")
        print(f"   📥 Received DataFrame: {len(df)} rows × {len(df.columns)} columns")
        print(f"   📋 DataFrame columns: {list(df.columns)}")

        # Clear the table
        self.inventory_table.setRowCount(0)

        # Calculate additional fields
        today = datetime.datetime.now().date()

        # Make sure total_value is calculated
        if 'price' in df.columns and 'quantity' in df.columns:
            if 'total_value' not in df.columns:
                df['total_value'] = df['quantity'] * df['price']

        # Add rows
        print(f"   🔧 Setting table row count to: {len(df)}")
        self.inventory_table.setRowCount(len(df))

        print(f"   🔄 Processing {len(df)} rows...")
        for i, (_, row) in enumerate(df.iterrows()):
            # Item ID - column 0
            if 'item_id' in row:
                self.inventory_table.setItem(i, 0, QTableWidgetItem(str(row['item_id'])))
            else:
                self.inventory_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            
            # Name - column 1
            if 'item_name' in row and pd.notna(row['item_name']):
                self.inventory_table.setItem(i, 1, QTableWidgetItem(str(row['item_name'])))
            else:
                self.inventory_table.setItem(i, 1, QTableWidgetItem(""))

            # Category - column 2
            if 'category' in row and pd.notna(row['category']):
                self.inventory_table.setItem(i, 2, QTableWidgetItem(str(row['category'])))
            else:
                self.inventory_table.setItem(i, 2, QTableWidgetItem(""))
            
            # Quantity Purchased - column 3
            qty_purchased = row.get('qty_purchased', row['quantity'])
            self.inventory_table.setItem(i, 3, QTableWidgetItem(str(qty_purchased)))
            
            # Quantity Used - column 4
            qty_used = row.get('qty_used', 0)
            self.inventory_table.setItem(i, 4, QTableWidgetItem(str(qty_used)))
            
            # Quantity Left - column 5
            qty_left = float(qty_purchased) - float(qty_used)
            qty_left_item = QTableWidgetItem(str(qty_left))
            
            # Check if stock is running low
            threshold = row.get('reorder_level', 1.0)  # Default threshold is 1.0
            if qty_left <= threshold:
                qty_left_item.setBackground(QColor(255, 200, 200))  # Light red for low stock
            self.inventory_table.setItem(i, 5, qty_left_item)
            
            # Unit - column 6
            if 'unit' in row and pd.notna(row['unit']):
                self.inventory_table.setItem(i, 6, QTableWidgetItem(str(row['unit'])))
            else:
                self.inventory_table.setItem(i, 6, QTableWidgetItem(""))
            
            # Get currency symbol from settings, default to Indian Rupee (₹)
            currency_symbol = "₹"
            if 'settings' in self.data and 'currency' in self.data['settings']:
                currency_symbol = self.data['settings']['currency']
                
            # Average Price - column 7
            if 'avg_price' in row and pd.notna(row['avg_price']):
                self.inventory_table.setItem(i, 7, QTableWidgetItem(f"{currency_symbol}{float(row['avg_price']):.2f}"))
            elif 'price' in row and pd.notna(row['price']):
                # If avg_price not available, use regular price
                price = float(row['price'])
                self.inventory_table.setItem(i, 7, QTableWidgetItem(f"{currency_symbol}{price:.2f}"))
            else:
                self.inventory_table.setItem(i, 7, QTableWidgetItem(f"{currency_symbol}0.00"))
            
            # Price per gram/ml/unit - column 8
            # Get price, preferring avg_price if available
            if 'avg_price' in row and pd.notna(row['avg_price']) and float(row['avg_price']) > 0:
                price = float(row['avg_price'])
            elif 'price' in row and pd.notna(row['price']) and float(row['price']) > 0:
                price = float(row['price'])
            else:
                price = 0
            
            # Use quantity left for price per unit calculation
            qty = float(qty_left) if qty_left > 0 else 0  # Use quantity left (calculated above)
            
            # Get unit information
            unit = ""
            if 'unit' in row and pd.notna(row['unit']):
                unit = row['unit'].lower()
            
            # Calculate price per unit based on unit type
            if price > 0 and qty > 0:
                if unit == 'kg':
                    # 1 kg = 1000 g
                    qty_in_grams = qty * 1000
                    price_per_g = price / qty_in_grams
                    self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price_per_g:.4f}/g"))
                elif unit == 'g':
                    # Already in grams
                    price_per_g = price / qty
                    self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price_per_g:.4f}/g"))
                elif unit in ['l', 'litre', 'liter']:
                    # 1 L = 1000 ml
                    qty_in_ml = qty * 1000
                    price_per_ml = price / qty_in_ml
                    self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price_per_ml:.4f}/ml"))
                elif unit == 'ml':
                    # Already in ml
                    price_per_ml = price / qty
                    self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price_per_ml:.4f}/ml"))
                elif unit:
                    # For other units, calculate generic price per unit
                    price_per_unit = price / qty
                    self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price_per_unit:.4f}/{unit}"))
                else:
                    # No unit specified but we have price and quantity
                    price_per_unit = price / qty
                    self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price_per_unit:.4f}/unit"))
            elif price > 0:
                # We have price but no quantity
                self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}{price:.2f} (no qty)"))
            elif qty > 0:
                # We have quantity but no price
                self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}0.00"))
            else:
                # No price and no quantity
                self.inventory_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol}0.00"))
                
            # Total value - column 9 (calculated for all items)
            # Calculate total value based on available quantity and average price
            qty = float(qty_left)  # Use available quantity (calculated above)

            # Calculate proper average price from purchase history
            avg_price = self.calculate_average_price_from_purchases(row.get('item_name', ''))

            # If no purchase history, use stored avg_price or price
            if avg_price == 0:
                if 'avg_price' in row and pd.notna(row['avg_price']):
                    avg_price = float(row['avg_price'])
                elif 'price' in row and pd.notna(row['price']):
                    avg_price = float(row['price'])
                else:
                    avg_price = 0

            # Calculate price per unit correctly
            # avg_price should be the total cost, so price_per_unit = avg_price / qty_purchased
            price_per_unit = 0
            if 'qty_purchased' in row and pd.notna(row['qty_purchased']) and float(row['qty_purchased']) > 0:
                # avg_price is total cost, so divide by total quantity purchased
                price_per_unit = avg_price / float(row['qty_purchased'])
            elif 'price_per_unit' in row and pd.notna(row['price_per_unit']):
                # Use stored price_per_unit if available
                price_per_unit = float(row['price_per_unit'])
            elif qty > 0 and avg_price > 0:
                # Fallback calculation
                price_per_unit = avg_price / qty

            # Calculate total value based on available quantity
            total_value = qty * price_per_unit
            self.inventory_table.setItem(i, 9, QTableWidgetItem(f"{currency_symbol}{total_value:.2f}"))
            
            # Location - column 10 (consolidated location/store)
            location_value = ""
            if 'location' in row and pd.notna(row['location']) and str(row['location']).strip():
                location_value = str(row['location']).strip()
            elif 'store' in row and pd.notna(row['store']) and str(row['store']).strip():
                # Fallback to store value if location is empty (for data migration)
                location_value = str(row['store']).strip()

            self.inventory_table.setItem(i, 10, QTableWidgetItem(location_value))

            # Purchase tracking columns
            # Purchase Count - column 11
            purchase_count = self.get_purchase_count(row.get('item_name', ''))
            self.inventory_table.setItem(i, 11, QTableWidgetItem(str(purchase_count)))

            # Total Spent - column 12
            total_spent = self.get_total_spent(row.get('item_name', ''))
            self.inventory_table.setItem(i, 12, QTableWidgetItem(f"{currency_symbol}{total_spent:.2f}"))

            # Last Purchase Date - column 13
            last_purchase_date = self.get_last_purchase_date(row.get('item_name', ''))
            self.inventory_table.setItem(i, 13, QTableWidgetItem(last_purchase_date))

            # Last Purchase Price - column 14
            last_purchase_price = self.get_last_purchase_price(row.get('item_name', ''))
            self.inventory_table.setItem(i, 14, QTableWidgetItem(f"{currency_symbol}{last_purchase_price:.2f}"))

            # Expiry Date - column 15 (shifted due to new columns)
            expiry_date_str = ""
            days_left_str = "N/A"
            expiry_item = None
            days_left_item = None

            if 'expiry_date' in row and pd.notna(row['expiry_date']) and str(row['expiry_date']).strip():
                expiry_date_raw = str(row['expiry_date']).strip()

                # Try to parse the expiry date with prioritized DD/MM/YYYY format
                expiry_date = None
                parsed_format = ""

                # List of date formats to try (in order of preference)
                # User prefers DD/MM/YYYY format (day/month/year)
                date_formats = [
                    ('%d/%m/%Y', 'DD/MM/YYYY'),      # 9/7/2025 (day/month/year) - USER PREFERENCE
                    ('%d-%m-%Y', 'DD-MM-YYYY'),      # 9-7-2025 (day-month-year)
                    ('%d.%m.%Y', 'DD.MM.YYYY'),      # 9.7.2025 (day.month.year)
                    ('%Y-%m-%d', 'YYYY-MM-DD'),      # 2025-07-09 (stored format)
                    ('%Y/%m/%d', 'YYYY/MM/DD'),      # 2025/7/9
                    ('%m/%d/%Y', 'MM/DD/YYYY'),      # 7/9/2025 (US format) - LAST RESORT
                ]

                for date_format, format_name in date_formats:
                    try:
                        expiry_date = datetime.datetime.strptime(expiry_date_raw, date_format).date()
                        parsed_format = format_name
                        break
                    except ValueError:
                        continue

                if not expiry_date:
                    # If all parsing fails, show the raw string
                    expiry_date_str = f"{expiry_date_raw} (Unknown Format)"
                    days_left_str = "Invalid Date"

                if expiry_date:
                    # Format for display as DD-MM-YYYY with format info
                    expiry_date_str = f"{expiry_date.strftime('%d-%m-%Y')}"

                    # Calculate days left
                    today = datetime.datetime.now().date()
                    days_left = (expiry_date - today).days

                    # Create table items
                    expiry_item = QTableWidgetItem(expiry_date_str)
                    days_left_item = QTableWidgetItem(str(days_left))

                    # Add tooltip with more information
                    expiry_item.setToolTip(f"Parsed as {parsed_format}: {expiry_date.strftime('%A, %B %d, %Y')}")

                    # Highlight and format based on days left
                    if days_left < 0:
                        # Expired - Red background
                        expiry_item.setBackground(QColor(255, 100, 100))
                        days_left_item.setBackground(QColor(255, 100, 100))
                        days_left_item.setText(f"{abs(days_left)} days ago (EXPIRED)")
                        days_left_item.setToolTip(f"Expired {abs(days_left)} days ago on {expiry_date.strftime('%d-%m-%Y')}")
                    elif days_left == 0:
                        # Expires today - Red background
                        expiry_item.setBackground(QColor(255, 150, 150))
                        days_left_item.setBackground(QColor(255, 150, 150))
                        days_left_item.setText("TODAY (URGENT)")
                        days_left_item.setToolTip("Expires today!")
                    elif days_left == 1:
                        # Expires tomorrow - Orange background
                        expiry_item.setBackground(QColor(255, 200, 100))
                        days_left_item.setBackground(QColor(255, 200, 100))
                        days_left_item.setText("1 day (TOMORROW)")
                        days_left_item.setToolTip("Expires tomorrow!")
                    elif days_left <= 3:
                        # Very close to expiry - Orange background
                        expiry_item.setBackground(QColor(255, 200, 100))
                        days_left_item.setBackground(QColor(255, 200, 100))
                        days_left_item.setText(f"{days_left} days (URGENT)")
                        days_left_item.setToolTip(f"Expires in {days_left} days on {expiry_date.strftime('%d-%m-%Y')}")
                    elif days_left <= 7:
                        # Close to expiry - Yellow background
                        expiry_item.setBackground(QColor(255, 255, 150))
                        days_left_item.setBackground(QColor(255, 255, 150))
                        days_left_item.setText(f"{days_left} days (SOON)")
                        days_left_item.setToolTip(f"Expires in {days_left} days on {expiry_date.strftime('%d-%m-%Y')}")
                    elif days_left <= 30:
                        # Within a month - Light green background
                        expiry_item.setBackground(QColor(200, 255, 200))
                        days_left_item.setBackground(QColor(200, 255, 200))
                        days_left_item.setText(f"{days_left} days")
                        days_left_item.setToolTip(f"Expires in {days_left} days on {expiry_date.strftime('%d-%m-%Y')}")
                    else:
                        # Good - Normal display
                        days_left_item.setText(f"{days_left} days")
                        days_left_item.setToolTip(f"Expires in {days_left} days on {expiry_date.strftime('%d-%m-%Y')}")

            # Set the table items
            if expiry_item:
                self.inventory_table.setItem(i, 15, expiry_item)
            else:
                self.inventory_table.setItem(i, 15, QTableWidgetItem(expiry_date_str))

            if days_left_item:
                self.inventory_table.setItem(i, 16, days_left_item)
            else:
                self.inventory_table.setItem(i, 16, QTableWidgetItem(days_left_str))

        # Final completion message
        print(f"   ✅ TABLE UPDATE COMPLETED: {len(df)} rows processed and displayed")
        print(f"   📊 Table now shows {self.inventory_table.rowCount()} rows")
    
    def setup_add_edit_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_edit_tab)
        
        # Add subheader
        header = QLabel("Add/Edit Inventory Items")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Edit item form
        edit_form_group = QGroupBox("Edit Existing Item")
        edit_form_layout = QFormLayout(edit_form_group)
        layout.addWidget(edit_form_group)
        
        # Item selection from Items tab
        self.edit_item_combo = QComboBox()
        self.edit_item_combo.addItem("Select an item...")
        
        # First try to get items from the Items tab
        if 'items' in self.data and len(self.data['items']) > 0:
            # Filter out NaN values and convert to strings before sorting
            items = self.data['items']['item_name'].dropna().unique()
            item_strings = [str(item) for item in items if pd.notna(item)]
            if item_strings:
                self.edit_item_combo.addItems(sorted(item_strings))
        # Fall back to inventory items if no items in Items tab
        elif len(self.inventory_df) > 0:
            # Filter out NaN values and convert to strings before sorting
            items = self.inventory_df['item_name'].dropna().unique()
            item_strings = [str(item) for item in items if pd.notna(item)]
            if item_strings:
                self.edit_item_combo.addItems(sorted(item_strings))
        
        self.edit_item_combo.currentIndexChanged.connect(self.load_item_for_edit)
        edit_form_layout.addRow("Select Item:", self.edit_item_combo)
        
        # Category
        self.edit_category_combo = QComboBox()
        self.edit_category_combo.setEditable(True)
        self.edit_category_combo.setPlaceholderText("Enter or select a category...")
        # Populate with categories from Categories tab if available
        if 'categories' in self.data and self.data['categories'] is not None and len(self.data['categories']) > 0:
            categories = sorted(self.data['categories']['category_name'].unique())
            self.edit_category_combo.addItems(categories)
        self.edit_category_combo.setEnabled(False)
        edit_form_layout.addRow("Category:", self.edit_category_combo)
        
        # Quantity Purchased
        self.edit_quantity_purchased_spin = QDoubleSpinBox()
        self.edit_quantity_purchased_spin.setDecimals(2)
        self.edit_quantity_purchased_spin.setMinimum(0.01)
        self.edit_quantity_purchased_spin.setMaximum(1000.0)
        self.edit_quantity_purchased_spin.setSingleStep(0.5)
        self.edit_quantity_purchased_spin.setEnabled(False)
        edit_form_layout.addRow("Quantity Purchased:", self.edit_quantity_purchased_spin)
        
        # Quantity Used
        self.edit_quantity_used_spin = QDoubleSpinBox()
        self.edit_quantity_used_spin.setDecimals(2)
        self.edit_quantity_used_spin.setMinimum(0.0)
        self.edit_quantity_used_spin.setMaximum(1000.0)
        self.edit_quantity_used_spin.setSingleStep(0.5)
        self.edit_quantity_used_spin.setEnabled(False)
        edit_form_layout.addRow("Quantity Used:", self.edit_quantity_used_spin)
        
        # Reorder Level
        self.edit_reorder_level_spin = QDoubleSpinBox()
        self.edit_reorder_level_spin.setDecimals(2)
        self.edit_reorder_level_spin.setMinimum(0.1)
        self.edit_reorder_level_spin.setMaximum(100.0)
        self.edit_reorder_level_spin.setSingleStep(0.5)
        self.edit_reorder_level_spin.setEnabled(False)
        edit_form_layout.addRow("Reorder Level:", self.edit_reorder_level_spin)
        
        # Price per unit
        self.edit_price_spin = QDoubleSpinBox()
        self.edit_price_spin.setMinimum(0.01)
        self.edit_price_spin.setMaximum(10000.0)
        self.edit_price_spin.setSingleStep(0.1)
        self.edit_price_spin.setEnabled(False)
        
        # Get currency symbol from settings, default to Indian Rupee (₹)
        currency_symbol = "₹"
        if 'settings' in self.data and 'currency' in self.data['settings']:
            currency_symbol = self.data['settings']['currency']
            
        edit_form_layout.addRow(f"Price per Unit ({currency_symbol}):", self.edit_price_spin)
        
        # Location
        self.edit_location_combo = QComboBox()
        if 'location' in self.inventory_df.columns:
            # Filter out NaN values and convert to strings before sorting
            locations = self.inventory_df['location'].dropna().unique()
            location_strings = [str(loc) for loc in locations if pd.notna(loc)]
            if location_strings:
                self.edit_location_combo.addItems(sorted(location_strings))
        self.edit_location_combo.setEditable(True)
        self.edit_location_combo.setEnabled(False)
        edit_form_layout.addRow("Location:", self.edit_location_combo)
        
        # Update button
        self.update_button = QPushButton("Update Item")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.update_inventory_item)
        edit_form_layout.addRow("", self.update_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete Item")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_inventory_item)
        edit_form_layout.addRow("", self.delete_button)
        
        # Add item form
        add_form_group = QGroupBox("Add New Item")
        add_form_layout = QFormLayout(add_form_group)
        layout.addWidget(add_form_group)
        
        # Item name
        self.add_name_input = QLineEdit()
        add_form_layout.addRow("Item Name:", self.add_name_input)
        
        # Category - populate from Categories tab if available
        self.add_category_combo = QComboBox()
        self.add_category_combo.setEditable(True)
        self.add_category_combo.setPlaceholderText("Enter or select a category...")
        # Populate with categories from Categories tab if available
        if 'categories' in self.data and self.data['categories'] is not None and len(self.data['categories']) > 0:
            categories = sorted(self.data['categories']['category_name'].unique())
            self.add_category_combo.addItems(categories)
        add_form_layout.addRow("Category:", self.add_category_combo)
        
        # Quantity Purchased
        self.add_quantity_purchased_spin = QDoubleSpinBox()
        self.add_quantity_purchased_spin.setDecimals(2)
        self.add_quantity_purchased_spin.setMinimum(0.01)
        self.add_quantity_purchased_spin.setMaximum(1000.0)
        self.add_quantity_purchased_spin.setSingleStep(0.5)
        self.add_quantity_purchased_spin.setValue(1.0)
        add_form_layout.addRow("Quantity Purchased:", self.add_quantity_purchased_spin)
        
        # Quantity Used
        self.add_quantity_used_spin = QDoubleSpinBox()
        self.add_quantity_used_spin.setDecimals(2)
        self.add_quantity_used_spin.setMinimum(0.0)
        self.add_quantity_used_spin.setMaximum(1000.0)
        self.add_quantity_used_spin.setSingleStep(0.5)
        self.add_quantity_used_spin.setValue(0.0)
        add_form_layout.addRow("Quantity Used:", self.add_quantity_used_spin)
        
        # Reorder Level
        self.add_reorder_level_spin = QDoubleSpinBox()
        self.add_reorder_level_spin.setDecimals(2)
        self.add_reorder_level_spin.setMinimum(0.1)
        self.add_reorder_level_spin.setMaximum(100.0)
        self.add_reorder_level_spin.setSingleStep(0.5)
        self.add_reorder_level_spin.setValue(1.0)
        add_form_layout.addRow("Reorder Level:", self.add_reorder_level_spin)
        
        # Unit
        self.add_unit_combo = QComboBox()
        self.add_unit_combo.addItems(["kg", "g", "L", "ml", "units", "pcs"])
        self.add_unit_combo.setEditable(True)
        add_form_layout.addRow("Unit:", self.add_unit_combo)
        
        # Price per unit
        self.add_price_spin = QDoubleSpinBox()
        self.add_price_spin.setMinimum(0.01)
        self.add_price_spin.setMaximum(10000.0)
        self.add_price_spin.setSingleStep(0.1)
        self.add_price_spin.setValue(1.0)
        add_form_layout.addRow("Price per Unit (₹):", self.add_price_spin)
        
        # Location
        self.add_location_combo = QComboBox()
        if 'location' in self.inventory_df.columns:
            # Filter out NaN values and convert to strings before sorting
            locations = self.inventory_df['location'].dropna().unique()
            location_strings = [str(loc) for loc in locations if pd.notna(loc)]
            if location_strings:
                self.add_location_combo.addItems(sorted(location_strings))
            else:
                self.add_location_combo.addItems(["Pantry", "Refrigerator", "Freezer", "Storage"])
        else:
            self.add_location_combo.addItems(["Pantry", "Refrigerator", "Freezer", "Storage"])
        self.add_location_combo.setEditable(True)
        add_form_layout.addRow("Location:", self.add_location_combo)
        
        # Expiry date
        self.add_expiry_date = QDateEdit()
        self.add_expiry_date.setCalendarPopup(True)
        self.add_expiry_date.setDate(QDate.currentDate().addDays(30))  # Default to 30 days from now
        add_form_layout.addRow("Expiry Date:", self.add_expiry_date)
        
        # Add button
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self.add_inventory_item)
        add_form_layout.addRow("", self.add_item_button)
    
    def load_item_for_edit(self):
        # Get selected item
        item_name = self.edit_item_combo.currentText()
        
        # If "Select an item..." is selected, disable edit controls
        if item_name == "Select an item...":
            self.edit_category_combo.setEnabled(False)
            self.edit_quantity_purchased_spin.setEnabled(False)
            self.edit_quantity_used_spin.setEnabled(False)
            self.edit_reorder_level_spin.setEnabled(False)
            self.edit_unit_combo.setEnabled(False)
            self.edit_price_spin.setEnabled(False)
            self.edit_location_combo.setEnabled(False)
            self.edit_expiry_date.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
            
        # Enable form elements
        self.edit_category_combo.setEnabled(True)
        self.edit_quantity_purchased_spin.setEnabled(True)
        self.edit_quantity_used_spin.setEnabled(True)
        self.edit_reorder_level_spin.setEnabled(True)
        self.edit_unit_combo.setEnabled(True)
        self.edit_price_spin.setEnabled(True)
        self.edit_location_combo.setEnabled(True)
        self.edit_expiry_date.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Find the item in the inventory
        item_data = self.inventory_df[self.inventory_df['item_name'] == item_name]
        if len(item_data) > 0:
            # Get the first (and should be only) row
            item = item_data.iloc[0]
            
            # Populate form fields with current values
            # Set category if it exists
            if 'category' in item and pd.notna(item['category']):
                index = self.edit_category_combo.findText(item['category'])
                if index >= 0:
                    self.edit_category_combo.setCurrentIndex(index)
            
            # Set quantity purchased
            if 'qty_purchased' in item and pd.notna(item['qty_purchased']):
                self.edit_quantity_purchased_spin.setValue(float(item['qty_purchased']))
            elif 'quantity' in item and pd.notna(item['quantity']):
                # Fall back to regular quantity if qty_purchased doesn't exist
                self.edit_quantity_purchased_spin.setValue(float(item['quantity']))
            
            # Set quantity used
            if 'qty_used' in item and pd.notna(item['qty_used']):
                self.edit_quantity_used_spin.setValue(float(item['qty_used']))
            else:
                self.edit_quantity_used_spin.setValue(0.0)
            
            # Set reorder level
            if 'reorder_level' in item and pd.notna(item['reorder_level']):
                self.edit_reorder_level_spin.setValue(float(item['reorder_level']))
            
            # Set unit
            if 'unit' in item and pd.notna(item['unit']):
                index = self.edit_unit_combo.findText(item['unit'])
                if index >= 0:
                    self.edit_unit_combo.setCurrentIndex(index)
            
            # Set price
            if 'price' in item and pd.notna(item['price']):
                self.edit_price_spin.setValue(float(item['price']))
            elif 'avg_price' in item and pd.notna(item['avg_price']):
                self.edit_price_spin.setValue(float(item['avg_price']))
            
            # Set location
            if 'location' in item and pd.notna(item['location']):
                index = self.edit_location_combo.findText(item['location'])
                if index >= 0:
                    self.edit_location_combo.setCurrentIndex(index)
            
            # Set expiry date
            if 'expiry_date' in item and pd.notna(item['expiry_date']):
                try:
                    date_parts = str(item['expiry_date']).split('-')
                    if len(date_parts) == 3:
                        year, month, day = map(int, date_parts)
                        self.edit_expiry_date.setDate(QDate(year, month, day))
                except:
                    # If there's any error parsing the date, use today
                    self.edit_expiry_date.setDate(QDate.currentDate())
    
    def delete_inventory_item(self):
        # Get selected item
        item_name = self.edit_item_combo.currentText()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete {item_name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove the item from the dataframe
            self.inventory_df = self.inventory_df[self.inventory_df['item_name'] != item_name]
            
            # Update the data dictionary
            self.data['inventory'] = self.inventory_df
            
            # Save to CSV
            self.inventory_df.to_csv('data/inventory.csv', index=False)
            
            # Show success message
            QMessageBox.information(self, "Success", f"{item_name} deleted successfully!")
            
            # Refresh the inventory table
            self.apply_filters()
            
            # Update the item combo box
            self.edit_item_combo.clear()
            self.edit_item_combo.addItem("Select an item...")
            # Filter out NaN values and convert to strings before sorting
            items = self.inventory_df['item_name'].dropna().unique()
            item_strings = [str(item) for item in items if pd.notna(item)]
            if item_strings:
                self.edit_item_combo.addItems(sorted(item_strings))
    
    def load_item_for_edit(self):
        # Get selected item
        item_name = self.edit_item_combo.currentText()
        
        # If "Select an item..." is selected, disable edit controls
        if item_name == "Select an item...":
            self.edit_category_combo.setEnabled(False)
            self.edit_quantity_purchased_spin.setEnabled(False)
            self.edit_quantity_used_spin.setEnabled(False)
            self.edit_reorder_level_spin.setEnabled(False)
            self.edit_unit_combo.setEnabled(False)
            self.edit_price_spin.setEnabled(False)
            self.edit_location_combo.setEnabled(False)
            self.edit_expiry_date.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
            
        # Enable form elements
        self.edit_category_combo.setEnabled(True)
        self.edit_quantity_purchased_spin.setEnabled(True)
        self.edit_quantity_used_spin.setEnabled(True)
        self.edit_reorder_level_spin.setEnabled(True)
        self.edit_unit_combo.setEnabled(True)
        self.edit_price_spin.setEnabled(True)
        self.edit_location_combo.setEnabled(True)
        self.edit_expiry_date.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Find the item in the inventory
        item_data = self.inventory_df[self.inventory_df['item_name'] == item_name]
        if len(item_data) > 0:
            # Get the first (and should be only) row
            item = item_data.iloc[0]
            
            # Populate form fields with current values
            # Set category if it exists
            if 'category' in item and pd.notna(item['category']):
                index = self.edit_category_combo.findText(item['category'])
                if index >= 0:
                    self.edit_category_combo.setCurrentIndex(index)
            
            # Set quantity purchased
            if 'qty_purchased' in item and pd.notna(item['qty_purchased']):
                self.edit_quantity_purchased_spin.setValue(float(item['qty_purchased']))
            elif 'quantity' in item and pd.notna(item['quantity']):
                # Fall back to regular quantity if qty_purchased doesn't exist
                self.edit_quantity_purchased_spin.setValue(float(item['quantity']))
            
            # Set quantity used
            if 'qty_used' in item and pd.notna(item['qty_used']):
                self.edit_quantity_used_spin.setValue(float(item['qty_used']))
            else:
                self.edit_quantity_used_spin.setValue(0.0)
            
            # Set reorder level
            if 'reorder_level' in item and pd.notna(item['reorder_level']):
                self.edit_reorder_level_spin.setValue(float(item['reorder_level']))
            
            # Set unit
            if 'unit' in item and pd.notna(item['unit']):
                index = self.edit_unit_combo.findText(item['unit'])
                if index >= 0:
                    self.edit_unit_combo.setCurrentIndex(index)
            
            # Set price
            if 'price' in item and pd.notna(item['price']):
                self.edit_price_spin.setValue(float(item['price']))
            elif 'avg_price' in item and pd.notna(item['avg_price']):
                self.edit_price_spin.setValue(float(item['avg_price']))
            
            # Set location
            if 'location' in item and pd.notna(item['location']):
                index = self.edit_location_combo.findText(item['location'])
                if index >= 0:
                    self.edit_location_combo.setCurrentIndex(index)
            
            # Set expiry date
            if 'expiry_date' in item and pd.notna(item['expiry_date']):
                try:
                    date_parts = str(item['expiry_date']).split('-')
                    if len(date_parts) == 3:
                        year, month, day = map(int, date_parts)
                        self.edit_expiry_date.setDate(QDate(year, month, day))
                except:
                    # If there's any error parsing the date, use today
                    self.edit_expiry_date.setDate(QDate.currentDate())
    
    def add_inventory_item(self):
        # Get values from form
        item_name = self.add_name_input.text().strip()
        category = self.add_category_combo.currentText()
        qty_purchased = self.add_quantity_purchased_spin.value()
        qty_used = self.add_quantity_used_spin.value()
        reorder_level = self.add_reorder_level_spin.value()
        unit = self.add_unit_combo.currentText()
        price = self.add_price_spin.value()
        location = self.add_location_combo.currentText()
        
        # Get expiry date
        expiry_date = self.add_expiry_date.date().toString('yyyy-MM-dd')
        
        # Validate inputs
        if not item_name:
            QMessageBox.warning(self, "Input Error", "Please enter an item name.")
            return
            
        # Validate that quantity used isn't more than purchased
        if qty_used > qty_purchased:
            QMessageBox.warning(self, "Input Error", "Quantity used cannot be more than quantity purchased.")
            return
            
        # Create new item dictionary
        new_item = {
            'item_id': len(self.inventory_df) + 1,
            'item_name': item_name,
            'category': category,
            'quantity': qty_purchased - qty_used,  # For backward compatibility
            'qty_purchased': qty_purchased,
            'qty_used': qty_used,
            'reorder_level': reorder_level,
            'unit': unit,
            'price': price,
            'avg_price': price,  # Initialize avg_price with current price
            'location': location,
            'expiry_date': expiry_date
        }
        
        # Check if this item exists in the items list
        item_exists = False
        if 'items' in self.data and len(self.data['items']) > 0:
            item_exists = item_name in self.data['items']['item_name'].values
        
        # If item doesn't exist in master list, prompt user to add it first
        if not item_exists:
            response = QMessageBox.question(
                self, 
                "Item Not Found", 
                f"'{item_name}' is not in your items database. Would you like to add it first?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                # Switch to items tab and pre-fill the name
                self.tabs.setCurrentIndex(1)  # Index 1 is the Items tab
                self.item_name_input.setCurrentText(item_name)
                return
            else:
                return
        
        # Check if item already exists in inventory
        if item_name in self.inventory_df['item_name'].values:
            # For existing items, we'll calculate a new average price
            existing_items = self.inventory_df[self.inventory_df['item_name'] == item_name]
            
            # Calculate new average price
            total_qty = existing_items['quantity'].sum() + quantity
            
            # Use the correct price field name
            price_field = 'price' if 'price' in existing_items.columns else 'price_per_unit'
            total_value = (existing_items[price_field] * existing_items['quantity']).sum() + (price * quantity)
            avg_price = total_value / total_qty if total_qty > 0 else price
            
            # Confirm with user about adding quantity
            response = QMessageBox.question(
                self,
                "Item Exists",
                f"'{item_name}' already exists in inventory. Would you like to add to its quantity?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.No:
                return
        else:
            # For new items, the average price is the same as the current price
            avg_price = price
        
        # Generate new item ID
        if 'item_id' in self.inventory_df.columns and len(self.inventory_df) > 0:
            new_item_id = self.inventory_df['item_id'].max() + 1
        else:
            new_item_id = 1
        
        # Calculate total value
        total_value = quantity * price
        
        # Calculate price per gram if unit is weight-based
        price_per_g = None
        if unit.lower() in ['g', 'kg']:
            qty_in_grams = quantity
            if unit.lower() == 'kg':
                qty_in_grams *= 1000
            
            if qty_in_grams > 0:
                price_per_g = price / qty_in_grams
        
        # Create new item record
        new_item = pd.DataFrame({
            'item_id': [new_item_id],
            'item_name': [item_name],
            'category': [category],
            'quantity': [quantity],
            'unit': [unit],
            'price': [price],
            'avg_price': [avg_price],
            'price_per_g': [price_per_g] if price_per_g is not None else [None],
            'total_value': [total_value],
            'location': [location],
            'expiry_date': [expiry_date]
        })
        
        # Add to inventory dataframe
        self.inventory_df = pd.concat([self.inventory_df, new_item], ignore_index=True)
        
        # Update the data dictionary
        self.data['inventory'] = self.inventory_df
        
        # Save to CSV
        self.inventory_df.to_csv('data/inventory.csv', index=False)
        
        # Show success message
        QMessageBox.information(self, "Success", f"{item_name} added to inventory!")
        
        # Clear form
        self.add_name_input.clear()
        self.add_quantity_spin.setValue(1.0)
        self.add_price_spin.setValue(1.0)
        self.add_expiry_date.setDate(QDate.currentDate().addDays(30))
        
        # Refresh the inventory table
        self.apply_filters()
        
        # Update the item combo box
        self.edit_item_combo.clear()
        self.edit_item_combo.addItem("Select an item...")
        # Filter out NaN values and convert to strings before sorting
        items = self.inventory_df['item_name'].dropna().unique()
        item_strings = [str(item) for item in items if pd.notna(item)]
        if item_strings:
            self.edit_item_combo.addItems(sorted(item_strings))
        
        # Also update the expiry tracking tab
        self.update_expiry_table()
    
    def setup_expiry_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.expiry_tab)
        layout.setContentsMargins(10, 5, 10, 10)  # Reduce margins to save space
        
        # Add compact subheader
        header = QLabel("Expiry Tracking")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setMaximumHeight(25)  # Limit header height
        layout.addWidget(header)
        
        # Check if there's data in the items tab
        if 'items' not in self.data or len(self.data['items']) == 0:
            # Show message when no items exist
            no_items_label = QLabel("No items available. Please add items in the Items tab first.")
            no_items_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_items_label)
            return
        
        # Expiry table with proper scrolling
        self.expiry_table = QTableWidget()
        self.expiry_table.setColumnCount(7)
        self.expiry_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", "Location", "Expiry Date", "Days Left"
        ])

        # Configure table scrolling
        self.expiry_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.expiry_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set custom widths for columns
        self.expiry_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.expiry_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Item name stretches
        self.expiry_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Category stretches
        self.expiry_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Location stretches

        # Set fixed widths for numeric columns
        column_widths = {2: 80, 3: 60, 5: 100, 6: 80}
        for col, width in column_widths.items():
            self.expiry_table.setColumnWidth(col, width)

        # Apply modern table styling
        if apply_modern_table_styling:
            apply_modern_table_styling(self.expiry_table, row_height=50)
        else:
            self.expiry_table.setAlternatingRowColors(True)
            self.expiry_table.verticalHeader().setDefaultSectionSize(50)
            self.expiry_table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    gridline-color: #f1f5f9;
                    selection-background-color: #dbeafe;
                    font-size: 13px;
                    alternate-background-color: #f8fafc;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #f1f5f9;
                    min-height: 40px;
                }
                QHeaderView::section {
                    background-color: #f0f9ff;
                    border: none;
                    border-bottom: 2px solid #0ea5e9;
                    border-right: 1px solid #e2e8f0;
                    padding: 12px 8px;
                    font-weight: 600;
                    color: #374151;
                    min-height: 40px;
                    font-size: 13px;
                }
            """)
        
        # Add label to explain color coding
        color_key = QWidget()
        color_key_layout = QHBoxLayout(color_key)
        color_key_layout.setContentsMargins(0, 5, 0, 5)
        
        expired_label = QLabel("⬤ Expired")
        expired_label.setStyleSheet("color: #ff5555;")
        
        warning_label = QLabel("⬤ Expiring soon (< 7 days)")
        warning_label.setStyleSheet("color: #ffaa00;")
        
        ok_label = QLabel("⬤ OK")
        ok_label.setStyleSheet("color: #55aa55;")
        
        color_key_layout.addWidget(expired_label)
        color_key_layout.addWidget(warning_label)
        color_key_layout.addWidget(ok_label)
        color_key_layout.addStretch(1)
        
        layout.addWidget(color_key)
        layout.addWidget(self.expiry_table)
        
        # Update the expiry table
        self.update_expiry_table()
    
    def update_expiry_table(self):
        # Clear the table
        self.expiry_table.setRowCount(0)
        
        # Check if expiry_date column exists
        if 'expiry_date' not in self.inventory_df.columns or len(self.inventory_df) == 0:
            return
        
        # Convert expiry_date to datetime
        try:
            # Make a copy to avoid modifying the original DataFrame
            working_df = self.inventory_df.copy()
            working_df['expiry_date'] = pd.to_datetime(working_df['expiry_date'])
        except Exception as e:
            # If conversion fails, handle more gracefully
            print(f"Error converting dates: {e}")
            return
        
        # Sort by expiry date
        sorted_df = working_df.sort_values('expiry_date')
        
        # Calculate days until expiry
        today = pd.Timestamp(datetime.datetime.now().date())
        sorted_df['days_until_expiry'] = (sorted_df['expiry_date'] - today).dt.days
        
        # Filter to show all items with expiry dates, sorting by closest to expiry
        # For better visibility, this now shows all items with expiry dates
        expiring_items = sorted_df.dropna(subset=['expiry_date'])
        
        # Add rows
        self.expiry_table.setRowCount(len(expiring_items))
        for i, (_, row) in enumerate(expiring_items.iterrows()):
            # Item Name - column 0
            item_cell = QTableWidgetItem(row['item_name'])
            self.expiry_table.setItem(i, 0, item_cell)
            
            # Category - column 1
            if 'category' in row and pd.notna(row['category']):
                self.expiry_table.setItem(i, 1, QTableWidgetItem(str(row['category'])))
            else:
                self.expiry_table.setItem(i, 1, QTableWidgetItem(""))
            
            # Quantity - column 2
            self.expiry_table.setItem(i, 2, QTableWidgetItem(str(row['quantity'])))
            
            # Unit - column 3
            if 'unit' in row and pd.notna(row['unit']):
                self.expiry_table.setItem(i, 3, QTableWidgetItem(str(row['unit'])))
            else:
                self.expiry_table.setItem(i, 3, QTableWidgetItem(""))

            # Location - column 4
            if 'location' in row and pd.notna(row['location']):
                self.expiry_table.setItem(i, 4, QTableWidgetItem(str(row['location'])))
            else:
                self.expiry_table.setItem(i, 4, QTableWidgetItem(""))
            
            # Expiry Date - column 5
            expiry_date = row['expiry_date'].strftime('%d-%m-%Y')  # Format as DD-MM-YYYY for consistency
            expiry_item = QTableWidgetItem(expiry_date)
            self.expiry_table.setItem(i, 5, expiry_item)
            
            # Days Until Expiry - column 6
            days_until_expiry = row['days_until_expiry']
            days_item = QTableWidgetItem(str(days_until_expiry))
            
            # Color code based on days until expiry
            if days_until_expiry < 0:  # Already expired
                days_item.setBackground(QColor(255, 200, 200))  # Light red
                item_cell.setBackground(QColor(255, 200, 200))  # Highlight item name too
            elif days_until_expiry <= 7:  # Expires within a week
                days_item.setBackground(QColor(255, 255, 150))  # Light yellow
                item_cell.setBackground(QColor(255, 255, 150))  # Highlight item name too
            
            self.expiry_table.setItem(i, 6, days_item)
    
    def setup_items_tab(self):
        """Set up the Items tab with item management functionality"""
        # Create layout for the tab
        layout = QVBoxLayout(self.items_tab)
        
        # Add compact subheader
        header = QLabel("Item Database")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setMaximumHeight(25)  # Limit header height
        layout.addWidget(header)
        
        

        # Create a splitter for the tab
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Item list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Items:")
        self.items_search = QLineEdit()
        self.items_search.setPlaceholderText("Enter item name...")
        self.items_search.textChanged.connect(self.filter_items)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.items_search)
        left_layout.addLayout(search_layout)
        
        # Items table with proper scrolling
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Unit", "Category"])

        # Configure table scrolling
        self.items_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.items_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setSelectionMode(QTableWidget.SingleSelection)
        self.items_table.itemSelectionChanged.connect(self.load_selected_item)

        # Apply modern table styling
        if apply_modern_table_styling:
            apply_modern_table_styling(self.items_table, row_height=45)
        else:
            self.items_table.setAlternatingRowColors(True)
            self.items_table.verticalHeader().setDefaultSectionSize(45)
            self.items_table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    gridline-color: #f1f5f9;
                    selection-background-color: #dbeafe;
                    font-size: 13px;
                    alternate-background-color: #f8fafc;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #f1f5f9;
                    min-height: 35px;
                }
                QHeaderView::section {
                    background-color: #f0f9ff;
                    border: none;
                    border-bottom: 2px solid #0ea5e9;
                    border-right: 1px solid #e2e8f0;
                    padding: 12px 8px;
                    font-weight: 600;
                    color: #374151;
                    min-height: 35px;
                    font-size: 13px;
                }
            """)

        left_layout.addWidget(self.items_table)
        
        # Right side - Item details and edit
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Item details group
        details_group = QGroupBox("Item Details")
        details_layout = QFormLayout(details_group)
        
        # Item name (as dropdown with editable option)
        self.item_name_input = QComboBox()
        self.item_name_input.setEditable(True)
        self.item_name_input.setMinimumContentsLength(20)  # Make dropdown wider
        self.item_name_input.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.item_name_input.setPlaceholderText("Enter or select an item name...")
        
        # Populate with existing items if available
        if 'items' in self.data and len(self.data['items']) > 0:
            if 'item_name' in self.data['items'].columns:
                items = sorted(self.data['items']['item_name'].unique())
                self.item_name_input.addItems(items)
        # If no items found in items dataframe, try inventory
        elif 'inventory' in self.data and len(self.data['inventory']) > 0:
            if 'item_name' in self.data['inventory'].columns:
                items = sorted(self.data['inventory']['item_name'].unique())
                self.item_name_input.addItems(items)
        details_layout.addRow("Item Name:", self.item_name_input)
        
        # Unit type
        self.item_unit_combo = QComboBox()
        self.item_unit_combo.addItems(["g", "kg", "ml", "l", "piece", "dozen", "packet"])
        details_layout.addRow("Unit:", self.item_unit_combo)
        
        # Category
        self.item_category_combo = QComboBox()
        self.item_category_combo.setEditable(True)  # Make editable to allow adding new categories
        self.item_category_combo.setPlaceholderText("Enter or select a category...")
        # Populate with categories from Categories tab if available
        if 'categories' in self.data and self.data['categories'] is not None and len(self.data['categories']) > 0:
            categories = sorted(self.data['categories']['category_name'].unique())
            self.item_category_combo.addItems(categories)
        details_layout.addRow("Category:", self.item_category_combo)
        
        # Description
        self.item_description = QLineEdit()
        details_layout.addRow("Description:", self.item_description)
        
        right_layout.addWidget(details_group)
        
        # Buttons for actions
        buttons_layout = QHBoxLayout()
        
        self.add_item_button = QPushButton("Add New Item")
        self.add_item_button.clicked.connect(self.add_new_item)
        buttons_layout.addWidget(self.add_item_button)
        
        self.update_item_button = QPushButton("Update Item")
        self.update_item_button.clicked.connect(self.edit_existing_item)
        self.update_item_button.setEnabled(False)  # Disabled until an item is selected
        buttons_layout.addWidget(self.update_item_button)
        
        self.delete_item_button = QPushButton("Delete Item")
        self.delete_item_button.clicked.connect(self.delete_item)
        self.delete_item_button.setEnabled(False)  # Disabled until an item is selected
        buttons_layout.addWidget(self.delete_item_button)
        
        right_layout.addLayout(buttons_layout)
        right_layout.addStretch(1)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes (left: 40%, right: 60%)
        splitter.setSizes([400, 600])
        
        # Initialize items data if not exists
        if 'items' not in self.data:
            self.data['items'] = pd.DataFrame({
                'item_id': [],
                'item_name': [],
                'unit': [],
                'category': [],
                'description': []
            })
        
        # Load items data
        self.items_df = self.data['items'].copy()
        self.update_items_table()
    
    def filter_items(self):
        """Filter items based on search text"""
        search_text = self.items_search.text().lower()
        if search_text:
            filtered_df = self.items_df[self.items_df['item_name'].str.lower().str.contains(search_text)]
        else:
            filtered_df = self.items_df
        
        self.update_items_table(filtered_df)
    
    def update_items_table(self, df=None):
        """Update the items table with data"""
        if df is None:
            df = self.items_df
        
        self.items_table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            self.items_table.setItem(i, 0, QTableWidgetItem(str(row['item_name'])))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(row['unit'])))
            self.items_table.setItem(i, 2, QTableWidgetItem(str(row['category'])))
    
    def load_selected_item(self):
        """Load the selected item into the details form"""
        selected_rows = self.items_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            item_name = self.items_table.item(row, 0).text()
            
            # Find the item in the dataframe
            item = self.items_df[self.items_df['item_name'] == item_name].iloc[0]
            
            # Set item name in dropdown
            index = self.item_name_input.findText(item_name)
            if index >= 0:
                self.item_name_input.setCurrentIndex(index)
            else:
                self.item_name_input.setCurrentText(item_name)
            
            # Set unit
            unit_index = self.item_unit_combo.findText(item['unit'])
            if unit_index >= 0:
                self.item_unit_combo.setCurrentIndex(unit_index)
            
            # Set category
            category_index = self.item_category_combo.findText(item['category'])
            if category_index >= 0:
                self.item_category_combo.setCurrentIndex(category_index)
            
            # Set description
            self.item_description.setText(item.get('description', ''))
            
            # Enable update and delete buttons
            self.update_item_button.setEnabled(True)
            self.delete_item_button.setEnabled(True)
        else:
            # Clear form and disable buttons
            self.item_name_input.setCurrentText("")
            self.item_description.clear()
            self.update_item_button.setEnabled(False)
            self.delete_item_button.setEnabled(False)
    
    def add_new_item(self):
        """Add a new item to the database"""
        item_name = self.item_name_input.currentText().strip()
        if not item_name:
            QMessageBox.warning(self, "Warning", "Item name cannot be empty.")
            return
        
        # Get category value
        category = self.item_category_combo.currentText().strip()
        
        # Check if item already exists
        if len(self.items_df[self.items_df['item_name'] == item_name]) > 0:
            QMessageBox.warning(self, "Warning", f"Item '{item_name}' already exists.")
            return
        
        # Create new item
        new_item = {
            'item_id': len(self.items_df) + 1,
            'item_name': item_name,
            'unit': self.item_unit_combo.currentText(),
            'category': category,
            'description': self.item_description.text()
        }
        
        # Add to dataframe
        self.items_df = pd.concat([self.items_df, pd.DataFrame([new_item])], ignore_index=True)
        
        # Update data dictionary
        self.data['items'] = self.items_df
        
        # Save to CSV
        self.items_df.to_csv('data/items.csv', index=False)
        
        # If category is new, add it to categories
        if category and ('categories' not in self.data or 
                        self.data['categories'] is None or
                        len(self.data['categories']) == 0 or 
                        category not in self.data['categories']['category_name'].values):
            # Initialize categories dataframe if it doesn't exist
            if 'categories' not in self.data or self.data['categories'] is None or len(self.data['categories']) == 0:
                self.data['categories'] = pd.DataFrame(columns=['category_id', 'category_name', 'description'])
            
            # Generate new category ID
            new_category_id = 1
            if len(self.data['categories']) > 0 and 'category_id' in self.data['categories'].columns:
                new_category_id = self.data['categories']['category_id'].max() + 1 if not self.data['categories'].empty else 1
            
            # Create new category record
            new_category = pd.DataFrame({
                'category_id': [new_category_id],
                'category_name': [category],
                'description': [f"Auto-created when adding item {item_name}"]
            })
            
            # Add to categories dataframe
            self.data['categories'] = pd.concat([self.data['categories'], new_category], ignore_index=True)
            
            # Save to CSV
            self.data['categories'].to_csv('data/categories.csv', index=False)
        
        # Update category combos in the UI
        self.update_category_combos()
        
        # Update tables
        self.update_items_table()
        self.update_categories_table()  # Update category counts
        
        QMessageBox.information(self, "Success", f"Item '{item_name}' added successfully.")

    def edit_existing_item(self):
        """Update an existing item's definition in the database"""
        selected_rows = self.items_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an item to update.")
            return

        # Get the original item name from the selected row in the table
        original_item_name = self.items_table.item(selected_rows[0].row(), 0).text()

        # Get new values from the form
        new_item_name = self.item_name_input.currentText().strip()
        new_unit = self.item_unit_combo.currentText()
        new_category = self.item_category_combo.currentText().strip()
        new_description = self.item_description.text()

        if not new_item_name:
            QMessageBox.warning(self, "Warning", "Item name cannot be empty.")
            return

        # Check if the new item name conflicts with another existing item
        if new_item_name != original_item_name and len(self.items_df[self.items_df['item_name'] == new_item_name]) > 0:
            QMessageBox.warning(self, "Warning", f"An item with the name '{new_item_name}' already exists.")
            return

        # Find the item in the dataframe
        item_indices = self.items_df[self.items_df['item_name'] == original_item_name].index
        if item_indices.empty:
            QMessageBox.critical(self, "Error", f"Could not find '{original_item_name}' to update. Please refresh.")
            return
        item_index = item_indices[0]

        # Update item in dataframe
        self.items_df.loc[item_index, 'item_name'] = new_item_name
        self.items_df.loc[item_index, 'unit'] = new_unit
        self.items_df.loc[item_index, 'category'] = new_category
        self.items_df.loc[item_index, 'description'] = new_description

        # Update data dictionary
        self.data['items'] = self.items_df.copy()

        # Save to CSV
        self.items_df.to_csv('data/items.csv', index=False)

        # If category is new, add it to categories
        if new_category and ('categories' not in self.data or
                            self.data['categories'] is None or
                            self.data['categories'].empty or
                            new_category not in self.data['categories']['category_name'].values):
            if 'categories' not in self.data or self.data['categories'] is None or self.data['categories'].empty:
                self.data['categories'] = pd.DataFrame(columns=['category_id', 'category_name', 'description'])
            
            new_category_id = 1
            if not self.data['categories'].empty and 'category_id' in self.data['categories'].columns and self.data['categories']['category_id'].notna().any():
                new_category_id = self.data['categories']['category_id'].max() + 1
            elif not self.data['categories'].empty:
                 new_category_id = len(self.data['categories']) + 1

            new_category_df = pd.DataFrame({
                'category_id': [new_category_id],
                'category_name': [new_category],
                'description': [f"Auto-created when updating item {new_item_name}"]
            })
            self.data['categories'] = pd.concat([self.data['categories'], new_category_df], ignore_index=True)
            self.data['categories'].to_csv('data/categories.csv', index=False)
            if hasattr(self, 'update_category_combos'): # Check if method exists
                self.update_category_combos()

        QMessageBox.information(self, "Success", f"Item '{original_item_name}' updated to '{new_item_name}'.")
        self.update_items_table()
        self.update_categories_table() # Update category counts
        if hasattr(self, 'update_category_combos'): # Check if method exists
            self.update_category_combos() # Ensure all category dropdowns are updated

        # Clear form and disable update/delete buttons as selection might be invalid
        self.item_name_input.setCurrentText("")
        self.item_unit_combo.setCurrentIndex(0)
        self.item_category_combo.setCurrentText("")
        self.item_description.clear()
        self.update_item_button.setEnabled(False)
        self.delete_item_button.setEnabled(False)

    def delete_item(self):
        """Delete an item from the database"""
        selected_rows = self.items_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        item_name = self.items_table.item(row, 0).text()
    
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                    f"Are you sure you want to delete '{item_name}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Delete from dataframe
            self.items_df = self.items_df[self.items_df['item_name'] != item_name]
            
            # Update data dictionary
            self.data['items'] = self.items_df
            
            # Save to CSV
            self.items_df.to_csv('data/items.csv', index=False)
            
            # Update tables
            self.update_items_table()
            self.update_categories_table()  # Update category counts
            

    def setup_categories_tab(self):
        """Set up the Categories tab with category management functionality"""
        # Create layout for the tab
        layout = QVBoxLayout(self.categories_tab)
    
                
        # Create a splitter for the tab
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Category list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["Category Name", "Item Count"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.categories_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.categories_table.setSelectionMode(QTableWidget.SingleSelection)
        self.categories_table.itemSelectionChanged.connect(self.load_selected_category)
        left_layout.addWidget(self.categories_table)
        
        # Right side - Category details and edit
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Category details group
        details_group = QGroupBox("Category Details")
        details_layout = QFormLayout(details_group)
        
        # Category name
        self.category_name_input = QLineEdit()
        details_layout.addRow("Category Name:", self.category_name_input)
        
        # Description
        self.category_description = QLineEdit()
        details_layout.addRow("Description:", self.category_description)
        
        right_layout.addWidget(details_group)

        # Items in Category group
        items_group = QGroupBox("Items in Selected Category")
        items_layout = QVBoxLayout(items_group)

        # Items table for selected category
        self.category_items_table = QTableWidget()
        self.category_items_table.setColumnCount(4)
        self.category_items_table.setHorizontalHeaderLabels(["Item Name", "Description", "Unit", "Actions"])

        # Set specific column widths instead of stretch to fit better
        header = self.category_items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Item Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Description (takes remaining space)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit
        header.setSectionResizeMode(3, QHeaderView.Fixed)            # Actions
        header.resizeSection(3, 80)  # Fixed width for Actions column

        self.category_items_table.setMaximumHeight(200)
        self.category_items_table.setMinimumHeight(150)
        items_layout.addWidget(self.category_items_table)

        right_layout.addWidget(items_group)

        # Buttons for actions
        buttons_layout = QHBoxLayout()
        
        self.add_category_button = QPushButton("Add New Category")
        self.add_category_button.clicked.connect(self.add_new_category)
        buttons_layout.addWidget(self.add_category_button)
        
        self.update_category_button = QPushButton("Update Category")
        self.update_category_button.clicked.connect(self.update_category)
        self.update_category_button.setEnabled(False)  # Disabled until a category is selected
        buttons_layout.addWidget(self.update_category_button)
        
        self.delete_category_button = QPushButton("Delete Category")
        self.delete_category_button.clicked.connect(self.delete_category)
        self.delete_category_button.setEnabled(False)  # Disabled until a category is selected
        buttons_layout.addWidget(self.delete_category_button)
        
        right_layout.addLayout(buttons_layout)
        right_layout.addStretch(1)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes (left: 40%, right: 60%)
        splitter.setSizes([400, 600])
        
        # Initialize categories data if not exists
        if 'categories' not in self.data:
            self.data['categories'] = pd.DataFrame({
                'category_id': [],
                'category_name': [],
                'description': []
            })
        
        # Load categories data
        self.categories_df = self.data['categories'].copy()

        # Force immediate update of categories table
        print(f"🔄 Initial categories table setup...")
        self.update_categories_table()

        # Also ensure items data is loaded for category counting
        if 'items' in self.data:
            self.items_df = self.data['items'].copy()
            print(f"   Items loaded for category counting: {len(self.items_df)} items")
            # Update again with item counts
            self.update_categories_table()
    
    def update_categories_table(self):
        """Update the categories table with data"""
        print(f"🔄 Updating categories table...")
        print(f"   Categories DF shape: {self.categories_df.shape}")

        # Count items in each category
        if 'items' in self.data and len(self.data['items']) > 0:
            # Make sure we're using the latest data
            self.items_df = self.data['items'].copy()
            print(f"   Items DF shape: {self.items_df.shape}")
            category_counts = self.items_df.groupby('category').size().reset_index()
            category_counts.columns = ['category_name', 'item_count']
            print(f"   Category counts: {len(category_counts)} categories")
        else:
            category_counts = pd.DataFrame(columns=['category_name', 'item_count'])
            print(f"   No items found for category counting")

        # Make sure we're using the latest categories data
        self.categories_df = self.data['categories'].copy()
        print(f"   Updated categories DF shape: {self.categories_df.shape}")

        # Merge with categories dataframe
        if len(self.categories_df) > 0:
            merged_df = pd.merge(self.categories_df, category_counts,
                                on='category_name', how='left').fillna(0)
            print(f"   Merged DF shape: {merged_df.shape}")
        else:
            merged_df = self.categories_df.copy()
            merged_df['item_count'] = 0
            print(f"   Using categories DF only")

        # Update table
        self.categories_table.setRowCount(len(merged_df))
        print(f"   Setting table rows to: {len(merged_df)}")

        for i, (_, row) in enumerate(merged_df.iterrows()):
            category_name = row['category_name']
            item_count = str(int(row.get('item_count', 0)))
            self.categories_table.setItem(i, 0, QTableWidgetItem(category_name))
            self.categories_table.setItem(i, 1, QTableWidgetItem(item_count))
            if i < 5:  # Only print first 5 for brevity
                print(f"   Row {i}: {category_name} - {item_count} items")

        print(f"✅ Categories table updated with {len(merged_df)} rows")
    
    def load_selected_category(self):
        """Load the selected category into the details form and show items in that category"""
        selected_rows = self.categories_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            category_name = self.categories_table.item(row, 0).text()

            # Find the category in the dataframe
            category = self.categories_df[self.categories_df['category_name'] == category_name]
            if len(category) > 0:
                category = category.iloc[0]

                # Populate the form
                self.category_name_input.setText(category['category_name'])
                self.category_description.setText(category.get('description', ''))

                # Enable update and delete buttons
                self.update_category_button.setEnabled(True)
                self.delete_category_button.setEnabled(True)

                # Load items in this category
                self.load_category_items(category_name)
        else:
            # Clear form and disable buttons
            self.category_name_input.clear()
            self.category_description.clear()
            self.update_category_button.setEnabled(False)
            self.delete_category_button.setEnabled(False)

            # Clear items table
            self.category_items_table.setRowCount(0)

    def load_category_items(self, category_name):
        """Load and display items that belong to the selected category"""
        try:
            # Get items in this category
            if 'items' in self.data and len(self.data['items']) > 0:
                category_items = self.data['items'][self.data['items']['category'] == category_name]

                # Update items table
                self.category_items_table.setRowCount(len(category_items))

                for i, (_, item) in enumerate(category_items.iterrows()):
                    # Item Name
                    self.category_items_table.setItem(i, 0, QTableWidgetItem(item.get('item_name', '')))

                    # Description
                    self.category_items_table.setItem(i, 1, QTableWidgetItem(item.get('description', '')))

                    # Unit
                    self.category_items_table.setItem(i, 2, QTableWidgetItem(item.get('unit', '')))

                    # Actions - Add a button to edit item
                    edit_btn = QPushButton("Edit")
                    edit_btn.clicked.connect(lambda checked, item_name=item.get('item_name', ''): self.edit_item_from_category(item_name))
                    self.category_items_table.setCellWidget(i, 3, edit_btn)

                print(f"Loaded {len(category_items)} items for category '{category_name}'")
            else:
                self.category_items_table.setRowCount(0)
                print(f"No items found for category '{category_name}'")

        except Exception as e:
            print(f"Error loading category items: {e}")
            self.category_items_table.setRowCount(0)

    def edit_item_from_category(self, item_name):
        """Switch to Items tab and load the selected item for editing"""
        try:
            # Switch to Items tab
            self.tabs.setCurrentIndex(1)  # Items tab is index 1

            # Find and select the item in the items table
            for row in range(self.items_table.rowCount()):
                if self.items_table.item(row, 0) and self.items_table.item(row, 0).text() == item_name:
                    self.items_table.selectRow(row)
                    self.load_selected_item()  # Load item into edit form
                    break

            print(f"Switched to Items tab and selected '{item_name}' for editing")

        except Exception as e:
            print(f"Error switching to edit item: {e}")
    
    def add_new_category(self):
        """Add a new category to the database"""
        category_name = self.category_name_input.text().strip()
        if not category_name:
            QMessageBox.warning(self, "Warning", "Category name cannot be empty.")
            return
        
        # Check if category already exists
        if len(self.categories_df) > 0 and len(self.categories_df[self.categories_df['category_name'] == category_name]) > 0:
            QMessageBox.warning(self, "Warning", f"Category '{category_name}' already exists.")
            return
        
        # Create new category
        new_category = {
            'category_id': len(self.categories_df) + 1,
            'category_name': category_name,
            'description': self.category_description.text()
        }
        
        # Add to dataframe
        self.categories_df = pd.concat([self.categories_df, pd.DataFrame([new_category])], ignore_index=True)
        
        # Update data dictionary
        self.data['categories'] = self.categories_df
        
        # Save to CSV
        self.categories_df.to_csv('data/categories.csv', index=False)
        
        # Update table
        self.update_categories_table()
        
        # Update category combo in items tab
        self.item_category_combo.clear()
        self.item_category_combo.addItems(self.categories_df['category_name'].tolist())
        
        # Clear form
        self.category_name_input.clear()
        self.category_description.clear()
        
        QMessageBox.information(self, "Success", f"Category '{category_name}' added successfully.")
    
    def update_category(self):
        """Update an existing category"""
        selected_rows = self.categories_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        old_category_name = self.categories_table.item(row, 0).text()
        new_category_name = self.category_name_input.text().strip()
        
        if not new_category_name:
            QMessageBox.warning(self, "Warning", "Category name cannot be empty.")
            return
        
        # Check if new name already exists (unless it's the same category)
        if new_category_name != old_category_name and len(self.categories_df[self.categories_df['category_name'] == new_category_name]) > 0:
            QMessageBox.warning(self, "Warning", f"Category '{new_category_name}' already exists.")
            return
        
        # Update category in dataframe
        category_index = self.categories_df[self.categories_df['category_name'] == old_category_name].index[0]
        self.categories_df.at[category_index, 'category_name'] = new_category_name
        self.categories_df.at[category_index, 'description'] = self.category_description.text()
        
        # Update data dictionary
        self.data['categories'] = self.categories_df
        
        # Save to CSV
        self.categories_df.to_csv('data/categories.csv', index=False)
        
        # Update table
        self.update_categories_table()
        
        # Update category combo in items tab
        self.item_category_combo.clear()
        self.item_category_combo.addItems(self.categories_df['category_name'].tolist())
        
        # Also update any items that used the old category name
        if 'items' in self.data and len(self.data['items']) > 0:
            self.data['items'].loc[self.data['items']['category'] == old_category_name, 'category'] = new_category_name
            self.items_df = self.data['items'].copy()
            self.items_df.to_csv('data/items.csv', index=False)
            self.update_items_table()
        
        QMessageBox.information(self, "Success", f"Category '{new_category_name}' updated successfully.")
    
    def delete_category(self):
        """Delete a category from the database"""
        selected_rows = self.categories_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        category_name = self.categories_table.item(row, 0).text()
        
        # Check if category is in use
        if 'items' in self.data and len(self.data['items']) > 0:
            items_using_category = self.data['items'][self.data['items']['category'] == category_name]
            if len(items_using_category) > 0:
                reply = QMessageBox.question(self, "Category In Use", 
                                          f"Category '{category_name}' is used by {len(items_using_category)} items. "
                                          "Deleting it will set those items to have no category. Continue?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                
                # Update items to have no category
                self.data['items'].loc[self.data['items']['category'] == category_name, 'category'] = ""
                self.items_df = self.data['items'].copy()
                self.items_df.to_csv('data/items.csv', index=False)
                self.update_items_table()
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete '{category_name}'?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Delete from dataframe
            self.categories_df = self.categories_df[self.categories_df['category_name'] != category_name]
            
            # Update data dictionary
            self.data['categories'] = self.categories_df
            
            # Save to CSV
            self.categories_df.to_csv('data/categories.csv', index=False)
            
            # Update table
            self.update_categories_table()
            
            # Update category combo in items tab
            self.item_category_combo.clear()
            self.item_category_combo.addItems(self.categories_df['category_name'].tolist())
            
            # Clear form
            self.category_name_input.clear()
            self.category_description.clear()
            self.update_category_button.setEnabled(False)
            self.delete_category_button.setEnabled(False)
            
            QMessageBox.information(self, "Success", f"Category '{category_name}' deleted successfully.")
    
    def setup_category_analysis_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.category_analysis_tab)
        
        # Add subheader
        header = QLabel("Category Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Make sure total_value is calculated
        if 'price_per_unit' in self.inventory_df.columns and 'quantity' in self.inventory_df.columns:
            if 'total_value' not in self.inventory_df.columns:
                self.inventory_df['total_value'] = self.inventory_df['quantity'] * self.inventory_df['price_per_unit']
        
        # Create a splitter for top charts
        top_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(top_splitter)
        
        # Check if category column exists
        if 'category' not in self.inventory_df.columns or len(self.inventory_df) == 0:
            layout.addWidget(QLabel("No category data available"))
            return
        
        # Calculate total value for each item before grouping
        if 'quantity' in self.inventory_df.columns and \
           ('avg_price' in self.inventory_df.columns or 'price' in self.inventory_df.columns):
            # First create a helper function to calculate total value for each row
            def calculate_row_value(row):
                # Get quantity - first calculate qty_left if we have purchased and used
                if 'qty_purchased' in row and pd.notna(row['qty_purchased']) and 'qty_used' in row and pd.notna(row['qty_used']):
                    qty = float(row['qty_purchased']) - float(row['qty_used'])
                # If qty_left is directly available, use it
                elif 'qty_left' in row and pd.notna(row['qty_left']):
                    qty = float(row['qty_left'])
                # Fallback to regular quantity field
                elif 'quantity' in row and pd.notna(row['quantity']):
                    qty = float(row['quantity'])
                else:
                    qty = 0
                    
                # Get price, using avg_price if available, otherwise price
                if 'avg_price' in row and pd.notna(row['avg_price']):
                    price = float(row['avg_price'])
                elif 'price' in row and pd.notna(row['price']):
                    price = float(row['price'])
                else:
                    price = 0
                    
                return qty * price
            
            # Apply the function to create a calculated total_value column
            self.inventory_df['calculated_total_value'] = self.inventory_df.apply(calculate_row_value, axis=1)
            
            # Now do the category analysis with our calculated value
            category_analysis = self.inventory_df.groupby('category').agg({
                'item_id': 'count' if 'item_id' in self.inventory_df.columns else 'size',
                'calculated_total_value': 'sum'
            }).reset_index()
            category_analysis.columns = ['category', 'item_count', 'total_value']
        else:
            # Fallback if we can't calculate values
            category_analysis = self.inventory_df.groupby('category').agg({
                'item_id': 'count' if 'item_id' in self.inventory_df.columns else 'size'
            }).reset_index()
            category_analysis['total_value'] = 1  # Placeholder value for display
            category_analysis.columns = ['category', 'item_count', 'total_value']
        
        # Left side - Category value chart
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Inventory Value by Category"))
        
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        # Ensure non-negative values for pie chart
        if (category_analysis['total_value'] < 0).any():
            # Handle negative values by replacing them with 0
            category_analysis.loc[category_analysis['total_value'] < 0, 'total_value'] = 0
        
        # Check if we have any positive values left
        if (category_analysis['total_value'] > 0).any():
            ax1.pie(category_analysis['total_value'], labels=category_analysis['category'], autopct='%1.1f%%')
        else:
            # If no positive values, display a message
            ax1.text(0.5, 0.5, 'No positive values available for chart', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax1.transAxes)
        ax1.set_title('Inventory Value by Category')
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.tight_layout()
        
        canvas1 = FigureCanvas(fig1)
        left_layout.addWidget(canvas1)
        top_splitter.addWidget(left_widget)
        
        # Right side - Category item count chart
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Item Count by Category"))
        
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        sorted_category = category_analysis.sort_values('item_count', ascending=False)
        ax2.bar(sorted_category['category'], sorted_category['item_count'])
        ax2.set_title('Item Count by Category')
        ax2.set_xlabel('Category')
        ax2.set_ylabel('Number of Items')
        ax2.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        canvas2 = FigureCanvas(fig2)
        right_layout.addWidget(canvas2)
        top_splitter.addWidget(right_widget)
        
        # Location analysis header
        location_header = QLabel("Storage Location Analysis")
        location_header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(location_header)
        
        # Check if location column exists
        if 'location' not in self.inventory_df.columns or len(self.inventory_df) == 0:
            layout.addWidget(QLabel("No location data available"))
            return
        
        # Create a splitter for bottom charts
        bottom_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(bottom_splitter)
        
        # Location analysis
        # Use the same calculated_total_value we created for the category analysis if it exists
        if 'calculated_total_value' not in self.inventory_df.columns:
            # If it doesn't exist, calculate it now
            def calculate_row_value(row):
                # Get quantity - first calculate qty_left if we have purchased and used
                if 'qty_purchased' in row and pd.notna(row['qty_purchased']) and 'qty_used' in row and pd.notna(row['qty_used']):
                    qty = float(row['qty_purchased']) - float(row['qty_used'])
                # If qty_left is directly available, use it
                elif 'qty_left' in row and pd.notna(row['qty_left']):
                    qty = float(row['qty_left'])
                # Fallback to regular quantity field
                elif 'quantity' in row and pd.notna(row['quantity']):
                    qty = float(row['quantity'])
                else:
                    qty = 0
                    
                # Get price, using avg_price if available, otherwise price
                if 'avg_price' in row and pd.notna(row['avg_price']):
                    price = float(row['avg_price'])
                elif 'price' in row and pd.notna(row['price']):
                    price = float(row['price'])
                else:
                    price = 0
                    
                return qty * price
            
            # Apply the function to create a calculated total_value column
            self.inventory_df['calculated_total_value'] = self.inventory_df.apply(calculate_row_value, axis=1)
        
        # Now do the location analysis with our calculated value
        location_analysis = self.inventory_df.groupby('location').agg({
            'item_id': 'count' if 'item_id' in self.inventory_df.columns else 'size',
            'calculated_total_value': 'sum'
        }).reset_index()
        location_analysis.columns = ['location', 'item_count', 'total_value']
        
        # Left side - Location value chart
        left_widget2 = QWidget()
        left_layout2 = QVBoxLayout(left_widget2)
        left_layout2.addWidget(QLabel("Inventory Value by Location"))
        
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        # Ensure non-negative values for pie chart
        if (location_analysis['total_value'] < 0).any():
            # Handle negative values by replacing them with 0
            location_analysis.loc[location_analysis['total_value'] < 0, 'total_value'] = 0
        
        # Check if we have any positive values left
        if (location_analysis['total_value'] > 0).any():
            ax3.pie(location_analysis['total_value'], labels=location_analysis['location'], autopct='%1.1f%%')
        else:
            # If no positive values, display a message
            ax3.text(0.5, 0.5, 'No positive values available for chart', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax3.transAxes)
        ax3.set_title('Inventory Value by Location')
        ax3.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.tight_layout()
        
        canvas3 = FigureCanvas(fig3)
        left_layout2.addWidget(canvas3)
        bottom_splitter.addWidget(left_widget2)
        
        # Right side - Location item count chart
        right_widget2 = QWidget()
        right_layout2 = QVBoxLayout(right_widget2)
        right_layout2.addWidget(QLabel("Item Count by Location"))
        
        fig4, ax4 = plt.subplots(figsize=(5, 4))
        sorted_location = location_analysis.sort_values('item_count', ascending=False)
        ax4.bar(sorted_location['location'], sorted_location['item_count'])
        ax4.set_title('Item Count by Location')
        ax4.set_xlabel('Location')
        ax4.set_ylabel('Number of Items')
        ax4.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        canvas4 = FigureCanvas(fig4)
        right_layout2.addWidget(canvas4)
        bottom_splitter.addWidget(right_widget2)
    

    def showEvent(self, event):
        """Handle widget show event to refresh data"""
        super().showEvent(event)
        try:
            # Force refresh data when widget is shown
            self.refresh_all_data()
        except Exception as e:
            print(f"Error in inventory showEvent: {e}")

    def update_inventory_item(self):
        # Get selected item
        item_name = self.edit_item_combo.currentText()
        
        # Get new values
        new_category = self.edit_category_combo.currentText()
        new_qty_purchased = self.edit_quantity_purchased_spin.value()
        new_qty_used = self.edit_quantity_used_spin.value()
        new_reorder_level = self.edit_reorder_level_spin.value()
        new_unit = self.edit_unit_combo.currentText()
        new_price = self.edit_price_spin.value()
        new_location = self.edit_location_combo.currentText()
        new_expiry_date = self.edit_expiry_date.date().toString('yyyy-MM-dd')
        
        # Validate that quantity used isn't more than purchased
        if new_qty_used > new_qty_purchased:
            QMessageBox.warning(self, "Input Error", "Quantity used cannot be more than quantity purchased.")
            return
        
        # Calculate quantity left (for backward compatibility)
        new_quantity = new_qty_purchased - new_qty_used
        
        # Update the item in the dataframe
        item_index = self.inventory_df[self.inventory_df['item_name'] == item_name].index
        if len(item_index) > 0:
            self.inventory_df.loc[item_index, 'category'] = new_category
            self.inventory_df.loc[item_index, 'qty_purchased'] = new_qty_purchased
            self.inventory_df.loc[item_index, 'qty_used'] = new_qty_used
            self.inventory_df.loc[item_index, 'quantity'] = new_quantity  # For backward compatibility
            self.inventory_df.loc[item_index, 'reorder_level'] = new_reorder_level
            self.inventory_df.loc[item_index, 'unit'] = new_unit
            self.inventory_df.loc[item_index, 'price'] = new_price
            self.inventory_df.loc[item_index, 'location'] = new_location
            self.inventory_df.loc[item_index, 'expiry_date'] = new_expiry_date
            
            # Update the data dictionary
            self.data['inventory'] = self.inventory_df
            
            # Save to CSV
            self.inventory_df.to_csv('data/inventory.csv', index=False)
            
            # Show success message
            QMessageBox.information(self, "Success", f"{item_name} updated successfully!")
            
            # Refresh the inventory table
            self.update_inventory_table(self.inventory_df)
            
            # Refresh the inventory table
            self.apply_filters()

    def refresh_data(self):
        """Refresh inventory data from CSV file"""
        try:
            # Reload inventory from CSV
            inventory_file = 'data/inventory.csv'
            if os.path.exists(inventory_file):
                self.inventory_df = pd.read_csv(inventory_file)
                self.data['inventory'] = self.inventory_df

                # Refresh all displays
                self.update_inventory_table(self.inventory_df)
                self.apply_filters()
                self.update_charts()

                # Show success message
                QMessageBox.information(self, "Refresh Complete",
                    f"Inventory data refreshed successfully!\n\nLoaded {len(self.inventory_df)} items from CSV file.")

                print(f"[SUCCESS] Inventory refreshed: {len(self.inventory_df)} items loaded")

            else:
                QMessageBox.warning(self, "File Not Found",
                    f"Inventory CSV file not found at: {inventory_file}")

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error refreshing inventory data: {e}")
            QMessageBox.critical(self, "Refresh Error",
                f"Failed to refresh inventory data:\n{str(e)}")
            print(f"[ERROR] Error refreshing inventory data: {e}")
