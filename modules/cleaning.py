from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                             QMessageBox, QHeaderView, QSplitter, QCalendarWidget)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import calendar
import os

class CleaningWidget(QWidget):
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
        self.tasks_table.setColumnCount(7)
        self.tasks_table.setHorizontalHeaderLabels([
            "Task", "Frequency", "Last Completed", "Next Due", "Days Left", "Priority", "Notes"
        ])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        
        layout.addWidget(buttons_widget)
        
        # Due tasks section
        due_tasks_group = QGroupBox("Tasks Due Today")
        due_tasks_layout = QVBoxLayout(due_tasks_group)
        self.due_tasks_label = QLabel()
        due_tasks_layout.addWidget(self.due_tasks_label)
        layout.addWidget(due_tasks_group)
        
        # Update the task list
        self.update_task_list()
    
    def update_task_list(self):
        # Apply filters
        filtered_df = self.cleaning_df.copy()
        
        # Make sure date columns are datetime
        if 'last_completed' in filtered_df.columns:
            filtered_df['last_completed'] = pd.to_datetime(filtered_df['last_completed'])
        if 'next_due' in filtered_df.columns:
            filtered_df['next_due'] = pd.to_datetime(filtered_df['next_due'])
        
        # Calculate days until due
        today = datetime.now().date()
        
        # Make sure next_due is properly converted to datetime
        try:
            if 'next_due' in filtered_df.columns:
                # Try to convert to datetime if it's not already
                if not pd.api.types.is_datetime64_any_dtype(filtered_df['next_due']):
                    filtered_df['next_due'] = pd.to_datetime(filtered_df['next_due'], errors='coerce')
                
                # Calculate days until due only for valid datetime values
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
        
        # Update table
        self.tasks_table.setRowCount(len(filtered_df))
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            self.tasks_table.setItem(i, 0, QTableWidgetItem(row['task_name']))
            self.tasks_table.setItem(i, 1, QTableWidgetItem(row['frequency']))
            self.tasks_table.setItem(i, 2, QTableWidgetItem(str(row['last_completed'].date())))
            self.tasks_table.setItem(i, 3, QTableWidgetItem(str(row['next_due'].date())))
            self.tasks_table.setItem(i, 4, QTableWidgetItem(str(row['days_until_due'])))
            self.tasks_table.setItem(i, 5, QTableWidgetItem(row['priority']))
            self.tasks_table.setItem(i, 6, QTableWidgetItem(row['notes']))
            
            # Color code based on days until due
            color = QColor(255, 255, 255)  # Default white
            if row['days_until_due'] <= 0:
                color = QColor(255, 200, 200)  # Light red for overdue
            elif row['days_until_due'] <= 3:
                color = QColor(255, 255, 200)  # Light yellow for soon due
            
            # Apply color to row
            for j in range(self.tasks_table.columnCount()):
                self.tasks_table.item(i, j).setBackground(color)
        
        # Update due tasks label
        due_tasks = filtered_df[filtered_df['days_until_due'] <= 0]
        if len(due_tasks) > 0:
            due_tasks_text = "<ul>"
            for _, row in due_tasks.iterrows():
                due_tasks_text += f"<li><b>{row['task_name']}</b> ({row['priority']} priority)</li>"
            due_tasks_text += "</ul>"
            self.due_tasks_label.setText(due_tasks_text)
            self.due_tasks_label.setStyleSheet("color: red;")
        else:
            self.due_tasks_label.setText("No tasks due today.")
            self.due_tasks_label.setStyleSheet("color: green;")
    
    def mark_task_completed(self):
        selected_rows = self.tasks_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a task to mark as completed.")
            return
        
        # Get the selected row index
        row = selected_rows[0].row()
        task_name = self.tasks_table.item(row, 0).text()
        
        # Update the task in the dataframe
        task_index = self.cleaning_df[self.cleaning_df['task_name'] == task_name].index
        if len(task_index) > 0:
            # Set last completed to today
            today = datetime.now()
            self.cleaning_df.loc[task_index, 'last_completed'] = today
            
            # Calculate next due date based on frequency
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
        selected_rows = self.tasks_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a task to edit.")
            return
        
        # Get the selected row index
        row = selected_rows[0].row()
        task_name = self.tasks_table.item(row, 0).text()
        
        # Find the task in the dataframe
        task = self.cleaning_df[self.cleaning_df['task_name'] == task_name]
        if len(task) > 0:
            # Switch to add/edit tab
            self.tabs.setCurrentIndex(1)
            
            # Populate form with task data
            self.task_name_input.setText(task['task_name'].values[0])
            index = self.frequency_combo.findText(task['frequency'].values[0])
            if index >= 0:
                self.frequency_combo.setCurrentIndex(index)
            
            last_completed = pd.to_datetime(task['last_completed'].values[0])
            self.last_completed_input.setDate(QDate(
                last_completed.year, 
                last_completed.month, 
                last_completed.day
            ))
            
            next_due = pd.to_datetime(task['next_due'].values[0])
            self.next_due_input.setDate(QDate(
                next_due.year, 
                next_due.month, 
                next_due.day
            ))
            
            index = self.priority_input.findText(task['priority'].values[0])
            if index >= 0:
                self.priority_input.setCurrentIndex(index)
            
            self.notes_input.setText(task['notes'].values[0])
            
            # Set editing mode
            self.edit_mode = True
            self.original_task_name = task_name
            self.add_task_button.setText("Update Task")
    
    def delete_task(self):
        selected_rows = self.tasks_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a task to delete.")
            return
        
        # Get the selected row index
        row = selected_rows[0].row()
        task_name = self.tasks_table.item(row, 0).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the task '{task_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove from the dataframe
            self.cleaning_df = self.cleaning_df[self.cleaning_df['task_name'] != task_name]
            
            # Update the data dictionary
            self.data['cleaning_maintenance'] = self.cleaning_df
            
            # Save to CSV
            self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
            
            # Update the table
            self.update_task_list()
            
            QMessageBox.information(self, "Success", f"Task '{task_name}' has been deleted.")
    
    def setup_add_task_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_task_tab)
        
        # Add subheader
        header = QLabel("Add/Edit Cleaning & Maintenance Task")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Create form for adding tasks
        form_group = QGroupBox("Task Details")
        form_layout = QFormLayout(form_group)
        
        # Task name
        self.task_name_input = QLineEdit()
        form_layout.addRow("Task Name:", self.task_name_input)
        
        # Frequency
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Daily", "Weekly", "Bi-weekly", "Monthly", "Quarterly", "Yearly"])
        form_layout.addRow("Frequency:", self.frequency_combo)
        
        # Last completed
        self.last_completed_input = QDateEdit()
        self.last_completed_input.setCalendarPopup(True)
        self.last_completed_input.setDate(QDate.currentDate())
        form_layout.addRow("Last Completed:", self.last_completed_input)
        
        # Next due
        self.next_due_input = QDateEdit()
        self.next_due_input.setCalendarPopup(True)
        self.next_due_input.setDate(QDate.currentDate().addDays(7))  # Default to one week from now
        form_layout.addRow("Next Due:", self.next_due_input)
        
        # Priority
        self.priority_input = QComboBox()
        self.priority_input.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priority:", self.priority_input)
        
        # Notes
        self.notes_input = QLineEdit()
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
        
        # Initialize edit mode flag
        self.edit_mode = False
        self.original_task_name = None
    
    def add_or_update_task(self):
        # Get form values
        task_name = self.task_name_input.text()
        frequency = self.frequency_combo.currentText()
        last_completed = self.last_completed_input.date().toString("yyyy-MM-dd")
        next_due = self.next_due_input.date().toString("yyyy-MM-dd")
        priority = self.priority_input.currentText()
        notes = self.notes_input.text()
        
        # Validate input
        if not task_name:
            QMessageBox.warning(self, "Input Error", "Please enter a task name.")
            return
        
        if self.edit_mode:
            # Update existing task
            task_index = self.cleaning_df[self.cleaning_df['task_name'] == self.original_task_name].index
            if len(task_index) > 0:
                self.cleaning_df.loc[task_index, 'task_name'] = task_name
                self.cleaning_df.loc[task_index, 'frequency'] = frequency
                self.cleaning_df.loc[task_index, 'last_completed'] = last_completed
                self.cleaning_df.loc[task_index, 'next_due'] = next_due
                self.cleaning_df.loc[task_index, 'priority'] = priority
                self.cleaning_df.loc[task_index, 'notes'] = notes
                
                # Reset edit mode
                self.edit_mode = False
                self.original_task_name = None
                self.add_task_button.setText("Add Task")
                
                QMessageBox.information(self, "Success", f"Task '{task_name}' has been updated.")
        else:
            # Check if task name already exists
            if task_name in self.cleaning_df['task_name'].values:
                QMessageBox.warning(self, "Input Error", f"A task named '{task_name}' already exists.")
                return
            
            # Generate new task ID
            new_task_id = self.cleaning_df['task_id'].max() + 1 if len(self.cleaning_df) > 0 else 1
            
            # Create new task record
            new_task = pd.DataFrame({
                'task_id': [new_task_id],
                'task_name': [task_name],
                'frequency': [frequency],
                'last_completed': [last_completed],
                'next_due': [next_due],
                'priority': [priority],
                'notes': [notes]
            })
            
            # Add to cleaning dataframe
            self.cleaning_df = pd.concat([self.cleaning_df, new_task], ignore_index=True)
            
            QMessageBox.information(self, "Success", f"Task '{task_name}' has been added.")
        
        # Update the data dictionary
        self.data['cleaning_maintenance'] = self.cleaning_df
        
        # Save to CSV
        self.cleaning_df.to_csv('data/cleaning_maintenance.csv', index=False)
        
        # Reset form
        self.reset_form()
        
        # Update task list
        self.update_task_list()
        
        # Update calendar
        self.setup_calendar_tab()
    
    def reset_form(self):
        self.task_name_input.clear()
        self.frequency_combo.setCurrentIndex(0)
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
        # Clear the tab
        while self.calendar_tab.layout():
            old_layout = self.calendar_tab.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old_layout)
        
        # Create layout for the tab
        layout = QVBoxLayout(self.calendar_tab)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate.currentDate().addMonths(-1))
        self.calendar.setMaximumDate(QDate.currentDate().addMonths(3))
        self.calendar.clicked.connect(self.show_tasks_for_date)
        layout.addWidget(self.calendar)
        
        # Highlight dates with tasks
        self.highlight_task_dates()
        
        # Tasks for selected date
        self.date_tasks_group = QGroupBox("Tasks for Selected Date")
        self.date_tasks_layout = QVBoxLayout(self.date_tasks_group)
        layout.addWidget(self.date_tasks_group)
        
        # Show tasks for current date
        self.show_tasks_for_date(QDate.currentDate())
    
def reset_form(self):
    self.task_name_input.clear()
    self.frequency_combo.setCurrentIndex(0)
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
    # Clear the tab
    while self.calendar_tab.layout():
        old_layout = self.calendar_tab.layout()
        while old_layout.count():
            item = old_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Convert QDate to Python date
        selected_date = date.toPython()
        
        # Find tasks due on the selected date
        if 'next_due' in self.cleaning_df.columns:
            self.cleaning_df['next_due'] = pd.to_datetime(self.cleaning_df['next_due'])
            tasks_due = self.cleaning_df[self.cleaning_df['next_due'].dt.date == selected_date]
            
            if len(tasks_due) > 0:
                # Create a table for tasks
                tasks_table = QTableWidget()
                tasks_table.setColumnCount(3)
                tasks_table.setHorizontalHeaderLabels(["Task", "Priority", "Notes"])
                tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
                tasks_table.setRowCount(len(tasks_due))
                for i, (_, row) in enumerate(tasks_due.iterrows()):
                    tasks_table.setItem(i, 0, QTableWidgetItem(row['task_name']))
                    tasks_table.setItem(i, 1, QTableWidgetItem(row['priority']))
                    tasks_table.setItem(i, 2, QTableWidgetItem(row['notes']))
                    
                    # Color code based on priority
                    color = QColor(255, 255, 255)  # Default white
                    if row['priority'] == 'High':
                        color = QColor(255, 200, 200)  # Light red
                    elif row['priority'] == 'Medium':
                        color = QColor(255, 255, 200)  # Light yellow
                    
                    # Apply color to row
                    for j in range(tasks_table.columnCount()):
                        tasks_table.item(i, j).setBackground(color)
                
                self.date_tasks_layout.addWidget(tasks_table)
                
                # Add "Mark as Completed" button
                complete_button = QPushButton("Mark Selected Task as Completed")
                complete_button.clicked.connect(self.mark_calendar_task_completed)
                self.date_tasks_layout.addWidget(complete_button)
            else:
                no_tasks_label = QLabel(f"No tasks due on {date.toString('yyyy-MM-dd')}.")
                no_tasks_label.setAlignment(Qt.AlignCenter)
                self.date_tasks_layout.addWidget(no_tasks_label)
    
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
