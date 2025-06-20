import os
import sys
import time
import logging
import traceback
import inspect
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class SafeUnicodeFormatter(logging.Formatter):
    """Custom formatter that safely handles Unicode characters"""

    def format(self, record):
        # Get the formatted message
        formatted = super().format(record)

        # Replace emoji characters that cause encoding issues
        emoji_replacements = {
            '✅': '[SUCCESS]', '❌': '[ERROR]', '⚠️': '[WARNING]',
            '🔄': '[REFRESH]', '📋': '[LIST]', '📱': '[MOBILE]',
            '🔍': '[SEARCH]', '💾': '[SAVE]', '🎯': '[TARGET]',
            '🚀': '[START]', '🔧': '[DEBUG]', '📊': '[DATA]',
            '🎉': '[CELEBRATION]', '💡': '[IDEA]', '🔔': '[NOTIFICATION]',
            '📤': '[UPLOAD]', '📥': '[DOWNLOAD]', '🌐': '[NETWORK]',
            '🔒': '[SECURE]', '📈': '[CHART]', '📉': '[DECLINE]',
            '🚨': '[ALERT]', '🔴': '[RED]', '🟢': '[GREEN]',
            '🟡': '[YELLOW]', '🔵': '[BLUE]', '⭐': '[STAR]',
            '💰': '[MONEY]', '📝': '[NOTE]', '📅': '[CALENDAR]',
            '⏰': '[CLOCK]', '🔑': '[KEY]', '🎨': '[DESIGN]',
            '📸': '[PHOTO]', '🎵': '[MUSIC]', '🔊': '[SOUND]',
            '📡': '[SIGNAL]', '🌟': '[FEATURE]', '🏆': '[TROPHY]',
            'ℹ️': '[INFO]', '🔥': '[FIREBASE]', '💻': '[COMPUTER]'
        }

        for emoji, replacement in emoji_replacements.items():
            formatted = formatted.replace(emoji, replacement)

        # Final fallback: encode to ASCII with replacement for any remaining Unicode
        try:
            formatted.encode('ascii')
            return formatted
        except UnicodeEncodeError:
            return formatted.encode('ascii', errors='replace').decode('ascii')

    def formatException(self, ei):
        """Format exception with safe Unicode handling"""
        result = super().formatException(ei)
        try:
            result.encode('ascii')
            return result
        except UnicodeEncodeError:
            return result.encode('ascii', errors='replace').decode('ascii')

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

        # Create logs directory - handle both executable and development modes
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                app_dir = os.path.dirname(sys.executable)
                logs_dir = os.path.join(app_dir, 'logs')
            else:
                # Running as script
                logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

            os.makedirs(logs_dir, exist_ok=True)
            self.logs_dir = logs_dir
        except Exception as e:
            # Fallback to temp directory
            import tempfile
            self.logs_dir = os.path.join(tempfile.gettempdir(), 'varsys_kitchen_logs')
            os.makedirs(self.logs_dir, exist_ok=True)
            print(f"Warning: Could not create logs in app directory, using temp: {self.logs_dir}")
            print(f"Error: {e}")
        
        # File handler for logging to file
        self.log_file = os.path.join(self.logs_dir, f'kitchen_dashboard_{datetime.now().strftime("%Y-%m-%d")}.log')
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Error-specific log file
        self.error_log_file = os.path.join(self.logs_dir, f'errors_{datetime.now().strftime("%Y-%m-%d")}.log')
        error_handler = logging.FileHandler(self.error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Console handler for logging to console with UTF-8 encoding and organized output
        class OrganizedConsoleHandler(logging.StreamHandler):
            def __init__(self, stream=None):
                # Force UTF-8 encoding for console output on Windows
                import sys
                import io
                if sys.platform == 'win32' and stream is None:
                    # Try to reconfigure stdout to use UTF-8
                    try:
                        if hasattr(sys.stdout, 'reconfigure'):
                            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                        stream = sys.stdout
                    except (AttributeError, OSError):
                        # Fallback: create a UTF-8 wrapper
                        try:
                            stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                        except:
                            stream = sys.stdout

                super().__init__(stream)
                self.last_category = None
                self.message_count = 0

            def emit(self, record):
                try:
                    msg = self.format(record)
                    stream = self.stream

                    # Replace problematic Unicode characters with their ASCII equivalents
                    msg = self._safe_encode_message(msg)



                    # Detect message category for organization
                    current_category = self._detect_category(record.getMessage())

                    # Add section headers for better organization
                    if current_category != self.last_category:
                        if self.last_category is not None:
                            self._safe_write("\n" + "="*60 + "\n")
                        self._safe_write(f"\n>>> {current_category.upper()} <<<\n")
                        self._safe_write("="*60 + "\n")
                        self.last_category = current_category
                        self.message_count = 0

                    self.message_count += 1

                    # Format the message with better structure
                    if record.levelname in ['ERROR', 'CRITICAL']:
                        self._safe_write(f"[{self.message_count:03d}] *** {record.levelname} *** {msg}\n")
                    elif record.levelname == 'WARNING':
                        self._safe_write(f"[{self.message_count:03d}] !!! {record.levelname} !!! {msg}\n")
                    else:
                        self._safe_write(f"[{self.message_count:03d}] {record.levelname}: {msg}\n")

                    self.flush()
                except Exception:
                    self.handleError(record)

            def _safe_encode_message(self, msg):
                """Safely encode message with emoji replacements"""
                # Replace currency symbols that might cause encoding issues
                msg = msg.replace('₹', 'Rs.')
                msg = msg.replace('€', 'EUR')
                msg = msg.replace('£', 'GBP')
                msg = msg.replace('¥', 'JPY')

                # Replace emoji characters that cause encoding issues
                emoji_replacements = {
                    '🔍': '[SEARCH]',
                    '📄': '[FILE]',
                    '✅': '[SUCCESS]',
                    '📋': '[LIST]',
                    '📊': '[DATA]',
                    '🆕': '[NEW]',
                    '❌': '[ERROR]',
                    '⏱️': '[TIME]',
                    '🚀': '[START]',
                    '🖥️': '[SYSTEM]',
                    '📁': '[FOLDER]',
                    '🖱️': '[UI]',
                    '🔧': '[DEBUG]',
                    '⚠️': '[WARNING]',
                    '🔔': '[NOTIFICATION]',
                    '🍳': '[KITCHEN]',
                    '🟢': '[ACTIVE]',
                    '🔥': '[FIREBASE]',
                    '💾': '[SAVE]',
                    '🎯': '[TARGET]',
                    '🔄': '[REFRESH]',
                    '📦': '[PACKAGE]',
                    '🌐': '[NETWORK]',
                    '🔒': '[SECURE]',
                    '🔓': '[UNLOCK]',
                    '📈': '[CHART]',
                    '📉': '[DECLINE]',
                    '💡': '[IDEA]',
                    '🚨': '[ALERT]',
                    '🔴': '[RED]',
                    '🟡': '[YELLOW]',
                    '🟠': '[ORANGE]',
                    '🔵': '[BLUE]',
                    '🟣': '[PURPLE]',
                    '⭐': '[STAR]',
                    '💰': '[MONEY]',
                    '🛒': '[CART]',
                    '📝': '[NOTE]',
                    '📅': '[CALENDAR]',
                    '⏰': '[CLOCK]',
                    '🔑': '[KEY]',
                    '🎨': '[DESIGN]',
                    '🧪': '[TEST]',
                    '🔬': '[ANALYZE]',
                    '📱': '[MOBILE]',
                    '💻': '[COMPUTER]',
                    '🖨️': '[PRINT]',
                    '📸': '[PHOTO]',
                    '🎵': '[MUSIC]',
                    '🔊': '[SOUND]',
                    '🔇': '[MUTE]',
                    '📡': '[SIGNAL]',
                    '🌟': '[FEATURE]',
                    '🎉': '[CELEBRATION]',
                    '🎊': '[PARTY]',
                    '🏆': '[TROPHY]',
                    '🥇': '[GOLD]',
                    '🥈': '[SILVER]',
                    '🥉': '[BRONZE]'
                }

                for emoji, replacement in emoji_replacements.items():
                    msg = msg.replace(emoji, replacement)

                return msg

            def _safe_write(self, text):
                """Safely write text with encoding fallback"""
                try:
                    self.stream.write(text)
                except UnicodeEncodeError:
                    # Fallback: encode to ASCII with replacement
                    safe_text = text.encode('ascii', errors='replace').decode('ascii')
                    self.stream.write(safe_text)

            def _detect_category(self, message):
                """Detect the category of the log message for organization"""
                message_lower = message.lower()

                if any(keyword in message_lower for keyword in ['processing', 'loading', 'loaded', 'file found', 'data']):
                    return "Data Loading"
                elif any(keyword in message_lower for keyword in ['firebase', 'sync', 'cloud', 'authentication']):
                    return "Firebase & Sync"
                elif any(keyword in message_lower for keyword in ['ui', 'layout', 'widget', 'sidebar', 'content', 'splitter']):
                    return "UI Initialization"
                elif any(keyword in message_lower for keyword in ['performance', 'optimizer', 'css', 'enhancer']):
                    return "Performance & Optimization"
                elif any(keyword in message_lower for keyword in ['responsive', 'pwa', 'enterprise', 'multi-ai']):
                    return "Advanced Features"
                elif any(keyword in message_lower for keyword in ['notification', 'bell', 'category', 'timer']):
                    return "System Features"
                elif any(keyword in message_lower for keyword in ['error', 'failed', 'exception', 'traceback']):
                    return "Errors & Issues"
                elif any(keyword in message_lower for keyword in ['startup', 'initialized', 'starting', 'application']):
                    return "Application Startup"
                else:
                    return "General"

        console_handler = OrganizedConsoleHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add them to handlers
        file_formatter = SafeUnicodeFormatter('%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
        error_formatter = SafeUnicodeFormatter('%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s\nMESSAGE: %(message)s\n' + '='*80)
        console_formatter = SafeUnicodeFormatter('%(message)s')  # Simplified for organized output

        file_handler.setFormatter(file_formatter)
        error_handler.setFormatter(error_formatter)
        console_handler.setFormatter(console_formatter)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        if not getattr(sys, 'frozen', False):  # Only add console in development
            self.logger.addHandler(console_handler)

        # Log startup information
        self.logger.info("="*80)
        self.logger.info("VARSYS Kitchen Dashboard - Logging System Initialized")
        self.logger.info(f"Application Mode: {'Executable' if getattr(sys, 'frozen', False) else 'Development'}")
        self.logger.info(f"Log Directory: {self.logs_dir}")
        self.logger.info(f"Main Log File: {self.log_file}")
        self.logger.info(f"Error Log File: {self.error_log_file}")
        self.logger.info("="*80)
        
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

    def _safe_encode_for_logging(self, message):
        """Safely encode message for logging to prevent Unicode errors"""
        if not isinstance(message, str):
            message = str(message)

        # Replace common emoji with ASCII equivalents
        emoji_replacements = {
            '✅': '[SUCCESS]', '❌': '[ERROR]', '⚠️': '[WARNING]',
            '🔄': '[REFRESH]', '📋': '[LIST]', '📱': '[MOBILE]',
            '🔍': '[SEARCH]', '💾': '[SAVE]', '🎯': '[TARGET]',
            '🚀': '[START]', '🔧': '[DEBUG]', '📊': '[DATA]',
            '🎉': '[CELEBRATION]', '💡': '[IDEA]', '🔔': '[NOTIFICATION]',
            '📤': '[UPLOAD]', '📥': '[DOWNLOAD]', '🌐': '[NETWORK]',
            '🔒': '[SECURE]', '📈': '[CHART]', '📉': '[DECLINE]',
            '🚨': '[ALERT]', '🔴': '[RED]', '🟢': '[GREEN]',
            '🟡': '[YELLOW]', '🔵': '[BLUE]', '⭐': '[STAR]',
            '💰': '[MONEY]', '📝': '[NOTE]', '📅': '[CALENDAR]',
            '⏰': '[CLOCK]', '🔑': '[KEY]', '🎨': '[DESIGN]',
            '📸': '[PHOTO]', '🎵': '[MUSIC]', '🔊': '[SOUND]',
            '📡': '[SIGNAL]', '🌟': '[FEATURE]', '🏆': '[TROPHY]',
            'ℹ️': '[INFO]', '📄': '[FILE]', '🖥️': '[SYSTEM]',
            '📁': '[FOLDER]', '🖱️': '[UI]', '🍳': '[KITCHEN]',
            '🔥': '[FIREBASE]', '📦': '[PACKAGE]', '🔓': '[UNLOCK]',
            '🧪': '[TEST]', '🔬': '[ANALYZE]', '💻': '[COMPUTER]',
            '🖨️': '[PRINT]', '🔇': '[MUTE]'
        }

        for emoji, replacement in emoji_replacements.items():
            message = message.replace(emoji, replacement)

        # Replace currency symbols
        message = message.replace('₹', 'Rs.')
        message = message.replace('€', 'EUR')
        message = message.replace('£', 'GBP')
        message = message.replace('¥', 'JPY')

        # Final fallback: encode to ASCII with replacement for any remaining Unicode
        try:
            # Test if the message can be encoded
            message.encode('ascii')
            return message
        except UnicodeEncodeError:
            # If it can't be encoded, replace problematic characters
            return message.encode('ascii', errors='replace').decode('ascii')
    
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

        # Apply safe encoding to message before logging
        safe_message = self._safe_encode_for_logging(message)

        self.logger.debug(safe_message)
        self._add_to_buffer('DEBUG', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('DEBUG', message, timestamp, caller_info, stack_trace)

    def info(self, message, include_stack=False):
        """Log info message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        # Apply safe encoding to message before logging
        safe_message = self._safe_encode_for_logging(message)

        self.logger.info(safe_message)
        self._add_to_buffer('INFO', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('INFO', message, timestamp, caller_info, stack_trace)

    def warning(self, message, include_stack=False):
        """Log warning message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        # Apply safe encoding to message before logging
        safe_message = self._safe_encode_for_logging(message)

        self.logger.warning(safe_message)
        self._add_to_buffer('WARNING', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('WARNING', message, timestamp, caller_info, stack_trace)

    def error(self, message, include_stack=True):
        """Log error message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        # Apply safe encoding to message before logging
        safe_message = self._safe_encode_for_logging(message)

        self.logger.error(safe_message)
        self._add_to_buffer('ERROR', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('ERROR', message, timestamp, caller_info, stack_trace)

    def critical(self, message, include_stack=True):
        """Log critical message"""
        caller_info = self._get_caller_info()
        stack_trace = "\n".join(self._get_stack_trace(include_stack)) if include_stack else ""

        # Apply safe encoding to message before logging
        safe_message = self._safe_encode_for_logging(message)

        self.logger.critical(safe_message)
        self._add_to_buffer('CRITICAL', message, caller_info, stack_trace)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.signal.new_log.emit('CRITICAL', message, timestamp, caller_info, stack_trace)

    def log_exception(self, exception, context=""):
        """Log exception with full traceback and context"""
        self.error(f"EXCEPTION OCCURRED: {context}")
        self.error(f"Exception Type: {type(exception).__name__}")
        self.error(f"Exception Message: {str(exception)}")
        self.error(f"Full Traceback:\n{traceback.format_exc()}")

    def log_startup_info(self):
        """Log comprehensive startup information"""
        self.info("VARSYS Kitchen Dashboard - Application Startup")
        self.info(f"Platform: {sys.platform}")
        self.info(f"Python Version: {sys.version.split()[0]}")
        self.info(f"Executable Mode: {getattr(sys, 'frozen', False)}")
        self.info(f"Working Directory: {os.getcwd()}")

        if getattr(sys, 'frozen', False):
            self.info(f"Executable Path: {sys.executable}")
            self.info(f"Application Directory: {os.path.dirname(sys.executable)}")

        self.info(f"Log Directory: {self.logs_dir}")
        self.info(f"Main Log: {os.path.basename(self.log_file)}")
        self.info(f"Error Log: {os.path.basename(self.error_log_file)}")

    def log_shutdown_info(self):
        """Log application shutdown information"""
        self.info("Application shutdown initiated")
        self.info("All systems terminated successfully")

    def log_section_header(self, section_name):
        """Log a section header for better organization"""
        self.info(f"Starting {section_name}")

    def log_section_footer(self, section_name, success=True, details=None):
        """Log a section completion"""
        status = "completed successfully" if success else "completed with issues"
        self.info(f"{section_name} {status}")
        if details:
            self.info(f"Details: {details}")

    def log_module_import(self, module_name, success=True, error=None):
        """Log module import attempts"""
        if success:
            self.debug(f"[SUCCESS] Successfully imported module: {module_name}")
        else:
            self.error(f"[ERROR] Failed to import module: {module_name}")
            if error:
                self.error(f"   Error: {str(error)}")

    def log_data_loading(self, data_type, success=True, details=None, error=None):
        """Log data loading operations"""
        if success:
            self.info(f"[DATA] Data loaded successfully: {data_type}")
            if details:
                self.info(f"   Details: {details}")
        else:
            self.error(f"[ERROR] Failed to load data: {data_type}")
            if error:
                self.error(f"   Error: {str(error)}")

    def log_ui_action(self, action, details=None):
        """Log user interface actions"""
        self.debug(f"[UI] UI Action: {action}")
        if details:
            self.debug(f"   Details: {details}")

    def log_performance(self, operation, duration, details=None):
        """Log performance metrics"""
        self.info(f"[TIME] Performance: {operation} took {duration:.2f}s")
        if details:
            self.info(f"   Details: {details}")

    def get_log_files(self):
        """Get paths to current log files"""
        try:
            if os.path.exists(self.logs_dir):
                log_files = []
                for file in os.listdir(self.logs_dir):
                    if file.endswith('.log'):
                        log_files.append(os.path.join(self.logs_dir, file))
                return sorted(log_files, key=os.path.getmtime, reverse=True)
        except Exception:
            pass
        return []

    def get_log_content(self, log_file_path, max_lines=1000):
        """Get content of a log file"""
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Return last max_lines
                return lines[-max_lines:] if len(lines) > max_lines else lines
        except Exception as e:
            return [f"Error reading log file: {str(e)}"]

    def get_system_info(self):
        """Get comprehensive system information for debugging"""
        info = []
        info.append("=== SYSTEM INFORMATION ===")
        info.append(f"Platform: {sys.platform}")
        info.append(f"Python Version: {sys.version}")
        info.append(f"Executable: {sys.executable}")
        info.append(f"Frozen (Compiled): {getattr(sys, 'frozen', False)}")
        info.append(f"Current Working Directory: {os.getcwd()}")

        if hasattr(self, 'logs_dir'):
            info.append(f"Logs Directory: {self.logs_dir}")

        info.append("\n=== ENVIRONMENT VARIABLES ===")
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['PATH', 'PYTHON', 'HOME', 'USER', 'TEMP']):
                info.append(f"{key}: {value}")

        info.append("\n=== LOG FILES ===")
        log_files = self.get_log_files()
        for log_file in log_files:
            try:
                size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
                modified = os.path.getmtime(log_file) if os.path.exists(log_file) else 0
                from datetime import datetime
                mod_time = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
                info.append(f"{os.path.basename(log_file)}: {size} bytes (modified: {mod_time})")
            except Exception as e:
                info.append(f"{os.path.basename(log_file)}: Error getting info - {e}")

        return '\n'.join(info)

# Shorthand function to get logger instance
def get_logger():
    return AppLogger.get_instance()

# Safe print function for Unicode handling
def safe_print(*args, **kwargs):
    """Safe print function that handles Unicode encoding errors"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Convert all arguments to safe ASCII
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace common emoji with ASCII equivalents
                safe_arg = str(arg)
                emoji_replacements = {
                    '✅': '[SUCCESS]', '❌': '[ERROR]', '⚠️': '[WARNING]',
                    '🔄': '[REFRESH]', '📋': '[LIST]', '📱': '[MOBILE]',
                    '🔍': '[SEARCH]', '💾': '[SAVE]', '🎯': '[TARGET]',
                    '🚀': '[START]', '🔧': '[DEBUG]', '📊': '[DATA]',
                    '🎉': '[CELEBRATION]', '💡': '[IDEA]', '🔔': '[NOTIFICATION]'
                }
                for emoji, replacement in emoji_replacements.items():
                    safe_arg = safe_arg.replace(emoji, replacement)

                # Encode to ASCII with replacement for any remaining Unicode
                safe_arg = safe_arg.encode('ascii', errors='replace').decode('ascii')
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)

        print(*safe_args, **kwargs)
