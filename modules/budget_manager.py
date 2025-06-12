from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                               QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                               QMessageBox, QHeaderView, QSplitter, QTextEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import os
import logging

class BudgetManager(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        
        # Ensure we have budget data
        if 'budget' in data:
            self.budget_df = data['budget'].copy()
        else:
            self.budget_df = pd.DataFrame(columns=['budget_id', 'category', 'amount', 'period', 'notes'])
            
        # Ensure we have expense data
        if 'expenses' in data:
            self.expenses_df = data['expenses'].copy()
        else:
            # Try to create expense data from inventory purchases and other sources
            self.expenses_df = self.create_expense_data()
            self.data['expenses'] = self.expenses_df
            
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Budget Management")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for budget management
        self.budget_tab = QWidget()
        self.expenses_tab = QWidget()
        self.analysis_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.budget_tab, "Budget Allocation")
        self.tabs.addTab(self.expenses_tab, "Expense Tracking")
        self.tabs.addTab(self.analysis_tab, "Budget Analysis")
        
        # Set up each tab
        self.setup_budget_tab()
        self.setup_expenses_tab()
        self.setup_analysis_tab()
        
    def setup_budget_tab(self):
        """Set up the budget allocation tab"""
        layout = QVBoxLayout(self.budget_tab)
        
        # Header
        header = QLabel("Budget Allocation")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create split view for budget list and details
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Budget table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Budget table
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels(["ID", "Category", "Amount", "Period"])
        self.budget_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.budget_table.setSelectionMode(QTableWidget.SingleSelection)
        self.budget_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.budget_table.verticalHeader().setVisible(False)
        left_layout.addWidget(self.budget_table)
        
        # Populate budget table
        self.populate_budget_table()
        
        # Right panel: Budget form
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Budget form
        form_group = QGroupBox("Budget Details")
        form_layout = QFormLayout(form_group)
        
        # Category selection
        self.category_combo = QComboBox()
        if 'categories' in self.data:
            categories = self.data['categories']['category_name'].tolist() if 'category_name' in self.data['categories'].columns else []
            self.category_combo.addItems(categories)
        self.category_combo.setEditable(True)
        
        # Amount field
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMinimum(0)
        self.amount_spin.setMaximum(1000000)
        self.amount_spin.setSingleStep(100)
        self.amount_spin.setPrefix("₹ ")  # Default currency symbol
        
        # Period selection
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
        self.period_combo.setCurrentText("Monthly")
        
        # Notes field
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter any notes about this budget allocation...")
        self.notes_edit.setMaximumHeight(100)
        
        # Add fields to form
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Amount:", self.amount_spin)
        form_layout.addRow("Period:", self.period_combo)
        form_layout.addRow("Notes:", self.notes_edit)
        
        right_layout.addWidget(form_group)
        
        # Button group
        button_layout = QHBoxLayout()
        
        self.add_budget_btn = QPushButton("Add Budget")
        self.add_budget_btn.clicked.connect(self.add_budget)
        
        self.update_budget_btn = QPushButton("Update Budget")
        self.update_budget_btn.clicked.connect(self.update_budget)
        self.update_budget_btn.setEnabled(False)
        
        self.delete_budget_btn = QPushButton("Delete Budget")
        self.delete_budget_btn.clicked.connect(self.delete_budget)
        self.delete_budget_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_budget_btn)
        button_layout.addWidget(self.update_budget_btn)
        button_layout.addWidget(self.delete_budget_btn)
        
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 300])
        
        # Connect budget selection to form
        self.budget_table.itemSelectionChanged.connect(self.load_budget_details)
        
    def setup_expenses_tab(self):
        """Set up the expense tracking tab"""
        layout = QVBoxLayout(self.expenses_tab)
        
        # Header
        header = QLabel("Expense Tracking")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Expense table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Source", "Notes"])
        self.expense_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expense_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.expense_table.verticalHeader().setVisible(False)
        layout.addWidget(self.expense_table)
        
        # Populate expense table
        self.populate_expense_table()
        
        # Form for adding expenses
        form_group = QGroupBox("Add Expense")
        form_layout = QFormLayout(form_group)
        
        # Date picker
        self.expense_date = QDateEdit()
        self.expense_date.setDate(QDate.currentDate())
        self.expense_date.setCalendarPopup(True)
        
        # Category selection
        self.expense_category = QComboBox()
        if 'categories' in self.data:
            categories = self.data['categories']['category_name'].tolist() if 'category_name' in self.data['categories'].columns else []
            self.expense_category.addItems(categories)
        self.expense_category.setEditable(True)
        
        # Amount field
        self.expense_amount = QDoubleSpinBox()
        self.expense_amount.setMinimum(0)
        self.expense_amount.setMaximum(1000000)
        self.expense_amount.setSingleStep(10)
        self.expense_amount.setPrefix("₹ ")  # Default currency symbol
        
        # Source field
        self.expense_source = QComboBox()
        self.expense_source.addItems(["Inventory Purchase", "Utilities", "Maintenance", "Salaries", "Other"])
        self.expense_source.setEditable(True)
        
        # Notes field
        self.expense_notes = QLineEdit()
        self.expense_notes.setPlaceholderText("Enter any notes about this expense...")
        
        # Add fields to form
        form_layout.addRow("Date:", self.expense_date)
        form_layout.addRow("Category:", self.expense_category)
        form_layout.addRow("Amount:", self.expense_amount)
        form_layout.addRow("Source:", self.expense_source)
        form_layout.addRow("Notes:", self.expense_notes)
        
        # Add expense button
        add_expense_btn = QPushButton("Add Expense")
        add_expense_btn.clicked.connect(self.add_expense)
        form_layout.addRow("", add_expense_btn)
        
        layout.addWidget(form_group)
        
    def setup_analysis_tab(self):
        """Set up the budget analysis tab"""
        layout = QVBoxLayout(self.analysis_tab)
        
        # Header
        header = QLabel("Budget Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create charts for budget analysis
        self.create_budget_charts(layout)
        
    def populate_budget_table(self):
        """Populate the budget table with data"""
        self.budget_table.setRowCount(0)  # Clear existing rows
        
        if len(self.budget_df) == 0:
            return
            
        # Add budgets to the table
        for i, (_, budget) in enumerate(self.budget_df.iterrows()):
            self.budget_table.insertRow(i)
            
            # Add budget data
            id_item = QTableWidgetItem(str(budget['budget_id']) if 'budget_id' in budget else str(i+1))
            category_item = QTableWidgetItem(str(budget['category']) if 'category' in budget else "")
            
            # Format amount with currency symbol
            amount = float(budget['amount']) if 'amount' in budget and pd.notna(budget['amount']) else 0
            amount_item = QTableWidgetItem(f"₹ {amount:.2f}")
            
            period_item = QTableWidgetItem(str(budget['period']) if 'period' in budget else "Monthly")
            
            self.budget_table.setItem(i, 0, id_item)
            self.budget_table.setItem(i, 1, category_item)
            self.budget_table.setItem(i, 2, amount_item)
            self.budget_table.setItem(i, 3, period_item)
            
    def populate_expense_table(self):
        """Populate the expense table with data"""
        self.expense_table.setRowCount(0)  # Clear existing rows
        
        if len(self.expenses_df) == 0:
            return
            
        # Add expenses to the table
        for i, (_, expense) in enumerate(self.expenses_df.iterrows()):
            self.expense_table.insertRow(i)
            
            # Add expense data
            date_item = QTableWidgetItem(str(expense['date']) if 'date' in expense else "")
            category_item = QTableWidgetItem(str(expense['category']) if 'category' in expense else "")
            
            # Format amount with currency symbol
            amount = float(expense['amount']) if 'amount' in expense and pd.notna(expense['amount']) else 0
            amount_item = QTableWidgetItem(f"₹ {amount:.2f}")
            
            source_item = QTableWidgetItem(str(expense['source']) if 'source' in expense else "")
            notes_item = QTableWidgetItem(str(expense['notes']) if 'notes' in expense else "")
            
            self.expense_table.setItem(i, 0, date_item)
            self.expense_table.setItem(i, 1, category_item)
            self.expense_table.setItem(i, 2, amount_item)
            self.expense_table.setItem(i, 3, source_item)
            self.expense_table.setItem(i, 4, notes_item)
            
    def load_budget_details(self):
        """Load the selected budget details into the form"""
        selected_items = self.budget_table.selectedItems()
        if not selected_items:
            return
            
        # Get the budget ID from the first column
        row = selected_items[0].row()
        budget_id = self.budget_table.item(row, 0).text()
        
        # Find the budget in the dataframe
        budget = self.budget_df[self.budget_df['budget_id'].astype(str) == budget_id].iloc[0] if len(self.budget_df) > 0 else None
        
        if budget is not None:
            # Update the form fields
            self.category_combo.setCurrentText(str(budget['category']) if 'category' in budget else "")
            
            amount = float(budget['amount']) if 'amount' in budget and pd.notna(budget['amount']) else 0
            self.amount_spin.setValue(amount)
            
            self.period_combo.setCurrentText(str(budget['period']) if 'period' in budget else "Monthly")
            self.notes_edit.setText(str(budget['notes']) if 'notes' in budget and pd.notna(budget['notes']) else "")
            
            # Enable update and delete buttons
            self.update_budget_btn.setEnabled(True)
            self.delete_budget_btn.setEnabled(True)
        
    def add_budget(self):
        """Add a new budget allocation"""
        category = self.category_combo.currentText()
        amount = self.amount_spin.value()
        period = self.period_combo.currentText()
        notes = self.notes_edit.toPlainText()
        
        if not category:
            QMessageBox.warning(self, "Missing Information", "Please enter a category for the budget.")
            return
            
        # Generate new budget ID
        next_id = len(self.budget_df) + 1 if len(self.budget_df) > 0 else 1
        
        # Create new budget entry
        new_budget = pd.DataFrame({
            'budget_id': [next_id],
            'category': [category],
            'amount': [amount],
            'period': [period],
            'notes': [notes]
        })
        
        # Add to dataframe
        self.budget_df = pd.concat([self.budget_df, new_budget], ignore_index=True)
        self.data['budget'] = self.budget_df
        
        # Save to CSV file
        try:
            budget_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    'data', 'budget.csv')
            self.budget_df.to_csv(budget_file, index=False)
            
            # Update the budget table
            self.populate_budget_table()
            
            # Clear the form
            self.category_combo.setCurrentIndex(0)
            self.amount_spin.setValue(0)
            self.period_combo.setCurrentText("Monthly")
            self.notes_edit.clear()
            
            # Update analysis charts
            self.update_analysis_charts()
            
            QMessageBox.information(self, "Budget Added", f"Budget allocation of ₹{amount:.2f} added for {category}.")
        except Exception as e:
            logging.error(f"Error saving budget data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving budget data: {e}")
            
    def update_budget(self):
        """Update the selected budget allocation"""
        selected_items = self.budget_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a budget to update.")
            return
            
        # Get the budget ID from the first column
        row = selected_items[0].row()
        budget_id = self.budget_table.item(row, 0).text()
        
        # Get form values
        category = self.category_combo.currentText()
        amount = self.amount_spin.value()
        period = self.period_combo.currentText()
        notes = self.notes_edit.toPlainText()
        
        if not category:
            QMessageBox.warning(self, "Missing Information", "Please enter a category for the budget.")
            return
            
        # Update budget in dataframe
        idx = self.budget_df[self.budget_df['budget_id'].astype(str) == budget_id].index
        if len(idx) > 0:
            self.budget_df.at[idx[0], 'category'] = category
            self.budget_df.at[idx[0], 'amount'] = amount
            self.budget_df.at[idx[0], 'period'] = period
            self.budget_df.at[idx[0], 'notes'] = notes
            
            # Save to CSV file
            try:
                budget_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'data', 'budget.csv')
                self.budget_df.to_csv(budget_file, index=False)
                
                # Update the budget table
                self.populate_budget_table()
                
                # Update analysis charts
                self.update_analysis_charts()
                
                QMessageBox.information(self, "Budget Updated", f"Budget allocation for {category} updated to ₹{amount:.2f}.")
            except Exception as e:
                logging.error(f"Error saving budget data: {e}")
                QMessageBox.warning(self, "Error", f"Error saving budget data: {e}")
        else:
            QMessageBox.warning(self, "Error", "Could not find budget to update.")
            
    def delete_budget(self):
        """Delete the selected budget allocation"""
        selected_items = self.budget_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a budget to delete.")
            return
            
        # Get the budget ID from the first column
        row = selected_items[0].row()
        budget_id = self.budget_table.item(row, 0).text()
        category = self.budget_table.item(row, 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete the budget for {category}?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
            
        # Delete budget from dataframe
        self.budget_df = self.budget_df[self.budget_df['budget_id'].astype(str) != budget_id]
        self.data['budget'] = self.budget_df
        
        # Save to CSV file
        try:
            budget_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    'data', 'budget.csv')
            self.budget_df.to_csv(budget_file, index=False)
            
            # Update the budget table
            self.populate_budget_table()
            
            # Clear the form
            self.category_combo.setCurrentIndex(0)
            self.amount_spin.setValue(0)
            self.period_combo.setCurrentText("Monthly")
            self.notes_edit.clear()
            
            # Disable update and delete buttons
            self.update_budget_btn.setEnabled(False)
            self.delete_budget_btn.setEnabled(False)
            
            # Update analysis charts
            self.update_analysis_charts()
            
            QMessageBox.information(self, "Budget Deleted", f"Budget allocation for {category} has been deleted.")
        except Exception as e:
            logging.error(f"Error saving budget data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving budget data: {e}")
            
    def add_expense(self):
        """Add a new expense record"""
        date = self.expense_date.date().toString("yyyy-MM-dd")
        category = self.expense_category.currentText()
        amount = self.expense_amount.value()
        source = self.expense_source.currentText()
        notes = self.expense_notes.text()
        
        if not category:
            QMessageBox.warning(self, "Missing Information", "Please enter a category for the expense.")
            return
            
        # Create expense dataframe if it doesn't exist
        if 'expenses' not in self.data:
            self.data['expenses'] = pd.DataFrame(columns=['expense_id', 'date', 'category', 'amount', 'source', 'notes'])
            self.expenses_df = self.data['expenses']
            
        # Generate new expense ID
        next_id = len(self.expenses_df) + 1 if len(self.expenses_df) > 0 else 1
        
        # Create new expense entry
        new_expense = pd.DataFrame({
            'expense_id': [next_id],
            'date': [date],
            'category': [category],
            'amount': [amount],
            'source': [source],
            'notes': [notes]
        })
        
        # Add to dataframe
        self.expenses_df = pd.concat([self.expenses_df, new_expense], ignore_index=True)
        self.data['expenses'] = self.expenses_df
        
        # Save to CSV file
        try:
            expenses_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'data', 'expenses.csv')
            self.expenses_df.to_csv(expenses_file, index=False)
            
            # Update the expense table
            self.populate_expense_table()
            
            # Clear the form
            self.expense_date.setDate(QDate.currentDate())
            self.expense_category.setCurrentIndex(0)
            self.expense_amount.setValue(0)
            self.expense_source.setCurrentIndex(0)
            self.expense_notes.clear()
            
            # Update analysis charts
            self.update_analysis_charts()
            
            QMessageBox.information(self, "Expense Added", f"Expense of ₹{amount:.2f} added for {category}.")
        except Exception as e:
            logging.error(f"Error saving expense data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving expense data: {e}")
            
    def create_expense_data(self):
        """Create expense data from inventory purchases and other sources if available"""
        expenses = pd.DataFrame(columns=['expense_id', 'date', 'category', 'amount', 'source', 'notes'])
        
        # Try to extract expenses from inventory purchases
        if 'inventory' in self.data and len(self.data['inventory']) > 0:
            inventory_df = self.data['inventory']
            
            # Check if we have purchase data
            if 'purchase_date' in inventory_df.columns and 'price' in inventory_df.columns:
                for i, (_, item) in enumerate(inventory_df.iterrows()):
                    if pd.notna(item['purchase_date']) and pd.notna(item['price']):
                        category = item['category'] if 'category' in item and pd.notna(item['category']) else "Inventory"
                        price = float(item['price']) if pd.notna(item['price']) else 0
                        qty = float(item['quantity']) if 'quantity' in item and pd.notna(item['quantity']) else 1
                        
                        # Create expense entry
                        new_expense = pd.DataFrame({
                            'expense_id': [i+1],
                            'date': [item['purchase_date']],
                            'category': [category],
                            'amount': [price * qty],
                            'source': ['Inventory Purchase'],
                            'notes': [f"Purchase of {item['item_name']}"]
                        })
                        
                        expenses = pd.concat([expenses, new_expense], ignore_index=True)
        
        # Save the expenses data
        try:
            expenses_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'data', 'expenses.csv')
            expenses.to_csv(expenses_file, index=False)
        except Exception as e:
            logging.error(f"Error saving expense data: {e}")
            
        return expenses
        
    def create_budget_charts(self, layout):
        """Create charts for budget analysis"""
        # Create container for charts
        charts_container = QWidget()
        charts_layout = QVBoxLayout(charts_container)
        
        # Budget vs. Expense chart
        budget_chart_group = QGroupBox("Budget vs. Actual Expenses")
        budget_chart_layout = QVBoxLayout(budget_chart_group)
        
        # Create figure and canvas
        self.budget_fig, self.budget_ax = plt.subplots(figsize=(8, 5))
        self.budget_canvas = FigureCanvas(self.budget_fig)
        budget_chart_layout.addWidget(self.budget_canvas)
        
        # Category breakdown chart
        category_chart_group = QGroupBox("Expense Categories Breakdown")
        category_chart_layout = QVBoxLayout(category_chart_group)
        
        # Create figure and canvas
        self.category_fig, self.category_ax = plt.subplots(figsize=(8, 5))
        self.category_canvas = FigureCanvas(self.category_fig)
        category_chart_layout.addWidget(self.category_canvas)
        
        # Add charts to layout
        charts_layout.addWidget(budget_chart_group)
        charts_layout.addWidget(category_chart_group)
        
        # Add charts container to main layout
        layout.addWidget(charts_container)
        
        # Update charts with data
        self.update_analysis_charts()
        
    def update_analysis_charts(self):
        """Update the budget analysis charts with current data"""
        # Clear existing charts
        self.budget_ax.clear()
        self.category_ax.clear()
        
        # Budget vs. Expense chart
        if len(self.budget_df) > 0:
            # Group budgets by category
            budget_by_category = self.budget_df.groupby('category')['amount'].sum().reset_index()
            
            # Group expenses by category if we have any
            expense_by_category = pd.DataFrame(columns=['category', 'amount'])
            if len(self.expenses_df) > 0:
                expense_by_category = self.expenses_df.groupby('category')['amount'].sum().reset_index()
            
            # Merge budgets and expenses
            categories = budget_by_category['category'].unique()
            budget_amounts = []
            expense_amounts = []
            
            for category in categories:
                # Get budget amount
                budget_amount = budget_by_category[budget_by_category['category'] == category]['amount'].sum()
                budget_amounts.append(budget_amount)
                
                # Get expense amount
                expense_amount = 0
                if category in expense_by_category['category'].values:
                    expense_amount = expense_by_category[expense_by_category['category'] == category]['amount'].sum()
                expense_amounts.append(expense_amount)
                
            # Create chart data
            x = range(len(categories))
            width = 0.35
            
            # Create bars
            self.budget_ax.bar(x, budget_amounts, width, label='Budget', color='#3498db')
            self.budget_ax.bar([i + width for i in x], expense_amounts, width, label='Actual', color='#e74c3c')
            
            # Add labels
            self.budget_ax.set_xlabel('Category')
            self.budget_ax.set_ylabel('Amount (₹)')
            self.budget_ax.set_title('Budget vs. Actual Expenses by Category')
            self.budget_ax.set_xticks([i + width/2 for i in x])
            self.budget_ax.set_xticklabels(categories)
            self.budget_ax.legend()
            
            # Format y-axis as currency
            self.budget_ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'₹{int(x):,}'))
            
            # Rotate x labels for better readability
            plt.setp(self.budget_ax.get_xticklabels(), rotation=45, ha='right')
            
            self.budget_fig.tight_layout()
        
        # Category breakdown chart (pie chart)
        if len(self.expenses_df) > 0:
            # Group expenses by category
            expense_by_category = self.expenses_df.groupby('category')['amount'].sum()
            
            # Create pie chart
            self.category_ax.pie(expense_by_category, labels=expense_by_category.index, autopct='%1.1f%%', 
                               startangle=90, shadow=True, explode=[0.05] * len(expense_by_category),
                               colors=plt.cm.tab10.colors)
            self.category_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            self.category_ax.set_title('Expense Distribution by Category')
            
            self.category_fig.tight_layout()
            
        # Update canvases
        self.budget_canvas.draw()
        self.category_canvas.draw()
