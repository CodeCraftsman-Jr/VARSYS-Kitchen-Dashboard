import os
import sys
import time
import logging
import traceback
import inspect
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class LogSignal(QObject):
    """Signal emitter for logs to enable communication with UI"""
    new_log = Signal(str, str, str, str, str)  # level, message, timestamp, caller_info, stack_trace

class AppLogger:
    """Application logger with UI signal support"""
    _instance = None
    _log_buffer = []  # Buffer to store logs before UI initialization
    _max_buffer_size = 1000  # Maximum number of logs to keep in memory
    
    def __init__(self):
        self.logger = logging.getLogger('KitchenDashboard')
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler for logging to file
        log_file = os.path.join(logs_dir, f'kitchen_dashboard_{datetime.now().strftime("%Y-%m-%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for logging to console with UTF-8 encoding
        # Use a special StreamHandler that handles Unicode characters properly
        class UTF8StreamHandler(logging.StreamHandler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    stream = self.stream
                    # Replace problematic Unicode characters with their ASCII equivalents
                    # For example, replace Indian Rupee symbol with 'Rs.'
                    msg = msg.replace('₹', 'Rs.')
                    msg = msg.replace('€', 'EUR')
                    msg = msg.replace('£', 'GBP')
                    msg = msg.replace('¥', 'JPY')
                    stream.write(msg + self.terminator)
                    self.flush()
                except Exception:
                    self.handleError(record)
        
        console_handler = UTF8StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add them to handlers
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
        console_formatter = logging.Formatter('%(levelname)s [%(funcName)s:%(lineno)d]: %(message)s')
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Create signal emitter for UI updates
        self.signal = LogSignal()
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of AppLogger"""
        if cls._instance is None:
            cls._instance = AppLogger()
        return cls._instance
    
    @classmethod
    def _add_to_buffer(cls, level, message, caller_info="", stack_trace=""):
        """Add log to buffer and trim if necessary"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        cls._log_buffer.append((level, message, timestamp, caller_info, stack_trace))

        # Trim buffer if it exceeds max size
        if len(cls._log_buffer) > cls._max_buffer_size:
            cls._log_buffer = cls._log_buffer[-cls._max_buffer_size:]

    def _get_caller_info(self):
        """Get information about the calling function"""
        try:
            # Get the current frame and go up the stack
            frame = inspect.currentframe()
            # Go up 3 levels: _get_caller_info -> log_method -> actual_caller
            for _ in range(3):
                frame = frame.f_back
                if frame is None:
                    break

            if frame:
                filename = os.path.basename(frame.f_code.co_filename)
                function_name = frame.f_code.co_name
                line_number = frame.f_lineno
                return f"{filename}:{function_name}:{line_number}"
            else:
                return "unknown:unknown:0"
        except Exception:
            return "error:error:0"

    def _get_stack_trace(self, include_full_trace=False):
        """Get current stack trace"""
        try:
            if include_full_trace:
                return traceback.format_stack()
            else:
                # Get just the last few frames for context
                stack = traceback.format_stack()
                return stack[-5:] if len(stack) > 5 else stack
        except Exception:
            return ["Stack trace unavailable"]
    
    @classmethod
    def get_log_buffer(cls):
        """Get current log buffer"""
        return cls._log_buffer
    
    @classmethod
    def clear_log_buffer(cls):
        """Clear log buffer"""
        cls._log_buffer = []
    
    def debug(self, message, include_stack=False):
        """Log debug message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        self.logger.debug(message)
        self._add_to_buffer('DEBUG', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('DEBUG', message, timestamp, caller_info, stack_trace)

    def info(self, message, include_stack=False):
        """Log info message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        self.logger.info(message)
        self._add_to_buffer('INFO', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('INFO', message, timestamp, caller_info, stack_trace)

    def warning(self, message, include_stack=False):
        """Log warning message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        self.logger.warning(message)
        self._add_to_buffer('WARNING', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('WARNING', message, timestamp, caller_info, stack_trace)

    def error(self, message, include_stack=True):
        """Log error message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        self.logger.error(message)
        self._add_to_buffer('ERROR', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('ERROR', message, timestamp, caller_info, stack_trace)

    def critical(self, message, include_stack=True):
        """Log critical message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        self.logger.critical(message)
        self._add_to_buffer('CRITICAL', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('CRITICAL', message, timestamp, caller_info, stack_trace)

# Shorthand function to get logger instance
def get_logger():
    return AppLogger.get_instance()
