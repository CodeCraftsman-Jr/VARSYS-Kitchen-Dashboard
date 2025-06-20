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
                             QGridLayout, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor
from modules.universal_table_widget import UniversalTableWidget

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
        
        # Staff table with universal filtering and sorting
        staff_columns = ["ID", "Name", "Role", "Contact", "Email", "Hire Date", "Status", "Notes"]
        self.staff_table_widget = UniversalTableWidget(
            data=self.data.get('staff', pd.DataFrame()),
            columns=staff_columns,
            parent=self,
            is_history_table=False  # Staff is a regular table - remove duplicates
        )

        # Connect signals for row selection
        self.staff_table_widget.row_selected.connect(self.on_staff_row_selected)

        layout.addWidget(self.staff_table_widget)
        
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
        """Load staff data into universal table widget"""
        try:
            if 'staff' not in self.data or self.data['staff'].empty:
                self.staff_table_widget.update_data(pd.DataFrame())
                return

            staff_df = self.data['staff'].copy()

            # Ensure all required columns exist and rename for display
            column_mapping = {
                'staff_id': 'ID',
                'staff_name': 'Name',
                'role': 'Role',
                'contact_number': 'Contact',
                'email': 'Email',
                'hire_date': 'Hire Date',
                'status': 'Status',
                'notes': 'Notes'
            }

            # Create display dataframe with proper column names
            display_data = pd.DataFrame()
            for original_col, display_col in column_mapping.items():
                if original_col in staff_df.columns:
                    display_data[display_col] = staff_df[original_col]
                else:
                    display_data[display_col] = ''

            # Update the universal table widget
            self.staff_table_widget.update_data(display_data)
            print(f"✅ Updated staff table with {len(display_data)} staff members")

        except Exception as e:
            self.logger.error(f"Error loading staff data: {e}")
            self.staff_table_widget.update_data(pd.DataFrame())

    def on_staff_row_selected(self, row_index):
        """Handle staff row selection"""
        try:
            if 'staff' in self.data and row_index >= 0 and row_index < len(self.data['staff']):
                selected_staff = self.data['staff'].iloc[row_index]
                print(f"Selected staff: {selected_staff.get('staff_name', 'Unknown')} - {selected_staff.get('role', 'No role')}")
        except Exception as e:
            print(f"Error handling staff row selection: {e}")

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



    def add_staff_member(self):
        """Add a new staff member"""
        dialog = StaffDialog(self.data, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_staff_data()
            self.data_changed.emit()

    def edit_staff_member(self):
        """Edit selected staff member"""
        current_row = self.staff_table_widget.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a staff member to edit.")
            return

        try:
            # Get staff ID from the filtered data
            if current_row < len(self.staff_table_widget.filtered_data):
                display_row = self.staff_table_widget.filtered_data.iloc[current_row]
                staff_id = str(display_row['ID'])

                dialog = StaffDialog(self.data, staff_id=staff_id, parent=self)
                if dialog.exec() == QDialog.Accepted:
                    self.load_staff_data()
                    self.data_changed.emit()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit staff member: {e}")

    def delete_staff_member(self):
        """Delete selected staff member"""
        current_row = self.staff_table_widget.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a staff member to delete.")
            return

        try:
            # Get staff info from the filtered data
            if current_row < len(self.staff_table_widget.filtered_data):
                display_row = self.staff_table_widget.filtered_data.iloc[current_row]
                staff_id = str(display_row['ID'])
                staff_name = str(display_row['Name'])

                reply = QMessageBox.question(
                    self, "Confirm Delete",
                    f"Are you sure you want to delete staff member '{staff_name}'?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Remove from dataframe
                    if 'staff' in self.data:
                        self.data['staff'] = self.data['staff'][
                            self.data['staff']['staff_id'] != int(staff_id)
                        ]

                        # Save to CSV
                        self.data['staff'].to_csv('data/staff.csv', index=False)

                        # Refresh display
                        self.load_staff_data()
                        self.data_changed.emit()

                        QMessageBox.information(self, "Success", f"Staff member '{staff_name}' deleted successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete staff member: {e}")

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
            self.data_changed.emit()

            QMessageBox.information(self, "Success", f"Task '{task_name}' marked as completed.")

        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            QMessageBox.critical(self, "Error", f"Failed to complete task: {str(e)}")



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
        self.resize(1000, 700)  # Further increased width for better content visibility
        self.setMaximumHeight(800)  # Increased maximum height for better usability
        self.setMinimumWidth(950)  # Set minimum width to ensure content is always visible

        self.setup_ui()

    def setup_ui(self):
        """Setup enhanced dialog UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title and description
        title_label = QLabel("Task Assignment")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title_label)

        desc_label = QLabel("Assign a task to a staff member with automated scheduling options.")
        desc_label.setStyleSheet("color: #666; font-size: 11px;")
        main_layout.addWidget(desc_label)

        # Create scroll area for the form content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Content widget for scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(5)

        # Form layout
        form_layout = QFormLayout()

        # Task selection (editable to allow typing new task names)
        self.task_combo = QComboBox()
        self.task_combo.setEditable(True)  # Allow typing new task names
        self.task_combo.setToolTip("Select an existing task or type a new task name")
        self.load_available_tasks()

        # Staff selection - Enhanced for multiple staff
        self.staff_assignment_type = QComboBox()
        self.staff_assignment_type.addItems([
            "Single Staff Member",
            "Multiple Staff (Daily Rotation)"
        ])
        self.staff_assignment_type.currentTextChanged.connect(self.on_staff_assignment_type_changed)
        self.staff_assignment_type.setToolTip("Choose between single staff assignment or multiple staff with daily rotation")

        # Single staff selection
        self.staff_combo = QComboBox()
        self.staff_combo.setToolTip("Select the staff member to assign this task to")
        self.load_available_staff()

        # Multiple staff selection widget
        self.multiple_staff_widget = QWidget()
        self.setup_multiple_staff_widget()

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
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 6px;
                margin: 2px;
            }
        """)
        nth_day_layout = QGridLayout(self.nth_day_options_widget)  # Use grid for compactness
        nth_day_layout.setContentsMargins(6, 6, 6, 6)
        nth_day_layout.setSpacing(3)

        # Title for the section
        title_label = QLabel("Nth Day Pattern")
        title_label.setStyleSheet("font-weight: bold; color: #2E7D32; font-size: 12px;")
        nth_day_layout.addWidget(title_label, 0, 0, 1, 4)

        # Day number selection
        nth_day_layout.addWidget(QLabel("Day:"), 1, 0)
        self.day_number_spin = QSpinBox()
        self.day_number_spin.setRange(1, 7)  # Start with week range (1st to 7th day)
        self.day_number_spin.setValue(3)  # Default to 3rd (Wednesday)
        self.day_number_spin.setMaximumWidth(60)
        self.day_number_spin.setToolTip("1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday")
        nth_day_layout.addWidget(self.day_number_spin, 1, 1)

        # Day name display
        self.day_name_label = QLabel("(Wednesday)")
        self.day_name_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        nth_day_layout.addWidget(self.day_name_label, 1, 2)

        # Time period selection
        nth_day_layout.addWidget(QLabel("of every:"), 2, 0)
        self.time_period_combo = QComboBox()
        self.time_period_combo.addItems([
            "Week",    # 3rd day of every week (Wednesday)
            "Month",   # 3rd day of every month
            "Year"     # 3rd day of every year (January 3rd)
        ])
        self.time_period_combo.setCurrentText("Week")
        self.time_period_combo.setMaximumWidth(80)
        self.time_period_combo.setToolTip("Choose the time period for repetition")
        nth_day_layout.addWidget(self.time_period_combo, 2, 1)

        # Interval selection
        nth_day_layout.addWidget(QLabel("Every:"), 3, 0)
        self.pattern_interval_spin = QSpinBox()
        self.pattern_interval_spin.setRange(1, 12)
        self.pattern_interval_spin.setValue(1)
        self.pattern_interval_spin.setMaximumWidth(60)
        self.pattern_interval_spin.setToolTip("How often to repeat (1 = every week/month/year, 2 = every 2nd week/month/year)")
        nth_day_layout.addWidget(self.pattern_interval_spin, 3, 1)

        self.interval_unit_label = QLabel("week(s)")
        self.interval_unit_label.setStyleSheet("font-size: 11px;")
        nth_day_layout.addWidget(self.interval_unit_label, 3, 2)

        # Connect signals to update day name and interval unit
        self.day_number_spin.valueChanged.connect(self.update_day_name)
        self.time_period_combo.currentTextChanged.connect(self.update_interval_unit)

        # Auto assign checkbox
        self.auto_assign_check = QCheckBox("Enable automatic scheduling")
        self.auto_assign_check.setChecked(True)
        self.auto_assign_check.setToolTip("When enabled, future occurrences will be automatically generated")

        # Schedule preview
        self.schedule_preview_label = QLabel("")
        self.schedule_preview_label.setStyleSheet("""
            QLabel {
                color: #0066cc;
                font-style: italic;
                font-size: 12px;
                background-color: #f0f8ff;
                border: 1px solid #4a90e2;
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
                line-height: 1.4;
            }
        """)
        self.schedule_preview_label.setWordWrap(True)
        self.schedule_preview_label.setMinimumHeight(60)  # Set minimum height for better visibility

        # Add form rows
        form_layout.addRow("Task:", self.task_combo)
        form_layout.addRow("Staff Assignment:", self.staff_assignment_type)
        form_layout.addRow("Single Staff:", self.staff_combo)
        form_layout.addRow("Multiple Staff:", self.multiple_staff_widget)
        form_layout.addRow("Priority:", self.priority_combo)
        form_layout.addRow("Schedule Type:", self.schedule_type_combo)

        layout.addLayout(form_layout)

        # Add scheduling options section with a more compact group box
        schedule_group = QGroupBox("Scheduling Configuration")
        schedule_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 3px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        schedule_group_layout = QVBoxLayout(schedule_group)
        schedule_group_layout.setSpacing(5)
        schedule_group_layout.setContentsMargins(5, 5, 5, 5)

        # Add all scheduling option widgets to the group
        schedule_group_layout.addWidget(self.nth_day_options_widget)

        layout.addWidget(schedule_group)
        layout.addWidget(self.auto_assign_check)
        layout.addWidget(self.schedule_preview_label)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Initially hide all scheduling options and multiple staff widget
        self.nth_day_options_widget.setVisible(False)
        self.multiple_staff_widget.setVisible(False)

        # Connect signals for preview updates
        self.schedule_type_combo.currentTextChanged.connect(self.update_schedule_preview)
        self.day_number_spin.valueChanged.connect(self.update_schedule_preview)
        self.time_period_combo.currentTextChanged.connect(self.update_schedule_preview)
        self.pattern_interval_spin.valueChanged.connect(self.update_schedule_preview)

        # Buttons (outside scroll area)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

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

    def setup_multiple_staff_widget(self):
        """Setup the multiple staff assignment widget"""
        layout = QVBoxLayout(self.multiple_staff_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Reduce spacing

        # Header (more compact)
        header_label = QLabel("Daily Rotation Assignment")
        header_label.setStyleSheet("font-weight: bold; color: #2E7D32; font-size: 14px;")
        layout.addWidget(header_label)

        # Description
        description = QLabel("Select staff members to rotate daily. Each day will be assigned to the next staff member in sequence.")
        description.setWordWrap(True)
        description.setStyleSheet("color: #666; font-style: italic; margin: 5px 0px; font-size: 11px;")
        layout.addWidget(description)

        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)  # Limit height
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(3)

        # Staff selection area (more compact)
        staff_selection_widget = QWidget()
        staff_selection_widget.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        staff_layout = QVBoxLayout(staff_selection_widget)
        staff_layout.setSpacing(2)

        # Available staff checkboxes
        self.staff_checkboxes = {}
        self.load_staff_checkboxes(staff_layout)

        scroll_layout.addWidget(staff_selection_widget)

        # Daily rotation info (simplified)
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background-color: #e8f5e8;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(5)

        info_title = QLabel("🔄 Daily Rotation Pattern")
        info_title.setStyleSheet("font-weight: bold; color: #2E7D32; font-size: 12px;")
        info_layout.addWidget(info_title)

        info_text = QLabel("• Each day will be assigned to the next staff member in sequence\n• Pattern repeats weekly (e.g., Staff A → Staff B → Staff C → Staff A...)\n• Rotation starts from tomorrow")
        info_text.setStyleSheet("color: #333; font-size: 10px; line-height: 1.3;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        scroll_layout.addWidget(info_widget)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Preview area (expanded for better visibility)
        preview_group = QGroupBox("Daily Rotation Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.multiple_staff_preview = QLabel("Select staff members above to see the daily rotation preview")
        self.multiple_staff_preview.setStyleSheet("""
            QLabel {
                color: #0066cc;
                font-style: italic;
                font-size: 12px;
                background-color: #f0f8ff;
                border: 1px solid #4a90e2;
                border-radius: 4px;
                padding: 12px;
                line-height: 1.4;
            }
        """)
        self.multiple_staff_preview.setWordWrap(True)
        self.multiple_staff_preview.setMinimumHeight(80)  # Increased minimum height
        self.multiple_staff_preview.setMaximumHeight(120)  # Increased maximum height for better content visibility

        preview_layout.addWidget(self.multiple_staff_preview)
        layout.addWidget(preview_group)

    def load_staff_checkboxes(self, layout):
        """Load staff checkboxes for multiple selection"""
        try:
            if 'staff' in self.data:
                staff_df = self.data['staff']
                active_staff = staff_df[staff_df['status'] == 'Active']

                for _, staff in active_staff.iterrows():
                    staff_name = staff['staff_name']
                    staff_id = staff['staff_id']

                    checkbox = QCheckBox(staff_name)
                    checkbox.setToolTip(f"Include {staff_name} in the rotation")
                    checkbox.stateChanged.connect(self.on_staff_checkbox_changed)

                    self.staff_checkboxes[staff_id] = {
                        'checkbox': checkbox,
                        'name': staff_name
                    }

                    layout.addWidget(checkbox)
        except Exception as e:
            pass

    def on_staff_assignment_type_changed(self, assignment_type):
        """Handle staff assignment type change"""
        if assignment_type == "Single Staff Member":
            self.staff_combo.setVisible(True)
            self.multiple_staff_widget.setVisible(False)
        else:  # Multiple Staff (Daily Rotation)
            self.staff_combo.setVisible(False)
            self.multiple_staff_widget.setVisible(True)
            self.update_multiple_staff_preview()

        # Force layout update
        self.layout().update()
        self.adjustSize()

    def on_staff_checkbox_changed(self):
        """Handle staff checkbox state changes"""
        # Update preview for daily rotation
        self.update_multiple_staff_preview()



    def setup_staff_pattern_configs(self):
        """Setup individual pattern configurations for each staff member"""
        # Clear existing widgets
        for i in reversed(range(self.staff_pattern_layout.count())):
            child = self.staff_pattern_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Create a more organized layout for staff patterns
        selected_staff = []
        for staff_id, staff_info in self.staff_checkboxes.items():
            if staff_info['checkbox'].isChecked():
                selected_staff.append((staff_id, staff_info['name']))

        if not selected_staff:
            # Show message when no staff selected
            no_staff_label = QLabel("Please select staff members above to configure their patterns.")
            no_staff_label.setStyleSheet("color: #666; font-style: italic; padding: 10px; text-align: center;")
            self.staff_pattern_layout.addWidget(no_staff_label)
            return

        # Create a compact grid layout for multiple staff patterns
        if len(selected_staff) > 2:
            # Use a more compact approach for many staff members
            self.create_compact_staff_patterns(selected_staff)
        else:
            # Use detailed layout for few staff members
            for staff_id, staff_name in selected_staff:
                self.add_staff_pattern_config(staff_id, staff_name)

    def add_staff_pattern_config(self, staff_id, staff_name):
        """Add pattern configuration for a specific staff member (detailed view)"""
        config_widget = QWidget()
        config_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
        """)

        # Use a more organized layout
        main_layout = QVBoxLayout(config_widget)
        main_layout.setSpacing(5)

        # Staff name header
        name_label = QLabel(f"📋 {staff_name}")
        name_label.setStyleSheet("""
            font-weight: bold;
            font-size: 12px;
            color: #2c3e50;
            padding: 2px 0px;
            border-bottom: 1px solid #bdc3c7;
        """)
        main_layout.addWidget(name_label)

        # Pattern configuration in a horizontal layout
        pattern_layout = QHBoxLayout()
        pattern_layout.setSpacing(8)

        # Day configuration
        day_group = QVBoxLayout()
        day_label = QLabel("Day:")
        day_label.setStyleSheet("font-size: 10px; color: #666;")
        day_group.addWidget(day_label)

        day_spin = QSpinBox()
        day_spin.setRange(1, 31)
        day_spin.setValue(1)
        day_spin.setMaximumWidth(60)
        day_spin.valueChanged.connect(self.update_multiple_staff_preview)
        day_group.addWidget(day_spin)
        pattern_layout.addLayout(day_group)

        # Period configuration
        period_group = QVBoxLayout()
        period_label = QLabel("Period:")
        period_label.setStyleSheet("font-size: 10px; color: #666;")
        period_group.addWidget(period_label)

        period_combo = QComboBox()
        period_combo.addItems(["Week", "Month", "Year"])
        period_combo.setMaximumWidth(80)
        period_combo.currentTextChanged.connect(self.update_multiple_staff_preview)
        period_group.addWidget(period_combo)
        pattern_layout.addLayout(period_group)

        # Interval configuration
        interval_group = QVBoxLayout()
        interval_label = QLabel("Every:")
        interval_label.setStyleSheet("font-size: 10px; color: #666;")
        interval_group.addWidget(interval_label)

        interval_spin = QSpinBox()
        interval_spin.setRange(1, 12)
        interval_spin.setValue(1)
        interval_spin.setMaximumWidth(60)
        interval_spin.valueChanged.connect(self.update_multiple_staff_preview)
        interval_group.addWidget(interval_spin)
        pattern_layout.addLayout(interval_group)

        # Add stretch to push everything to the left
        pattern_layout.addStretch()

        main_layout.addLayout(pattern_layout)

        # Store references for later access
        if not hasattr(self, 'staff_pattern_configs'):
            self.staff_pattern_configs = {}

        self.staff_pattern_configs[staff_id] = {
            'day_spin': day_spin,
            'period_combo': period_combo,
            'interval_spin': interval_spin,
            'widget': config_widget
        }

        self.staff_pattern_layout.addWidget(config_widget)

    def create_compact_staff_patterns(self, selected_staff):
        """Create a more compact layout for multiple staff patterns"""
        # Create a table-like layout for multiple staff
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 10, 12, 10)  # Further increased margins for better header spacing
        header_layout.setSpacing(15)  # Add spacing between header columns

        # Headers with better proportions
        staff_label = QLabel("Staff Member")
        staff_label.setMinimumWidth(150)  # Set minimum width for staff column
        header_layout.addWidget(staff_label, 3)  # Increased proportion for staff names

        day_label = QLabel("Day")
        day_label.setMinimumWidth(60)
        header_layout.addWidget(day_label, 1)

        period_label = QLabel("Period")
        period_label.setMinimumWidth(80)
        header_layout.addWidget(period_label, 1)

        every_label = QLabel("Every")
        every_label.setMinimumWidth(60)
        header_layout.addWidget(every_label, 1)

        # Style the header
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        self.staff_pattern_layout.addWidget(header_widget)

        # Add each staff member as a compact row
        for staff_id, staff_name in selected_staff:
            self.add_compact_staff_pattern_row(staff_id, staff_name)

    def add_compact_staff_pattern_row(self, staff_id, staff_name):
        """Add a compact row for staff pattern configuration"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(12, 8, 12, 8)  # Further increased margins for better spacing
        row_layout.setSpacing(15)  # Further increased spacing between controls

        # Staff name (show more characters)
        name_label = QLabel(staff_name[:18] + "..." if len(staff_name) > 18 else staff_name)
        name_label.setToolTip(staff_name)
        name_label.setMinimumWidth(150)  # Increased minimum width
        name_label.setStyleSheet("font-weight: bold; padding: 2px;")
        row_layout.addWidget(name_label, 3)  # Increased proportion

        # Day number
        day_spin = QSpinBox()
        day_spin.setRange(1, 31)
        day_spin.setValue(1)
        day_spin.setMinimumWidth(60)  # Increased minimum width
        day_spin.setMaximumWidth(80)  # Increased maximum width
        day_spin.valueChanged.connect(self.update_multiple_staff_preview)
        row_layout.addWidget(day_spin, 1)

        # Period
        period_combo = QComboBox()
        period_combo.addItems(["Week", "Month", "Year"])
        period_combo.setMinimumWidth(80)  # Increased minimum width
        period_combo.setMaximumWidth(100)  # Increased maximum width
        period_combo.currentTextChanged.connect(self.update_multiple_staff_preview)
        row_layout.addWidget(period_combo, 1)

        # Interval
        interval_spin = QSpinBox()
        interval_spin.setRange(1, 12)
        interval_spin.setValue(1)
        interval_spin.setMinimumWidth(60)  # Increased minimum width
        interval_spin.setMaximumWidth(80)  # Increased maximum width
        interval_spin.valueChanged.connect(self.update_multiple_staff_preview)
        row_layout.addWidget(interval_spin, 1)

        # Style the row
        row_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 2px;
                margin: 1px;
            }
        """)

        # Store references
        if not hasattr(self, 'staff_pattern_configs'):
            self.staff_pattern_configs = {}

        self.staff_pattern_configs[staff_id] = {
            'day_spin': day_spin,
            'period_combo': period_combo,
            'interval_spin': interval_spin,
            'widget': row_widget
        }

        self.staff_pattern_layout.addWidget(row_widget)

    def update_multiple_staff_preview(self):
        """Update the daily rotation assignment preview"""
        try:
            selected_staff = []
            for staff_id, staff_info in self.staff_checkboxes.items():
                if staff_info['checkbox'].isChecked():
                    selected_staff.append(staff_info['name'])

            if not selected_staff:
                self.multiple_staff_preview.setText("Select staff members above to see the daily rotation preview")
                return

            if len(selected_staff) == 1:
                preview_text = f"🔄 Daily Assignment: {selected_staff[0]} will be assigned every day"
            elif len(selected_staff) <= 7:
                # Show the weekly rotation pattern
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                rotation_preview = []
                for i in range(7):
                    staff_name = selected_staff[i % len(selected_staff)]
                    short_name = staff_name[:10] + "..." if len(staff_name) > 10 else staff_name
                    rotation_preview.append(f"{days[i]}: {short_name}")

                preview_text = f"🔄 Weekly Rotation Pattern:\n" + "\n".join(rotation_preview[:4])
                if len(rotation_preview) > 4:
                    preview_text += f"\n... and {len(rotation_preview)-4} more days"
                preview_text += f"\n\n📅 Pattern repeats every week with {len(selected_staff)} staff members"
            else:
                # Many staff members
                preview_text = f"🔄 Daily Rotation: {len(selected_staff)} staff members\n📅 Each day assigned to next staff member in sequence\n🔁 Pattern repeats continuously"

            self.multiple_staff_preview.setText(preview_text)

        except Exception as e:
            self.multiple_staff_preview.setText("Unable to generate preview - please check your selection")

    def get_weekday_number(self, day_name):
        """Convert day name to weekday number (0=Monday, 6=Sunday)"""
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        return day_mapping.get(day_name.lower(), 0)

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
            assignment_type = self.staff_assignment_type.currentText()

            if assignment_type == "Multiple Staff (Daily Rotation)":
                # For multiple staff, show the multiple staff preview instead
                self.schedule_preview_label.setText("Preview: See daily rotation assignment preview below")
                return

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
        """Save enhanced task assignment with support for multiple staff"""
        try:
            if not self.task_combo.currentText():
                QMessageBox.warning(self, "Validation Error", "Please enter a task name.")
                return

            assignment_type = self.staff_assignment_type.currentText()

            if assignment_type == "Single Staff Member":
                self.save_single_staff_assignment()
            else:  # Multiple Staff (Daily Rotation)
                self.save_multiple_staff_assignment()

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to assign task: {str(e)}")

    def save_single_staff_assignment(self):
        """Save single staff assignment (original functionality)"""
        if not self.staff_combo.currentText():
            QMessageBox.warning(self, "Validation Error", "Please select a staff member.")
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

        # Add new fields if they don't exist
        self.ensure_task_columns(tasks_df)

        # Set next due date based on schedule type
        from datetime import datetime, timedelta
        now = datetime.now()

        if schedule_type == "daily":
            next_due = now + timedelta(days=schedule_interval)
        elif schedule_type == "nth_day_pattern":
            next_due = self.calculate_nth_day_pattern(now, day_number, time_period, schedule_interval)
        else:
            next_due = now + timedelta(days=1)  # Default to tomorrow

        # Create or update task
        self.create_or_update_task(tasks_df, task_name, {
            'assigned_staff_id': staff_id,
            'assigned_staff_name': staff_name,
            'schedule_type': schedule_type,
            'schedule_interval': schedule_interval,
            'day_number': day_number,
            'time_period': time_period,
            'priority': self.priority_combo.currentText(),
            'auto_assign': 1 if self.auto_assign_check.isChecked() else 0,
            'next_due': next_due.strftime('%Y-%m-%d %H:%M:%S'),
            'rotation_order': '',
            'multiple_staff_config': ''
        })

        # Save to CSV
        tasks_df.to_csv('data/cleaning_maintenance.csv', index=False)

        # Update the data dictionary to ensure changes are reflected
        self.data['cleaning_maintenance'] = tasks_df

        # Notify parent to refresh data - try multiple refresh methods
        parent = self.parent()
        refreshed = False

        # Try to find the main application window
        main_app = parent
        while main_app and not hasattr(main_app, 'refresh_all_tabs'):
            main_app = main_app.parent() if hasattr(main_app, 'parent') else None

        if main_app and hasattr(main_app, 'refresh_all_tabs'):
            # Refresh the main application
            main_app.data = main_app.load_data()  # Reload data first
            main_app.refresh_all_tabs()
            refreshed = True
        elif hasattr(parent, 'refresh_all_data'):
            parent.refresh_all_data()
            refreshed = True
        elif hasattr(parent, 'refresh_data'):
            parent.refresh_data()
            refreshed = True

        if not refreshed:
            print("Warning: Could not find refresh method in parent")

        QMessageBox.information(self, "Success",
            f"Task '{task_name}' assigned to {staff_name} with {schedule_type_text.lower()} scheduling.")

    def save_multiple_staff_assignment(self):
        """Save multiple staff assignment with daily rotation"""
        # Get selected staff
        selected_staff = []
        for staff_id, staff_info in self.staff_checkboxes.items():
            if staff_info['checkbox'].isChecked():
                selected_staff.append((staff_id, staff_info['name']))

        if not selected_staff:
            QMessageBox.warning(self, "Validation Error", "Please select at least one staff member.")
            return

        # Daily rotation logic (simplified - no complex rotation types)
        task_name = self.task_combo.currentText().strip()
        tasks_df = self.data['cleaning_maintenance']

        # Add new fields if they don't exist
        self.ensure_task_columns(tasks_df)

        from datetime import datetime, timedelta
        now = datetime.now()

        # Create a single task with daily rotation pattern
        rotation_order = ';'.join([str(staff_id) for staff_id, _ in selected_staff])
        staff_names = ', '.join([staff_name for _, staff_name in selected_staff])

        # Calculate next due date (start from tomorrow for daily rotation)
        next_due = now + timedelta(days=1)

        # Create or update task with daily rotation
        self.create_or_update_task(tasks_df, task_name, {
            'assigned_staff_id': selected_staff[0][0],  # First staff as primary
            'assigned_staff_name': staff_names,
            'schedule_type': 'daily_rotation',
            'schedule_interval': 1,  # Daily
            'day_number': 1,
            'time_period': 'Week',
            'priority': self.priority_combo.currentText(),
            'auto_assign': 1 if self.auto_assign_check.isChecked() else 0,
            'next_due': next_due.strftime('%Y-%m-%d %H:%M:%S'),
            'rotation_order': rotation_order,
            'multiple_staff_config': f'daily_rotation:{len(selected_staff)}:weekly_cycle'
        })

        success_msg = f"Task '{task_name}' assigned to {len(selected_staff)} staff members with daily rotation: {staff_names}"

        # Save to CSV
        tasks_df.to_csv('data/cleaning_maintenance.csv', index=False)

        # Update the data dictionary to ensure changes are reflected
        self.data['cleaning_maintenance'] = tasks_df

        # Notify parent to refresh data - try multiple refresh methods
        parent = self.parent()
        refreshed = False

        # Try to find the main application window
        main_app = parent
        while main_app and not hasattr(main_app, 'refresh_all_tabs'):
            main_app = main_app.parent() if hasattr(main_app, 'parent') else None

        if main_app and hasattr(main_app, 'refresh_all_tabs'):
            # Refresh the main application
            main_app.data = main_app.load_data()  # Reload data first
            main_app.refresh_all_tabs()
            refreshed = True
        elif hasattr(parent, 'refresh_all_data'):
            parent.refresh_all_data()
            refreshed = True
        elif hasattr(parent, 'refresh_data'):
            parent.refresh_data()
            refreshed = True

        if not refreshed:
            print("Warning: Could not find refresh method in parent")

        QMessageBox.information(self, "Success", success_msg)

    def ensure_task_columns(self, tasks_df):
        """Ensure all required columns exist in the tasks dataframe"""
        required_columns = [
            'day_number', 'time_period', 'rotation_order', 'multiple_staff_config'
        ]

        for column in required_columns:
            if column not in tasks_df.columns:
                if column == 'day_number':
                    tasks_df[column] = 1
                elif column == 'time_period':
                    tasks_df[column] = "Week"
                else:
                    tasks_df[column] = ''

    def create_or_update_task(self, tasks_df, task_name, task_data):
        """Create or update a task with the given data"""
        task_index = tasks_df[tasks_df['task_name'] == task_name].index

        if not task_index.empty:
            # Update existing task
            idx = task_index[0]
            for key, value in task_data.items():
                tasks_df.loc[idx, key] = value
        else:
            # Create new task
            new_task_id = tasks_df['task_id'].max() + 1 if not tasks_df.empty else 1

            new_task = {
                'task_id': new_task_id,
                'task_name': task_name,
                'frequency': self.schedule_type_combo.currentText(),
                'last_completed': '',
                'notes': f'Created via staff assignment - {self.schedule_type_combo.currentText()}'
            }

            # Add all the task data
            new_task.update(task_data)

            # Add new row to dataframe
            new_row_df = pd.DataFrame([new_task])
            tasks_df = pd.concat([tasks_df, new_row_df], ignore_index=True)
            self.data['cleaning_maintenance'] = tasks_df

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

            # For daily rotation, calculate the starting rotation index based on the current date
            if schedule_type == 'daily_rotation' and staff_rotation:
                # Calculate days since epoch to determine rotation position
                epoch_date = datetime(2024, 1, 1)  # Reference date
                days_since_epoch = (assignment_date - epoch_date).days
                rotation_index = days_since_epoch % len(staff_rotation)

            while assignment_date <= start_date + timedelta(days=days_ahead):
                # Determine assigned staff
                if staff_rotation and len(staff_rotation) > 0:
                    if schedule_type == 'daily_rotation':
                        # Daily rotation: each day gets the next staff member in sequence
                        staff_id = staff_rotation[rotation_index % len(staff_rotation)]
                        staff_name = self.get_staff_name_by_id(staff_id)
                        rotation_index += 1  # Increment for next day
                    else:
                        # Weekly/other rotation: each period gets the next staff member
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

    def get_staff_name_by_id(self, staff_id):
        """Get staff name by staff ID"""
        try:
            if 'staff' in self.data:
                staff_df = self.data['staff']
                staff_row = staff_df[staff_df['staff_id'] == staff_id]
                if not staff_row.empty:
                    return staff_row.iloc[0]['staff_name']
            return f"Staff {staff_id}"
        except Exception as e:
            self.logger.error(f"Error getting staff name for ID {staff_id}: {e}")
            return f"Staff {staff_id}"

    def get_next_assignment_date(self, current_date, schedule_type, interval, task=None):
        """Calculate the next assignment date - Enhanced for complex patterns"""
        try:
            if schedule_type == 'daily' or schedule_type == 'daily_rotation':
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
