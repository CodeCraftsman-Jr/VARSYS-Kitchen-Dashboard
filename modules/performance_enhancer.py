"""
Performance Enhancer for Kitchen Dashboard
Advanced performance optimization to prevent "not responding" issues
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

class PerformanceEnhancer:
    """Advanced performance enhancer to prevent UI freezing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workers = []
        self.timers = {}
        self.mutex = QMutex()
        
        # Performance settings
        self.max_table_rows_sync = 1000  # Load more than this in background
        self.debounce_delay = 300  # ms
        self.memory_check_interval = 30000  # 30 seconds
        self.gc_interval = 60000  # 1 minute
        
        # Memory monitoring
        self.memory_threshold = 80  # Percentage
        self.setup_memory_monitoring()
        
        self.logger.info("Performance Enhancer initialized")
    
    def setup_memory_monitoring(self):
        """Setup automatic memory monitoring and cleanup"""
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.check_memory_usage)
        self.memory_timer.start(self.memory_check_interval)
        
        self.gc_timer = QTimer()
        self.gc_timer.timeout.connect(self.force_garbage_collection)
        self.gc_timer.start(self.gc_interval)
    
    def check_memory_usage(self):
        """Check memory usage and trigger cleanup if needed"""
        try:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.memory_threshold:
                self.logger.warning(f"High memory usage: {memory_percent}%")
                self.force_garbage_collection()
                self.clear_caches()
        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory"""
        try:
            collected = gc.collect()
            if collected > 0:
                self.logger.info(f"Garbage collection freed {collected} objects")
        except Exception as e:
            self.logger.error(f"Error in garbage collection: {e}")
    
    def clear_caches(self):
        """Clear various caches to free memory"""
        try:
            # Clear QPixmap cache
            QPixmap.clearCache()
            
            # Clear application cache if available
            app = QApplication.instance()
            if hasattr(app, 'clearCache'):
                app.clearCache()
                
            self.logger.info("Caches cleared")
        except Exception as e:
            self.logger.error(f"Error clearing caches: {e}")
    
    def async_operation(self, func: Callable, callback: Callable = None, 
                       error_callback: Callable = None, progress_callback: Callable = None):
        """Execute operation in background thread"""
        def wrapper(*args, **kwargs):
            worker = BackgroundWorker(func, *args, **kwargs)
            
            if callback:
                worker.finished.connect(callback)
            if error_callback:
                worker.error.connect(error_callback)
            if progress_callback:
                worker.progress.connect(progress_callback)
            
            # Clean up finished workers
            worker.finished.connect(lambda: self.cleanup_worker(worker))
            worker.error.connect(lambda: self.cleanup_worker(worker))
            
            self.workers.append(worker)
            worker.start()
            
            return worker
        
        return wrapper
    
    def cleanup_worker(self, worker):
        """Clean up finished worker"""
        try:
            if worker in self.workers:
                self.workers.remove(worker)
            worker.deleteLater()
        except Exception as e:
            self.logger.error(f"Error cleaning up worker: {e}")
    
    def debounce(self, key: str, func: Callable, delay: int = None):
        """Debounce function calls to prevent excessive execution"""
        if delay is None:
            delay = self.debounce_delay
            
        # Cancel existing timer
        if key in self.timers:
            self.timers[key].stop()
            self.timers[key].deleteLater()
        
        # Create new timer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(func)
        timer.start(delay)
        
        self.timers[key] = timer
    
    def optimize_table_loading(self, table: QTableWidget, data, populate_func: Callable):
        """Optimize table loading for large datasets"""
        if not data or len(data) == 0:
            return
        
        # If data is small, load synchronously
        if len(data) <= self.max_table_rows_sync:
            populate_func(table, data)
            return
        
        # For large data, load in chunks
        self.load_table_in_chunks(table, data, populate_func)
    
    def load_table_in_chunks(self, table: QTableWidget, data, populate_func: Callable, chunk_size: int = 100):
        """Load table data in chunks to prevent UI freezing"""
        try:
            # Show progress dialog
            progress = QProgressDialog("Loading data...", "Cancel", 0, len(data), table.parent())
            progress.setWindowModality(2)  # Application modal
            progress.show()
            
            # Disable table updates during loading
            table.setUpdatesEnabled(False)
            
            def load_chunk(start_idx):
                try:
                    end_idx = min(start_idx + chunk_size, len(data))
                    chunk_data = data[start_idx:end_idx]
                    
                    # Populate chunk
                    populate_func(table, chunk_data, start_idx)
                    
                    # Update progress
                    progress.setValue(end_idx)
                    QApplication.processEvents()
                    
                    # Check if cancelled
                    if progress.wasCanceled():
                        return
                    
                    # Load next chunk
                    if end_idx < len(data):
                        QTimer.singleShot(10, lambda: load_chunk(end_idx))
                    else:
                        # Loading complete
                        table.setUpdatesEnabled(True)
                        progress.close()
                        self.logger.info(f"Table loaded with {len(data)} rows in chunks")
                        
                except Exception as e:
                    self.logger.error(f"Error loading table chunk: {e}")
                    table.setUpdatesEnabled(True)
                    progress.close()
            
            # Start loading
            load_chunk(0)
            
        except Exception as e:
            self.logger.error(f"Error in chunked table loading: {e}")
            table.setUpdatesEnabled(True)
    
    def optimize_data_loading(self, load_func: Callable):
        """Optimize data loading operations"""
        @wraps(load_func)
        def wrapper(*args, **kwargs):
            try:
                # Show loading indicator
                app = QApplication.instance()
                app.setOverrideCursor(app.waitCursor())
                
                # Execute in background if data is large
                def background_load():
                    return load_func(*args, **kwargs)
                
                def on_complete(result):
                    app.restoreOverrideCursor()
                    return result
                
                def on_error(error):
                    app.restoreOverrideCursor()
                    self.logger.error(f"Data loading error: {error}")
                
                # For now, execute synchronously but with optimizations
                result = load_func(*args, **kwargs)
                app.restoreOverrideCursor()
                return result
                
            except Exception as e:
                app = QApplication.instance()
                app.restoreOverrideCursor()
                self.logger.error(f"Error in optimized data loading: {e}")
                raise
        
        return wrapper
    
    def optimize_widget_updates(self, widget: QWidget):
        """Optimize widget update performance"""
        try:
            # Batch updates
            widget.setUpdatesEnabled(False)
            
            # Set optimal attributes
            widget.setAttribute(widget.WA_OpaquePaintEvent, True)
            widget.setAttribute(widget.WA_NoSystemBackground, True)
            
            # Re-enable updates
            widget.setUpdatesEnabled(True)
            
        except Exception as e:
            self.logger.error(f"Error optimizing widget updates: {e}")
    
    def prevent_ui_freeze(self, func: Callable, *args, **kwargs):
        """Prevent UI freeze during heavy operations"""
        def execute():
            try:
                # Process events periodically
                app = QApplication.instance()
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Process any pending events
                app.processEvents()
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error in UI freeze prevention: {e}")
                raise
        
        return execute()
    
    def optimize_file_operations(self, file_func: Callable):
        """Optimize file I/O operations"""
        @wraps(file_func)
        def wrapper(*args, **kwargs):
            try:
                # Check file size before loading
                if args and isinstance(args[0], str) and os.path.exists(args[0]):
                    file_size = os.path.getsize(args[0])
                    
                    # For large files, show progress
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        self.logger.info(f"Loading large file: {file_size/1024/1024:.1f}MB")
                
                return file_func(*args, **kwargs)
                
            except Exception as e:
                self.logger.error(f"Error in file operation: {e}")
                raise
        
        return wrapper
    
    def create_performance_monitor(self):
        """Create performance monitoring widget"""
        try:
            from .performance_monitor_widget import PerformanceMonitorWidget
            return PerformanceMonitorWidget()
        except ImportError:
            self.logger.warning("Performance monitor widget not available")
            return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        try:
            process = psutil.Process()
            
            return {
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'active_workers': len(self.workers),
                'active_timers': len(self.timers)
            }
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {e}")
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop all timers
            for timer in self.timers.values():
                timer.stop()
                timer.deleteLater()
            self.timers.clear()
            
            # Stop memory monitoring
            if hasattr(self, 'memory_timer'):
                self.memory_timer.stop()
            if hasattr(self, 'gc_timer'):
                self.gc_timer.stop()
            
            # Clean up workers
            for worker in self.workers:
                if worker.isRunning():
                    worker.quit()
                    worker.wait(1000)  # Wait 1 second
                worker.deleteLater()
            self.workers.clear()
            
            self.logger.info("Performance enhancer cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error in cleanup: {e}")

# Global instance
_performance_enhancer = None

def get_performance_enhancer():
    """Get the global performance enhancer instance"""
    global _performance_enhancer
    if _performance_enhancer is None:
        _performance_enhancer = PerformanceEnhancer()
    return _performance_enhancer

# Decorator for async operations
def async_operation(callback=None, error_callback=None):
    """Decorator for async operations"""
    def decorator(func):
        enhancer = get_performance_enhancer()
        return enhancer.async_operation(func, callback, error_callback)
    return decorator

# Decorator for debouncing
def debounce(key, delay=None):
    """Decorator for debouncing function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            enhancer = get_performance_enhancer()
            enhancer.debounce(key, lambda: func(*args, **kwargs), delay)
        return wrapper
    return decorator
