#!/usr/bin/env python3
"""
Notification Performance Optimizer
Advanced performance optimizations for the notification system
"""

import sys
import os
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import weakref

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtCore import QObject, QTimer, Signal, QThread, QMutex, QMutexLocker
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("⚠️ PySide6 not available - using threading fallbacks")
    QObject = object
    Signal = lambda: None

from modules.enhanced_notification_system import get_notification_manager

class NotificationCache:
    """High-performance notification cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.access_order.remove(key)
            elif len(self.cache) >= self.max_size:
                # Evict least recently used
                lru_key = self.access_order.pop(0)
                del self.cache[lru_key]
            
            self.cache[key] = value
            self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

class NotificationDatabase:
    """High-performance SQLite database for notification persistence"""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        self.connection_pool = queue.Queue(maxsize=10)
        self.lock = threading.RLock()
        self._initialize_db()
        self._populate_connection_pool()
    
    def _initialize_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_id TEXT UNIQUE,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                read_status INTEGER DEFAULT 0,
                dismissed INTEGER DEFAULT 0,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON notifications(category)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_priority ON notifications(priority)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON notifications(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_read_status ON notifications(read_status)')
        
        conn.commit()
        conn.close()
    
    def _populate_connection_pool(self):
        """Populate connection pool"""
        for _ in range(5):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.connection_pool.put(conn)
    
    def _get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.get(timeout=1.0)
        except queue.Empty:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        try:
            self.connection_pool.put(conn, timeout=0.1)
        except queue.Full:
            # Close connection if pool is full
            conn.close()
    
    def store_notification(self, notification: Dict[str, Any]) -> bool:
        """Store notification in database"""
        conn = self._get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO notifications 
                (notification_id, title, message, category, priority, source, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notification.get('id', ''),
                notification.get('title', ''),
                notification.get('message', ''),
                notification.get('category', ''),
                notification.get('priority', 10),
                notification.get('source', ''),
                notification.get('timestamp', ''),
                json.dumps(notification.get('metadata', {}))
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error storing notification: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_notifications(self, limit: int = 100, category: str = None, 
                         priority_max: int = None) -> List[Dict]:
        """Get notifications from database"""
        conn = self._get_connection()
        try:
            query = 'SELECT * FROM notifications WHERE 1=1'
            params = []
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            if priority_max:
                query += ' AND priority <= ?'
                params.append(priority_max)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            notifications = []
            for row in rows:
                notification = dict(row)
                try:
                    notification['metadata'] = json.loads(notification['metadata'] or '{}')
                except:
                    notification['metadata'] = {}
                notifications.append(notification)
            
            return notifications
        except Exception as e:
            print(f"❌ Error getting notifications: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old notifications"""
        conn = self._get_connection()
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cursor = conn.execute(
                'DELETE FROM notifications WHERE created_at < ?',
                (cutoff_date.isoformat(),)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error cleaning up notifications: {e}")
            return 0
        finally:
            self._return_connection(conn)

class NotificationWorker(QThread if 'QThread' in globals() else threading.Thread):
    """Background worker for processing notifications"""
    
    def __init__(self):
        super().__init__()
        self.notification_queue = queue.Queue()
        self.running = True
        self.cache = NotificationCache()
        self.database = NotificationDatabase()
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        if hasattr(self, 'finished'):
            self.finished.connect(self.cleanup)
    
    def add_notification(self, notification: Dict[str, Any]):
        """Add notification to processing queue"""
        self.notification_queue.put(notification)
    
    def run(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get notification from queue with timeout
                notification = self.notification_queue.get(timeout=1.0)
                
                # Process notification in thread pool
                future = self.executor.submit(self._process_notification, notification)
                
                # Don't wait for completion to maintain responsiveness
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error in notification worker: {e}")
    
    def _process_notification(self, notification: Dict[str, Any]):
        """Process individual notification"""
        try:
            # Add to cache
            notification_id = notification.get('id', str(time.time()))
            self.cache.put(notification_id, notification)
            
            # Store in database
            self.database.store_notification(notification)
            
            # Perform any additional processing
            self._analyze_notification(notification)
            
        except Exception as e:
            print(f"❌ Error processing notification {notification.get('id', 'unknown')}: {e}")
    
    def _analyze_notification(self, notification: Dict[str, Any]):
        """Analyze notification for patterns and insights"""
        try:
            category = notification.get('category', '')
            priority = notification.get('priority', 10)
            
            # Update analytics (simplified)
            analytics_key = f"analytics_{category}"
            current_stats = self.cache.get(analytics_key) or {'count': 0, 'avg_priority': 0}
            
            current_stats['count'] += 1
            current_stats['avg_priority'] = (
                (current_stats['avg_priority'] * (current_stats['count'] - 1) + priority) / 
                current_stats['count']
            )
            
            self.cache.put(analytics_key, current_stats)
            
        except Exception as e:
            print(f"❌ Error analyzing notification: {e}")
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        self.executor.shutdown(wait=False)
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)

class PerformanceMonitor:
    """Monitor notification system performance"""
    
    def __init__(self):
        self.metrics = {
            'notifications_sent': 0,
            'notifications_queued': 0,
            'average_processing_time': 0.0,
            'cache_hit_rate': 0.0,
            'database_operations': 0,
            'memory_usage': 0,
            'cpu_usage': 0.0
        }
        self.start_time = time.time()
        self.processing_times = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_notification_sent(self):
        """Record notification sent"""
        self.metrics['notifications_sent'] += 1
    
    def record_notification_queued(self):
        """Record notification queued"""
        self.metrics['notifications_queued'] += 1
    
    def record_processing_time(self, processing_time: float):
        """Record processing time"""
        self.processing_times.append(processing_time)
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)
        
        self.metrics['average_processing_time'] = sum(self.processing_times) / len(self.processing_times)
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1
        self._update_cache_hit_rate()
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1
        self._update_cache_hit_rate()
    
    def _update_cache_hit_rate(self):
        """Update cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total > 0:
            self.metrics['cache_hit_rate'] = self.cache_hits / total
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'notifications_per_second': self.metrics['notifications_sent'] / max(uptime, 1),
            'queue_backlog': self.metrics['notifications_queued'],
            'average_processing_time_ms': self.metrics['average_processing_time'] * 1000,
            'cache_hit_rate_percent': self.metrics['cache_hit_rate'] * 100,
            'total_cache_operations': self.cache_hits + self.cache_misses,
            'performance_score': self._calculate_performance_score()
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100.0
        
        # Deduct for slow processing
        if self.metrics['average_processing_time'] > 0.1:
            score -= min(50, (self.metrics['average_processing_time'] - 0.1) * 500)
        
        # Deduct for low cache hit rate
        if self.metrics['cache_hit_rate'] < 0.8:
            score -= (0.8 - self.metrics['cache_hit_rate']) * 50
        
        # Deduct for large queue backlog
        if self.metrics['notifications_queued'] > 100:
            score -= min(30, (self.metrics['notifications_queued'] - 100) * 0.1)
        
        return max(0, score)

class OptimizedNotificationManager:
    """High-performance notification manager with optimizations"""
    
    def __init__(self):
        self.base_manager = get_notification_manager()
        self.worker = NotificationWorker()
        self.monitor = PerformanceMonitor()
        self.cache = NotificationCache(max_size=2000)
        
        # Start background worker
        self.worker.start()
        
        # Setup cleanup timer
        if hasattr(QTimer, '__init__'):
            self.cleanup_timer = QTimer()
            self.cleanup_timer.timeout.connect(self._periodic_cleanup)
            self.cleanup_timer.start(300000)  # 5 minutes
    
    def send_notification(self, title: str, message: str, category: str = "info",
                         priority: int = 10, source: str = "System", **kwargs) -> bool:
        """Send optimized notification"""
        start_time = time.time()
        
        try:
            # Create notification object
            notification = {
                'id': f"{category}_{int(time.time() * 1000)}",
                'title': title,
                'message': message,
                'category': category,
                'priority': priority,
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'metadata': kwargs
            }
            
            # Check cache for duplicate detection
            cache_key = f"{category}_{title}_{message}"
            cached = self.cache.get(cache_key)
            
            if cached:
                self.monitor.record_cache_hit()
                # Skip if duplicate within last 5 minutes
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if (datetime.now() - cached_time).total_seconds() < 300:
                    return False
            else:
                self.monitor.record_cache_miss()
            
            # Cache the notification
            self.cache.put(cache_key, notification)
            
            # Send through base manager
            result = self.base_manager.notify(
                title=title,
                message=message,
                category=category,
                priority=priority,
                source=source,
                **kwargs
            )
            
            if result:
                # Queue for background processing
                self.worker.add_notification(notification)
                self.monitor.record_notification_sent()
            else:
                self.monitor.record_notification_queued()
            
            # Record performance metrics
            processing_time = time.time() - start_time
            self.monitor.record_processing_time(processing_time)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in optimized notification manager: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.monitor.get_performance_report()
    
    def _periodic_cleanup(self):
        """Periodic cleanup of old data"""
        try:
            # Clean up old notifications from database
            cleaned = self.worker.database.cleanup_old_notifications(30)
            if cleaned > 0:
                print(f"🧹 Cleaned up {cleaned} old notifications")
            
            # Clear cache if it's getting too large
            if self.cache.size() > 1500:
                self.cache.clear()
                print("🧹 Cleared notification cache")
                
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def shutdown(self):
        """Shutdown the optimized manager"""
        try:
            self.worker.stop()
            if hasattr(self.worker, 'wait'):
                self.worker.wait(5000)  # Wait up to 5 seconds
            else:
                self.worker.join(5.0)
                
            if hasattr(self, 'cleanup_timer'):
                self.cleanup_timer.stop()
                
        except Exception as e:
            print(f"❌ Error during shutdown: {e}")

def create_performance_test():
    """Create a performance test for the optimized system"""
    print("🚀 Notification Performance Test")
    print("=" * 50)
    
    manager = OptimizedNotificationManager()
    
    # Performance test
    start_time = time.time()
    test_count = 100
    
    print(f"📤 Sending {test_count} notifications for performance testing...")
    
    for i in range(test_count):
        category = ['info', 'success', 'warning', 'error'][i % 4]
        manager.send_notification(
            title=f"Performance Test {i+1}",
            message=f"This is test notification number {i+1}",
            category=category,
            priority=10 + (i % 10),
            source="Performance Test"
        )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"⏱️ Performance Results:")
    print(f"   • Total time: {total_time:.3f} seconds")
    print(f"   • Notifications per second: {test_count / total_time:.1f}")
    print(f"   • Average time per notification: {(total_time / test_count) * 1000:.2f}ms")
    
    # Get detailed metrics
    time.sleep(1)  # Allow background processing
    metrics = manager.get_performance_metrics()
    
    print(f"\n📊 Detailed Performance Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   • {key.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    # Cleanup
    manager.shutdown()
    
    return metrics

if __name__ == "__main__":
    create_performance_test()
