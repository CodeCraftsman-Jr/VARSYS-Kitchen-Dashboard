"""
Sales Reports Module
Handles Zomato and Swiggy sales tracking and reporting
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from utils.table_styling import apply_universal_column_resizing
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTabWidget,
                             QPushButton, QComboBox, QDateEdit, QGroupBox,
                             QGridLayout, QFrame, QFormLayout, QLineEdit,
                             QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog,
                             QProgressBar, QTextEdit)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class SalesMetricsCard(QFrame):
    """Sales metrics display card"""
    
    def __init__(self, title: str, value: str = "0", subtitle: str = "", color: str = "#3b82f6"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin: 8px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #64748b;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 10))
            subtitle_label.setStyleSheet("color: #94a3b8;")
            layout.addWidget(subtitle_label)
    
    def update_value(self, value: str):
        """Update the displayed value"""
        self.value_label.setText(value)

class SalesReportsWidget(QWidget):
    """Sales reports widget for Zomato and Swiggy tracking"""
    
    # Signals
    data_changed = Signal()
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI
        self.init_ui()
        
        # Load data
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Sales Reports & Analytics")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Import buttons
        import_zomato_btn = QPushButton("📊 Import Zomato Report")
        import_zomato_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        import_zomato_btn.clicked.connect(self.import_zomato_report)
        header_layout.addWidget(import_zomato_btn)
        
        import_swiggy_btn = QPushButton("🍔 Import Swiggy Report")
        import_swiggy_btn.setStyleSheet("""
            QPushButton {
                background-color: #f97316;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #ea580c;
            }
        """)
        import_swiggy_btn.clicked.connect(self.import_swiggy_report)
        header_layout.addWidget(import_swiggy_btn)
        
        layout.addLayout(header_layout)
        
        # Sales overview cards
        self.create_sales_overview(layout)
        
        # Main content tabs
        self.create_tabs_section(layout)
    
    def create_sales_overview(self, parent_layout):
        """Create sales overview cards"""
        overview_frame = QFrame()
        overview_frame.setStyleSheet("background: transparent; border: none;")
        
        overview_layout = QGridLayout(overview_frame)
        overview_layout.setSpacing(16)
        
        # Initialize overview cards
        self.total_sales_card = SalesMetricsCard("Total Sales", "₹0", "Today", "#10b981")
        self.zomato_sales_card = SalesMetricsCard("Zomato Sales", "₹0", "Today", "#dc2626")
        self.swiggy_sales_card = SalesMetricsCard("Swiggy Sales", "₹0", "Today", "#f97316")
        self.commission_card = SalesMetricsCard("Total Commission", "₹0", "Platform Fees", "#ef4444")
        
        overview_layout.addWidget(self.total_sales_card, 0, 0)
        overview_layout.addWidget(self.zomato_sales_card, 0, 1)
        overview_layout.addWidget(self.swiggy_sales_card, 0, 2)
        overview_layout.addWidget(self.commission_card, 0, 3)
        
        parent_layout.addWidget(overview_frame)
    
    def create_tabs_section(self, parent_layout):
        """Create tabbed interface for different views"""
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
        
        # Sales Overview Tab
        self.create_overview_tab()
        
        # Platform Analytics Tab
        self.create_platform_analytics_tab()
        
        # Commission Analysis Tab
        self.create_commission_analysis_tab()
        
        # Reports Tab
        self.create_reports_tab()
        
        parent_layout.addWidget(self.tabs)
    
    def create_overview_tab(self):
        """Create sales overview tab"""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Date filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Today", "This Week", "This Month", "This Year", "All Time"])
        self.period_combo.currentTextChanged.connect(self.update_sales_overview)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(10)
        self.sales_table.setHorizontalHeaderLabels([
            "Date", "Order ID", "Platform", "Customer", "Items", 
            "Subtotal", "Commission", "Delivery Fee", "Total", "Status"
        ])
        
        # Apply universal column resizing functionality
        sales_default_column_widths = {
            0: 100,  # Date
            1: 120,  # Order ID
            2: 100,  # Platform
            3: 150,  # Customer
            4: 200,  # Items
            5: 100,  # Subtotal
            6: 100,  # Commission
            7: 100,  # Delivery Fee
            8: 100,  # Total
            9: 80    # Status
        }

        # Apply column resizing with settings persistence
        self.sales_table_resizer = apply_universal_column_resizing(
            self.sales_table,
            'sales_reports_column_settings.json',
            sales_default_column_widths
        )

        print("✅ Applied universal column resizing to sales reports table")

        # Enable sorting functionality for sales reports table (history table - preserve all records)
        self.sales_table.setSortingEnabled(True)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        layout.addWidget(self.sales_table)
        
        self.tabs.addTab(overview_widget, "Sales Overview")
    
    def create_platform_analytics_tab(self):
        """Create platform analytics tab"""
        platform_widget = QWidget()
        layout = QVBoxLayout(platform_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Platform comparison
        comparison_frame = QFrame()
        comparison_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        comparison_layout = QGridLayout(comparison_frame)
        
        # Zomato metrics
        zomato_label = QLabel("Zomato Performance")
        zomato_label.setFont(QFont("Arial", 14, QFont.Bold))
        zomato_label.setStyleSheet("color: #dc2626;")
        comparison_layout.addWidget(zomato_label, 0, 0, 1, 2)
        
        self.zomato_orders_label = QLabel("Orders: 0")
        self.zomato_revenue_label = QLabel("Revenue: ₹0")
        self.zomato_commission_label = QLabel("Commission: ₹0")
        self.zomato_avg_order_label = QLabel("Avg Order: ₹0")
        
        comparison_layout.addWidget(self.zomato_orders_label, 1, 0)
        comparison_layout.addWidget(self.zomato_revenue_label, 1, 1)
        comparison_layout.addWidget(self.zomato_commission_label, 2, 0)
        comparison_layout.addWidget(self.zomato_avg_order_label, 2, 1)
        
        # Swiggy metrics
        swiggy_label = QLabel("Swiggy Performance")
        swiggy_label.setFont(QFont("Arial", 14, QFont.Bold))
        swiggy_label.setStyleSheet("color: #f97316;")
        comparison_layout.addWidget(swiggy_label, 0, 2, 1, 2)
        
        self.swiggy_orders_label = QLabel("Orders: 0")
        self.swiggy_revenue_label = QLabel("Revenue: ₹0")
        self.swiggy_commission_label = QLabel("Commission: ₹0")
        self.swiggy_avg_order_label = QLabel("Avg Order: ₹0")
        
        comparison_layout.addWidget(self.swiggy_orders_label, 1, 2)
        comparison_layout.addWidget(self.swiggy_revenue_label, 1, 3)
        comparison_layout.addWidget(self.swiggy_commission_label, 2, 2)
        comparison_layout.addWidget(self.swiggy_avg_order_label, 2, 3)
        
        layout.addWidget(comparison_frame)
        
        # Charts area
        if MATPLOTLIB_AVAILABLE:
            self.create_platform_charts(layout)
        
        self.tabs.addTab(platform_widget, "Platform Analytics")
    
    def create_commission_analysis_tab(self):
        """Create commission analysis tab"""
        commission_widget = QWidget()
        layout = QVBoxLayout(commission_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Commission summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        summary_layout = QGridLayout(summary_frame)
        
        # Commission cards
        self.total_commission_card = SalesMetricsCard("Total Commission", "₹0", "This Month", "#ef4444")
        self.commission_rate_card = SalesMetricsCard("Avg Commission Rate", "0%", "Across Platforms", "#f59e0b")
        self.net_revenue_card = SalesMetricsCard("Net Revenue", "₹0", "After Commission", "#10b981")
        
        summary_layout.addWidget(self.total_commission_card, 0, 0)
        summary_layout.addWidget(self.commission_rate_card, 0, 1)
        summary_layout.addWidget(self.net_revenue_card, 0, 2)
        
        layout.addWidget(summary_frame)
        
        # Commission breakdown table
        self.commission_table = QTableWidget()
        self.commission_table.setColumnCount(6)
        self.commission_table.setHorizontalHeaderLabels([
            "Platform", "Orders", "Gross Revenue", "Commission Rate", "Commission Amount", "Net Revenue"
        ])
        self.commission_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.commission_table)
        
        self.tabs.addTab(commission_widget, "Commission Analysis")
    
    def create_reports_tab(self):
        """Create reports generation tab"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Report generation controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        controls_layout = QFormLayout(controls_frame)
        
        # Date range
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        controls_layout.addRow("Start Date:", self.start_date)
        controls_layout.addRow("End Date:", self.end_date)
        
        # Report type
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Daily Sales Summary",
            "Platform Comparison",
            "Commission Analysis",
            "Top Selling Items",
            "Customer Analysis"
        ])
        controls_layout.addRow("Report Type:", self.report_type_combo)
        
        # Generate button
        generate_btn = QPushButton("Generate Report")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        generate_btn.clicked.connect(self.generate_report)
        controls_layout.addRow("", generate_btn)
        
        layout.addWidget(controls_frame)
        
        # Report display area
        self.report_text = QTextEdit()
        self.report_text.setFont(QFont("Consolas", 10))
        self.report_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout.addWidget(self.report_text)
        
        self.tabs.addTab(reports_widget, "Reports")
    
    def create_platform_charts(self, layout):
        """Create platform comparison charts"""
        try:
            # Revenue comparison chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Sample data - replace with actual data
            platforms = ['Zomato', 'Swiggy', 'Local']
            revenues = [50000, 45000, 25000]
            orders = [150, 140, 80]
            
            # Revenue chart
            ax1.bar(platforms, revenues, color=['#dc2626', '#f97316', '#10b981'])
            ax1.set_title('Revenue by Platform')
            ax1.set_ylabel('Revenue (₹)')
            
            # Orders chart
            ax2.bar(platforms, orders, color=['#dc2626', '#f97316', '#10b981'])
            ax2.set_title('Orders by Platform')
            ax2.set_ylabel('Number of Orders')
            
            plt.tight_layout()
            
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            
        except Exception as e:
            self.logger.error(f"Error creating platform charts: {e}")
    
    def import_zomato_report(self):
        """Import Zomato sales report"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Zomato Report", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # Load and process Zomato report
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # Process and add to sales data
                self.process_platform_report(df, 'Zomato')
                
                QMessageBox.information(self, "Success", "Zomato report imported successfully!")
                self.update_sales_overview()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import Zomato report: {str(e)}")
    
    def import_swiggy_report(self):
        """Import Swiggy sales report"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Swiggy Report", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # Load and process Swiggy report
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # Process and add to sales data
                self.process_platform_report(df, 'Swiggy')
                
                QMessageBox.information(self, "Success", "Swiggy report imported successfully!")
                self.update_sales_overview()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import Swiggy report: {str(e)}")
    
    def process_platform_report(self, df, platform):
        """Process platform report and add to sales data"""
        try:
            # This is a placeholder - implement actual report processing based on platform format
            processed_data = []
            
            for _, row in df.iterrows():
                # Map platform-specific columns to standard format
                order_data = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'order_id': f"{platform}-{len(processed_data)+1}",
                    'platform': platform,
                    'customer': 'Customer',
                    'items': 'Various',
                    'subtotal': 0,
                    'commission': 0,
                    'delivery_fee': 0,
                    'total': 0,
                    'status': 'Completed'
                }
                processed_data.append(order_data)
            
            # Add to sales data
            if 'sales' not in self.data:
                self.data['sales'] = pd.DataFrame()
            
            new_df = pd.DataFrame(processed_data)
            self.data['sales'] = pd.concat([self.data['sales'], new_df], ignore_index=True)
            
            # Save to CSV
            self.data['sales'].to_csv('data/sales.csv', index=False)
            
        except Exception as e:
            self.logger.error(f"Error processing {platform} report: {e}")
            raise
    
    def update_sales_overview(self):
        """Update sales overview with current data"""
        try:
            if 'sales' not in self.data or self.data['sales'].empty:
                return
            
            sales_df = self.data['sales']
            
            # Filter by selected period
            period = self.period_combo.currentText()
            filtered_df = self.filter_by_period(sales_df, period)
            
            # Update overview cards
            total_sales = filtered_df['total'].sum() if 'total' in filtered_df.columns else 0
            zomato_sales = filtered_df[filtered_df['platform'] == 'Zomato']['total'].sum() if 'platform' in filtered_df.columns else 0
            swiggy_sales = filtered_df[filtered_df['platform'] == 'Swiggy']['total'].sum() if 'platform' in filtered_df.columns else 0
            total_commission = filtered_df['commission'].sum() if 'commission' in filtered_df.columns else 0
            
            self.total_sales_card.update_value(f"₹{total_sales:.2f}")
            self.zomato_sales_card.update_value(f"₹{zomato_sales:.2f}")
            self.swiggy_sales_card.update_value(f"₹{swiggy_sales:.2f}")
            self.commission_card.update_value(f"₹{total_commission:.2f}")
            
            # Update sales table
            self.populate_sales_table(filtered_df)
            
        except Exception as e:
            self.logger.error(f"Error updating sales overview: {e}")
    
    def filter_by_period(self, df, period):
        """Filter dataframe by selected period"""
        if df.empty or 'date' not in df.columns:
            return df
        
        today = datetime.now()
        
        if period == "Today":
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "This Week":
            start_date = today - timedelta(days=today.weekday())
        elif period == "This Month":
            start_date = today.replace(day=1)
        elif period == "This Year":
            start_date = today.replace(month=1, day=1)
        else:  # All Time
            return df
        
        # Convert date column to datetime if it's not already
        df['date'] = pd.to_datetime(df['date'])
        
        return df[df['date'] >= start_date]
    
    def populate_sales_table(self, df):
        """Populate sales table with data"""
        try:
            self.sales_table.setRowCount(len(df))
            
            for row, (_, sale) in enumerate(df.iterrows()):
                self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale.get('date', ''))))
                self.sales_table.setItem(row, 1, QTableWidgetItem(str(sale.get('order_id', ''))))
                self.sales_table.setItem(row, 2, QTableWidgetItem(str(sale.get('platform', ''))))
                self.sales_table.setItem(row, 3, QTableWidgetItem(str(sale.get('customer', ''))))
                self.sales_table.setItem(row, 4, QTableWidgetItem(str(sale.get('items', ''))))
                self.sales_table.setItem(row, 5, QTableWidgetItem(f"₹{sale.get('subtotal', 0):.2f}"))
                self.sales_table.setItem(row, 6, QTableWidgetItem(f"₹{sale.get('commission', 0):.2f}"))
                self.sales_table.setItem(row, 7, QTableWidgetItem(f"₹{sale.get('delivery_fee', 0):.2f}"))
                self.sales_table.setItem(row, 8, QTableWidgetItem(f"₹{sale.get('total', 0):.2f}"))
                self.sales_table.setItem(row, 9, QTableWidgetItem(str(sale.get('status', ''))))
                
        except Exception as e:
            self.logger.error(f"Error populating sales table: {e}")
    
    def generate_report(self):
        """Generate selected report"""
        try:
            report_type = self.report_type_combo.currentText()
            start_date = self.start_date.date().toPython()
            end_date = self.end_date.date().toPython()
            
            # Generate report based on type
            if report_type == "Daily Sales Summary":
                report = self.generate_daily_summary(start_date, end_date)
            elif report_type == "Platform Comparison":
                report = self.generate_platform_comparison(start_date, end_date)
            elif report_type == "Commission Analysis":
                report = self.generate_commission_analysis(start_date, end_date)
            else:
                report = "Report generation not implemented for this type yet."
            
            self.report_text.setText(report)
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            self.report_text.setText(f"Error generating report: {str(e)}")
    
    def generate_daily_summary(self, start_date, end_date):
        """Generate daily sales summary report"""
        try:
            if 'sales' not in self.data or self.data['sales'].empty:
                return "No sales data available for the selected period."
            
            sales_df = self.data['sales']
            
            # Filter by date range
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            filtered_df = sales_df[
                (sales_df['date'] >= pd.Timestamp(start_date)) &
                (sales_df['date'] <= pd.Timestamp(end_date))
            ]
            
            if filtered_df.empty:
                return "No sales data found for the selected date range."
            
            # Generate summary
            total_orders = len(filtered_df)
            total_revenue = filtered_df['total'].sum()
            total_commission = filtered_df['commission'].sum()
            net_revenue = total_revenue - total_commission
            
            report = f"""
DAILY SALES SUMMARY
Period: {start_date} to {end_date}
{'='*50}

Total Orders: {total_orders}
Total Revenue: ₹{total_revenue:.2f}
Total Commission: ₹{total_commission:.2f}
Net Revenue: ₹{net_revenue:.2f}

Platform Breakdown:
"""
            
            # Platform breakdown
            for platform in filtered_df['platform'].unique():
                platform_data = filtered_df[filtered_df['platform'] == platform]
                platform_orders = len(platform_data)
                platform_revenue = platform_data['total'].sum()
                
                report += f"\n{platform}:"
                report += f"\n  Orders: {platform_orders}"
                report += f"\n  Revenue: ₹{platform_revenue:.2f}"
            
            return report
            
        except Exception as e:
            return f"Error generating daily summary: {str(e)}"
    
    def generate_platform_comparison(self, start_date, end_date):
        """Generate platform comparison report"""
        return "Platform comparison report will be implemented here."
    
    def generate_commission_analysis(self, start_date, end_date):
        """Generate commission analysis report"""
        return "Commission analysis report will be implemented here."
    
    def load_data(self):
        """Load sales data"""
        try:
            # Initialize sales data if not exists
            if 'sales' not in self.data:
                self.data['sales'] = pd.DataFrame()
            
            # Update overview
            self.update_sales_overview()
            
        except Exception as e:
            self.logger.error(f"Error loading sales data: {e}")
