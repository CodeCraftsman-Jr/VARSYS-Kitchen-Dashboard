"""
Advanced Recipe Costing & Pricing Management Module
Comprehensive pricing analysis with cost calculations and profit margins
"""

import os
import json
import pandas as pd
import logging
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel,
                             QTabWidget, QGroupBox, QFormLayout, QLineEdit,
                             QSpinBox, QTextEdit, QPushButton, QDialog,
                             QDialogButtonBox, QMessageBox, QSplitter,
                             QComboBox, QDateEdit, QDoubleSpinBox, QGridLayout,
                             QFrame, QScrollArea, QProgressBar, QCheckBox,
                             QAbstractItemView, QMenu, QInputDialog)
from PySide6.QtCore import Qt, Signal, QDate, QTimer, QPoint
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QAction
from utils.table_styling import apply_universal_column_resizing

# Import notification system
try:
    from .notification_system import notify_info, notify_success, notify_warning, notify_error
except ImportError:
    def notify_info(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_success(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_warning(title, message, **kwargs): logging.warning(f"{title}: {message}")
    def notify_error(title, message, **kwargs): logging.error(f"{title}: {message}")

class PricingCard(QFrame):
    """Modern pricing metrics card widget"""
    
    def __init__(self, title, value, subtitle="", color="#2563eb", parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #f8fafc;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 700;")
        layout.addWidget(value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
            layout.addWidget(subtitle_label)
        
        layout.addStretch()

class PricingManagementWidget(QWidget):
    """Advanced pricing management widget with comprehensive cost analysis"""

    data_changed = Signal()
    pricing_updated = Signal(str, str, float)  # recipe_name, field_name, new_value
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)

        self.data_loaded = False

        # Initialize ingredient pricing data based on user's Excel analysis
        self.init_ingredient_pricing()

        # Initialize recipe pricing data from user's Excel
        self.init_recipe_pricing_data()

        # Initialize pricing data structure
        self.init_pricing_data()

        # Initialize UI
        self.init_ui()

        # Load data lazily to prevent lag - but don't auto-check missing items
        QTimer.singleShot(100, self.load_data_lazy_no_missing_check)

        # Remove auto-refresh timer - use manual button instead
        # self.refresh_timer = QTimer()
        # self.refresh_timer.timeout.connect(self.refresh_calculations)
        # self.refresh_timer.start(60000)  # Disabled - use manual button
    
    def init_ingredient_pricing(self):
        """Initialize ingredient pricing data based on user's Excel analysis"""
        self.ingredient_unit_prices = {
            # Oils and Fats
            "Oil": 0.146, "oil": 0.146, "Ghee": 0.74,

            # Dairy Products
            "Milk": 0.076, "milk": 0.076, "Curd": 0.068,

            # Eggs
            "Eggs": 7.0,

            # Rice and Grains
            "Bheemas Rice": 0.074, "cooked rice": 0.0222, "Dosa batter": 0.0286,
            "Dosa Batter": 0.0286, "Wheat": 0.0524,

            # Vegetables
            "Onion": 0.0415, "onion": 0.0415, "Tomato": 0.03, "tomato": 0.03,
            "Carrot": 0.15, "Potatoes": 0.06, "Green Chilli": 0.1156,
            "green chilli": 0.1156, "Garlic": 0.2, "garlic": 0.2,
            "Ginger": 0.2632, "ginger": 0.2632, "Bringal": 0.08,

            # Spices and Seasonings
            "Salt": 0.05, "Pepper": 0.7, "Pepper Powder(Milagu Thool)": 0.1875,
            "turmeric powder": 0.3, "Red chilli Powder": 0.3647, "Garam Masala": 1.05,
            "Chicken Masala": 0.3, "garam masala": 1.05, "Cumin Powder(seraga Thool)": 0.5,
            "corainder powder(mali powder)": 0.28, "Fennel Seed(Sombu)-saunf": 0.2,
            "Cardamon(Yelakai)": 0.1875, "cinamon(pattai)": 0.0, "clove(lavagam)": 0.5,
            "Star Anise(Annachipu)": 0.2143, "bring leaf": 0.15, "Idli podi": 0.12,
            "sambhar podi": 0.2, "perugayam(asafoetida)": 0.6, "kolambu molaga thool": 0.375,
            "Dry Chilli": 0.125,

            # Lentils and Pulses
            "Urad Dal(ulunda parupu)": 0.3111, "kadalai parupu(bengal gram)": 0.113,
            "Mustard Urad Dal(Kadugu Uluntha Parupu)": 0.25, "toovaram parupu(toor dal)": 0.1837,
            "Pasiparupu(algae lenthils)": 0.1586, "Fried Gram Split(Pottu Kadalai)": 0.2437,
            "white channa": 0.0, "beans": 0.0, "Green Beans": 0.2273,

            # Nuts and Seeds
            "Coconut": 0.1333, "coconut": 0.1333, "cashew nut": 0.1667, "Peanuts": 0.2209,

            # Herbs and Leaves
            "Curry Leaves(Karuvepulai)": 0.15, "Coriander(kothamali)": 0.1136,

            # Beverages and Powders
            "Tea powder": 0.15, "Coffee powder": 0.5, "Sugar": 0.05, "sugar": 0.05,
            "Boost": 5.0, "Horlicks": 5.0, "Green tea leaves": 0.0,

            # Prepared Items
            "Coconut Chutni(Cooked)": 0.0577, "Tomato Chutni(Cooked)": 0.0583,
            "Sambhar": 0.0542, "Chicken gravy": 0.2208, "Chicken Gravy": 0.2208,
            "Fish Kolambu(Parai Fish)": 0.0888, "Fish(Parai Fish)": 10.9375,
            "vellam(jaggery)": 0.08, "bread": 2.857,

            # Meat and Protein
            "Chicken": 0.4,

            # Fruits
            "Lemons": 5.0,

            # Tamarind and Souring Agents
            "Pulli": 0.36,

            # Paste and Prepared Ingredients
            "garlic ginger paste": 0.2,
        }

    def init_recipe_pricing_data(self):
        """Initialize recipe pricing data from CSV files first, then fallback to hardcoded data"""
        # First try to load from CSV files
        self.recipe_pricing_data = {}

        # Load from main pricing CSV file
        try:
            import os
            import pandas as pd

            pricing_csv_path = os.path.join('data', 'pricing.csv')
            if os.path.exists(pricing_csv_path):
                pricing_df = pd.read_csv(pricing_csv_path)
                self.logger.info(f"Loading pricing data from {pricing_csv_path}")

                for _, row in pricing_df.iterrows():
                    recipe_name = row.get('recipe_name', '')
                    if recipe_name:
                        self.recipe_pricing_data[recipe_name] = {
                            'others_pricing': float(row.get('others_pricing', 0)),
                            'our_pricing': float(row.get('our_pricing', 0)),
                            'cooking_time': str(row.get('cooking_time', '')),
                            'other_charges': float(row.get('other_charges', 2.0))
                        }

                self.logger.info(f"Loaded {len(self.recipe_pricing_data)} recipes from CSV")

                # If we successfully loaded data from CSV, return early
                if self.recipe_pricing_data:
                    return

        except Exception as e:
            self.logger.error(f"Error loading pricing data from CSV: {e}")

        # Fallback to hardcoded data if CSV loading fails
        self.logger.info("Using fallback hardcoded pricing data")
        self.recipe_pricing_data = {
            # Basic Items
            "Dosa": {"others_pricing": 76, "our_pricing": 62, "cooking_time": "20 mins"},
            "2 Masala Dosa": {"others_pricing": 110, "our_pricing": 120, "cooking_time": "30 mins"},
            "2 Ghee Dosa": {"others_pricing": 75, "our_pricing": 125, "cooking_time": "20 mins"},
            "2 Paper Roast": {"others_pricing": 100, "our_pricing": 96, "cooking_time": "25 mins"},
            "Idli(2 pcs)": {"others_pricing": 45, "our_pricing": 48, "cooking_time": "15 mins"},
            "Podi Idli": {"others_pricing": 75, "our_pricing": 56, "cooking_time": "20 mins"},
            "Mini Idli": {"others_pricing": 110, "our_pricing": 62, "cooking_time": "15 mins"},
            "Idli Podimas": {"others_pricing": 90, "our_pricing": 100, "cooking_time": "25 mins"},

            # Chutneys and Sides
            "Tomato Chutney": {"others_pricing": 15, "our_pricing": 250, "cooking_time": "10 mins"},
            "Coconut Chutney": {"others_pricing": 15, "our_pricing": 135, "cooking_time": "10 mins"},
            "Sambar": {"others_pricing": 20, "our_pricing": 400, "cooking_time": "30 mins"},
            "Kurma": {"others_pricing": 20, "our_pricing": 65, "cooking_time": "25 mins"},

            # Beverages
            "Ginger Tea": {"others_pricing": 50, "our_pricing": 38, "cooking_time": "5 mins"},
            "Tea(250 ml)": {"others_pricing": 35, "our_pricing": 40, "cooking_time": "5 mins"},
            "Coffee": {"others_pricing": 45, "our_pricing": 60, "cooking_time": "5 mins"},
            "Boost": {"others_pricing": 50, "our_pricing": 65, "cooking_time": "5 mins"},
            "Horlicks": {"others_pricing": 50, "our_pricing": 65, "cooking_time": "5 mins"},
            "Black Coffee": {"others_pricing": 30, "our_pricing": 30, "cooking_time": "5 mins"},
            "Tea(125ml)": {"others_pricing": 27, "our_pricing": 22, "cooking_time": "5 mins"},
            "Tea(500ml)": {"others_pricing": 100, "our_pricing": 70, "cooking_time": "5 mins"},
            "Tea(750ml)": {"others_pricing": 100, "our_pricing": 105, "cooking_time": "5 mins"},
            "Milk": {"others_pricing": 100, "our_pricing": 32, "cooking_time": "2 mins"},

            # Rice Items
            "Chapathi": {"others_pricing": 50, "our_pricing": 40, "cooking_time": "15 mins"},
            "Kuli Paniyaram": {"others_pricing": 90, "our_pricing": 100, "cooking_time": "20 mins"},
            "Lemon Rice": {"others_pricing": 80, "our_pricing": 56, "cooking_time": "20 mins"},
            "Tomato Rice": {"others_pricing": 80, "our_pricing": 60, "cooking_time": "20 mins"},
            "Plain Rice": {"others_pricing": 70, "our_pricing": 50, "cooking_time": "15 mins"},
            "Curd Rice": {"others_pricing": 80, "our_pricing": 62, "cooking_time": "15 mins"},
            "cooked rice(InventorySide)": {"others_pricing": 300, "our_pricing": 280, "cooking_time": "20 mins"},

            # Additional Idli Varieties
            "Idly 5 pcs": {"others_pricing": 55, "our_pricing": 52, "cooking_time": "20 mins"},
            "Mini Podi Idli": {"others_pricing": 69, "our_pricing": 50, "cooking_time": "20 mins"},
            "Ghee Mini Idli with Sambhar (15 pcs)": {"others_pricing": 100, "our_pricing": 68, "cooking_time": "25 mins"},

            # Dosa Varieties
            "Onion Egg Dosa": {"others_pricing": 120, "our_pricing": 110, "cooking_time": "25 mins"},
            "Onion Dosa": {"others_pricing": 60, "our_pricing": 90, "cooking_time": "20 mins"},
            "Tomato Dosa": {"others_pricing": 60, "our_pricing": 60, "cooking_time": "20 mins"},
            "Egg Dosa": {"others_pricing": 80, "our_pricing": 85, "cooking_time": "20 mins"},
            "Masala Dosa": {"others_pricing": 110, "our_pricing": 115, "cooking_time": "25 mins"},
            "Paper Roast": {"others_pricing": 100, "our_pricing": 62, "cooking_time": "25 mins"},
            "Ghee Dosa": {"others_pricing": 100, "our_pricing": 90, "cooking_time": "20 mins"},
            "Onion Podi Dosa": {"others_pricing": 100, "our_pricing": 90, "cooking_time": "25 mins"},
            "Idli Podimas": {"others_pricing": 90, "our_pricing": 100, "cooking_time": "25 mins"},
            "Tomato Chutney": {"others_pricing": 15, "our_pricing": 250, "cooking_time": "15 mins"},
            "Coconut Chutney": {"others_pricing": 15, "our_pricing": 135, "cooking_time": "10 mins"},
            "Sambar": {"others_pricing": 20, "our_pricing": 400, "cooking_time": "40 mins"},
            "Kurma": {"others_pricing": 20, "our_pricing": 65, "cooking_time": "35 mins"},

            # Beverages
            "Ginger Tea": {"others_pricing": 50, "our_pricing": 38, "cooking_time": "10 mins"},
            "Tea(250 ml)": {"others_pricing": 35, "our_pricing": 40, "cooking_time": "5 mins"},
            "Coffee": {"others_pricing": 45, "our_pricing": 60, "cooking_time": "5 mins"},
            "Boost": {"others_pricing": 50, "our_pricing": 65, "cooking_time": "5 mins"},
            "Horlicks": {"others_pricing": 50, "our_pricing": 65, "cooking_time": "5 mins"},
            "Black Coffee": {"others_pricing": 30, "our_pricing": 30, "cooking_time": "5 mins"},
            "Tea(125ml)": {"others_pricing": 27, "our_pricing": 22, "cooking_time": "5 mins"},
            "Tea(500ml)": {"others_pricing": 100, "our_pricing": 70, "cooking_time": "10 mins"},
            "Tea(750ml)": {"others_pricing": 100, "our_pricing": 105, "cooking_time": "15 mins"},
            "Milk": {"others_pricing": 100, "our_pricing": 32, "cooking_time": "5 mins"},

            # Main Dishes
            "Chapathi": {"others_pricing": 50, "our_pricing": 40, "cooking_time": "20 mins"},
            "Kuli Paniyaram": {"others_pricing": 90, "our_pricing": 100, "cooking_time": "20 mins"},
            "Lemon Rice": {"others_pricing": 80, "our_pricing": 56, "cooking_time": "15 mins"},
            "Tomato Rice": {"others_pricing": 80, "our_pricing": 60, "cooking_time": "20 mins"},
            "Plain Rice": {"others_pricing": 70, "our_pricing": 50, "cooking_time": "15 mins"},
            "Curd Rice": {"others_pricing": 80, "our_pricing": 62, "cooking_time": "10 mins"},
            "cooked rice(InventorySide)": {"others_pricing": 300, "our_pricing": 280, "cooking_time": "30 mins"},

            # Dosa Varieties
            "Masala Dosa": {"others_pricing": 110, "our_pricing": 115, "cooking_time": "30 mins"},
            "Paper Roast": {"others_pricing": 100, "our_pricing": 62, "cooking_time": "25 mins"},
            "Ghee Dosa": {"others_pricing": 100, "our_pricing": 90, "cooking_time": "20 mins"},
            "Onion Egg Dosa": {"others_pricing": 120, "our_pricing": 110, "cooking_time": "20 mins"},
            "Onion Dosa": {"others_pricing": 60, "our_pricing": 90, "cooking_time": "15 mins"},
            "Tomato Dosa": {"others_pricing": 60, "our_pricing": 60, "cooking_time": "15 mins"},
            "Egg Dosa": {"others_pricing": 80, "our_pricing": 85, "cooking_time": "20 mins"},
            "Onion Podi Dosa": {"others_pricing": 100, "our_pricing": 90, "cooking_time": "18 mins"},

            # Idli Varieties
            "Idly 5 pcs": {"others_pricing": 55, "our_pricing": 52, "cooking_time": "15 mins"},
            "Mini Podi Idli": {"others_pricing": 69, "our_pricing": 50, "cooking_time": "15 mins"},
            "Ghee Mini Idli with Sambhar (15 pcs)": {"others_pricing": 100, "our_pricing": 68, "cooking_time": "20 mins"},

            # Special Items
            "Chappathi and Channa (2 pcs)": {"others_pricing": 90, "our_pricing": 105, "cooking_time": "25 mins"},
            "Boiled Egg": {"others_pricing": 20, "our_pricing": 22, "cooking_time": "10 mins"},

            # Fish Items
            "Fish Kolambu(Parai Fish)": {"others_pricing": 900, "our_pricing": 750, "cooking_time": "30 mins"},
            "Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 110, "our_pricing": 73, "cooking_time": "25 mins"},
            "2 Masala Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 75, "our_pricing": 152, "cooking_time": "35 mins"},
            "2 Ghee Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 100, "our_pricing": 94, "cooking_time": "25 mins"},
            "2 Paper Roast with Fish Kolambu(Parai Fish)": {"others_pricing": 45, "our_pricing": 75, "cooking_time": "30 mins"},
            "Idli(2 pcs) with Fish Kolambu(Parai Fish)": {"others_pricing": 110, "our_pricing": 190, "cooking_time": "20 mins"},
            "Mini Idli with Fish Kolambu(Parai Fish)": {"others_pricing": 50, "our_pricing": 90, "cooking_time": "20 mins"},
            "Chapathi with Fish Kolambu(Parai Fish)": {"others_pricing": 90, "our_pricing": 80, "cooking_time": "25 mins"},
            "Kuli Paniyaram with Fish Kolambu(Parai Fish)": {"others_pricing": 70, "our_pricing": 70, "cooking_time": "25 mins"},
            "Onion Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 60, "our_pricing": 102, "cooking_time": "20 mins"},
            "Tomato Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 80, "our_pricing": 125, "cooking_time": "20 mins"},
            "Egg Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 300, "our_pricing": 182, "cooking_time": "25 mins"},
            "Plain rice with Fish Kolambu(Parai Fish)": {"others_pricing": 110, "our_pricing": 125, "cooking_time": "20 mins"},
            "Masala Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 100, "our_pricing": 125, "cooking_time": "35 mins"},
            "Paper Roast with Fish Kolambu(Parai Fish)": {"others_pricing": 100, "our_pricing": 125, "cooking_time": "30 mins"},
            "Ghee Dosa with Fish Kolambu(Parai Fish)": {"others_pricing": 100, "our_pricing": 125, "cooking_time": "25 mins"},

            # Uttapam Varieties
            "Carrot and Coriander Uthapam": {"others_pricing": 80, "our_pricing": 125, "cooking_time": "18 mins"},
            "Onion Uttapam": {"others_pricing": 100, "our_pricing": 90, "cooking_time": "16 mins"},
            "Tomato Uttapam": {"others_pricing": 100, "our_pricing": 80, "cooking_time": "17 mins"},
            "Plain Uttapam": {"others_pricing": 100, "our_pricing": 70, "cooking_time": "18 mins"},

            # Egg Items
            "Double Omelette": {"others_pricing": 80, "our_pricing": 58, "cooking_time": "10 mins"},
            "Onion bread omellete": {"others_pricing": 120, "our_pricing": 102, "cooking_time": "12 mins"},
            "Plain bread omellete": {"others_pricing": 100, "our_pricing": 92, "cooking_time": "10 mins"},

            # Chicken Items
            "Chicken Gravy": {"others_pricing": 170, "our_pricing": 100, "cooking_time": "35 mins"},
            "Chicken Gravy(250G)": {"others_pricing": 120, "our_pricing": 190, "cooking_time": "35 mins"},
        }

    def init_pricing_data(self):
        """Initialize pricing data structure"""
        if 'pricing' not in self.data:
            # Create default pricing data structure
            pricing_columns = [
                'recipe_id', 'recipe_name', 'cost_of_making', 'others_pricing',
                'our_pricing', 'profit', 'profit_percentage', 'pkg_cost',
                'other_charges', 'electricity_cost', 'gas_cost', 'gst_amount'
            ]
            self.data['pricing'] = pd.DataFrame(columns=pricing_columns)



    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("Pricing Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search functionality
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("font-weight: 500; color: #374151;")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search recipes...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background: white;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tables)
        search_layout.addWidget(self.search_input)

        clear_search_btn = QPushButton("✕")
        clear_search_btn.setFixedSize(32, 32)
        clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)

        header_layout.addLayout(search_layout)

        # Action buttons
        check_missing_btn = QPushButton("🔍 Check Missing Items")
        check_missing_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        check_missing_btn.clicked.connect(self.check_missing_items_manual)
        header_layout.addWidget(check_missing_btn)

        # Debug button for testing missing items logic
        debug_missing_btn = QPushButton("🐛 Debug Missing Items")
        debug_missing_btn.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e8590c;
            }
        """)
        debug_missing_btn.clicked.connect(self.debug_missing_items_logic)
        header_layout.addWidget(debug_missing_btn)

        calculate_all_btn = QPushButton("Calculate All Prices")
        calculate_all_btn.setStyleSheet("background-color: #10b981; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 500;")
        calculate_all_btn.clicked.connect(self.calculate_all_prices)
        header_layout.addWidget(calculate_all_btn)

        export_pricing_btn = QPushButton("Export Pricing Report")
        export_pricing_btn.setStyleSheet("background-color: #6c757d; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 500;")
        export_pricing_btn.clicked.connect(self.export_pricing_report)
        header_layout.addWidget(export_pricing_btn)

        # Note: Bulk pricing editor moved to Shopping tab

        cost_analysis_btn = QPushButton("🔬 Advanced Analysis")
        cost_analysis_btn.setStyleSheet("background-color: #8b5cf6; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 500;")
        cost_analysis_btn.clicked.connect(self.open_advanced_analysis)
        header_layout.addWidget(cost_analysis_btn)
        
        layout.addLayout(header_layout)
        
        # Pricing overview cards
        self.create_pricing_overview(layout)
        
        # Main content tabs
        self.create_tabs_section(layout)
    
    def create_pricing_overview(self, parent_layout):
        """Create pricing overview cards"""
        overview_frame = QFrame()
        overview_frame.setStyleSheet("background: transparent; border: none;")
        
        overview_layout = QGridLayout(overview_frame)
        overview_layout.setSpacing(16)
        
        # Initialize overview cards
        self.avg_cost_card = PricingCard("Average Cost", "Rs.0", "Per Dish", "#ef4444")
        self.avg_selling_price_card = PricingCard("Average Selling Price", "Rs.0", "Per Dish", "#10b981")
        self.avg_profit_card = PricingCard("Average Profit", "Rs.0", "Per Dish", "#3b82f6")
        self.avg_margin_card = PricingCard("Average Margin", "0%", "Profit Percentage", "#8b5cf6")
        
        overview_layout.addWidget(self.avg_cost_card, 0, 0)
        overview_layout.addWidget(self.avg_selling_price_card, 0, 1)
        overview_layout.addWidget(self.avg_profit_card, 0, 2)
        overview_layout.addWidget(self.avg_margin_card, 0, 3)
        
        parent_layout.addWidget(overview_frame)
    
    def create_tabs_section(self, parent_layout):
        """Create tabbed interface for different pricing views"""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
        """)
        
        # Cost Analysis Tab
        self.create_cost_analysis_tab()
        
        # Pricing Strategy Tab
        self.create_pricing_strategy_tab()
        
        # Profit Analysis Tab
        self.create_profit_analysis_tab()
        
        # Discount Analysis Tab
        self.create_discount_analysis_tab()

        # Recipe Scaling Tab
        self.create_recipe_scaling_tab()

        # Enhanced Cost Breakdown Tab
        self.create_enhanced_breakdown_tab()

        # Order Management Tab
        self.create_order_management_tab()

        parent_layout.addWidget(self.tabs)

    def filter_tables(self):
        """Filter all tables based on search input"""
        search_text = self.search_input.text().lower().strip()

        # Get the currently active tab
        current_tab_index = self.tabs.currentIndex()

        # Filter only the table in the current tab for better performance
        if current_tab_index == 0:  # Cost Analysis tab
            if hasattr(self, 'cost_table') and self.cost_table is not None:
                self.filter_table(self.cost_table, search_text, 0)
        elif current_tab_index == 1:  # Pricing Strategy tab
            if hasattr(self, 'pricing_table') and self.pricing_table is not None:
                self.filter_table(self.pricing_table, search_text, 0)
        elif current_tab_index == 2:  # Profit Analysis tab
            if hasattr(self, 'profit_table') and self.profit_table is not None:
                self.filter_table(self.profit_table, search_text, 0)
        elif current_tab_index == 3:  # Discount Analysis tab
            if hasattr(self, 'discount_table') and self.discount_table is not None:
                self.filter_table(self.discount_table, search_text, 0)
        elif current_tab_index == 4:  # Recipe Scaling tab
            if hasattr(self, 'scaling_table') and self.scaling_table is not None:
                self.filter_table(self.scaling_table, search_text, 0)

        # Also filter all tables if search is cleared
        if search_text == "":
            tables = ['cost_table', 'pricing_table', 'profit_table', 'discount_table', 'scaling_table']
            for table_name in tables:
                if hasattr(self, table_name):
                    table = getattr(self, table_name)
                    if table is not None:
                        self.filter_table(table, search_text, 0)

    def filter_table(self, table, search_text, search_column):
        """Filter a specific table based on search text"""
        try:
            if table is None or table.rowCount() == 0:
                self.logger.debug("Table is None or empty, skipping filter")
                return

            rows_shown = 0
            rows_hidden = 0

            for row in range(table.rowCount()):
                item = table.item(row, search_column)
                if item and item.text():
                    recipe_name = item.text().lower().strip()
                    search_lower = search_text.lower().strip()

                    # Show row if search text is found in recipe name or if search is empty
                    should_show = search_text == "" or search_lower in recipe_name
                    table.setRowHidden(row, not should_show)

                    if should_show:
                        rows_shown += 1
                    else:
                        rows_hidden += 1
                else:
                    # Hide rows with empty recipe names when searching
                    table.setRowHidden(row, search_text != "")
                    if search_text != "":
                        rows_hidden += 1
                    else:
                        rows_shown += 1

            self.logger.info(f"Search '{search_text}': {rows_shown} rows shown, {rows_hidden} rows hidden")

        except Exception as e:
            self.logger.error(f"Error filtering table: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def clear_search(self):
        """Clear search input and show all rows"""
        self.search_input.clear()
        self.filter_tables()

    def create_cost_analysis_tab(self):
        """Create cost analysis tab with actual pricing formulas"""
        cost_widget = QWidget()
        layout = QVBoxLayout(cost_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Cost Analysis Table - Updated columns based on user requirements
        self.cost_table = QTableWidget()
        self.cost_table.setColumnCount(11)
        self.cost_table.setHorizontalHeaderLabels([
            "Recipe Name", "Cost of Making", "Others Pricing", "Our Pricing",
            "Profit", "Current Profit %", "PKG Cost", "Other Charges",
            "Electricity Cost", "Gas Cost", "GST+SGST Amount"
        ])

        # Simple column resizing for pricing cost table
        header = self.cost_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.cost_table.setColumnWidth(0, 180)  # Recipe Name
        self.cost_table.setColumnWidth(1, 120)  # Cost of Making
        self.cost_table.setColumnWidth(2, 120)  # Others Pricing
        self.cost_table.setColumnWidth(3, 120)  # Our Pricing
        self.cost_table.setColumnWidth(4, 100)  # Profit
        self.cost_table.setColumnWidth(5, 120)  # Current Profit %
        self.cost_table.setColumnWidth(6, 100)  # PKG Cost
        self.cost_table.setColumnWidth(7, 120)  # Other Charges
        self.cost_table.setColumnWidth(8, 120)  # Electricity Cost
        self.cost_table.setColumnWidth(9, 100)  # Gas Cost
        self.cost_table.setColumnWidth(10, 140) # GST+SGST Amount
        
        # Modern table styling
        self.cost_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #f1f5f9;
                selection-background-color: #dbeafe;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #374151;
            }
        """)
        
        # Set column widths
        header = self.cost_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Recipe Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Ingredient Cost
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Making Cost
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Packaging Cost
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Electricity Cost
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Gas Cost
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Other Charges
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Total Cost
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # GST Amount
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Final Cost
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents) # Overhead %

        # Enable right-click context menu for editable columns
        self.cost_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cost_table.customContextMenuRequested.connect(self.show_cost_table_context_menu)

        # FIXED: Ensure manual column resizing is preserved for Cost Analysis table
        print("🔧 Ensuring Cost Analysis table column resizing is preserved...")
        cost_header = self.cost_table.horizontalHeader()

        # Verify ALL columns are still Interactive mode (they should be from line 642)
        for col in range(11):
            current_mode = cost_header.sectionResizeMode(col)
            if current_mode != QHeaderView.Interactive:
                cost_header.setSectionResizeMode(col, QHeaderView.Interactive)
                print(f"   Cost Column {col}: Fixed to Interactive")
            else:
                print(f"   Cost Column {col}: Interactive (OK)")

        print("✅ Cost Analysis table column resizing preserved!")

        layout.addWidget(self.cost_table)
        
        # Add Recipe Pricing Button
        add_pricing_btn = QPushButton("Add Recipe Pricing")
        add_pricing_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        add_pricing_btn.clicked.connect(self.add_recipe_pricing)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_pricing_btn)
        layout.addLayout(button_layout)
        
        self.tabs.addTab(cost_widget, "Cost Analysis")
    
    def create_pricing_strategy_tab(self):
        """Create pricing strategy tab"""
        pricing_widget = QWidget()
        layout = QVBoxLayout(pricing_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Pricing Strategy Table
        self.pricing_table = QTableWidget()
        self.pricing_table.setColumnCount(7)
        self.pricing_table.setHorizontalHeaderLabels([
            "Recipe Name", "Total Cost", "Others Pricing", "Margin Value",
            "Our Pricing", "Selling Price", "Profit"
        ])

        # Apply modern styling
        self.pricing_table.setStyleSheet(self.cost_table.styleSheet())

        # Simple column resizing for pricing strategy table
        header = self.pricing_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.pricing_table.setColumnWidth(0, 180)  # Recipe Name
        self.pricing_table.setColumnWidth(1, 120)  # Total Cost
        self.pricing_table.setColumnWidth(2, 120)  # Others Pricing
        self.pricing_table.setColumnWidth(3, 120)  # Margin Value
        self.pricing_table.setColumnWidth(4, 120)  # Our Pricing
        self.pricing_table.setColumnWidth(5, 120)  # Selling Price
        self.pricing_table.setColumnWidth(6, 100)  # Profit

        # Enable right-click context menu for editable columns
        self.pricing_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pricing_table.customContextMenuRequested.connect(self.show_pricing_table_context_menu)

        # FIXED: Ensure manual column resizing is preserved for Pricing Strategy table
        print("🔧 Ensuring Pricing Strategy table column resizing is preserved...")
        pricing_header = self.pricing_table.horizontalHeader()

        # Verify ALL columns are still Interactive mode (they should be from line 777)
        for col in range(7):
            current_mode = pricing_header.sectionResizeMode(col)
            if current_mode != QHeaderView.Interactive:
                pricing_header.setSectionResizeMode(col, QHeaderView.Interactive)
                print(f"   Pricing Column {col}: Fixed to Interactive")
            else:
                print(f"   Pricing Column {col}: Interactive (OK)")

        print("✅ Pricing Strategy table column resizing preserved!")

        layout.addWidget(self.pricing_table)
        
        self.tabs.addTab(pricing_widget, "Pricing Strategy")
    
    def create_profit_analysis_tab(self):
        """Create profit analysis tab"""
        profit_widget = QWidget()
        layout = QVBoxLayout(profit_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Profit Analysis Table
        self.profit_table = QTableWidget()
        self.profit_table.setColumnCount(6)
        self.profit_table.setHorizontalHeaderLabels([
            "Recipe Name", "Selling Price", "Total Cost", "Profit",
            "Profit %", "Status"
        ])

        # FIXED: Enable manual column resizing for Profit Analysis table
        print("🔧 Setting up Profit Analysis table column resizing...")
        profit_header = self.profit_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        profit_columns = ["Recipe Name", "Selling Price", "Total Cost", "Profit", "Profit %", "Status"]
        for col in range(6):
            profit_header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Profit Column {col} ({profit_columns[col]}): Interactive")

        # Set default column widths
        profit_default_widths = {
            0: 180,  # Recipe Name
            1: 120,  # Selling Price
            2: 120,  # Total Cost
            3: 100,  # Profit
            4: 100,  # Profit %
            5: 100   # Status
        }
        for col, width in profit_default_widths.items():
            self.profit_table.setColumnWidth(col, width)
            print(f"   Profit Column {col}: {width}px")

        # Basic header configuration
        profit_header.setStretchLastSection(False)
        profit_header.setMinimumSectionSize(80)
        print("✅ Profit Analysis table column resizing enabled!")

        # Apply modern styling
        self.profit_table.setStyleSheet(self.cost_table.styleSheet())

        # Enable right-click context menu for editable columns
        self.profit_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.profit_table.customContextMenuRequested.connect(self.show_profit_table_context_menu)

        # FIXED: Ensure manual column resizing is preserved for Profit Analysis table
        print("🔧 Ensuring Profit Analysis table column resizing is preserved...")
        profit_header = self.profit_table.horizontalHeader()

        # Verify ALL columns are still Interactive mode (they should be from the fix above)
        for col in range(6):
            current_mode = profit_header.sectionResizeMode(col)
            if current_mode != QHeaderView.Interactive:
                profit_header.setSectionResizeMode(col, QHeaderView.Interactive)
                print(f"   Profit Column {col}: Fixed to Interactive")
            else:
                print(f"   Profit Column {col}: Interactive (OK)")

        print("✅ Profit Analysis table column resizing preserved!")

        layout.addWidget(self.profit_table)
        
        self.tabs.addTab(profit_widget, "Profit Analysis")
    
    def create_discount_analysis_tab(self):
        """Create discount analysis tab"""
        discount_widget = QWidget()
        layout = QVBoxLayout(discount_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Discount Analysis Table
        self.discount_table = QTableWidget()
        self.discount_table.setColumnCount(8)
        self.discount_table.setHorizontalHeaderLabels([
            "Recipe Name", "Original Price", "10% Discount", "15% Discount", 
            "25% Discount", "30% Discount", "40% Discount", "Min Profitable"
        ])
        
        # Apply modern styling
        self.discount_table.setStyleSheet(self.cost_table.styleSheet())
        
        # FIXED: Enable manual column resizing for Discount Analysis table
        print("🔧 Setting up Discount Analysis table column resizing...")
        discount_header = self.discount_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        discount_columns = ["Recipe Name", "Original Price", "10% Discount", "15% Discount",
                           "25% Discount", "30% Discount", "40% Discount", "Min Profitable"]
        for col in range(8):
            discount_header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Discount Column {col} ({discount_columns[col]}): Interactive")

        # Set default column widths
        discount_default_widths = {
            0: 180,  # Recipe Name
            1: 120,  # Original Price
            2: 120,  # 10% Discount
            3: 120,  # 15% Discount
            4: 120,  # 25% Discount
            5: 120,  # 30% Discount
            6: 120,  # 40% Discount
            7: 130   # Min Profitable
        }
        for col, width in discount_default_widths.items():
            self.discount_table.setColumnWidth(col, width)
            print(f"   Discount Column {col}: {width}px")

        # Basic header configuration
        discount_header.setStretchLastSection(False)
        discount_header.setMinimumSectionSize(80)
        print("✅ Discount Analysis table column resizing enabled!")

        layout.addWidget(self.discount_table)
        
        self.tabs.addTab(discount_widget, "Discount Analysis")

    def create_recipe_scaling_tab(self):
        """Create recipe scaling tab for bulk cost analysis"""
        scaling_widget = QWidget()
        layout = QVBoxLayout(scaling_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Scaling controls
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Box)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)

        # Scale factor input
        scale_label = QLabel("Scale Factor:")
        scale_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(scale_label)

        self.scale_factor_spin = QSpinBox()
        self.scale_factor_spin.setMinimum(1)
        self.scale_factor_spin.setMaximum(100)
        self.scale_factor_spin.setValue(10)
        self.scale_factor_spin.setSuffix("x")
        controls_layout.addWidget(self.scale_factor_spin)

        controls_layout.addStretch()

        # Calculate button
        calculate_btn = QPushButton("Calculate Scaled Costs")
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        calculate_btn.clicked.connect(self.calculate_scaled_costs)
        controls_layout.addWidget(calculate_btn)

        layout.addWidget(controls_frame)

        # Scaling results table
        self.scaling_table = QTableWidget()
        self.scaling_table.setColumnCount(8)
        self.scaling_table.setHorizontalHeaderLabels([
            "Recipe Name", "Single Cost", "Scaled Quantity", "Scaled Ingredient Cost",
            "Scaled Total Cost", "Cost per Unit", "Profit Margin", "Bulk Savings"
        ])

        # Simple column resizing for scaling table
        header = self.scaling_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.scaling_table.setColumnWidth(0, 180)  # Recipe Name
        self.scaling_table.setColumnWidth(1, 120)  # Single Cost
        self.scaling_table.setColumnWidth(2, 120)  # Scaled Quantity
        self.scaling_table.setColumnWidth(3, 140)  # Scaled Ingredient Cost
        self.scaling_table.setColumnWidth(4, 140)  # Scaled Total Cost
        self.scaling_table.setColumnWidth(5, 120)  # Cost per Unit
        self.scaling_table.setColumnWidth(6, 120)  # Profit Margin
        self.scaling_table.setColumnWidth(7, 120)  # Bulk Savings

        # Set table properties
        self.scaling_table.setAlternatingRowColors(True)
        self.scaling_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.scaling_table)

        self.tabs.addTab(scaling_widget, "Recipe Scaling")

    def calculate_scaled_costs(self):
        """Calculate costs for scaled recipe quantities"""
        try:
            scale_factor = self.scale_factor_spin.value()

            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.scaling_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate single recipe costs
                single_ingredient_cost = self.calculate_ingredient_cost(recipe_id)
                single_making_cost = single_ingredient_cost * 0.2
                single_packaging_cost = self.calculate_actual_packaging_cost(recipe_name)
                single_electricity_cost = self.calculate_electricity_cost(recipe.get('cook_time', 30), recipe_name=recipe_name)
                single_gas_cost = self.calculate_gas_cost(recipe_data=recipe)
                single_other_charges = 2.0
                single_total_cost = (single_ingredient_cost + single_making_cost +
                                   single_packaging_cost + single_electricity_cost +
                                   single_gas_cost + single_other_charges)

                # Calculate scaled costs
                scaled_ingredient_cost = single_ingredient_cost * scale_factor
                scaled_making_cost = single_making_cost * scale_factor

                # Bulk discounts for utilities (economies of scale)
                scaled_electricity_cost = single_electricity_cost * scale_factor * 0.85  # 15% savings
                scaled_gas_cost = single_gas_cost * scale_factor * 0.85  # 15% savings

                # Bulk packaging savings
                scaled_packaging_cost = single_packaging_cost * scale_factor * 0.75  # 25% savings
                scaled_other_charges = single_other_charges * scale_factor * 0.9  # 10% savings

                scaled_total_cost = (scaled_ingredient_cost + scaled_making_cost +
                                   scaled_packaging_cost + scaled_electricity_cost +
                                   scaled_gas_cost + scaled_other_charges)

                # Calculate metrics
                cost_per_unit = scaled_total_cost / scale_factor
                bulk_savings_per_unit = single_total_cost - cost_per_unit
                bulk_savings_percentage = (bulk_savings_per_unit / single_total_cost) * 100

                # Profit margin calculation (assuming 40% markup)
                selling_price_per_unit = cost_per_unit * 1.4
                profit_per_unit = selling_price_per_unit - cost_per_unit
                profit_margin = (profit_per_unit / selling_price_per_unit) * 100

                # Populate table
                self.scaling_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.scaling_table.setItem(row, 1, QTableWidgetItem(f"Rs.{single_total_cost:.2f}"))
                self.scaling_table.setItem(row, 2, QTableWidgetItem(f"{scale_factor}x"))
                self.scaling_table.setItem(row, 3, QTableWidgetItem(f"Rs.{scaled_ingredient_cost:.2f}"))
                self.scaling_table.setItem(row, 4, QTableWidgetItem(f"Rs.{scaled_total_cost:.2f}"))
                self.scaling_table.setItem(row, 5, QTableWidgetItem(f"Rs.{cost_per_unit:.2f}"))
                self.scaling_table.setItem(row, 6, QTableWidgetItem(f"{profit_margin:.1f}%"))

                # Color code savings
                savings_item = QTableWidgetItem(f"Rs.{bulk_savings_per_unit:.2f} ({bulk_savings_percentage:.1f}%)")
                if bulk_savings_percentage > 15:
                    savings_item.setForeground(QColor("#27ae60"))  # Green for good savings
                elif bulk_savings_percentage > 10:
                    savings_item.setForeground(QColor("#f39c12"))  # Orange for moderate savings
                else:
                    savings_item.setForeground(QColor("#e74c3c"))  # Red for low savings

                self.scaling_table.setItem(row, 7, savings_item)

        except Exception as e:
            self.logger.error(f"Error calculating scaled costs: {e}")

    def create_enhanced_breakdown_tab(self):
        """Create enhanced cost breakdown tab"""
        try:
            from modules.enhanced_cost_breakdown import EnhancedCostBreakdownPanel

            breakdown_widget = EnhancedCostBreakdownPanel(self.data, self)
            breakdown_widget.cost_updated.connect(self.on_cost_breakdown_updated)

            self.tabs.addTab(breakdown_widget, "📊 Enhanced Breakdown")

        except Exception as e:
            self.logger.error(f"Error creating enhanced breakdown tab: {e}")
            # Create placeholder tab
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_label = QLabel("Enhanced breakdown not available.\nPlease check module installation.")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("color: #64748b; font-size: 16px;")
            placeholder_layout.addWidget(placeholder_label)

            self.tabs.addTab(placeholder, "📊 Enhanced Breakdown")

    def create_order_management_tab(self):
        """Create order management tab"""
        try:
            from modules.order_management import OrderManagementWidget

            order_widget = OrderManagementWidget(self.data, self)
            order_widget.order_added.connect(self.on_order_added)
            order_widget.order_updated.connect(self.on_order_updated)

            self.tabs.addTab(order_widget, "📋 Order Management")

        except Exception as e:
            self.logger.error(f"Error creating order management tab: {e}")
            # Create placeholder tab
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_label = QLabel("Order management not available.\nPlease check module installation.")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("color: #64748b; font-size: 16px;")
            placeholder_layout.addWidget(placeholder_label)

            self.tabs.addTab(placeholder, "📋 Order Management")

    def on_order_added(self, order_data):
        """Handle new order added"""
        try:
            self.logger.info(f"New order added: {order_data['order_id']}")
            # Update pricing overview if needed
            self.update_pricing_overview()
        except Exception as e:
            self.logger.error(f"Error handling order added: {e}")

    def on_order_updated(self, order_data):
        """Handle order updated"""
        try:
            self.logger.info(f"Order updated: {order_data['order_id']}")
            # Update pricing overview if needed
            self.update_pricing_overview()
        except Exception as e:
            self.logger.error(f"Error handling order updated: {e}")

    def on_cost_breakdown_updated(self, recipe_id, new_cost):
        """Handle cost breakdown updates"""
        try:
            self.logger.info(f"Cost updated for recipe {recipe_id}: Rs.{new_cost:.2f}")
            # Refresh pricing data
            self.load_data()

        except Exception as e:
            self.logger.error(f"Error handling cost breakdown update: {e}")

    def load_data_lazy_no_missing_check(self):
        """Load data lazily without automatically checking missing items"""
        if not self.data_loaded:
            try:
                self.logger.info("Loading pricing data lazily (no auto-check)...")
                self.load_data_no_missing_check()
                self.data_loaded = True
                self.logger.info("Pricing data loaded successfully")
            except Exception as e:
                self.logger.error(f"Error in lazy data loading: {e}")

    def load_data_lazy(self):
        """Load data lazily to prevent initial lag"""
        if not self.data_loaded:
            try:
                self.logger.info("Loading pricing data lazily...")
                self.load_data()
                self.data_loaded = True
                self.logger.info("Pricing data loaded successfully")
            except Exception as e:
                self.logger.error(f"Error in lazy data loading: {e}")

    def load_data_no_missing_check(self):
        """Load and display pricing data without checking missing items"""
        try:
            self.populate_cost_analysis_no_missing_check()
            self.populate_pricing_strategy_no_missing_check()
            self.populate_profit_analysis_no_missing_check()
            self.populate_discount_analysis_no_missing_check()
            self.update_overview_cards()
        except Exception as e:
            self.logger.error(f"Error loading pricing data: {e}")
            notify_error("Error", f"Failed to load pricing data: {str(e)}", parent=self)

    def load_data(self):
        """Load and display pricing data"""
        try:
            # First reload pricing data from CSV to get latest updates
            self.reload_pricing_data_from_csv()

            self.populate_cost_analysis()
            self.populate_pricing_strategy()
            self.populate_profit_analysis()
            self.populate_discount_analysis()
            self.update_overview_cards()
        except Exception as e:
            self.logger.error(f"Error loading pricing data: {e}")
            notify_error("Error", f"Failed to load pricing data: {str(e)}", parent=self)
    
    def populate_cost_analysis(self):
        """Populate cost analysis table"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return
            
            recipes_df = self.data['recipes']
            self.cost_table.setRowCount(len(recipes_df))
            
            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)
                
                # Calculate ingredient cost directly
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)
                # Skip if ingredient cost is None (missing ingredients)
                if ingredient_cost is None:
                    # Show incomplete pricing
                    self.cost_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    self.cost_table.setItem(row, 1, QTableWidgetItem("❌ Missing Ingredients"))
                    for col in range(2, 11):
                        self.cost_table.setItem(row, col, QTableWidgetItem("N/A"))
                    continue

                making_cost = ingredient_cost  # Making cost equals ingredient cost

                # Calculate actual packaging cost from packing materials
                packaging_cost = self.calculate_actual_packaging_cost(recipe_name)

                # Calculate electricity and gas costs based on preparation time
                cook_time = recipe.get('cook_time', 30)  # Default 30 minutes
                recipe_name = recipe.get('recipe_name', '')
                electricity_cost = self.calculate_electricity_cost(cook_time, recipe_name=recipe_name)
                gas_cost = self.calculate_gas_cost(recipe_data=recipe)

                other_charges = 2.0  # Default other charges
                overhead_percentage = 15.0  # 15% overhead

                subtotal = ingredient_cost + making_cost + packaging_cost + electricity_cost + gas_cost + other_charges
                overhead_cost = subtotal * (overhead_percentage / 100)
                total_cost = subtotal + overhead_cost

                gst_amount = total_cost * 0.18  # 18% GST
                final_cost = total_cost + gst_amount
                
                # Populate table
                self.cost_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.cost_table.setItem(row, 1, QTableWidgetItem(f"Rs.{ingredient_cost:.2f}"))
                self.cost_table.setItem(row, 2, QTableWidgetItem(f"Rs.{making_cost:.2f}"))
                self.cost_table.setItem(row, 3, QTableWidgetItem(f"Rs.{packaging_cost:.2f}"))
                self.cost_table.setItem(row, 4, QTableWidgetItem(f"Rs.{electricity_cost:.2f}"))
                self.cost_table.setItem(row, 5, QTableWidgetItem(f"Rs.{gas_cost:.2f}"))
                self.cost_table.setItem(row, 6, QTableWidgetItem(f"Rs.{other_charges:.2f}"))
                self.cost_table.setItem(row, 7, QTableWidgetItem(f"Rs.{total_cost:.2f}"))
                self.cost_table.setItem(row, 8, QTableWidgetItem(f"Rs.{gst_amount:.2f}"))
                self.cost_table.setItem(row, 9, QTableWidgetItem(f"Rs.{final_cost:.2f}"))
                self.cost_table.setItem(row, 10, QTableWidgetItem(f"{overhead_percentage:.1f}%"))
                
        except Exception as e:
            self.logger.error(f"Error populating cost analysis: {e}")

    def populate_cost_analysis_no_missing_check(self):
        """Populate cost analysis table with actual pricing formulas using application data"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.cost_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate cost of making using application's ingredient data
                cost_of_making = self.calculate_ingredient_cost(recipe_id)

                # Get pricing data from Excel reference (if available)
                excel_pricing = self.recipe_pricing_data.get(recipe_name, {})
                others_pricing = excel_pricing.get('others_pricing')
                our_pricing = excel_pricing.get('our_pricing')

                # Calculate standard charges
                pkg_cost = self.calculate_actual_packaging_cost(recipe_name)

                # Calculate electricity cost using proper method with cooking time
                cook_time = recipe.get('cook_time', 30)  # Default 30 minutes if not specified
                electricity_cost = self.calculate_electricity_cost(cook_time, recipe_name=recipe_name)

                gas_cost = self.calculate_gas_cost(recipe_data=recipe)
                other_charges = 2.0  # Standard 2 rupees as per user requirement

                # Calculate GST+SGST using configurable rates
                gst_sgst_rates = self.get_tax_rates()
                if cost_of_making is not None and cost_of_making > 0:
                    total_base_cost = cost_of_making + pkg_cost + electricity_cost + gas_cost + other_charges
                    gst_amount = total_base_cost * (gst_sgst_rates['gst_rate'] + gst_sgst_rates['sgst_rate'])
                else:
                    total_base_cost = 0
                    gst_amount = 0

                # Populate table
                self.cost_table.setItem(row, 0, QTableWidgetItem(recipe_name))

                # Cost of Making - calculated from actual ingredients
                if cost_of_making is not None and cost_of_making > 0:
                    self.cost_table.setItem(row, 1, QTableWidgetItem(f"Rs.{cost_of_making:.2f}"))

                    # Calculate profit if we have our pricing
                    if our_pricing is not None:
                        total_cost_with_charges = total_base_cost + gst_amount
                        profit = our_pricing - total_cost_with_charges
                        profit_percentage = (profit / total_cost_with_charges) * 100 if total_cost_with_charges > 0 else 0

                        # Others Pricing
                        if others_pricing is not None:
                            self.cost_table.setItem(row, 2, QTableWidgetItem(f"Rs.{others_pricing:.2f}"))
                        else:
                            self.cost_table.setItem(row, 2, QTableWidgetItem("N/A"))

                        # Our Pricing
                        self.cost_table.setItem(row, 3, QTableWidgetItem(f"Rs.{our_pricing:.2f}"))

                        # Profit
                        profit_item = QTableWidgetItem(f"Rs.{profit:.2f}")
                        if profit > 0:
                            profit_item.setForeground(QColor("#10b981"))  # Green
                        else:
                            profit_item.setForeground(QColor("#ef4444"))  # Red
                        self.cost_table.setItem(row, 4, profit_item)

                        # Profit Percentage
                        percentage_item = QTableWidgetItem(f"{profit_percentage:.1f}%")
                        if profit_percentage > 100:
                            percentage_item.setForeground(QColor("#10b981"))  # Green
                        elif profit_percentage > 50:
                            percentage_item.setForeground(QColor("#3b82f6"))  # Blue
                        elif profit_percentage > 0:
                            percentage_item.setForeground(QColor("#f59e0b"))  # Orange
                        else:
                            percentage_item.setForeground(QColor("#ef4444"))  # Red
                        self.cost_table.setItem(row, 5, percentage_item)
                    else:
                        # No pricing data available
                        for col in range(2, 6):
                            self.cost_table.setItem(row, col, QTableWidgetItem("N/A"))
                else:
                    # No ingredient cost data available
                    for col in range(1, 6):
                        self.cost_table.setItem(row, col, QTableWidgetItem("N/A"))

                # Set standard charges columns with actual values
                self.cost_table.setItem(row, 6, QTableWidgetItem(f"Rs.{pkg_cost:.2f}"))  # PKG Cost
                self.cost_table.setItem(row, 7, QTableWidgetItem(f"Rs.{other_charges:.2f}"))  # Other Charges
                self.cost_table.setItem(row, 8, QTableWidgetItem(f"Rs.{electricity_cost:.2f}"))  # Electricity Cost
                self.cost_table.setItem(row, 9, QTableWidgetItem(f"Rs.{gas_cost:.2f}"))  # Gas Cost
                self.cost_table.setItem(row, 10, QTableWidgetItem(f"Rs.{gst_amount:.2f}"))  # GST Amount

        except Exception as e:
            self.logger.error(f"Error populating cost analysis: {e}")

    def populate_pricing_strategy_no_missing_check(self):
        """Populate pricing strategy table without checking missing items"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.pricing_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate ingredient cost directly
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                if ingredient_cost is None:
                    self.pricing_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    self.pricing_table.setItem(row, 1, QTableWidgetItem("❌ Missing Ingredients"))
                    for col in range(2, 7):
                        self.pricing_table.setItem(row, col, QTableWidgetItem("N/A"))
                    continue

                making_cost = ingredient_cost  # Making cost equals ingredient cost
                packaging_cost = self.calculate_actual_packaging_cost(recipe_name)
                other_charges = 2.0
                total_cost = ingredient_cost + making_cost + packaging_cost + other_charges

                # Pricing strategy
                others_pricing = total_cost * 1.8  # 80% markup
                margin_percentage = 30.0  # 30% margin
                margin_value = total_cost * (margin_percentage / 100)
                our_pricing = total_cost + margin_value
                selling_price = max(our_pricing, others_pricing * 0.9)  # 10% below others
                profit = selling_price - total_cost

                # Populate table
                self.pricing_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.pricing_table.setItem(row, 1, QTableWidgetItem(f"Rs.{total_cost:.2f}"))
                self.pricing_table.setItem(row, 2, QTableWidgetItem(f"Rs.{others_pricing:.2f}"))
                self.pricing_table.setItem(row, 3, QTableWidgetItem(f"Rs.{margin_value:.2f}"))
                self.pricing_table.setItem(row, 4, QTableWidgetItem(f"Rs.{our_pricing:.2f}"))
                self.pricing_table.setItem(row, 5, QTableWidgetItem(f"Rs.{selling_price:.2f}"))
                self.pricing_table.setItem(row, 6, QTableWidgetItem(f"Rs.{profit:.2f}"))

        except Exception as e:
            self.logger.error(f"Error populating pricing strategy (no missing check): {e}")

    def populate_profit_analysis_no_missing_check(self):
        """Populate profit analysis table using application data"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.profit_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate cost of making using application's ingredient data
                cost_of_making = self.calculate_ingredient_cost(recipe_id)

                # Get our pricing from Excel reference
                excel_pricing = self.recipe_pricing_data.get(recipe_name, {})
                our_pricing = excel_pricing.get('our_pricing')

                if cost_of_making is None or cost_of_making <= 0:
                    self.profit_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    for col in range(1, 6):
                        self.profit_table.setItem(row, col, QTableWidgetItem("Soon"))
                    continue

                # Calculate profit if we have pricing data
                if our_pricing is not None:
                    profit = our_pricing - cost_of_making
                    profit_percentage = (profit / cost_of_making) * 100 if cost_of_making > 0 else 0

                    # Determine status
                    if profit_percentage > 100:
                        status = "Excellent"
                        status_color = "#10b981"
                    elif profit_percentage > 50:
                        status = "Good"
                        status_color = "#3b82f6"
                    elif profit_percentage > 0:
                        status = "Average"
                        status_color = "#f59e0b"
                    else:
                        status = "Loss"
                        status_color = "#ef4444"
                else:
                    profit = None
                    profit_percentage = None
                    status = "No Pricing"
                    status_color = "#6b7280"

                # Populate table
                self.profit_table.setItem(row, 0, QTableWidgetItem(recipe_name))

                if our_pricing is not None:
                    self.profit_table.setItem(row, 1, QTableWidgetItem(f"Rs.{our_pricing:.2f}"))
                else:
                    self.profit_table.setItem(row, 1, QTableWidgetItem("Soon"))

                self.profit_table.setItem(row, 2, QTableWidgetItem(f"Rs.{cost_of_making:.2f}"))

                if profit is not None:
                    profit_item = QTableWidgetItem(f"Rs.{profit:.2f}")
                    if profit > 0:
                        profit_item.setForeground(QColor("#10b981"))
                    else:
                        profit_item.setForeground(QColor("#ef4444"))
                    self.profit_table.setItem(row, 3, profit_item)
                else:
                    self.profit_table.setItem(row, 3, QTableWidgetItem("Soon"))

                if profit_percentage is not None:
                    percentage_item = QTableWidgetItem(f"{profit_percentage:.1f}%")
                    percentage_item.setForeground(QColor(status_color))
                    self.profit_table.setItem(row, 4, percentage_item)
                else:
                    self.profit_table.setItem(row, 4, QTableWidgetItem("Soon"))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                self.profit_table.setItem(row, 5, status_item)

        except Exception as e:
            self.logger.error(f"Error populating profit analysis (no missing check): {e}")

    def populate_discount_analysis_no_missing_check(self):
        """Populate discount analysis table without checking missing items"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.discount_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate ingredient cost directly
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                if ingredient_cost is None:
                    self.discount_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    self.discount_table.setItem(row, 1, QTableWidgetItem("❌ Missing Ingredients"))
                    for col in range(2, 8):
                        self.discount_table.setItem(row, col, QTableWidgetItem("N/A"))
                    continue

                total_cost = ingredient_cost * 1.5
                original_price = total_cost * 1.4

                # Calculate discounted prices
                discount_10 = original_price * 0.9
                discount_15 = original_price * 0.85
                discount_25 = original_price * 0.75
                discount_30 = original_price * 0.7
                discount_40 = original_price * 0.6

                # Find minimum profitable price (break-even + 5%)
                min_profitable = total_cost * 1.05

                # Populate table
                self.discount_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.discount_table.setItem(row, 1, QTableWidgetItem(f"Rs.{original_price:.2f}"))
                self.discount_table.setItem(row, 2, QTableWidgetItem(f"Rs.{discount_10:.2f}"))
                self.discount_table.setItem(row, 3, QTableWidgetItem(f"Rs.{discount_15:.2f}"))
                self.discount_table.setItem(row, 4, QTableWidgetItem(f"Rs.{discount_25:.2f}"))
                self.discount_table.setItem(row, 5, QTableWidgetItem(f"Rs.{discount_30:.2f}"))
                self.discount_table.setItem(row, 6, QTableWidgetItem(f"Rs.{discount_40:.2f}"))
                self.discount_table.setItem(row, 7, QTableWidgetItem(f"Rs.{min_profitable:.2f}"))

        except Exception as e:
            self.logger.error(f"Error populating discount analysis (no missing check): {e}")

    def calculate_ingredient_cost(self, recipe_id):
        """Calculate total ingredient cost for a recipe using actual pricing data"""
        try:
            if 'recipe_ingredients' not in self.data:
                return 0.0

            recipe_ingredients = self.data['recipe_ingredients']

            # Get ingredients for this recipe
            recipe_items = recipe_ingredients[recipe_ingredients['recipe_id'] == recipe_id]

            total_cost = 0.0
            missing_ingredients = []

            for _, ingredient in recipe_items.iterrows():
                item_name = ingredient.get('item_name', '')
                quantity = float(ingredient.get('quantity', 0))
                unit = ingredient.get('unit', '')

                # Get unit price from our pricing data
                unit_price = self.get_ingredient_unit_price(item_name, unit)

                if unit_price > 0:
                    ingredient_cost = quantity * unit_price
                    total_cost += ingredient_cost
                    self.logger.debug(f"Recipe {recipe_id}: {item_name} = {quantity} {unit} × Rs.{unit_price} = Rs.{ingredient_cost:.4f}")
                else:
                    missing_ingredients.append({
                        'item_name': item_name,
                        'quantity': quantity,
                        'unit': unit
                    })
                    self.logger.warning(f"Missing price for ingredient: {item_name}")

            if missing_ingredients:
                self.logger.warning(f"Recipe {recipe_id} has {len(missing_ingredients)} missing ingredient prices")
                # Return None to indicate incomplete pricing data
                return None

            return round(total_cost, 2)

        except Exception as e:
            self.logger.error(f"Error calculating ingredient cost for recipe {recipe_id}: {e}")
            return None

    def get_ingredient_unit_price(self, ingredient_name, unit):
        """Get unit price for an ingredient"""
        try:
            # Clean ingredient name
            clean_name = ingredient_name.strip()

            # Look up price in our pricing data
            unit_price = self.ingredient_unit_prices.get(clean_name, 0.0)

            if unit_price == 0.0:
                # Try to get from inventory or shopping data
                unit_price = self.get_ingredient_price_from_inventory_only(clean_name)
                if unit_price is None:
                    unit_price = self.get_ingredient_price_from_shopping_list(clean_name)
                    if unit_price is None:
                        unit_price = 0.0

            return unit_price

        except Exception as e:
            self.logger.error(f"Error getting unit price for {ingredient_name}: {e}")
            return 0.0

    def calculate_recipe_pricing(self, recipe_name, recipe_id=None):
        """Calculate complete pricing for a recipe based on user's Excel formulas"""
        try:
            # Get recipe ID if not provided
            if recipe_id is None:
                recipe_id = self.get_recipe_id_by_name(recipe_name)
                if recipe_id is None:
                    return None

            # Calculate cost of making (sum of ingredient costs)
            cost_of_making = self.calculate_ingredient_cost(recipe_id)
            if cost_of_making is None:
                return None

            # Get pricing data from user's Excel
            pricing_data = self.recipe_pricing_data.get(recipe_name, {})
            others_pricing = pricing_data.get('others_pricing')
            our_pricing = pricing_data.get('our_pricing')
            cooking_time = pricing_data.get('cooking_time', 'N/A')

            # Set all additional costs to 0 as per user requirement
            pkg_cost = 0.0
            other_charges = 0.0
            electricity_cost = 0.0
            gas_cost = 0.0
            gst_amount = 0.0

            # Calculate profit and profit percentage
            if our_pricing is not None:
                profit = our_pricing - cost_of_making - pkg_cost - other_charges - electricity_cost - gas_cost
                profit_percentage = (profit / cost_of_making) * 100 if cost_of_making > 0 else 0
            else:
                profit = None
                profit_percentage = None

            return {
                'recipe_name': recipe_name,
                'recipe_id': recipe_id,
                'cost_of_making': cost_of_making,
                'others_pricing': others_pricing,
                'our_pricing': our_pricing,
                'profit': profit,
                'profit_percentage': profit_percentage,
                'pkg_cost': pkg_cost,
                'other_charges': other_charges,
                'electricity_cost': electricity_cost,
                'gas_cost': gas_cost,
                'gst_amount': gst_amount,
                'cooking_time': cooking_time
            }

        except Exception as e:
            self.logger.error(f"Error calculating pricing for {recipe_name}: {e}")
            return None

    def get_recipe_id_by_name(self, recipe_name):
        """Get recipe ID by recipe name using application's data structure"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return None

            recipes_df = self.data['recipes']
            matching_recipes = recipes_df[recipes_df['recipe_name'] == recipe_name]

            if not matching_recipes.empty:
                return matching_recipes.iloc[0]['recipe_id']

            return None

        except Exception as e:
            self.logger.error(f"Error getting recipe ID for {recipe_name}: {e}")
            return None

    def get_recipe_name_by_id(self, recipe_id):
        """Get recipe name by recipe ID"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return None

            recipes_df = self.data['recipes']
            matching_recipes = recipes_df[recipes_df['recipe_id'] == recipe_id]

            if not matching_recipes.empty:
                return matching_recipes.iloc[0]['recipe_name']

            return None

        except Exception as e:
            self.logger.error(f"Error getting recipe name for ID {recipe_id}: {e}")
            return None

    def convert_price_with_units(self, price_per_unit, item_name, recipe_unit, recipe_quantity):
        """Convert price based on unit differences between inventory and recipe"""
        try:
            # Get the inventory unit for this item
            inventory_unit = self.get_inventory_unit(item_name)
            if not inventory_unit:
                # If we can't find inventory unit, assume the price is correct as-is
                return recipe_quantity * price_per_unit

            # Convert recipe quantity to inventory unit
            converted_quantity = self.convert_units(recipe_quantity, recipe_unit, inventory_unit)

            # Calculate cost using converted quantity
            total_cost = converted_quantity * price_per_unit

            # Log the conversion for debugging
            self.logger.debug(f"Unit conversion for {item_name}: {recipe_quantity} {recipe_unit} = {converted_quantity} {inventory_unit}, cost = Rs.{total_cost:.2f}")

            return total_cost

        except Exception as e:
            self.logger.error(f"Error in unit conversion for {item_name}: {e}")
            # Fallback to simple multiplication
            return recipe_quantity * price_per_unit

    def get_inventory_unit(self, item_name):
        """Get the unit used in inventory for this item"""
        try:
            if 'inventory' not in self.data:
                return None

            inventory = self.data['inventory']

            # Look for exact match first
            exact_match = inventory[inventory['item_name'].str.lower() == item_name.lower()]
            if not exact_match.empty:
                return exact_match.iloc[0].get('unit', 'units')

            # Try partial match
            partial_match = inventory[inventory['item_name'].str.lower().str.contains(item_name.lower(), na=False)]
            if not partial_match.empty:
                return partial_match.iloc[0].get('unit', 'units')

            return None
        except Exception as e:
            self.logger.error(f"Error getting inventory unit for {item_name}: {e}")
            return None

    def convert_units(self, quantity, from_unit, to_unit):
        """Convert quantity from one unit to another"""
        try:
            # Normalize units to lowercase
            from_unit = from_unit.lower().strip()
            to_unit = to_unit.lower().strip()

            # If units are the same, no conversion needed
            if from_unit == to_unit:
                return quantity

            # Volume conversions
            volume_conversions = {
                ('ml', 'l'): 0.001,
                ('l', 'ml'): 1000,
                ('ml', 'liters'): 0.001,
                ('liters', 'ml'): 1000,
                ('ml', 'liter'): 0.001,
                ('liter', 'ml'): 1000,
            }

            # Weight conversions
            weight_conversions = {
                ('grams', 'kg'): 0.001,
                ('kg', 'grams'): 1000,
                ('g', 'grams'): 1,  # Convert old 'g' to 'grams'
                ('grams', 'g'): 1,  # Convert 'grams' to old 'g'
                ('g', 'kg'): 0.001,  # Legacy support
                ('kg', 'g'): 1000,  # Legacy support
            }

            # Special cooking unit conversions (approximate)
            cooking_conversions = {
                # Teaspoons and tablespoons to grams (approximate for spices)
                ('tsp', 'grams'): 5,  # 1 tsp ≈ 5g for spices
                ('tbsp', 'grams'): 15,  # 1 tbsp ≈ 15g for spices

                # Units/pieces to grams (very approximate, depends on item)
                ('units', 'grams'): 50,  # 1 unit ≈ 50g (average for vegetables)
                ('pcs', 'grams'): 50,
                ('pieces', 'grams'): 50,

                # Leaves to grams
                ('leaves', 'grams'): 1,  # 1 leaf ≈ 1g

                # Legacy support for old units
                ('tsp', 'g'): 5,
                ('tbsp', 'g'): 15,
                ('units', 'g'): 50,
                ('pcs', 'g'): 50,
                ('pieces', 'g'): 50,
                ('leaves', 'g'): 1,

                # Volume to weight conversions (for liquids, 1ml ≈ 1g)
                ('ml', 'grams'): 1,
                ('ml', 'g'): 1,
                ('ml', 'gram'): 1,
                ('grams', 'ml'): 1,
                ('g', 'ml'): 1,
                ('gram', 'ml'): 1,
                ('l', 'grams'): 1000,
                ('l', 'g'): 1000,
                ('l', 'gram'): 1000,
                ('grams', 'l'): 0.001,
                ('g', 'l'): 0.001,
                ('gram', 'l'): 0.001,
                ('liters', 'grams'): 1000,
                ('liters', 'g'): 1000,
                ('liters', 'gram'): 1000,
                ('grams', 'liters'): 0.001,
                ('g', 'liters'): 0.001,
                ('gram', 'liters'): 0.001,
                ('liter', 'grams'): 1000,
                ('liter', 'g'): 1000,
                ('liter', 'gram'): 1000,
                ('grams', 'liter'): 0.001,
                ('g', 'liter'): 0.001,
                ('gram', 'liter'): 0.001,

                # Critical missing conversions that are causing the warnings
                ('ml', 'kg'): 0.000001,  # 1ml = 0.000001kg (for liquids)
                ('kg', 'ml'): 1000000,   # 1kg = 1000000ml (for liquids)
            }

            # Combine all conversions
            all_conversions = {**volume_conversions, **weight_conversions, **cooking_conversions}

            # Check for direct conversion
            conversion_key = (from_unit, to_unit)
            if conversion_key in all_conversions:
                converted_quantity = quantity * all_conversions[conversion_key]
                self.logger.debug(f"Converted {quantity} {from_unit} to {converted_quantity} {to_unit}")
                return converted_quantity

            # If no conversion found, use reasonable defaults based on unit types
            if self.is_volume_unit(from_unit) and self.is_weight_unit(to_unit):
                # Volume to weight: assume 1ml = 1g (for liquids)
                self.logger.debug(f"Volume to weight conversion: {quantity} {from_unit} ≈ {quantity} {to_unit}")
                return quantity
            elif self.is_weight_unit(from_unit) and self.is_volume_unit(to_unit):
                # Weight to volume: assume 1g = 1ml (for liquids)
                self.logger.debug(f"Weight to volume conversion: {quantity} {from_unit} ≈ {quantity} {to_unit}")
                return quantity
            else:
                # Last resort: 1:1 ratio
                self.logger.warning(f"No conversion found from {from_unit} to {to_unit}, using 1:1 ratio")
                return quantity

        except Exception as e:
            self.logger.error(f"Error converting units from {from_unit} to {to_unit}: {e}")
            return quantity

    def is_volume_unit(self, unit):
        """Check if unit is a volume unit"""
        volume_units = ['ml', 'l', 'liters', 'liter']
        return unit.lower() in volume_units

    def is_weight_unit(self, unit):
        """Check if unit is a weight unit"""
        weight_units = ['grams', 'kg', 'g', 'gram', 'kilograms', 'kilogram']  # grams first as preferred
        return unit.lower() in weight_units

    def store_missing_ingredients(self, recipe_id, missing_ingredients, found_ingredients=None):
        """Store missing ingredients for reporting"""
        try:
            # Create missing ingredients file if it doesn't exist
            missing_file = os.path.join('data', 'missing_ingredients.json')

            # Load existing missing ingredients
            if os.path.exists(missing_file):
                with open(missing_file, 'r') as f:
                    all_missing = json.load(f)
            else:
                all_missing = {}

            # Add current missing ingredients
            recipe_key = f"recipe_{recipe_id}"

            if missing_ingredients:  # Only store if there are missing ingredients
                all_missing[recipe_key] = {
                    'recipe_id': recipe_id,
                    'missing_items': missing_ingredients,
                    'found_items': found_ingredients or [],
                    'last_checked': datetime.now().isoformat(),
                    'status': 'incomplete'
                }
            else:
                # Remove from missing if all ingredients are now found
                if recipe_key in all_missing:
                    del all_missing[recipe_key]

            # Save updated missing ingredients
            os.makedirs('data', exist_ok=True)
            with open(missing_file, 'w') as f:
                json.dump(all_missing, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error storing missing ingredients: {e}")

    def get_ingredient_price_from_inventory_only(self, item_name):
        """Get ingredient price ONLY from inventory.csv - no other sources"""
        try:
            if 'inventory' not in self.data:
                return None

            inventory = self.data['inventory']
            if inventory.empty:
                return None

            # Look for exact match first
            exact_match = inventory[inventory['item_name'].str.lower() == item_name.lower()]
            if not exact_match.empty:
                # Use avg_price if available (more reliable), otherwise calculate from price_per_unit
                if 'avg_price' in exact_match.columns and pd.notna(exact_match.iloc[0]['avg_price']):
                    price = float(exact_match.iloc[0]['avg_price'])
                elif 'price_per_unit' in exact_match.columns and pd.notna(exact_match.iloc[0]['price_per_unit']):
                    # Calculate actual price per unit from total price and quantity
                    price_per_unit = float(exact_match.iloc[0]['price_per_unit'])
                    quantity = float(exact_match.iloc[0]['quantity']) if pd.notna(exact_match.iloc[0]['quantity']) else 1.0

                    # If price_per_unit seems too high, it might be total price, so divide by quantity
                    if price_per_unit > 100 and quantity > 1:
                        price = price_per_unit / quantity
                    else:
                        price = price_per_unit
                else:
                    return None

                # Return reasonable price (cap at Rs.1000 per unit to avoid extreme values)
                return min(price, 1000.0)

            # Try partial match
            partial_match = inventory[inventory['item_name'].str.lower().str.contains(item_name.lower(), na=False)]
            if not partial_match.empty:
                if 'avg_price' in partial_match.columns and pd.notna(partial_match.iloc[0]['avg_price']):
                    price = float(partial_match.iloc[0]['avg_price'])
                elif 'price_per_unit' in partial_match.columns and pd.notna(partial_match.iloc[0]['price_per_unit']):
                    # Calculate actual price per unit from total price and quantity
                    price_per_unit = float(partial_match.iloc[0]['price_per_unit'])
                    quantity = float(partial_match.iloc[0]['quantity']) if pd.notna(partial_match.iloc[0]['quantity']) else 1.0

                    # If price_per_unit seems too high, it might be total price, so divide by quantity
                    if price_per_unit > 100 and quantity > 1:
                        price = price_per_unit / quantity
                    else:
                        price = price_per_unit
                else:
                    return None

                # Return reasonable price (cap at ₹1000 per unit to avoid extreme values)
                return min(price, 1000.0)

            return None
        except Exception as e:
            self.logger.error(f"Error getting price from inventory for {item_name}: {e}")
            return None

    def get_ingredient_price_from_shopping_list(self, item_name):
        """Get ingredient price from shopping list using average_price"""
        try:
            if 'shopping_list' not in self.data:
                return None

            shopping_df = self.data['shopping_list']

            # Look for exact match first
            exact_match = shopping_df[shopping_df['item_name'].str.lower() == item_name.lower()]
            if not exact_match.empty:
                # Use avg_price if available, otherwise current_price, otherwise last_price
                if 'avg_price' in exact_match.columns and pd.notna(exact_match.iloc[0]['avg_price']):
                    price = float(exact_match.iloc[0]['avg_price'])
                elif 'current_price' in exact_match.columns and pd.notna(exact_match.iloc[0]['current_price']):
                    price = float(exact_match.iloc[0]['current_price'])
                elif 'last_price' in exact_match.columns and pd.notna(exact_match.iloc[0]['last_price']):
                    # Calculate price per unit from last_price and quantity
                    estimated_cost = float(exact_match.iloc[0]['last_price'])
                    quantity = float(exact_match.iloc[0]['quantity']) if pd.notna(exact_match.iloc[0]['quantity']) else 1.0
                    price = estimated_cost / quantity if quantity > 0 else estimated_cost
                else:
                    return None

                # Return reasonable price (cap at Rs.1000 per unit to avoid extreme values)
                return min(price, 1000.0)

            # Try partial match
            partial_match = shopping_df[shopping_df['item_name'].str.lower().str.contains(item_name.lower(), na=False)]
            if not partial_match.empty:
                if 'avg_price' in partial_match.columns and pd.notna(partial_match.iloc[0]['avg_price']):
                    price = float(partial_match.iloc[0]['avg_price'])
                elif 'current_price' in partial_match.columns and pd.notna(partial_match.iloc[0]['current_price']):
                    price = float(partial_match.iloc[0]['current_price'])
                elif 'last_price' in partial_match.columns and pd.notna(partial_match.iloc[0]['last_price']):
                    # Calculate price per unit from last_price and quantity
                    estimated_cost = float(partial_match.iloc[0]['last_price'])
                    quantity = float(partial_match.iloc[0]['quantity']) if pd.notna(partial_match.iloc[0]['quantity']) else 1.0
                    price = estimated_cost / quantity if quantity > 0 else estimated_cost
                else:
                    return None

                # Return reasonable price (cap at Rs.1000 per unit to avoid extreme values)
                return min(price, 1000.0)

            return None
        except Exception as e:
            self.logger.error(f"Error getting price from shopping list for {item_name}: {e}")
            return None

    def get_ingredient_price_from_items(self, item_name):
        """Get ingredient price from items table"""
        try:
            if 'items' not in self.data:
                return None

            items = self.data['items']

            # Look for exact match first
            exact_match = items[items['item_name'].str.lower() == item_name.lower()]
            if not exact_match.empty:
                # Use avg_price if available, otherwise price, otherwise default_cost
                if 'avg_price' in exact_match.columns and pd.notna(exact_match.iloc[0]['avg_price']):
                    return float(exact_match.iloc[0]['avg_price'])
                elif 'price' in exact_match.columns and pd.notna(exact_match.iloc[0]['price']):
                    return float(exact_match.iloc[0]['price'])
                elif 'default_cost' in exact_match.columns and pd.notna(exact_match.iloc[0]['default_cost']):
                    return float(exact_match.iloc[0]['default_cost'])

            return None
        except Exception as e:
            self.logger.error(f"Error getting price from items for {item_name}: {e}")
            return None



    def calculate_ingredient_cost_from_recipe(self, recipe_id):
        """Fallback method to calculate cost from recipe ingredients string"""
        try:
            if 'recipes' not in self.data:
                return 10.0

            recipes = self.data['recipes']
            recipe = recipes[recipes['recipe_id'] == recipe_id]

            if recipe.empty:
                return 10.0

            ingredients_str = recipe.iloc[0].get('ingredients', '')
            if not ingredients_str:
                return 10.0

            # Parse ingredients string and estimate cost
            ingredients = ingredients_str.split(',')
            total_cost = 0.0

            for ingredient in ingredients:
                ingredient = ingredient.strip()
                # Try to get price from shopping list or items
                cost = self.get_ingredient_price_from_shopping_list(ingredient)
                if cost is None:
                    cost = self.get_ingredient_price_from_items(ingredient)
                if cost is None:
                    cost = self.get_smart_ingredient_price(ingredient)  # Use smart pricing

                total_cost += cost

            return max(total_cost, 10.0)
        except Exception as e:
            self.logger.error(f"Error calculating cost from recipe ingredients: {e}")
            return 10.0

    def calculate_electricity_cost(self, cook_time_minutes, recipe_name=None, selected_appliance=None):
        """Calculate electricity cost - basic ₹0.50 for all items unless specifically mapped to electric appliances"""
        try:
            # Load electricity cost configuration
            electricity_config = self.load_electricity_cost_config()
            electricity_settings = electricity_config.get('electricity_settings', {})
            appliances = electricity_config.get('appliances', {})
            recipe_mapping = electricity_config.get('recipe_appliance_mapping', {})

            # Get basic settings
            rate_per_kwh = electricity_settings.get('electricity_rate_per_kwh_inr', 7.50)
            basic_charge = electricity_settings.get('minimum_cost_inr', 0.50)  # Basic ₹0.50 for tubelight

            # Check if recipe is specifically mapped to an electric appliance
            appliance_name = selected_appliance
            if not appliance_name and recipe_name:
                appliance_name = recipe_mapping.get(recipe_name)

            # If no specific appliance mapping, return basic charge (tubelight only)
            if not appliance_name:
                self.logger.debug(f"Electricity cost: {recipe_name} using basic charge (tubelight only) = Rs.{basic_charge:.2f}")
                return basic_charge

            # Calculate actual appliance cost for mapped dishes
            appliance_data = appliances.get(appliance_name, {})
            power_kw = appliance_data.get('power_consumption_kw', 0.0)

            if power_kw == 0.0:
                # If appliance has 0 power (like Basic Kitchen Lighting), return basic charge
                return basic_charge

            # Calculate actual electricity cost for electric appliances
            hours = cook_time_minutes / 60.0
            cost = power_kw * hours * rate_per_kwh
            final_cost = max(cost, basic_charge)  # Never less than basic charge

            self.logger.debug(f"Electricity cost calculated: {recipe_name} using {appliance_name} "
                            f"({power_kw}kW) for {cook_time_minutes}min = Rs.{final_cost:.2f}")
            return final_cost

        except Exception as e:
            self.logger.error(f"Error calculating electricity cost: {e}")
            return 0.50  # Return basic charge on error

    def calculate_gas_cost(self, recipe_data=None, cook_time_minutes=None):
        """Calculate gas cost based on total preparation time (prep_time + cook_time)"""
        try:
            # Load gas cost configuration
            gas_config = self.load_gas_cost_config()
            gas_settings = gas_config.get('gas_cost_settings', {})
            cylinder_settings = gas_config.get('cylinder_settings', {})

            gas_consumption_per_hour = gas_settings.get('gas_consumption_per_hour_kg', 0.3)
            rate_per_kg = cylinder_settings.get('cost_per_kg_inr', gas_settings.get('gas_rate_per_kg_inr', 60.67))
            minimum_cost = gas_settings.get('minimum_cost_inr', 0.5)
            use_total_prep_time = gas_settings.get('use_total_preparation_time', True)

            total_time_minutes = 0

            # If recipe_data is provided, calculate preparation time based on config
            if recipe_data is not None:
                prep_time = recipe_data.get('prep_time', 0)
                cook_time = recipe_data.get('cook_time', 0)

                if use_total_prep_time:
                    total_time_minutes = prep_time + cook_time
                    self.logger.debug(f"Gas cost calculation - Prep: {prep_time}min, Cook: {cook_time}min, Total: {total_time_minutes}min")
                else:
                    total_time_minutes = cook_time
                    self.logger.debug(f"Gas cost calculation - Using cook_time only: {total_time_minutes}min")

            # Fallback to cook_time_minutes parameter if recipe_data not available
            elif cook_time_minutes is not None:
                total_time_minutes = cook_time_minutes
                self.logger.debug(f"Gas cost calculation - Using cook_time only: {total_time_minutes}min")

            # Default to 30 minutes if no time data available
            else:
                total_time_minutes = 30
                self.logger.warning("No time data available for gas cost calculation, using default 30 minutes")

            # Calculate gas cost
            hours = total_time_minutes / 60.0
            cost = gas_consumption_per_hour * hours * rate_per_kg
            final_cost = max(cost, minimum_cost)

            self.logger.debug(f"Gas cost calculated: {total_time_minutes}min = Rs.{final_cost:.2f}")
            return final_cost

        except Exception as e:
            self.logger.error(f"Error calculating gas cost: {e}")
            return 1.0

    def load_gas_cost_config(self):
        """Load gas cost configuration from JSON file"""
        try:
            import json
            import os

            config_path = os.path.join('data', 'gas_cost_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('gas_cost_settings', {})
            else:
                self.logger.warning(f"Gas cost config file not found at {config_path}, using defaults")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading gas cost config: {e}")
            return {}

    def load_electricity_cost_config(self):
        """Load electricity cost configuration from JSON file"""
        try:
            import json
            import os

            config_path = os.path.join('data', 'electricity_cost_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Electricity cost config file not found at {config_path}, using defaults")
                return {
                    "electricity_settings": {
                        "default_appliance": "Basic Kitchen Lighting",
                        "electricity_rate_per_kwh_inr": 7.50,
                        "minimum_cost_inr": 0.50,
                        "use_cooking_time_only": True
                    },
                    "appliances": {
                        "Basic Kitchen Lighting": {"power_consumption_kw": 0.0},
                        "Electric Induction Cooktop": {"power_consumption_kw": 2.0},
                        "Mixer": {"power_consumption_kw": 0.5}
                    }
                }
        except Exception as e:
            self.logger.error(f"Error loading electricity cost config: {e}")
            return {
                "electricity_settings": {
                    "default_appliance": "Basic Kitchen Lighting",
                    "electricity_rate_per_kwh_inr": 7.50,
                    "minimum_cost_inr": 0.50,
                    "use_cooking_time_only": True
                },
                "appliances": {
                    "Basic Kitchen Lighting": {"power_consumption_kw": 0.0},
                    "Electric Induction Cooktop": {"power_consumption_kw": 2.0},
                    "Mixer": {"power_consumption_kw": 0.5}
                }
            }

    def get_tax_rates(self):
        """Get GST and SGST rates from configuration"""
        try:
            # Try to load from settings file
            import os
            config_path = os.path.join('data', 'tax_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    import json
                    tax_config = json.load(f)
                    tax_settings = tax_config.get('tax_settings', {})
                    return {
                        'gst_rate': tax_settings.get('gst_rate', 0.075),  # 7.5%
                        'sgst_rate': tax_settings.get('sgst_rate', 0.075)  # 7.5%
                    }
            else:
                # Return default rates
                return {
                    'gst_rate': 0.075,  # 7.5% GST
                    'sgst_rate': 0.075  # 7.5% SGST
                }
        except Exception as e:
            self.logger.error(f"Error loading tax rates: {e}")
            return {
                'gst_rate': 0.075,  # 7.5% GST
                'sgst_rate': 0.075  # 7.5% SGST
            }

    def calculate_actual_packaging_cost(self, recipe_name):
        """Calculate actual packaging cost from in-memory data first, then CSV fallback"""
        try:
            # First try to use in-memory data (from Packing Materials Management interface)
            if hasattr(self, 'main_app') and hasattr(self.main_app, 'data'):
                data = self.main_app.data
            else:
                data = self.data

            # Check if recipe packing materials data exists in memory
            if 'recipe_packing_materials' in data and not data['recipe_packing_materials'].empty:
                # Get materials for this recipe from in-memory data
                recipe_materials = data['recipe_packing_materials'][
                    data['recipe_packing_materials']['recipe_name'] == recipe_name
                ]

                if not recipe_materials.empty:
                    # Use the pre-calculated cost_per_recipe from in-memory data
                    total_cost = recipe_materials['cost_per_recipe'].sum()

                    if total_cost > 0:
                        # Debug information
                        materials_list = []
                        for _, row in recipe_materials.iterrows():
                            materials_list.append(f"{row['material_name']} (Rs.{row['cost_per_recipe']:.2f})")

                        self.logger.info(f"[SUCCESS] Packing cost from IN-MEMORY data for {recipe_name}: {', '.join(materials_list)} = Rs.{total_cost:.2f}")
                        return float(total_cost)

            # Fallback to CSV file if in-memory data is not available or empty
            import os
            import pandas as pd

            packing_file = os.path.join('data', 'recipe_packing_materials.csv')
            if os.path.exists(packing_file):
                packing_df = pd.read_csv(packing_file)

                # Filter for the specific recipe
                recipe_materials = packing_df[packing_df['recipe_name'] == recipe_name]

                if not recipe_materials.empty:
                    # Sum up all packing costs for this recipe (cost_per_recipe column already calculated)
                    total_cost = recipe_materials['cost_per_recipe'].sum()

                    if total_cost > 0:
                        # Debug information
                        materials_list = []
                        for _, row in recipe_materials.iterrows():
                            materials_list.append(f"{row['material_name']} (Rs.{row['cost_per_recipe']:.2f})")

                        self.logger.info(f"⚠️ Packing cost from CSV FALLBACK for {recipe_name}: {', '.join(materials_list)} = Rs.{total_cost:.2f}")
                        return float(total_cost)

            # Final fallback - use default cost
            self.logger.debug(f"No packing materials data found for {recipe_name}, using default cost")
            return 5.0  # Default fallback cost

        except Exception as e:
            self.logger.error(f"Error calculating packaging cost for {recipe_name}: {e}")
            return 5.0  # Default fallback cost

    def populate_pricing_strategy(self):
        """Populate pricing strategy table"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.pricing_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate costs
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                # Skip if ingredient cost is None (missing ingredients)
                if ingredient_cost is None:
                    self.pricing_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    self.pricing_table.setItem(row, 1, QTableWidgetItem("❌ Missing Ingredients"))
                    for col in range(2, 7):
                        self.pricing_table.setItem(row, col, QTableWidgetItem("N/A"))
                    continue

                making_cost = ingredient_cost * 0.2
                packaging_cost = self.calculate_actual_packaging_cost(recipe_name)
                other_charges = 2.0
                total_cost = ingredient_cost + making_cost + packaging_cost + other_charges

                # Pricing strategy
                others_pricing = total_cost * 1.8  # 80% markup
                margin_percentage = 30.0  # 30% margin
                margin_value = total_cost * (margin_percentage / 100)
                our_pricing = total_cost + margin_value
                selling_price = max(our_pricing, others_pricing * 0.9)  # 10% below others
                profit = selling_price - total_cost

                # Populate table
                self.pricing_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.pricing_table.setItem(row, 1, QTableWidgetItem(f"Rs.{total_cost:.2f}"))
                self.pricing_table.setItem(row, 2, QTableWidgetItem(f"Rs.{others_pricing:.2f}"))
                self.pricing_table.setItem(row, 3, QTableWidgetItem(f"Rs.{margin_value:.2f}"))
                self.pricing_table.setItem(row, 4, QTableWidgetItem(f"Rs.{our_pricing:.2f}"))
                self.pricing_table.setItem(row, 5, QTableWidgetItem(f"Rs.{selling_price:.2f}"))
                self.pricing_table.setItem(row, 6, QTableWidgetItem(f"Rs.{profit:.2f}"))

        except Exception as e:
            self.logger.error(f"Error populating pricing strategy: {e}")

    def populate_profit_analysis(self):
        """Populate profit analysis table"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.profit_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate costs and pricing
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                # Skip if ingredient cost is None (missing ingredients)
                if ingredient_cost is None:
                    self.profit_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    self.profit_table.setItem(row, 1, QTableWidgetItem("❌ Missing Ingredients"))
                    for col in range(2, 6):
                        self.profit_table.setItem(row, col, QTableWidgetItem("N/A"))
                    continue

                total_cost = ingredient_cost * 1.5  # Including all costs
                selling_price = total_cost * 1.4  # 40% markup
                profit = selling_price - total_cost
                profit_percentage = (profit / total_cost) * 100 if total_cost > 0 else 0

                # Determine status
                if profit_percentage > 30:
                    status = "Excellent"
                    status_color = "#10b981"
                elif profit_percentage > 20:
                    status = "Good"
                    status_color = "#3b82f6"
                elif profit_percentage > 10:
                    status = "Average"
                    status_color = "#f59e0b"
                else:
                    status = "Poor"
                    status_color = "#ef4444"

                # Populate table
                self.profit_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.profit_table.setItem(row, 1, QTableWidgetItem(f"Rs.{selling_price:.2f}"))
                self.profit_table.setItem(row, 2, QTableWidgetItem(f"Rs.{total_cost:.2f}"))
                self.profit_table.setItem(row, 3, QTableWidgetItem(f"Rs.{profit:.2f}"))
                self.profit_table.setItem(row, 4, QTableWidgetItem(f"{profit_percentage:.1f}%"))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                self.profit_table.setItem(row, 5, status_item)

        except Exception as e:
            self.logger.error(f"Error populating profit analysis: {e}")

    def populate_discount_analysis(self):
        """Populate discount analysis table"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            self.discount_table.setRowCount(len(recipes_df))

            for row, (_, recipe) in enumerate(recipes_df.iterrows()):
                recipe_name = recipe.get('recipe_name', '')
                recipe_id = recipe.get('recipe_id', row + 1)

                # Calculate base pricing
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                # Skip if ingredient cost is None (missing ingredients)
                if ingredient_cost is None:
                    self.discount_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                    self.discount_table.setItem(row, 1, QTableWidgetItem("❌ Missing Ingredients"))
                    for col in range(2, 8):
                        self.discount_table.setItem(row, col, QTableWidgetItem("N/A"))
                    continue

                total_cost = ingredient_cost * 1.5
                original_price = total_cost * 1.4

                # Calculate discounted prices
                discount_10 = original_price * 0.9
                discount_15 = original_price * 0.85
                discount_25 = original_price * 0.75
                discount_30 = original_price * 0.7
                discount_40 = original_price * 0.6

                # Find minimum profitable price (break-even + 5%)
                min_profitable = total_cost * 1.05

                # Populate table
                self.discount_table.setItem(row, 0, QTableWidgetItem(recipe_name))
                self.discount_table.setItem(row, 1, QTableWidgetItem(f"Rs.{original_price:.2f}"))
                self.discount_table.setItem(row, 2, QTableWidgetItem(f"Rs.{discount_10:.2f}"))
                self.discount_table.setItem(row, 3, QTableWidgetItem(f"Rs.{discount_15:.2f}"))
                self.discount_table.setItem(row, 4, QTableWidgetItem(f"Rs.{discount_25:.2f}"))
                self.discount_table.setItem(row, 5, QTableWidgetItem(f"Rs.{discount_30:.2f}"))
                self.discount_table.setItem(row, 6, QTableWidgetItem(f"Rs.{discount_40:.2f}"))
                self.discount_table.setItem(row, 7, QTableWidgetItem(f"Rs.{min_profitable:.2f}"))

        except Exception as e:
            self.logger.error(f"Error populating discount analysis: {e}")

    def update_overview_cards(self):
        """Update overview metric cards"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return

            recipes_df = self.data['recipes']
            total_recipes = len(recipes_df)

            total_cost = 0
            total_selling_price = 0
            total_profit = 0
            valid_recipes = 0

            for _, recipe in recipes_df.iterrows():
                recipe_id = recipe.get('recipe_id', 0)
                ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                # Skip if ingredient cost is None (missing ingredients)
                if ingredient_cost is None:
                    continue

                cost = ingredient_cost * 1.5
                selling_price = cost * 1.4
                profit = selling_price - cost

                total_cost += cost
                total_selling_price += selling_price
                total_profit += profit
                valid_recipes += 1

            if valid_recipes > 0:
                avg_cost = total_cost / valid_recipes
                avg_selling_price = total_selling_price / valid_recipes
                avg_profit = total_profit / valid_recipes
                avg_margin = (avg_profit / avg_cost * 100) if avg_cost > 0 else 0

                # Update cards
                self.avg_cost_card.findChildren(QLabel)[1].setText(f"Rs.{avg_cost:.2f}")
                self.avg_selling_price_card.findChildren(QLabel)[1].setText(f"Rs.{avg_selling_price:.2f}")
                self.avg_profit_card.findChildren(QLabel)[1].setText(f"Rs.{avg_profit:.2f}")
                self.avg_margin_card.findChildren(QLabel)[1].setText(f"{avg_margin:.1f}%")
            else:
                # No valid recipes with complete pricing
                self.avg_cost_card.findChildren(QLabel)[1].setText("❌ Missing Data")
                self.avg_selling_price_card.findChildren(QLabel)[1].setText("❌ Missing Data")
                self.avg_profit_card.findChildren(QLabel)[1].setText("❌ Missing Data")
                self.avg_margin_card.findChildren(QLabel)[1].setText("❌ Missing Data")

        except Exception as e:
            self.logger.error(f"Error updating overview cards: {e}")

    def refresh_all_tables(self):
        """Refresh all pricing tables with current data"""
        try:
            self.populate_cost_analysis_no_missing_check()
            self.populate_pricing_strategy_no_missing_check()
            self.populate_profit_analysis_no_missing_check()
            self.populate_discount_analysis_no_missing_check()
            self.update_overview_cards()
            self.logger.info("All pricing tables refreshed successfully")
        except Exception as e:
            self.logger.error(f"Error refreshing all tables: {e}")

    def calculate_all_prices(self):
        """Calculate prices for all recipes using actual ingredient costs"""
        try:
            notify_info("Calculate", "Calculating prices for all recipes...", parent=self)

            if 'recipes' not in self.data or self.data['recipes'].empty:
                notify_warning("Warning", "No recipes found. Please load recipe data first.", parent=self)
                return

            recipes_df = self.data['recipes']
            total_recipes = len(recipes_df)
            calculated_count = 0
            missing_ingredients = set()

            for _, recipe in recipes_df.iterrows():
                recipe_id = recipe.get('recipe_id')
                recipe_name = recipe.get('recipe_name', f'Recipe {recipe_id}')

                try:
                    # Calculate ingredient cost using actual pricing data
                    ingredient_cost = self.calculate_ingredient_cost(recipe_id)

                    if ingredient_cost is not None and ingredient_cost > 0:
                        calculated_count += 1
                        self.logger.info(f"Calculated cost for {recipe_name}: Rs.{ingredient_cost:.2f}")
                    else:
                        # Check for missing ingredient prices
                        if 'recipe_ingredients' in self.data:
                            recipe_items = self.data['recipe_ingredients'][
                                self.data['recipe_ingredients']['recipe_id'] == recipe_id
                            ]
                            for _, ingredient in recipe_items.iterrows():
                                item_name = ingredient.get('item_name', '')
                                unit_price = self.get_ingredient_unit_price(item_name, ingredient.get('unit', ''))
                                if unit_price == 0:
                                    missing_ingredients.add(item_name)

                except Exception as e:
                    self.logger.error(f"Error calculating {recipe_name}: {e}")

            # Refresh all tables
            self.refresh_all_tables()

            # Show results
            if missing_ingredients:
                missing_list = list(missing_ingredients)[:10]
                missing_msg = f"Calculated {calculated_count}/{total_recipes} recipes.\n\nMissing ingredient prices for:\n" + "\n".join(missing_list)
                if len(missing_ingredients) > 10:
                    missing_msg += f"\n... and {len(missing_ingredients) - 10} more ingredients"
                missing_msg += "\n\nPlease provide inventory data with pricing information."
                notify_warning("Partial Success", missing_msg, parent=self)
            else:
                notify_success("Complete", f"Successfully calculated pricing for {calculated_count} recipes!", parent=self)

        except Exception as e:
            self.logger.error(f"Error in calculate_all_prices: {e}")
            notify_error("Error", f"Failed to calculate prices: {str(e)}", parent=self)
    
    def export_pricing_report(self):
        """Export comprehensive pricing report"""
        notify_info("Export", "Pricing report export feature coming soon", parent=self)
    
    def add_recipe_pricing(self):
        """Add pricing for a new recipe"""
        dialog = AddRecipePricingDialog(self.data, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            notify_success("Success", "Recipe pricing added successfully", parent=self)

    def open_bulk_editor(self):
        """Open bulk pricing editor"""
        try:
            from modules.bulk_pricing_editor import BulkPricingEditor

            # Create bulk editor dialog
            bulk_editor = BulkPricingEditor(self.data, self)
            bulk_editor.pricing_updated.connect(self.on_bulk_pricing_updated)

            # Show as dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Bulk Pricing Editor")
            dialog.setModal(True)
            dialog.resize(1200, 800)

            layout = QVBoxLayout(dialog)
            layout.addWidget(bulk_editor)

            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error opening bulk editor: {e}")
            notify_error("Error", f"Failed to open bulk editor: {str(e)}", parent=self)

    def open_advanced_analysis(self):
        """Open advanced cost analysis panel"""
        try:
            from modules.advanced_cost_analysis import AdvancedCostAnalysisPanel

            # Create analysis panel dialog
            analysis_panel = AdvancedCostAnalysisPanel(self.data, self)

            # Show as dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Advanced Cost Analysis")
            dialog.setModal(True)
            dialog.resize(1400, 900)

            layout = QVBoxLayout(dialog)
            layout.addWidget(analysis_panel)

            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error opening advanced analysis: {e}")
            notify_error("Error", f"Failed to open advanced analysis: {str(e)}", parent=self)

    def on_bulk_pricing_updated(self, updated_items):
        """Handle bulk pricing updates"""
        try:
            # Update data with new pricing
            for item in updated_items:
                self.logger.info(f"Updated pricing for {item['name']}: {item['old_price']} -> {item['new_price']}")

            # Refresh pricing data
            self.load_data()

            notify_success("Success", f"Updated pricing for {len(updated_items)} items", parent=self)

        except Exception as e:
            self.logger.error(f"Error handling bulk pricing updates: {e}")
            notify_error("Error", f"Failed to update pricing: {str(e)}", parent=self)
    
    def check_missing_items_manual(self):
        """Manually check for missing items and update missing items file"""
        try:
            from PySide6.QtWidgets import QMessageBox, QProgressDialog, QApplication

            # Show progress dialog
            progress = QProgressDialog("Scanning recipes for missing ingredients...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Checking Missing Items")
            progress.setModal(True)
            progress.setValue(10)
            progress.show()
            QApplication.processEvents()

            self.logger.info("🔍 Starting manual missing items check...")

            if 'recipes' not in self.data or self.data['recipes'].empty:
                progress.close()
                try:
                    notify_warning("No Recipes", "No recipes found to check for missing ingredients.", parent=self)
                except:
                    QMessageBox.warning(self, "No Recipes", "No recipes found to check for missing ingredients.")
                    self.logger.warning("No Recipes: No recipes found to check for missing ingredients.")
                return

            progress.setValue(30)
            QApplication.processEvents()

            recipes_df = self.data['recipes']
            total_missing_ingredients = 0
            affected_recipes = 0
            all_missing_data = {}

            # Clear existing missing items file
            missing_file = os.path.join('data', 'missing_ingredients.json')
            if os.path.exists(missing_file):
                os.remove(missing_file)

            # Check each recipe for missing ingredients
            total_recipes = len(recipes_df)
            processed_recipes = 0

            for _, recipe in recipes_df.iterrows():
                recipe_id = recipe.get('recipe_id', 0)
                recipe_name = recipe.get('recipe_name', f'Recipe {recipe_id}')

                # Update progress
                processed_recipes += 1
                progress_value = 30 + int((processed_recipes / total_recipes) * 50)  # 30-80% range
                progress.setValue(progress_value)
                progress.setLabelText(f"Processing recipe {processed_recipes}/{total_recipes}: {recipe_name}")
                QApplication.processEvents()

                # Get recipe ingredients
                if 'recipe_ingredients' not in self.data:
                    continue

                recipe_ingredients = self.data['recipe_ingredients'][
                    self.data['recipe_ingredients']['recipe_id'] == recipe_id
                ]

                self.logger.info(f"Checking recipe {recipe_id} ({recipe_name}) - found {len(recipe_ingredients)} ingredients")

                if recipe_ingredients.empty:
                    self.logger.info(f"  No ingredients found for recipe {recipe_id}, skipping")
                    continue

                # Debug: Check the DataFrame structure
                self.logger.info(f"  Recipe ingredients columns: {list(recipe_ingredients.columns)}")
                if not recipe_ingredients.empty:
                    self.logger.info(f"  First ingredient row: {recipe_ingredients.iloc[0].to_dict()}")

                missing_ingredients = []
                found_ingredients = []

                self.logger.info(f"  Starting ingredient loop for {len(recipe_ingredients)} ingredients")

                # Check each ingredient
                for idx, ingredient_row in recipe_ingredients.iterrows():
                    ingredient_name = ingredient_row.get('item_name', '').strip()
                    self.logger.info(f"  Processing ingredient {idx}: '{ingredient_name}'")

                    if not ingredient_name:
                        self.logger.info(f"  Skipping empty ingredient name")
                        continue

                    self.logger.info(f"  Checking ingredient: '{ingredient_name}'")

                    # 3-step validation as per user requirements:
                    # 1. Check if ingredient exists in items table (master catalog)
                    # 2. Check if ingredient is properly categorized
                    # 3. Check if ingredient exists in current inventory (quantity can be 0/negative)

                    step1_items_found = False
                    step2_categorized = False
                    step3_in_inventory = False
                    price_found = False
                    matched_item_name = ingredient_name

                    # STEP 1: Check Items Table (Master Catalog)
                    if 'items' in self.data and not self.data['items'].empty:
                        items_df = self.data['items']
                        self.logger.info(f"    Step 1: Checking items table ({len(items_df)} items)")

                        # Try exact match first
                        exact_match = items_df[items_df['item_name'].str.lower() == ingredient_name.lower()]
                        if not exact_match.empty:
                            step1_items_found = True
                            matched_item_name = exact_match.iloc[0]['item_name']
                            self.logger.info(f"    Step 1: [SUCCESS] Found exact match for '{ingredient_name}'")
                        else:
                            # Try partial match if exact match failed
                            partial_match = items_df[items_df['item_name'].str.lower().str.contains(ingredient_name.lower(), na=False)]
                            if not partial_match.empty:
                                step1_items_found = True
                                matched_item_name = partial_match.iloc[0]['item_name']
                                self.logger.info(f"    Step 1: [SUCCESS] Found partial match for '{ingredient_name}' -> '{matched_item_name}'")
                            else:
                                self.logger.info(f"    Step 1: [ERROR] Not found in items table")
                    else:
                        self.logger.info(f"    Step 1: [ERROR] Items table is empty or doesn't exist")

                    # STEP 2: Check if properly categorized
                    if step1_items_found:
                        if 'items' in self.data and not self.data['items'].empty:
                            items_df = self.data['items']
                            item_match = items_df[items_df['item_name'].str.lower() == matched_item_name.lower()]
                            if not item_match.empty:
                                category = item_match.iloc[0].get('category', '').strip()
                                if category and category.lower() not in ['', 'none', 'null', 'undefined']:
                                    step2_categorized = True
                                    self.logger.info(f"    Step 2: [SUCCESS] Item is categorized as '{category}'")
                                else:
                                    self.logger.info(f"    Step 2: [ERROR] Item has no valid category")
                            else:
                                self.logger.info(f"    Step 2: [ERROR] Could not find item for category check")
                    else:
                        self.logger.info(f"    Step 2: ⏭️ Skipped (not in items table)")

                    # STEP 3: Check if exists in current inventory (quantity can be 0 or negative)
                    if step1_items_found:
                        if 'inventory' in self.data and not self.data['inventory'].empty:
                            inventory_df = self.data['inventory']
                            self.logger.info(f"    Step 3: Checking inventory table ({len(inventory_df)} items)")

                            # Debug: Show first few inventory items for comparison
                            if len(inventory_df) > 0:
                                sample_items = inventory_df['item_name'].head(3).tolist()
                                self.logger.info(f"    Step 3: Sample inventory items: {sample_items}")

                            # Enhanced matching with multiple strategies
                            step3_in_inventory = False
                            current_qty = 0
                            inventory_item_name = matched_item_name

                            # Strategy 1: Exact match (case-insensitive)
                            try:
                                inventory_match = inventory_df[
                                    inventory_df['item_name'].str.lower().str.strip() == matched_item_name.lower().strip()
                                ]
                                if not inventory_match.empty:
                                    step3_in_inventory = True
                                    current_qty = inventory_match.iloc[0].get('quantity', 0)
                                    inventory_item_name = inventory_match.iloc[0]['item_name']
                                    self.logger.info(f"    Step 3: [SUCCESS] Found exact match in inventory: '{inventory_item_name}' with quantity: {current_qty}")
                            except Exception as e:
                                self.logger.warning(f"    Step 3: Error in exact match: {e}")

                            # Strategy 2: Partial match if exact match failed
                            if not step3_in_inventory:
                                try:
                                    inventory_partial = inventory_df[
                                        inventory_df['item_name'].str.lower().str.contains(
                                            matched_item_name.lower().strip(), na=False, regex=False
                                        )
                                    ]
                                    if not inventory_partial.empty:
                                        step3_in_inventory = True
                                        current_qty = inventory_partial.iloc[0].get('quantity', 0)
                                        inventory_item_name = inventory_partial.iloc[0]['item_name']
                                        self.logger.info(f"    Step 3: [SUCCESS] Found partial match in inventory: '{inventory_item_name}' with quantity: {current_qty}")
                                except Exception as e:
                                    self.logger.warning(f"    Step 3: Error in partial match: {e}")

                            # Strategy 3: Reverse partial match (ingredient name contains inventory item)
                            if not step3_in_inventory:
                                try:
                                    for _, inv_item in inventory_df.iterrows():
                                        inv_name = str(inv_item['item_name']).lower().strip()
                                        search_name = matched_item_name.lower().strip()
                                        if inv_name in search_name or search_name in inv_name:
                                            if len(inv_name) > 2 and len(search_name) > 2:  # Avoid very short matches
                                                step3_in_inventory = True
                                                current_qty = inv_item.get('quantity', 0)
                                                inventory_item_name = inv_item['item_name']
                                                self.logger.info(f"    Step 3: [SUCCESS] Found reverse match in inventory: '{inventory_item_name}' with quantity: {current_qty}")
                                                break
                                except Exception as e:
                                    self.logger.warning(f"    Step 3: Error in reverse match: {e}")

                            if not step3_in_inventory:
                                self.logger.info(f"    Step 3: ❌ Not found in inventory after trying all matching strategies")
                                self.logger.info(f"    Step 3: Searched for: '{matched_item_name}' (original: '{ingredient_name}')")
                        else:
                            self.logger.info(f"    Step 3: ❌ Inventory table is empty or doesn't exist")
                    else:
                        self.logger.info(f"    Step 3: ⏭️ Skipped (not in items table)")

                    # Check pricing data (for found items)
                    if step1_items_found:
                        if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                            shopping_df = self.data['shopping_list']
                            price_match = shopping_df[shopping_df['item_name'].str.lower() == matched_item_name.lower()]
                            if not price_match.empty and 'last_price' in price_match.columns:
                                price = price_match.iloc[0].get('last_price', 0)
                                if pd.notna(price) and price > 0:
                                    price_found = True
                                    self.logger.info(f"    Pricing: [SUCCESS] Found pricing for '{matched_item_name}': Rs.{price}")

                    # REVISED VALIDATION LOGIC: More intelligent missing item detection
                    # An item is considered "missing" only if it's truly unavailable for cooking

                    # Primary check: Is the ingredient available in some form?
                    ingredient_available = False
                    availability_source = ""

                    if step1_items_found and step2_categorized:
                        # If item is in catalog with category, check inventory availability
                        if step3_in_inventory:
                            ingredient_available = True
                            availability_source = "exact_inventory_match"
                        else:
                            # Even if not in current inventory, if it's in the items catalog
                            # it means we know about this ingredient and can potentially get it
                            # Only flag as missing if it's a critical ingredient that we absolutely need

                            # Check if this is a basic/common ingredient that should always be available
                            basic_ingredients = [
                                'salt', 'oil', 'water', 'onion', 'garlic', 'ginger',
                                'tomato', 'rice', 'flour', 'sugar', 'pepper', 'chili'
                            ]

                            ingredient_lower = ingredient_name.lower()
                            is_basic_ingredient = any(basic in ingredient_lower for basic in basic_ingredients)

                            if is_basic_ingredient:
                                # Basic ingredients should be flagged as missing if not in inventory
                                ingredient_available = False
                                availability_source = "basic_ingredient_missing_from_inventory"
                            else:
                                # Non-basic ingredients: if in catalog, consider available (can be purchased)
                                ingredient_available = True
                                availability_source = "in_catalog_can_be_purchased"
                    elif step1_items_found and not step2_categorized:
                        # Item in catalog but no category - consider available but needs categorization
                        ingredient_available = True
                        availability_source = "in_catalog_needs_category"
                    else:
                        # Item not in catalog at all - definitely missing
                        ingredient_available = False
                        availability_source = "not_in_catalog"

                    # Log the decision
                    if ingredient_available:
                        self.logger.info(f"    [SUCCESS] AVAILABLE: {availability_source}")
                        found_ingredients.append({
                            'name': ingredient_name,
                            'matched_item': matched_item_name if matched_item_name != ingredient_name else None,
                            'price': price if price_found else 0,
                            'source': availability_source
                        })
                    else:
                        self.logger.info(f"    ❌ MISSING: {availability_source}")

                        # Add to missing items only if truly unavailable
                        missing_ingredients.append({
                            'name': ingredient_name,
                            'quantity': ingredient_row.get('quantity', 0),
                            'unit': ingredient_row.get('unit', 'units'),
                            'reason': availability_source,
                            'matched_item': matched_item_name if step1_items_found and matched_item_name != ingredient_name else None,
                            'validation_details': {
                                'step1_items_found': step1_items_found,
                                'step2_categorized': step2_categorized,
                                'step3_in_inventory': step3_in_inventory
                            }
                        })

                # Store results if there are missing ingredients
                if missing_ingredients:
                    affected_recipes += 1
                    total_missing_ingredients += len(missing_ingredients)

                    all_missing_data[f"recipe_{recipe_id}"] = {
                        'recipe_id': recipe_id,
                        'recipe_name': recipe_name,
                        'missing_items': missing_ingredients,
                        'found_items': found_ingredients,
                        'last_checked': datetime.now().isoformat(),
                        'status': 'incomplete'
                    }

            # Save missing ingredients data
            if all_missing_data:
                os.makedirs('data', exist_ok=True)
                with open(missing_file, 'w') as f:
                    json.dump(all_missing_data, f, indent=2)

            # Enhanced debug logging
            self.logger.info(f"Missing items check results: total_missing={total_missing_ingredients}, affected_recipes={affected_recipes}")
            self.logger.info(f"Items table empty: {'items' not in self.data or self.data['items'].empty}")
            if 'items' in self.data:
                self.logger.info(f"Items table shape: {self.data['items'].shape}")
                if not self.data['items'].empty:
                    sample_items = self.data['items']['item_name'].head(5).tolist()
                    self.logger.info(f"Sample items from items table: {sample_items}")

            self.logger.info(f"Inventory table empty: {'inventory' not in self.data or self.data['inventory'].empty}")
            if 'inventory' in self.data:
                self.logger.info(f"Inventory table shape: {self.data['inventory'].shape}")
                if not self.data['inventory'].empty:
                    sample_inventory = self.data['inventory']['item_name'].head(5).tolist()
                    self.logger.info(f"Sample items from inventory table: {sample_inventory}")

            self.logger.info(f"Total recipes checked: {len(recipes_df)}")
            self.logger.info(f"Recipe ingredients table shape: {self.data['recipe_ingredients'].shape if 'recipe_ingredients' in self.data else 'N/A'}")

            # Show summary of validation failures
            if all_missing_data:
                failure_reasons = {}
                for recipe_key, recipe_data in all_missing_data.items():
                    for item in recipe_data.get('missing_items', []):
                        reason = item.get('reason', 'unknown')
                        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

                self.logger.info(f"Failure reasons summary: {failure_reasons}")

                # Show specific examples of failures
                for reason, count in failure_reasons.items():
                    self.logger.info(f"  {reason}: {count} items")
                    # Show first few examples
                    examples = []
                    for recipe_key, recipe_data in all_missing_data.items():
                        for item in recipe_data.get('missing_items', []):
                            if item.get('reason') == reason and len(examples) < 3:
                                examples.append(item.get('name', 'unknown'))
                    if examples:
                        self.logger.info(f"    Examples: {examples}")

            # Show results
            progress.setValue(90)
            QApplication.processEvents()

            if total_missing_ingredients > 0:
                progress.close()
                try:
                    notify_warning(
                        "Missing Items Found",
                        f"Found {total_missing_ingredients} missing ingredients across {affected_recipes} recipes.\n\nMissing items saved to: {missing_file}",
                        parent=self
                    )
                except:
                    QMessageBox.warning(self, "Missing Items Found",
                        f"Found {total_missing_ingredients} missing ingredients across {affected_recipes} recipes.\n\nMissing items saved to: {missing_file}")
                self.logger.warning(f"Missing ingredients check completed: {total_missing_ingredients} missing items in {affected_recipes} recipes")
            else:
                progress.close()
                try:
                    notify_success(
                        "All Items Available",
                        "All recipe ingredients are properly cataloged in the items table with pricing data!",
                        parent=self
                    )
                except:
                    QMessageBox.information(self, "All Items Available", "All recipe ingredients are properly cataloged in the items table with pricing data!")
                self.logger.info("Missing ingredients check completed: All items properly cataloged")

        except Exception as e:
            # Close progress dialog if it exists
            try:
                progress.close()
            except:
                pass

            self.logger.error(f"Error in manual missing items check: {e}")
            # Always use QMessageBox for error messages to avoid import issues
            QMessageBox.critical(self, "Error", f"Failed to check missing items: {e}")

    def refresh_calculations(self):
        """Refresh all pricing calculations"""
        self.load_data()

    def debug_missing_items_logic(self):
        """Debug function to test missing items logic with specific examples"""
        try:
            self.logger.info("🔍 DEBUG: Starting missing items logic debugging...")

            # Check data availability
            if 'recipe_ingredients' not in self.data or self.data['recipe_ingredients'].empty:
                self.logger.error("DEBUG: No recipe ingredients data available")
                return

            if 'items' not in self.data or self.data['items'].empty:
                self.logger.error("DEBUG: No items table data available")
                return

            if 'inventory' not in self.data or self.data['inventory'].empty:
                self.logger.error("DEBUG: No inventory data available")
                return

            # Get sample data
            recipe_ingredients = self.data['recipe_ingredients'].head(10)  # Test first 10 ingredients
            items_df = self.data['items']
            inventory_df = self.data['inventory']

            self.logger.info(f"DEBUG: Testing with {len(recipe_ingredients)} sample ingredients")
            self.logger.info(f"DEBUG: Items table has {len(items_df)} items")
            self.logger.info(f"DEBUG: Inventory table has {len(inventory_df)} items")

            # Test each ingredient
            for idx, ingredient_row in recipe_ingredients.iterrows():
                ingredient_name = ingredient_row.get('item_name', '').strip()
                self.logger.info(f"\n[DEBUG] Testing ingredient: '{ingredient_name}'")

                # Step 1: Items table check
                exact_match = items_df[items_df['item_name'].str.lower() == ingredient_name.lower()]
                step1_result = not exact_match.empty
                self.logger.info(f"  Step 1 (Items): {'[SUCCESS] PASS' if step1_result else '[ERROR] FAIL'}")

                if step1_result:
                    matched_item_name = exact_match.iloc[0]['item_name']

                    # Step 2: Category check
                    category = exact_match.iloc[0].get('category', '').strip()
                    step2_result = category and category.lower() not in ['', 'none', 'null', 'undefined']
                    self.logger.info(f"  Step 2 (Category): {'[SUCCESS] PASS' if step2_result else '[ERROR] FAIL'} - Category: '{category}'")

                    # Step 3: Inventory check
                    inventory_match = inventory_df[inventory_df['item_name'].str.lower() == matched_item_name.lower()]
                    step3_result = not inventory_match.empty
                    if step3_result:
                        qty = inventory_match.iloc[0].get('quantity', 0)
                        self.logger.info(f"  Step 3 (Inventory): [SUCCESS] PASS - Found with quantity: {qty}")
                    else:
                        self.logger.info(f"  Step 3 (Inventory): [ERROR] FAIL - Not found in inventory")
                        # Show what IS in inventory for comparison
                        inventory_sample = inventory_df['item_name'].head(5).tolist()
                        self.logger.info(f"    Inventory sample: {inventory_sample}")

                    # Final result
                    all_passed = step1_result and step2_result and step3_result
                    self.logger.info(f"  FINAL RESULT: {'[SUCCESS] FOUND' if all_passed else '[ERROR] MISSING'}")

                    if not all_passed:
                        failed_steps = []
                        if not step1_result: failed_steps.append("items_table")
                        if not step2_result: failed_steps.append("category")
                        if not step3_result: failed_steps.append("inventory")
                        self.logger.info(f"  Failed steps: {failed_steps}")
                else:
                    self.logger.info(f"  Steps 2-3: ⏭️ SKIPPED (not in items table)")
                    self.logger.info(f"  FINAL RESULT: ❌ MISSING (not in items table)")

            self.logger.info("🔍 DEBUG: Missing items logic debugging completed")

        except Exception as e:
            self.logger.error(f"Error in debug_missing_items_logic: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def show_cost_table_context_menu(self, position: QPoint):
        """Show context menu for cost analysis table"""
        item = self.cost_table.itemAt(position)
        if not item:
            return

        row = item.row()
        col = item.column()

        # Only show context menu for editable columns
        editable_columns = {
            2: "Others Pricing",  # Others Pricing column
            3: "Our Pricing",     # Our Pricing column
            7: "Other Charges"    # Other Charges column
        }

        if col not in editable_columns:
            return

        # Get recipe name
        recipe_name_item = self.cost_table.item(row, 0)
        if not recipe_name_item:
            return

        recipe_name = recipe_name_item.text()
        column_name = editable_columns[col]
        current_value = item.text().replace('Rs.', '').replace('₹', '').replace(',', '').strip()

        # Create context menu
        menu = QMenu(self)

        edit_action = QAction(f"Edit {column_name}", self)
        edit_action.triggered.connect(lambda: self.edit_pricing_value(
            recipe_name, column_name, current_value, row, col, self.cost_table
        ))
        menu.addAction(edit_action)

        # Show menu
        menu.exec(self.cost_table.mapToGlobal(position))

    def show_pricing_table_context_menu(self, position: QPoint):
        """Show context menu for pricing strategy table"""
        item = self.pricing_table.itemAt(position)
        if not item:
            return

        row = item.row()
        col = item.column()

        # Only show context menu for editable columns
        editable_columns = {
            2: "Others Pricing",  # Others Pricing column
            4: "Our Pricing",     # Our Pricing column
        }

        if col not in editable_columns:
            return

        # Get recipe name
        recipe_name_item = self.pricing_table.item(row, 0)
        if not recipe_name_item:
            return

        recipe_name = recipe_name_item.text()
        column_name = editable_columns[col]
        current_value = item.text().replace('Rs.', '').replace('₹', '').replace(',', '').strip()

        # Create context menu
        menu = QMenu(self)

        edit_action = QAction(f"Edit {column_name}", self)
        edit_action.triggered.connect(lambda: self.edit_pricing_value(
            recipe_name, column_name, current_value, row, col, self.pricing_table
        ))
        menu.addAction(edit_action)

        # Show menu
        menu.exec(self.pricing_table.mapToGlobal(position))

    def show_profit_table_context_menu(self, position: QPoint):
        """Show context menu for profit analysis table"""
        item = self.profit_table.itemAt(position)
        if not item:
            return

        row = item.row()
        col = item.column()

        # Only show context menu for selling price column (which represents "Our Pricing")
        if col != 1:  # Selling Price column
            return

        # Get recipe name
        recipe_name_item = self.profit_table.item(row, 0)
        if not recipe_name_item:
            return

        recipe_name = recipe_name_item.text()
        current_value = item.text().replace('Rs.', '').replace('₹', '').replace(',', '').strip()

        # Create context menu
        menu = QMenu(self)

        edit_action = QAction("Edit Our Pricing", self)
        edit_action.triggered.connect(lambda: self.edit_pricing_value(
            recipe_name, "Our Pricing", current_value, row, col, self.profit_table
        ))
        menu.addAction(edit_action)

        # Show menu
        menu.exec(self.profit_table.mapToGlobal(position))

    def edit_pricing_value(self, recipe_name, field_name, current_value, row, col, table):
        """Edit pricing value with input dialog"""
        try:
            # Parse current value
            try:
                current_float = float(current_value) if current_value else 0.0
            except ValueError:
                current_float = 0.0

            # Show input dialog
            new_value, ok = QInputDialog.getDouble(
                self,
                f"Edit {field_name}",
                f"Enter new {field_name.lower()} for {recipe_name}:",
                current_float,
                0.0,
                99999.99,
                2
            )

            if ok:
                # Update the table cell
                table.setItem(row, col, QTableWidgetItem(f"Rs.{new_value:.2f}"))

                # Update the underlying data
                self.update_recipe_pricing_data(recipe_name, field_name, new_value)

                # Emit signal for real-time updates
                self.pricing_updated.emit(recipe_name, field_name, new_value)

                # Refresh all calculations and tables
                self.refresh_all_pricing_displays()

                # Show success notification
                notify_success(
                    "Pricing Updated",
                    f"Updated {field_name.lower()} for {recipe_name} to Rs.{new_value:.2f}",
                    parent=self
                )

        except Exception as e:
            self.logger.error(f"Error editing pricing value: {e}")
            notify_error("Error", f"Failed to update pricing: {str(e)}", parent=self)

    def update_recipe_pricing_data(self, recipe_name, field_name, new_value):
        """Update recipe pricing data in memory and persist to file"""
        try:
            # Update in-memory data
            if recipe_name in self.recipe_pricing_data:
                if field_name == "Others Pricing":
                    self.recipe_pricing_data[recipe_name]["others_pricing"] = new_value
                elif field_name == "Our Pricing":
                    self.recipe_pricing_data[recipe_name]["our_pricing"] = new_value
                elif field_name == "Other Charges":
                    # Store other charges separately if needed
                    if "other_charges" not in self.recipe_pricing_data[recipe_name]:
                        self.recipe_pricing_data[recipe_name]["other_charges"] = new_value
                    else:
                        self.recipe_pricing_data[recipe_name]["other_charges"] = new_value

            # Update CSV file
            self.save_pricing_data_to_csv()

            # Update JavaScript file for consistency
            self.update_javascript_pricing_data()

            self.logger.info(f"Updated {field_name} for {recipe_name} to {new_value}")

        except Exception as e:
            self.logger.error(f"Error updating recipe pricing data: {e}")
            raise

    def save_pricing_data_to_csv(self):
        """Save current pricing data to CSV file"""
        try:
            import os

            # Prepare data for CSV - use the same format as the main app expects
            csv_data = []
            for recipe_name, data in self.recipe_pricing_data.items():
                csv_data.append({
                    'recipe_id': recipe_name.lower().replace(' ', '_'),  # Generate ID from name
                    'recipe_name': recipe_name,
                    'total_cost': self.calculate_total_cost_for_recipe(recipe_name),
                    'cost_per_serving': self.calculate_cost_per_serving(recipe_name),
                    'others_pricing': data.get('others_pricing', 0),
                    'our_pricing': data.get('our_pricing', 0),
                    'cooking_time': data.get('cooking_time', ''),
                    'other_charges': data.get('other_charges', 2.0),  # Default 2 rupees
                    'last_calculated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            # Create DataFrame and save to CSV
            df = pd.DataFrame(csv_data)

            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)

            # Save to the main pricing CSV file that the app loads from
            csv_path = os.path.join('data', 'pricing.csv')
            df.to_csv(csv_path, index=False)

            # Also save to the backup file for compatibility
            backup_path = os.path.join('data', 'updated_pricing_data.csv')
            df.to_csv(backup_path, index=False)

            self.logger.info(f"Saved pricing data to {csv_path} and {backup_path}")

        except Exception as e:
            self.logger.error(f"Error saving pricing data to CSV: {e}")

    def calculate_total_cost_for_recipe(self, recipe_name):
        """Calculate total cost for a recipe"""
        try:
            if recipe_name in self.recipe_pricing_data:
                data = self.recipe_pricing_data[recipe_name]
                # Basic cost calculation - can be enhanced
                base_cost = 10.0  # Default base cost
                other_charges = data.get('other_charges', 2.0)
                return base_cost + other_charges
            return 10.0
        except:
            return 10.0

    def calculate_cost_per_serving(self, recipe_name):
        """Calculate cost per serving for a recipe"""
        try:
            total_cost = self.calculate_total_cost_for_recipe(recipe_name)
            # Assume 1 serving by default - can be enhanced with actual serving data
            return total_cost
        except:
            return 10.0

    def update_javascript_pricing_data(self):
        """Update JavaScript pricing data file for consistency"""
        try:
            js_file_path = 'pricing_formulas.js'

            if not os.path.exists(js_file_path):
                self.logger.warning(f"JavaScript file {js_file_path} not found, skipping update")
                return

            # Read current JavaScript file
            with open(js_file_path, 'r', encoding='utf-8') as f:
                js_content = f.read()

            # Generate new JavaScript object
            js_data_lines = []
            js_data_lines.append("const RECIPE_PRICING_DATA = {")

            for recipe_name, data in self.recipe_pricing_data.items():
                others_pricing = data.get('others_pricing', 'null')
                our_pricing = data.get('our_pricing', 0)
                cooking_time = data.get('cooking_time', '15 mins')

                js_data_lines.append(f'    "{recipe_name}": {{ others_pricing: {others_pricing}, our_pricing: {our_pricing}, cooking_time: "{cooking_time}" }},')

            js_data_lines.append("};")

            # Replace the RECIPE_PRICING_DATA section
            import re
            pattern = r'const RECIPE_PRICING_DATA = \{[^}]*\};'
            new_js_content = re.sub(pattern, '\n'.join(js_data_lines), js_content, flags=re.DOTALL)

            # Write back to file
            with open(js_file_path, 'w', encoding='utf-8') as f:
                f.write(new_js_content)

            self.logger.info("Updated JavaScript pricing data file")

        except Exception as e:
            self.logger.error(f"Error updating JavaScript pricing data: {e}")

    def refresh_all_pricing_displays(self):
        """Refresh all pricing displays with updated data"""
        try:
            # Reload data to reflect changes
            self.load_data()

            # Update overview cards
            self.update_overview_cards()

            self.logger.info("Refreshed all pricing displays")

        except Exception as e:
            self.logger.error(f"Error refreshing pricing displays: {e}")

    def reload_pricing_data_from_csv(self):
        """Reload pricing data from CSV files to get latest updates"""
        try:
            import os
            import pandas as pd

            pricing_csv_path = os.path.join('data', 'pricing.csv')
            if os.path.exists(pricing_csv_path):
                pricing_df = pd.read_csv(pricing_csv_path)
                self.logger.info(f"Reloading pricing data from {pricing_csv_path}")

                # Clear existing data
                self.recipe_pricing_data.clear()

                # Load fresh data from CSV
                for _, row in pricing_df.iterrows():
                    recipe_name = row.get('recipe_name', '')
                    if recipe_name:
                        self.recipe_pricing_data[recipe_name] = {
                            'others_pricing': float(row.get('others_pricing', 0)),
                            'our_pricing': float(row.get('our_pricing', 0)),
                            'cooking_time': str(row.get('cooking_time', '')),
                            'other_charges': float(row.get('other_charges', 2.0))
                        }

                self.logger.info(f"Reloaded {len(self.recipe_pricing_data)} recipes from CSV")

                # Refresh all displays with new data
                self.refresh_all_pricing_displays()

                return True

        except Exception as e:
            self.logger.error(f"Error reloading pricing data from CSV: {e}")
            return False


class AddRecipePricingDialog(QDialog):
    """Dialog for adding recipe pricing"""
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Add Recipe Pricing")
        self.setFixedSize(600, 700)
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Recipe selection
        recipe_group = QGroupBox("Recipe Selection")
        recipe_layout = QFormLayout(recipe_group)
        
        self.recipe_combo = QComboBox()
        if 'recipes' in self.data and not self.data['recipes'].empty:
            recipes = self.data['recipes']['recipe_name'].tolist()
            self.recipe_combo.addItems(recipes)
        recipe_layout.addRow("Recipe:", self.recipe_combo)
        
        layout.addWidget(recipe_group)
        
        # Cost inputs
        cost_group = QGroupBox("Cost Details")
        cost_layout = QFormLayout(cost_group)
        
        self.making_cost_edit = QDoubleSpinBox()
        self.making_cost_edit.setMaximum(9999.99)
        self.making_cost_edit.setValue(10.0)
        cost_layout.addRow("Making Cost:", self.making_cost_edit)
        
        self.packaging_cost_edit = QDoubleSpinBox()
        self.packaging_cost_edit.setMaximum(9999.99)
        self.packaging_cost_edit.setValue(5.0)
        cost_layout.addRow("Packaging Cost:", self.packaging_cost_edit)
        
        self.other_charges_edit = QDoubleSpinBox()
        self.other_charges_edit.setMaximum(9999.99)
        self.other_charges_edit.setValue(2.0)
        cost_layout.addRow("Other Charges:", self.other_charges_edit)
        
        layout.addWidget(cost_group)
        
        # Pricing inputs
        pricing_group = QGroupBox("Pricing Strategy")
        pricing_layout = QFormLayout(pricing_group)
        
        self.others_pricing_edit = QDoubleSpinBox()
        self.others_pricing_edit.setMaximum(9999.99)
        self.others_pricing_edit.setValue(100.0)
        pricing_layout.addRow("Others Pricing:", self.others_pricing_edit)
        
        self.margin_edit = QDoubleSpinBox()
        self.margin_edit.setMaximum(100.0)
        self.margin_edit.setValue(30.0)
        self.margin_edit.setSuffix("%")
        pricing_layout.addRow("Margin %:", self.margin_edit)
        
        layout.addWidget(pricing_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept(self):
        """Save the recipe pricing"""
        try:
            # Implementation for saving recipe pricing
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save pricing: {str(e)}")
