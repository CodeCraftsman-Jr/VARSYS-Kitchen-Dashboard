"""
Enhanced Budget Module with Expense Tracking Integration
Modern UI with comprehensive budget management and shopping integration
"""

import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel,
                             QTabWidget, QGroupBox, QFormLayout, QLineEdit,
                             QSpinBox, QTextEdit, QPushButton, QDialog,
                             QDialogButtonBox, QMessageBox, QSplitter,
                             QComboBox, QDateEdit, QDoubleSpinBox, QGridLayout,
                             QFrame, QScrollArea, QProgressBar, QCheckBox)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

# Import notification system
try:
    from .notification_system import notify_info, notify_success, notify_warning, notify_error
except ImportError:
    def notify_info(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_success(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_warning(title, message, **kwargs): logging.warning(f"{title}: {message}")
    def notify_error(title, message, **kwargs): logging.error(f"{title}: {message}")

class BudgetProgressCard(QFrame):
    """Budget progress card with visual progress bar"""
    
    def __init__(self, category, budget_amount, spent_amount, parent=None):
        super().__init__(parent)
        self.category = category
        self.budget_amount = budget_amount
        self.spent_amount = spent_amount
        
        self.setFixedHeight(140)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: rgba(59, 130, 246, 0.05);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Category name
        category_label = QLabel(category)
        category_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #0f172a;")
        layout.addWidget(category_label)
        
        # Budget vs Spent
        budget_label = QLabel(f"Budget: ₹{budget_amount:,.2f}")
        budget_label.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(budget_label)
        
        spent_label = QLabel(f"Spent: ₹{spent_amount:,.2f}")
        spent_label.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(spent_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(int(budget_amount * 100))
        progress.setValue(int(spent_amount * 100))
        
        # Color based on usage
        percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        if percentage > 90:
            color = "#ef4444"  # Red
        elif percentage > 75:
            color = "#f59e0b"  # Amber
        else:
            color = "#10b981"  # Green
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color: #f1f5f9;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)
        
        layout.addWidget(progress)
        
        # Remaining amount
        remaining = budget_amount - spent_amount
        remaining_label = QLabel(f"Remaining: ₹{remaining:,.2f}")
        remaining_label.setStyleSheet(f"font-size: 12px; font-weight: 500; color: {color};")
        layout.addWidget(remaining_label)

class EnhancedBudgetWidget(QWidget):
    """Enhanced budget widget with expense tracking integration"""
    
    data_changed = Signal()
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI
        self.init_ui()
        self.load_data()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Budget Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        sync_expenses_btn = QPushButton("Sync Shopping Expenses")
        sync_expenses_btn.setStyleSheet("background-color: #10b981; color: white;")
        sync_expenses_btn.clicked.connect(self.sync_shopping_expenses)
        header_layout.addWidget(sync_expenses_btn)
        
        add_budget_btn = QPushButton("Add Budget Category")
        add_budget_btn.clicked.connect(self.add_budget_category)
        header_layout.addWidget(add_budget_btn)
        
        layout.addLayout(header_layout)
        
        # Budget overview cards
        self.create_budget_overview(layout)
        
        # Main content tabs
        self.create_tabs_section(layout)
    
    def create_budget_overview(self, parent_layout):
        """Create budget overview cards"""
        overview_frame = QFrame()
        overview_frame.setStyleSheet("background: transparent; border: none;")
        
        self.overview_layout = QGridLayout(overview_frame)
        self.overview_layout.setSpacing(16)
        
        parent_layout.addWidget(overview_frame)
    
    def create_tabs_section(self, parent_layout):
        """Create tabbed interface"""
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
        
        # Budget Allocation Tab
        self.create_allocation_tab()
        
        # Expense Tracking Tab
        self.create_expense_tracking_tab()
        
        # Shopping Integration Tab
        self.create_shopping_integration_tab()
        
        # Reports Tab
        self.create_reports_tab()
        
        parent_layout.addWidget(self.tabs)
    
    def create_allocation_tab(self):
        """Create enhanced budget allocation tab with Kitchen Essentials and other categories"""
        allocation_widget = QWidget()
        layout = QVBoxLayout(allocation_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header with add category button
        header_layout = QHBoxLayout()
        header_label = QLabel("Budget Categories")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Add Category button
        add_category_btn = QPushButton("➕ Add Category")
        add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        add_category_btn.clicked.connect(self.show_add_category_dialog)
        header_layout.addWidget(add_category_btn)
        layout.addLayout(header_layout)

        # Enhanced budget allocation table
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(7)
        self.budget_table.setHorizontalHeaderLabels([
            "Category", "Amount Allocated", "Amount Spent", "Amount Balance", "% Used", "Status", "Actions"
        ])

        # Style the table
        self.budget_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 12px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 25px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)

        # Enable manual column resizing with proper default widths
        header = self.budget_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        for col in range(7):
            header.setSectionResizeMode(col, QHeaderView.Interactive)

        # Set default column widths for better initial display (increased to prevent overlapping)
        budget_default_widths = {
            0: 220,  # Category (hierarchical display)
            1: 130,  # Amount Allocated
            2: 130,  # Amount Spent
            3: 130,  # Amount Balance
            4: 90,   # % Used
            5: 120,  # Status (increased to prevent overlap)
            6: 120   # Actions (Delete button) (increased for better button display)
        }

        # Apply default widths
        for col_index, width in budget_default_widths.items():
            self.budget_table.setColumnWidth(col_index, width)

        # Enable auto-fit functionality (double-click column borders to auto-fit)
        header.sectionDoubleClicked.connect(self.auto_fit_column)

        layout.addWidget(self.budget_table)
        
        self.tabs.addTab(allocation_widget, "Budget Allocation")

    def auto_fit_column(self, logical_index):
        """Auto-fit column width to content when header is double-clicked"""
        try:
            self.budget_table.resizeColumnToContents(logical_index)
            print(f"🔧 Auto-fitted budget column {logical_index} to content")
        except Exception as e:
            print(f"Error auto-fitting budget column {logical_index}: {e}")

    def auto_fit_expense_column(self, logical_index):
        """Auto-fit expense table column width to content when header is double-clicked"""
        try:
            self.expense_table.resizeColumnToContents(logical_index)
            print(f"🔧 Auto-fitted expense column {logical_index} to content")
        except Exception as e:
            print(f"Error auto-fitting expense column {logical_index}: {e}")
    
    def create_expense_tracking_tab(self):
        """Create enhanced expense tracking tab with transaction history"""
        expense_widget = QWidget()
        layout = QVBoxLayout(expense_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header with summary cards
        summary_layout = QHBoxLayout()

        # Total Expenses Card
        total_card = QFrame()
        total_card.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        total_layout = QVBoxLayout(total_card)
        total_title = QLabel("Total Expenses")
        total_title.setStyleSheet("font-weight: bold; color: #374151;")
        self.total_expenses_label = QLabel("₹0.00")
        self.total_expenses_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #059669;")
        total_layout.addWidget(total_title)
        total_layout.addWidget(self.total_expenses_label)
        summary_layout.addWidget(total_card)

        # This Month Card
        month_card = QFrame()
        month_card.setStyleSheet(total_card.styleSheet())
        month_layout = QVBoxLayout(month_card)
        month_title = QLabel("This Month")
        month_title.setStyleSheet("font-weight: bold; color: #374151;")
        self.month_expenses_label = QLabel("₹0.00")
        self.month_expenses_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #dc2626;")
        month_layout.addWidget(month_title)
        month_layout.addWidget(self.month_expenses_label)
        summary_layout.addWidget(month_card)

        # Budget Remaining Card
        remaining_card = QFrame()
        remaining_card.setStyleSheet(total_card.styleSheet())
        remaining_layout = QVBoxLayout(remaining_card)
        remaining_title = QLabel("Budget Remaining")
        remaining_title.setStyleSheet("font-weight: bold; color: #374151;")
        self.remaining_budget_label = QLabel("₹0.00")
        self.remaining_budget_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")
        remaining_layout.addWidget(remaining_title)
        remaining_layout.addWidget(self.remaining_budget_label)
        summary_layout.addWidget(remaining_card)

        layout.addLayout(summary_layout)

        # Expense tracking table
        table_header = QLabel("Transaction History")
        table_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151; margin-top: 20px;")
        layout.addWidget(table_header)

        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(8)
        self.expense_table.setHorizontalHeaderLabels([
            "Date", "Category", "Description", "Amount", "Type", "Source", "Receipt", "Notes"
        ])

        # Apply modern styling
        self.expense_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 12px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 25px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)

        # Enable manual column resizing for expense table
        header = self.expense_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        for col in range(8):
            header.setSectionResizeMode(col, QHeaderView.Interactive)

        # Set default column widths for expense table
        expense_default_widths = {
            0: 100,  # Date
            1: 120,  # Category
            2: 200,  # Description
            3: 100,  # Amount
            4: 80,   # Type
            5: 100,  # Source
            6: 80,   # Receipt
            7: 150   # Notes
        }

        # Apply default widths
        for col_index, width in expense_default_widths.items():
            self.expense_table.setColumnWidth(col_index, width)

        # Enable auto-fit functionality for expense table
        header.sectionDoubleClicked.connect(self.auto_fit_expense_column)

        layout.addWidget(self.expense_table)

        # Action buttons
        button_layout = QHBoxLayout()

        # Add Manual Expense button
        add_expense_btn = QPushButton("➕ Add Manual Expense")
        add_expense_btn.setStyleSheet("""
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
        add_expense_btn.clicked.connect(self.add_manual_expense)

        # Add Repair/Bills Transaction button
        add_transaction_btn = QPushButton("🔧 Add Repair/Bills")
        add_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        add_transaction_btn.clicked.connect(self.add_repair_bills_transaction)

        button_layout.addStretch()
        button_layout.addWidget(add_transaction_btn)
        button_layout.addWidget(add_expense_btn)
        layout.addLayout(button_layout)

        self.tabs.addTab(expense_widget, "Transaction Tracking")
    
    def create_shopping_integration_tab(self):
        """Create shopping integration tab"""
        shopping_widget = QWidget()
        layout = QVBoxLayout(shopping_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Integration settings
        settings_frame = QFrame()
        settings_frame.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;")
        settings_layout = QVBoxLayout(settings_frame)
        
        title_label = QLabel("Shopping Integration Settings")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 16px;")
        settings_layout.addWidget(title_label)
        
        # Auto-sync checkbox
        self.auto_sync_checkbox = QCheckBox("Automatically sync shopping expenses to budget")
        self.auto_sync_checkbox.setChecked(True)
        settings_layout.addWidget(self.auto_sync_checkbox)
        
        # Category mapping
        mapping_label = QLabel("Category Mapping:")
        mapping_label.setStyleSheet("font-size: 14px; font-weight: 500; margin-top: 16px;")
        settings_layout.addWidget(mapping_label)
        
        # Category mapping table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["Shopping Category", "Budget Category"])
        self.mapping_table.setMaximumHeight(200)
        settings_layout.addWidget(self.mapping_table)
        
        layout.addWidget(settings_frame)
        layout.addStretch()
        
        self.tabs.addTab(shopping_widget, "Shopping Integration")
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Report generation section
        reports_frame = QFrame()
        reports_frame.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;")
        reports_layout = QVBoxLayout(reports_frame)
        
        title_label = QLabel("Budget Reports")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 16px;")
        reports_layout.addWidget(title_label)
        
        # Report buttons
        buttons_layout = QGridLayout()
        
        monthly_budget_btn = QPushButton("Monthly Budget Report")
        expense_analysis_btn = QPushButton("Expense Analysis")
        variance_report_btn = QPushButton("Budget Variance Report")
        category_breakdown_btn = QPushButton("Category Breakdown")
        
        for btn in [monthly_budget_btn, expense_analysis_btn, variance_report_btn, category_breakdown_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8fafc;
                    color: #374151;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: 500;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                    border-color: #cbd5e1;
                }
            """)
        
        buttons_layout.addWidget(monthly_budget_btn, 0, 0)
        buttons_layout.addWidget(expense_analysis_btn, 0, 1)
        buttons_layout.addWidget(variance_report_btn, 1, 0)
        buttons_layout.addWidget(category_breakdown_btn, 1, 1)
        
        reports_layout.addLayout(buttons_layout)
        layout.addWidget(reports_frame)
        layout.addStretch()
        
        self.tabs.addTab(reports_widget, "Reports")
    
    def load_data(self):
        """Load and display budget data"""
        try:
            self.populate_budget_overview()
            self.populate_budget_table()
            self.populate_expense_table()
            self.populate_category_mapping()
        except Exception as e:
            self.logger.error(f"Error loading budget data: {e}")
            notify_error("Error", f"Failed to load budget data: {str(e)}", parent=self)
    
    def populate_budget_overview(self):
        """Populate budget overview cards"""
        try:
            # Clear existing cards
            for i in reversed(range(self.overview_layout.count())):
                self.overview_layout.itemAt(i).widget().setParent(None)
            
            if 'budget' in self.data and not self.data['budget'].empty:
                budget_df = self.data['budget']
                
                col = 0
                for _, budget in budget_df.iterrows():
                    category = budget.get('category', 'Unknown')
                    budget_amount = budget.get('budget_amount', 0)
                    actual_amount = budget.get('actual_amount', 0)
                    
                    card = BudgetProgressCard(category, budget_amount, actual_amount)
                    self.overview_layout.addWidget(card, 0, col)
                    col += 1
                    
                    if col >= 4:  # Max 4 cards per row
                        break
        except Exception as e:
            self.logger.error(f"Error populating budget overview: {e}")
    
    def populate_budget_table(self):
        """Populate enhanced budget allocation table with hierarchical structure"""
        try:
            # Clear existing data
            self.budget_table.setRowCount(0)

            # Initialize default categories if budget is empty
            self.initialize_default_budget_categories()

            if 'budget' not in self.data or self.data['budget'].empty:
                return

            # Get inventory categories for Kitchen Essentials subcategories
            inventory_categories = self.get_inventory_categories()

            # Organize budget data
            budget_df = self.data['budget']
            organized_budget = self.organize_budget_data(budget_df, inventory_categories)

            # Populate table with hierarchical structure
            row = 0
            for main_category, subcategories in organized_budget.items():
                if main_category == "Kitchen Essentials":
                    # Add Kitchen Essentials parent category
                    self.add_hierarchical_budget_row(row, main_category,
                                                   subcategories.get('total_allocated', 0),
                                                   subcategories.get('total_spent', 0),
                                                   is_parent=True, category_id=None)
                    row += 1

                    # Add subcategories as actual budget entries
                    for subcat_name, subcat_data in subcategories.get('subcategories', {}).items():
                        self.add_hierarchical_budget_row(row, f"  └─ {subcat_name}",
                                                       subcat_data.get('allocated', 0),
                                                       subcat_data.get('spent', 0),
                                                       is_parent=False,
                                                       category_id=subcat_data.get('budget_id'))
                        row += 1
                else:
                    # Add regular categories as budget entries
                    self.add_hierarchical_budget_row(row, main_category,
                                                   subcategories.get('allocated', 0),
                                                   subcategories.get('spent', 0),
                                                   is_parent=False,
                                                   category_id=subcategories.get('budget_id'))
                    row += 1

        except Exception as e:
            self.logger.error(f"Error populating budget table: {e}")

    def add_hierarchical_budget_row(self, row, category_name, allocated, spent, is_parent=False, category_id=None):
        """Add a hierarchical budget row with proper styling and delete functionality"""
        try:
            self.budget_table.insertRow(row)

            # Category name with hierarchical styling
            category_item = QTableWidgetItem(category_name)
            if is_parent:
                # Parent category styling
                category_item.setBackground(QColor(248, 250, 252))  # Light gray background
                font = category_item.font()
                font.setBold(True)
                category_item.setFont(font)
                category_item.setForeground(QColor(55, 65, 81))  # Dark gray text
            else:
                # Child category styling
                category_item.setForeground(QColor(107, 114, 128))  # Medium gray text

            self.budget_table.setItem(row, 0, category_item)

            # Calculate balance and percentage
            balance = allocated - spent
            percentage = (spent / allocated * 100) if allocated > 0 else 0

            # Amount Allocated
            allocated_item = QTableWidgetItem(f"₹{allocated:.2f}")
            allocated_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(row, 1, allocated_item)

            # Amount Spent
            spent_item = QTableWidgetItem(f"₹{spent:.2f}")
            spent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if spent > allocated:
                spent_item.setForeground(QColor(220, 38, 38))  # Red for overspent
            self.budget_table.setItem(row, 2, spent_item)

            # Amount Balance
            balance_item = QTableWidgetItem(f"₹{balance:.2f}")
            balance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if balance < 0:
                balance_item.setForeground(QColor(220, 38, 38))  # Red for negative balance
            else:
                balance_item.setForeground(QColor(34, 197, 94))  # Green for positive balance
            self.budget_table.setItem(row, 3, balance_item)

            # Percentage Used
            percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            percentage_item.setTextAlignment(Qt.AlignCenter)
            if percentage > 100:
                percentage_item.setForeground(QColor(220, 38, 38))  # Red for over budget
            elif percentage > 80:
                percentage_item.setForeground(QColor(245, 158, 11))  # Orange for warning
            else:
                percentage_item.setForeground(QColor(34, 197, 94))  # Green for good
            self.budget_table.setItem(row, 4, percentage_item)

            # Status
            if percentage > 100:
                status = "Over Budget"
                status_color = QColor(220, 38, 38)
            elif percentage > 80:
                status = "Warning"
                status_color = QColor(245, 158, 11)
            else:
                status = "On Track"
                status_color = QColor(34, 197, 94)

            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(status_color)
            self.budget_table.setItem(row, 5, status_item)

            # Actions (Delete button) - only for non-parent categories
            if not is_parent and category_id:
                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("Delete this budget category")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 2px 6px;
                        font-size: 10px;
                        max-width: 30px;
                        max-height: 25px;
                        min-width: 30px;
                        min-height: 25px;
                    }
                    QPushButton:hover {
                        background-color: #b91c1c;
                    }
                """)
                delete_btn.clicked.connect(lambda: self.delete_budget_category(category_id, category_name))
                self.budget_table.setCellWidget(row, 6, delete_btn)
            else:
                # Empty cell for parent categories
                self.budget_table.setItem(row, 6, QTableWidgetItem(""))

        except Exception as e:
            self.logger.error(f"Error adding hierarchical budget row: {e}")

    def delete_budget_category(self, category_id, category_name):
        """Delete a budget category with confirmation"""
        try:
            from PySide6.QtWidgets import QMessageBox

            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Delete Budget Category",
                f"Are you sure you want to delete the budget category '{category_name}'?\n\n"
                f"This action cannot be undone and will remove all associated data.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove from budget dataframe
                if 'budget' in self.data and not self.data['budget'].empty:
                    budget_df = self.data['budget']
                    budget_df = budget_df[budget_df['budget_id'] != category_id]
                    self.data['budget'] = budget_df

                    # Save to CSV
                    budget_file = os.path.join('data', 'budget.csv')
                    budget_df.to_csv(budget_file, index=False)

                    # Refresh the table
                    self.populate_budget_table()

                    # Show success message
                    QMessageBox.information(
                        self,
                        "Category Deleted",
                        f"Budget category '{category_name}' has been successfully deleted."
                    )

                    print(f"✅ Deleted budget category: {category_name} (ID: {category_id})")

        except Exception as e:
            self.logger.error(f"Error deleting budget category: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to delete budget category: {str(e)}"
            )

    def initialize_default_budget_categories(self):
        """Initialize default budget categories if they don't exist"""
        try:
            if 'budget' not in self.data:
                self.data['budget'] = pd.DataFrame(columns=[
                    'budget_id', 'category', 'budget_amount', 'actual_amount', 'period', 'notes'
                ])

            budget_df = self.data['budget']
            default_categories = {
                'Repairs': 2000.0,
                'Bills': 3000.0,
                'Kitchen Equipment': 1500.0,
                'Utilities': 2500.0,
                'Maintenance': 1000.0
            }

            # Add missing default categories
            for category, default_amount in default_categories.items():
                if budget_df.empty or len(budget_df[budget_df['category'] == category]) == 0:
                    new_budget = pd.DataFrame({
                        'budget_id': [len(budget_df) + 1],
                        'category': [category],
                        'budget_amount': [default_amount],
                        'actual_amount': [0.0],
                        'period': ['Monthly'],
                        'notes': ['Default category']
                    })
                    budget_df = pd.concat([budget_df, new_budget], ignore_index=True)

            self.data['budget'] = budget_df

            # Save to CSV
            budget_file = os.path.join('data', 'budget.csv')
            budget_df.to_csv(budget_file, index=False)

        except Exception as e:
            self.logger.error(f"Error initializing default budget categories: {e}")

    def get_inventory_categories(self):
        """Get inventory categories for Kitchen Essentials subcategories"""
        try:
            if 'categories' in self.data and not self.data['categories'].empty:
                return self.data['categories']['category_name'].tolist()
            return []
        except Exception as e:
            self.logger.error(f"Error getting inventory categories: {e}")
            return []

    def organize_budget_data(self, budget_df, inventory_categories):
        """Organize budget data into main categories and subcategories"""
        try:
            organized = {}

            # Kitchen Essentials - group inventory categories
            kitchen_essentials = {
                'total_allocated': 0,
                'total_spent': 0,
                'subcategories': {}
            }

            # Process each budget category
            for _, budget in budget_df.iterrows():
                category = budget.get('category', '')
                allocated = budget.get('budget_amount', 0)
                spent = budget.get('actual_amount', 0)
                budget_id = budget.get('budget_id', None)

                # Check if this category should be under Kitchen Essentials
                if category in inventory_categories:
                    kitchen_essentials['total_allocated'] += allocated
                    kitchen_essentials['total_spent'] += spent
                    kitchen_essentials['subcategories'][category] = {
                        'allocated': allocated,
                        'spent': spent,
                        'budget_id': budget_id
                    }
                else:
                    # Regular category
                    organized[category] = {
                        'allocated': allocated,
                        'spent': spent,
                        'budget_id': budget_id
                    }

            # Add Kitchen Essentials if it has subcategories
            if kitchen_essentials['subcategories']:
                organized['Kitchen Essentials'] = kitchen_essentials

            return organized

        except Exception as e:
            self.logger.error(f"Error organizing budget data: {e}")
            return {}



    def populate_expense_table(self):
        """Populate expense tracking table with all transaction types"""
        try:
            # Clear existing data
            self.expense_table.setRowCount(0)

            # Get expenses from shopping data and manual expenses
            expenses = []
            total_amount = 0
            month_amount = 0
            current_month = QDate.currentDate().toString("yyyy-MM")

            # Add shopping expenses
            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                shopping_df = self.data['shopping_list']
                for _, item in shopping_df.iterrows():
                    if item.get('status', '').lower() == 'purchased':
                        amount = float(item.get('current_price', 0))
                        date_str = str(item.get('date_purchased', item.get('date_added', '')))

                        expense = {
                            'date': date_str,
                            'category': item.get('category', 'Shopping'),
                            'description': f"Shopping: {item.get('item_name', 'Unknown')}",
                            'amount': amount,
                            'type': 'Shopping',
                            'source': 'Shopping List',
                            'receipt': '',
                            'notes': item.get('notes', '')
                        }
                        expenses.append(expense)
                        total_amount += amount

                        # Check if this month
                        if date_str.startswith(current_month):
                            month_amount += amount

            # Add manual expenses (repairs, bills, etc.)
            if 'manual_expenses' in self.data and not self.data['manual_expenses'].empty:
                manual_df = self.data['manual_expenses']
                for _, expense in manual_df.iterrows():
                    amount = float(expense.get('amount', 0))
                    date_str = str(expense.get('date', ''))

                    expense_data = {
                        'date': date_str,
                        'category': expense.get('category', 'Manual'),
                        'description': expense.get('description', ''),
                        'amount': amount,
                        'type': 'Manual',
                        'source': 'Manual Entry',
                        'receipt': expense.get('receipt', ''),
                        'notes': expense.get('notes', '')
                    }
                    expenses.append(expense_data)
                    total_amount += amount

                    # Check if this month
                    if date_str.startswith(current_month):
                        month_amount += amount

            # Add gas purchases
            if 'gas_purchases' in self.data and not self.data['gas_purchases'].empty:
                gas_df = self.data['gas_purchases']
                for _, purchase in gas_df.iterrows():
                    amount = float(purchase.get('total_cost', 0))
                    date_str = str(purchase.get('purchase_date', ''))

                    expense = {
                        'date': date_str,
                        'category': 'Gas',
                        'description': f"Gas Cylinder - {purchase.get('supplier', 'Unknown')}",
                        'amount': amount,
                        'type': 'Utilities',
                        'source': 'Gas Management',
                        'receipt': '',
                        'notes': purchase.get('notes', '')
                    }
                    expenses.append(expense)
                    total_amount += amount

                    # Check if this month
                    if date_str.startswith(current_month):
                        month_amount += amount

            # Add packing materials purchases
            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                packing_df = self.data['packing_materials']
                for _, material in packing_df.iterrows():
                    # Only include if there's a purchase record
                    if material.get('last_purchase_date'):
                        amount = float(material.get('cost_per_unit', 0)) * float(material.get('current_stock', 0))
                        date_str = str(material.get('last_purchase_date', ''))

                        expense = {
                            'date': date_str,
                            'category': 'Packing Materials',
                            'description': f"Packing: {material.get('material_name', 'Unknown')}",
                            'amount': amount,
                            'type': 'Supplies',
                            'source': 'Stock Management',
                            'receipt': '',
                            'notes': material.get('notes', '')
                        }
                        expenses.append(expense)
                        total_amount += amount

                        # Check if this month
                        if date_str.startswith(current_month):
                            month_amount += amount

            # Sort expenses by date (newest first)
            expenses.sort(key=lambda x: x.get('date', ''), reverse=True)

            # Update summary cards
            self.total_expenses_label.setText(f"₹{total_amount:,.2f}")
            self.month_expenses_label.setText(f"₹{month_amount:,.2f}")

            # Calculate remaining budget
            total_budget = 0
            if 'budget' in self.data and not self.data['budget'].empty:
                total_budget = self.data['budget']['budget_amount'].sum()
            remaining_budget = total_budget - total_amount
            self.remaining_budget_label.setText(f"₹{remaining_budget:,.2f}")

            # Set color based on remaining budget
            if remaining_budget < 0:
                self.remaining_budget_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #dc2626;")
            elif remaining_budget < total_budget * 0.2:
                self.remaining_budget_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f59e0b;")
            else:
                self.remaining_budget_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #059669;")

            # Populate table
            self.expense_table.setRowCount(len(expenses))
            for row, expense in enumerate(expenses):
                self.expense_table.setItem(row, 0, QTableWidgetItem(str(expense.get('date', ''))))
                self.expense_table.setItem(row, 1, QTableWidgetItem(str(expense.get('category', ''))))
                self.expense_table.setItem(row, 2, QTableWidgetItem(str(expense.get('description', ''))))
                self.expense_table.setItem(row, 3, QTableWidgetItem(f"₹{expense.get('amount', 0):.2f}"))
                self.expense_table.setItem(row, 4, QTableWidgetItem(str(expense.get('type', ''))))
                self.expense_table.setItem(row, 5, QTableWidgetItem(str(expense.get('source', ''))))
                self.expense_table.setItem(row, 6, QTableWidgetItem(str(expense.get('receipt', ''))))
                self.expense_table.setItem(row, 7, QTableWidgetItem(str(expense.get('notes', ''))))

        except Exception as e:
            self.logger.error(f"Error populating expense table: {e}")
    
    def populate_category_mapping(self):
        """Populate category mapping table"""
        try:
            # Get unique categories from different sources
            shopping_categories = set()
            budget_categories = set()

            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                shopping_categories = set(self.data['shopping_list']['category'].dropna().unique())

            if 'budget' in self.data and not self.data['budget'].empty:
                budget_categories = set(self.data['budget']['category'].dropna().unique())

            # Create mapping pairs
            all_categories = shopping_categories.union(budget_categories)
            mappings = []

            for cat in all_categories:
                mappings.append({
                    'shopping_category': cat,
                    'budget_category': cat  # Default to same name
                })

            # Populate table
            self.mapping_table.setRowCount(len(mappings))
            for row, mapping in enumerate(mappings):
                shopping_item = QTableWidgetItem(mapping['shopping_category'])
                budget_item = QTableWidgetItem(mapping['budget_category'])

                self.mapping_table.setItem(row, 0, shopping_item)
                self.mapping_table.setItem(row, 1, budget_item)

        except Exception as e:
            self.logger.error(f"Error populating category mapping: {e}")
    
    def sync_shopping_expenses(self):
        """Sync expenses from shopping list to budget tracking"""
        try:
            if 'shopping_list' not in self.data or self.data['shopping_list'].empty:
                notify_warning("No Data", "No shopping data found to sync", parent=self)
                return
            
            # Process shopping data and add to expenses
            shopping_df = self.data['shopping_list']
            
            # Group by category and sum amounts using current_price or last_price
            price_column = 'current_price' if 'current_price' in shopping_df.columns else 'last_price'
            if price_column in shopping_df.columns:
                category_expenses = shopping_df.groupby('category')[price_column].sum().reset_index()
                category_expenses.rename(columns={price_column: 'price_estimate'}, inplace=True)
            else:
                # No price data available
                category_expenses = pd.DataFrame(columns=['category', 'price_estimate'])
            
            # Update budget actual amounts
            if 'budget' in self.data:
                for _, expense in category_expenses.iterrows():
                    category = expense['category']
                    amount = expense['price_estimate']
                    
                    # Find matching budget category
                    budget_mask = self.data['budget']['category'] == category
                    if budget_mask.any():
                        self.data['budget'].loc[budget_mask, 'actual_amount'] += amount
            
            # Save updated budget data
            self.save_budget_data()
            self.load_data()
            
            notify_success("Sync Complete", f"Synced expenses from {len(category_expenses)} categories", parent=self)
            
        except Exception as e:
            self.logger.error(f"Error syncing shopping expenses: {e}")
            notify_error("Sync Error", f"Failed to sync expenses: {str(e)}", parent=self)
    
    def add_budget_category(self):
        """Add a new budget category"""
        try:
            from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("Add Budget Category")
            dialog.setMinimumSize(350, 250)

            layout = QFormLayout(dialog)

            # Category name input
            category_input = QLineEdit()
            layout.addRow("Category Name:", category_input)

            # Budget amount input
            amount_input = QDoubleSpinBox()
            amount_input.setRange(0.01, 999999.99)
            amount_input.setDecimals(2)
            amount_input.setPrefix("₹")
            amount_input.setValue(1000.00)
            layout.addRow("Budget Amount:", amount_input)

            # Period input
            period_input = QComboBox()
            period_input.addItems(["Monthly", "Weekly", "Quarterly", "Yearly"])
            layout.addRow("Period:", period_input)

            # Notes input
            notes_input = QTextEdit()
            notes_input.setMaximumHeight(80)
            layout.addRow("Notes:", notes_input)

            # Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                category_name = category_input.text().strip()
                if not category_name:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a category name.")
                    return

                # Save the budget category
                self.save_budget_category(
                    category_name,
                    amount_input.value(),
                    period_input.currentText(),
                    notes_input.toPlainText()
                )

        except Exception as e:
            self.logger.error(f"Error adding budget category: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add budget category: {str(e)}")

    def add_repair_bills_transaction(self):
        """Show dialog to add repair/bills transaction"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Repair/Bills Transaction")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Transaction type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Transaction Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Repairs", "Bills", "Utilities", "Maintenance", "Other"])
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)

        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("e.g., Kitchen equipment repair, Electricity bill")
        desc_layout.addWidget(desc_input)
        layout.addLayout(desc_layout)

        # Amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount (₹):"))
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 999999)
        amount_input.setValue(100)
        amount_layout.addWidget(amount_input)
        layout.addLayout(amount_layout)

        # Date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        date_input = QDateEdit()
        date_input.setDate(QDate.currentDate())
        date_input.setCalendarPopup(True)
        date_layout.addWidget(date_input)
        layout.addLayout(date_layout)

        # Receipt/Reference
        receipt_layout = QHBoxLayout()
        receipt_layout.addWidget(QLabel("Receipt/Reference:"))
        receipt_input = QLineEdit()
        receipt_input.setPlaceholderText("Receipt number or reference")
        receipt_layout.addWidget(receipt_input)
        layout.addLayout(receipt_layout)

        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(80)
        notes_input.setPlaceholderText("Additional details about the transaction")
        notes_layout.addWidget(notes_input)
        layout.addLayout(notes_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            transaction_type = type_combo.currentText()
            description = desc_input.text().strip()
            amount = amount_input.value()
            date = date_input.date().toString("yyyy-MM-dd")
            receipt = receipt_input.text().strip()
            notes = notes_input.toPlainText().strip()

            if description and amount > 0:
                self.add_transaction_to_budget(transaction_type, description, amount, date, receipt, notes)
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a description and amount.")

    def add_transaction_to_budget(self, transaction_type, description, amount, date, receipt, notes):
        """Add transaction to budget tracking and update budget spent amounts"""
        try:
            # Initialize manual expenses dataframe if needed
            if 'manual_expenses' not in self.data:
                self.data['manual_expenses'] = pd.DataFrame(columns=[
                    'expense_id', 'date', 'category', 'description', 'amount', 'receipt', 'notes'
                ])

            # Add to manual expenses
            new_expense = pd.DataFrame({
                'expense_id': [len(self.data['manual_expenses']) + 1],
                'date': [date],
                'category': [transaction_type],
                'description': [description],
                'amount': [amount],
                'receipt': [receipt],
                'notes': [notes]
            })

            self.data['manual_expenses'] = pd.concat([self.data['manual_expenses'], new_expense], ignore_index=True)

            # Update budget spent amount for this category
            if 'budget' in self.data and not self.data['budget'].empty:
                budget_df = self.data['budget']
                category_mask = budget_df['category'] == transaction_type

                if category_mask.any():
                    # Update existing category
                    current_spent = budget_df.loc[category_mask, 'actual_amount'].iloc[0]
                    budget_df.loc[category_mask, 'actual_amount'] = current_spent + amount
                else:
                    # Create new budget category if it doesn't exist
                    new_budget = pd.DataFrame({
                        'budget_id': [len(budget_df) + 1],
                        'category': [transaction_type],
                        'budget_amount': [amount * 2],  # Set budget to 2x the first expense
                        'actual_amount': [amount],
                        'period': ['Monthly'],
                        'notes': ['Auto-created from transaction']
                    })
                    budget_df = pd.concat([budget_df, new_budget], ignore_index=True)

                self.data['budget'] = budget_df

            # Save to CSV files
            expenses_file = os.path.join('data', 'manual_expenses.csv')
            self.data['manual_expenses'].to_csv(expenses_file, index=False)

            budget_file = os.path.join('data', 'budget.csv')
            self.data['budget'].to_csv(budget_file, index=False)

            # Refresh displays
            self.load_data()

            QMessageBox.information(self, "Success", f"Transaction added successfully!\nCategory: {transaction_type}\nAmount: ₹{amount:.2f}")

        except Exception as e:
            self.logger.error(f"Error adding transaction: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add transaction: {str(e)}")

    def save_budget_category(self, category, amount, period, notes):
        """Save new budget category to data"""
        try:
            # Initialize budget dataframe if it doesn't exist
            if 'budget' not in self.data:
                self.data['budget'] = pd.DataFrame(columns=[
                    'budget_id', 'category', 'budget_amount', 'actual_amount', 'period', 'notes'
                ])

            # Check if category already exists
            if not self.data['budget'].empty:
                existing = self.data['budget'][self.data['budget']['category'] == category]
                if not existing.empty:
                    QMessageBox.warning(self, "Category Exists", f"Budget category '{category}' already exists.")
                    return

            # Create new budget entry
            new_budget = pd.DataFrame({
                'budget_id': [len(self.data['budget']) + 1],
                'category': [category],
                'budget_amount': [amount],
                'actual_amount': [0.0],
                'period': [period],
                'notes': [notes]
            })

            # Add to dataframe
            self.data['budget'] = pd.concat([self.data['budget'], new_budget], ignore_index=True)

            # Save to CSV
            budget_file = os.path.join('data', 'budget.csv')
            self.data['budget'].to_csv(budget_file, index=False)

            # Refresh displays
            self.load_data()

            QMessageBox.information(self, "Success", f"Budget category '{category}' with ₹{amount:.2f} budget added successfully!")

        except Exception as e:
            self.logger.error(f"Error saving budget category: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save budget category: {str(e)}")
    
    def add_manual_expense(self):
        """Add manual expense entry"""
        try:
            from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("Add Manual Expense")
            dialog.setMinimumSize(400, 300)

            layout = QFormLayout(dialog)

            # Date input
            date_input = QDateEdit()
            date_input.setDate(QDate.currentDate())
            layout.addRow("Date:", date_input)

            # Category input
            category_input = QComboBox()
            category_input.setEditable(True)
            # Get existing categories from budget
            categories = ['General', 'Food', 'Gas', 'Packing Materials', 'Utilities', 'Maintenance']
            if 'budget' in self.data and not self.data['budget'].empty:
                existing_categories = self.data['budget']['category'].unique().tolist()
                categories.extend([cat for cat in existing_categories if cat not in categories])
            category_input.addItems(categories)
            layout.addRow("Category:", category_input)

            # Description input
            description_input = QLineEdit()
            layout.addRow("Description:", description_input)

            # Amount input
            amount_input = QDoubleSpinBox()
            amount_input.setRange(0.01, 999999.99)
            amount_input.setDecimals(2)
            amount_input.setPrefix("₹")
            layout.addRow("Amount:", amount_input)

            # Receipt input
            receipt_input = QLineEdit()
            layout.addRow("Receipt/Reference:", receipt_input)

            # Notes input
            notes_input = QTextEdit()
            notes_input.setMaximumHeight(80)
            layout.addRow("Notes:", notes_input)

            # Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                # Save the expense
                self.save_manual_expense(
                    date_input.date().toString("yyyy-MM-dd"),
                    category_input.currentText(),
                    description_input.text(),
                    amount_input.value(),
                    receipt_input.text(),
                    notes_input.toPlainText()
                )

        except Exception as e:
            self.logger.error(f"Error adding manual expense: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add manual expense: {str(e)}")

    def save_manual_expense(self, date, category, description, amount, receipt, notes):
        """Save manual expense to data"""
        try:
            # Initialize manual expenses dataframe if it doesn't exist
            if 'manual_expenses' not in self.data:
                self.data['manual_expenses'] = pd.DataFrame(columns=[
                    'expense_id', 'date', 'category', 'description', 'amount', 'receipt', 'notes'
                ])

            # Create new expense entry
            new_expense = pd.DataFrame({
                'expense_id': [len(self.data['manual_expenses']) + 1],
                'date': [date],
                'category': [category],
                'description': [description],
                'amount': [amount],
                'receipt': [receipt],
                'notes': [notes]
            })

            # Add to dataframe
            self.data['manual_expenses'] = pd.concat([self.data['manual_expenses'], new_expense], ignore_index=True)

            # Save to CSV
            manual_expenses_file = os.path.join('data', 'manual_expenses.csv')
            self.data['manual_expenses'].to_csv(manual_expenses_file, index=False)

            # Update budget tracking
            self.update_budget_with_expense(category, amount)

            # Refresh displays
            self.load_data()

            QMessageBox.information(self, "Success", f"Manual expense of ₹{amount:.2f} added successfully!")

        except Exception as e:
            self.logger.error(f"Error saving manual expense: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save manual expense: {str(e)}")

    def update_budget_with_expense(self, category, amount):
        """Update budget tracking with new expense"""
        try:
            if 'budget' not in self.data:
                return

            # Find matching budget category
            budget_df = self.data['budget']
            matching_budget = budget_df[budget_df['category'] == category]

            if not matching_budget.empty:
                # Update actual amount
                idx = matching_budget.index[0]
                current_actual = budget_df.loc[idx, 'actual_amount'] if 'actual_amount' in budget_df.columns else 0
                budget_df.loc[idx, 'actual_amount'] = current_actual + amount

                # Save updated budget
                budget_file = os.path.join('data', 'budget.csv')
                budget_df.to_csv(budget_file, index=False)

        except Exception as e:
            self.logger.error(f"Error updating budget with expense: {e}")

    def show_add_category_dialog(self):
        """Show dialog to add new budget category"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Budget Category")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)

        layout = QVBoxLayout(dialog)

        # Category name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Category Name:"))
        name_input = QLineEdit()
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)

        # Budget amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Budget Amount (₹):"))
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 999999)
        amount_input.setValue(1000)
        amount_layout.addWidget(amount_input)
        layout.addLayout(amount_layout)

        # Period
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Period:"))
        period_combo = QComboBox()
        period_combo.addItems(["Monthly", "Weekly", "Yearly"])
        period_layout.addWidget(period_combo)
        layout.addLayout(period_layout)

        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(80)
        notes_layout.addWidget(notes_input)
        layout.addLayout(notes_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            category_name = name_input.text().strip()
            budget_amount = amount_input.value()
            period = period_combo.currentText()
            notes = notes_input.toPlainText().strip()

            if category_name:
                self.add_budget_category(category_name, budget_amount, period, notes)
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a category name.")

    def add_budget_category(self, category_name, budget_amount, period, notes):
        """Add new budget category"""
        try:
            # Initialize budget dataframe if needed
            if 'budget' not in self.data:
                self.data['budget'] = pd.DataFrame(columns=[
                    'budget_id', 'category', 'budget_amount', 'actual_amount', 'period', 'notes'
                ])

            # Check if category already exists
            budget_df = self.data['budget']
            if not budget_df.empty:
                existing = budget_df[budget_df['category'] == category_name]
                if not existing.empty:
                    QMessageBox.warning(self, "Category Exists", f"Budget category '{category_name}' already exists.")
                    return

            # Create new budget entry
            new_budget = pd.DataFrame({
                'budget_id': [len(budget_df) + 1],
                'category': [category_name],
                'budget_amount': [budget_amount],
                'actual_amount': [0.0],
                'period': [period],
                'notes': [notes]
            })

            # Add to dataframe
            self.data['budget'] = pd.concat([self.data['budget'], new_budget], ignore_index=True)

            # Save to CSV
            budget_file = os.path.join('data', 'budget.csv')
            self.data['budget'].to_csv(budget_file, index=False)

            # Refresh displays
            self.load_data()

            QMessageBox.information(self, "Success", f"Budget category '{category_name}' added successfully!")

        except Exception as e:
            self.logger.error(f"Error adding budget category: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add budget category: {str(e)}")
    
    def save_budget_data(self):
        """Save budget data to file"""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            budget_file = os.path.join(data_dir, 'budget.csv')
            self.data['budget'].to_csv(budget_file, index=False)
        except Exception as e:
            self.logger.error(f"Error saving budget data: {e}")
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_data()
