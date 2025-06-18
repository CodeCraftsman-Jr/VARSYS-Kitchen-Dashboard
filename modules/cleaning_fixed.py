from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                             QMessageBox, QHeaderView, QSplitter, QCalendarWidget, QTextEdit)
import numpy as np
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QTextCharFormat
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import calendar
import os
from utils.table_styling import apply_universal_column_resizing

class CleaningWidget(QWidget):
    def safe_string_convert(self, value):
        """Safely convert any value to a string for QTableWidgetItem to prevent overflow errors"""
        try:
            # Handle NaN, None, and other special values
            if pd.isna(value) or value is None:
                return ""
            
            # Handle numpy integers that might cause overflow
            if isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                return str(int(value))
                
            # Handle other numeric types
            if isinstance(value, (int, float)):
                return str(value)
                
            # Default string conversion
            return str(value)
        except Exception as e:
            print(f"Error converting value to string: {e}")
            return ""
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.cleaning_df = data['cleaning_maintenance'].copy()
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Cleaning & Maintenance")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
    
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for different cleaning views
        self.schedule_tab = QWidget()
        self.add_task_tab = QWidget()
        self.calendar_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.schedule_tab, "Task Schedule")
        self.tabs.addTab(self.add_task_tab, "Add/Edit Task")
        self.tabs.addTab(self.calendar_tab, "Calendar View")
        
        # Set up each tab
        self.setup_schedule_tab()
        self.setup_add_task_tab()
        self.setup_calendar_tab()
        
        # Initialize edit mode variables
        self.edit_mode = False
        self.original_task_name = None

    def load_staff_options(self):
        """Load staff members into the combo box"""
        try:
            self.assigned_staff_combo.clear()
            self.assigned_staff_combo.addItem("Unassigned", "")

            # Check if staff data exists
            if 'staff' in self.data and not self.data['staff'].empty:
                staff_df = self.data['staff']
                active_staff = staff_df[staff_df['status'] == 'Active']

                for _, staff in active_staff.iterrows():
                    staff_name = staff.get('staff_name', '')
                    staff_id = staff.get('staff_id', '')
                    if staff_name:
                        self.assigned_staff_combo.addItem(staff_name, staff_id)

        except Exception as e:
            print(f"Error loading staff options: {e}")

    def open_staff_management(self):
        """Open the staff management dialog"""
        try:
            from modules.staff_management import StaffManagementWidget
            from PySide6.QtWidgets import QDialog, QVBoxLayout

            # Create a dialog to host the staff management widget
            dialog = QDialog(self)
            dialog.setWindowTitle("Staff Management & Task Assignments")
            dialog.setModal(True)
            dialog.resize(1200, 800)

            layout = QVBoxLayout(dialog)

            # Create staff management widget
            staff_widget = StaffManagementWidget(self.data)
            staff_widget.data_changed.connect(self.refresh_data)
            layout.addWidget(staff_widget)

            # Show dialog
            dialog.exec()

        except ImportError:
            QMessageBox.warning(
                self, "Feature Not Available",
                "Staff management module is not available. Please check the installation."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to open staff management: {str(e)}"
            )

    def refresh_data(self):
        """Refresh the cleaning data after staff management changes"""
        try:
            # Reload cleaning data from CSV file to get latest assignments
            import pandas as pd
            import os

            cleaning_file = 'data/cleaning_maintenance.csv'
            if os.path.exists(cleaning_file):
                # Reload from CSV to get the latest data
                self.data['cleaning_maintenance'] = pd.read_csv(cleaning_file)
                self.cleaning_df = self.data['cleaning_maintenance'].copy()

                # Convert date columns properly
                if 'last_completed' in self.cleaning_df.columns:
                    self.cleaning_df['last_completed'] = pd.to_datetime(self.cleaning_df['last_completed'], errors='coerce')
                if 'next_due' in self.cleaning_df.columns:
                    self.cleaning_df['next_due'] = pd.to_datetime(self.cleaning_df['next_due'], errors='coerce')

            # Reload staff options
            self.load_staff_options()

            # Update the task list
            self.update_task_list()

            # Update calendar if it exists
            if hasattr(self, 'calendar'):
                self.highlight_task_dates()

            print(f"Cleaning data refreshed: {len(self.cleaning_df)} tasks loaded")

        except Exception as e:
            print(f"Error refreshing data: {e}")
        
    def setup_schedule_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.schedule_tab)
        
        # Add subheader
        header = QLabel("Cleaning & Maintenance Schedule")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        # Priority filter
        priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All", "High", "Medium", "Low"])
        self.priority_combo.currentIndexChanged.connect(self.update_task_list)
        
        # Status filter
        status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Due", "Upcoming", "Completed"])
        self.status_combo.currentIndexChanged.connect(self.update_task_list)
        
        # Add widgets to filter layout
        filter_layout.addWidget(priority_label)
        filter_layout.addWidget(self.priority_combo)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch(1)
        
        layout.addWidget(filter_widget)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(9)
        self.tasks_table.setHorizontalHeaderLabels([
            "Task", "Assigned Staff", "Frequency", "Last Completed", "Next Due", "Days Left", "Priority", "Schedule Type", "Notes"
        ])

        # Apply universal column resizing functionality
        tasks_default_column_widths = {
            0: 180,  # Task
            1: 120,  # Assigned Staff
            2: 100,  # Frequency
            3: 120,  # Last Completed
            4: 120,  # Next Due
            5: 80,   # Days Left
            6: 80,   # Priority
            7: 100,  # Schedule Type
            8: 200   # Notes
        }

        # Apply column resizing with settings persistence
        self.tasks_table_resizer = apply_universal_column_resizing(
            self.tasks_table,
            'cleaning_tasks_column_settings.json',
            tasks_default_column_widths
        )

        print("✅ Applied universal column resizing to cleaning tasks table")
        layout.addWidget(self.tasks_table)
        
        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.mark_completed_button = QPushButton("Mark as Completed")
        self.mark_completed_button.clicked.connect(self.mark_task_completed)
        buttons_layout.addWidget(self.mark_completed_button)

        self.edit_task_button = QPushButton("Edit Task")
        self.edit_task_button.clicked.connect(self.edit_task)
        buttons_layout.addWidget(self.edit_task_button)

        self.delete_task_button = QPushButton("Delete Task")
        self.delete_task_button.clicked.connect(self.delete_task)
        buttons_layout.addWidget(self.delete_task_button)

        # Add separator
        buttons_layout.addStretch()

        # Staff Management button
        self.staff_mgmt_button = QPushButton("👥 Manage Staff & Assignments")
        self.staff_mgmt_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.staff_mgmt_button.clicked.connect(self.open_staff_management)
        buttons_layout.addWidget(self.staff_mgmt_button)

        layout.addWidget(buttons_widget)
        
        # Update the task list
        self.update_task_list()
        
    def update_task_list(self):
        # Clear the table
        self.tasks_table.setRowCount(0)
        
        # If no data, return
        if len(self.cleaning_df) == 0:
            return
        
        # Make a copy of the dataframe for filtering
        filtered_df = self.cleaning_df.copy()
        
        # Make sure next_due is properly converted to datetime
        try:
            if 'next_due' in filtered_df.columns:
                # Try to convert to datetime if it's not already
                if not pd.api.types.is_datetime64_any_dtype(filtered_df['next_due']):
                    filtered_df['next_due'] = pd.to_datetime(filtered_df['next_due'], errors='coerce')
                
                # Calculate days until due only for valid datetime values
                today = datetime.now().date()
                filtered_df['days_until_due'] = filtered_df['next_due'].apply(
                    lambda x: (x.date() - today).days if pd.notnull(x) else 999  # Use a large number for null dates
                )
            else:
                # If next_due column doesn't exist, set a default value
                filtered_df['days_until_due'] = 999
        except Exception as e:
            # If there's any error, set a default value
            filtered_df['days_until_due'] = 999
        
        # Priority filter
        priority_filter = self.priority_combo.currentText()
        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
        
        # Status filter
        status_filter = self.status_combo.currentText()
        if status_filter == "Due":
            filtered_df = filtered_df[filtered_df['days_until_due'] <= 0]
        elif status_filter == "Upcoming":
            filtered_df = filtered_df[(filtered_df['days_until_due'] > 0) & (filtered_df['days_until_due'] <= 7)]
        elif status_filter == "Completed":
            # Make sure last_completed is properly converted to datetime
            try:
                if 'last_completed' in filtered_df.columns:
                    # Try to convert to datetime if it's not already
                    if not pd.api.types.is_datetime64_any_dtype(filtered_df['last_completed']):
                        filtered_df['last_completed'] = pd.to_datetime(filtered_df['last_completed'], errors='coerce')
                    
                    # Filter for tasks completed in the last 7 days
                    filtered_df = filtered_df[filtered_df['last_completed'].apply(
                        lambda x: x.date() >= (today - timedelta(days=7)) if pd.notnull(x) else False
                    )]
                else:
                    # If last_completed column doesn't exist, return empty dataframe for completed tasks
                    filtered_df = filtered_df.head(0)
            except Exception as e:
                # If there's any error, return empty dataframe for completed tasks
                filtered_df = filtered_df.head(0)
        
        # Sort by days until due
        filtered_df = filtered_df.sort_values('days_until_due')
        
        # Add rows to the table
        self.tasks_table.setRowCount(len(filtered_df))
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            # Task name
            self.tasks_table.setItem(i, 0, QTableWidgetItem(self.safe_string_convert(row['task_name'])))

            # Assigned Staff
            if 'assigned_staff_name' in row and pd.notnull(row['assigned_staff_name']):
                self.tasks_table.setItem(i, 1, QTableWidgetItem(self.safe_string_convert(row['assigned_staff_name'])))
            else:
                self.tasks_table.setItem(i, 1, QTableWidgetItem("Unassigned"))

            # Frequency
            if 'frequency' in row:
                self.tasks_table.setItem(i, 2, QTableWidgetItem(self.safe_string_convert(row['frequency'])))
            else:
                self.tasks_table.setItem(i, 2, QTableWidgetItem(""))

            # Last completed
            if 'last_completed' in row and pd.notnull(row['last_completed']):
                try:
                    last_completed = pd.to_datetime(row['last_completed'])
                    self.tasks_table.setItem(i, 3, QTableWidgetItem(last_completed.strftime('%Y-%m-%d')))
                except:
                    self.tasks_table.setItem(i, 3, QTableWidgetItem(self.safe_string_convert(row['last_completed'])))
            else:
                self.tasks_table.setItem(i, 3, QTableWidgetItem("Never"))

            # Next due
            if 'next_due' in row and pd.notnull(row['next_due']):
                try:
                    next_due = pd.to_datetime(row['next_due'])
                    self.tasks_table.setItem(i, 4, QTableWidgetItem(next_due.strftime('%Y-%m-%d')))
                except:
                    self.tasks_table.setItem(i, 4, QTableWidgetItem(self.safe_string_convert(row['next_due'])))
            else:
                self.tasks_table.setItem(i, 4, QTableWidgetItem("Not scheduled"))

            # Days left
            days_left_item = QTableWidgetItem(self.safe_string_convert(row['days_until_due']))

            # Color code based on days left
            if row['days_until_due'] <= 0:  # Overdue
                days_left_item.setBackground(QColor(255, 0, 0, 100))  # Red
            elif row['days_until_due'] <= 3:  # Due soon
                days_left_item.setBackground(QColor(255, 165, 0, 100))  # Orange
            elif row['days_until_due'] <= 7:  # Due this week
                days_left_item.setBackground(QColor(255, 255, 0, 100))  # Yellow

            self.tasks_table.setItem(i, 5, days_left_item)

            # Priority
            if 'priority' in row:
                priority_value = self.safe_string_convert(row['priority'])
                priority_item = QTableWidgetItem(priority_value)

                # Color code based on priority
                if priority_value == "High":
                    priority_item.setBackground(QColor(255, 0, 0, 100))  # Red
                elif priority_value == "Medium":
                    priority_item.setBackground(QColor(255, 165, 0, 100))  # Orange
                elif priority_value == "Low":
                    priority_item.setBackground(QColor(255, 255, 0, 100))  # Yellow

                self.tasks_table.setItem(i, 6, priority_item)
            else:
                self.tasks_table.setItem(i, 6, QTableWidgetItem(""))

            # Schedule Type
            if 'schedule_type' in row and pd.notnull(row['schedule_type']):
                self.tasks_table.setItem(i, 7, QTableWidgetItem(self.safe_string_convert(row['schedule_type'])))
            else:
                self.tasks_table.setItem(i, 7, QTableWidgetItem("Manual"))

            # Notes
            if 'notes' in row:
                # Use our safe string conversion helper
                notes_str = self.safe_string_convert(row['notes'])
                self.tasks_table.setItem(i, 8, QTableWidgetItem(notes_str))
            else:
                self.tasks_table.setItem(i, 8, QTableWidgetItem(""))
                
    def mark_task_completed(self):
        # Get selected row
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to mark as completed.")
            return
        
        # Get the task name from the first column
        row = selected_items[0].row()
        task_name = self.tasks_table.item(row, 0).text()
        
        # Update the task in the dataframe
        task_index = self.cleaning_df[self.cleaning_df['task_name'] == task_name].index
        if len(task_index) > 0:
            # Set last completed to today
            today = datetime.now()
            self.cleaning_df.loc[task_index, 'last_completed'] = today
            
            # Calculate next due date based on frequency
            if 'frequency' in self.cleaning_df.columns:
                frequency = self.cleaning_df.loc[task_index, 'frequency'].values[0]
                if frequency == "Daily":
                    next_due = today + timedelta(days=1)
                elif frequency == "Weekly":
                    next_due = today + timedelta(days=7)
                elif frequency == "Bi-weekly":
                    next_due = today + timedelta(days=14)
                elif frequency == "Monthly":
                    # Add one month (approximately)
                    next_due = today + timedelta(days=30)
                elif frequency == "Quarterly":
                    next_due = today + timedelta(days=90)
                elif frequency == "Yearly":
                    next_due = today + timedelta(days=365)
                else:
                    next_due = today + timedelta(days=7)  # Default to weekly
                
                self.cleaning_df.loc[task_index, 'next_due'] = next_due
            
            # Update the data dictionary
            self.data['cleaning_maintenance'] = self.cleaning_df
            
            # Save to CSV
            self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
            
            # Update the table
            self.update_task_list()
            
            QMessageBox.information(self, "Success", f"{task_name} marked as completed.")
    
    def edit_task(self):
        # Get selected row
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to edit.")
            return
        
        # Get the task name from the first column
        row = selected_items[0].row()
        task_name = self.tasks_table.item(row, 0).text()
        
        # Get the task from the dataframe
        task = self.cleaning_df[self.cleaning_df['task_name'] == task_name]
        if len(task) == 0:
            QMessageBox.warning(self, "Error", "Task not found.")
            return
        
        # Switch to the add/edit tab
        self.tabs.setCurrentIndex(1)
        
        # Set edit mode
        self.edit_mode = True
        self.original_task_name = task_name
        
        # Populate form with task data
        self.task_name_input.setText(task_name)

        # Set assigned staff
        if 'assigned_staff_name' in task.columns and pd.notnull(task['assigned_staff_name'].values[0]):
            staff_name = task['assigned_staff_name'].values[0]
            index = self.assigned_staff_combo.findText(staff_name)
            if index >= 0:
                self.assigned_staff_combo.setCurrentIndex(index)
            else:
                self.assigned_staff_combo.setCurrentIndex(0)  # Unassigned
        else:
            self.assigned_staff_combo.setCurrentIndex(0)  # Unassigned

        if 'frequency' in task.columns:
            frequency = task['frequency'].values[0]
            index = self.frequency_combo.findText(frequency)
            if index >= 0:
                self.frequency_combo.setCurrentIndex(index)

        # Set schedule type
        if 'schedule_type' in task.columns and pd.notnull(task['schedule_type'].values[0]):
            schedule_type = task['schedule_type'].values[0]
            index = self.schedule_type_combo.findText(schedule_type)
            if index >= 0:
                self.schedule_type_combo.setCurrentIndex(index)
            else:
                self.schedule_type_combo.setCurrentIndex(0)  # Manual
        else:
            self.schedule_type_combo.setCurrentIndex(0)  # Manual
        
        if 'last_completed' in task.columns and pd.notnull(task['last_completed'].values[0]):
            try:
                last_completed = pd.to_datetime(task['last_completed'].values[0])
                self.last_completed_input.setDate(QDate(last_completed.year, last_completed.month, last_completed.day))
            except:
                self.last_completed_input.setDate(QDate.currentDate())
        
        if 'next_due' in task.columns and pd.notnull(task['next_due'].values[0]):
            try:
                next_due = pd.to_datetime(task['next_due'].values[0])
                self.next_due_input.setDate(QDate(next_due.year, next_due.month, next_due.day))
            except:
                self.next_due_input.setDate(QDate.currentDate().addDays(7))
        
        if 'priority' in task.columns:
            priority = task['priority'].values[0]
            index = self.priority_input.findText(priority)
            if index >= 0:
                self.priority_input.setCurrentIndex(index)
        
        if 'notes' in task.columns and pd.notnull(task['notes'].values[0]):
            self.notes_input.setText(task['notes'].values[0])
        
        # Change button text
        self.add_task_button.setText("Update Task")
    
    def delete_task(self):
        # Get selected row
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to delete.")
            return
        
        # Get the task name from the first column
        row = selected_items[0].row()
        task_name = self.tasks_table.item(row, 0).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete {task_name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove the task from the dataframe
            self.cleaning_df = self.cleaning_df[self.cleaning_df['task_name'] != task_name]
            
            # Update the data dictionary
            self.data['cleaning_maintenance'] = self.cleaning_df
            
            # Save to CSV
            self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
            
            # Update the table
            self.update_task_list()
            
            QMessageBox.information(self, "Success", f"{task_name} deleted.")
    
    def setup_add_task_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_task_tab)
        
        # Add subheader
        header = QLabel("Add/Edit Cleaning & Maintenance Task")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Create form
        form_group = QGroupBox("Task Details")
        form_layout = QFormLayout(form_group)
        
        # Task name
        self.task_name_input = QLineEdit()
        form_layout.addRow("Task Name:", self.task_name_input)

        # Assigned Staff
        self.assigned_staff_combo = QComboBox()
        self.load_staff_options()
        form_layout.addRow("Assign to Staff:", self.assigned_staff_combo)

        # Frequency
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Daily", "Weekly", "Bi-weekly", "Monthly", "Quarterly", "Yearly"])
        form_layout.addRow("Frequency:", self.frequency_combo)

        # Schedule Type
        self.schedule_type_combo = QComboBox()
        self.schedule_type_combo.addItems(["Manual", "daily", "weekly", "monthly", "custom"])
        form_layout.addRow("Schedule Type:", self.schedule_type_combo)
        
        # Last completed
        self.last_completed_input = QDateEdit()
        self.last_completed_input.setCalendarPopup(True)
        self.last_completed_input.setDate(QDate.currentDate())
        form_layout.addRow("Last Completed:", self.last_completed_input)
        
        # Next due
        self.next_due_input = QDateEdit()
        self.next_due_input.setCalendarPopup(True)
        self.next_due_input.setDate(QDate.currentDate().addDays(7))
        form_layout.addRow("Next Due:", self.next_due_input)
        
        # Priority
        self.priority_input = QComboBox()
        self.priority_input.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priority:", self.priority_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addWidget(form_group)
        
        # Add button
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_or_update_task)
        layout.addWidget(self.add_task_button)
        
        # Reset button
        self.reset_button = QPushButton("Reset Form")
        self.reset_button.clicked.connect(self.reset_form)
        layout.addWidget(self.reset_button)
        
        # Add stretch to push form to the top
        layout.addStretch(1)
    
    def add_or_update_task(self):
        # Get form values
        task_name = self.task_name_input.text()
        assigned_staff_name = self.assigned_staff_combo.currentText()
        assigned_staff_id = self.assigned_staff_combo.currentData()
        frequency = self.frequency_combo.currentText()
        schedule_type = self.schedule_type_combo.currentText()
        last_completed = self.last_completed_input.date().toString("yyyy-MM-dd")
        next_due = self.next_due_input.date().toString("yyyy-MM-dd")
        priority = self.priority_input.currentText()
        notes = self.notes_input.toPlainText()
        
        # Validate input
        if not task_name:
            QMessageBox.warning(self, "Input Error", "Please enter a task name.")
            return
        
        # Check if task name already exists (for new tasks)
        if not self.edit_mode and task_name in self.cleaning_df['task_name'].values:
            QMessageBox.warning(self, "Input Error", f"A task named '{task_name}' already exists.")
            return
        
        # Create new task record or update existing
        if self.edit_mode:
            # Update existing task
            task_index = self.cleaning_df[self.cleaning_df['task_name'] == self.original_task_name].index
            if len(task_index) > 0:
                self.cleaning_df.loc[task_index, 'task_name'] = task_name
                self.cleaning_df.loc[task_index, 'assigned_staff_name'] = assigned_staff_name if assigned_staff_name != "Unassigned" else ""
                self.cleaning_df.loc[task_index, 'assigned_staff_id'] = assigned_staff_id if assigned_staff_id else ""
                self.cleaning_df.loc[task_index, 'frequency'] = frequency
                self.cleaning_df.loc[task_index, 'schedule_type'] = schedule_type
                self.cleaning_df.loc[task_index, 'last_completed'] = last_completed
                self.cleaning_df.loc[task_index, 'next_due'] = next_due
                self.cleaning_df.loc[task_index, 'priority'] = priority
                self.cleaning_df.loc[task_index, 'notes'] = notes
                
                # Update the data dictionary
                self.data['cleaning_maintenance'] = self.cleaning_df
                
                # Save to CSV
                self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
                
                # Update the table
                self.update_task_list()
                
                # Reset form and edit mode
                self.reset_form()
                
                # Show success message
                QMessageBox.information(self, "Success", f"{task_name} updated.")
                
                # Switch back to schedule tab
                self.tabs.setCurrentIndex(0)
        else:
            # Create new task
            new_task = pd.DataFrame({
                'task_name': [task_name],
                'assigned_staff_name': [assigned_staff_name if assigned_staff_name != "Unassigned" else ""],
                'assigned_staff_id': [assigned_staff_id if assigned_staff_id else ""],
                'frequency': [frequency],
                'schedule_type': [schedule_type],
                'last_completed': [last_completed],
                'next_due': [next_due],
                'priority': [priority],
                'notes': [notes]
            })
            
            # Add to cleaning dataframe
            self.cleaning_df = pd.concat([self.cleaning_df, new_task], ignore_index=True)
            
            # Update the data dictionary
            self.data['cleaning_maintenance'] = self.cleaning_df
            
            # Save to CSV
            self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
            
            # Update the table
            self.update_task_list()
            
            # Reset form
            self.reset_form()
            
            # Show success message
            QMessageBox.information(self, "Success", f"{task_name} added.")
    
    def reset_form(self):
        self.task_name_input.clear()
        self.assigned_staff_combo.setCurrentIndex(0)  # Reset to "Unassigned"
        self.frequency_combo.setCurrentIndex(0)
        self.schedule_type_combo.setCurrentIndex(0)  # Reset to "Manual"
        self.last_completed_input.setDate(QDate.currentDate())
        self.next_due_input.setDate(QDate.currentDate().addDays(7))
        self.priority_input.setCurrentIndex(0)
        self.notes_input.clear()
        
        # Reset edit mode
        if self.edit_mode:
            self.edit_mode = False
            self.original_task_name = None
            self.add_task_button.setText("Add Task")
            
    def setup_calendar_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.calendar_tab)
        
        # Create a horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Calendar
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        
        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumWidth(400)
        self.calendar.clicked.connect(self.show_tasks_for_date)
        calendar_layout.addWidget(self.calendar)
        
        # Highlight task dates
        try:
            self.highlight_task_dates()
        except Exception as e:
            print(f"Error highlighting task dates: {e}")
        
        splitter.addWidget(calendar_widget)
        
        # Right side - Tasks for selected date
        tasks_widget = QWidget()
        self.date_tasks_layout = QVBoxLayout(tasks_widget)
        
        # Date header
        self.date_header = QLabel("Tasks for " + QDate.currentDate().toString("yyyy-MM-dd"))
        self.date_header.setFont(QFont("Arial", 12, QFont.Bold))
        self.date_tasks_layout.addWidget(self.date_header)
        
        splitter.addWidget(tasks_widget)
        
        # Show tasks for current date
        self.show_tasks_for_date(QDate.currentDate())
    
    def highlight_task_dates(self):
        try:
            # Clear existing formatting first
            self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

            # Make sure next_due is properly converted to datetime
            if 'next_due' in self.cleaning_df.columns:
                if not pd.api.types.is_datetime64_any_dtype(self.cleaning_df['next_due']):
                    self.cleaning_df['next_due'] = pd.to_datetime(self.cleaning_df['next_due'], errors='coerce')

                current_date = datetime.now().date()
                highlighted_dates = set()  # Track highlighted dates to avoid conflicts

                for _, task in self.cleaning_df.iterrows():
                    schedule_type = task.get('schedule_type', '')

                    if schedule_type == 'daily_rotation':
                        # Highlight daily rotation dates
                        self.highlight_daily_rotation_dates(task, highlighted_dates, current_date)
                    else:
                        # Handle regular tasks (existing logic)
                        next_due_str = task.get('next_due')
                        if pd.notnull(next_due_str):
                            next_due = pd.to_datetime(next_due_str, errors='coerce')
                            if pd.notnull(next_due):
                                date = next_due.date()
                                date_key = (date.year, date.month, date.day)

                                if date_key not in highlighted_dates:
                                    highlighted_dates.add(date_key)
                                    qdate = QDate(date.year, date.month, date.day)
                                    text_format = QTextCharFormat()

                                    # Color based on priority and due date
                                    priority = task.get('priority', 'Medium')
                                    days_diff = (date - current_date).days

                                    if days_diff < 0:
                                        # Overdue - Red
                                        text_format.setBackground(QColor(255, 200, 200))
                                    elif days_diff == 0:
                                        # Due today - Orange
                                        text_format.setBackground(QColor(255, 220, 150))
                                    elif days_diff <= 3:
                                        # Due soon - Yellow
                                        text_format.setBackground(QColor(255, 255, 200))
                                    elif priority == 'High':
                                        # High priority - Light red
                                        text_format.setBackground(QColor(255, 230, 230))
                                    else:
                                        # Regular tasks - Light blue
                                        text_format.setBackground(QColor(230, 240, 255))

                                    self.calendar.setDateTextFormat(qdate, text_format)

        except Exception as e:
            # If there's any error, just skip highlighting
            print(f"Error highlighting task dates: {e}")
            pass

    def highlight_daily_rotation_dates(self, task, highlighted_dates, current_date):
        """Highlight dates for daily rotation tasks"""
        try:
            # Get the task start date
            next_due_str = task.get('next_due')
            if pd.isna(next_due_str) or not next_due_str:
                return

            start_date = pd.to_datetime(next_due_str, errors='coerce')
            if pd.isna(start_date):
                return

            start_date = start_date.date()

            # Highlight dates for the next 30 days from start date
            from datetime import timedelta
            for days_offset in range(30):
                highlight_date = start_date + timedelta(days=days_offset)

                # Skip dates too far in the past or future
                if highlight_date < current_date - timedelta(days=7) or highlight_date > current_date + timedelta(days=60):
                    continue

                # Create QDate safely
                try:
                    qdate = QDate(highlight_date.year, highlight_date.month, highlight_date.day)
                    if not qdate.isValid():
                        continue

                    # Skip if already highlighted
                    date_key = (highlight_date.year, highlight_date.month, highlight_date.day)
                    if date_key in highlighted_dates:
                        continue
                    highlighted_dates.add(date_key)

                    # Create format for highlighting daily rotation
                    text_format = QTextCharFormat()

                    # Special color scheme for daily rotation tasks
                    days_diff = (highlight_date - current_date).days

                    if days_diff < 0:
                        # Past dates - Light purple
                        text_format.setBackground(QColor(230, 220, 255))
                    elif days_diff == 0:
                        # Today - Bright purple
                        text_format.setBackground(QColor(200, 150, 255))
                    else:
                        # Future dates - Light lavender
                        text_format.setBackground(QColor(240, 230, 255))

                    # Apply the format
                    self.calendar.setDateTextFormat(qdate, text_format)

                except Exception as date_error:
                    continue

        except Exception as e:
            print(f"Error highlighting daily rotation dates: {e}")
    
    def show_tasks_for_date(self, date):
        # Clear the tasks layout
        while self.date_tasks_layout.count():
            item = self.date_tasks_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Update date header
        self.date_header = QLabel("Tasks for " + date.toString("yyyy-MM-dd"))
        self.date_header.setFont(QFont("Arial", 12, QFont.Bold))
        self.date_tasks_layout.addWidget(self.date_header)

        # Filter tasks for the selected date
        try:
            # Make sure next_due is properly converted to datetime
            if 'next_due' in self.cleaning_df.columns:
                if not pd.api.types.is_datetime64_any_dtype(self.cleaning_df['next_due']):
                    self.cleaning_df['next_due'] = pd.to_datetime(self.cleaning_df['next_due'], errors='coerce')

                # Convert QDate to Python date
                py_date = datetime(date.year(), date.month(), date.day()).date()

                # Initialize lists for different types of tasks
                tasks_due = pd.DataFrame()
                daily_rotation_tasks = []

                # Check for daily rotation tasks
                for _, task in self.cleaning_df.iterrows():
                    schedule_type = task.get('schedule_type', '')

                    if schedule_type == 'daily_rotation':
                        # Check if this daily rotation task should be shown for the selected date
                        if self.should_show_daily_rotation_task(task, py_date):
                            # Calculate which staff member is assigned for this date
                            assigned_staff = self.get_staff_for_date(task, py_date)

                            # Create a modified task with the correct staff for this date
                            task_for_date = task.copy()
                            task_for_date['assigned_staff_name'] = assigned_staff
                            task_for_date['rotation_date'] = py_date.strftime('%Y-%m-%d')
                            daily_rotation_tasks.append(task_for_date)
                    else:
                        # Handle regular tasks (existing logic)
                        if pd.notnull(task.get('next_due')):
                            task_due_date = pd.to_datetime(task.get('next_due'), errors='coerce')
                            if pd.notnull(task_due_date) and task_due_date.date() == py_date:
                                if tasks_due.empty:
                                    tasks_due = pd.DataFrame([task])
                                else:
                                    tasks_due = pd.concat([tasks_due, pd.DataFrame([task])], ignore_index=True)

                # Filter tasks allotted/completed on the selected date (last_completed)
                tasks_allotted = pd.DataFrame()
                if 'last_completed' in self.cleaning_df.columns:
                    if not pd.api.types.is_datetime64_any_dtype(self.cleaning_df['last_completed']):
                        self.cleaning_df['last_completed'] = pd.to_datetime(self.cleaning_df['last_completed'], errors='coerce')
                    tasks_allotted = self.cleaning_df[self.cleaning_df['last_completed'].dt.date == py_date]
                else:
                    tasks_allotted = pd.DataFrame()

                # Create sections for due tasks, daily rotation tasks, and allotted tasks
                self.create_due_tasks_section(tasks_due, date)
                self.create_daily_rotation_section(daily_rotation_tasks, date)
                self.create_allotted_tasks_section(tasks_allotted, date)
            else:
                no_tasks_label = QLabel("No task data available.")
                no_tasks_label.setAlignment(Qt.AlignCenter)
                self.date_tasks_layout.addWidget(no_tasks_label)
        except Exception as e:
            error_label = QLabel(f"Error loading tasks: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            self.date_tasks_layout.addWidget(error_label)

    def create_due_tasks_section(self, tasks_due, date):
        """Create section for tasks due on the selected date"""
        # Due Tasks Section
        due_section_label = QLabel("📅 Tasks Due")
        due_section_label.setFont(QFont("Arial", 11, QFont.Bold))
        due_section_label.setStyleSheet("color: #d32f2f; margin-top: 10px; margin-bottom: 5px;")
        self.date_tasks_layout.addWidget(due_section_label)

        if len(tasks_due) > 0:
            # Create a table for due tasks
            due_tasks_table = QTableWidget()
            due_tasks_table.setColumnCount(3)
            due_tasks_table.setHorizontalHeaderLabels(["Task", "Priority", "Notes"])
            due_tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            due_tasks_table.setMaximumHeight(150)  # Limit height

            # Add rows to the table
            due_tasks_table.setRowCount(len(tasks_due))
            for i, (_, row) in enumerate(tasks_due.iterrows()):
                due_tasks_table.setItem(i, 0, QTableWidgetItem(self.safe_string_convert(row['task_name'])))

                if 'priority' in row:
                    due_tasks_table.setItem(i, 1, QTableWidgetItem(self.safe_string_convert(row['priority'])))
                else:
                    due_tasks_table.setItem(i, 1, QTableWidgetItem(""))

                if 'notes' in row:
                    notes_str = self.safe_string_convert(row['notes'])
                    due_tasks_table.setItem(i, 2, QTableWidgetItem(notes_str))
                else:
                    due_tasks_table.setItem(i, 2, QTableWidgetItem(""))

                # Color code based on priority
                if 'priority' in row:
                    priority_value = self.safe_string_convert(row['priority'])
                    color = QColor(255, 255, 255)  # Default white
                    if priority_value == 'High':
                        color = QColor(255, 200, 200)  # Light red
                    elif priority_value == 'Medium':
                        color = QColor(255, 255, 200)  # Light yellow

                    # Apply color to row
                    for j in range(due_tasks_table.columnCount()):
                        due_tasks_table.item(i, j).setBackground(color)

            self.date_tasks_layout.addWidget(due_tasks_table)

            # Add "Mark as Completed" button for due tasks
            complete_button = QPushButton("Mark Selected Task as Completed")
            complete_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            complete_button.clicked.connect(self.mark_calendar_task_completed)
            self.date_tasks_layout.addWidget(complete_button)
        else:
            no_due_tasks_label = QLabel(f"No tasks due on {date.toString('yyyy-MM-dd')}.")
            no_due_tasks_label.setAlignment(Qt.AlignCenter)
            no_due_tasks_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
            self.date_tasks_layout.addWidget(no_due_tasks_label)

    def create_allotted_tasks_section(self, tasks_allotted, date):
        """Create section for tasks allotted/completed on the selected date"""
        # Allotted Tasks Section
        allotted_section_label = QLabel("✅ Tasks Completed/Allotted")
        allotted_section_label.setFont(QFont("Arial", 11, QFont.Bold))
        allotted_section_label.setStyleSheet("color: #388e3c; margin-top: 15px; margin-bottom: 5px;")
        self.date_tasks_layout.addWidget(allotted_section_label)

        if len(tasks_allotted) > 0:
            # Create a table for allotted tasks
            allotted_tasks_table = QTableWidget()
            allotted_tasks_table.setColumnCount(4)
            allotted_tasks_table.setHorizontalHeaderLabels(["Task", "Priority", "Completed Time", "Notes"])
            allotted_tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            allotted_tasks_table.setMaximumHeight(150)  # Limit height

            # Add rows to the table
            allotted_tasks_table.setRowCount(len(tasks_allotted))
            for i, (_, row) in enumerate(tasks_allotted.iterrows()):
                allotted_tasks_table.setItem(i, 0, QTableWidgetItem(self.safe_string_convert(row['task_name'])))

                if 'priority' in row:
                    allotted_tasks_table.setItem(i, 1, QTableWidgetItem(self.safe_string_convert(row['priority'])))
                else:
                    allotted_tasks_table.setItem(i, 1, QTableWidgetItem(""))

                # Show completion time
                if 'last_completed' in row and pd.notnull(row['last_completed']):
                    completed_time = pd.to_datetime(row['last_completed']).strftime('%H:%M')
                    allotted_tasks_table.setItem(i, 2, QTableWidgetItem(completed_time))
                else:
                    allotted_tasks_table.setItem(i, 2, QTableWidgetItem(""))

                if 'notes' in row:
                    notes_str = self.safe_string_convert(row['notes'])
                    allotted_tasks_table.setItem(i, 3, QTableWidgetItem(notes_str))
                else:
                    allotted_tasks_table.setItem(i, 3, QTableWidgetItem(""))

                # Color code completed tasks with light green background
                color = QColor(200, 255, 200)  # Light green
                for j in range(allotted_tasks_table.columnCount()):
                    allotted_tasks_table.item(i, j).setBackground(color)

            self.date_tasks_layout.addWidget(allotted_tasks_table)

            # Add info label
            info_label = QLabel(f"✅ {len(tasks_allotted)} task(s) completed on this date")
            info_label.setStyleSheet("color: #388e3c; font-weight: bold; padding: 5px;")
            info_label.setAlignment(Qt.AlignCenter)
            self.date_tasks_layout.addWidget(info_label)
        else:
            no_allotted_tasks_label = QLabel(f"No tasks completed on {date.toString('yyyy-MM-dd')}.")
            no_allotted_tasks_label.setAlignment(Qt.AlignCenter)
            no_allotted_tasks_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
            self.date_tasks_layout.addWidget(no_allotted_tasks_label)
    
    def mark_calendar_task_completed(self):
        # Get the tasks table from the layout
        tasks_table = None
        for i in range(self.date_tasks_layout.count()):
            widget = self.date_tasks_layout.itemAt(i).widget()
            if isinstance(widget, QTableWidget):
                tasks_table = widget
                break
        
        if tasks_table:
            selected_items = tasks_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a task to mark as completed.")
                return
            
            # Get the selected row index
            row = selected_items[0].row()
            task_name = tasks_table.item(row, 0).text()
            
            # Update the task in the dataframe
            task_index = self.cleaning_df[self.cleaning_df['task_name'] == task_name].index
            if len(task_index) > 0:
                # Set last completed to today
                today = datetime.now()
                self.cleaning_df.loc[task_index, 'last_completed'] = today
                
                # Calculate next due date based on frequency
                if 'frequency' in self.cleaning_df.columns:
                    frequency = self.cleaning_df.loc[task_index, 'frequency'].values[0]
                    if frequency == "Daily":
                        next_due = today + timedelta(days=1)
                    elif frequency == "Weekly":
                        next_due = today + timedelta(days=7)
                    elif frequency == "Bi-weekly":
                        next_due = today + timedelta(days=14)
                    elif frequency == "Monthly":
                        # Add one month (approximately)
                        next_due = today + timedelta(days=30)
                    elif frequency == "Quarterly":
                        next_due = today + timedelta(days=90)
                    elif frequency == "Yearly":
                        next_due = today + timedelta(days=365)
                    else:
                        next_due = today + timedelta(days=7)  # Default to weekly
                    
                    self.cleaning_df.loc[task_index, 'next_due'] = next_due
                
                # Update the data dictionary
                self.data['cleaning_maintenance'] = self.cleaning_df
                
                # Save to CSV
                self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
                
                # Update the table
                self.update_task_list()
                
                # Update calendar
                self.highlight_task_dates()
                self.show_tasks_for_date(self.calendar.selectedDate())
                
                QMessageBox.information(self, "Success", f"{task_name} marked as completed.")

    def create_daily_rotation_section(self, daily_rotation_tasks, date):
        """Create section for daily rotation tasks"""
        if not daily_rotation_tasks:
            return

        # Daily Rotation Tasks Section
        rotation_section_label = QLabel("🔄 Daily Rotation Tasks")
        rotation_section_label.setFont(QFont("Arial", 11, QFont.Bold))
        rotation_section_label.setStyleSheet("color: #7b1fa2; margin-top: 10px; margin-bottom: 5px;")
        self.date_tasks_layout.addWidget(rotation_section_label)

        # Create a table for daily rotation tasks
        rotation_tasks_table = QTableWidget()
        rotation_tasks_table.setColumnCount(4)
        rotation_tasks_table.setHorizontalHeaderLabels(["Task", "Assigned Staff", "Priority", "Notes"])
        rotation_tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        rotation_tasks_table.setMaximumHeight(150)  # Limit height

        # Add rows to the table
        rotation_tasks_table.setRowCount(len(daily_rotation_tasks))
        for i, task in enumerate(daily_rotation_tasks):
            rotation_tasks_table.setItem(i, 0, QTableWidgetItem(self.safe_string_convert(task.get('task_name', ''))))
            rotation_tasks_table.setItem(i, 1, QTableWidgetItem(self.safe_string_convert(task.get('assigned_staff_name', ''))))
            rotation_tasks_table.setItem(i, 2, QTableWidgetItem(self.safe_string_convert(task.get('priority', ''))))

            # Enhanced notes for rotation
            notes = self.safe_string_convert(task.get('notes', ''))
            rotation_info = task.get('multiple_staff_config', '')
            if rotation_info:
                notes += f" | Rotation: {rotation_info}"
            rotation_tasks_table.setItem(i, 3, QTableWidgetItem(notes))

            # Color code daily rotation tasks with light purple background
            color = QColor(240, 230, 255)  # Light purple
            for j in range(rotation_tasks_table.columnCount()):
                rotation_tasks_table.item(i, j).setBackground(color)

        self.date_tasks_layout.addWidget(rotation_tasks_table)

        # Add info label
        info_label = QLabel(f"🔄 {len(daily_rotation_tasks)} daily rotation task(s) assigned for this date")
        info_label.setStyleSheet("color: #7b1fa2; font-weight: bold; padding: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        self.date_tasks_layout.addWidget(info_label)

    def should_show_daily_rotation_task(self, task, date):
        """Check if a daily rotation task should be shown for the given date"""
        try:
            # Get the task start date (next_due date)
            next_due_str = task.get('next_due')
            if pd.isna(next_due_str) or not next_due_str:
                return False

            # Parse start date
            start_date = pd.to_datetime(next_due_str, errors='coerce')
            if pd.isna(start_date):
                return False

            # Daily rotation tasks are shown from the start date onwards
            return date >= start_date.date()

        except Exception as e:
            print(f"Error checking daily rotation task: {e}")
            return False

    def get_staff_for_date(self, task, date):
        """Get the staff member assigned for a specific date in daily rotation"""
        try:
            # Get rotation order
            rotation_order = task.get('rotation_order', '')
            if not rotation_order:
                return task.get('assigned_staff_name', 'Unassigned')

            # Parse staff IDs from rotation order
            staff_ids = [int(x.strip()) for x in rotation_order.split(';') if x.strip().isdigit()]
            if not staff_ids:
                return task.get('assigned_staff_name', 'Unassigned')

            # Get the task start date
            next_due_str = task.get('next_due')
            if pd.isna(next_due_str) or not next_due_str:
                return task.get('assigned_staff_name', 'Unassigned')

            start_date = pd.to_datetime(next_due_str, errors='coerce')
            if pd.isna(start_date):
                return task.get('assigned_staff_name', 'Unassigned')

            # Calculate days since start date
            days_since_start = (date - start_date.date()).days

            # Determine which staff member is assigned (rotation index)
            rotation_index = days_since_start % len(staff_ids)
            assigned_staff_id = staff_ids[rotation_index]

            # Get staff name from ID
            if 'staff' in self.data:
                staff_df = self.data['staff']
                staff_row = staff_df[staff_df['staff_id'] == assigned_staff_id]
                if not staff_row.empty:
                    return staff_row.iloc[0]['staff_name']

            return f"Staff {assigned_staff_id}"

        except Exception as e:
            print(f"Error getting staff for date: {e}")
            return task.get('assigned_staff_name', 'Unassigned')
