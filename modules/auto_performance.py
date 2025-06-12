
# Performance optimizations applied automatically
import logging
from modules.css_optimizer import get_css_optimizer, optimize_stylesheet
from modules.performance_optimizer import get_performance_optimizer, optimize_widget

logger = logging.getLogger(__name__)

def apply_widget_optimizations(widget):
    '''Apply performance optimizations to a widget'''
    try:
        optimizer = get_performance_optimizer()
        if optimizer:
            optimizer.optimize_widget_rendering(widget)
            
        # Apply CSS optimizations if widget has stylesheet
        if hasattr(widget, 'styleSheet') and widget.styleSheet():
            optimized_css = optimize_stylesheet(widget.styleSheet())
            widget.setStyleSheet(optimized_css)
            
    except Exception as e:
        logger.error(f"Error optimizing widget: {e}")

def optimize_application_css():
    '''Optimize all CSS in the application'''
    try:
        from modules.css_optimizer import get_optimized_stylesheet
        return get_optimized_stylesheet()
    except Exception as e:
        logger.error(f"Error getting optimized stylesheet: {e}")
        return ""
