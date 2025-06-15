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
from utils.table_styling import apply_universal_column_resizing

class WasteWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.waste_df = data['waste'].copy()
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Waste Tracking")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
    
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for different waste views
        self.waste_log_tab = QWidget()
        self.add_waste_tab = QWidget()
        self.waste_analysis_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.waste_log_tab, "Waste Log")
        self.tabs.addTab(self.add_waste_tab, "Record Waste")
        self.tabs.addTab(self.waste_analysis_tab, "Waste Analysis")
        
        # Set up each tab
        self.setup_waste_log_tab()
        self.setup_add_waste_tab()
        self.setup_waste_analysis_tab()
    
    def setup_waste_log_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.waste_log_tab)
        
        # Add subheader
        header = QLabel("Waste Log")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        # Date range filter
        date_label = QLabel("Date Range:")
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["All Time", "This Week", "This Month", "This Year", "Custom"])
        self.date_range_combo.currentIndexChanged.connect(self.update_date_filter)
        
        # Custom date range inputs (hidden by default)
        self.start_date_label = QLabel("Start Date:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate().addDays(-30))
        self.start_date_input.setVisible(False)
        
        self.end_date_label = QLabel("End Date:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setVisible(False)
        
        # Reason filter
        reason_label = QLabel("Reason:")
        self.reason_combo = QComboBox()
        self.reason_combo.addItem("All Reasons")
        if len(self.waste_df) > 0:
            reasons = sorted(self.waste_df['reason'].unique())
            self.reason_combo.addItems(reasons)
        
        # Add widgets to filter layout
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_range_combo)
        filter_layout.addWidget(self.start_date_label)
        filter_layout.addWidget(self.start_date_input)
        filter_layout.addWidget(self.end_date_label)
        filter_layout.addWidget(self.end_date_input)
        filter_layout.addWidget(reason_label)
        filter_layout.addWidget(self.reason_combo)
        filter_layout.addStretch(1)
        
        layout.addWidget(filter_widget)
        
        # Apply button
        self.apply_filter_button = QPushButton("Apply Filters")
        self.apply_filter_button.clicked.connect(self.update_waste_log)
        layout.addWidget(self.apply_filter_button)
        
        # Waste log table
        self.waste_table = QTableWidget()
        self.waste_table.setColumnCount(6)
        self.waste_table.setHorizontalHeaderLabels([
            "Date", "Item", "Quantity", "Unit", "Reason", "Cost"
        ])
        self.waste_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.waste_table.setAlternatingRowColors(True)

        # Apply universal column resizing functionality
        waste_default_column_widths = {
            0: 120,  # Date
            1: 200,  # Item
            2: 80,   # Quantity
            3: 80,   # Unit
            4: 150,  # Reason
            5: 100   # Cost
        }

        # Apply column resizing with settings persistence
        self.waste_table_resizer = apply_universal_column_resizing(
            self.waste_table,
            'waste_column_settings.json',
            waste_default_column_widths
        )

        print("✅ Applied universal column resizing to waste table")
        layout.addWidget(self.waste_table)

        # Action buttons for waste records
        waste_buttons_layout = QHBoxLayout()

        # Edit button
        self.edit_waste_button = QPushButton("Edit Selected")
        self.edit_waste_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.edit_waste_button.clicked.connect(self.edit_selected_waste)
        waste_buttons_layout.addWidget(self.edit_waste_button)

        # Delete button
        self.delete_waste_button = QPushButton("Delete Selected")
        self.delete_waste_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.delete_waste_button.clicked.connect(self.delete_selected_waste)
        waste_buttons_layout.addWidget(self.delete_waste_button)

        waste_buttons_layout.addStretch()
        layout.addLayout(waste_buttons_layout)

        # Summary section
        self.summary_widget = QWidget()
        self.summary_layout = QHBoxLayout(self.summary_widget)
        layout.addWidget(self.summary_widget)
        
        # Update the waste log
        self.update_waste_log()
    
    def update_date_filter(self):
        # Show/hide custom date inputs based on selection
        show_custom = self.date_range_combo.currentText() == "Custom"
        self.start_date_label.setVisible(show_custom)
        self.start_date_input.setVisible(show_custom)
        self.end_date_label.setVisible(show_custom)
        self.end_date_input.setVisible(show_custom)
    
    def update_waste_log(self):
        # Apply filters
        filtered_df = self.waste_df.copy()
        
        # Check if we have any data
        if len(filtered_df) == 0:
            return
        
        # Ensure date column is datetime type
        if 'date' in filtered_df.columns:
            try:
                if filtered_df['date'].dtype == 'object':
                    filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
            except Exception as e:
                print(f"Error converting dates: {e}")
                # If conversion fails, just display as is
                pass
        
        # Date range filter
        date_range = self.date_range_combo.currentText()
        today = datetime.now().date()
        
        # Only apply date filters if date column is datetime
        if 'date' in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df['date']):
            if date_range == "This Week":
                start_of_week = today - timedelta(days=today.weekday())
                filtered_df = filtered_df[filtered_df['date'].dt.date >= start_of_week]
            elif date_range == "This Month":
                start_of_month = today.replace(day=1)
                filtered_df = filtered_df[filtered_df['date'].dt.date >= start_of_month]
            elif date_range == "This Year":
                start_of_year = today.replace(month=1, day=1)
                filtered_df = filtered_df[filtered_df['date'].dt.date >= start_of_year]
            elif date_range == "Custom":
                start_date = self.start_date_input.date().toPython()
                end_date = self.end_date_input.date().toPython()
                filtered_df = filtered_df[
                    (filtered_df['date'].dt.date >= start_date) & 
                    (filtered_df['date'].dt.date <= end_date)
                ]
        
        # Reason filter
        reason_filter = self.reason_combo.currentText()
        if reason_filter != "All Reasons":
            filtered_df = filtered_df[filtered_df['reason'] == reason_filter]
        
        # Update table
        self.waste_table.setRowCount(len(filtered_df))
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            # Handle date display safely
            if 'date' in row and pd.notna(row['date']):
                if isinstance(row['date'], datetime):
                    date_str = str(row['date'].date())
                else:
                    # If it's still a string after conversion attempts
                    date_str = str(row['date'])
            else:
                date_str = ""
                
            self.waste_table.setItem(i, 0, QTableWidgetItem(date_str))
            self.waste_table.setItem(i, 1, QTableWidgetItem(str(row['item_name']) if 'item_name' in row else ""))
            self.waste_table.setItem(i, 2, QTableWidgetItem(str(row['quantity']) if 'quantity' in row else ""))
            self.waste_table.setItem(i, 3, QTableWidgetItem(str(row['unit']) if 'unit' in row else ""))
            self.waste_table.setItem(i, 4, QTableWidgetItem(str(row['reason']) if 'reason' in row else ""))
            self.waste_table.setItem(i, 5, QTableWidgetItem(f"₹{row['cost']:.2f}" if 'cost' in row else "₹0.00"))
        
        # Update summary
        self.update_summary(filtered_df)
    
    def update_summary(self, df):
        # Clear the summary layout
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Calculate summary metrics
        total_items = len(df)
        total_cost = df['cost'].sum()
        
        # Create summary widgets
        items_group = QGroupBox("Total Waste Items")
        items_layout = QVBoxLayout(items_group)
        items_label = QLabel(f"{total_items}")
        items_label.setFont(QFont("Arial", 16, QFont.Bold))
        items_label.setAlignment(Qt.AlignCenter)
        items_layout.addWidget(items_label)
        self.summary_layout.addWidget(items_group)
        
        cost_group = QGroupBox("Total Cost")
        cost_layout = QVBoxLayout(cost_group)
        cost_label = QLabel(f"₹{total_cost:.2f}")
        cost_label.setFont(QFont("Arial", 16, QFont.Bold))
        cost_label.setAlignment(Qt.AlignCenter)
        cost_layout.addWidget(cost_label)
        self.summary_layout.addWidget(cost_group)
    
    def setup_add_waste_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_waste_tab)
        
        # Add subheader
        header = QLabel("Record Waste Item")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Create form for adding waste
        form_group = QGroupBox("Waste Details")
        form_layout = QFormLayout(form_group)
        
        # Item name from inventory or meal planning
        self.item_name = QComboBox()
        self.item_name.setEditable(False)  # Allow custom entries too
        self.item_name.setCurrentText("")
        
        # Populate with items from inventory if available
        all_items = []
        if 'items' in self.data and len(self.data['items']) > 0:
            inventory_items = sorted(self.data['items']['item_name'].unique())
            all_items.extend(inventory_items)
            
        # Add recipe names from meal planning if available
        if 'recipes' in self.data and len(self.data['recipes']) > 0:
            recipe_items = sorted(self.data['recipes']['recipe_name'].unique())
            all_items.extend(recipe_items)
            
        # Remove duplicates and sort
        all_items = sorted(set(all_items))
        if all_items:
            self.item_name.addItems(all_items)
            
        form_layout.addRow("Item Name:", self.item_name)
        
        # Quantity
        self.waste_quantity = QDoubleSpinBox()
        self.waste_quantity.setMinimum(0.1)
        self.waste_quantity.setMaximum(1000)
        self.waste_quantity.setValue(1)
        form_layout.addRow("Quantity:", self.waste_quantity)
        
        # Unit
        self.waste_unit = QComboBox()
        self.waste_unit.addItems(["kg", "g", "L", "ml", "units", "pcs", "loaves", "cans", "bottles"])
        self.waste_unit.setEditable(False)
        form_layout.addRow("Unit:", self.waste_unit)
        
        # Reason
        self.waste_reason = QComboBox()
        default_reasons = ["Spoiled", "Expired", "Overcooked", "Leftover", "Damaged", "Other"]
        if len(self.waste_df) > 0:
            reasons = sorted(self.waste_df['reason'].unique())
            self.waste_reason.addItems(reasons)
        else:
            self.waste_reason.addItems(default_reasons)
        self.waste_reason.setEditable(True)
        form_layout.addRow("Reason:", self.waste_reason)
        
        # Cost
        self.waste_cost = QDoubleSpinBox()
        self.waste_cost.setPrefix("₹")
        self.waste_cost.setMinimum(0.01)
        self.waste_cost.setMaximum(1000)
        self.waste_cost.setValue(1.00)
        self.waste_cost.setDecimals(2)
        form_layout.addRow("Cost:", self.waste_cost)
        
        # Date
        self.waste_date = QDateEdit()
        self.waste_date.setCalendarPopup(True)
        self.waste_date.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.waste_date)
        
        layout.addWidget(form_group)
        
        # Add button
        self.add_waste_button = QPushButton("Record Waste")
        self.add_waste_button.clicked.connect(self.add_waste_record)
        layout.addWidget(self.add_waste_button)
        
        # Add stretch to push form to the top
        layout.addStretch(1)
    
    def add_waste_record(self):
        # Get form values
        item_name = self.item_name.currentText()
        quantity = self.waste_quantity.value()
        unit = self.waste_unit.currentText()
        reason = self.waste_reason.currentText()
        cost = self.waste_cost.value()
        date = self.waste_date.date().toString("yyyy-MM-dd")
        
        # Validate input
        if not item_name:
            QMessageBox.warning(self, "Input Error", "Please enter an item name.")
            return
        
        # Generate new waste ID
        if 'waste_id' in self.waste_df.columns and len(self.waste_df) > 0:
            new_waste_id = self.waste_df['waste_id'].max() + 1
        else:
            new_waste_id = 1
        
        # Create new waste record
        new_waste = pd.DataFrame({
            'waste_id': [new_waste_id],
            'item_name': [item_name],
            'quantity': [quantity],
            'unit': [unit],
            'reason': [reason],
            'cost': [cost],
            'date': [date]
        })
        
        # Add to waste dataframe
        self.waste_df = pd.concat([self.waste_df, new_waste], ignore_index=True)
        self.data['waste'] = self.waste_df
        
        # Save to CSV
        self.waste_df.to_csv('data/waste.csv', index=False)
        
        # Show success message
        QMessageBox.information(self, "Success", "Waste record added successfully!")
        
        # Clear form
        self.item_name.setCurrentText("")
        self.waste_quantity.setValue(1)
        self.waste_cost.setValue(1.00)
        
        # Update waste log
        self.update_waste_log()
        
        # Update analysis
        self.setup_waste_analysis_tab()
    
    def setup_waste_analysis_tab(self):
        # Clear the tab
        while self.waste_analysis_tab.layout():
            old_layout = self.waste_analysis_tab.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old_layout)
        
        # Create layout for the tab
        layout = QVBoxLayout(self.waste_analysis_tab)
    
        # Check if we have waste data
        if len(self.waste_df) > 0:
            # Ensure date column is datetime type
            if 'date' in self.waste_df.columns and not pd.api.types.is_datetime64_any_dtype(self.waste_df['date']):
                try:
                    self.waste_df['date'] = pd.to_datetime(self.waste_df['date'], errors='coerce')
                except Exception as e:
                    print(f"Error converting dates: {e}")
            
            # Create a splitter for top charts
            top_splitter = QSplitter(Qt.Horizontal)
            layout.addWidget(top_splitter)
            
            # Left side - Waste by reason
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            left_layout.addWidget(QLabel("Waste by Reason"))
            
            # Group by reason
            waste_by_reason = self.waste_df.groupby('reason')['cost'].sum().reset_index()
            waste_by_reason = waste_by_reason.sort_values('cost', ascending=False)
            
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            ax1.pie(waste_by_reason['cost'], labels=waste_by_reason['reason'], autopct='%1.1f%%')
            ax1.set_title('Waste Cost by Reason')
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.tight_layout()
            
            canvas1 = FigureCanvas(fig1)
            left_layout.addWidget(canvas1)
            top_splitter.addWidget(left_widget)
            
            # Right side - Waste over time
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.addWidget(QLabel("Waste Over Time"))
            
            # Group by month - only if date is a valid datetime column
            if 'date' in self.waste_df.columns and pd.api.types.is_datetime64_any_dtype(self.waste_df['date']):
                # Create month period and group by it
                self.waste_df['month'] = self.waste_df['date'].dt.to_period('M')
                waste_by_month = self.waste_df.groupby('month')['cost'].sum().reset_index()
                waste_by_month['month_str'] = waste_by_month['month'].dt.strftime('%Y-%m')
                
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                ax2.bar(waste_by_month['month_str'], waste_by_month['cost'])
                ax2.set_xlabel('Month')
                ax2.set_ylabel('Cost (₹)')
                ax2.set_title('Waste Cost Over Time')
                ax2.tick_params(axis='x', rotation=45)
                plt.tight_layout()
                
                canvas2 = FigureCanvas(fig2)
                right_layout.addWidget(canvas2)
            else:
                # If date column is not valid, show a message
                no_date_label = QLabel("Date information not available for time analysis.")
                no_date_label.setAlignment(Qt.AlignCenter)
                right_layout.addWidget(no_date_label)
                
            top_splitter.addWidget(right_widget)
            
            # Add table with waste by reason
            table_label = QLabel("Waste by Reason")
            table_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(table_label)
            
            reason_table = QTableWidget()
            reason_table.setColumnCount(3)
            reason_table.setHorizontalHeaderLabels(["Reason", "Number of Items", "Total Cost"])

            # Apply universal column resizing functionality
            reason_default_column_widths = {
                0: 200,  # Reason
                1: 150,  # Number of Items
                2: 120   # Total Cost
            }

            # Apply column resizing with settings persistence
            reason_table_resizer = apply_universal_column_resizing(
                reason_table,
                'waste_reason_column_settings.json',
                reason_default_column_widths
            )

            print("✅ Applied universal column resizing to waste reason table")
            
            # Group by reason with count and sum
            # Check if waste_id column exists
            if 'waste_id' in self.waste_df.columns:
                count_column = 'waste_id'
            else:
                # If waste_id doesn't exist, use any column for counting
                count_column = self.waste_df.columns[0]
                
            waste_by_reason_detail = self.waste_df.groupby('reason').agg({
                count_column: 'count',
                'cost': 'sum'
            }).reset_index()
            waste_by_reason_detail.columns = ['reason', 'count', 'total_cost']
            waste_by_reason_detail = waste_by_reason_detail.sort_values('total_cost', ascending=False)
            
            reason_table.setRowCount(len(waste_by_reason_detail))
            for i, (_, row) in enumerate(waste_by_reason_detail.iterrows()):
                reason_table.setItem(i, 0, QTableWidgetItem(row['reason']))
                reason_table.setItem(i, 1, QTableWidgetItem(str(row['count'])))
                reason_table.setItem(i, 2, QTableWidgetItem(f"₹{row['total_cost']:.2f}"))
            
            layout.addWidget(reason_table)
            
            # Add recommendations section
            recommendations_group = QGroupBox("Waste Reduction Recommendations")
            recommendations_layout = QVBoxLayout(recommendations_group)
            
            # Get top waste reason
            top_reason = waste_by_reason.iloc[0]['reason'] if len(waste_by_reason) > 0 else None
            
            if top_reason:
                if top_reason == "Expired":
                    recommendations_layout.addWidget(QLabel("• Implement a first-in, first-out (FIFO) inventory system"))
                    recommendations_layout.addWidget(QLabel("• Improve inventory tracking and labeling with expiry dates"))
                    recommendations_layout.addWidget(QLabel("• Adjust ordering quantities to reduce excess inventory"))
                elif top_reason == "Spoiled":
                    recommendations_layout.addWidget(QLabel("• Check and adjust refrigeration temperatures"))
                    recommendations_layout.addWidget(QLabel("• Improve storage conditions for perishable items"))
                    recommendations_layout.addWidget(QLabel("• Consider more frequent, smaller deliveries of fresh items"))
                elif top_reason == "Leftover":
                    recommendations_layout.addWidget(QLabel("• Adjust portion sizes or batch cooking amounts"))
                    recommendations_layout.addWidget(QLabel("• Implement better meal planning to use leftovers"))
                    recommendations_layout.addWidget(QLabel("• Consider creative ways to repurpose leftover ingredients"))
                else:
                    recommendations_layout.addWidget(QLabel("• Analyze the cause of your most common waste reason"))
                    recommendations_layout.addWidget(QLabel("• Implement targeted strategies to address this specific issue"))
                    recommendations_layout.addWidget(QLabel("• Train staff on waste reduction practices"))
            else:
                recommendations_layout.addWidget(QLabel("• Start tracking waste consistently to identify patterns"))
                recommendations_layout.addWidget(QLabel("• Implement a labeling system with dates for all stored items"))
                recommendations_layout.addWidget(QLabel("• Review inventory management practices"))
            
            layout.addWidget(recommendations_group)
        else:
            no_data_label = QLabel("No waste data available for analysis.")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)

    def edit_selected_waste(self):
        """Edit the selected waste record"""
        try:
            current_row = self.waste_table.currentRow()
            if current_row < 0:
                QMessageBox.information(self, "No Selection", "Please select a waste record to edit.")
                return

            # Get the waste record from the current row
            if current_row < len(self.waste_df):
                record = self.waste_df.iloc[current_row]

                # Populate form fields with existing data
                self.item_name.setCurrentText(str(record.get('item_name', '')))
                self.waste_quantity.setValue(float(record.get('quantity', 0)))
                self.waste_unit.setCurrentText(str(record.get('unit', 'kg')))
                self.waste_reason.setCurrentText(str(record.get('reason', '')))
                self.waste_cost.setValue(float(record.get('cost', 0)))

                # Set date
                date_str = str(record.get('date', ''))
                if date_str:
                    try:
                        date_obj = pd.to_datetime(date_str).date()
                        self.waste_date.setDate(QDate.fromString(date_obj.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
                    except:
                        self.waste_date.setDate(QDate.currentDate())

                # Store the row index for updating
                self.editing_waste_row = current_row

                QMessageBox.information(self, "Edit Mode", "Form populated with selected record data. Modify the fields and click 'Add Waste Record' to update.")

        except Exception as e:
            print(f"Error editing waste record: {e}")
            QMessageBox.warning(self, "Error", f"Error editing waste record: {str(e)}")

    def delete_selected_waste(self):
        """Delete the selected waste record"""
        try:
            current_row = self.waste_table.currentRow()
            if current_row < 0:
                QMessageBox.information(self, "No Selection", "Please select a waste record to delete.")
                return

            # Get item name for confirmation
            item_name = self.waste_table.item(current_row, 1).text()

            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete the waste record for '{item_name}'?\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove from dataframe
                if current_row < len(self.waste_df):
                    self.waste_df = self.waste_df.drop(self.waste_df.index[current_row]).reset_index(drop=True)

                    # Update data reference
                    self.data['waste'] = self.waste_df

                    # Save to CSV
                    self.waste_df.to_csv('data/waste.csv', index=False)

                    # Refresh the display
                    self.update_waste_log()
                    self.setup_waste_analysis_tab()

                    QMessageBox.information(self, "Success", f"Waste record for '{item_name}' has been deleted.")

        except Exception as e:
            print(f"Error deleting waste record: {e}")
            QMessageBox.warning(self, "Error", f"Error deleting waste record: {str(e)}")
