"""Logging configuration for the application."""
import sys
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Global constants
APP_NAME = 'replicate-desktop'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DEFAULT_LOG_LEVEL = logging.INFO  # Default to INFO level
DEBUG_LOG_LEVEL = logging.DEBUG  # Used when debug mode is enabled

class SingletonLogger:
    """Ensures only one logger instance is created."""
    _instance = None
    
    @classmethod
    def get_logger(cls, name=APP_NAME):
        """Get or create the singleton logger instance."""
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance
    
    @classmethod
    def _setup_logger(cls, name):
        """Configure the application logger with appropriate handlers."""
        logger = logging.getLogger(name)
        
        # Only add handlers if none exist
        if not logger.handlers:
            logger.setLevel(DEFAULT_LOG_LEVEL)
            
            # Determine if debug mode is enabled
            debug_mode = os.environ.get('REPLICATE_DEBUG', '').lower() in ('1', 'true')
            if debug_mode:
                logger.setLevel(DEBUG_LOG_LEVEL)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(console_handler)
            
            # File handler for debug logging
            if debug_mode:
                log_dir = Path.home() / '.replicate-desktop' / 'logs'
                log_dir.mkdir(parents=True, exist_ok=True)
                
                file_handler = RotatingFileHandler(
                    log_dir / 'debug.log',
                    maxBytes=5*1024*1024,  # 5MB
                    backupCount=3
                )
                file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
                file_handler.setLevel(DEBUG_LOG_LEVEL)
                logger.addHandler(file_handler)
        
        return logger

# Create the default logger instance
logger = SingletonLogger.get_logger()

# Optional: Function to change log level at runtime
def set_log_level(level):
    """Change the log level of the logger at runtime."""
    logger = SingletonLogger.get_logger()
    logger.setLevel(level)
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
            handler.setLevel(level)