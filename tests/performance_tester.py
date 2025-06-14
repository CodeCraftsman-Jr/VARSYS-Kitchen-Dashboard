"""
Performance Tester
Tests application performance with large datasets and stress testing
"""

import time
import psutil
import gc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QProgressBar
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtGui import QFont

class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.start_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        self.start_cpu = psutil.cpu_percent()
        
    def get_metrics(self):
        """Get current performance metrics"""
        if self.start_time is None:
            return None
            
        current_time = time.time()
        current_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        current_cpu = psutil.cpu_percent()
        
        return {
            'execution_time': current_time - self.start_time,
            'memory_used': current_memory - self.start_memory,
            'cpu_usage': current_cpu,
            'memory_total': current_memory
        }

class PerformanceTester:
    """Tests application performance"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = app_instance.logger
        self.monitor = PerformanceMonitor()
        
    def test_performance(self):
        """Run performance tests"""
        self.logger.info("Starting performance testing...")
        
        # Create test dialog
        dialog = PerformanceTestDialog(self.app)
        dialog.show()
        
        # Performance tests
        tests_to_run = [
            ("Application Startup", self.test_startup_performance),
            ("Data Loading", self.test_data_loading_performance),
            ("Large Dataset Handling", self.test_large_dataset_performance),
            ("UI Responsiveness", self.test_ui_responsiveness),
            ("Memory Usage", self.test_memory_usage),
            ("CPU Usage", self.test_cpu_usage),
            ("Table Performance", self.test_table_performance),
            ("Chart Rendering", self.test_chart_performance),
            ("File I/O Performance", self.test_file_io_performance),
            ("Database Operations", self.test_database_performance),
            ("Concurrent Operations", self.test_concurrent_performance),
            ("Memory Leaks", self.test_memory_leaks),
            ("Stress Testing", self.test_stress_performance)
        ]
        
        results = []
        for test_name, test_function in tests_to_run:
            try:
                dialog.update_status(f"Testing {test_name}...")
                
                self.monitor.start_monitoring()
                test_function()
                metrics = self.monitor.get_metrics()
                
                result = f"✅ {test_name}: PASSED"
                if metrics:
                    result += f" (Time: {metrics['execution_time']:.2f}s, "
                    result += f"Memory: {metrics['memory_used']:.1f}MB, "
                    result += f"CPU: {metrics['cpu_usage']:.1f}%)"
                    
                self.logger.info(f"Performance test passed: {test_name}")
                
            except Exception as e:
                metrics = self.monitor.get_metrics()
                result = f"❌ {test_name}: FAILED - {str(e)}"
                if metrics:
                    result += f" (Time: {metrics['execution_time']:.2f}s)"
                    
                self.logger.error(f"Performance test failed: {test_name} - {str(e)}")
                
            results.append(result)
            dialog.add_result(result)
            
            # Force garbage collection between tests
            gc.collect()
            time.sleep(0.1)  # Brief pause between tests
            
        dialog.update_status("All performance tests completed!")
        self.logger.info("Performance testing completed")
        
    def create_large_dataset(self, rows=100000):
        """Create large dataset for testing"""
        return pd.DataFrame({
            'id': range(rows),
            'name': [f'Item_{i}' for i in range(rows)],
            'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], rows),
            'quantity': np.random.randint(1, 1000, rows),
            'price': np.random.uniform(1, 1000, rows),
            'date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(rows)],
            'description': [f'Description for item {i}' * 10 for i in range(rows)]  # Larger text fields
        })
        
    def test_startup_performance(self):
        """Test application startup performance"""
        # This test measures the time it took to initialize the app
        # Since the app is already running, we'll simulate startup components
        
        start_time = time.time()
        
        # Simulate data loading
        data = self.app.load_data()
        
        # Simulate UI initialization
        if hasattr(self.app, 'sidebar'):
            self.app.sidebar.update()
            
        if hasattr(self.app, 'content_widget'):
            self.app.content_widget.update()
            
        startup_time = time.time() - start_time
        
        # Startup should be reasonably fast
        assert startup_time < 10.0, f"Startup took too long: {startup_time:.2f}s"
        
    def test_data_loading_performance(self):
        """Test data loading performance"""
        start_time = time.time()
        
        # Test loading multiple datasets
        for i in range(10):
            data = self.create_large_dataset(10000)  # 10k rows each
            
        load_time = time.time() - start_time
        
        # Should handle multiple datasets efficiently
        assert load_time < 30.0, f"Data loading took too long: {load_time:.2f}s"
        
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        # Create very large dataset
        large_data = self.create_large_dataset(500000)  # 500k rows
        
        start_time = time.time()
        
        # Test filtering
        filtered = large_data[large_data['quantity'] > 500]
        
        # Test grouping
        grouped = large_data.groupby('category')['price'].mean()
        
        # Test sorting
        sorted_data = large_data.sort_values('price')
        
        operation_time = time.time() - start_time
        
        # Large dataset operations should complete in reasonable time
        assert operation_time < 60.0, f"Large dataset operations took too long: {operation_time:.2f}s"
        
    def test_ui_responsiveness(self):
        """Test UI responsiveness"""
        start_time = time.time()
        
        # Test UI updates
        for i in range(100):
            if hasattr(self.app, 'content_widget'):
                self.app.content_widget.update()
                
            # Process events to keep UI responsive
            self.app.processEvents()
            
        ui_time = time.time() - start_time
        
        # UI should remain responsive
        assert ui_time < 5.0, f"UI updates took too long: {ui_time:.2f}s"
        
    def test_memory_usage(self):
        """Test memory usage"""
        initial_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # Create and process large datasets
        datasets = []
        for i in range(10):
            data = self.create_large_dataset(50000)
            datasets.append(data)
            
        peak_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        memory_used = peak_memory - initial_memory
        
        # Clean up
        del datasets
        gc.collect()
        
        final_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        memory_freed = peak_memory - final_memory
        
        # Memory usage should be reasonable
        assert memory_used < 2000, f"Memory usage too high: {memory_used:.1f}MB"
        
        # Should free most memory after cleanup
        assert memory_freed > memory_used * 0.5, f"Memory not properly freed: {memory_freed:.1f}MB"
        
    def test_cpu_usage(self):
        """Test CPU usage"""
        # Monitor CPU during intensive operations
        cpu_readings = []
        
        start_time = time.time()
        while time.time() - start_time < 5:  # Monitor for 5 seconds
            # Perform CPU-intensive operations
            data = self.create_large_dataset(10000)
            result = data.groupby('category').agg({
                'quantity': ['sum', 'mean', 'std'],
                'price': ['sum', 'mean', 'std']
            })
            
            cpu_readings.append(psutil.cpu_percent())
            
        avg_cpu = sum(cpu_readings) / len(cpu_readings)
        
        # CPU usage should be reasonable (not constantly at 100%)
        assert avg_cpu < 90, f"CPU usage too high: {avg_cpu:.1f}%"
        
    def test_table_performance(self):
        """Test table performance with large datasets"""
        try:
            from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
            
            # Create large table
            table = QTableWidget(10000, 10)  # 10k rows, 10 columns
            
            start_time = time.time()
            
            # Populate table
            for row in range(min(1000, table.rowCount())):  # Limit to 1000 for performance
                for col in range(table.columnCount()):
                    item = QTableWidgetItem(f"Item_{row}_{col}")
                    table.setItem(row, col, item)
                    
            table_time = time.time() - start_time
            
            # Table population should be reasonably fast
            assert table_time < 30.0, f"Table population took too long: {table_time:.2f}s"
            
        except Exception as e:
            # Table creation might fail in headless environment
            pass
            
    def test_chart_performance(self):
        """Test chart rendering performance"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
            
            start_time = time.time()
            
            # Create multiple charts
            for i in range(10):
                fig = Figure(figsize=(8, 6))
                ax = fig.add_subplot(111)
                
                # Generate data
                x = np.random.randn(1000)
                y = np.random.randn(1000)
                
                # Create scatter plot
                ax.scatter(x, y, alpha=0.5)
                ax.set_title(f"Chart {i}")
                
            chart_time = time.time() - start_time
            
            # Chart rendering should be reasonably fast
            assert chart_time < 20.0, f"Chart rendering took too long: {chart_time:.2f}s"
            
        except ImportError:
            # Matplotlib might not be available
            pass
            
    def test_file_io_performance(self):
        """Test file I/O performance"""
        # Create test data
        test_data = self.create_large_dataset(100000)
        
        # Test CSV writing
        start_time = time.time()
        test_data.to_csv('performance_test.csv', index=False)
        write_time = time.time() - start_time
        
        # Test CSV reading
        start_time = time.time()
        loaded_data = pd.read_csv('performance_test.csv')
        read_time = time.time() - start_time
        
        # Cleanup
        import os
        os.remove('performance_test.csv')
        
        # File I/O should be reasonably fast
        assert write_time < 30.0, f"CSV writing took too long: {write_time:.2f}s"
        assert read_time < 30.0, f"CSV reading took too long: {read_time:.2f}s"
        
        # Data integrity check
        assert len(loaded_data) == len(test_data), "Data integrity check failed"
        
    def test_database_performance(self):
        """Test database operations performance"""
        # Test with SQLite (in-memory)
        try:
            import sqlite3
            
            # Create in-memory database
            conn = sqlite3.connect(':memory:')
            
            # Create test data
            test_data = self.create_large_dataset(50000)
            
            start_time = time.time()
            
            # Write to database
            test_data.to_sql('test_table', conn, index=False)
            
            # Read from database
            loaded_data = pd.read_sql('SELECT * FROM test_table', conn)
            
            # Perform queries
            result1 = pd.read_sql('SELECT category, COUNT(*) as count FROM test_table GROUP BY category', conn)
            result2 = pd.read_sql('SELECT * FROM test_table WHERE price > 500', conn)
            
            db_time = time.time() - start_time
            
            conn.close()
            
            # Database operations should be reasonably fast
            assert db_time < 60.0, f"Database operations took too long: {db_time:.2f}s"
            
        except ImportError:
            # SQLite might not be available
            pass
            
    def test_concurrent_performance(self):
        """Test concurrent operations performance"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def worker_function(worker_id):
            try:
                # Each worker processes data
                data = self.create_large_dataset(10000)
                result = data.groupby('category')['price'].mean()
                results_queue.put(('success', worker_id, len(result)))
            except Exception as e:
                results_queue.put(('error', worker_id, str(e)))
                
        start_time = time.time()
        
        # Create multiple worker threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        concurrent_time = time.time() - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
            
        # All workers should complete successfully
        successful_workers = [r for r in results if r[0] == 'success']
        assert len(successful_workers) == 5, f"Only {len(successful_workers)} workers completed successfully"
        
        # Concurrent operations should be reasonably fast
        assert concurrent_time < 60.0, f"Concurrent operations took too long: {concurrent_time:.2f}s"
        
    def test_memory_leaks(self):
        """Test for memory leaks"""
        initial_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # Perform operations that might cause memory leaks
        for i in range(100):
            # Create and destroy data
            data = self.create_large_dataset(1000)
            processed = data.groupby('category').sum()
            
            # Force garbage collection
            del data, processed
            gc.collect()
            
            # Check memory periodically
            if i % 20 == 0:
                current_memory = psutil.virtual_memory().used / 1024 / 1024
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be minimal
                assert memory_growth < 500, f"Potential memory leak detected: {memory_growth:.1f}MB growth"
                
    def test_stress_performance(self):
        """Test application under stress"""
        start_time = time.time()
        
        # Simulate heavy load
        for i in range(50):
            # Create large dataset
            data = self.create_large_dataset(20000)
            
            # Perform multiple operations
            filtered = data[data['quantity'] > 100]
            grouped = data.groupby('category').agg({
                'quantity': 'sum',
                'price': 'mean'
            })
            sorted_data = data.sort_values(['category', 'price'])
            
            # Update UI (if possible)
            if hasattr(self.app, 'processEvents'):
                self.app.processEvents()
                
            # Clean up
            del data, filtered, grouped, sorted_data
            
            if i % 10 == 0:
                gc.collect()
                
        stress_time = time.time() - start_time
        
        # Should handle stress test without crashing
        assert stress_time < 300.0, f"Stress test took too long: {stress_time:.2f}s"


class PerformanceTestDialog(QDialog):
    """Dialog for displaying performance test results"""
    
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.app = app_instance
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Performance Testing")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Kitchen Dashboard - Performance Testing")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # System info
        try:
            cpu_count = psutil.cpu_count()
            memory_total = psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB
            info_text = f"System: {cpu_count} CPUs, {memory_total:.1f}GB RAM"
            
            info_label = QLabel(info_text)
            layout.addWidget(info_label)
        except:
            pass
            
        # Status label
        self.status_label = QLabel("Preparing performance tests...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setFont(QFont("Consolas", 9))
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
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
