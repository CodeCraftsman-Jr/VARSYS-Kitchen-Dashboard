"""
CSS Optimizer
Removes unsupported CSS properties and optimizes styling for Qt
"""

import re
import logging
from typing import Dict, List, Optional

class CSSOptimizer:
    """
    CSS Optimizer that:
    - Removes unsupported CSS properties (box-shadow, transform, etc.)
    - Optimizes CSS for Qt performance
    - Provides Qt-compatible alternatives
    - Reduces CSS complexity for better performance
    """
    
    # CSS properties not supported by Qt
    UNSUPPORTED_PROPERTIES = [
        'box-shadow',
        'text-shadow',
        'transform',
        'transition',
        'animation',
        'filter',
        'backdrop-filter',
        'clip-path',
        'mask',
        'opacity',  # Limited support
        'z-index',  # Not supported in Qt stylesheets
        'position',  # Not supported in Qt stylesheets
        'float',
        'display',  # Limited support
        'flex',
        'grid',
        'overflow',  # Limited support
    ]
    
    # Qt-compatible alternatives for common effects
    QT_ALTERNATIVES = {
        'box-shadow': {
            'hover_effect': 'background-color: rgba(59, 130, 246, 0.05);',
            'focus_effect': 'border: 2px solid #3b82f6;',
            'pressed_effect': 'background-color: rgba(59, 130, 246, 0.1);'
        },
        ''
        },
        'transition': {
            'remove': True  # Qt doesn't support CSS transitions
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimizations_applied = 0
        
    def optimize_css(self, css_text: str) -> str:
        """Optimize CSS text for Qt compatibility"""
        if not css_text:
            return css_text
            
        # Remove unsupported properties
        optimized_css = self.remove_unsupported_properties(css_text)
        
        # Apply Qt-specific optimizations
        optimized_css = self.apply_qt_optimizations(optimized_css)
        
        # Clean up formatting
        optimized_css = self.clean_css_formatting(optimized_css)
        
        return optimized_css
    
    def remove_unsupported_properties(self, css_text: str) -> str:
        """Remove unsupported CSS properties"""
        lines = css_text.split('\n')
        optimized_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if line contains unsupported property
            is_unsupported = False
            for prop in self.UNSUPPORTED_PROPERTIES:
                if line_stripped.startswith(prop + ':') or line_stripped.startswith(prop + ' '):
                    is_unsupported = True
                    self.optimizations_applied += 1
                    self.logger.debug(f"Removed unsupported property: {line_stripped}")
                    break
            
            if not is_unsupported:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def apply_qt_optimizations(self, css_text: str) -> str:
        """Apply Qt-specific optimizations"""
        # Replace common patterns with Qt-compatible alternatives
        
        # Replace box-shadow hover effects with background color changes
        css_text = re.sub(
            r'background-color: rgba(59, 130, 246, 0.05);]+;',
            'background-color: rgba(59, 130, 246, 0.05);',
            css_text,
            flags=re.IGNORECASE
        )
        
        # Remove transform properties
        css_text = re.sub(
            r']+;',
            '',
            css_text,
            flags=re.IGNORECASE
        )
        
        # Remove transition properties
        css_text = re.sub(
            r']+;',
            '',
            css_text,
            flags=re.IGNORECASE
        )
        
        # Optimize color values (use hex instead of rgba when possible)
        css_text = self.optimize_colors(css_text)
        
        return css_text
    
    def optimize_colors(self, css_text: str) -> str:
        """Optimize color values for better performance"""
        # Convert simple rgba to hex when alpha is 1
        css_text = re.sub(
            r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*1\.?0?\)',
            lambda m: f"#{int(m.group(1)):02x}{int(m.group(2)):02x}{int(m.group(3)):02x}",
            css_text
        )
        
        return css_text
    
    def clean_css_formatting(self, css_text: str) -> str:
        """Clean up CSS formatting"""
        # Remove empty lines
        lines = [line for line in css_text.split('\n') if line.strip()]
        
        # Remove empty rules
        cleaned_lines = []
        in_rule = False
        rule_content = []
        
        for line in lines:
            stripped = line.strip()
            
            if '{' in stripped:
                in_rule = True
                rule_content = [line]
            elif '}' in stripped and in_rule:
                rule_content.append(line)
                
                # Check if rule has any content
                has_content = any(':' in l for l in rule_content[1:-1])
                if has_content:
                    cleaned_lines.extend(rule_content)
                
                in_rule = False
                rule_content = []
            elif in_rule:
                rule_content.append(line)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_optimized_button_style(self, base_color: str = "#3b82f6") -> str:
        """Create optimized button style without unsupported properties"""
        return f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
                margin-top: 1px;
            }}
            QPushButton:disabled {{
                background-color: #9ca3af;
                color: #6b7280;
            }}
        """
    
    def create_optimized_card_style(self) -> str:
        """Create optimized card style without unsupported properties"""
        return """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin: 4px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: #f8fafc;
            }
        """
    
    def create_optimized_input_style(self) -> str:
        """Create optimized input style without unsupported properties"""
        return """
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #3b82f6;
                background-color: #f0f9ff;
            }
            QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
                border-color: #9ca3af;
            }
        """
    
    def create_optimized_table_style(self) -> str:
        """Create optimized table style without unsupported properties"""
        return """
            QTableWidget {
                gridline-color: #e5e7eb;
                selection-background-color: #dbeafe;
                selection-color: #1e40af;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 13px;
                color: #374151;
            }
        """
    
    def create_optimized_tab_style(self) -> str:
        """Create optimized tab style without unsupported properties"""
        return """
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
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f1f5f9;
                color: #475569;
            }
        """
    
    def get_performance_optimized_stylesheet(self) -> str:
        """Get a complete performance-optimized stylesheet"""
        return f"""
            /* Global Styles - Optimized for Qt */
            QMainWindow, QWidget {{
                background-color: #f8fafc;
                color: #0f172a;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
            
            /* Buttons - No unsupported properties */
            {self.create_optimized_button_style()}
            
            /* Cards and Frames - No box-shadow */
            {self.create_optimized_card_style()}
            
            /* Input Fields - No transitions */
            {self.create_optimized_input_style()}
            
            /* Tables - Optimized rendering */
            {self.create_optimized_table_style()}
            
            /* Tabs - Clean styling */
            {self.create_optimized_tab_style()}
            
            /* Group Boxes */
            QGroupBox {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-top: 16px;
                font-weight: 600;
                font-size: 14px;
                color: #0f172a;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-
                padding: 0 8px;
                background-color: white;
                color: #0f172a;
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                background-color: #f1f5f9;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #cbd5e1;
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #94a3b8;
            }}
            
            /* Labels */
            QLabel {{
                color: #374151;
                font-size: 13px;
            }}
            
            /* Progress Bars */
            QProgressBar {{
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                background-color: #f3f4f6;
                height: 16px;
            }}
            QProgressBar::chunk {{
                background-color: #3b82f6;
                border-radius: 3px;
            }}
        """
    
    def get_optimization_stats(self) -> Dict[str, int]:
        """Get optimization statistics"""
        return {
            "optimizations_applied": self.optimizations_applied,
            "unsupported_properties_count": len(self.UNSUPPORTED_PROPERTIES)
        }

# Global CSS optimizer instance
_css_optimizer = None

def get_css_optimizer():
    """Get global CSS optimizer instance"""
    global _css_optimizer
    if _css_optimizer is None:
        _css_optimizer = CSSOptimizer()
    return _css_optimizer

def optimize_stylesheet(css_text: str) -> str:
    """Optimize a stylesheet for Qt compatibility"""
    optimizer = get_css_optimizer()
    return optimizer.optimize_css(css_text)

def get_optimized_stylesheet() -> str:
    """Get the complete optimized stylesheet"""
    optimizer = get_css_optimizer()
    return optimizer.get_performance_optimized_stylesheet()
