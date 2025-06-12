"""
Performance Optimizer
Optimizes UI performance and reduces lag
"""

import logging
import time
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QTimer, QThread, QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPixmap

class PerformanceOptimizer:
    """
    Performance optimizer that:
    - Reduces UI lag through efficient rendering
    - Implements lazy loading for heavy components
    - Optimizes memory usage
    - Provides performance monitoring
    - Implements caching strategies
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Performance settings
        self.enable_lazy_loading = True
        self.enable_caching = True
        self.enable_debouncing = True
        self.cache_size_limit = 100  # MB
        
        # Performance metrics
        self.render_times = []
        self.memory_usage = []
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Caches
        self.widget_cache = {}
        self.pixmap_cache = {}
        self.stylesheet_cache = {}
        
        # Timers for debouncing
        self.debounce_timers = {}
        
        self.logger.info("Performance Optimizer initialized")
    
    def optimize_widget_rendering(self, widget: QWidget):
        """Optimize widget rendering performance"""
        if not widget:
            return
        
        try:
            # Enable double buffering
            widget.setAttribute(Qt.WA_OpaquePaintEvent, True)
            widget.setAttribute(Qt.WA_NoSystemBackground, True)
            
            # Optimize updates
            widget.setUpdatesEnabled(True)
            
            # Set optimal size policy for performance
            from PySide6.QtWidgets import QSizePolicy
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            
        except Exception as e:
            self.logger.error(f"Error optimizing widget rendering: {e}")
    
    def debounce_function(self, key: str, func, delay_ms: int = 300):
        """Debounce function calls to reduce UI lag"""
        if not self.enable_debouncing:
            func()
            return
        
        # Cancel existing timer
        if key in self.debounce_timers:
            self.debounce_timers[key].stop()
        
        # Create new timer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(func)
        timer.start(delay_ms)
        
        self.debounce_timers[key] = timer
    
    def cache_widget(self, key: str, widget: QWidget):
        """Cache widget for reuse - DISABLED to prevent issues"""
        # Caching disabled to prevent data consistency issues
        pass
    
    def get_cached_widget(self, key: str) -> Optional[QWidget]:
        """Get cached widget"""
        if not self.enable_caching:
            return None
        
        if key in self.widget_cache:
            self.cache_hits += 1
            return self.widget_cache[key]
        
        self.cache_misses += 1
        return None
    
    def cache_stylesheet(self, key: str, stylesheet: str):
        """Cache stylesheet for reuse"""
        if not self.enable_caching:
            return
        
        self.stylesheet_cache[key] = stylesheet
    
    def get_cached_stylesheet(self, key: str) -> Optional[str]:
        """Get cached stylesheet"""
        if not self.enable_caching:
            return None
        
        return self.stylesheet_cache.get(key)
    
    def optimize_table_performance(self, table_widget):
        """Optimize table widget performance"""
        try:
            # Disable sorting during updates
            table_widget.setSortingEnabled(False)
            
            # Set optimal resize modes
            from PySide6.QtWidgets import QHeaderView
            header = table_widget.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.Interactive)
            
            # Enable alternating row colors for better performance
            table_widget.setAlternatingRowColors(True)
            
            # Optimize selection behavior
            from PySide6.QtWidgets import QAbstractItemView
            table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
            table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
            
        except Exception as e:
            self.logger.error(f"Error optimizing table performance: {e}")
    
    def optimize_layout_performance(self, layout):
        """Optimize layout performance"""
        try:
            # Set optimal spacing
            layout.setSpacing(8)
            layout.setContentsMargins(8, 8, 8, 8)
            
            # Enable size constraints
            from PySide6.QtWidgets import QLayout
            layout.setSizeConstraint(QLayout.SetDefaultConstraint)
            
        except Exception as e:
            self.logger.error(f"Error optimizing layout performance: {e}")
    
    def lazy_load_widget(self, widget_factory, container, delay_ms: int = 100):
        """Lazy load widget to improve initial render time"""
        if not self.enable_lazy_loading:
            widget = widget_factory()
            container.addWidget(widget)
            return widget
        
        def load_widget():
            try:
                widget = widget_factory()
                container.addWidget(widget)
                self.optimize_widget_rendering(widget)
            except Exception as e:
                self.logger.error(f"Error in lazy loading widget: {e}")
        
        # Use timer for lazy loading
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(load_widget)
        timer.start(delay_ms)
        
        return timer
    
    def batch_update_widgets(self, widgets: List[QWidget], update_func):
        """Batch update multiple widgets for better performance"""
        try:
            # Disable updates during batch operation
            for widget in widgets:
                widget.setUpdatesEnabled(False)
            
            # Perform updates
            for widget in widgets:
                update_func(widget)
            
            # Re-enable updates
            for widget in widgets:
                widget.setUpdatesEnabled(True)
                widget.update()
                
        except Exception as e:
            self.logger.error(f"Error in batch update: {e}")
    
    def measure_render_time(self, func):
        """Measure rendering time for performance monitoring"""
        start_time = time.time()
        
        try:
            result = func()
            end_time = time.time()
            render_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.render_times.append(render_time)
            
            # Keep only last 100 measurements
            if len(self.render_times) > 100:
                self.render_times = self.render_times[-100:]
            
            if render_time > 100:  # Log slow renders (>100ms)
                self.logger.warning(f"Slow render detected: {render_time:.2f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error measuring render time: {e}")
            return None
    
    def optimize_application_performance(self, app: QApplication):
        """Optimize overall application performance"""
        try:
            # Set optimal graphics system
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            
            # Optimize font rendering
            app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
            
            # Set optimal style
            from PySide6.QtWidgets import QStyleFactory
            app.setStyle(QStyleFactory.create("Fusion"))
            
        except Exception as e:
            self.logger.error(f"Error optimizing application performance: {e}")
    
    def clear_caches(self):
        """Clear all caches to free memory - DISABLED"""
        # Caching disabled to prevent data consistency issues
        self.logger.info("Cache clearing disabled")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_render_time = sum(self.render_times) / len(self.render_times) if self.render_times else 0
        max_render_time = max(self.render_times) if self.render_times else 0
        
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses)) * 100 if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            "average_render_time_ms": round(avg_render_time, 2),
            "max_render_time_ms": round(max_render_time, 2),
            "total_renders": len(self.render_times),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "cached_widgets": len(self.widget_cache),
            "cached_stylesheets": len(self.stylesheet_cache)
        }
    
    def optimize_for_mobile(self):
        """Apply mobile-specific performance optimizations"""
        # Reduce cache sizes for mobile
        self.cache_size_limit = 50  # MB

        # Enable more aggressive lazy loading
        self.enable_lazy_loading = True

        # Reduce debounce delays for better responsiveness
        self.debounce_delay = 150  # ms

        self.logger.info("Mobile performance optimizations applied")

    def optimize_data_loading(self, data_loader_func):
        """Optimize data loading - CACHING DISABLED"""
        def optimized_loader(*args, **kwargs):
            # Direct loading without caching to prevent data consistency issues
            try:
                result = data_loader_func(*args, **kwargs)
                return result
            except Exception as e:
                self.logger.error(f"Error in data loading: {e}")
                return None

        return optimized_loader

    def optimize_ui_updates(self, update_func):
        """Optimize UI updates with debouncing"""
        def debounced_update(*args, **kwargs):
            update_key = f"ui_update_{hash(str(args) + str(kwargs))}"

            # Cancel previous timer if exists
            if update_key in self.debounce_timers:
                self.debounce_timers[update_key].stop()

            # Create new timer
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: update_func(*args, **kwargs))
            timer.start(self.debounce_delay)

            self.debounce_timers[update_key] = timer

        return debounced_update

    def get_object_size(self, obj):
        """Get approximate size of object in bytes"""
        try:
            import sys
            return sys.getsizeof(obj)
        except:
            return 0

    def optimize_memory_usage(self):
        """Optimize memory usage by cleaning up unused objects"""
        try:
            import gc

            # Clear caches if they're too large
            total_cache_size = sum(self.get_object_size(obj) for obj in self.widget_cache.values())
            if total_cache_size > self.cache_size_limit * 1024 * 1024:
                # Remove oldest entries
                cache_items = list(self.widget_cache.items())
                for key, value in cache_items[:len(cache_items)//2]:
                    del self.widget_cache[key]

                self.logger.info(f"Cleared cache to free memory. Size was: {total_cache_size/1024/1024:.1f}MB")

            # Force garbage collection
            gc.collect()

        except Exception as e:
            self.logger.error(f"Error optimizing memory usage: {e}")

    def create_lazy_loader(self, widget_factory, *args, **kwargs):
        """Create a lazy-loading widget wrapper"""
        class LazyWidget(QWidget):
            def __init__(self, factory, *factory_args, **factory_kwargs):
                super().__init__()
                self.factory = factory
                self.factory_args = factory_args
                self.factory_kwargs = factory_kwargs
                self.actual_widget = None
                self.loaded = False

                # Placeholder layout
                self.placeholder_layout = QVBoxLayout(self)
                placeholder_label = QLabel("Loading...")
                placeholder_label.setAlignment(Qt.AlignCenter)
                placeholder_label.setStyleSheet("color: #64748b; font-size: 14px;")
                self.placeholder_layout.addWidget(placeholder_label)

            def showEvent(self, event):
                """Load actual widget when shown"""
                if not self.loaded:
                    self.load_actual_widget()
                super().showEvent(event)

            def load_actual_widget(self):
                """Load the actual widget"""
                try:
                    self.actual_widget = self.factory(*self.factory_args, **self.factory_kwargs)

                    # Clear placeholder
                    for i in reversed(range(self.placeholder_layout.count())):
                        self.placeholder_layout.itemAt(i).widget().setParent(None)

                    # Add actual widget
                    self.placeholder_layout.addWidget(self.actual_widget)
                    self.loaded = True

                except Exception as e:
                    error_label = QLabel(f"Error loading widget: {e}")
                    error_label.setStyleSheet("color: #ef4444; font-size: 12px;")
                    self.placeholder_layout.addWidget(error_label)

        return LazyWidget(widget_factory, *args, **kwargs)

    def optimize_table_performance(self, table_widget):
        """Enhanced table performance optimization"""
        try:
            # Enable uniform row heights for better performance
            table_widget.setUniformRowHeights(True)

            # Optimize selection behavior
            table_widget.setSelectionBehavior(table_widget.SelectRows)

            # Enable alternating row colors for better readability
            table_widget.setAlternatingRowColors(True)

            # Optimize scrolling
            table_widget.setVerticalScrollMode(table_widget.ScrollPerPixel)
            table_widget.setHorizontalScrollMode(table_widget.ScrollPerPixel)

            # Set optimal size policies
            from PySide6.QtWidgets import QSizePolicy
            table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Optimize header
            header = table_widget.horizontalHeader()
            header.setStretchLastSection(True)
            header.setCascadingSectionResizes(True)

            # Enable sorting but defer it
            table_widget.setSortingEnabled(False)  # Enable only when needed

            self.logger.debug("Table performance optimized")

        except Exception as e:
            self.logger.error(f"Error optimizing table performance: {e}")

    def create_performance_monitor(self):
        """Create performance monitoring widget"""
        class PerformanceMonitor(QWidget):
            def __init__(self, optimizer):
                super().__init__()
                self.optimizer = optimizer
                self.setWindowTitle("Performance Monitor")
                self.resize(400, 300)

                layout = QVBoxLayout(self)

                # Cache statistics
                cache_group = QGroupBox("Cache Statistics")
                cache_layout = QVBoxLayout(cache_group)

                self.cache_hits_label = QLabel("Cache Hits: 0")
                self.cache_misses_label = QLabel("Cache Misses: 0")
                self.cache_size_label = QLabel("Cache Size: 0 MB")

                cache_layout.addWidget(self.cache_hits_label)
                cache_layout.addWidget(self.cache_misses_label)
                cache_layout.addWidget(self.cache_size_label)

                layout.addWidget(cache_group)

                # Memory usage
                memory_group = QGroupBox("Memory Usage")
                memory_layout = QVBoxLayout(memory_group)

                self.memory_label = QLabel("Memory Usage: Unknown")
                memory_layout.addWidget(self.memory_label)

                layout.addWidget(memory_group)

                # Control buttons
                buttons_layout = QHBoxLayout()

                clear_cache_btn = QPushButton("Clear Cache")
                clear_cache_btn.clicked.connect(self.optimizer.clear_caches)
                buttons_layout.addWidget(clear_cache_btn)

                optimize_memory_btn = QPushButton("Optimize Memory")
                optimize_memory_btn.clicked.connect(self.optimizer.optimize_memory_usage)
                buttons_layout.addWidget(optimize_memory_btn)

                layout.addLayout(buttons_layout)

                # Update timer
                self.update_timer = QTimer()
                self.update_timer.timeout.connect(self.update_stats)
                self.update_timer.start(2000)  # Update every 2 seconds

            def update_stats(self):
                """Update performance statistics"""
                self.cache_hits_label.setText(f"Cache Hits: {self.optimizer.cache_hits}")
                self.cache_misses_label.setText(f"Cache Misses: {self.optimizer.cache_misses}")

                cache_size = sum(self.optimizer.get_object_size(obj) for obj in self.optimizer.widget_cache.values())
                self.cache_size_label.setText(f"Cache Size: {cache_size/1024/1024:.1f} MB")

                try:
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.memory_label.setText(f"Memory Usage: {memory_mb:.1f} MB")
                except:
                    self.memory_label.setText("Memory Usage: Unknown")

        return PerformanceMonitor(self)
    
    def create_performance_monitor_widget(self):
        """Create a widget to monitor performance"""
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance stats
        stats = self.get_performance_stats()
        
        # Render time
        render_label = QLabel(f"Avg Render Time: {stats['average_render_time_ms']}ms")
        layout.addWidget(render_label)
        
        # Cache hit rate
        cache_label = QLabel(f"Cache Hit Rate: {stats['cache_hit_rate_percent']}%")
        layout.addWidget(cache_label)
        
        # Cache hit rate progress bar
        cache_progress = QProgressBar()
        cache_progress.setRange(0, 100)
        cache_progress.setValue(int(stats['cache_hit_rate_percent']))
        layout.addWidget(cache_progress)
        
        # Memory usage (cached items)
        memory_label = QLabel(f"Cached Items: {stats['cached_widgets']} widgets, {stats['cached_stylesheets']} styles")
        layout.addWidget(memory_label)
        
        return widget

class AsyncWorker(QObject):
    """Worker for performing heavy operations in background"""
    
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Run the function in background"""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class BackgroundProcessor:
    """Process heavy operations in background to prevent UI lag"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_workers = []
    
    def process_async(self, func, callback=None, error_callback=None, *args, **kwargs):
        """Process function asynchronously"""
        try:
            # Create worker and thread
            worker = AsyncWorker(func, *args, **kwargs)
            thread = QThread()
            
            # Move worker to thread
            worker.moveToThread(thread)
            
            # Connect signals
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            
            if callback:
                worker.finished.connect(callback)
            
            if error_callback:
                worker.error.connect(error_callback)
            
            # Start processing
            thread.start()
            
            # Track active worker
            self.active_workers.append((worker, thread))
            
            # Clean up finished workers
            thread.finished.connect(lambda: self.cleanup_worker(worker, thread))
            
        except Exception as e:
            self.logger.error(f"Error starting async process: {e}")
    
    def cleanup_worker(self, worker, thread):
        """Clean up finished worker"""
        try:
            if (worker, thread) in self.active_workers:
                self.active_workers.remove((worker, thread))
        except Exception as e:
            self.logger.error(f"Error cleaning up worker: {e}")

# Global performance optimizer instance
_performance_optimizer = None
_background_processor = None

def get_performance_optimizer():
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def get_background_processor():
    """Get global background processor instance"""
    global _background_processor
    if _background_processor is None:
        _background_processor = BackgroundProcessor()
    return _background_processor

def optimize_widget(widget: QWidget):
    """Optimize a widget for better performance"""
    optimizer = get_performance_optimizer()
    optimizer.optimize_widget_rendering(widget)

def debounce(key: str, func, delay_ms: int = 300):
    """Debounce a function call"""
    optimizer = get_performance_optimizer()
    optimizer.debounce_function(key, func, delay_ms)
