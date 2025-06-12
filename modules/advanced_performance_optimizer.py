"""
Advanced Performance Optimizer for Kitchen Dashboard
Comprehensive solution to prevent "not responding" issues
"""

import logging
import threading
import time
import gc
import psutil
import os
from typing import Callable, Any, Dict, List
from functools import wraps
from PySide6.QtCore import QThread, QTimer, QObject, Signal, QMutex, QWaitCondition
from PySide6.QtWidgets import QApplication, QWidget, QTableWidget, QProgressDialog
from PySide6.QtGui import QPixmap

class BackgroundWorker(QThread):
    """Background worker for heavy operations"""
    
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        
    def run(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.finished.emit(self.result)
        except Exception as e:
            self.error.emit(str(e))

class DataLoadingManager(QObject):
    """Manages data loading operations to prevent UI blocking"""
    
    data_loaded = Signal(str, object)  # key, data
    loading_progress = Signal(int)
    loading_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.loading_queue = []
        self.is_loading = False
        
    def load_data_async(self, load_func: Callable, key: str):
        """Load data asynchronously"""
        if self.is_loading:
            self.loading_queue.append((load_func, key))
            return
            
        self.is_loading = True
        worker = BackgroundWorker(load_func)
        worker.finished.connect(lambda result: self._on_data_loaded(key, result))
        worker.error.connect(self._on_loading_error)
        worker.start()
        
    def _on_data_loaded(self, key: str, data):
        """Handle data loading completion"""
        self.data_loaded.emit(key, data)
        self.is_loading = False
        
        # Process queue
        if self.loading_queue:
            load_func, next_key = self.loading_queue.pop(0)
            self.load_data_async(load_func, next_key)
        else:
            self.loading_finished.emit()
            
    def _on_loading_error(self, error_msg: str):
        """Handle loading error"""
        self.logger.error(f"Data loading error: {error_msg}")
        self.is_loading = False

class UIUpdateManager(QObject):
    """Manages UI updates to prevent blocking"""
    
    def __init__(self):
        super().__init__()
        self.update_queue = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._process_update_queue)
        self.update_timer.start(50)  # Process updates every 50ms
        
    def queue_update(self, widget: QWidget, update_func: Callable, *args, **kwargs):
        """Queue a UI update"""
        self.update_queue.append((widget, update_func, args, kwargs))
        
    def _process_update_queue(self):
        """Process queued UI updates"""
        if not self.update_queue:
            return
            
        # Process up to 5 updates per cycle to prevent blocking
        for _ in range(min(5, len(self.update_queue))):
            if not self.update_queue:
                break
                
            widget, update_func, args, kwargs = self.update_queue.pop(0)
            try:
                if widget and not widget.isHidden():
                    update_func(*args, **kwargs)
            except Exception as e:
                logging.error(f"UI update error: {e}")

class MemoryManager:
    """Manages memory usage and cleanup"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_threshold = 80  # Percentage
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.check_memory_usage)
        self.cleanup_timer.start(30000)  # Check every 30 seconds
        
    def check_memory_usage(self):
        """Check memory usage and cleanup if needed"""
        try:
            memory_percent = psutil.virtual_memory().percent
            
            if memory_percent > self.memory_threshold:
                self.logger.warning(f"High memory usage: {memory_percent}%")
                self.cleanup_memory()
                
        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
            
    def cleanup_memory(self):
        """Perform memory cleanup"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear Qt caches
            QPixmap.clearCache()
            
            # Clear application cache if available
            app = QApplication.instance()
            if hasattr(app, 'clearCache'):
                app.clearCache()
                
            self.logger.info("Memory cleanup performed")
            
        except Exception as e:
            self.logger.error(f"Error during memory cleanup: {e}")

class TableOptimizer:
    """Optimizes table performance"""
    
    @staticmethod
    def optimize_table(table: QTableWidget):
        """Apply performance optimizations to table"""
        try:
            # Enable sorting but defer it
            table.setSortingEnabled(False)
            
            # Optimize selection behavior
            table.setSelectionBehavior(QTableWidget.SelectRows)
            
            # Use uniform row heights for better performance
            table.verticalHeader().setDefaultSectionSize(30)
            table.verticalHeader().setSectionResizeMode(table.verticalHeader().Fixed)
            
            # Disable alternating row colors for large tables
            if table.rowCount() > 1000:
                table.setAlternatingRowColors(False)
                
            # Enable updates batching
            table.setUpdatesEnabled(True)
            
        except Exception as e:
            logging.error(f"Error optimizing table: {e}")
            
    @staticmethod
    def populate_table_chunked(table: QTableWidget, data, chunk_size=100):
        """Populate table in chunks to prevent blocking"""
        if not data:
            return
            
        table.setUpdatesEnabled(False)
        
        try:
            total_rows = len(data)
            table.setRowCount(total_rows)
            
            # Process in chunks
            for start_idx in range(0, total_rows, chunk_size):
                end_idx = min(start_idx + chunk_size, total_rows)
                
                for row in range(start_idx, end_idx):
                    # Populate row data
                    row_data = data[row] if isinstance(data, list) else data.iloc[row]
                    
                    for col, value in enumerate(row_data):
                        item = table.item(row, col)
                        if item is None:
                            from PySide6.QtWidgets import QTableWidgetItem
                            item = QTableWidgetItem(str(value))
                            table.setItem(row, col, item)
                        else:
                            item.setText(str(value))
                
                # Allow UI to update
                QApplication.processEvents()
                
        finally:
            table.setUpdatesEnabled(True)

def async_operation(show_progress=True):
    """Decorator for async operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if show_progress:
                progress = QProgressDialog("Processing...", "Cancel", 0, 0, self)
                progress.setWindowModality(progress.WindowModal)
                progress.show()
                
            def run_operation():
                try:
                    result = func(self, *args, **kwargs)
                    if show_progress:
                        progress.close()
                    return result
                except Exception as e:
                    if show_progress:
                        progress.close()
                    raise e
                    
            worker = BackgroundWorker(run_operation)
            worker.finished.connect(lambda result: setattr(self, '_async_result', result))
            worker.error.connect(lambda error: setattr(self, '_async_error', error))
            worker.start()
            
            return worker
            
        return wrapper
    return decorator

def debounce(delay_ms=300):
    """Decorator to debounce function calls"""
    def decorator(func):
        timer = None
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            def call_func():
                func(*args, **kwargs)
                
            if timer:
                timer.stop()
                
            timer = QTimer()
            timer.timeout.connect(call_func)
            timer.setSingleShot(True)
            timer.start(delay_ms)
            
        return wrapper
    return decorator

class AdvancedPerformanceOptimizer:
    """Main performance optimizer class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.data_loader = DataLoadingManager()
        self.ui_updater = UIUpdateManager()
        self.memory_manager = MemoryManager()
        
        # Performance settings
        self.max_table_rows_before_virtualization = 1000
        self.ui_update_batch_size = 50
        self.memory_cleanup_interval = 30000  # 30 seconds
        
        self.logger.info("Advanced Performance Optimizer initialized")
        
    def optimize_application(self, app):
        """Apply application-wide optimizations"""
        try:
            # Set optimal attributes
            app.setAttribute(app.AA_UseHighDpiPixmaps, True)
            app.setAttribute(app.AA_EnableHighDpiScaling, True)
            app.setAttribute(app.AA_UseDesktopOpenGL, True)
            
            # Set optimal style
            from PySide6.QtWidgets import QStyleFactory
            app.setStyle(QStyleFactory.create("Fusion"))
            
            # Optimize event processing
            app.processEvents()
            
            self.logger.info("Application optimizations applied")
            
        except Exception as e:
            self.logger.error(f"Error optimizing application: {e}")
            
    def optimize_widget(self, widget: QWidget):
        """Optimize individual widget performance"""
        try:
            # Enable double buffering
            widget.setAttribute(widget.WA_OpaquePaintEvent, True)
            widget.setAttribute(widget.WA_NoSystemBackground, True)
            
            # Optimize updates
            widget.setUpdatesEnabled(True)
            
            # Special handling for tables
            if isinstance(widget, QTableWidget):
                TableOptimizer.optimize_table(widget)
                
        except Exception as e:
            self.logger.error(f"Error optimizing widget: {e}")
            
    def load_data_async(self, load_func: Callable, key: str):
        """Load data asynchronously"""
        return self.data_loader.load_data_async(load_func, key)
        
    def queue_ui_update(self, widget: QWidget, update_func: Callable, *args, **kwargs):
        """Queue UI update to prevent blocking"""
        self.ui_updater.queue_update(widget, update_func, *args, **kwargs)
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        try:
            process = psutil.Process()
            
            return {
                'memory_usage_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': process.cpu_percent(),
                'thread_count': process.num_threads(),
                'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {e}")
            return {}

# Global instance
_performance_optimizer = None

def get_advanced_performance_optimizer():
    """Get the global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = AdvancedPerformanceOptimizer()
    return _performance_optimizer
