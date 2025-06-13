"""
Enhanced Sales Module with Zomato/Swiggy Integration
Modern UI with comprehensive sales tracking and analytics
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
                             QFrame, QScrollArea, QProgressBar)
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

class SalesMetricsCard(QFrame):
    """Modern metrics card widget"""
    
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
                background-color: rgba(59, 130, 246, 0.05);
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

class EnhancedSalesWidget(QWidget):
    """Enhanced sales widget with modern UI and platform integration"""
    
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
        self.refresh_timer.timeout.connect(self.refresh_metrics)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Sales Analytics")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Import buttons
        import_zomato_btn = QPushButton("Import Zomato Data")
        import_zomato_btn.setStyleSheet("background-color: #dc2626; color: white;")
        import_zomato_btn.clicked.connect(self.import_zomato_data)
        header_layout.addWidget(import_zomato_btn)
        
        import_swiggy_btn = QPushButton("Import Swiggy Data")
        import_swiggy_btn.setStyleSheet("background-color: #ea580c; color: white;")
        import_swiggy_btn.clicked.connect(self.import_swiggy_data)
        header_layout.addWidget(import_swiggy_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_metrics)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Metrics Cards
        self.create_metrics_section(layout)
        
        # Main Content Tabs
        self.create_tabs_section(layout)
    
    def create_metrics_section(self, parent_layout):
        """Create metrics cards section"""
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("background: transparent; border: none;")
        
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setSpacing(16)
        
        # Initialize metrics cards
        self.total_sales_card = SalesMetricsCard("Total Sales", "₹0", "Today", "#10b981")
        self.orders_card = SalesMetricsCard("Orders", "0", "Today", "#3b82f6")
        self.avg_order_card = SalesMetricsCard("Avg Order Value", "₹0", "Today", "#8b5cf6")
        self.platform_revenue_card = SalesMetricsCard("Platform Revenue", "₹0", "Zomato + Swiggy", "#f59e0b")
        
        metrics_layout.addWidget(self.total_sales_card, 0, 0)
        metrics_layout.addWidget(self.orders_card, 0, 1)
        metrics_layout.addWidget(self.avg_order_card, 0, 2)
        metrics_layout.addWidget(self.platform_revenue_card, 0, 3)
        
        parent_layout.addWidget(metrics_frame)
    
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
        self.create_platform_tab()
        
        # Order Management Tab
        self.create_orders_tab()
        
        # Reports Tab
        self.create_reports_tab()
        
        parent_layout.addWidget(self.tabs)
    
    def create_overview_tab(self):
        """Create sales overview tab"""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Sales Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(12)
        self.sales_table.setHorizontalHeaderLabels([
            "Date", "Order ID", "Platform", "Customer", "Items", 
            "Quantity", "Subtotal", "Taxes", "Delivery Fee", 
            "Discount", "Total Amount", "Status"
        ])
        
        # Modern table styling
        self.sales_table.setStyleSheet("""
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
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Order ID
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Platform
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Customer
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Items
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Subtotal
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Taxes
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Delivery Fee
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Discount
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents) # Total
        header.setSectionResizeMode(11, QHeaderView.ResizeToContents) # Status
        
        layout.addWidget(self.sales_table)
        
        # Add New Sale Button
        add_sale_btn = QPushButton("Add New Sale")
        add_sale_btn.setStyleSheet("""
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
        add_sale_btn.clicked.connect(self.add_new_sale)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_sale_btn)
        layout.addLayout(button_layout)
        
        self.tabs.addTab(overview_widget, "Sales Overview")
    
    def create_platform_tab(self):
        """Create platform analytics tab"""
        platform_widget = QWidget()
        layout = QVBoxLayout(platform_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Platform comparison metrics
        platform_frame = QFrame()
        platform_frame.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;")
        platform_layout = QGridLayout(platform_frame)
        
        # Zomato metrics
        zomato_label = QLabel("Zomato Analytics")
        zomato_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #dc2626;")
        platform_layout.addWidget(zomato_label, 0, 0, 1, 2)
        
        self.zomato_orders_label = QLabel("Orders: 0")
        self.zomato_revenue_label = QLabel("Revenue: ₹0")
        self.zomato_commission_label = QLabel("Commission: ₹0")
        
        platform_layout.addWidget(self.zomato_orders_label, 1, 0)
        platform_layout.addWidget(self.zomato_revenue_label, 1, 1)
        platform_layout.addWidget(self.zomato_commission_label, 2, 0)
        
        # Swiggy metrics
        swiggy_label = QLabel("Swiggy Analytics")
        swiggy_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #ea580c;")
        platform_layout.addWidget(swiggy_label, 3, 0, 1, 2)
        
        self.swiggy_orders_label = QLabel("Orders: 0")
        self.swiggy_revenue_label = QLabel("Revenue: ₹0")
        self.swiggy_commission_label = QLabel("Commission: ₹0")
        
        platform_layout.addWidget(self.swiggy_orders_label, 4, 0)
        platform_layout.addWidget(self.swiggy_revenue_label, 4, 1)
        platform_layout.addWidget(self.swiggy_commission_label, 5, 0)
        
        layout.addWidget(platform_frame)
        layout.addStretch()
        
        self.tabs.addTab(platform_widget, "Platform Analytics")
    
    def create_orders_tab(self):
        """Create order management tab"""
        orders_widget = QWidget()
        layout = QVBoxLayout(orders_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Order status overview
        status_frame = QFrame()
        status_frame.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;")
        status_layout = QHBoxLayout(status_frame)
        
        # Status cards
        self.pending_orders_card = SalesMetricsCard("Pending", "0", "Orders", "#f59e0b")
        self.completed_orders_card = SalesMetricsCard("Completed", "0", "Orders", "#10b981")
        self.cancelled_orders_card = SalesMetricsCard("Cancelled", "0", "Orders", "#ef4444")
        
        status_layout.addWidget(self.pending_orders_card)
        status_layout.addWidget(self.completed_orders_card)
        status_layout.addWidget(self.cancelled_orders_card)
        
        layout.addWidget(status_frame)
        layout.addStretch()
        
        self.tabs.addTab(orders_widget, "Order Management")
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Report generation section
        reports_frame = QFrame()
        reports_frame.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;")
        reports_layout = QVBoxLayout(reports_frame)
        
        title_label = QLabel("Generate Reports")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 16px;")
        reports_layout.addWidget(title_label)
        
        # Report buttons
        buttons_layout = QGridLayout()
        
        daily_report_btn = QPushButton("Daily Sales Report")
        weekly_report_btn = QPushButton("Weekly Summary")
        monthly_report_btn = QPushButton("Monthly Analysis")
        platform_report_btn = QPushButton("Platform Comparison")
        
        for btn in [daily_report_btn, weekly_report_btn, monthly_report_btn, platform_report_btn]:
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
        
        buttons_layout.addWidget(daily_report_btn, 0, 0)
        buttons_layout.addWidget(weekly_report_btn, 0, 1)
        buttons_layout.addWidget(monthly_report_btn, 1, 0)
        buttons_layout.addWidget(platform_report_btn, 1, 1)
        
        reports_layout.addLayout(buttons_layout)
        layout.addWidget(reports_frame)
        layout.addStretch()
        
        self.tabs.addTab(reports_widget, "Reports")
    
    def load_data(self):
        """Load and display sales data"""
        try:
            if 'sales' in self.data and not self.data['sales'].empty:
                self.populate_sales_table()
                self.update_metrics()
            else:
                self.logger.info("No sales data found")
        except Exception as e:
            self.logger.error(f"Error loading sales data: {e}")
            notify_error("Error", f"Failed to load sales data: {str(e)}", parent=self)
    
    def populate_sales_table(self):
        """Populate the sales table with data"""
        try:
            sales_df = self.data['sales']
            self.sales_table.setRowCount(len(sales_df))
            
            for row, (_, sale) in enumerate(sales_df.iterrows()):
                # Date
                date_item = QTableWidgetItem(str(sale.get('date', '')))
                self.sales_table.setItem(row, 0, date_item)
                
                # Order ID
                order_id = str(sale.get('order_id', f"ORD-{row+1:04d}"))
                order_item = QTableWidgetItem(order_id)
                self.sales_table.setItem(row, 1, order_item)
                
                # Platform
                platform = str(sale.get('platform', 'Direct'))
                platform_item = QTableWidgetItem(platform)
                self.sales_table.setItem(row, 2, platform_item)
                
                # Customer
                customer = str(sale.get('customer', 'Walk-in'))
                customer_item = QTableWidgetItem(customer)
                self.sales_table.setItem(row, 3, customer_item)
                
                # Items
                items = str(sale.get('item_name', ''))
                items_item = QTableWidgetItem(items)
                self.sales_table.setItem(row, 4, items_item)
                
                # Quantity
                quantity = str(sale.get('quantity', 1))
                quantity_item = QTableWidgetItem(quantity)
                self.sales_table.setItem(row, 5, quantity_item)
                
                # Subtotal
                subtotal = f"₹{sale.get('subtotal', sale.get('total_amount', 0)):.2f}"
                subtotal_item = QTableWidgetItem(subtotal)
                self.sales_table.setItem(row, 6, subtotal_item)
                
                # Taxes
                taxes = f"₹{sale.get('taxes', 0):.2f}"
                taxes_item = QTableWidgetItem(taxes)
                self.sales_table.setItem(row, 7, taxes_item)
                
                # Delivery Fee
                delivery_fee = f"₹{sale.get('delivery_fee', 0):.2f}"
                delivery_item = QTableWidgetItem(delivery_fee)
                self.sales_table.setItem(row, 8, delivery_item)
                
                # Discount
                discount = f"₹{sale.get('discount', 0):.2f}"
                discount_item = QTableWidgetItem(discount)
                self.sales_table.setItem(row, 9, discount_item)
                
                # Total Amount
                total = f"₹{sale.get('total_amount', 0):.2f}"
                total_item = QTableWidgetItem(total)
                self.sales_table.setItem(row, 10, total_item)
                
                # Status
                status = str(sale.get('status', 'Completed'))
                status_item = QTableWidgetItem(status)
                self.sales_table.setItem(row, 11, status_item)
                
        except Exception as e:
            self.logger.error(f"Error populating sales table: {e}")
    
    def update_metrics(self):
        """Update metrics cards with current data"""
        try:
            if 'sales' not in self.data or self.data['sales'].empty:
                return
            
            sales_df = self.data['sales']
            today = datetime.now().date()
            
            # Filter today's sales
            if 'date' in sales_df.columns:
                today_sales = sales_df[pd.to_datetime(sales_df['date']).dt.date == today]
            else:
                today_sales = sales_df
            
            # Calculate metrics
            total_sales = today_sales['total_amount'].sum() if 'total_amount' in today_sales.columns else 0
            total_orders = len(today_sales)
            avg_order = total_sales / total_orders if total_orders > 0 else 0
            
            # Platform revenue
            platform_revenue = sales_df[sales_df['platform'].isin(['Zomato', 'Swiggy'])]['total_amount'].sum() if 'platform' in sales_df.columns else 0
            
            # Update cards
            self.total_sales_card.findChild(QLabel).setText(f"₹{total_sales:.2f}")
            self.orders_card.findChild(QLabel).setText(str(total_orders))
            self.avg_order_card.findChild(QLabel).setText(f"₹{avg_order:.2f}")
            self.platform_revenue_card.findChild(QLabel).setText(f"₹{platform_revenue:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
    
    def refresh_metrics(self):
        """Refresh all metrics and data"""
        self.load_data()
        notify_info("Refreshed", "Sales data refreshed successfully", parent=self)
    
    def import_zomato_data(self):
        """Import data from Zomato reports"""
        try:
            from .data_import_wizard import DataImportWizard

            # Create and show import wizard
            wizard = DataImportWizard(self)
            wizard.data_imported.connect(self.handle_imported_data)

            # Switch to Zomato tab
            wizard.tabs.setCurrentIndex(0)  # Platform import tab

            if wizard.exec() == wizard.Accepted:
                self.load_data()
                self.data_changed.emit()

        except ImportError:
            # Fallback to simple file dialog
            from PySide6.QtWidgets import QFileDialog

            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Select Zomato Report",
                "",
                "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
            )

            if file_path:
                self.process_zomato_file(file_path)

    def import_swiggy_data(self):
        """Import data from Swiggy reports"""
        try:
            from .data_import_wizard import DataImportWizard

            # Create and show import wizard
            wizard = DataImportWizard(self)
            wizard.data_imported.connect(self.handle_imported_data)

            # Switch to Swiggy tab
            wizard.tabs.setCurrentIndex(0)  # Platform import tab

            if wizard.exec() == wizard.Accepted:
                self.load_data()
                self.data_changed.emit()

        except ImportError:
            # Fallback to simple file dialog
            from PySide6.QtWidgets import QFileDialog

            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Select Swiggy Report",
                "",
                "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
            )

            if file_path:
                self.process_swiggy_file(file_path)

    def handle_imported_data(self, results):
        """Handle data imported from wizard"""
        try:
            if results['import_type'] in ['zomato', 'swiggy'] and results['data'] is not None:
                # Merge with existing sales data
                if 'sales' not in self.data:
                    self.data['sales'] = pd.DataFrame()

                # Append new data
                self.data['sales'] = pd.concat([self.data['sales'], results['data']], ignore_index=True)

                # Save to file
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
                sales_file = os.path.join(data_dir, 'sales.csv')
                self.data['sales'].to_csv(sales_file, index=False)

                # Refresh display
                self.load_data()
                self.data_changed.emit()

                notify_success("Import Complete",
                             f"Successfully imported {results['records_count']} {results['import_type']} records",
                             parent=self)
        except Exception as e:
            self.logger.error(f"Error handling imported data: {e}")
            notify_error("Import Error", f"Failed to process imported data: {str(e)}", parent=self)

    def process_zomato_file(self, file_path):
        """Process Zomato file directly"""
        try:
            # Read the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Process and add to sales data
            processed_count = 0
            for _, row in df.iterrows():
                if pd.notna(row.get('Order ID', row.get('order_id'))):
                    # Create sales record
                    new_sale = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'order_id': str(row.get('Order ID', row.get('order_id', ''))),
                        'platform': 'Zomato',
                        'customer': 'Zomato Customer',
                        'item_name': str(row.get('Item Name', row.get('item_name', 'Unknown Item'))),
                        'quantity': 1,
                        'subtotal': float(row.get('Item Total', row.get('item_total', 0))),
                        'taxes': float(row.get('Tax', row.get('tax', 0))),
                        'delivery_fee': float(row.get('Delivery Fee', row.get('delivery_fee', 0))),
                        'discount': float(row.get('Discount', row.get('discount', 0))),
                        'total_amount': float(row.get('Net Amount', row.get('net_amount', 0))),
                        'payment_method': 'Online',
                        'status': 'Completed',
                        'notes': 'Imported from Zomato'
                    }

                    # Add to data
                    if 'sales' not in self.data:
                        self.data['sales'] = pd.DataFrame()

                    new_df = pd.DataFrame([new_sale])
                    self.data['sales'] = pd.concat([self.data['sales'], new_df], ignore_index=True)
                    processed_count += 1

            # Save and refresh
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            sales_file = os.path.join(data_dir, 'sales.csv')
            self.data['sales'].to_csv(sales_file, index=False)

            self.load_data()
            self.data_changed.emit()

            notify_success("Import Complete", f"Successfully imported {processed_count} Zomato records", parent=self)

        except Exception as e:
            self.logger.error(f"Error processing Zomato file: {e}")
            notify_error("Import Error", f"Failed to process Zomato file: {str(e)}", parent=self)

    def process_swiggy_file(self, file_path):
        """Process Swiggy file directly"""
        try:
            # Similar processing for Swiggy
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            processed_count = 0
            for _, row in df.iterrows():
                if pd.notna(row.get('Order ID', row.get('order_id'))):
                    new_sale = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'order_id': str(row.get('Order ID', row.get('order_id', ''))),
                        'platform': 'Swiggy',
                        'customer': 'Swiggy Customer',
                        'item_name': str(row.get('Item Name', row.get('item_name', 'Unknown Item'))),
                        'quantity': 1,
                        'subtotal': float(row.get('Item Total', row.get('item_total', 0))),
                        'taxes': float(row.get('Tax', row.get('tax', 0))),
                        'delivery_fee': float(row.get('Delivery Fee', row.get('delivery_fee', 0))),
                        'discount': float(row.get('Discount', row.get('discount', 0))),
                        'total_amount': float(row.get('Net Amount', row.get('net_amount', 0))),
                        'payment_method': 'Online',
                        'status': 'Completed',
                        'notes': 'Imported from Swiggy'
                    }

                    if 'sales' not in self.data:
                        self.data['sales'] = pd.DataFrame()

                    new_df = pd.DataFrame([new_sale])
                    self.data['sales'] = pd.concat([self.data['sales'], new_df], ignore_index=True)
                    processed_count += 1

            # Save and refresh
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            sales_file = os.path.join(data_dir, 'sales.csv')
            self.data['sales'].to_csv(sales_file, index=False)

            self.load_data()
            self.data_changed.emit()

            notify_success("Import Complete", f"Successfully imported {processed_count} Swiggy records", parent=self)

        except Exception as e:
            self.logger.error(f"Error processing Swiggy file: {e}")
            notify_error("Import Error", f"Failed to process Swiggy file: {str(e)}", parent=self)
    
    def add_new_sale(self):
        """Add a new sale entry"""
        dialog = AddSaleDialog(self.data, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            notify_success("Success", "New sale added successfully", parent=self)


class AddSaleDialog(QDialog):
    """Dialog for adding new sales entries"""

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Add New Sale")
        self.setFixedSize(500, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Form fields
        form_layout = QFormLayout()

        self.date_edit = QDateEdit(QDate.currentDate())
        self.order_id_edit = QLineEdit()
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Direct", "Zomato", "Swiggy", "Other"])
        self.customer_edit = QLineEdit()
        self.items_edit = QLineEdit()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setValue(1)
        self.subtotal_edit = QDoubleSpinBox()
        self.subtotal_edit.setMaximum(999999.99)
        self.taxes_edit = QDoubleSpinBox()
        self.taxes_edit.setMaximum(999999.99)
        self.delivery_fee_edit = QDoubleSpinBox()
        self.delivery_fee_edit.setMaximum(999999.99)
        self.discount_edit = QDoubleSpinBox()
        self.discount_edit.setMaximum(999999.99)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Completed", "Cancelled"])
        self.status_combo.setCurrentText("Completed")

        form_layout.addRow("Date:", self.date_edit)
        form_layout.addRow("Order ID:", self.order_id_edit)
        form_layout.addRow("Platform:", self.platform_combo)
        form_layout.addRow("Customer:", self.customer_edit)
        form_layout.addRow("Items:", self.items_edit)
        form_layout.addRow("Quantity:", self.quantity_spin)
        form_layout.addRow("Subtotal:", self.subtotal_edit)
        form_layout.addRow("Taxes:", self.taxes_edit)
        form_layout.addRow("Delivery Fee:", self.delivery_fee_edit)
        form_layout.addRow("Discount:", self.discount_edit)
        form_layout.addRow("Status:", self.status_combo)

        layout.addLayout(form_layout)

        # Total calculation
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #059669;")
        layout.addWidget(self.total_label)

        # Connect signals for auto-calculation
        for widget in [self.subtotal_edit, self.taxes_edit, self.delivery_fee_edit, self.discount_edit]:
            widget.valueChanged.connect(self.calculate_total)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Generate order ID
        self.generate_order_id()

    def generate_order_id(self):
        """Generate a unique order ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        order_id = f"ORD-{timestamp}"
        self.order_id_edit.setText(order_id)

    def calculate_total(self):
        """Calculate and display total amount"""
        subtotal = self.subtotal_edit.value()
        taxes = self.taxes_edit.value()
        delivery_fee = self.delivery_fee_edit.value()
        discount = self.discount_edit.value()

        total = subtotal + taxes + delivery_fee - discount
        self.total_label.setText(f"Total: ₹{total:.2f}")

    def accept(self):
        """Save the new sale"""
        try:
            # Calculate total
            subtotal = self.subtotal_edit.value()
            taxes = self.taxes_edit.value()
            delivery_fee = self.delivery_fee_edit.value()
            discount = self.discount_edit.value()
            total = subtotal + taxes + delivery_fee - discount

            # Create new sale record
            new_sale = {
                'date': self.date_edit.date().toString('yyyy-MM-dd'),
                'order_id': self.order_id_edit.text(),
                'platform': self.platform_combo.currentText(),
                'customer': self.customer_edit.text(),
                'item_name': self.items_edit.text(),
                'quantity': self.quantity_spin.value(),
                'subtotal': subtotal,
                'taxes': taxes,
                'delivery_fee': delivery_fee,
                'discount': discount,
                'total_amount': total,
                'status': self.status_combo.currentText(),
                'payment_method': 'Card',  # Default
                'notes': ''
            }

            # Add to data
            if 'sales' not in self.data:
                self.data['sales'] = pd.DataFrame()

            new_df = pd.DataFrame([new_sale])
            self.data['sales'] = pd.concat([self.data['sales'], new_df], ignore_index=True)

            # Save to file
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            sales_file = os.path.join(data_dir, 'sales.csv')
            self.data['sales'].to_csv(sales_file, index=False)

            # Use inventory integration system for comprehensive updates
            try:
                from modules.inventory_integration import InventoryIntegration

                integration = InventoryIntegration(self.data)
                integration_result = integration.process_sale_completion(new_sale)

                if not integration_result['success']:
                    print(f"Integration warnings: {integration_result['errors']}")

            except Exception as e:
                print(f"Integration error: {e}")

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sale: {str(e)}")
