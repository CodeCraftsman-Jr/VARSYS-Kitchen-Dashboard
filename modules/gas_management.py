#!/usr/bin/env python3
"""
Gas Management Module

Comprehensive gas tracking system with order management, purchase history,
and alert system for 15kg LPG cylinders.
"""

import os
import sys
import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox,
    QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox,
    QFormLayout, QMessageBox, QHeaderView, QFrame, QGridLayout,
    QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, QDate, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap

class GasManagementWidget(QWidget):
    """Main gas management widget with tabs for tracking, orders, and alerts"""
    
    # Signal for gas alerts
    gas_alert_triggered = Signal(str, str)  # alert_type, message
    
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data if data else {}
        self.logger = logging.getLogger(__name__)
        
        # Load gas configuration
        self.gas_config = self.load_gas_config()
        
        # Initialize data structures
        self.init_gas_data()
        
        # Setup UI
        self.setup_ui()
        
        # Setup alert timer
        self.setup_alert_system()
        
        # Load existing data
        self.load_gas_data()
        
        self.logger.info("Gas Management module initialized")
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("🔥 Gas Management System")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1f2937;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f3f4f6, stop:1 #e5e7eb);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Alert status bar
        self.create_alert_status_bar(layout)
        
        # Create tab widget
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
        
        # Create tabs
        self.create_current_status_tab()
        self.create_order_management_tab()
        self.create_purchase_history_tab()
        self.create_usage_analytics_tab()
        self.create_settings_tab()
        
        layout.addWidget(self.tabs)
    
    def create_alert_status_bar(self, parent_layout):
        """Create alert status bar at the top"""
        self.alert_frame = QFrame()
        self.alert_frame.setStyleSheet("""
            QFrame {
                background-color: #10b981;
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0;
            }
        """)
        
        alert_layout = QHBoxLayout(self.alert_frame)
        alert_layout.setContentsMargins(15, 8, 15, 8)
        
        self.alert_icon = QLabel("✅")
        self.alert_icon.setFont(QFont("Arial", 14))
        alert_layout.addWidget(self.alert_icon)
        
        self.alert_message = QLabel("Gas levels are normal")
        self.alert_message.setFont(QFont("Arial", 12, QFont.Bold))
        self.alert_message.setStyleSheet("color: white;")
        alert_layout.addWidget(self.alert_message)
        
        alert_layout.addStretch()
        
        self.alert_action_btn = QPushButton("Order Gas")
        self.alert_action_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #10b981;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.alert_action_btn.clicked.connect(self.quick_order_gas)
        self.alert_action_btn.hide()  # Hidden by default
        alert_layout.addWidget(self.alert_action_btn)
        
        parent_layout.addWidget(self.alert_frame)
    
    def create_current_status_tab(self):
        """Create current gas status tab"""
        self.status_tab = QWidget()
        layout = QVBoxLayout(self.status_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Current cylinder status cards
        self.create_status_cards(layout)
        
        # Gas usage chart placeholder
        usage_group = QGroupBox("Daily Gas Usage Tracking")
        usage_layout = QVBoxLayout(usage_group)
        
        # Usage input section
        usage_input_layout = QHBoxLayout()

        usage_input_layout.addWidget(QLabel("Today's Usage (kg):"))
        self.daily_usage_input = QDoubleSpinBox()
        self.daily_usage_input.setRange(0.0, 5.0)
        self.daily_usage_input.setSingleStep(0.1)
        self.daily_usage_input.setDecimals(2)
        usage_input_layout.addWidget(self.daily_usage_input)

        update_usage_btn = QPushButton("Update Usage")
        update_usage_btn.clicked.connect(self.update_daily_usage)
        usage_input_layout.addWidget(update_usage_btn)

        # Add manual home usage button
        home_usage_btn = QPushButton("Add Home Usage")
        home_usage_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        home_usage_btn.clicked.connect(self.add_home_usage)
        usage_input_layout.addWidget(home_usage_btn)

        usage_input_layout.addStretch()
        usage_layout.addLayout(usage_input_layout)
        
        # Usage history table
        self.usage_table = QTableWidget()
        self.usage_table.setColumnCount(4)
        self.usage_table.setHorizontalHeaderLabels([
            "Date", "Usage (kg)", "Remaining (kg)", "Days Left"
        ])
        self.usage_table.horizontalHeader().setStretchLastSection(True)
        usage_layout.addWidget(self.usage_table)
        
        layout.addWidget(usage_group)
        
        self.tabs.addTab(self.status_tab, "🔥 Current Status")
    
    def create_status_cards(self, parent_layout):
        """Create status overview cards"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # Current cylinder card
        self.current_cylinder_card = self.create_status_card(
            "Current Cylinder", "15.0 kg", "100% Full", "#10b981"
        )
        cards_layout.addWidget(self.current_cylinder_card, 0, 0)
        
        # Days remaining card
        self.days_remaining_card = self.create_status_card(
            "Days Remaining", "50 days", "Based on usage", "#3b82f6"
        )
        cards_layout.addWidget(self.days_remaining_card, 0, 1)
        
        # Monthly cost card
        self.monthly_cost_card = self.create_status_card(
            "Monthly Cost", "₹910", "Current month", "#8b5cf6"
        )
        cards_layout.addWidget(self.monthly_cost_card, 0, 2)
        
        # Next order card
        self.next_order_card = self.create_status_card(
            "Next Order Due", "3 days", "Auto-reminder", "#f59e0b"
        )
        cards_layout.addWidget(self.next_order_card, 0, 3)
        
        parent_layout.addWidget(cards_frame)
    
    def create_status_card(self, title, value, subtitle, color):
        """Create a status card widget"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet("color: #6b7280;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Arial", 9))
        subtitle_label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(subtitle_label)
        
        return card

    def create_order_management_tab(self):
        """Create order management tab"""
        self.order_tab = QWidget()
        layout = QVBoxLayout(self.order_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # New order section - Make it collapsible
        order_group = QGroupBox("Place New Gas Order")
        order_group.setCheckable(True)
        order_group.setChecked(False)  # Start collapsed to save space
        order_layout = QFormLayout(order_group)

        self.supplier_combo = QComboBox()
        self.supplier_combo.addItems(["Indian Gas Agency", "Bharat Gas", "HP Gas", "Indane Gas"])
        order_layout.addRow("Supplier:", self.supplier_combo)

        self.cylinder_weight_spin = QSpinBox()
        self.cylinder_weight_spin.setValue(15)
        self.cylinder_weight_spin.setRange(5, 50)
        order_layout.addRow("Cylinder Weight (kg):", self.cylinder_weight_spin)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setValue(1)
        self.quantity_spin.setRange(1, 10)
        order_layout.addRow("Quantity:", self.quantity_spin)

        self.cost_per_cylinder_spin = QDoubleSpinBox()
        self.cost_per_cylinder_spin.setValue(910.0)
        self.cost_per_cylinder_spin.setRange(500.0, 2000.0)
        order_layout.addRow("Cost per Cylinder (₹):", self.cost_per_cylinder_spin)

        self.delivery_charges_spin = QDoubleSpinBox()
        self.delivery_charges_spin.setValue(0.0)
        self.delivery_charges_spin.setRange(0.0, 500.0)
        order_layout.addRow("Delivery Charges (₹):", self.delivery_charges_spin)

        self.expected_delivery_date = QDateEdit()
        self.expected_delivery_date.setDate(QDate.currentDate().addDays(1))
        order_layout.addRow("Expected Delivery:", self.expected_delivery_date)

        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "UPI", "Card", "Bank Transfer"])
        order_layout.addRow("Payment Method:", self.payment_method_combo)

        self.order_notes = QTextEdit()
        self.order_notes.setMaximumHeight(60)
        order_layout.addRow("Notes:", self.order_notes)

        # Order button
        place_order_btn = QPushButton("Place Order")
        place_order_btn.setStyleSheet("""
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
        place_order_btn.clicked.connect(self.place_gas_order)
        order_layout.addRow("", place_order_btn)

        layout.addWidget(order_group)

        # Current orders table
        orders_group = QGroupBox("Current Orders")
        orders_layout = QVBoxLayout(orders_group)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(9)
        self.orders_table.setHorizontalHeaderLabels([
            "Order ID", "Date", "Supplier", "Quantity", "Total Cost",
            "Expected Delivery", "Status", "Payment", "Actions"
        ])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        orders_layout.addWidget(self.orders_table)

        layout.addWidget(orders_group)

        self.tabs.addTab(self.order_tab, "📋 Order Management")

    def create_purchase_history_tab(self):
        """Create purchase history tab"""
        self.history_tab = QWidget()
        layout = QVBoxLayout(self.history_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Filter section
        filter_group = QGroupBox("Filter Purchase History")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-6))
        filter_layout.addWidget(self.from_date)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)

        filter_layout.addWidget(QLabel("Supplier:"))
        self.filter_supplier = QComboBox()
        self.filter_supplier.addItems(["All", "Indian Gas Agency", "Bharat Gas", "HP Gas", "Indane Gas"])
        filter_layout.addWidget(self.filter_supplier)

        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.apply_history_filter)
        filter_layout.addWidget(apply_filter_btn)

        filter_layout.addStretch()
        layout.addWidget(filter_group)

        # Purchase history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Purchase Date", "Supplier", "Cylinder Weight", "Cost",
            "Delivery Charges", "Total", "Payment Method", "Notes"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)

        # Summary section
        summary_group = QGroupBox("Purchase Summary")
        summary_layout = QGridLayout(summary_group)

        self.total_purchases_label = QLabel("Total Purchases: 0")
        summary_layout.addWidget(self.total_purchases_label, 0, 0)

        self.total_cost_label = QLabel("Total Cost: ₹0")
        summary_layout.addWidget(self.total_cost_label, 0, 1)

        self.avg_cost_label = QLabel("Average Cost: ₹0")
        summary_layout.addWidget(self.avg_cost_label, 0, 2)

        layout.addWidget(summary_group)

        self.tabs.addTab(self.history_tab, "📊 Purchase History")

    def create_usage_analytics_tab(self):
        """Create usage analytics tab"""
        self.analytics_tab = QWidget()
        layout = QVBoxLayout(self.analytics_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Analytics cards
        analytics_frame = QFrame()
        analytics_layout = QGridLayout(analytics_frame)

        self.daily_avg_card = self.create_status_card(
            "Daily Average", "0.3 kg", "Last 30 days", "#10b981"
        )
        analytics_layout.addWidget(self.daily_avg_card, 0, 0)

        self.monthly_usage_card = self.create_status_card(
            "Monthly Usage", "9.0 kg", "Current month", "#3b82f6"
        )
        analytics_layout.addWidget(self.monthly_usage_card, 0, 1)

        self.efficiency_card = self.create_status_card(
            "Efficiency", "85%", "vs. standard", "#8b5cf6"
        )
        analytics_layout.addWidget(self.efficiency_card, 0, 2)

        layout.addWidget(analytics_frame)

        # Usage prediction
        prediction_group = QGroupBox("Usage Prediction")
        prediction_layout = QVBoxLayout(prediction_group)

        prediction_text = QLabel("""
        Based on your current usage patterns:
        • Current cylinder will last approximately 45 days
        • Recommended to order new cylinder in 42 days
        • Monthly gas cost: ₹910
        • Annual estimated cost: ₹10,920
        """)
        prediction_text.setStyleSheet("color: #6b7280; line-height: 1.6;")
        prediction_layout.addWidget(prediction_text)

        layout.addWidget(prediction_group)

        # Cost optimization tips
        tips_group = QGroupBox("Cost Optimization Tips")
        tips_layout = QVBoxLayout(tips_group)

        tips_text = QLabel("""
        💡 Tips to reduce gas consumption:
        • Use pressure cooker for faster cooking
        • Keep flame size appropriate for pot size
        • Regular maintenance of gas stove
        • Plan cooking to use residual heat
        • Consider bulk cooking for efficiency
        """)
        tips_text.setStyleSheet("color: #6b7280; line-height: 1.6;")
        tips_layout.addWidget(tips_text)

        layout.addWidget(tips_group)

        self.tabs.addTab(self.analytics_tab, "📈 Usage Analytics")

    def create_settings_tab(self):
        """Create settings tab"""
        self.settings_tab = QWidget()
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Alert settings
        alert_group = QGroupBox("Alert Settings")
        alert_layout = QFormLayout(alert_group)

        self.low_gas_threshold = QSpinBox()
        self.low_gas_threshold.setValue(3)
        self.low_gas_threshold.setRange(1, 10)
        alert_layout.addRow("Low Gas Alert (days):", self.low_gas_threshold)

        self.critical_gas_threshold = QSpinBox()
        self.critical_gas_threshold.setValue(1)
        self.critical_gas_threshold.setRange(1, 5)
        alert_layout.addRow("Critical Gas Alert (days):", self.critical_gas_threshold)

        self.enable_notifications = QCheckBox("Enable Notifications")
        self.enable_notifications.setChecked(True)
        alert_layout.addRow("", self.enable_notifications)

        layout.addWidget(alert_group)

        # Supplier settings
        supplier_group = QGroupBox("Default Supplier Settings")
        supplier_layout = QFormLayout(supplier_group)

        self.default_supplier = QComboBox()
        self.default_supplier.addItems(["Indian Gas Agency", "Bharat Gas", "HP Gas", "Indane Gas"])
        supplier_layout.addRow("Default Supplier:", self.default_supplier)

        self.default_cylinder_cost = QDoubleSpinBox()
        self.default_cylinder_cost.setValue(910.0)
        self.default_cylinder_cost.setRange(500.0, 2000.0)
        supplier_layout.addRow("Default Cylinder Cost (₹):", self.default_cylinder_cost)

        layout.addWidget(supplier_group)

        # Save settings button
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        save_settings_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_settings_btn)

        layout.addStretch()

        self.tabs.addTab(self.settings_tab, "⚙️ Settings")

    def init_gas_data(self):
        """Initialize gas data structures"""
        try:
            # Initialize gas tracking data
            if 'gas_tracking' not in self.data:
                self.data['gas_tracking'] = pd.DataFrame(columns=[
                    'cylinder_id', 'purchase_date', 'supplier', 'cylinder_weight_kg',
                    'cost_inr', 'delivery_charges_inr', 'total_cost_inr', 'installation_date',
                    'current_weight_kg', 'estimated_days_remaining', 'status', 'last_updated', 'notes'
                ])

            # Initialize gas orders data
            if 'gas_orders' not in self.data:
                self.data['gas_orders'] = pd.DataFrame(columns=[
                    'order_id', 'order_date', 'supplier', 'cylinder_weight_kg', 'quantity',
                    'cost_per_cylinder_inr', 'delivery_charges_inr', 'total_cost_inr',
                    'expected_delivery_date', 'actual_delivery_date', 'status',
                    'payment_method', 'payment_status', 'notes'
                ])

            self.logger.info("Gas data structures initialized")

        except Exception as e:
            self.logger.error(f"Error initializing gas data: {e}")

    def load_gas_config(self):
        """Load gas configuration from JSON file"""
        try:
            config_path = os.path.join('data', 'gas_cost_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning("Gas config file not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading gas config: {e}")
            return self.get_default_config()

    def get_default_config(self):
        """Get default gas configuration"""
        return {
            "gas_cost_settings": {
                "gas_consumption_per_hour_kg": 0.3,
                "gas_rate_per_kg_inr": 60.67,
                "minimum_cost_inr": 0.5,
                "use_total_preparation_time": True
            },
            "cylinder_settings": {
                "cylinder_weight_kg": 15,
                "cylinder_cost_inr": 910,
                "cost_per_kg_inr": 60.67,
                "supplier": "Indian Gas Agency"
            },
            "alert_settings": {
                "low_gas_threshold_days": 3,
                "critical_gas_threshold_days": 1,
                "enable_notifications": True
            }
        }

    def load_gas_data(self):
        """Load gas data from CSV files"""
        try:
            # Load gas tracking data
            tracking_path = os.path.join('data', 'gas_tracking.csv')
            if os.path.exists(tracking_path):
                self.data['gas_tracking'] = pd.read_csv(tracking_path, encoding='utf-8')
                self.logger.info("Gas tracking data loaded")

            # Load gas orders data
            orders_path = os.path.join('data', 'gas_orders.csv')
            if os.path.exists(orders_path):
                self.data['gas_orders'] = pd.read_csv(orders_path, encoding='utf-8')
                self.logger.info("Gas orders data loaded")

            # Update UI with loaded data
            self.update_status_display()
            self.populate_orders_table()
            self.populate_history_table()

        except Exception as e:
            self.logger.error(f"Error loading gas data: {e}")

    def save_gas_data(self):
        """Save gas data to CSV files"""
        try:
            # Save gas tracking data
            if 'gas_tracking' in self.data and not self.data['gas_tracking'].empty:
                tracking_path = os.path.join('data', 'gas_tracking.csv')
                self.data['gas_tracking'].to_csv(tracking_path, index=False, encoding='utf-8')

            # Save gas orders data
            if 'gas_orders' in self.data and not self.data['gas_orders'].empty:
                orders_path = os.path.join('data', 'gas_orders.csv')
                self.data['gas_orders'].to_csv(orders_path, index=False, encoding='utf-8')

            self.logger.info("Gas data saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving gas data: {e}")

    def setup_alert_system(self):
        """Setup the alert monitoring system"""
        try:
            # Create timer for periodic checks
            self.alert_timer = QTimer()
            self.alert_timer.timeout.connect(self.check_gas_levels)
            self.alert_timer.start(3600000)  # Check every hour

            # Initial check
            self.check_gas_levels()

            self.logger.info("Alert system initialized")

        except Exception as e:
            self.logger.error(f"Error setting up alert system: {e}")

    def check_gas_levels(self):
        """Check current gas levels and trigger alerts if needed"""
        try:
            if 'gas_tracking' not in self.data or self.data['gas_tracking'].empty:
                return

            # Get current active cylinder
            active_cylinders = self.data['gas_tracking'][
                self.data['gas_tracking']['status'] == 'Active'
            ]

            if active_cylinders.empty:
                self.update_alert_status("warning", "⚠️", "No active gas cylinder found", True)
                return

            current_cylinder = active_cylinders.iloc[-1]  # Get latest active cylinder
            days_remaining = current_cylinder.get('estimated_days_remaining', 0)

            alert_settings = self.gas_config.get('alert_settings', {})
            low_threshold = alert_settings.get('low_gas_threshold_days', 3)
            critical_threshold = alert_settings.get('critical_gas_threshold_days', 1)

            if days_remaining <= critical_threshold:
                self.update_alert_status(
                    "critical", "🚨",
                    f"CRITICAL: Gas will run out in {days_remaining} day(s)!",
                    True
                )
                self.gas_alert_triggered.emit("critical", f"Gas critically low: {days_remaining} days remaining")
            elif days_remaining <= low_threshold:
                self.update_alert_status(
                    "warning", "⚠️",
                    f"Low gas: {days_remaining} days remaining",
                    True
                )
                self.gas_alert_triggered.emit("warning", f"Gas running low: {days_remaining} days remaining")
            else:
                self.update_alert_status(
                    "normal", "✅",
                    f"Gas levels normal: {days_remaining} days remaining",
                    False
                )

        except Exception as e:
            self.logger.error(f"Error checking gas levels: {e}")

    def update_alert_status(self, alert_type, icon, message, show_action):
        """Update the alert status bar"""
        try:
            colors = {
                "normal": "#10b981",
                "warning": "#f59e0b",
                "critical": "#ef4444"
            }

            color = colors.get(alert_type, "#10b981")

            self.alert_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 8px;
                    margin: 5px 0;
                }}
            """)

            self.alert_icon.setText(icon)
            self.alert_message.setText(message)

            if show_action:
                self.alert_action_btn.show()
            else:
                self.alert_action_btn.hide()

        except Exception as e:
            self.logger.error(f"Error updating alert status: {e}")

    def place_gas_order(self):
        """Place a new gas order"""
        try:
            # Get form data
            supplier = self.supplier_combo.currentText()
            cylinder_weight = self.cylinder_weight_spin.value()
            quantity = self.quantity_spin.value()
            cost_per_cylinder = self.cost_per_cylinder_spin.value()
            delivery_charges = self.delivery_charges_spin.value()
            expected_delivery = self.expected_delivery_date.date().toString("yyyy-MM-dd")
            payment_method = self.payment_method_combo.currentText()
            notes = self.order_notes.toPlainText()

            # Calculate total cost
            total_cost = (cost_per_cylinder * quantity) + delivery_charges

            # Generate order ID
            order_id = len(self.data['gas_orders']) + 1

            # Create new order record
            new_order = {
                'order_id': order_id,
                'order_date': datetime.now().strftime('%Y-%m-%d'),
                'supplier': supplier,
                'cylinder_weight_kg': cylinder_weight,
                'quantity': quantity,
                'cost_per_cylinder_inr': cost_per_cylinder,
                'delivery_charges_inr': delivery_charges,
                'total_cost_inr': total_cost,
                'expected_delivery_date': expected_delivery,
                'actual_delivery_date': '',
                'status': 'Ordered',
                'payment_method': payment_method,
                'payment_status': 'Pending',
                'notes': notes
            }

            # Add to dataframe
            self.data['gas_orders'] = pd.concat([
                self.data['gas_orders'],
                pd.DataFrame([new_order])
            ], ignore_index=True)

            # Save data
            self.save_gas_data()

            # Update UI
            self.populate_orders_table()

            # Clear form
            self.clear_order_form()

            # Show success message
            QMessageBox.information(self, "Order Placed",
                f"Gas order #{order_id} placed successfully!\nTotal cost: ₹{total_cost}")

            self.logger.info(f"Gas order placed: {order_id}")

        except Exception as e:
            self.logger.error(f"Error placing gas order: {e}")
            QMessageBox.critical(self, "Error", f"Failed to place order: {str(e)}")

    def quick_order_gas(self):
        """Quick order gas from alert"""
        try:
            # Switch to order tab
            self.tabs.setCurrentIndex(1)

            # Pre-fill with default values
            cylinder_settings = self.gas_config.get('cylinder_settings', {})
            self.cost_per_cylinder_spin.setValue(cylinder_settings.get('cylinder_cost_inr', 910))

            # Show message
            QMessageBox.information(self, "Quick Order",
                "Switched to Order Management tab. Please review and place your order.")

        except Exception as e:
            self.logger.error(f"Error in quick order: {e}")

    def update_daily_usage(self):
        """Update daily gas usage"""
        try:
            usage = self.daily_usage_input.value()
            if usage <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid usage amount.")
                return

            # Update current cylinder data
            if 'gas_tracking' in self.data and not self.data['gas_tracking'].empty:
                active_cylinders = self.data['gas_tracking'][
                    self.data['gas_tracking']['status'] == 'Active'
                ]

                if not active_cylinders.empty:
                    # Update the latest active cylinder
                    latest_idx = active_cylinders.index[-1]
                    current_weight = self.data['gas_tracking'].loc[latest_idx, 'current_weight_kg']
                    new_weight = max(0, current_weight - usage)

                    self.data['gas_tracking'].loc[latest_idx, 'current_weight_kg'] = new_weight
                    self.data['gas_tracking'].loc[latest_idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Calculate estimated days remaining
                    if usage > 0:
                        days_remaining = int(new_weight / usage)
                        self.data['gas_tracking'].loc[latest_idx, 'estimated_days_remaining'] = days_remaining

                    # Save data
                    self.save_gas_data()

                    # Update UI
                    self.update_status_display()
                    self.check_gas_levels()

                    # Clear input
                    self.daily_usage_input.setValue(0.0)

                    QMessageBox.information(self, "Usage Updated",
                        f"Daily usage of {usage} kg recorded successfully!")

        except Exception as e:
            self.logger.error(f"Error updating daily usage: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update usage: {str(e)}")

    def populate_orders_table(self):
        """Populate the orders table"""
        try:
            if 'gas_orders' not in self.data or self.data['gas_orders'].empty:
                self.orders_table.setRowCount(0)
                return

            orders_df = self.data['gas_orders']
            self.orders_table.setRowCount(len(orders_df))

            for row, (_, order) in enumerate(orders_df.iterrows()):
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.get('order_id', ''))))
                self.orders_table.setItem(row, 1, QTableWidgetItem(str(order.get('order_date', ''))))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(order.get('supplier', ''))))
                self.orders_table.setItem(row, 3, QTableWidgetItem(str(order.get('quantity', ''))))
                self.orders_table.setItem(row, 4, QTableWidgetItem(f"₹{order.get('total_cost_inr', 0):.2f}"))
                self.orders_table.setItem(row, 5, QTableWidgetItem(str(order.get('expected_delivery_date', ''))))
                self.orders_table.setItem(row, 6, QTableWidgetItem(str(order.get('status', ''))))
                self.orders_table.setItem(row, 7, QTableWidgetItem(str(order.get('payment_status', ''))))

                # Action button
                action_btn = QPushButton("Mark Delivered")
                action_btn.clicked.connect(lambda checked, r=row: self.mark_order_delivered(r))
                self.orders_table.setCellWidget(row, 8, action_btn)

        except Exception as e:
            self.logger.error(f"Error populating orders table: {e}")

    def populate_history_table(self):
        """Populate the purchase history table"""
        try:
            if 'gas_tracking' not in self.data or self.data['gas_tracking'].empty:
                self.history_table.setRowCount(0)
                return

            tracking_df = self.data['gas_tracking']
            self.history_table.setRowCount(len(tracking_df))

            total_cost = 0
            for row, (_, record) in enumerate(tracking_df.iterrows()):
                self.history_table.setItem(row, 0, QTableWidgetItem(str(record.get('purchase_date', ''))))
                self.history_table.setItem(row, 1, QTableWidgetItem(str(record.get('supplier', ''))))
                self.history_table.setItem(row, 2, QTableWidgetItem(f"{record.get('cylinder_weight_kg', 0)} kg"))
                self.history_table.setItem(row, 3, QTableWidgetItem(f"₹{record.get('cost_inr', 0):.2f}"))
                self.history_table.setItem(row, 4, QTableWidgetItem(f"₹{record.get('delivery_charges_inr', 0):.2f}"))
                self.history_table.setItem(row, 5, QTableWidgetItem(f"₹{record.get('total_cost_inr', 0):.2f}"))
                self.history_table.setItem(row, 6, QTableWidgetItem("Cash"))  # Default for now
                self.history_table.setItem(row, 7, QTableWidgetItem(str(record.get('notes', ''))))

                total_cost += record.get('total_cost_inr', 0)

            # Update summary
            self.update_purchase_summary(len(tracking_df), total_cost)

        except Exception as e:
            self.logger.error(f"Error populating history table: {e}")

    def update_status_display(self):
        """Update the status display cards"""
        try:
            if 'gas_tracking' not in self.data or self.data['gas_tracking'].empty:
                return

            # Get current active cylinder
            active_cylinders = self.data['gas_tracking'][
                self.data['gas_tracking']['status'] == 'Active'
            ]

            if not active_cylinders.empty:
                current_cylinder = active_cylinders.iloc[-1]
                current_weight = current_cylinder.get('current_weight_kg', 15)
                total_weight = current_cylinder.get('cylinder_weight_kg', 15)
                days_remaining = current_cylinder.get('estimated_days_remaining', 50)

                # Update cards (this would need to update the actual card widgets)
                # For now, just log the values
                self.logger.info(f"Status update - Weight: {current_weight}kg, Days: {days_remaining}")

        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")

    def clear_order_form(self):
        """Clear the order form"""
        try:
            self.quantity_spin.setValue(1)
            self.delivery_charges_spin.setValue(0.0)
            self.expected_delivery_date.setDate(QDate.currentDate().addDays(1))
            self.order_notes.clear()

        except Exception as e:
            self.logger.error(f"Error clearing order form: {e}")

    def mark_order_delivered(self, row):
        """Mark an order as delivered"""
        try:
            if 'gas_orders' not in self.data or row >= len(self.data['gas_orders']):
                return

            # Update order status
            self.data['gas_orders'].loc[row, 'status'] = 'Delivered'
            self.data['gas_orders'].loc[row, 'actual_delivery_date'] = datetime.now().strftime('%Y-%m-%d')
            self.data['gas_orders'].loc[row, 'payment_status'] = 'Paid'

            # Create tracking record
            order = self.data['gas_orders'].iloc[row]
            new_tracking = {
                'cylinder_id': len(self.data['gas_tracking']) + 1,
                'purchase_date': order.get('actual_delivery_date'),
                'supplier': order.get('supplier'),
                'cylinder_weight_kg': order.get('cylinder_weight_kg'),
                'cost_inr': order.get('cost_per_cylinder_inr'),
                'delivery_charges_inr': order.get('delivery_charges_inr'),
                'total_cost_inr': order.get('total_cost_inr'),
                'installation_date': datetime.now().strftime('%Y-%m-%d'),
                'current_weight_kg': order.get('cylinder_weight_kg'),
                'estimated_days_remaining': 50,  # Default estimate
                'status': 'Active',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'notes': 'Delivered and installed'
            }

            # Add to tracking
            self.data['gas_tracking'] = pd.concat([
                self.data['gas_tracking'],
                pd.DataFrame([new_tracking])
            ], ignore_index=True)

            # Save data
            self.save_gas_data()

            # Update UI
            self.populate_orders_table()
            self.populate_history_table()
            self.update_status_display()
            self.check_gas_levels()

            QMessageBox.information(self, "Order Delivered", "Order marked as delivered and cylinder activated!")

        except Exception as e:
            self.logger.error(f"Error marking order delivered: {e}")

    def update_purchase_summary(self, count, total_cost):
        """Update purchase summary labels"""
        try:
            avg_cost = total_cost / count if count > 0 else 0

            self.total_purchases_label.setText(f"Total Purchases: {count}")
            self.total_cost_label.setText(f"Total Cost: ₹{total_cost:.2f}")
            self.avg_cost_label.setText(f"Average Cost: ₹{avg_cost:.2f}")

        except Exception as e:
            self.logger.error(f"Error updating purchase summary: {e}")

    def apply_history_filter(self):
        """Apply filter to purchase history"""
        # This would filter the history table based on date range and supplier
        # For now, just refresh the table
        self.populate_history_table()

    def save_settings(self):
        """Save gas management settings"""
        try:
            # Update configuration
            self.gas_config['alert_settings']['low_gas_threshold_days'] = self.low_gas_threshold.value()
            self.gas_config['alert_settings']['critical_gas_threshold_days'] = self.critical_gas_threshold.value()
            self.gas_config['alert_settings']['enable_notifications'] = self.enable_notifications.isChecked()

            self.gas_config['cylinder_settings']['supplier'] = self.default_supplier.currentText()
            self.gas_config['cylinder_settings']['cylinder_cost_inr'] = self.default_cylinder_cost.value()

            # Save to file
            config_path = os.path.join('data', 'gas_cost_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.gas_config, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Settings Saved", "Gas management settings saved successfully!")

        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def add_home_usage(self):
        """Add manual home usage entry"""
        try:
            from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit

            dialog = QDialog(self)
            dialog.setWindowTitle("Add Home Gas Usage")
            dialog.setMinimumSize(300, 200)

            layout = QFormLayout(dialog)

            # Usage amount input
            usage_input = QDoubleSpinBox()
            usage_input.setRange(0.01, 5.0)
            usage_input.setSingleStep(0.1)
            usage_input.setDecimals(2)
            usage_input.setSuffix(" kg")
            layout.addRow("Usage Amount:", usage_input)

            # Purpose input
            purpose_input = QLineEdit()
            purpose_input.setPlaceholderText("e.g., Home cooking, heating water")
            layout.addRow("Purpose:", purpose_input)

            # Date input
            date_input = QDateEdit()
            date_input.setDate(QDate.currentDate())
            layout.addRow("Date:", date_input)

            # Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                self.save_home_usage(
                    usage_input.value(),
                    purpose_input.text(),
                    date_input.date().toString("yyyy-MM-dd")
                )

        except Exception as e:
            self.logger.error(f"Error adding home usage: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add home usage: {str(e)}")

    def save_home_usage(self, usage_amount, purpose, date):
        """Save home usage to data"""
        try:
            # Initialize gas usage dataframe if it doesn't exist
            if 'gas_usage' not in self.data:
                self.data['gas_usage'] = pd.DataFrame(columns=[
                    'usage_id', 'date', 'usage_kg', 'purpose', 'type', 'notes'
                ])

            # Create new usage entry
            new_usage = pd.DataFrame({
                'usage_id': [len(self.data['gas_usage']) + 1],
                'date': [date],
                'usage_kg': [usage_amount],
                'purpose': [purpose],
                'type': ['Home Usage'],
                'notes': ['Manual entry for home usage']
            })

            # Add to dataframe
            self.data['gas_usage'] = pd.concat([self.data['gas_usage'], new_usage], ignore_index=True)

            # Save to CSV
            gas_usage_file = os.path.join('data', 'gas_usage.csv')
            self.data['gas_usage'].to_csv(gas_usage_file, index=False)

            # Update displays
            self.load_gas_data()

            QMessageBox.information(self, "Success", f"Home gas usage of {usage_amount} kg added successfully!")

        except Exception as e:
            self.logger.error(f"Error saving home usage: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save home usage: {str(e)}")

    def update_gas_usage_from_sale(self, recipe_data, cooking_time_minutes):
        """Update gas usage when a sale is made based on cooking time"""
        try:
            # Calculate gas usage based on cooking time
            # Assume average gas consumption of 0.2 kg per hour of cooking
            gas_usage_per_hour = 0.2
            cooking_time_hours = cooking_time_minutes / 60.0
            estimated_gas_usage = gas_usage_per_hour * cooking_time_hours

            # Initialize gas usage dataframe if it doesn't exist
            if 'gas_usage' not in self.data:
                self.data['gas_usage'] = pd.DataFrame(columns=[
                    'usage_id', 'date', 'usage_kg', 'purpose', 'type', 'notes'
                ])

            # Create new usage entry
            new_usage = pd.DataFrame({
                'usage_id': [len(self.data['gas_usage']) + 1],
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'usage_kg': [estimated_gas_usage],
                'purpose': [f"Cooking: {recipe_data.get('recipe_name', 'Unknown Recipe')}"],
                'type': ['Cooking'],
                'notes': [f"Auto-calculated from sale. Cooking time: {cooking_time_minutes} minutes"]
            })

            # Add to dataframe
            self.data['gas_usage'] = pd.concat([self.data['gas_usage'], new_usage], ignore_index=True)

            # Save to CSV
            gas_usage_file = os.path.join('data', 'gas_usage.csv')
            self.data['gas_usage'].to_csv(gas_usage_file, index=False)

            self.logger.info(f"Gas usage updated: {estimated_gas_usage:.3f} kg for cooking {recipe_data.get('recipe_name', 'Unknown')}")

        except Exception as e:
            self.logger.error(f"Error updating gas usage from sale: {e}")

    def update_daily_usage(self):
        """Update daily gas usage"""
        try:
            usage_amount = self.daily_usage_input.value()
            if usage_amount <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid usage amount.")
                return

            # Save the usage
            self.save_home_usage(
                usage_amount,
                "Daily usage update",
                datetime.now().strftime('%Y-%m-%d')
            )

            # Clear the input
            self.daily_usage_input.setValue(0.0)

        except Exception as e:
            self.logger.error(f"Error updating daily usage: {e}")
            QMessageBox.warning(self, "Error", f"Failed to update daily usage: {str(e)}")
