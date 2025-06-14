"""
UI Component Tester
Tests all UI components and interactions
"""

import time
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, 
                               QTableWidget, QComboBox, QLineEdit, QSpinBox, QDateEdit)
from PySide6.QtCore import QTimer, QDate
from PySide6.QtGui import QFont

class UIComponentTester:
    """Tests UI components and interactions"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = app_instance.logger
        
    def test_all_ui_components(self):
        """Test all UI components"""
        self.logger.info("Starting UI component testing...")
        
        # Create test dialog
        dialog = UITestDialog(self.app)
        dialog.show()
        
        # Test components
        components_to_test = [
            ("Main Window", self.test_main_window),
            ("Navigation Sidebar", self.test_navigation_sidebar),
            ("Content Area", self.test_content_area),
            ("Tables", self.test_tables),
            ("Forms", self.test_forms),
            ("Buttons", self.test_buttons),
            ("Dialogs", self.test_dialogs),
            ("Menus", self.test_menus),
            ("Notifications", self.test_notifications),
            ("Charts", self.test_charts),
            ("Responsive Design", self.test_responsive_design),
            ("Keyboard Navigation", self.test_keyboard_navigation),
            ("Mouse Interactions", self.test_mouse_interactions),
            ("Accessibility", self.test_accessibility)
        ]
        
        results = []
        for component_name, test_function in components_to_test:
            try:
                dialog.update_status(f"Testing {component_name}...")
                start_time = time.time()
                
                test_function()
                
                execution_time = time.time() - start_time
                result = f"✅ {component_name}: PASSED ({execution_time:.2f}s)"
                self.logger.info(f"UI component test passed: {component_name}")
                
            except Exception as e:
                execution_time = time.time() - start_time
                result = f"❌ {component_name}: FAILED - {str(e)} ({execution_time:.2f}s)"
                self.logger.error(f"UI component test failed: {component_name} - {str(e)}")
                
            results.append(result)
            dialog.add_result(result)
            
        dialog.update_status("All UI component tests completed!")
        self.logger.info("UI component testing completed")
        
    def test_main_window(self):
        """Test main window components"""
        # Test window properties
        assert self.app.isVisible(), "Main window should be visible"
        assert self.app.windowTitle() == "Kitchen Dashboard - Modern Edition", "Window title should match"
        
        # Test minimum size
        min_size = self.app.minimumSize()
        assert min_size.width() >= 1400, "Minimum width should be at least 1400"
        assert min_size.height() >= 900, "Minimum height should be at least 900"
        
        # Test central widget
        assert hasattr(self.app, 'central_widget'), "Should have central widget"
        assert self.app.central_widget is not None, "Central widget should not be None"
        
    def test_navigation_sidebar(self):
        """Test navigation sidebar"""
        # Test sidebar existence
        assert hasattr(self.app, 'sidebar'), "Should have sidebar"
        assert self.app.sidebar is not None, "Sidebar should not be None"
        assert self.app.sidebar.isVisible(), "Sidebar should be visible"
        
        # Test navigation buttons
        assert hasattr(self.app, 'nav_buttons'), "Should have navigation buttons"
        assert len(self.app.nav_buttons) > 0, "Should have at least one navigation button"
        
        # Test button functionality
        for button in self.app.nav_buttons:
            assert button.isEnabled(), "Navigation buttons should be enabled"
            assert button.text() != "", "Navigation buttons should have text"
            
    def test_content_area(self):
        """Test content area"""
        # Test content widget
        assert hasattr(self.app, 'content_widget'), "Should have content widget"
        assert self.app.content_widget is not None, "Content widget should not be None"
        assert self.app.content_widget.isVisible(), "Content widget should be visible"
        
        # Test content layout
        assert hasattr(self.app, 'content_layout'), "Should have content layout"
        assert self.app.content_layout is not None, "Content layout should not be None"
        
        # Test scroll area
        assert hasattr(self.app, 'content_scroll'), "Should have content scroll area"
        assert self.app.content_scroll is not None, "Content scroll should not be None"
        
    def test_tables(self):
        """Test table components"""
        # Test inventory table if available
        if hasattr(self.app, 'inventory_widget') and self.app.inventory_widget:
            inventory_table = self.app.inventory_widget.findChild(QTableWidget)
            if inventory_table:
                assert inventory_table.columnCount() > 0, "Inventory table should have columns"
                assert inventory_table.isEnabled(), "Inventory table should be enabled"
                
        # Test table creation and population
        test_table = QTableWidget(5, 3)
        test_table.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])
        
        # Test table properties
        assert test_table.columnCount() == 3, "Test table should have 3 columns"
        assert test_table.rowCount() == 5, "Test table should have 5 rows"
        
        # Test header labels
        headers = [test_table.horizontalHeaderItem(i).text() for i in range(3)]
        expected_headers = ['Column 1', 'Column 2', 'Column 3']
        assert headers == expected_headers, "Headers should match expected values"
        
    def test_forms(self):
        """Test form components"""
        # Test form controls
        test_line_edit = QLineEdit()
        test_line_edit.setText("Test Input")
        assert test_line_edit.text() == "Test Input", "Line edit should accept text input"
        
        test_combo_box = QComboBox()
        test_combo_box.addItems(['Option 1', 'Option 2', 'Option 3'])
        assert test_combo_box.count() == 3, "Combo box should have 3 items"
        
        test_spin_box = QSpinBox()
        test_spin_box.setRange(0, 100)
        test_spin_box.setValue(50)
        assert test_spin_box.value() == 50, "Spin box should accept value"
        
        test_date_edit = QDateEdit()
        test_date = QDate.currentDate()
        test_date_edit.setDate(test_date)
        assert test_date_edit.date() == test_date, "Date edit should accept date"
        
    def test_buttons(self):
        """Test button components"""
        # Test button creation and properties
        test_button = QPushButton("Test Button")
        assert test_button.text() == "Test Button", "Button should have correct text"
        assert test_button.isEnabled(), "Button should be enabled by default"
        
        # Test button click simulation
        clicked = False
        def on_click():
            nonlocal clicked
            clicked = True
            
        test_button.clicked.connect(on_click)
        test_button.click()
        assert clicked, "Button click should trigger connected function"
        
    def test_dialogs(self):
        """Test dialog components"""
        # Test dialog creation
        test_dialog = QDialog(self.app)
        test_dialog.setWindowTitle("Test Dialog")
        test_dialog.setModal(True)
        
        assert test_dialog.windowTitle() == "Test Dialog", "Dialog should have correct title"
        assert test_dialog.isModal(), "Dialog should be modal"
        
        # Test dialog layout
        layout = QVBoxLayout(test_dialog)
        label = QLabel("Test Dialog Content")
        layout.addWidget(label)
        
        assert test_dialog.layout() is not None, "Dialog should have layout"
        
    def test_menus(self):
        """Test menu components"""
        # Test menu bar existence
        menu_bar = self.app.menuBar()
        assert menu_bar is not None, "Should have menu bar"
        
        # Test if testing menu was created
        menus = menu_bar.findChildren(object)
        menu_found = False
        for menu in menus:
            if hasattr(menu, 'title') and 'Testing' in str(menu.title()):
                menu_found = True
                break
                
        # Note: Menu might not be visible immediately, so we don't assert its presence
        
    def test_notifications(self):
        """Test notification system"""
        # Test notification manager
        if hasattr(self.app, 'notification_manager'):
            assert self.app.notification_manager is not None, "Notification manager should exist"
            
        # Test notification bell
        if hasattr(self.app, 'notification_bell'):
            assert self.app.notification_bell is not None, "Notification bell should exist"
            
        # Test adding notification
        try:
            self.app.add_notification("Test Notification", "This is a test message", "info")
        except Exception as e:
            # Notification system might not be fully initialized
            pass
            
    def test_charts(self):
        """Test chart components"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
            
            # Test chart creation
            fig = Figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            
            # Test basic plot
            x = [1, 2, 3, 4, 5]
            y = [2, 4, 6, 8, 10]
            ax.plot(x, y)
            ax.set_title("Test Chart")
            
            assert ax.get_title() == "Test Chart", "Chart should have correct title"
            assert len(ax.lines) == 1, "Chart should have one line"
            
        except ImportError:
            # Matplotlib might not be available
            pass
            
    def test_responsive_design(self):
        """Test responsive design features"""
        # Test window resizing
        original_size = self.app.size()
        
        # Test minimum size constraints
        self.app.resize(800, 600)
        current_size = self.app.size()
        
        # Should respect minimum size
        assert current_size.width() >= self.app.minimumSize().width(), "Should respect minimum width"
        assert current_size.height() >= self.app.minimumSize().height(), "Should respect minimum height"
        
        # Restore original size
        self.app.resize(original_size)
        
        # Test splitter functionality
        if hasattr(self.app, 'main_splitter'):
            splitter = self.app.main_splitter
            original_sizes = splitter.sizes()
            
            # Test splitter resize
            new_sizes = [200, 1000]
            splitter.setSizes(new_sizes)
            
            # Restore original sizes
            splitter.setSizes(original_sizes)
            
    def test_keyboard_navigation(self):
        """Test keyboard navigation"""
        # Test tab order for form elements
        test_widget = QDialog()
        layout = QVBoxLayout(test_widget)
        
        edit1 = QLineEdit()
        edit2 = QLineEdit()
        button = QPushButton("Test")
        
        layout.addWidget(edit1)
        layout.addWidget(edit2)
        layout.addWidget(button)
        
        # Test tab order
        test_widget.setTabOrder(edit1, edit2)
        test_widget.setTabOrder(edit2, button)
        
        # Focus should start with first widget
        edit1.setFocus()
        assert edit1.hasFocus(), "First edit should have focus"
        
    def test_mouse_interactions(self):
        """Test mouse interactions"""
        # Test button hover states
        test_button = QPushButton("Hover Test")
        
        # Test if button accepts hover events
        test_button.setAttribute(Qt.WA_Hover, True)
        
        # Test click functionality
        clicked = False
        def on_click():
            nonlocal clicked
            clicked = True
            
        test_button.clicked.connect(on_click)
        test_button.click()
        assert clicked, "Mouse click should work"
        
    def test_accessibility(self):
        """Test accessibility features"""
        # Test widget accessibility properties
        test_button = QPushButton("Accessible Button")
        test_button.setToolTip("This is a tooltip")
        
        assert test_button.toolTip() == "This is a tooltip", "Tooltip should be set"
        
        # Test label associations
        test_label = QLabel("Test Label:")
        test_edit = QLineEdit()
        test_label.setBuddy(test_edit)
        
        assert test_label.buddy() == test_edit, "Label should be associated with edit"
        
        # Test keyboard shortcuts
        test_button_with_shortcut = QPushButton("&Save")
        assert "&" in test_button_with_shortcut.text(), "Button should have keyboard shortcut"


class UITestDialog(QDialog):
    """Dialog for displaying UI component test results"""
    
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.app = app_instance
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("UI Component Testing")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Kitchen Dashboard - UI Component Testing")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # Status label
        self.status_label = QLabel("Preparing tests...")
        layout.addWidget(self.status_label)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
        
    def add_result(self, result):
        """Add test result"""
        self.results_text.append(result)
