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
        """Create budget allocation tab"""
        allocation_widget = QWidget()
        layout = QVBoxLayout(allocation_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Budget allocation table
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(6)
        self.budget_table.setHorizontalHeaderLabels([
            "Category", "Budget Amount", "Spent Amount", "Remaining", "Percentage Used", "Status"
        ])
        
        # Modern table styling
        self.budget_table.setStyleSheet("""
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
        header = self.budget_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Category
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Budget Amount
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Spent Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Remaining
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Percentage
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        
        layout.addWidget(self.budget_table)
        
        self.tabs.addTab(allocation_widget, "Budget Allocation")
    
    def create_expense_tracking_tab(self):
        """Create expense tracking tab"""
        expense_widget = QWidget()
        layout = QVBoxLayout(expense_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Expense tracking table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(7)
        self.expense_table.setHorizontalHeaderLabels([
            "Date", "Category", "Description", "Amount", "Source", "Receipt", "Notes"
        ])
        
        # Apply modern styling
        self.expense_table.setStyleSheet(self.budget_table.styleSheet())
        
        # Set column widths
        header = self.expense_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Source
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Receipt
        header.setSectionResizeMode(6, QHeaderView.Stretch)           # Notes
        
        layout.addWidget(self.expense_table)
        
        # Add expense button
        add_expense_btn = QPushButton("Add Manual Expense")
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
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_expense_btn)
        layout.addLayout(button_layout)
        
        self.tabs.addTab(expense_widget, "Expense Tracking")
    
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
        """Populate budget allocation table"""
        try:
            if 'budget' not in self.data or self.data['budget'].empty:
                return
            
            budget_df = self.data['budget']
            self.budget_table.setRowCount(len(budget_df))
            
            for row, (_, budget) in enumerate(budget_df.iterrows()):
                # Category
                category_item = QTableWidgetItem(str(budget.get('category', '')))
                self.budget_table.setItem(row, 0, category_item)
                
                # Budget Amount
                budget_amount = budget.get('budget_amount', 0)
                budget_item = QTableWidgetItem(f"₹{budget_amount:,.2f}")
                self.budget_table.setItem(row, 1, budget_item)
                
                # Spent Amount
                spent_amount = budget.get('actual_amount', 0)
                spent_item = QTableWidgetItem(f"₹{spent_amount:,.2f}")
                self.budget_table.setItem(row, 2, spent_item)
                
                # Remaining
                remaining = budget_amount - spent_amount
                remaining_item = QTableWidgetItem(f"₹{remaining:,.2f}")
                self.budget_table.setItem(row, 3, remaining_item)
                
                # Percentage Used
                percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
                percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
                self.budget_table.setItem(row, 4, percentage_item)
                
                # Status
                if percentage > 100:
                    status = "Over Budget"
                    color = "#ef4444"
                elif percentage > 90:
                    status = "Critical"
                    color = "#f59e0b"
                elif percentage > 75:
                    status = "Warning"
                    color = "#f59e0b"
                else:
                    status = "On Track"
                    color = "#10b981"
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(color))
                self.budget_table.setItem(row, 5, status_item)
                
        except Exception as e:
            self.logger.error(f"Error populating budget table: {e}")
    
    def populate_expense_table(self):
        """Populate expense tracking table"""
        try:
            # Clear existing data
            self.expense_table.setRowCount(0)

            # Get expenses from shopping data and manual expenses
            expenses = []

            # Add shopping expenses
            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                shopping_df = self.data['shopping_list']
                for _, item in shopping_df.iterrows():
                    if item.get('status', '').lower() == 'purchased':
                        expense = {
                            'date': item.get('date_purchased', item.get('date_added', '')),
                            'category': item.get('category', 'Shopping'),
                            'description': f"Shopping: {item.get('item_name', 'Unknown')}",
                            'amount': item.get('current_price', 0),
                            'source': 'Shopping',
                            'receipt': '',
                            'notes': item.get('notes', '')
                        }
                        expenses.append(expense)

            # Add manual expenses
            if 'manual_expenses' in self.data and not self.data['manual_expenses'].empty:
                manual_df = self.data['manual_expenses']
                for _, expense in manual_df.iterrows():
                    expense_data = {
                        'date': expense.get('date', ''),
                        'category': expense.get('category', 'Manual'),
                        'description': expense.get('description', ''),
                        'amount': expense.get('amount', 0),
                        'source': 'Manual Entry',
                        'receipt': expense.get('receipt', ''),
                        'notes': expense.get('notes', '')
                    }
                    expenses.append(expense_data)

            # Add gas purchases
            if 'gas_purchases' in self.data and not self.data['gas_purchases'].empty:
                gas_df = self.data['gas_purchases']
                for _, purchase in gas_df.iterrows():
                    expense = {
                        'date': purchase.get('purchase_date', ''),
                        'category': 'Gas',
                        'description': f"Gas Cylinder - {purchase.get('supplier', 'Unknown')}",
                        'amount': purchase.get('total_cost', 0),
                        'source': 'Gas Management',
                        'receipt': '',
                        'notes': purchase.get('notes', '')
                    }
                    expenses.append(expense)

            # Add packing materials purchases
            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                packing_df = self.data['packing_materials']
                for _, material in packing_df.iterrows():
                    # Only include if there's a purchase record
                    if material.get('last_purchase_date'):
                        expense = {
                            'date': material.get('last_purchase_date', ''),
                            'category': 'Packing Materials',
                            'description': f"Packing: {material.get('material_name', 'Unknown')}",
                            'amount': material.get('cost_per_unit', 0) * material.get('current_stock', 0),
                            'source': 'Stock Management',
                            'receipt': '',
                            'notes': material.get('notes', '')
                        }
                        expenses.append(expense)

            # Sort expenses by date (newest first)
            expenses.sort(key=lambda x: x.get('date', ''), reverse=True)

            # Populate table
            self.expense_table.setRowCount(len(expenses))
            for row, expense in enumerate(expenses):
                self.expense_table.setItem(row, 0, QTableWidgetItem(str(expense.get('date', ''))))
                self.expense_table.setItem(row, 1, QTableWidgetItem(str(expense.get('category', ''))))
                self.expense_table.setItem(row, 2, QTableWidgetItem(str(expense.get('description', ''))))
                self.expense_table.setItem(row, 3, QTableWidgetItem(f"₹{expense.get('amount', 0):.2f}"))
                self.expense_table.setItem(row, 4, QTableWidgetItem(str(expense.get('source', ''))))
                self.expense_table.setItem(row, 5, QTableWidgetItem(str(expense.get('receipt', ''))))
                self.expense_table.setItem(row, 6, QTableWidgetItem(str(expense.get('notes', ''))))

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
