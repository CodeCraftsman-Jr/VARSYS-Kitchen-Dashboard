"""
Responsive Chart Utilities
Utilities for making matplotlib charts responsive across different screen sizes
"""

import logging
from typing import Optional, Dict, Any, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

# Import matplotlib components
try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    Figure = None
    FigureCanvas = None

# Import responsive design manager
try:
    from .responsive_design_manager import get_responsive_manager, DeviceType
except ImportError:
    def get_responsive_manager():
        return None
    
    class DeviceType:
        MOBILE = "mobile"
        TABLET = "tablet"
        DESKTOP = "desktop"
        LARGE_DESKTOP = "large_desktop"

class ResponsiveChartWidget(QWidget):
    """A responsive chart widget that adapts to different screen sizes"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.logger = logging.getLogger(__name__)
        self.responsive_manager = get_responsive_manager()
        
        # Chart components
        self.figure = None
        self.canvas = None
        self.axes = None
        
        # Setup UI
        self.setup_ui()
        
        # Apply initial responsive behavior
        self.apply_responsive_behavior()
        
    def setup_ui(self):
        """Setup the chart widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure and canvas
            self.figure = Figure(facecolor='white')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            layout.addWidget(self.canvas)
            
            # Create axes
            self.axes = self.figure.add_subplot(111)
            
        else:
            # Fallback for when matplotlib is not available
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("Charts require matplotlib\nInstall with: pip install matplotlib")
            fallback_label.setAlignment(Qt.AlignCenter)
            fallback_label.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            layout.addWidget(fallback_label)
            
    def apply_responsive_behavior(self):
        """Apply responsive behavior based on current device type"""
        if not MATPLOTLIB_AVAILABLE or not self.responsive_manager:
            return
            
        device_type = self.responsive_manager.current_device_type
        
        # Get responsive dimensions
        width, height = self.get_responsive_dimensions(device_type)
        
        # Update figure size
        self.figure.set_size_inches(width, height)
        
        # Apply responsive styling
        self.apply_responsive_styling(device_type)
        
        # Update layout
        self.update_layout(device_type)
        
        # Refresh canvas
        if self.canvas:
            self.canvas.draw()
            
    def get_responsive_dimensions(self, device_type: DeviceType) -> Tuple[float, float]:
        """Get responsive chart dimensions based on device type"""
        dimension_map = {
            DeviceType.MOBILE: (6, 4),
            DeviceType.TABLET: (8, 5),
            DeviceType.DESKTOP: (10, 6),
            DeviceType.LARGE_DESKTOP: (12, 7)
        }
        
        return dimension_map.get(device_type, (10, 6))
        
    def apply_responsive_styling(self, device_type: DeviceType):
        """Apply responsive styling to chart elements"""
        if not self.axes:
            return
            
        # Font size mapping
        font_size_map = {
            DeviceType.MOBILE: {'title': 12, 'label': 10, 'tick': 8, 'legend': 8},
            DeviceType.TABLET: {'title': 14, 'label': 11, 'tick': 9, 'legend': 9},
            DeviceType.DESKTOP: {'title': 16, 'label': 12, 'tick': 10, 'legend': 10},
            DeviceType.LARGE_DESKTOP: {'title': 18, 'label': 14, 'tick': 12, 'legend': 12}
        }
        
        font_sizes = font_size_map.get(device_type, font_size_map[DeviceType.DESKTOP])
        
        # Apply title styling
        if self.title:
            self.axes.set_title(self.title, fontsize=font_sizes['title'], 
                              fontweight='bold', color='#2c3e50', pad=20)
        
        # Apply label styling
        self.axes.tick_params(axis='both', which='major', labelsize=font_sizes['tick'])
        
        # Apply legend styling if present
        legend = self.axes.get_legend()
        if legend:
            legend.set_fontsize(font_sizes['legend'])
            
        # Set spine colors
        for spine in self.axes.spines.values():
            spine.set_color('#e2e8f0')
            spine.set_linewidth(1)
            
        # Hide top and right spines for cleaner look
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        
        # Set grid
        self.axes.grid(True, linestyle='--', alpha=0.3, color='#e2e8f0')
        self.axes.set_axisbelow(True)
        
    def update_layout(self, device_type: DeviceType):
        """Update chart layout based on device type"""
        if not self.figure:
            return
            
        # Layout parameters based on device type
        layout_params = {
            DeviceType.MOBILE: {'left': 0.15, 'right': 0.95, 'top': 0.9, 'bottom': 0.15},
            DeviceType.TABLET: {'left': 0.12, 'right': 0.95, 'top': 0.9, 'bottom': 0.12},
            DeviceType.DESKTOP: {'left': 0.1, 'right': 0.95, 'top': 0.9, 'bottom': 0.1},
            DeviceType.LARGE_DESKTOP: {'left': 0.08, 'right': 0.96, 'top': 0.92, 'bottom': 0.08}
        }
        
        params = layout_params.get(device_type, layout_params[DeviceType.DESKTOP])
        self.figure.subplots_adjust(**params)
        
    def create_pie_chart(self, data: Dict[str, float], title: str = ""):
        """Create a responsive pie chart"""
        if not MATPLOTLIB_AVAILABLE or not self.axes:
            return
            
        # Clear previous chart
        self.axes.clear()
        
        # Prepare data
        labels = list(data.keys())
        values = list(data.values())
        
        # Color palette
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        
        # Create pie chart
        wedges, texts, autotexts = self.axes.pie(
            values, 
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(labels)],
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        # Set title
        if title:
            self.title = title
            
        # Apply responsive styling
        self.apply_responsive_behavior()
        
    def create_bar_chart(self, data: Dict[str, float], title: str = "", xlabel: str = "", ylabel: str = ""):
        """Create a responsive bar chart"""
        if not MATPLOTLIB_AVAILABLE or not self.axes:
            return
            
        # Clear previous chart
        self.axes.clear()
        
        # Prepare data
        labels = list(data.keys())
        values = list(data.values())
        
        # Create bar chart
        bars = self.axes.bar(labels, values, color='#3498db', alpha=0.8, edgecolor='white', linewidth=1)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height,
                         f'{height:.1f}', ha='center', va='bottom')
        
        # Set labels
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)
        if title:
            self.title = title
            
        # Rotate x-axis labels if needed
        if self.responsive_manager and self.responsive_manager.current_device_type == DeviceType.MOBILE:
            self.axes.tick_params(axis='x', rotation=45)
            
        # Apply responsive styling
        self.apply_responsive_behavior()
        
    def create_line_chart(self, data: Dict[str, list], title: str = "", xlabel: str = "", ylabel: str = ""):
        """Create a responsive line chart"""
        if not MATPLOTLIB_AVAILABLE or not self.axes:
            return
            
        # Clear previous chart
        self.axes.clear()
        
        # Create line chart
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        
        for i, (label, values) in enumerate(data.items()):
            color = colors[i % len(colors)]
            self.axes.plot(values, label=label, color=color, linewidth=2, marker='o', markersize=4)
        
        # Add legend if multiple lines
        if len(data) > 1:
            self.axes.legend()
            
        # Set labels
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)
        if title:
            self.title = title
            
        # Apply responsive styling
        self.apply_responsive_behavior()
        
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        if self.responsive_manager:
            # Update responsive behavior when widget is resized
            self.apply_responsive_behavior()

class ResponsiveChartManager:
    """Manager for creating and managing responsive charts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.responsive_manager = get_responsive_manager()
        
    def create_chart_widget(self, title: str = "", parent=None) -> ResponsiveChartWidget:
        """Create a new responsive chart widget"""
        return ResponsiveChartWidget(title, parent)
        
    def make_figure_responsive(self, figure, device_type: DeviceType = None):
        """Make an existing matplotlib figure responsive"""
        if not MATPLOTLIB_AVAILABLE or not figure:
            return
            
        if device_type is None and self.responsive_manager:
            device_type = self.responsive_manager.current_device_type
        elif device_type is None:
            device_type = DeviceType.DESKTOP
            
        # Apply responsive dimensions
        width, height = self._get_responsive_dimensions(device_type)
        figure.set_size_inches(width, height)
        
        # Apply responsive styling to all axes
        font_sizes = self._get_font_sizes(device_type)
        
        for ax in figure.get_axes():
            # Apply font sizes
            if ax.get_title():
                ax.set_title(ax.get_title(), fontsize=font_sizes['title'])
            if ax.get_xlabel():
                ax.set_xlabel(ax.get_xlabel(), fontsize=font_sizes['label'])
            if ax.get_ylabel():
                ax.set_ylabel(ax.get_ylabel(), fontsize=font_sizes['label'])
                
            ax.tick_params(axis='both', which='major', labelsize=font_sizes['tick'])
            
            # Apply styling
            for spine in ax.spines.values():
                spine.set_color('#e2e8f0')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, linestyle='--', alpha=0.3, color='#e2e8f0')
            ax.set_axisbelow(True)
            
        # Update layout
        layout_params = self._get_layout_params(device_type)
        figure.subplots_adjust(**layout_params)
        figure.tight_layout()
        
    def _get_responsive_dimensions(self, device_type: DeviceType) -> Tuple[float, float]:
        """Get responsive dimensions for device type"""
        dimension_map = {
            DeviceType.MOBILE: (6, 4),
            DeviceType.TABLET: (8, 5),
            DeviceType.DESKTOP: (10, 6),
            DeviceType.LARGE_DESKTOP: (12, 7)
        }
        return dimension_map.get(device_type, (10, 6))
        
    def _get_font_sizes(self, device_type: DeviceType) -> Dict[str, int]:
        """Get font sizes for device type"""
        font_size_map = {
            DeviceType.MOBILE: {'title': 12, 'label': 10, 'tick': 8},
            DeviceType.TABLET: {'title': 14, 'label': 11, 'tick': 9},
            DeviceType.DESKTOP: {'title': 16, 'label': 12, 'tick': 10},
            DeviceType.LARGE_DESKTOP: {'title': 18, 'label': 14, 'tick': 12}
        }
        return font_size_map.get(device_type, font_size_map[DeviceType.DESKTOP])
        
    def _get_layout_params(self, device_type: DeviceType) -> Dict[str, float]:
        """Get layout parameters for device type"""
        layout_params = {
            DeviceType.MOBILE: {'left': 0.15, 'right': 0.95, 'top': 0.9, 'bottom': 0.15},
            DeviceType.TABLET: {'left': 0.12, 'right': 0.95, 'top': 0.9, 'bottom': 0.12},
            DeviceType.DESKTOP: {'left': 0.1, 'right': 0.95, 'top': 0.9, 'bottom': 0.1},
            DeviceType.LARGE_DESKTOP: {'left': 0.08, 'right': 0.96, 'top': 0.92, 'bottom': 0.08}
        }
        return layout_params.get(device_type, layout_params[DeviceType.DESKTOP])

# Global instance
_responsive_chart_manager = None

def get_responsive_chart_manager():
    """Get the global responsive chart manager instance"""
    global _responsive_chart_manager
    if _responsive_chart_manager is None:
        _responsive_chart_manager = ResponsiveChartManager()
    return _responsive_chart_manager
