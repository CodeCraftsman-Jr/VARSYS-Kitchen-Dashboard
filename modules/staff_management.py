"""
Staff Management Module
Handles staff management, task assignments, and automated scheduling
"""

import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QTabWidget, QGroupBox, QFormLayout, QLineEdit,
                             QComboBox, QTextEdit, QDialog, QDialogButtonBox,
                             QMessageBox, QDateEdit, QSpinBox, QCheckBox,
                             QCalendarWidget, QListWidget, QSplitter,
                             QGridLayout, QFrame)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor

class StaffManagementWidget(QWidget):
    """Main widget for staff management system"""
    
    data_changed = Signal()
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)
        
        # Initialize data structures
        self.init_data_structures()

        # Initialize scheduling engine
        self.scheduling_engine = AutoSchedulingEngine(self.data)

        # Setup UI
        self.setup_ui()

        # Load data
        self.load_data()
    
    def init_data_structures(self):
        """Initialize staff and task data structures"""
        try:
            # Initialize staff data
            if 'staff' not in self.data:
                self.data['staff'] = pd.DataFrame(columns=[
                    'staff_id', 'staff_name', 'role', 'contact_number', 'email',
                    'hire_date', 'status', 'notes'
                ])
            
            # Update cleaning_maintenance structure if needed
            if 'cleaning_maintenance' in self.data:
                cleaning_df = self.data['cleaning_maintenance']
                required_columns = [
                    'assigned_staff_id', 'assigned_staff_name', 'schedule_type',
                    'schedule_interval', 'schedule_days', 'schedule_dates',
                    'auto_assign', 'rotation_order'
                ]
                
                for col in required_columns:
                    if col not in cleaning_df.columns:
                        cleaning_df[col] = ''
                        
                self.data['cleaning_maintenance'] = cleaning_df
                
        except Exception as e:
            self.logger.error(f"Error initializing data structures: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.create_staff_tab()
        self.create_task_assignment_tab()
        self.create_calendar_tab()
        self.create_scheduling_tab()
        
        layout.addWidget(self.tabs)
    
    def create_staff_tab(self):
        """Create staff management tab"""
        staff_widget = QWidget()
        layout = QVBoxLayout(staff_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Staff Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add staff button
        add_staff_btn = QPushButton("Add Staff Member")
        add_staff_btn.clicked.connect(self.add_staff_member)
        header_layout.addWidget(add_staff_btn)
        
        layout.addLayout(header_layout)
        
        # Staff table
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(8)
        self.staff_table.setHorizontalHeaderLabels([
            "ID", "Name", "Role", "Contact", "Email", "Hire Date", "Status", "Notes"
        ])
        
        # Configure table
        header = self.staff_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.staff_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit Staff")
        edit_btn.clicked.connect(self.edit_staff_member)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Staff")
        delete_btn.clicked.connect(self.delete_staff_member)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.tabs.addTab(staff_widget, "👥 Staff Management")
    
    def create_task_assignment_tab(self):
        """Create task assignment tab"""
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Task Assignments")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Assign task button
        assign_btn = QPushButton("Assign Task")
        assign_btn.clicked.connect(self.assign_task)
        header_layout.addWidget(assign_btn)
        
        layout.addLayout(header_layout)
        
        # Task assignments table
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(9)
        self.assignments_table.setHorizontalHeaderLabels([
            "Task", "Assigned Staff", "Schedule Type", "Frequency", 
            "Next Due", "Priority", "Status", "Last Completed", "Actions"
        ])
        
        # Configure table
        header = self.assignments_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.assignments_table)
        
        self.tabs.addTab(task_widget, "📋 Task Assignments")
    
    def create_calendar_tab(self):
        """Create calendar view tab"""
        calendar_widget = QWidget()
        layout = QHBoxLayout(calendar_widget)
        
        # Left side - Calendar
        left_layout = QVBoxLayout()
        
        calendar_title = QLabel("Task Calendar")
        calendar_title.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(calendar_title)
        
        self.calendar = QCalendarWidget()

        # Fix calendar display issues
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)  # Remove week numbers
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)  # Use short day names
        self.calendar.setGridVisible(True)  # Show grid lines
        self.calendar.setNavigationBarVisible(True)  # Show navigation

        # Set proper date range to avoid invalid dates
        from PySide6.QtCore import QDate
        self.calendar.setMinimumDate(QDate(2020, 1, 1))
        self.calendar.setMaximumDate(QDate(2030, 12, 31))

        # Set current date
        self.calendar.setSelectedDate(QDate.currentDate())

        self.calendar.selectionChanged.connect(self.on_date_selected)
        left_layout.addWidget(self.calendar)
        
        # Right side - Tasks for selected date
        right_layout = QVBoxLayout()
        
        tasks_title = QLabel("Tasks for Selected Date")
        tasks_title.setFont(QFont("Arial", 14, QFont.Bold))
        right_layout.addWidget(tasks_title)
        
        self.date_tasks_list = QListWidget()
        right_layout.addWidget(self.date_tasks_list)
        
        # Task details
        details_group = QGroupBox("Task Details")
        details_layout = QFormLayout(details_group)
        
        self.task_detail_name = QLabel("-")
        self.task_detail_staff = QLabel("-")
        self.task_detail_priority = QLabel("-")
        self.task_detail_notes = QLabel("-")
        
        details_layout.addRow("Task:", self.task_detail_name)
        details_layout.addRow("Assigned Staff:", self.task_detail_staff)
        details_layout.addRow("Priority:", self.task_detail_priority)
        details_layout.addRow("Notes:", self.task_detail_notes)
        
        right_layout.addWidget(details_group)

        # Quick action button
        quick_assign_btn = QPushButton("➕ Quick Assign Task")
        quick_assign_btn.clicked.connect(self.open_task_assignment_dialog)
        quick_assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        right_layout.addWidget(quick_assign_btn)

        # Add layouts to main layout
        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)
        
        self.tabs.addTab(calendar_widget, "📅 Calendar View")
    
    def create_scheduling_tab(self):
        """Create automated scheduling tab"""
        schedule_widget = QWidget()
        layout = QVBoxLayout(schedule_widget)
        
        # Header
        title = QLabel("Automated Scheduling")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Scheduling controls
        controls_group = QGroupBox("Scheduling Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Auto-generate button
        generate_btn = QPushButton("Generate Future Assignments")
        generate_btn.clicked.connect(self.generate_future_assignments)
        controls_layout.addWidget(generate_btn, 0, 0)
        
        # Days ahead input
        controls_layout.addWidget(QLabel("Days Ahead:"), 0, 1)
        self.days_ahead_spin = QSpinBox()
        self.days_ahead_spin.setRange(1, 365)
        self.days_ahead_spin.setValue(30)
        controls_layout.addWidget(self.days_ahead_spin, 0, 2)
        
        layout.addWidget(controls_group)
        
        # Generated assignments table
        assignments_title = QLabel("Generated Assignments")
        assignments_title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(assignments_title)

        # Action buttons
        button_layout = QHBoxLayout()

        # Assign Task button
        assign_btn = QPushButton("📋 Assign Task to Staff")
        assign_btn.clicked.connect(self.open_task_assignment_dialog)
        assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(assign_btn)

        # Add test data button for development
        test_btn = QPushButton("Add Sample Tasks (Testing)")
        test_btn.clicked.connect(self.add_sample_tasks)
        test_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 5px;")
        button_layout.addWidget(test_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.generated_table = QTableWidget()
        self.generated_table.setColumnCount(6)
        self.generated_table.setHorizontalHeaderLabels([
            "Date", "Task", "Assigned Staff", "Schedule Type", "Priority", "Auto Generated"
        ])
        
        header = self.generated_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.generated_table)
        
        self.tabs.addTab(schedule_widget, "⚙️ Auto Scheduling")
    
    def load_data(self):
        """Load staff and task data"""
        try:
            self.load_staff_data()
            self.load_task_assignments()
            self.update_calendar()
            # Show tasks for today by default
            today = datetime.now().date()
            self.show_tasks_for_date(today)
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")

    def refresh_all_data(self):
        """Refresh all data and update displays"""
        try:
            # Reload data from CSV files
            if 'cleaning_maintenance' in self.data:
                self.data['cleaning_maintenance'] = pd.read_csv('data/cleaning_maintenance.csv')
            if 'staff' in self.data:
                self.data['staff'] = pd.read_csv('data/staff.csv')

            # Refresh all displays
            self.load_data()

        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")

    def add_sample_tasks(self):
        """Add sample tasks for testing calendar functionality"""
        try:
            from datetime import datetime, timedelta

            # Sample staff data
            sample_staff = [
                {'staff_id': 1, 'staff_name': 'Alice Johnson', 'role': 'Kitchen Helper', 'status': 'Active'},
                {'staff_id': 2, 'staff_name': 'Bob Smith', 'role': 'Maintenance Assistant', 'status': 'Active'},
                {'staff_id': 3, 'staff_name': 'Carol Davis', 'role': 'Cleaning Staff', 'status': 'Active'}
            ]

            # Add sample staff if not exists
            if 'staff' not in self.data or self.data['staff'].empty:
                self.data['staff'] = pd.DataFrame(sample_staff)
                self.data['staff'].to_csv('data/staff.csv', index=False)

            # Sample tasks with various scheduling patterns
            now = datetime.now()
            sample_tasks = [
                {
                    'task_id': 1,
                    'task_name': 'Daily Kitchen Cleaning',
                    'assigned_staff_id': 1,
                    'assigned_staff_name': 'Alice Johnson',
                    'schedule_type': 'daily',
                    'schedule_interval': 1,
                    'priority': 'High',
                    'frequency': 'Daily',
                    'next_due': (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    'auto_assign': 1,
                    'notes': 'Daily cleaning of kitchen surfaces and equipment'
                },
                {
                    'task_id': 2,
                    'task_name': 'Weekly Deep Clean',
                    'assigned_staff_id': 3,
                    'assigned_staff_name': 'Carol Davis',
                    'schedule_type': 'weekly',
                    'schedule_interval': 1,
                    'schedule_days': 'Friday',
                    'priority': 'Medium',
                    'frequency': 'Weekly',
                    'next_due': (now + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'auto_assign': 1,
                    'notes': 'Weekly deep cleaning of all areas'
                },
                {
                    'task_id': 3,
                    'task_name': 'Monthly Equipment Check',
                    'assigned_staff_id': 2,
                    'assigned_staff_name': 'Bob Smith',
                    'schedule_type': 'monthly',
                    'schedule_interval': 1,
                    'schedule_dates': '15',
                    'priority': 'Medium',
                    'frequency': 'Monthly',
                    'next_due': (now + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                    'auto_assign': 1,
                    'notes': 'Monthly inspection and maintenance of equipment'
                },
                {
                    'task_id': 4,
                    'task_name': 'Overdue Task Example',
                    'assigned_staff_id': 1,
                    'assigned_staff_name': 'Alice Johnson',
                    'schedule_type': 'weekly',
                    'schedule_interval': 1,
                    'schedule_days': 'Monday',
                    'priority': 'High',
                    'frequency': 'Weekly',
                    'next_due': (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'auto_assign': 1,
                    'notes': 'This task is overdue for testing'
                },
                {
                    'task_id': 5,
                    'task_name': 'Due Today Example',
                    'assigned_staff_id': 2,
                    'assigned_staff_name': 'Bob Smith',
                    'schedule_type': 'custom',
                    'schedule_interval': 3,
                    'priority': 'Medium',
                    'frequency': 'Every 3 days',
                    'next_due': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'auto_assign': 1,
                    'notes': 'This task is due today for testing'
                }
            ]

            # Add sample tasks
            if 'cleaning_maintenance' not in self.data or self.data['cleaning_maintenance'].empty:
                self.data['cleaning_maintenance'] = pd.DataFrame(sample_tasks)
            else:
                # Append to existing tasks
                new_tasks_df = pd.DataFrame(sample_tasks)
                self.data['cleaning_maintenance'] = pd.concat([self.data['cleaning_maintenance'], new_tasks_df], ignore_index=True)

            # Save to CSV
            self.data['cleaning_maintenance'].to_csv('data/cleaning_maintenance.csv', index=False)

            # Refresh displays
            self.refresh_all_data()

            QMessageBox.information(self, "Sample Data Added",
                f"Added {len(sample_tasks)} sample tasks and {len(sample_staff)} sample staff members for testing.")

        except Exception as e:
            self.logger.error(f"Error adding sample tasks: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add sample tasks: {str(e)}")

    def open_task_assignment_dialog(self):
        """Open the enhanced task assignment dialog"""
        try:
            dialog = TaskAssignmentDialog(self.data, self)
            if dialog.exec() == QDialog.Accepted:
                # Refresh data after assignment
                self.refresh_all_data()
                QMessageBox.information(self, "Success", "Task assignment completed successfully!")
        except Exception as e:
            self.logger.error(f"Error opening task assignment dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open task assignment dialog: {str(e)}")
    
    def load_staff_data(self):
        """Load staff data into table"""
        try:
            if 'staff' not in self.data or self.data['staff'].empty:
                return
            
            staff_df = self.data['staff']
            self.staff_table.setRowCount(len(staff_df))
            
            for row, (_, staff) in enumerate(staff_df.iterrows()):
                self.staff_table.setItem(row, 0, QTableWidgetItem(str(staff.get('staff_id', ''))))
                self.staff_table.setItem(row, 1, QTableWidgetItem(str(staff.get('staff_name', ''))))
                self.staff_table.setItem(row, 2, QTableWidgetItem(str(staff.get('role', ''))))
                self.staff_table.setItem(row, 3, QTableWidgetItem(str(staff.get('contact_number', ''))))
                self.staff_table.setItem(row, 4, QTableWidgetItem(str(staff.get('email', ''))))
                self.staff_table.setItem(row, 5, QTableWidgetItem(str(staff.get('hire_date', ''))))
                self.staff_table.setItem(row, 6, QTableWidgetItem(str(staff.get('status', ''))))
                self.staff_table.setItem(row, 7, QTableWidgetItem(str(staff.get('notes', ''))))
                
        except Exception as e:
            self.logger.error(f"Error loading staff data: {e}")

    def load_task_assignments(self):
        """Load task assignments into table"""
        try:
            if 'cleaning_maintenance' not in self.data or self.data['cleaning_maintenance'].empty:
                return

            tasks_df = self.data['cleaning_maintenance']
            self.assignments_table.setRowCount(len(tasks_df))

            for row, (_, task) in enumerate(tasks_df.iterrows()):
                self.assignments_table.setItem(row, 0, QTableWidgetItem(str(task.get('task_name', ''))))
                self.assignments_table.setItem(row, 1, QTableWidgetItem(str(task.get('assigned_staff_name', ''))))
                self.assignments_table.setItem(row, 2, QTableWidgetItem(str(task.get('schedule_type', ''))))
                self.assignments_table.setItem(row, 3, QTableWidgetItem(str(task.get('frequency', ''))))
                self.assignments_table.setItem(row, 4, QTableWidgetItem(str(task.get('next_due', ''))))
                self.assignments_table.setItem(row, 5, QTableWidgetItem(str(task.get('priority', ''))))

                # Status based on next_due
                status = "Pending"
                if task.get('next_due'):
                    try:
                        next_due = pd.to_datetime(task.get('next_due'))
                        if next_due < datetime.now():
                            status = "Overdue"
                        elif next_due.date() == datetime.now().date():
                            status = "Due Today"
                    except:
                        pass

                self.assignments_table.setItem(row, 6, QTableWidgetItem(status))
                self.assignments_table.setItem(row, 7, QTableWidgetItem(str(task.get('last_completed', ''))))

                # Action button
                action_btn = QPushButton("Complete")
                action_btn.clicked.connect(lambda checked, r=row: self.complete_task(r))
                self.assignments_table.setCellWidget(row, 8, action_btn)

        except Exception as e:
            self.logger.error(f"Error loading task assignments: {e}")

    def update_calendar(self):
        """Update calendar with task highlights - Fixed date handling"""
        try:
            if 'cleaning_maintenance' not in self.data:
                return

            tasks_df = self.data['cleaning_maintenance']
            current_date = datetime.now().date()

            # Clear existing highlights by resetting to default format
            default_format = self.calendar.dateTextFormat(QDate())

            # Reset all dates to default format first
            start_date = QDate.currentDate().addDays(-365)
            end_date = QDate.currentDate().addDays(365)
            current_reset_date = start_date
            while current_reset_date <= end_date:
                self.calendar.setDateTextFormat(current_reset_date, default_format)
                current_reset_date = current_reset_date.addDays(1)

            # Highlight dates with tasks
            highlighted_dates = set()  # Track highlighted dates to avoid conflicts

            for _, task in tasks_df.iterrows():
                try:
                    next_due_str = task.get('next_due')
                    if pd.isna(next_due_str) or not next_due_str:
                        continue

                    # Parse the date more carefully
                    next_due = pd.to_datetime(next_due_str, errors='coerce')
                    if pd.isna(next_due):
                        self.logger.warning(f"Invalid date format for task {task.get('task_name', '')}: {next_due_str}")
                        continue

                    # Extract date components safely
                    due_date = next_due.date()

                    # Validate date components
                    if due_date.year < 1900 or due_date.year > 2100:
                        self.logger.warning(f"Invalid year for task {task.get('task_name', '')}: {due_date.year}")
                        continue

                    # Create QDate safely
                    q_date = QDate(due_date.year, due_date.month, due_date.day)
                    if not q_date.isValid():
                        self.logger.warning(f"Invalid QDate for task {task.get('task_name', '')}: {due_date}")
                        continue

                    # Skip if already highlighted (avoid conflicts)
                    date_key = (due_date.year, due_date.month, due_date.day)
                    if date_key in highlighted_dates:
                        continue
                    highlighted_dates.add(date_key)

                    # Create format for highlighting
                    format = self.calendar.dateTextFormat(q_date)

                    # Color based on priority and status
                    priority = task.get('priority', 'Medium')
                    days_diff = (due_date - current_date).days

                    if days_diff < 0:
                        # Overdue - Red background
                        format.setBackground(QColor(255, 200, 200))
                        format.setForeground(QColor(139, 0, 0))
                    elif days_diff == 0:
                        # Due today - Orange background
                        format.setBackground(QColor(255, 220, 150))
                        format.setForeground(QColor(139, 69, 0))
                    elif days_diff <= 3:
                        # Due soon - Yellow background
                        format.setBackground(QColor(255, 255, 200))
                        format.setForeground(QColor(139, 139, 0))
                    elif priority == 'High':
                        # High priority - Light red
                        format.setBackground(QColor(255, 230, 230))
                        format.setForeground(QColor(139, 0, 0))
                    elif priority == 'Medium':
                        # Medium priority - Light blue
                        format.setBackground(QColor(230, 240, 255))
                        format.setForeground(QColor(0, 0, 139))
                    else:
                        # Low priority - Light green
                        format.setBackground(QColor(230, 255, 230))
                        format.setForeground(QColor(0, 100, 0))

                    # Apply the format
                    self.calendar.setDateTextFormat(q_date, format)

                except Exception as date_error:
                    self.logger.warning(f"Error processing date for task {task.get('task_name', '')}: {date_error}")
                    continue

            self.logger.info(f"Calendar updated with {len(highlighted_dates)} highlighted dates")

        except Exception as e:
            self.logger.error(f"Error updating calendar: {e}")

    def add_staff_member(self):
        """Add a new staff member"""
        dialog = StaffDialog(self.data, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_staff_data()
            self.data_changed.emit()

    def edit_staff_member(self):
        """Edit selected staff member"""
        current_row = self.staff_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a staff member to edit.")
            return

        staff_id = self.staff_table.item(current_row, 0).text()
        dialog = StaffDialog(self.data, staff_id=staff_id, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_staff_data()
            self.data_changed.emit()

    def delete_staff_member(self):
        """Delete selected staff member"""
        current_row = self.staff_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a staff member to delete.")
            return

        staff_name = self.staff_table.item(current_row, 1).text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete staff member '{staff_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            staff_id = self.staff_table.item(current_row, 0).text()

            # Remove from dataframe
            if 'staff' in self.data:
                self.data['staff'] = self.data['staff'][
                    self.data['staff']['staff_id'] != int(staff_id)
                ]

                # Save to CSV
                self.data['staff'].to_csv('data/staff.csv', index=False)

                self.load_staff_data()
                self.data_changed.emit()

                QMessageBox.information(self, "Success", f"Staff member '{staff_name}' deleted successfully.")

    def assign_task(self):
        """Assign a task to staff member"""
        dialog = TaskAssignmentDialog(self.data, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_task_assignments()
            self.data_changed.emit()

    def complete_task(self, row):
        """Mark task as completed"""
        try:
            if 'cleaning_maintenance' not in self.data:
                return

            tasks_df = self.data['cleaning_maintenance']
            if row >= len(tasks_df):
                return

            task = tasks_df.iloc[row]
            task_name = task.get('task_name', '')

            # Update completion time and calculate next due
            now = datetime.now()
            tasks_df.loc[row, 'last_completed'] = now.strftime('%Y-%m-%d %H:%M:%S')

            # Calculate next due based on schedule
            schedule_type = task.get('schedule_type', 'daily')
            interval = int(task.get('schedule_interval', 1))

            if schedule_type == 'daily':
                next_due = now + timedelta(days=interval)
            elif schedule_type == 'weekly':
                next_due = now + timedelta(weeks=interval)
            elif schedule_type == 'monthly':
                next_due = now + timedelta(days=30 * interval)
            elif schedule_type == 'custom':
                next_due = now + timedelta(days=interval)
            else:
                next_due = now + timedelta(days=1)

            tasks_df.loc[row, 'next_due'] = next_due.strftime('%Y-%m-%d %H:%M:%S')

            # Save to CSV
            tasks_df.to_csv('data/cleaning_maintenance.csv', index=False)

            # Reload data and refresh displays
            self.load_task_assignments()
            self.update_calendar()
            self.data_changed.emit()

            QMessageBox.information(self, "Success", f"Task '{task_name}' marked as completed.")

        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            QMessageBox.critical(self, "Error", f"Failed to complete task: {str(e)}")

    def on_date_selected(self):
        """Handle calendar date selection"""
        try:
            selected_date = self.calendar.selectedDate().toPython()
            self.show_tasks_for_date(selected_date)
        except Exception as e:
            self.logger.error(f"Error handling date selection: {e}")

    def show_tasks_for_date(self, date):
        """Show tasks for selected date - Fixed date handling"""
        try:
            self.date_tasks_list.clear()
            self.clear_task_details()

            if 'cleaning_maintenance' not in self.data:
                self.date_tasks_list.addItem("No task data available")
                return

            tasks_df = self.data['cleaning_maintenance']
            if tasks_df.empty:
                self.date_tasks_list.addItem("No tasks found")
                return

            tasks_for_date = []

            for _, task in tasks_df.iterrows():
                try:
                    next_due_str = task.get('next_due')
                    if pd.isna(next_due_str) or not next_due_str:
                        continue

                    # Parse date carefully
                    next_due = pd.to_datetime(next_due_str, errors='coerce')
                    if pd.isna(next_due):
                        continue

                    # Compare dates
                    if next_due.date() == date:
                        priority = task.get('priority', 'Medium')
                        priority_icon = "🔴" if priority == 'High' else "🟡" if priority == 'Medium' else "🟢"

                        task_name = task.get('task_name', 'Unknown Task')
                        staff_name = task.get('assigned_staff_name', 'Unassigned')

                        task_text = f"{priority_icon} {task_name}"
                        if staff_name and staff_name != 'Unassigned':
                            task_text += f" - {staff_name}"

                        self.date_tasks_list.addItem(task_text)
                        tasks_for_date.append(task)

                except Exception as task_error:
                    self.logger.warning(f"Error processing task {task.get('task_name', '')}: {task_error}")
                    continue

            if not tasks_for_date:
                self.date_tasks_list.addItem(f"No tasks scheduled for {date.strftime('%Y-%m-%d')}")

            # Connect selection change to show details (disconnect first to avoid multiple connections)
            try:
                self.date_tasks_list.itemSelectionChanged.disconnect()
            except:
                pass
            self.date_tasks_list.itemSelectionChanged.connect(self.on_task_selected)

        except Exception as e:
            self.logger.error(f"Error showing tasks for date: {e}")
            self.date_tasks_list.clear()
            self.date_tasks_list.addItem(f"Error loading tasks: {str(e)}")

    def clear_task_details(self):
        """Clear task detail display"""
        self.task_detail_name.setText("-")
        self.task_detail_staff.setText("-")
        self.task_detail_priority.setText("-")
        self.task_detail_notes.setText("-")

    def on_task_selected(self):
        """Handle task selection in calendar view"""
        try:
            current_item = self.date_tasks_list.currentItem()
            if not current_item:
                return

            # Extract task info from the text
            task_text = current_item.text()

            # Find the corresponding task in data
            if 'cleaning_maintenance' not in self.data:
                return

            tasks_df = self.data['cleaning_maintenance']
            selected_date = self.calendar.selectedDate().toPython()

            for _, task in tasks_df.iterrows():
                try:
                    next_due = pd.to_datetime(task.get('next_due'))
                    if (next_due.date() == selected_date and
                        task.get('task_name', '') in task_text and
                        task.get('assigned_staff_name', '') in task_text):

                        # Update task details
                        self.task_detail_name.setText(task.get('task_name', '-'))
                        self.task_detail_staff.setText(task.get('assigned_staff_name', '-'))
                        self.task_detail_priority.setText(task.get('priority', '-'))
                        self.task_detail_notes.setText(task.get('notes', '-'))
                        break
                except:
                    continue

        except Exception as e:
            self.logger.error(f"Error handling task selection: {e}")

    def generate_future_assignments(self):
        """Generate future task assignments based on schedules using the scheduling engine"""
        try:
            days_ahead = self.days_ahead_spin.value()

            # Use the scheduling engine to generate assignments
            generated_assignments = self.scheduling_engine.auto_generate_assignments(days_ahead)

            if not generated_assignments:
                QMessageBox.information(
                    self, "No Assignments",
                    "No automatic assignments were generated. Please check that tasks have auto-assignment enabled."
                )
                return

            # Populate generated assignments table
            self.generated_table.setRowCount(len(generated_assignments))

            for row, assignment in enumerate(generated_assignments):
                self.generated_table.setItem(row, 0, QTableWidgetItem(assignment['date']))
                self.generated_table.setItem(row, 1, QTableWidgetItem(assignment['task_name']))
                self.generated_table.setItem(row, 2, QTableWidgetItem(assignment['assigned_staff_name']))
                self.generated_table.setItem(row, 3, QTableWidgetItem(assignment['schedule_type']))
                self.generated_table.setItem(row, 4, QTableWidgetItem(assignment['priority']))
                self.generated_table.setItem(row, 5, QTableWidgetItem('Yes' if assignment['auto_generated'] else 'No'))

            # Save generated assignments
            self.scheduling_engine.save_generated_assignments(generated_assignments)

            # Clean up old assignments
            self.scheduling_engine.cleanup_old_assignments()

            QMessageBox.information(
                self, "Success",
                f"Generated {len(generated_assignments)} future assignments for the next {days_ahead} days.\n"
                f"Assignments have been saved to data/generated_assignments.csv"
            )

        except Exception as e:
            self.logger.error(f"Error generating future assignments: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate assignments: {str(e)}")

    def auto_schedule_background(self):
        """Run automatic scheduling in the background"""
        try:
            # Generate assignments for the next 7 days automatically
            generated_assignments = self.scheduling_engine.auto_generate_assignments(7)

            if generated_assignments:
                self.scheduling_engine.save_generated_assignments(generated_assignments)
                self.logger.info(f"Background scheduling generated {len(generated_assignments)} assignments")

        except Exception as e:
            self.logger.error(f"Error in background scheduling: {e}")


class StaffDialog(QDialog):
    """Dialog for adding/editing staff members"""

    def __init__(self, data, staff_id=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.staff_id = staff_id
        self.is_edit = staff_id is not None

        self.setWindowTitle("Edit Staff Member" if self.is_edit else "Add Staff Member")
        self.setModal(True)
        self.resize(400, 300)

        self.setup_ui()

        if self.is_edit:
            self.load_staff_data()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Kitchen Helper", "Maintenance Assistant", "Cleaning Staff",
            "Kitchen Manager", "Supervisor", "Cook", "Other"
        ])
        self.contact_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setDate(QDate.currentDate())
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "On Leave"])
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Role:", self.role_combo)
        form_layout.addRow("Contact:", self.contact_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Hire Date:", self.hire_date_edit)
        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Notes:", self.notes_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_staff_data(self):
        """Load existing staff data for editing"""
        try:
            if 'staff' not in self.data:
                return

            staff_df = self.data['staff']
            staff_row = staff_df[staff_df['staff_id'] == int(self.staff_id)]

            if not staff_row.empty:
                staff = staff_row.iloc[0]
                self.name_edit.setText(str(staff.get('staff_name', '')))

                role = str(staff.get('role', ''))
                role_index = self.role_combo.findText(role)
                if role_index >= 0:
                    self.role_combo.setCurrentIndex(role_index)

                self.contact_edit.setText(str(staff.get('contact_number', '')))
                self.email_edit.setText(str(staff.get('email', '')))

                hire_date = staff.get('hire_date', '')
                if hire_date:
                    try:
                        date = QDate.fromString(str(hire_date), "yyyy-MM-dd")
                        self.hire_date_edit.setDate(date)
                    except:
                        pass

                status = str(staff.get('status', ''))
                status_index = self.status_combo.findText(status)
                if status_index >= 0:
                    self.status_combo.setCurrentIndex(status_index)

                self.notes_edit.setPlainText(str(staff.get('notes', '')))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load staff data: {str(e)}")

    def accept(self):
        """Save staff data"""
        try:
            # Validate input
            if not self.name_edit.text().strip():
                QMessageBox.warning(self, "Validation Error", "Name is required.")
                return

            # Prepare data
            staff_data = {
                'staff_name': self.name_edit.text().strip(),
                'role': self.role_combo.currentText(),
                'contact_number': self.contact_edit.text().strip(),
                'email': self.email_edit.text().strip(),
                'hire_date': self.hire_date_edit.date().toString("yyyy-MM-dd"),
                'status': self.status_combo.currentText(),
                'notes': self.notes_edit.toPlainText().strip()
            }

            if 'staff' not in self.data:
                self.data['staff'] = pd.DataFrame(columns=[
                    'staff_id', 'staff_name', 'role', 'contact_number', 'email',
                    'hire_date', 'status', 'notes'
                ])

            staff_df = self.data['staff']

            if self.is_edit:
                # Update existing staff
                staff_df.loc[staff_df['staff_id'] == int(self.staff_id), list(staff_data.keys())] = list(staff_data.values())
            else:
                # Add new staff
                new_id = staff_df['staff_id'].max() + 1 if not staff_df.empty else 1
                staff_data['staff_id'] = new_id

                new_staff = pd.DataFrame([staff_data])
                self.data['staff'] = pd.concat([staff_df, new_staff], ignore_index=True)

            # Save to CSV
            self.data['staff'].to_csv('data/staff.csv', index=False)

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save staff data: {str(e)}")


class TaskAssignmentDialog(QDialog):
    """Dialog for assigning tasks to staff members"""

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        self.setWindowTitle("Advanced Task Assignment")
        self.setModal(True)
        self.resize(650, 600)  # Larger dialog to accommodate all options

        self.setup_ui()

    def setup_ui(self):
        """Setup enhanced dialog UI"""
        layout = QVBoxLayout(self)

        # Title and description
        title_label = QLabel("Task Assignment")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        desc_label = QLabel("Assign a task to a staff member with automated scheduling options.")
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Form layout
        form_layout = QFormLayout()

        # Task selection (editable to allow typing new task names)
        self.task_combo = QComboBox()
        self.task_combo.setEditable(True)  # Allow typing new task names
        self.task_combo.setToolTip("Select an existing task or type a new task name")
        self.load_available_tasks()

        # Staff selection
        self.staff_combo = QComboBox()
        self.staff_combo.setToolTip("Select the staff member to assign this task to")
        self.load_available_staff()

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText("Medium")
        self.priority_combo.setToolTip("Set the priority level for this task")

        # Schedule type with enhanced options
        self.schedule_type_combo = QComboBox()
        self.schedule_type_combo.addItems([
            "Manual (No automation)",
            "Daily",
            "Nth Day Pattern"  # New flexible system: 3rd day of every week/month/year
        ])
        self.schedule_type_combo.currentTextChanged.connect(self.on_schedule_type_changed)
        self.schedule_type_combo.setToolTip("Choose how often this task should be automatically scheduled")

        # Scheduling options container
        self.schedule_options_widget = QWidget()
        self.schedule_options_layout = QFormLayout(self.schedule_options_widget)

        # Only keep the Nth Day Pattern options - remove all old complex scheduling

        # Nth Day Pattern options (e.g., 3rd day of every week/month/year)
        self.nth_day_options_widget = QWidget()
        self.nth_day_options_widget.setStyleSheet("""
            QWidget {
                background-color: #e8f5e8;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }
        """)
        nth_day_layout = QVBoxLayout(self.nth_day_options_widget)
        nth_day_layout.setContentsMargins(12, 12, 12, 12)

        # Title for the section
        title_label = QLabel("Configure Nth Day Pattern")
        title_label.setStyleSheet("font-weight: bold; color: #2E7D32; margin-bottom: 8px;")
        nth_day_layout.addWidget(title_label)

        # First row: Day number selection
        day_row = QHBoxLayout()
        day_row.addWidget(QLabel("Day Number:"))

        self.day_number_spin = QSpinBox()
        self.day_number_spin.setRange(1, 7)  # Start with week range (1st to 7th day)
        self.day_number_spin.setValue(3)  # Default to 3rd (Wednesday)
        self.day_number_spin.setToolTip("1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday")
        day_row.addWidget(self.day_number_spin)

        # Day name display
        self.day_name_label = QLabel("(Wednesday)")
        self.day_name_label.setStyleSheet("color: #666; font-style: italic;")
        day_row.addWidget(self.day_name_label)

        day_row.addStretch()
        nth_day_layout.addLayout(day_row)

        # Second row: Time period selection
        period_row = QHBoxLayout()
        period_row.addWidget(QLabel("of every:"))

        self.time_period_combo = QComboBox()
        self.time_period_combo.addItems([
            "Week",    # 3rd day of every week (Wednesday)
            "Month",   # 3rd day of every month
            "Year"     # 3rd day of every year (January 3rd)
        ])
        self.time_period_combo.setCurrentText("Week")
        self.time_period_combo.setToolTip("Choose the time period for repetition")
        period_row.addWidget(self.time_period_combo)

        period_row.addStretch()
        nth_day_layout.addLayout(period_row)

        # Third row: Interval (optional)
        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Repeat every:"))

        self.pattern_interval_spin = QSpinBox()
        self.pattern_interval_spin.setRange(1, 12)
        self.pattern_interval_spin.setValue(1)
        self.pattern_interval_spin.setToolTip("How often to repeat (1 = every week/month/year, 2 = every 2nd week/month/year)")
        interval_row.addWidget(self.pattern_interval_spin)

        self.interval_unit_label = QLabel("week(s)")
        interval_row.addWidget(self.interval_unit_label)

        interval_row.addStretch()
        nth_day_layout.addLayout(interval_row)

        # Connect signals to update day name and interval unit
        self.day_number_spin.valueChanged.connect(self.update_day_name)
        self.time_period_combo.currentTextChanged.connect(self.update_interval_unit)

        # Auto assign checkbox
        self.auto_assign_check = QCheckBox("Enable automatic scheduling")
        self.auto_assign_check.setChecked(True)
        self.auto_assign_check.setToolTip("When enabled, future occurrences will be automatically generated")

        # Schedule preview
        self.schedule_preview_label = QLabel("")
        self.schedule_preview_label.setStyleSheet("color: #0066cc; font-style: italic; margin: 5px 0;")

        # Add form rows
        form_layout.addRow("Task:", self.task_combo)
        form_layout.addRow("Assign to Staff:", self.staff_combo)
        form_layout.addRow("Priority:", self.priority_combo)
        form_layout.addRow("Schedule Type:", self.schedule_type_combo)

        layout.addLayout(form_layout)

        # Add scheduling options section with a group box for better visibility
        schedule_group = QGroupBox("Advanced Scheduling Configuration")
        schedule_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        schedule_group_layout = QVBoxLayout(schedule_group)
        schedule_group_layout.setSpacing(10)

        # Add instruction label
        instruction_label = QLabel("Configure the scheduling pattern based on the selected type:")
        instruction_label.setStyleSheet("color: #666; font-style: italic; margin-bottom: 5px;")
        schedule_group_layout.addWidget(instruction_label)

        # Add all scheduling option widgets to the group
        schedule_group_layout.addWidget(self.nth_day_options_widget)

        layout.addWidget(schedule_group)
        layout.addWidget(self.auto_assign_check)
        layout.addWidget(self.schedule_preview_label)

        # Initially hide all scheduling options
        self.nth_day_options_widget.setVisible(False)

        # Connect signals for preview updates
        self.schedule_type_combo.currentTextChanged.connect(self.update_schedule_preview)
        self.day_number_spin.valueChanged.connect(self.update_schedule_preview)
        self.time_period_combo.currentTextChanged.connect(self.update_schedule_preview)
        self.pattern_interval_spin.valueChanged.connect(self.update_schedule_preview)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Initial preview update
        self.update_schedule_preview()

    def load_available_tasks(self):
        """Load available tasks"""
        try:
            if 'cleaning_maintenance' in self.data:
                tasks_df = self.data['cleaning_maintenance']
                task_names = tasks_df['task_name'].tolist()
                self.task_combo.addItems(task_names)
        except Exception as e:
            pass

    def load_available_staff(self):
        """Load available staff"""
        try:
            if 'staff' in self.data:
                staff_df = self.data['staff']
                active_staff = staff_df[staff_df['status'] == 'Active']
                staff_names = active_staff['staff_name'].tolist()
                self.staff_combo.addItems(staff_names)
        except Exception as e:
            pass

    def update_day_name(self, day_number):
        """Update the day name display when day number changes"""
        try:
            period = self.time_period_combo.currentText()

            if period == "Week":
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if 1 <= day_number <= 7:
                    day_name = day_names[day_number - 1]
                    self.day_name_label.setText(f"({day_name})")
                else:
                    self.day_name_label.setText("(Invalid)")
            elif period == "Month":
                suffix = self.get_ordinal_suffix(day_number)
                self.day_name_label.setText(f"({day_number}{suffix} of month)")
            elif period == "Year":
                suffix = self.get_ordinal_suffix(day_number)
                self.day_name_label.setText(f"(January {day_number}{suffix})")
            else:
                self.day_name_label.setText("")
        except:
            self.day_name_label.setText("")

    def update_interval_unit(self, period):
        """Update the interval unit label when time period changes"""
        if period == "Week":
            self.interval_unit_label.setText("week(s)")
            self.pattern_interval_spin.setRange(1, 52)
            self.day_number_spin.setRange(1, 7)  # 1st to 7th day of week
            self.day_number_spin.setToolTip("1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday")
        elif period == "Month":
            self.interval_unit_label.setText("month(s)")
            self.pattern_interval_spin.setRange(1, 12)
            self.day_number_spin.setRange(1, 31)  # 1st to 31st day of month
            self.day_number_spin.setToolTip("Day of the month (1-31)")
        elif period == "Year":
            self.interval_unit_label.setText("year(s)")
            self.pattern_interval_spin.setRange(1, 10)
            self.day_number_spin.setRange(1, 31)  # 1st to 31st day of January
            self.day_number_spin.setToolTip("Day of January (1-31)")

        # Update the day name display
        self.update_day_name(self.day_number_spin.value())

    def on_schedule_type_changed(self, schedule_type):
        """Handle schedule type change - Simplified for nth day pattern"""
        # Hide all scheduling options first
        self.nth_day_options_widget.setVisible(False)

        # Show appropriate options based on schedule type
        if schedule_type == "Nth Day Pattern":
            self.nth_day_options_widget.setVisible(True)
            # Ensure the widget is properly sized
            self.nth_day_options_widget.adjustSize()
            # Update day name and interval unit
            self.update_day_name(self.day_number_spin.value())
            self.update_interval_unit(self.time_period_combo.currentText())

        # Force layout update to ensure proper display
        self.layout().update()
        self.adjustSize()

        # Update preview
        self.update_schedule_preview()

    def update_schedule_preview(self):
        """Update the schedule preview text"""
        try:
            schedule_type = self.schedule_type_combo.currentText()
            preview_text = ""

            if schedule_type == "Manual (No automation)":
                preview_text = "Task will be assigned manually without automatic scheduling."
            elif schedule_type == "Daily":
                preview_text = "Task will be scheduled every day."
            elif schedule_type == "Nth Day Pattern":
                day_number = self.day_number_spin.value()
                period = self.time_period_combo.currentText()
                interval = self.pattern_interval_spin.value()

                # Get day name for week pattern
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day_name = day_names[day_number - 1] if 1 <= day_number <= 7 else "Invalid"

                if period == "Week":
                    if interval == 1:
                        preview_text = f"Task will be scheduled on the {day_number}{self.get_ordinal_suffix(day_number)} day of every week ({day_name})."
                    else:
                        preview_text = f"Task will be scheduled on the {day_number}{self.get_ordinal_suffix(day_number)} day of every {interval} weeks ({day_name})."
                elif period == "Month":
                    if interval == 1:
                        preview_text = f"Task will be scheduled on the {day_number}{self.get_ordinal_suffix(day_number)} day of every month."
                    else:
                        preview_text = f"Task will be scheduled on the {day_number}{self.get_ordinal_suffix(day_number)} day of every {interval} months."
                elif period == "Year":
                    if interval == 1:
                        preview_text = f"Task will be scheduled on the {day_number}{self.get_ordinal_suffix(day_number)} day of every year (January {day_number})."
                    else:
                        preview_text = f"Task will be scheduled on the {day_number}{self.get_ordinal_suffix(day_number)} day of every {interval} years (January {day_number})."

            self.schedule_preview_label.setText(f"Preview: {preview_text}")

        except Exception as e:
            self.schedule_preview_label.setText("Preview: Unable to generate preview")

    def get_ordinal_suffix(self, day):
        """Get ordinal suffix for day numbers (1st, 2nd, 3rd, etc.)"""
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return suffix

    def accept(self):
        """Save enhanced task assignment"""
        try:
            if not self.task_combo.currentText() or not self.staff_combo.currentText():
                QMessageBox.warning(self, "Validation Error", "Please select both task and staff member.")
                return

            # Get staff ID
            staff_name = self.staff_combo.currentText()
            staff_df = self.data['staff']
            staff_row = staff_df[staff_df['staff_name'] == staff_name]
            staff_id = staff_row.iloc[0]['staff_id'] if not staff_row.empty else 0

            # Determine schedule parameters based on type
            schedule_type_text = self.schedule_type_combo.currentText()
            schedule_type = "manual"
            schedule_interval = 1
            day_number = 1
            time_period = "Week"

            if schedule_type_text == "Daily":
                schedule_type = "daily"
                schedule_interval = 1
            elif schedule_type_text == "Nth Day Pattern":
                schedule_type = "nth_day_pattern"
                day_number = self.day_number_spin.value()
                time_period = self.time_period_combo.currentText()
                schedule_interval = self.pattern_interval_spin.value()

            # Update or create task assignment
            task_name = self.task_combo.currentText().strip()
            tasks_df = self.data['cleaning_maintenance']
            task_index = tasks_df[tasks_df['task_name'] == task_name].index

            # Add new fields for nth day pattern scheduling if they don't exist
            if 'day_number' not in tasks_df.columns:
                tasks_df['day_number'] = 1
            if 'time_period' not in tasks_df.columns:
                tasks_df['time_period'] = "Week"

            # Set next due date based on schedule type
            from datetime import datetime, timedelta
            now = datetime.now()

            if schedule_type == "daily":
                next_due = now + timedelta(days=schedule_interval)
            elif schedule_type == "nth_day_pattern":
                next_due = self.calculate_nth_day_pattern(now, day_number, time_period, schedule_interval)
            else:
                next_due = now + timedelta(days=1)  # Default to tomorrow

            if not task_index.empty:
                # Update existing task
                idx = task_index[0]
                tasks_df.loc[idx, 'assigned_staff_id'] = staff_id
                tasks_df.loc[idx, 'assigned_staff_name'] = staff_name
                tasks_df.loc[idx, 'schedule_type'] = schedule_type
                tasks_df.loc[idx, 'schedule_interval'] = schedule_interval
                tasks_df.loc[idx, 'day_number'] = day_number
                tasks_df.loc[idx, 'time_period'] = time_period
                tasks_df.loc[idx, 'priority'] = self.priority_combo.currentText()
                tasks_df.loc[idx, 'auto_assign'] = 1 if self.auto_assign_check.isChecked() else 0
                tasks_df.loc[idx, 'next_due'] = next_due.strftime('%Y-%m-%d %H:%M:%S')

                action_text = "updated"
            else:
                # Create new task
                new_task_id = tasks_df['task_id'].max() + 1 if not tasks_df.empty else 1

                new_task = {
                    'task_id': new_task_id,
                    'task_name': task_name,
                    'frequency': schedule_type_text,
                    'last_completed': '',
                    'next_due': next_due.strftime('%Y-%m-%d %H:%M:%S'),
                    'priority': self.priority_combo.currentText(),
                    'notes': f'Created via staff assignment - {schedule_type_text}',
                    'assigned_staff_id': staff_id,
                    'assigned_staff_name': staff_name,
                    'schedule_type': schedule_type,
                    'schedule_interval': schedule_interval,
                    'day_number': day_number,
                    'time_period': time_period,
                    'auto_assign': 1 if self.auto_assign_check.isChecked() else 0,
                    'rotation_order': ''
                }

                # Add new row to dataframe
                new_row_df = pd.DataFrame([new_task])
                tasks_df = pd.concat([tasks_df, new_row_df], ignore_index=True)
                self.data['cleaning_maintenance'] = tasks_df

                action_text = "created and assigned"

            # Save to CSV
            tasks_df.to_csv('data/cleaning_maintenance.csv', index=False)

            QMessageBox.information(self, "Success",
                f"Task '{task_name}' {action_text} to {staff_name} with {schedule_type_text.lower()} scheduling.")

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to assign task: {str(e)}")

    def calculate_nth_day_pattern(self, base_date, day_number, time_period, interval):
        """Calculate the next occurrence of nth day pattern"""
        from datetime import datetime, timedelta

        try:
            if time_period == "Week":
                # 3rd day of every week = Wednesday
                # Calculate days until the target day of week
                target_weekday = (day_number - 1) % 7  # Convert to 0-6 (Monday=0)
                days_ahead = (target_weekday - base_date.weekday()) % 7

                if days_ahead == 0:  # If it's today, move to next interval
                    days_ahead = 7 * interval
                else:
                    days_ahead += 7 * (interval - 1)

                return base_date + timedelta(days=days_ahead)

            elif time_period == "Month":
                # 3rd day of every month
                next_date = base_date.replace(day=min(day_number, 28))  # Safe day

                if next_date <= base_date:
                    # Move to next interval
                    month = next_date.month + interval
                    year = next_date.year
                    while month > 12:
                        month -= 12
                        year += 1
                    next_date = next_date.replace(year=year, month=month)

                return next_date

            elif time_period == "Year":
                # 3rd day of every year = January 3rd
                next_date = base_date.replace(month=1, day=min(day_number, 31))

                if next_date <= base_date:
                    # Move to next interval
                    next_date = next_date.replace(year=next_date.year + interval)

                return next_date

            else:
                return base_date + timedelta(days=1)

        except Exception as e:
            print(f"Error calculating nth day pattern: {e}")
            return base_date + timedelta(days=1)

    def calculate_nth_weekday(self, base_date, occurrence, weekday):
        """Calculate the next occurrence of nth weekday (e.g., 3rd Monday)"""
        from datetime import datetime, timedelta
        import calendar

        try:
            # Get the weekday number (0=Monday, 6=Sunday)
            target_weekday = self.get_weekday_number(weekday)

            # Start with the current month
            year = base_date.year
            month = base_date.month

            # Calculate for current month first
            next_date = self.get_nth_weekday_of_month(year, month, occurrence, target_weekday)

            # If the date has passed this month, move to next month
            if next_date is None or next_date <= base_date:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                next_date = self.get_nth_weekday_of_month(year, month, occurrence, target_weekday)

            return next_date if next_date else base_date + timedelta(days=30)

        except Exception as e:
            print(f"Error calculating nth weekday: {e}")
            return base_date + timedelta(days=30)

    def get_nth_weekday_of_month(self, year, month, occurrence, target_weekday):
        """Get the nth occurrence of a weekday in a specific month"""
        import calendar
        from datetime import datetime

        try:
            # Get the first day of the month
            first_day = datetime(year, month, 1)

            if occurrence.lower() == "last":
                # Find the last occurrence
                # Get the last day of the month
                last_day = calendar.monthrange(year, month)[1]
                last_date = datetime(year, month, last_day)

                # Work backwards to find the last occurrence of the target weekday
                for day in range(last_day, 0, -1):
                    date = datetime(year, month, day)
                    if date.weekday() == target_weekday:
                        return date
            else:
                # Find the nth occurrence (1st, 2nd, 3rd, 4th)
                occurrence_num = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4}.get(occurrence, 1)

                # Find the first occurrence of the target weekday
                first_weekday = first_day.weekday()
                days_to_target = (target_weekday - first_weekday) % 7
                first_occurrence = first_day + timedelta(days=days_to_target)

                # Calculate the nth occurrence
                nth_occurrence = first_occurrence + timedelta(weeks=occurrence_num - 1)

                # Check if this date exists in the month
                if nth_occurrence.month == month:
                    return nth_occurrence

            return None

        except Exception as e:
            print(f"Error getting nth weekday of month: {e}")
            return None


class AutoSchedulingEngine:
    """Automated task scheduling engine"""

    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(__name__)

    def auto_generate_assignments(self, days_ahead=30):
        """Automatically generate future assignments"""
        try:
            if 'cleaning_maintenance' not in self.data:
                return []

            tasks_df = self.data['cleaning_maintenance']
            current_date = datetime.now()
            generated_assignments = []

            for _, task in tasks_df.iterrows():
                # Only process tasks with auto_assign enabled
                if not task.get('auto_assign') or task.get('auto_assign') == '0':
                    continue

                assignments = self.generate_task_assignments(task, current_date, days_ahead)
                generated_assignments.extend(assignments)

            return generated_assignments

        except Exception as e:
            self.logger.error(f"Error in auto_generate_assignments: {e}")
            return []

    def generate_task_assignments(self, task, start_date, days_ahead):
        """Generate assignments for a specific task"""
        try:
            assignments = []
            schedule_type = task.get('schedule_type', 'daily')
            interval = int(task.get('schedule_interval', 1))

            # Handle staff rotation if specified
            rotation_order = task.get('rotation_order', '')
            staff_rotation = []
            if rotation_order:
                staff_rotation = [int(x.strip()) for x in rotation_order.split(';') if x.strip().isdigit()]

            assignment_date = start_date
            rotation_index = 0

            while assignment_date <= start_date + timedelta(days=days_ahead):
                # Determine assigned staff
                if staff_rotation and len(staff_rotation) > 0:
                    staff_id = staff_rotation[rotation_index % len(staff_rotation)]
                    staff_name = self.get_staff_name_by_id(staff_id)
                    rotation_index += 1
                else:
                    staff_id = task.get('assigned_staff_id', '')
                    staff_name = task.get('assigned_staff_name', '')

                # Check if assignment should be created based on schedule
                if self.should_create_assignment(task, assignment_date):
                    assignments.append({
                        'date': assignment_date.strftime('%Y-%m-%d'),
                        'task_id': task.get('task_id', ''),
                        'task_name': task.get('task_name', ''),
                        'assigned_staff_id': staff_id,
                        'assigned_staff_name': staff_name,
                        'schedule_type': schedule_type,
                        'priority': task.get('priority', 'Medium'),
                        'auto_generated': True,
                        'estimated_duration': self.estimate_task_duration(task),
                        'notes': f"Auto-generated {schedule_type} assignment"
                    })

                # Calculate next assignment date
                assignment_date = self.get_next_assignment_date(assignment_date, schedule_type, interval, task)

                # Safety check to prevent infinite loops
                if assignment_date <= start_date:
                    break

            return assignments

        except Exception as e:
            self.logger.error(f"Error generating assignments for task {task.get('task_name', '')}: {e}")
            return []

    def should_create_assignment(self, task, date):
        """Check if an assignment should be created for the given date - Enhanced"""
        try:
            schedule_type = task.get('schedule_type', 'daily')

            if schedule_type == 'weekly':
                # Check if it's the correct day of week and interval
                schedule_days = task.get('schedule_days', '')
                schedule_interval = int(task.get('schedule_interval', 1))

                if schedule_days:
                    target_weekday = self.get_weekday_number(schedule_days)
                    if date.weekday() != target_weekday:
                        return False

                    # Check if it's the correct week interval
                    # Calculate weeks since epoch to determine interval
                    epoch_date = datetime(1970, 1, 5)  # A Monday
                    weeks_since_epoch = (date - epoch_date.date()).days // 7
                    return weeks_since_epoch % schedule_interval == 0

                return True

            elif schedule_type == 'monthly':
                # Check if it's the correct day of month and interval
                schedule_dates = task.get('schedule_dates', '')
                schedule_interval = int(task.get('schedule_interval', 1))

                if schedule_dates:
                    try:
                        target_day = int(schedule_dates)
                        if date.day != target_day:
                            return False

                        # Check if it's the correct month interval
                        # Calculate months since a reference date
                        ref_date = datetime(2024, 1, 1).date()
                        months_diff = (date.year - ref_date.year) * 12 + (date.month - ref_date.month)
                        return months_diff % schedule_interval == 0
                    except:
                        pass

                return date.day == 1  # Default to first day of month

            elif schedule_type == 'nth_weekday':
                # Check if it's the correct nth weekday of the month
                nth_occurrence = task.get('nth_occurrence', '')
                nth_weekday = task.get('nth_weekday', '')

                if nth_occurrence and nth_weekday:
                    # Calculate the expected date for this month
                    expected_date = self.get_nth_weekday_of_month(
                        date.year, date.month, nth_occurrence,
                        self.get_weekday_number(nth_weekday)
                    )
                    return expected_date and expected_date.date() == date

                return False

            elif schedule_type == 'custom':
                # Check custom interval in days
                schedule_interval = int(task.get('schedule_interval', 1))

                # Calculate days since a reference date
                ref_date = datetime(2024, 1, 1).date()
                days_diff = (date - ref_date).days
                return days_diff % schedule_interval == 0

            # For daily and manual, always create (daily) or never create (manual)
            if schedule_type == 'manual':
                return False

            return True  # Daily

        except Exception as e:
            self.logger.error(f"Error checking assignment creation: {e}")
            return True

    def get_next_assignment_date(self, current_date, schedule_type, interval, task=None):
        """Calculate the next assignment date - Enhanced for complex patterns"""
        try:
            if schedule_type == 'daily':
                return current_date + timedelta(days=interval)

            elif schedule_type == 'weekly':
                # For weekly, move to next occurrence of the specified day
                if task and task.get('schedule_days'):
                    target_weekday = self.get_weekday_number(task.get('schedule_days'))
                    days_ahead = (target_weekday - current_date.weekday()) % 7
                    if days_ahead == 0:  # If it's the same day, move to next interval
                        days_ahead = 7 * interval
                    else:
                        days_ahead += 7 * (interval - 1)
                    return current_date + timedelta(days=days_ahead)
                else:
                    return current_date + timedelta(weeks=interval)

            elif schedule_type == 'monthly':
                # For monthly, move to next occurrence of the specified date
                if task and task.get('schedule_dates'):
                    try:
                        target_day = int(task.get('schedule_dates'))
                        next_date = current_date.replace(day=min(target_day, 28))

                        # If the target date has passed this month, move to next interval
                        if next_date <= current_date:
                            # Add the interval in months
                            month = next_date.month
                            year = next_date.year
                            month += interval
                            while month > 12:
                                month -= 12
                                year += 1
                            next_date = next_date.replace(year=year, month=month)

                        return next_date
                    except:
                        # Fallback to approximate calculation
                        return current_date + timedelta(days=30 * interval)
                else:
                    return current_date + timedelta(days=30 * interval)

            elif schedule_type == 'nth_weekday':
                # For nth weekday, move to next month's occurrence
                if task and task.get('nth_occurrence') and task.get('nth_weekday'):
                    occurrence = task.get('nth_occurrence')
                    weekday = task.get('nth_weekday')

                    # Move to next month
                    next_month = current_date.month + 1
                    next_year = current_date.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1

                    # Calculate the nth weekday of next month
                    target_weekday = self.get_weekday_number(weekday)
                    next_date = self.get_nth_weekday_of_month(next_year, next_month, occurrence, target_weekday)

                    return next_date if next_date else current_date + timedelta(days=30)
                else:
                    return current_date + timedelta(days=30)

            elif schedule_type == 'custom':
                return current_date + timedelta(days=interval)

            elif schedule_type == 'manual':
                # Manual tasks don't have automatic next dates
                return current_date + timedelta(days=365)  # Far future

            else:
                return current_date + timedelta(days=1)

        except Exception as e:
            self.logger.error(f"Error calculating next assignment date: {e}")
            return current_date + timedelta(days=1)

    def get_weekday_number(self, day_name):
        """Convert day name to weekday number (0=Monday, 6=Sunday)"""
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        return day_mapping.get(day_name.lower(), 0)

    def get_staff_name_by_id(self, staff_id):
        """Get staff name by ID"""
        try:
            if 'staff' not in self.data:
                return 'Unknown Staff'

            staff_df = self.data['staff']
            staff_row = staff_df[staff_df['staff_id'] == staff_id]

            if not staff_row.empty:
                return staff_row.iloc[0]['staff_name']

            return 'Unknown Staff'

        except Exception as e:
            self.logger.error(f"Error getting staff name for ID {staff_id}: {e}")
            return 'Unknown Staff'

    def estimate_task_duration(self, task):
        """Estimate task duration based on task type and complexity"""
        try:
            task_name = task.get('task_name', '').lower()

            # Simple duration estimation based on task keywords
            if any(keyword in task_name for keyword in ['deep', 'thorough', 'complete']):
                return 120  # 2 hours
            elif any(keyword in task_name for keyword in ['maintenance', 'repair', 'check']):
                return 90   # 1.5 hours
            elif any(keyword in task_name for keyword in ['cleaning', 'washing', 'mopping']):
                return 60   # 1 hour
            elif any(keyword in task_name for keyword in ['organization', 'inventory']):
                return 45   # 45 minutes
            else:
                return 30   # 30 minutes default

        except Exception as e:
            self.logger.error(f"Error estimating task duration: {e}")
            return 30

    def save_generated_assignments(self, assignments):
        """Save generated assignments to a separate tracking file"""
        try:
            if not assignments:
                return

            # Create assignments dataframe
            assignments_df = pd.DataFrame(assignments)

            # Save to CSV
            assignments_file = 'data/generated_assignments.csv'
            assignments_df.to_csv(assignments_file, index=False)

            self.logger.info(f"Saved {len(assignments)} generated assignments to {assignments_file}")

        except Exception as e:
            self.logger.error(f"Error saving generated assignments: {e}")

    def cleanup_old_assignments(self, days_to_keep=90):
        """Clean up old generated assignments"""
        try:
            assignments_file = 'data/generated_assignments.csv'

            if not os.path.exists(assignments_file):
                return

            assignments_df = pd.read_csv(assignments_file)
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Filter out old assignments
            assignments_df['date'] = pd.to_datetime(assignments_df['date'])
            filtered_df = assignments_df[assignments_df['date'] >= cutoff_date]

            # Save filtered data
            filtered_df.to_csv(assignments_file, index=False)

            removed_count = len(assignments_df) - len(filtered_df)
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old assignments")

        except Exception as e:
            self.logger.error(f"Error cleaning up old assignments: {e}")
