"""
Comprehensive Data Import Wizard for Kitchen Dashboard
Supports Zomato/Swiggy data import and historical data upload
"""

import os
import pandas as pd
import logging
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QWidget, QFileDialog,
                             QProgressBar, QTextEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QGroupBox, QFormLayout, QLineEdit, QCheckBox,
                             QScrollArea, QFrame, QGridLayout, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

# Import notification system
try:
    from .notification_system import notify_info, notify_success, notify_warning, notify_error
except ImportError:
    def notify_info(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_success(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_warning(title, message, **kwargs): logging.warning(f"{title}: {message}")
    def notify_error(title, message, **kwargs): logging.error(f"{title}: {message}")

class DataImportWorker(QThread):
    """Background worker for data import operations"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    import_completed = Signal(dict)
    import_failed = Signal(str)
    
    def __init__(self, file_path, import_type, data_mapping, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.import_type = import_type
        self.data_mapping = data_mapping
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Execute the import operation"""
        try:
            self.status_updated.emit("Starting import...")
            self.progress_updated.emit(10)
            
            # Read the file
            if self.file_path.endswith('.csv'):
                df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format")
            
            self.status_updated.emit("File loaded successfully...")
            self.progress_updated.emit(30)
            
            # Process based on import type
            if self.import_type == "zomato":
                processed_data = self.process_zomato_data(df)
            elif self.import_type == "swiggy":
                processed_data = self.process_swiggy_data(df)
            elif self.import_type == "sales":
                processed_data = self.process_sales_data(df)
            elif self.import_type == "inventory":
                processed_data = self.process_inventory_data(df)
            elif self.import_type == "expenses":
                processed_data = self.process_expenses_data(df)
            else:
                processed_data = self.process_generic_data(df)
            
            self.status_updated.emit("Data processed successfully...")
            self.progress_updated.emit(80)
            
            # Validate data
            validation_results = self.validate_data(processed_data)
            
            self.status_updated.emit("Import completed!")
            self.progress_updated.emit(100)
            
            # Return results
            results = {
                'data': processed_data,
                'validation': validation_results,
                'import_type': self.import_type,
                'records_count': len(processed_data) if processed_data is not None else 0
            }
            
            self.import_completed.emit(results)
            
        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}")
            self.import_failed.emit(str(e))
    
    def process_zomato_data(self, df):
        """Process Zomato settlement report data"""
        try:
            # Look for order level data in Zomato reports
            if 'Order ID' in df.columns:
                # Process order level data
                sales_data = []
                for _, row in df.iterrows():
                    if pd.notna(row.get('Order ID')):
                        sale_record = {
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'order_id': str(row.get('Order ID', '')),
                            'platform': 'Zomato',
                            'customer': 'Zomato Customer',
                            'item_name': str(row.get('Item Name', 'Unknown Item')),
                            'quantity': 1,
                            'subtotal': float(row.get('Item Total', 0)),
                            'taxes': float(row.get('Tax', 0)),
                            'delivery_fee': float(row.get('Delivery Fee', 0)),
                            'discount': float(row.get('Discount', 0)),
                            'total_amount': float(row.get('Net Amount', 0)),
                            'payment_method': 'Online',
                            'status': 'Completed',
                            'notes': 'Imported from Zomato'
                        }
                        sales_data.append(sale_record)
                
                return pd.DataFrame(sales_data)
            else:
                # Try to extract summary data
                return self.extract_zomato_summary(df)
                
        except Exception as e:
            self.logger.error(f"Error processing Zomato data: {e}")
            return None
    
    def process_swiggy_data(self, df):
        """Process Swiggy data"""
        try:
            # Similar processing for Swiggy data
            sales_data = []
            for _, row in df.iterrows():
                if pd.notna(row.get('Order ID', row.get('order_id'))):
                    sale_record = {
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
                    sales_data.append(sale_record)
            
            return pd.DataFrame(sales_data)
            
        except Exception as e:
            self.logger.error(f"Error processing Swiggy data: {e}")
            return None
    
    def process_sales_data(self, df):
        """Process generic sales data"""
        # Map columns to standard format
        return df
    
    def process_inventory_data(self, df):
        """Process inventory data"""
        return df
    
    def process_expenses_data(self, df):
        """Process expenses data"""
        return df
    
    def process_generic_data(self, df):
        """Process generic data"""
        return df
    
    def extract_zomato_summary(self, df):
        """Extract summary data from Zomato reports"""
        # Look for summary information in the report
        summary_data = []
        
        # Try to find total sales, orders, etc.
        for _, row in df.iterrows():
            if 'Total' in str(row.iloc[0]) or 'Summary' in str(row.iloc[0]):
                # Extract summary information
                pass
        
        return pd.DataFrame(summary_data)
    
    def validate_data(self, df):
        """Validate imported data"""
        if df is None or df.empty:
            return {'valid': False, 'errors': ['No data to import']}
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_records': len(df),
                'valid_records': 0,
                'invalid_records': 0
            }
        }
        
        # Basic validation
        if len(df) == 0:
            validation_results['valid'] = False
            validation_results['errors'].append('No records found in file')
        
        # Check for required columns based on import type
        required_columns = self.get_required_columns()
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            validation_results['warnings'].append(f'Missing columns: {", ".join(missing_columns)}')
        
        validation_results['stats']['valid_records'] = len(df)
        
        return validation_results
    
    def get_required_columns(self):
        """Get required columns for the import type"""
        if self.import_type in ['zomato', 'swiggy', 'sales']:
            return ['order_id', 'total_amount']
        elif self.import_type == 'inventory':
            return ['item_name', 'quantity']
        elif self.import_type == 'expenses':
            return ['date', 'amount', 'category']
        return []

class DataImportWizard(QDialog):
    """Comprehensive data import wizard"""
    
    data_imported = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Import Wizard")
        self.setFixedSize(900, 700)
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI
        self.init_ui()
        
        # Import worker
        self.import_worker = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Data Import Wizard")
        header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        subtitle_label = QLabel("Import historical data from various sources")
        subtitle_label.setStyleSheet("font-size: 14px; color: #64748b; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)
        
        # Create tabs for different import types
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
        
        # Platform Import Tab
        self.create_platform_import_tab()
        
        # Historical Data Tab
        self.create_historical_data_tab()
        
        # Bulk Import Tab
        self.create_bulk_import_tab()
        
        layout.addWidget(self.tabs)
        
        # Progress section
        self.create_progress_section(layout)
        
        # Buttons
        self.create_buttons(layout)
    
    def create_platform_import_tab(self):
        """Create platform import tab for Zomato/Swiggy"""
        platform_widget = QWidget()
        layout = QVBoxLayout(platform_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Zomato Import Section
        zomato_group = QGroupBox("Zomato Data Import")
        zomato_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #dc2626;
                border: 2px solid #fecaca;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        zomato_layout = QVBoxLayout(zomato_group)
        
        zomato_info = QLabel("Import settlement reports and order data from Zomato")
        zomato_info.setStyleSheet("color: #64748b; margin-bottom: 10px;")
        zomato_layout.addWidget(zomato_info)
        
        zomato_file_layout = QHBoxLayout()
        self.zomato_file_label = QLabel("No file selected")
        self.zomato_file_label.setStyleSheet("color: #64748b; padding: 8px; border: 1px solid #e2e8f0; border-radius: 4px;")
        zomato_browse_btn = QPushButton("Browse Zomato Files")
        zomato_browse_btn.clicked.connect(lambda: self.browse_file('zomato'))
        
        zomato_file_layout.addWidget(self.zomato_file_label, 1)
        zomato_file_layout.addWidget(zomato_browse_btn)
        zomato_layout.addLayout(zomato_file_layout)
        
        zomato_import_btn = QPushButton("Import Zomato Data")
        zomato_import_btn.setStyleSheet("background-color: #dc2626; color: white; padding: 10px; border-radius: 6px;")
        zomato_import_btn.clicked.connect(lambda: self.start_import('zomato'))
        zomato_layout.addWidget(zomato_import_btn)
        
        layout.addWidget(zomato_group)
        
        # Swiggy Import Section
        swiggy_group = QGroupBox("Swiggy Data Import")
        swiggy_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #ea580c;
                border: 2px solid #fed7aa;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        swiggy_layout = QVBoxLayout(swiggy_group)
        
        swiggy_info = QLabel("Import payment advice and order data from Swiggy")
        swiggy_info.setStyleSheet("color: #64748b; margin-bottom: 10px;")
        swiggy_layout.addWidget(swiggy_info)
        
        swiggy_file_layout = QHBoxLayout()
        self.swiggy_file_label = QLabel("No file selected")
        self.swiggy_file_label.setStyleSheet("color: #64748b; padding: 8px; border: 1px solid #e2e8f0; border-radius: 4px;")
        swiggy_browse_btn = QPushButton("Browse Swiggy Files")
        swiggy_browse_btn.clicked.connect(lambda: self.browse_file('swiggy'))
        
        swiggy_file_layout.addWidget(self.swiggy_file_label, 1)
        swiggy_file_layout.addWidget(swiggy_browse_btn)
        swiggy_layout.addLayout(swiggy_file_layout)
        
        swiggy_import_btn = QPushButton("Import Swiggy Data")
        swiggy_import_btn.setStyleSheet("background-color: #ea580c; color: white; padding: 10px; border-radius: 6px;")
        swiggy_import_btn.clicked.connect(lambda: self.start_import('swiggy'))
        swiggy_layout.addWidget(swiggy_import_btn)
        
        layout.addWidget(swiggy_group)
        
        layout.addStretch()
        
        self.tabs.addTab(platform_widget, "Platform Import")
    
    def create_historical_data_tab(self):
        """Create historical data import tab"""
        historical_widget = QWidget()
        layout = QVBoxLayout(historical_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Data type selection
        type_group = QGroupBox("Select Data Type")
        type_layout = QFormLayout(type_group)
        
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            "Sales Data", "Inventory Data", "Expense Data", 
            "Recipe Data", "Customer Data", "Supplier Data"
        ])
        type_layout.addRow("Data Type:", self.data_type_combo)
        
        layout.addWidget(type_group)
        
        # File selection
        file_group = QGroupBox("Select File")
        file_layout = QVBoxLayout(file_group)
        
        file_select_layout = QHBoxLayout()
        self.historical_file_label = QLabel("No file selected")
        self.historical_file_label.setStyleSheet("color: #64748b; padding: 8px; border: 1px solid #e2e8f0; border-radius: 4px;")
        historical_browse_btn = QPushButton("Browse Files")
        historical_browse_btn.clicked.connect(lambda: self.browse_file('historical'))
        
        file_select_layout.addWidget(self.historical_file_label, 1)
        file_select_layout.addWidget(historical_browse_btn)
        file_layout.addLayout(file_select_layout)
        
        layout.addWidget(file_group)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        self.append_data_checkbox = QCheckBox("Append to existing data")
        self.append_data_checkbox.setChecked(True)
        options_layout.addWidget(self.append_data_checkbox)
        
        self.validate_data_checkbox = QCheckBox("Validate data before import")
        self.validate_data_checkbox.setChecked(True)
        options_layout.addWidget(self.validate_data_checkbox)
        
        layout.addWidget(options_group)
        
        # Import button
        historical_import_btn = QPushButton("Import Historical Data")
        historical_import_btn.setStyleSheet("background-color: #2563eb; color: white; padding: 12px; border-radius: 6px; font-weight: 500;")
        historical_import_btn.clicked.connect(lambda: self.start_import('historical'))
        layout.addWidget(historical_import_btn)
        
        layout.addStretch()
        
        self.tabs.addTab(historical_widget, "Historical Data")
    
    def create_bulk_import_tab(self):
        """Create bulk import tab"""
        bulk_widget = QWidget()
        layout = QVBoxLayout(bulk_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        info_label = QLabel("Bulk import multiple files at once")
        info_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 20px;")
        layout.addWidget(info_label)
        
        # File list
        self.bulk_files_table = QTableWidget()
        self.bulk_files_table.setColumnCount(3)
        self.bulk_files_table.setHorizontalHeaderLabels(["File Name", "Data Type", "Status"])
        self.bulk_files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.bulk_files_table)
        
        # Buttons
        bulk_buttons_layout = QHBoxLayout()
        
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_bulk_files)
        bulk_buttons_layout.addWidget(add_files_btn)
        
        remove_files_btn = QPushButton("Remove Selected")
        remove_files_btn.clicked.connect(self.remove_bulk_files)
        bulk_buttons_layout.addWidget(remove_files_btn)
        
        bulk_buttons_layout.addStretch()
        
        import_all_btn = QPushButton("Import All Files")
        import_all_btn.setStyleSheet("background-color: #059669; color: white; padding: 10px 20px; border-radius: 6px;")
        import_all_btn.clicked.connect(self.start_bulk_import)
        bulk_buttons_layout.addWidget(import_all_btn)
        
        layout.addLayout(bulk_buttons_layout)
        
        self.tabs.addTab(bulk_widget, "Bulk Import")
    
    def create_progress_section(self, parent_layout):
        """Create progress tracking section"""
        progress_group = QGroupBox("Import Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to import")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px;")
        progress_layout.addWidget(self.status_label)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(100)
        self.results_text.setVisible(False)
        progress_layout.addWidget(self.results_text)
        
        parent_layout.addWidget(progress_group)
    
    def create_buttons(self, parent_layout):
        """Create dialog buttons"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    def browse_file(self, import_type):
        """Browse for import file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            f"Select {import_type.title()} File",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            if import_type == 'zomato':
                self.zomato_file_label.setText(os.path.basename(file_path))
                self.zomato_file_path = file_path
            elif import_type == 'swiggy':
                self.swiggy_file_label.setText(os.path.basename(file_path))
                self.swiggy_file_path = file_path
            elif import_type == 'historical':
                self.historical_file_label.setText(os.path.basename(file_path))
                self.historical_file_path = file_path
    
    def start_import(self, import_type):
        """Start the import process"""
        try:
            # Get file path
            if import_type == 'zomato':
                file_path = getattr(self, 'zomato_file_path', None)
            elif import_type == 'swiggy':
                file_path = getattr(self, 'swiggy_file_path', None)
            elif import_type == 'historical':
                file_path = getattr(self, 'historical_file_path', None)
            else:
                file_path = None
            
            if not file_path:
                notify_warning("No File", "Please select a file to import", parent=self)
                return
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Starting import...")
            self.results_text.setVisible(False)
            
            # Start import worker
            self.import_worker = DataImportWorker(file_path, import_type, {})
            self.import_worker.progress_updated.connect(self.progress_bar.setValue)
            self.import_worker.status_updated.connect(self.status_label.setText)
            self.import_worker.import_completed.connect(self.import_completed)
            self.import_worker.import_failed.connect(self.import_failed)
            self.import_worker.start()
            
        except Exception as e:
            self.logger.error(f"Error starting import: {e}")
            notify_error("Import Error", f"Failed to start import: {str(e)}", parent=self)
    
    def import_completed(self, results):
        """Handle completed import"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Import completed successfully!")
        
        # Show results
        self.results_text.setVisible(True)
        results_text = f"""
Import Summary:
- Import Type: {results['import_type'].title()}
- Records Imported: {results['records_count']}
- Validation: {'Passed' if results['validation']['valid'] else 'Failed'}
"""
        
        if results['validation']['errors']:
            results_text += f"- Errors: {len(results['validation']['errors'])}\n"
        if results['validation']['warnings']:
            results_text += f"- Warnings: {len(results['validation']['warnings'])}\n"
        
        self.results_text.setText(results_text)
        
        # Emit signal with imported data
        self.data_imported.emit(results)
        
        notify_success("Import Complete", f"Successfully imported {results['records_count']} records", parent=self)
    
    def import_failed(self, error_message):
        """Handle failed import"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Import failed!")
        
        self.results_text.setVisible(True)
        self.results_text.setText(f"Import failed with error:\n{error_message}")
        
        notify_error("Import Failed", f"Import failed: {error_message}", parent=self)
    
    def add_bulk_files(self):
        """Add files for bulk import"""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "Select Files for Bulk Import",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        
        for file_path in file_paths:
            row = self.bulk_files_table.rowCount()
            self.bulk_files_table.insertRow(row)
            
            self.bulk_files_table.setItem(row, 0, QTableWidgetItem(os.path.basename(file_path)))
            self.bulk_files_table.setItem(row, 1, QTableWidgetItem("Auto-detect"))
            self.bulk_files_table.setItem(row, 2, QTableWidgetItem("Pending"))
    
    def remove_bulk_files(self):
        """Remove selected files from bulk import"""
        current_row = self.bulk_files_table.currentRow()
        if current_row >= 0:
            self.bulk_files_table.removeRow(current_row)
    
    def start_bulk_import(self):
        """Start bulk import process"""
        notify_info("Bulk Import", "Bulk import functionality coming soon", parent=self)
