#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Qt Effects
Quick test to verify Qt-native shadow effects are working
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

def test_qt_effects():
    """Test Qt-native effects"""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Qt Effects Test")
    window.setGeometry(100, 100, 600, 400)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Test title with shadow
    title = QLabel("VARSYS Kitchen Dashboard")
    title.setFont(QFont("Segoe UI", 20, QFont.Bold))
    title.setStyleSheet("color: #2563eb; padding: 20px;")
    title.setAlignment(Qt.AlignCenter)
    
    # Apply Qt-native text shadow
    try:
        from utils.qt_effects import add_title_shadow
        add_title_shadow(title)
        print("✅ Title shadow applied successfully")
    except Exception as e:
        print(f"❌ Title shadow failed: {e}")
    
    layout.addWidget(title)
    
    # Test buttons with hover shadows
    button_layout = QHBoxLayout()
    
    for i, text in enumerate(["Button 1", "Button 2", "Button 3"]):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        
        # Apply Qt-native shadow
        try:
            from utils.qt_effects import add_button_hover_shadow
            add_button_hover_shadow(button)
            print(f"✅ Button {i+1} shadow applied successfully")
        except Exception as e:
            print(f"❌ Button {i+1} shadow failed: {e}")
        
        button_layout.addWidget(button)
    
    layout.addLayout(button_layout)
    
    # Test card with shadow
    card = QFrame()
    card.setStyleSheet("""
        QFrame {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin: 10px;
        }
    """)
    
    card_layout = QVBoxLayout(card)
    card_title = QLabel("Test Card")
    card_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
    card_content = QLabel("This card should have a subtle shadow effect applied using Qt's native QGraphicsDropShadowEffect instead of CSS box-shadow.")
    card_content.setWordWrap(True)
    
    card_layout.addWidget(card_title)
    card_layout.addWidget(card_content)
    
    # Apply Qt-native card shadow
    try:
        from utils.qt_effects import add_card_shadow
        add_card_shadow(card)
        print("✅ Card shadow applied successfully")
    except Exception as e:
        print(f"❌ Card shadow failed: {e}")
    
    layout.addWidget(card)
    
    # Status label
    status = QLabel("Qt Effects Test - Check console for results")
    status.setAlignment(Qt.AlignCenter)
    status.setStyleSheet("color: #64748b; font-style: italic; padding: 10px;")
    layout.addWidget(status)
    
    # Show window
    window.show()
    
    print("\n" + "="*50)
    print("Qt Effects Test Results:")
    print("- Title should have text shadow")
    print("- Buttons should have hover shadows")
    print("- Card should have subtle drop shadow")
    print("- No CSS shadow warnings in console")
    print("="*50)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_qt_effects())
