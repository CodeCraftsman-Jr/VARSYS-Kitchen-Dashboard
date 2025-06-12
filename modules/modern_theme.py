"""
Modern Theme and Styling for Kitchen Dashboard
Provides contemporary UI styling with better space utilization
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont

class ModernTheme:
    """Modern theme with contemporary colors and styling"""
    
    # Color Palette
    COLORS = {
        # Primary Colors
        'primary': '#2563eb',           # Blue 600
        'primary_hover': '#1d4ed8',     # Blue 700
        'primary_light': '#dbeafe',     # Blue 100
        
        # Secondary Colors
        'secondary': '#64748b',         # Slate 500
        'secondary_hover': '#475569',   # Slate 600
        'secondary_light': '#f1f5f9',   # Slate 100
        
        # Background Colors
        'bg_primary': '#ffffff',        # White
        'bg_secondary': '#f8fafc',      # Slate 50
        'bg_tertiary': '#f1f5f9',       # Slate 100
        'bg_dark': '#0f172a',           # Slate 900
        
        # Text Colors
        'text_primary': '#0f172a',      # Slate 900
        'text_secondary': '#475569',    # Slate 600
        'text_muted': '#94a3b8',        # Slate 400
        'text_white': '#ffffff',        # White
        
        # Status Colors
        'success': '#10b981',           # Emerald 500
        'success_light': '#d1fae5',     # Emerald 100
        'warning': '#f59e0b',           # Amber 500
        'warning_light': '#fef3c7',     # Amber 100
        'error': '#ef4444',             # Red 500
        'error_light': '#fee2e2',       # Red 100
        'info': '#3b82f6',              # Blue 500
        'info_light': '#dbeafe',        # Blue 100
        
        # Border Colors
        'border': '#e2e8f0',            # Slate 200
        'border_hover': '#cbd5e1',      # Slate 300
        'border_focus': '#2563eb',      # Blue 600
        
        # Shadow Colors
        'shadow_light': 'rgba(0, 0, 0, 0.05)',
        'shadow_medium': 'rgba(0, 0, 0, 0.1)',
        'shadow_heavy': 'rgba(0, 0, 0, 0.25)',
    }
    
    # Typography
    FONTS = {
        'heading_xl': ('Segoe UI', 28, QFont.Weight.Bold),
        'heading_lg': ('Segoe UI', 24, QFont.Weight.Bold),
        'heading_md': ('Segoe UI', 20, QFont.Weight.Bold),
        'heading_sm': ('Segoe UI', 16, QFont.Weight.Bold),
        'body_lg': ('Segoe UI', 14, QFont.Weight.Normal),
        'body_md': ('Segoe UI', 12, QFont.Weight.Normal),
        'body_sm': ('Segoe UI', 11, QFont.Weight.Normal),
        'caption': ('Segoe UI', 10, QFont.Weight.Normal),
        'button': ('Segoe UI', 12, QFont.Weight.Medium),
    }
    
    # Spacing
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        'xxl': '48px',
    }
    
    # Border Radius
    RADIUS = {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '50%',
    }

    @classmethod
    def get_stylesheet(cls):
        """Get the complete modern stylesheet"""
        return f"""
        /* Global Styles */
        QMainWindow, QWidget {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            font-family: 'Segoe UI', sans-serif;
        }}
        
        /* Cards and Containers */
        QGroupBox {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['lg']};
            padding: {cls.SPACING['md']};
            margin-top: {cls.SPACING['md']};
            font-weight: 600;
            font-size: 14px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-
            padding: 0 {cls.SPACING['sm']};
            background-color: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QFrame {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['md']};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_white']};
            border: none;
            border-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            font-weight: 500;
            font-size: 12px;
            min-height: 36px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['primary_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['primary_hover']};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['secondary_light']};
            color: {cls.COLORS['text_muted']};
        }}
        
        /* Secondary Button */
        QPushButton[class="secondary"] {{
            background-color: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {cls.COLORS['bg_tertiary']};
            border-color: {cls.COLORS['border_hover']};
        }}
        
        /* Success Button */
        QPushButton[class="success"] {{
            background-color: {cls.COLORS['success']};
        }}
        
        QPushButton[class="success"]:hover {{
            background-color: #059669;
        }}
        
        /* Warning Button */
        QPushButton[class="warning"] {{
            background-color: {cls.COLORS['warning']};
        }}
        
        QPushButton[class="warning"]:hover {{
            background-color: #d97706;
        }}
        
        /* Error Button */
        QPushButton[class="error"] {{
            background-color: {cls.COLORS['error']};
        }}
        
        QPushButton[class="error"]:hover {{
            background-color: #dc2626;
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            font-size: 12px;
            min-height: 36px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
            border-color: {cls.COLORS['border_focus']};
            outline: none;
        }}
        
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover, QTimeEdit:hover, QDateTimeEdit:hover {{
            border-color: {cls.COLORS['border_hover']};
        }}
        
        /* ComboBox */
        QComboBox {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            font-size: 12px;
            min-height: 36px;
        }}
        
        QComboBox:hover {{
            border-color: {cls.COLORS['border_hover']};
        }}
        
        QComboBox:focus {{
            border-color: {cls.COLORS['border_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.COLORS['text_secondary']};
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['md']};
            selection-background-color: {cls.COLORS['primary_light']};
            selection-color: {cls.COLORS['text_primary']};
        }}
        
        /* Tables */
        QTableWidget {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['lg']};
            gridline-color: {cls.COLORS['border']};
            selection-background-color: {cls.COLORS['primary_light']};
            selection-color: {cls.COLORS['text_primary']};
            font-size: 12px;
        }}
        
        QTableWidget::item {{
            padding: {cls.SPACING['sm']};
            border-bottom: 1px solid {cls.COLORS['border']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {cls.COLORS['primary_light']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QHeaderView::section {{
            background-color: {cls.COLORS['bg_tertiary']};
            border: none;
            border-bottom: 1px solid {cls.COLORS['border']};
            border-right: 1px solid {cls.COLORS['border']};
            padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            font-weight: 600;
            font-size: 12px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QHeaderView::section:first {{
            border-top-left-radius: {cls.RADIUS['lg']};
        }}
        
        QHeaderView::section:last {{
            border-top-right-radius: {cls.RADIUS['lg']};
            border-right: none;
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            background-color: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['lg']};
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border']};
            border-bottom: none;
            border-top-left-radius: {cls.RADIUS['md']};
            border-top-right-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            margin-right: 2px;
            font-size: 12px;
            font-weight: 500;
            color: {cls.COLORS['text_secondary']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['bg_primary']};
            border-bottom: 1px solid {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {cls.COLORS['secondary_light']};
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {cls.COLORS['bg_tertiary']};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['secondary']};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['secondary_hover']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.COLORS['bg_tertiary']};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['secondary']};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['secondary_hover']};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
        }}
        
        /* Labels */
        QLabel {{
            color: {cls.COLORS['text_primary']};
            font-size: 12px;
        }}
        
        QLabel[class="heading"] {{
            font-size: 16px;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
        }}
        
        QLabel[class="subheading"] {{
            font-size: 14px;
            font-weight: 500;
            color: {cls.COLORS['text_secondary']};
        }}
        
        QLabel[class="caption"] {{
            font-size: 10px;
            color: {cls.COLORS['text_muted']};
        }}
        
        /* Status Labels */
        QLabel[class="success"] {{
            color: {cls.COLORS['success']};
            font-weight: 500;
        }}
        
        QLabel[class="warning"] {{
            color: {cls.COLORS['warning']};
            font-weight: 500;
        }}
        
        QLabel[class="error"] {{
            color: {cls.COLORS['error']};
            font-weight: 500;
        }}
        
        QLabel[class="info"] {{
            color: {cls.COLORS['info']};
            font-weight: 500;
        }}
        """

    @classmethod
    def apply_theme(cls, app):
        """Apply the modern theme to the application"""
        app.setStyleSheet(cls.get_stylesheet())
        
        # Set application font
        font = QFont('Segoe UI', 10)
        app.setFont(font)

    @classmethod
    def get_font(cls, font_type):
        """Get a specific font from the theme"""
        if font_type in cls.FONTS:
            family, size, weight = cls.FONTS[font_type]
            font = QFont(family, size)
            font.setWeight(weight)
            return font
        return QFont('Segoe UI', 10)

    @classmethod
    def get_color(cls, color_name):
        """Get a specific color from the theme"""
        return cls.COLORS.get(color_name, '#000000')
