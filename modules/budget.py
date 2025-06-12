from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                             QMessageBox, QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import calendar
import os

class BudgetWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.budget_df = data['budget'].copy()
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Budget Tracker")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
    
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for different budget views
        self.monthly_overview_tab = QWidget()
        self.add_edit_tab = QWidget()
        self.category_analysis_tab = QWidget()
        self.yearly_summary_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.monthly_overview_tab, "Monthly Overview")
        self.tabs.addTab(self.add_edit_tab, "Add/Edit Expenses")
        self.tabs.addTab(self.category_analysis_tab, "Category Analysis")
        self.tabs.addTab(self.yearly_summary_tab, "Yearly Summary")
        
        # Set up each tab
        self.setup_monthly_overview_tab()
        self.setup_add_edit_tab()
        self.setup_category_analysis_tab()
        self.setup_yearly_summary_tab()
    
    def setup_monthly_overview_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.monthly_overview_tab)
        
        # Add subheader
        header = QLabel("Monthly Budget Overview")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Date filter section
        date_filter_widget = QWidget()
        date_filter_layout = QHBoxLayout(date_filter_widget)
        
        # Month filter
        month_label = QLabel("Month:")
        self.month_combo = QComboBox()
        for i in range(1, 13):
            self.month_combo.addItem(calendar.month_name[i], i)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        
        # Year filter
        year_label = QLabel("Year:")
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        
        # Safely get years from the dataframe
        years = [current_year]
        if len(self.budget_df) > 0 and 'date' in self.budget_df.columns:
            # Ensure date column is datetime type
            if self.budget_df['date'].dtype == 'object':
                try:
                    self.budget_df['date'] = pd.to_datetime(self.budget_df['date'], errors='coerce')
                except Exception as e:
                    print(f"Error converting dates: {e}")
            
            # Only extract years if we have datetime data
            if pd.api.types.is_datetime64_any_dtype(self.budget_df['date']):
                years_from_df = sorted(self.budget_df['date'].dt.year.unique(), reverse=True)
                if len(years_from_df) > 0:
                    years = years_from_df
        
        for year in years:
            self.year_combo.addItem(str(year), year)
        
        # Add widgets to date filter layout
        date_filter_layout.addWidget(month_label)
        date_filter_layout.addWidget(self.month_combo)
        date_filter_layout.addWidget(year_label)
        date_filter_layout.addWidget(self.year_combo)
        date_filter_layout.addStretch(1)
        
        layout.addWidget(date_filter_widget)
        
        # Connect signals
        self.month_combo.currentIndexChanged.connect(self.update_monthly_overview)
        self.year_combo.currentIndexChanged.connect(self.update_monthly_overview)
        
        # Placeholder for monthly summary
        self.monthly_summary_widget = QWidget()
        self.monthly_summary_layout = QVBoxLayout(self.monthly_summary_widget)
        layout.addWidget(self.monthly_summary_widget)
        
        # Update the monthly overview
        self.update_monthly_overview()
    
    def update_monthly_overview(self):
        # Clear the monthly summary layout
        while self.monthly_summary_layout.count():
            item = self.monthly_summary_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get selected month and year
        selected_month = self.month_combo.currentData()
        selected_year = self.year_combo.currentData()
        
        # Initialize empty dataframe for filtered data
        monthly_budget = pd.DataFrame()
        
        # Filter data for selected month and year if we have data
        if len(self.budget_df) > 0 and 'date' in self.budget_df.columns:
            # Ensure date column is datetime type
            if not pd.api.types.is_datetime64_any_dtype(self.budget_df['date']):
                try:
                    self.budget_df['date'] = pd.to_datetime(self.budget_df['date'], errors='coerce')
                except Exception as e:
                    print(f"Error converting dates: {e}")
            
            # Only apply date filters if we have datetime data
            if pd.api.types.is_datetime64_any_dtype(self.budget_df['date']):
                monthly_budget = self.budget_df[
                    (self.budget_df['date'].dt.month == selected_month) & 
                    (self.budget_df['date'].dt.year == selected_year)
                ]
        
        # Display placeholder text if no data
        if len(monthly_budget) == 0:
            no_data_label = QLabel("No budget data available for the selected month and year.")
            no_data_label.setAlignment(Qt.AlignCenter)
            self.monthly_summary_layout.addWidget(no_data_label)
            return
        
        # TODO: Implement monthly overview visualization
        # This will include budget vs. actual spending, category breakdown, etc.
        placeholder = QLabel("Monthly overview visualization will be implemented here")
        placeholder.setAlignment(Qt.AlignCenter)
        self.monthly_summary_layout.addWidget(placeholder)
    
    def setup_add_edit_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_edit_tab)
        
        # Add subheader
        header = QLabel("Add/Edit Budget Items")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # TODO: Implement add/edit budget items form
        placeholder = QLabel("Add/Edit budget items form will be implemented here")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
    
    def setup_category_analysis_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.category_analysis_tab)
        
        # Add subheader
        header = QLabel("Category Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # TODO: Implement category analysis visualization
        placeholder = QLabel("Category analysis visualization will be implemented here")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
    
    def setup_yearly_summary_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.yearly_summary_tab)
        
        # Add subheader
        header = QLabel("Yearly Summary")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # TODO: Implement yearly summary visualization
        placeholder = QLabel("Yearly summary visualization will be implemented here")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
