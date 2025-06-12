"""
Advanced Activity Tracker
Comprehensive tracking of user actions, system events, and performance metrics
"""

import os
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QApplication

class ActivityType(Enum):
    """Types of activities to track"""
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    DATA_CHANGE = "data_change"
    ERROR = "error"
    PERFORMANCE = "performance"
    NAVIGATION = "navigation"
    IMPORT_EXPORT = "import_export"
    NOTIFICATION = "notification"
    INGREDIENT_AUTO_ADD = "ingredient_auto_add"
    PRICING_CALCULATION = "pricing_calculation"

class ActivityLevel(Enum):
    """Activity importance levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ActivityRecord:
    """Data structure for activity records"""
    timestamp: str
    activity_type: str
    level: str
    module: str
    action: str
    description: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    data_before: Optional[Dict] = None
    data_after: Optional[Dict] = None
    execution_time: Optional[float] = None
    error_details: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Optional[Dict] = None

class ActivityTracker(QObject):
    """
    Comprehensive activity tracking system that monitors:
    - User interactions and navigation
    - Data modifications and changes
    - System events and errors
    - Performance metrics
    - Import/export operations
    - Notification events
    """
    
    activity_logged = Signal(ActivityRecord)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Initialize tracking data
        self.activities: List[ActivityRecord] = []
        self.session_id = self.generate_session_id()
        self.user_id = "anonymous"  # Will be updated when user logs in
        
        # File paths
        self.activities_file = "data/activities.json"
        self.daily_activities_dir = "data/daily_activities"
        
        # Performance tracking
        self.performance_metrics = {}
        self.start_times = {}
        
        # Load existing activities
        self.load_activities()
        
        # Setup periodic save
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_activities)
        self.save_timer.start(30000)  # Save every 30 seconds
        
        # Setup daily rotation
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_daily_logs)
        self.rotation_timer.start(3600000)  # Check every hour
        
        self.logger.info("Activity Tracker initialized")
        self.track_system_event("activity_tracker", "initialized", "Activity tracking system started")
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def set_user_id(self, user_id: str):
        """Set the current user ID"""
        old_user = self.user_id
        self.user_id = user_id
        self.track_user_action("authentication", "user_login", f"User changed from {old_user} to {user_id}")
    
    def track_user_action(self, module: str, action: str, description: str, 
                         data_before: Optional[Dict] = None, data_after: Optional[Dict] = None,
                         metadata: Optional[Dict] = None):
        """Track user actions and interactions"""
        self._log_activity(
            activity_type=ActivityType.USER_ACTION,
            level=ActivityLevel.INFO,
            module=module,
            action=action,
            description=description,
            data_before=data_before,
            data_after=data_after,
            metadata=metadata
        )
    
    def track_navigation(self, from_page: str, to_page: str, metadata: Optional[Dict] = None):
        """Track navigation between pages"""
        self._log_activity(
            activity_type=ActivityType.NAVIGATION,
            level=ActivityLevel.DEBUG,
            module="navigation",
            action="page_change",
            description=f"Navigated from {from_page} to {to_page}",
            metadata={"from": from_page, "to": to_page, **(metadata or {})}
        )
    
    def track_data_change(self, module: str, action: str, description: str,
                         data_before: Optional[Dict] = None, data_after: Optional[Dict] = None,
                         metadata: Optional[Dict] = None):
        """Track data modifications"""
        self._log_activity(
            activity_type=ActivityType.DATA_CHANGE,
            level=ActivityLevel.INFO,
            module=module,
            action=action,
            description=description,
            data_before=data_before,
            data_after=data_after,
            metadata=metadata
        )
    
    def track_system_event(self, module: str, action: str, description: str,
                          level: ActivityLevel = ActivityLevel.INFO,
                          metadata: Optional[Dict] = None):
        """Track system events"""
        self._log_activity(
            activity_type=ActivityType.SYSTEM_EVENT,
            level=level,
            module=module,
            action=action,
            description=description,
            metadata=metadata
        )
    
    def track_error(self, module: str, action: str, error: Exception,
                   description: Optional[str] = None, metadata: Optional[Dict] = None):
        """Track errors with full details"""
        error_details = str(error)
        stack_trace = traceback.format_exc()
        
        self._log_activity(
            activity_type=ActivityType.ERROR,
            level=ActivityLevel.ERROR,
            module=module,
            action=action,
            description=description or f"Error in {action}: {error_details}",
            error_details=error_details,
            stack_trace=stack_trace,
            metadata=metadata
        )
    
    def track_performance_start(self, operation_id: str, module: str, action: str):
        """Start tracking performance for an operation"""
        self.start_times[operation_id] = datetime.now()
        self.track_system_event(module, f"{action}_start", f"Started {action}", 
                               ActivityLevel.DEBUG, {"operation_id": operation_id})
    
    def track_performance_end(self, operation_id: str, module: str, action: str,
                             description: Optional[str] = None, metadata: Optional[Dict] = None):
        """End tracking performance for an operation"""
        if operation_id in self.start_times:
            start_time = self.start_times.pop(operation_id)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self._log_activity(
                activity_type=ActivityType.PERFORMANCE,
                level=ActivityLevel.DEBUG,
                module=module,
                action=action,
                description=description or f"Completed {action}",
                execution_time=execution_time,
                metadata={"operation_id": operation_id, **(metadata or {})}
            )
    
    def track_import_export(self, module: str, action: str, description: str,
                           file_path: Optional[str] = None, record_count: Optional[int] = None,
                           metadata: Optional[Dict] = None):
        """Track import/export operations"""
        self._log_activity(
            activity_type=ActivityType.IMPORT_EXPORT,
            level=ActivityLevel.INFO,
            module=module,
            action=action,
            description=description,
            metadata={
                "file_path": file_path,
                "record_count": record_count,
                **(metadata or {})
            }
        )
    
    def track_notification(self, notification_type: str, title: str, message: str,
                          metadata: Optional[Dict] = None):
        """Track notification events"""
        self._log_activity(
            activity_type=ActivityType.NOTIFICATION,
            level=ActivityLevel.DEBUG,
            module="notification_system",
            action="notification_sent",
            description=f"{notification_type}: {title} - {message}",
            metadata={"type": notification_type, "title": title, **(metadata or {})}
        )
    
    def track_ingredient_auto_add(self, ingredient_name: str, category: str, 
                                 recipe_context: Optional[str] = None, metadata: Optional[Dict] = None):
        """Track automatic ingredient additions"""
        self._log_activity(
            activity_type=ActivityType.INGREDIENT_AUTO_ADD,
            level=ActivityLevel.INFO,
            module="smart_ingredient_manager",
            action="auto_add_ingredient",
            description=f"Auto-added ingredient '{ingredient_name}' with category '{category}'",
            metadata={
                "ingredient_name": ingredient_name,
                "category": category,
                "recipe_context": recipe_context,
                **(metadata or {})
            }
        )
    
    def _log_activity(self, activity_type: ActivityType, level: ActivityLevel,
                     module: str, action: str, description: str,
                     data_before: Optional[Dict] = None, data_after: Optional[Dict] = None,
                     execution_time: Optional[float] = None, error_details: Optional[str] = None,
                     stack_trace: Optional[str] = None, metadata: Optional[Dict] = None):
        """Internal method to log activities"""
        
        activity = ActivityRecord(
            timestamp=datetime.now().isoformat(),
            activity_type=activity_type.value,
            level=level.value,
            module=module,
            action=action,
            description=description,
            user_id=self.user_id,
            session_id=self.session_id,
            data_before=data_before,
            data_after=data_after,
            execution_time=execution_time,
            error_details=error_details,
            stack_trace=stack_trace,
            metadata=metadata
        )
        
        self.activities.append(activity)
        self.activity_logged.emit(activity)
        
        # Also log to standard logger
        log_level = getattr(logging, level.value.upper(), logging.INFO)
        self.logger.log(log_level, f"[{activity_type.value}] {module}.{action}: {description}")
    
    def get_activities(self, 
                      activity_type: Optional[ActivityType] = None,
                      level: Optional[ActivityLevel] = None,
                      module: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: Optional[int] = None) -> List[ActivityRecord]:
        """Get filtered activities"""
        
        filtered_activities = self.activities.copy()
        
        # Apply filters
        if activity_type:
            filtered_activities = [a for a in filtered_activities if a.activity_type == activity_type.value]
        
        if level:
            filtered_activities = [a for a in filtered_activities if a.level == level.value]
        
        if module:
            filtered_activities = [a for a in filtered_activities if a.module == module]
        
        if start_time:
            start_iso = start_time.isoformat()
            filtered_activities = [a for a in filtered_activities if a.timestamp >= start_iso]
        
        if end_time:
            end_iso = end_time.isoformat()
            filtered_activities = [a for a in filtered_activities if a.timestamp <= end_iso]
        
        # Sort by timestamp (newest first)
        filtered_activities.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            filtered_activities = filtered_activities[:limit]
        
        return filtered_activities
    
    def get_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get activity summary for the last N hours"""
        start_time = datetime.now() - timedelta(hours=hours)
        recent_activities = self.get_activities(start_time=start_time)
        
        summary = {
            "total_activities": len(recent_activities),
            "by_type": {},
            "by_level": {},
            "by_module": {},
            "errors": 0,
            "performance_avg": 0,
            "most_active_module": None
        }
        
        # Count by type, level, module
        for activity in recent_activities:
            # By type
            summary["by_type"][activity.activity_type] = summary["by_type"].get(activity.activity_type, 0) + 1
            
            # By level
            summary["by_level"][activity.level] = summary["by_level"].get(activity.level, 0) + 1
            
            # By module
            summary["by_module"][activity.module] = summary["by_module"].get(activity.module, 0) + 1
            
            # Count errors
            if activity.level == ActivityLevel.ERROR.value:
                summary["errors"] += 1
        
        # Find most active module
        if summary["by_module"]:
            summary["most_active_module"] = max(summary["by_module"], key=summary["by_module"].get)
        
        # Calculate average performance
        performance_activities = [a for a in recent_activities if a.execution_time is not None]
        if performance_activities:
            summary["performance_avg"] = sum(a.execution_time for a in performance_activities) / len(performance_activities)
        
        return summary
    
    def save_activities(self):
        """Save activities to file"""
        try:
            os.makedirs(os.path.dirname(self.activities_file), exist_ok=True)
            
            # Convert activities to dict format
            activities_data = [asdict(activity) for activity in self.activities]
            
            with open(self.activities_file, 'w') as f:
                json.dump(activities_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving activities: {e}")
    
    def load_activities(self):
        """Load activities from file"""
        try:
            if os.path.exists(self.activities_file):
                with open(self.activities_file, 'r') as f:
                    activities_data = json.load(f)
                
                self.activities = [ActivityRecord(**data) for data in activities_data]
                self.logger.info(f"Loaded {len(self.activities)} activities from file")
            
        except Exception as e:
            self.logger.error(f"Error loading activities: {e}")
            self.activities = []
    
    def rotate_daily_logs(self):
        """Rotate logs daily to prevent file size issues"""
        try:
            today = datetime.now().date()
            
            # Create daily activities directory
            os.makedirs(self.daily_activities_dir, exist_ok=True)
            
            # Move old activities to daily file
            old_activities = []
            current_activities = []
            
            for activity in self.activities:
                activity_date = datetime.fromisoformat(activity.timestamp).date()
                if activity_date < today:
                    old_activities.append(activity)
                else:
                    current_activities.append(activity)
            
            # Save old activities to daily file
            if old_activities:
                yesterday = today - timedelta(days=1)
                daily_file = os.path.join(self.daily_activities_dir, f"activities_{yesterday.isoformat()}.json")
                
                activities_data = [asdict(activity) for activity in old_activities]
                with open(daily_file, 'w') as f:
                    json.dump(activities_data, f, indent=2)
                
                self.logger.info(f"Rotated {len(old_activities)} activities to {daily_file}")
            
            # Keep only current activities in memory
            self.activities = current_activities
            
        except Exception as e:
            self.logger.error(f"Error rotating daily logs: {e}")
    
    def export_activities_csv(self, file_path: str, 
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> bool:
        """Export activities to CSV file"""
        try:
            activities = self.get_activities(start_time=start_date, end_time=end_date)
            
            # Convert to DataFrame
            data = []
            for activity in activities:
                row = {
                    'timestamp': activity.timestamp,
                    'type': activity.activity_type,
                    'level': activity.level,
                    'module': activity.module,
                    'action': activity.action,
                    'description': activity.description,
                    'user_id': activity.user_id,
                    'session_id': activity.session_id,
                    'execution_time': activity.execution_time,
                    'error_details': activity.error_details
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            self.track_import_export("activity_tracker", "export_csv", 
                                   f"Exported {len(activities)} activities to CSV",
                                   file_path=file_path, record_count=len(activities))
            
            return True
            
        except Exception as e:
            self.track_error("activity_tracker", "export_csv", e)
            return False

# Global activity tracker instance
_activity_tracker = None

def get_activity_tracker():
    """Get global activity tracker instance"""
    global _activity_tracker
    if _activity_tracker is None:
        _activity_tracker = ActivityTracker()
    return _activity_tracker

# Convenience functions for easy tracking
def track_user_action(module: str, action: str, description: str, **kwargs):
    """Track user action"""
    get_activity_tracker().track_user_action(module, action, description, **kwargs)

def track_navigation(from_page: str, to_page: str, **kwargs):
    """Track navigation"""
    get_activity_tracker().track_navigation(from_page, to_page, **kwargs)

def track_data_change(module: str, action: str, description: str, **kwargs):
    """Track data change"""
    get_activity_tracker().track_data_change(module, action, description, **kwargs)

def track_system_event(module: str, action: str, description: str, **kwargs):
    """Track system event"""
    get_activity_tracker().track_system_event(module, action, description, **kwargs)

def track_error(module: str, action: str, error: Exception, **kwargs):
    """Track error"""
    get_activity_tracker().track_error(module, action, error, **kwargs)

def track_performance_start(operation_id: str, module: str, action: str):
    """Start performance tracking"""
    get_activity_tracker().track_performance_start(operation_id, module, action)

def track_performance_end(operation_id: str, module: str, action: str, **kwargs):
    """End performance tracking"""
    get_activity_tracker().track_performance_end(operation_id, module, action, **kwargs)
