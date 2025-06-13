#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic UI Test
Test the basic UI components to identify white screen issue
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class BasicUITest(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("VARSYS Kitchen Dashboard - UI Test")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        print("✅ Window created")
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        print("✅ Central widget set")
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        print("✅ Main layout created")
        
        # Create splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        print("✅ Splitter created")
        
        # Create sidebar
        self.create_sidebar()
        print("✅ Sidebar created")
        
        # Create content area
        self.create_content_area()
        print("✅ Content area created")
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.main_splitter)
        print("✅ Splitter added to layout")
        
        # Set splitter sizes
        self.main_splitter.setSizes([240, 800])
        print("✅ Splitter sizes set")
        
        # Apply basic styling
        self.apply_basic_styling()
        print("✅ Basic styling applied")
        
        print("🎉 UI Test completed successfully!")
    
    def create_sidebar(self):
        """Create a simple sidebar"""
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #2563eb;
                border-radius: 0px 15px 15px 0px;
                min-width: 200px;
                max-width: 300px;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(10)
        
        # Title
        title = QLabel("VARSYS")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Navigation buttons
        nav_buttons = ["🏠 Dashboard", "📊 Analytics", "🍽️ Menu", "💰 Sales", "⚙️ Settings"]
        
        for button_text in nav_buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """)
            sidebar_layout.addWidget(button)
        
        sidebar_layout.addStretch()
        
        # Add to splitter
        self.main_splitter.addWidget(self.sidebar)
    
    def create_content_area(self):
        """Create a simple content area"""
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                border-radius: 10px;
                min-width: 400px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Header
        header = QLabel("Kitchen Dashboard")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b; margin-bottom: 20px;")
        content_layout.addWidget(header)
        
        # Welcome message
        welcome = QLabel("Welcome to VARSYS Kitchen Dashboard!")
        welcome.setStyleSheet("font-size: 16px; color: #64748b; margin-bottom: 30px;")
        content_layout.addWidget(welcome)
        
        # Test cards
        for i in range(3):
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 5px;
                }
            """)
            
            card_layout = QVBoxLayout(card)
            
            card_title = QLabel(f"Test Card {i+1}")
            card_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b; margin-bottom: 10px;")
            card_layout.addWidget(card_title)
            
            card_content = QLabel(f"This is test content for card {i+1}. The UI is working correctly!")
            card_content.setStyleSheet("font-size: 14px; color: #64748b;")
            card_content.setWordWrap(True)
            card_layout.addWidget(card_content)
            
            content_layout.addWidget(card)
        
        content_layout.addStretch()
        
        # Add to splitter
        self.main_splitter.addWidget(self.content_widget)
    
    def apply_basic_styling(self):
        """Apply basic application styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f1f5f9;
            }
            QSplitter::handle {
                background-color: #cbd5e1;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #94a3b8;
            }
        """)

def main():
    """Main function to test basic UI"""
    print("🚀 Starting Basic UI Test...")
    
    # Set Qt attributes before QApplication creation
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    app = QApplication(sys.argv)
    print("✅ QApplication created")
    
    # Create and show window
    window = BasicUITest()
    print("✅ Window created")
    
    window.show()
    print("✅ Window shown")
    
    print("🎯 If you see this message and a working UI, the basic components are fine!")
    print("🔍 Check the console for any error messages...")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
