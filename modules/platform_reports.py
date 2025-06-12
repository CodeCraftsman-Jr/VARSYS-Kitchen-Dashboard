"""
Platform Reports Module
Dedicated module for Zomato and Swiggy report management and analytics
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTabWidget,
                             QPushButton, QComboBox, QDateEdit, QGroupBox,
                             QGridLayout, QFrame, QFormLayout, QLineEdit,
                             QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog,
                             QProgressBar, QTextEdit, QSplitter, QCheckBox)
from PySide6.QtCore import Qt, QDate, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class PlatformMetricsCard(QFrame):
    """Platform-specific metrics display card"""

    def __init__(self, platform: str, title: str, value: str = "0", subtitle: str = "", color: str = "#3b82f6"):
        super().__init__()
        self.platform = platform
        self.setFrameStyle(QFrame.StyledPanel)

        # Platform-specific colors
        platform_colors = {
            'Zomato': '#dc2626',
            'Swiggy': '#f97316',
            'Combined': '#10b981',
            'Commission': '#ef4444'
        }

        card_color = platform_colors.get(platform, color)

        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {card_color}15, stop:1 {card_color}08);
                border: 2px solid {card_color}40;
                border-radius: 16px;
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

        # Platform icon and title
        header_layout = QHBoxLayout()

        # Platform icon
        platform_icons = {
            'Zomato': '🍕',
            'Swiggy': '🍔',
            'Combined': '📊',
            'Commission': '💰'
        }

        icon_label = QLabel(platform_icons.get(platform, '📈'))
        icon_label.setFont(QFont("Arial", 16))
        header_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {card_color};")
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {card_color};")
        layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 10))
            subtitle_label.setStyleSheet("color: #64748b;")
            layout.addWidget(subtitle_label)

    def update_value(self, value: str):
        """Update the displayed value"""
        self.value_label.setText(value)

class PlatformReportsWidget(QWidget):
    """Dedicated widget for Zomato and Swiggy platform reports"""

    # Signals
    data_imported = Signal(str, dict)  # platform, data
    report_generated = Signal(str)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)

        # Initialize platform data
        if 'platform_reports' not in self.data:
            self.data['platform_reports'] = {
                'zomato': pd.DataFrame(),
                'swiggy': pd.DataFrame(),
                'combined': pd.DataFrame()
            }

        self.setup_ui()
        self.load_platform_data()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header with import buttons
        self.create_header_section(layout)

        # Platform metrics overview
        self.create_metrics_overview(layout)

        # Main content tabs
        self.create_content_tabs(layout)

    def create_header_section(self, parent_layout):
        """Create header with title and import buttons"""
        header_layout = QHBoxLayout()

        # Title with platform icons
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("🍕 Platform Reports 🍔")
        title_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #0f172a;")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Zomato & Swiggy Analytics Dashboard")
        subtitle_label.setStyleSheet("font-size: 14px; color: #64748b; margin-left: 16px;")
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(title_container)
        header_layout.addStretch()

        # Import buttons
        import_buttons_layout = QHBoxLayout()

        # Zomato import button
        zomato_import_btn = QPushButton("📊 Import Zomato Report")
        zomato_import_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #dc2626, stop:1 #b91c1c);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #b91c1c, stop:1 #991b1b);
                transform: translateY(-1px);
            }
        """)
        zomato_import_btn.clicked.connect(self.import_zomato_report)
        import_buttons_layout.addWidget(zomato_import_btn)

        # Swiggy import button
        swiggy_import_btn = QPushButton("🍔 Import Swiggy Report")
        swiggy_import_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f97316, stop:1 #ea580c);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ea580c, stop:1 #c2410c);
                transform: translateY(-1px);
            }
        """)
        swiggy_import_btn.clicked.connect(self.import_swiggy_report)
        import_buttons_layout.addWidget(swiggy_import_btn)

        # Export combined report button
        export_btn = QPushButton("📤 Export Combined Report")
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #059669, stop:1 #047857);
                transform: translateY(-1px);
            }
        """)
        export_btn.clicked.connect(self.export_combined_report)
        import_buttons_layout.addWidget(export_btn)

        header_layout.addLayout(import_buttons_layout)
        parent_layout.addLayout(header_layout)

    def create_metrics_overview(self, parent_layout):
        """Create platform metrics overview cards"""
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("background: transparent; border: none;")

        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setSpacing(16)

        # Initialize metric cards
        self.zomato_revenue_card = PlatformMetricsCard("Zomato", "Zomato Revenue", "₹0", "Today")
        self.swiggy_revenue_card = PlatformMetricsCard("Swiggy", "Swiggy Revenue", "₹0", "Today")
        self.total_revenue_card = PlatformMetricsCard("Combined", "Total Revenue", "₹0", "Combined")
        self.commission_card = PlatformMetricsCard("Commission", "Total Commission", "₹0", "Platform Fees")

        # Zomato metrics
        self.zomato_orders_card = PlatformMetricsCard("Zomato", "Zomato Orders", "0", "Today")
        self.swiggy_orders_card = PlatformMetricsCard("Swiggy", "Swiggy Orders", "0", "Today")

        # Add to grid (3 columns, 2 rows)
        metrics_layout.addWidget(self.zomato_revenue_card, 0, 0)
        metrics_layout.addWidget(self.swiggy_revenue_card, 0, 1)
        metrics_layout.addWidget(self.total_revenue_card, 0, 2)

        metrics_layout.addWidget(self.zomato_orders_card, 1, 0)
        metrics_layout.addWidget(self.swiggy_orders_card, 1, 1)
        metrics_layout.addWidget(self.commission_card, 1, 2)

        parent_layout.addWidget(metrics_frame)

    def create_content_tabs(self, parent_layout):
        """Create tabbed interface for different platform views"""
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
                font-weight: 600;
            }
        """)

        # Zomato Reports Tab
        self.create_zomato_tab()

        # Swiggy Reports Tab
        self.create_swiggy_tab()

        # Combined Analytics Tab
        self.create_combined_analytics_tab()

        # Commission Analysis Tab
        self.create_commission_analysis_tab()

        parent_layout.addWidget(self.tabs)

    def create_zomato_tab(self):
        """Create Zomato-specific reports tab"""
        zomato_widget = QWidget()
        layout = QVBoxLayout(zomato_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Zomato header
        header_layout = QHBoxLayout()

        zomato_title = QLabel("🍕 Zomato Reports & Analytics")
        zomato_title.setFont(QFont("Arial", 18, QFont.Bold))
        zomato_title.setStyleSheet("color: #dc2626;")
        header_layout.addWidget(zomato_title)

        header_layout.addStretch()

        # Date filter for Zomato
        self.zomato_period_combo = QComboBox()
        self.zomato_period_combo.addItems(["Today", "This Week", "This Month", "This Year", "All Time"])
        self.zomato_period_combo.currentTextChanged.connect(self.update_zomato_data)
        header_layout.addWidget(QLabel("Period:"))
        header_layout.addWidget(self.zomato_period_combo)

        layout.addLayout(header_layout)

        # Zomato data table
        self.zomato_table = QTableWidget()
        self.zomato_table.setColumnCount(9)
        self.zomato_table.setHorizontalHeaderLabels([
            "Date", "Order ID", "Customer", "Items", "Subtotal",
            "Commission Rate", "Commission", "Delivery Fee", "Net Amount"
        ])

        # Apply responsive table functionality
        try:
            from modules.responsive_table_utils import make_table_responsive

            column_priorities = {
                0: 2,   # Date - high priority
                1: 1,   # Order ID - highest priority
                2: 3,   # Customer - medium priority
                3: 2,   # Items - high priority
                4: 3,   # Subtotal - medium priority
                5: 4,   # Commission Rate - low priority
                6: 2,   # Commission - high priority
                7: 5,   # Delivery Fee - lowest priority
                8: 2    # Net Amount - high priority
            }

            column_config = {
                'priorities': column_priorities,
                'stretch_columns': [1, 3, 6, 8]  # Order ID, Items, Commission, Net Amount
            }

            make_table_responsive(self.zomato_table, column_config)

        except ImportError:
            self.zomato_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.zomato_table)

        self.tabs.addTab(zomato_widget, "🍕 Zomato Reports")

    def create_swiggy_tab(self):
        """Create Swiggy-specific reports tab"""
        swiggy_widget = QWidget()
        layout = QVBoxLayout(swiggy_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Swiggy header
        header_layout = QHBoxLayout()

        swiggy_title = QLabel("🍔 Swiggy Reports & Analytics")
        swiggy_title.setFont(QFont("Arial", 18, QFont.Bold))
        swiggy_title.setStyleSheet("color: #f97316;")
        header_layout.addWidget(swiggy_title)

        header_layout.addStretch()

        # Date filter for Swiggy
        self.swiggy_period_combo = QComboBox()
        self.swiggy_period_combo.addItems(["Today", "This Week", "This Month", "This Year", "All Time"])
        self.swiggy_period_combo.currentTextChanged.connect(self.update_swiggy_data)
        header_layout.addWidget(QLabel("Period:"))
        header_layout.addWidget(self.swiggy_period_combo)

        layout.addLayout(header_layout)

        # Swiggy data table
        self.swiggy_table = QTableWidget()
        self.swiggy_table.setColumnCount(9)
        self.swiggy_table.setHorizontalHeaderLabels([
            "Date", "Order ID", "Customer", "Items", "Subtotal",
            "Commission Rate", "Commission", "Delivery Fee", "Net Amount"
        ])

        # Apply responsive table functionality
        try:
            from modules.responsive_table_utils import make_table_responsive

            column_priorities = {
                0: 2,   # Date - high priority
                1: 1,   # Order ID - highest priority
                2: 3,   # Customer - medium priority
                3: 2,   # Items - high priority
                4: 3,   # Subtotal - medium priority
                5: 4,   # Commission Rate - low priority
                6: 2,   # Commission - high priority
                7: 5,   # Delivery Fee - lowest priority
                8: 2    # Net Amount - high priority
            }

            column_config = {
                'priorities': column_priorities,
                'stretch_columns': [1, 3, 6, 8]  # Order ID, Items, Commission, Net Amount
            }

            make_table_responsive(self.swiggy_table, column_config)

        except ImportError:
            self.swiggy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.swiggy_table)

        self.tabs.addTab(swiggy_widget, "🍔 Swiggy Reports")

    def create_combined_analytics_tab(self):
        """Create combined analytics tab"""
        combined_widget = QWidget()
        layout = QVBoxLayout(combined_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Combined analytics header
        header_label = QLabel("📊 Combined Platform Analytics")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setStyleSheet("color: #10b981;")
        layout.addWidget(header_label)

        # Platform comparison charts
        if MATPLOTLIB_AVAILABLE:
            self.create_comparison_charts(layout)
        else:
            # Fallback comparison table
            self.create_comparison_table(layout)

        self.tabs.addTab(combined_widget, "📊 Combined Analytics")

    def create_commission_analysis_tab(self):
        """Create commission analysis tab"""
        commission_widget = QWidget()
        layout = QVBoxLayout(commission_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Commission analysis header
        header_label = QLabel("💰 Commission Analysis")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setStyleSheet("color: #ef4444;")
        layout.addWidget(header_label)

        # Commission breakdown table
        self.commission_table = QTableWidget()
        self.commission_table.setColumnCount(7)
        self.commission_table.setHorizontalHeaderLabels([
            "Platform", "Orders", "Gross Revenue", "Commission Rate",
            "Commission Amount", "Net Revenue", "Profit Margin"
        ])
        self.commission_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.commission_table)

        self.tabs.addTab(commission_widget, "💰 Commission Analysis")

    def create_comparison_charts(self, layout):
        """Create platform comparison charts"""
        try:
            # Create matplotlib figure
            fig = Figure(figsize=(12, 8))
            canvas = FigureCanvas(fig)

            # Revenue comparison chart
            ax1 = fig.add_subplot(221)
            platforms = ['Zomato', 'Swiggy']
            revenues = [50000, 45000]  # Sample data - replace with actual
            colors = ['#dc2626', '#f97316']

            ax1.bar(platforms, revenues, color=colors)
            ax1.set_title('Revenue Comparison')
            ax1.set_ylabel('Revenue (₹)')

            # Orders comparison chart
            ax2 = fig.add_subplot(222)
            orders = [150, 140]  # Sample data - replace with actual

            ax2.bar(platforms, orders, color=colors)
            ax2.set_title('Orders Comparison')
            ax2.set_ylabel('Number of Orders')

            # Commission comparison chart
            ax3 = fig.add_subplot(223)
            commissions = [5000, 4500]  # Sample data - replace with actual

            ax3.bar(platforms, commissions, color=colors)
            ax3.set_title('Commission Comparison')
            ax3.set_ylabel('Commission (₹)')

            # Trend chart
            ax4 = fig.add_subplot(224)
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            zomato_trend = [8000, 9000, 7500, 8500, 9500, 12000, 11000]
            swiggy_trend = [7500, 8500, 7000, 8000, 9000, 11500, 10500]

            ax4.plot(days, zomato_trend, color='#dc2626', marker='o', label='Zomato')
            ax4.plot(days, swiggy_trend, color='#f97316', marker='s', label='Swiggy')
            ax4.set_title('Weekly Revenue Trend')
            ax4.set_ylabel('Revenue (₹)')
            ax4.legend()

            plt.tight_layout()
            layout.addWidget(canvas)

        except Exception as e:
            self.logger.error(f"Error creating comparison charts: {e}")
            self.create_comparison_table(layout)

    def create_comparison_table(self, layout):
        """Create platform comparison table as fallback"""
        comparison_table = QTableWidget()
        comparison_table.setColumnCount(6)
        comparison_table.setHorizontalHeaderLabels([
            "Platform", "Orders", "Revenue", "Avg Order Value", "Commission", "Net Revenue"
        ])
        comparison_table.setRowCount(3)

        # Sample data
        platforms_data = [
            ["Zomato", "150", "₹50,000", "₹333", "₹5,000", "₹45,000"],
            ["Swiggy", "140", "₹45,000", "₹321", "₹4,500", "₹40,500"],
            ["Total", "290", "₹95,000", "₹328", "₹9,500", "₹85,500"]
        ]

        for row, data in enumerate(platforms_data):
            for col, value in enumerate(data):
                comparison_table.setItem(row, col, QTableWidgetItem(value))

        comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(comparison_table)

    def import_zomato_report(self):
        """Import Zomato report from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Zomato Report", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            try:
                # Load the file
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    QMessageBox.warning(self, "Warning", "Unsupported file format")
                    return

                # Process Zomato data
                processed_data = self.process_zomato_data(df)

                # Save to platform reports
                self.data['platform_reports']['zomato'] = processed_data

                # Update UI
                self.update_zomato_data()
                self.update_metrics()

                # Emit signal
                self.data_imported.emit('Zomato', processed_data.to_dict())

                QMessageBox.information(
                    self, "Success",
                    f"Zomato report imported successfully!\n{len(processed_data)} orders processed."
                )

            except Exception as e:
                self.logger.error(f"Error importing Zomato report: {e}")
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to import Zomato report:\n{str(e)}"
                )

    def import_swiggy_report(self):
        """Import Swiggy report from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Swiggy Report", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            try:
                # Load the file
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    QMessageBox.warning(self, "Warning", "Unsupported file format")
                    return

                # Process Swiggy data
                processed_data = self.process_swiggy_data(df)

                # Save to platform reports
                self.data['platform_reports']['swiggy'] = processed_data

                # Update UI
                self.update_swiggy_data()
                self.update_metrics()

                # Emit signal
                self.data_imported.emit('Swiggy', processed_data.to_dict())

                QMessageBox.information(
                    self, "Success",
                    f"Swiggy report imported successfully!\n{len(processed_data)} orders processed."
                )

            except Exception as e:
                self.logger.error(f"Error importing Swiggy report: {e}")
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to import Swiggy report:\n{str(e)}"
                )

    def process_zomato_data(self, df):
        """Process Zomato report data"""
        try:
            # This is a placeholder - implement actual Zomato data processing
            # based on the actual format of Zomato reports

            processed_data = []
            for _, row in df.iterrows():
                order_data = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'order_id': f"ZOM-{len(processed_data)+1:06d}",
                    'customer': 'Zomato Customer',
                    'items': 'Various Items',
                    'subtotal': 500.0,
                    'commission_rate': 18.0,
                    'commission': 90.0,
                    'delivery_fee': 30.0,
                    'net_amount': 410.0
                }
                processed_data.append(order_data)

            return pd.DataFrame(processed_data)

        except Exception as e:
            self.logger.error(f"Error processing Zomato data: {e}")
            raise

    def process_swiggy_data(self, df):
        """Process Swiggy report data"""
        try:
            # This is a placeholder - implement actual Swiggy data processing
            # based on the actual format of Swiggy reports

            processed_data = []
            for _, row in df.iterrows():
                order_data = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'order_id': f"SWG-{len(processed_data)+1:06d}",
                    'customer': 'Swiggy Customer',
                    'items': 'Various Items',
                    'subtotal': 450.0,
                    'commission_rate': 20.0,
                    'commission': 90.0,
                    'delivery_fee': 25.0,
                    'net_amount': 360.0
                }
                processed_data.append(order_data)

            return pd.DataFrame(processed_data)

        except Exception as e:
            self.logger.error(f"Error processing Swiggy data: {e}")
            raise

    def export_combined_report(self):
        """Export combined platform report"""
        try:
            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Combined Report",
                f"platform_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )

            if file_path:
                # Combine data from both platforms
                combined_data = self.get_combined_data()

                if file_path.endswith('.xlsx'):
                    with pd.ExcelWriter(file_path) as writer:
                        if not self.data['platform_reports']['zomato'].empty:
                            self.data['platform_reports']['zomato'].to_excel(
                                writer, sheet_name='Zomato', index=False
                            )
                        if not self.data['platform_reports']['swiggy'].empty:
                            self.data['platform_reports']['swiggy'].to_excel(
                                writer, sheet_name='Swiggy', index=False
                            )
                        if not combined_data.empty:
                            combined_data.to_excel(
                                writer, sheet_name='Combined', index=False
                            )
                else:
                    combined_data.to_csv(file_path, index=False)

                QMessageBox.information(
                    self, "Success",
                    f"Combined report exported successfully to:\n{file_path}"
                )

        except Exception as e:
            self.logger.error(f"Error exporting combined report: {e}")
            QMessageBox.critical(
                self, "Error",
                f"Failed to export combined report:\n{str(e)}"
            )

    def get_combined_data(self):
        """Get combined data from both platforms"""
        try:
            combined_list = []

            # Add Zomato data
            if not self.data['platform_reports']['zomato'].empty:
                zomato_data = self.data['platform_reports']['zomato'].copy()
                zomato_data['platform'] = 'Zomato'
                combined_list.append(zomato_data)

            # Add Swiggy data
            if not self.data['platform_reports']['swiggy'].empty:
                swiggy_data = self.data['platform_reports']['swiggy'].copy()
                swiggy_data['platform'] = 'Swiggy'
                combined_list.append(swiggy_data)

            if combined_list:
                combined_df = pd.concat(combined_list, ignore_index=True)
                return combined_df
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error getting combined data: {e}")
            return pd.DataFrame()

    def update_zomato_data(self):
        """Update Zomato data display"""
        try:
            if self.data['platform_reports']['zomato'].empty:
                self.zomato_table.setRowCount(0)
                return

            df = self.data['platform_reports']['zomato']
            period = self.zomato_period_combo.currentText()
            filtered_df = self.filter_by_period(df, period)

            self.populate_table(self.zomato_table, filtered_df)

        except Exception as e:
            self.logger.error(f"Error updating Zomato data: {e}")

    def update_swiggy_data(self):
        """Update Swiggy data display"""
        try:
            if self.data['platform_reports']['swiggy'].empty:
                self.swiggy_table.setRowCount(0)
                return

            df = self.data['platform_reports']['swiggy']
            period = self.swiggy_period_combo.currentText()
            filtered_df = self.filter_by_period(df, period)

            self.populate_table(self.swiggy_table, filtered_df)

        except Exception as e:
            self.logger.error(f"Error updating Swiggy data: {e}")

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

    def populate_table(self, table, df):
        """Populate table with dataframe data"""
        try:
            table.setRowCount(len(df))

            for row, (_, data) in enumerate(df.iterrows()):
                table.setItem(row, 0, QTableWidgetItem(str(data.get('date', ''))))
                table.setItem(row, 1, QTableWidgetItem(str(data.get('order_id', ''))))
                table.setItem(row, 2, QTableWidgetItem(str(data.get('customer', ''))))
                table.setItem(row, 3, QTableWidgetItem(str(data.get('items', ''))))
                table.setItem(row, 4, QTableWidgetItem(f"₹{data.get('subtotal', 0):.2f}"))
                table.setItem(row, 5, QTableWidgetItem(f"{data.get('commission_rate', 0):.1f}%"))
                table.setItem(row, 6, QTableWidgetItem(f"₹{data.get('commission', 0):.2f}"))
                table.setItem(row, 7, QTableWidgetItem(f"₹{data.get('delivery_fee', 0):.2f}"))
                table.setItem(row, 8, QTableWidgetItem(f"₹{data.get('net_amount', 0):.2f}"))

        except Exception as e:
            self.logger.error(f"Error populating table: {e}")

    def update_metrics(self):
        """Update platform metrics cards"""
        try:
            # Calculate Zomato metrics
            zomato_df = self.data['platform_reports']['zomato']
            if not zomato_df.empty:
                zomato_revenue = zomato_df['net_amount'].sum()
                zomato_orders = len(zomato_df)
            else:
                zomato_revenue = 0
                zomato_orders = 0

            # Calculate Swiggy metrics
            swiggy_df = self.data['platform_reports']['swiggy']
            if not swiggy_df.empty:
                swiggy_revenue = swiggy_df['net_amount'].sum()
                swiggy_orders = len(swiggy_df)
            else:
                swiggy_revenue = 0
                swiggy_orders = 0

            # Calculate combined metrics
            total_revenue = zomato_revenue + swiggy_revenue
            total_commission = 0

            if not zomato_df.empty:
                total_commission += zomato_df['commission'].sum()
            if not swiggy_df.empty:
                total_commission += swiggy_df['commission'].sum()

            # Update cards
            self.zomato_revenue_card.update_value(f"₹{zomato_revenue:.2f}")
            self.swiggy_revenue_card.update_value(f"₹{swiggy_revenue:.2f}")
            self.total_revenue_card.update_value(f"₹{total_revenue:.2f}")
            self.commission_card.update_value(f"₹{total_commission:.2f}")

            self.zomato_orders_card.update_value(str(zomato_orders))
            self.swiggy_orders_card.update_value(str(swiggy_orders))

        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def load_platform_data(self):
        """Load existing platform data"""
        try:
            # Load from CSV files if they exist
            import os

            zomato_file = 'data/zomato_reports.csv'
            swiggy_file = 'data/swiggy_reports.csv'

            if os.path.exists(zomato_file):
                self.data['platform_reports']['zomato'] = pd.read_csv(zomato_file)

            if os.path.exists(swiggy_file):
                self.data['platform_reports']['swiggy'] = pd.read_csv(swiggy_file)

            # Update displays
            self.update_zomato_data()
            self.update_swiggy_data()
            self.update_metrics()

        except Exception as e:
            self.logger.error(f"Error loading platform data: {e}")

    def refresh_data(self):
        """Refresh all platform data"""
        try:
            self.update_zomato_data()
            self.update_swiggy_data()
            self.update_metrics()

        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")

    def save_platform_data(self):
        """Save platform data to files"""
        try:
            import os
            os.makedirs('data', exist_ok=True)

            # Save Zomato data
            if not self.data['platform_reports']['zomato'].empty:
                self.data['platform_reports']['zomato'].to_csv(
                    'data/zomato_reports.csv', index=False
                )

            # Save Swiggy data
            if not self.data['platform_reports']['swiggy'].empty:
                self.data['platform_reports']['swiggy'].to_csv(
                    'data/swiggy_reports.csv', index=False
                )

        except Exception as e:
            self.logger.error(f"Error saving platform data: {e}")

    def closeEvent(self, event):
        """Handle close event"""
        try:
            # Save data before closing
            self.save_platform_data()

            # Stop timer
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()

            event.accept()

        except Exception as e:
            self.logger.error(f"Error in close event: {e}")
            event.accept()