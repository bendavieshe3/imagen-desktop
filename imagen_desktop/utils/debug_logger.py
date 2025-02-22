"""Logging configuration for the application."""
import sys
import json
import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

# Global constants
APP_NAME = 'imagen-desktop'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DEFAULT_LOG_LEVEL = logging.INFO
DEBUG_LOG_LEVEL = logging.DEBUG

# Define standard log levels for different types of events
TRACE_LEVEL = 5  # Custom level for very detailed debugging
logging.addLevelName(TRACE_LEVEL, 'TRACE')

class StructuredLogger(logging.Logger):
    """Logger that supports structured logging with additional context."""
    
    def _log_structured(self, level: int, msg: str, context: Dict[str, Any] = None, **kwargs):
        """Add structured context to log message."""
        if context:
            structured_msg = {
                'message': msg,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context
            }
            msg = json.dumps(structured_msg)
        super().log(level, msg, **kwargs)
    
    def trace(self, msg: str, *args, **kwargs):
        """Log at TRACE level."""
        if self.isEnabledFor(TRACE_LEVEL):
            self._log_structured(TRACE_LEVEL, msg, *args, **kwargs)

class LoggerFactory:
    """Factory for creating and configuring loggers."""
    
    @staticmethod
    def get_log_dir() -> Path:
        """Get the logging directory."""
        log_dir = Path.home() / '.imagen-desktop' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    @staticmethod
    def create_logger(name: str = APP_NAME) -> StructuredLogger:
        """Create and configure a new logger instance."""
        logging.setLoggerClass(StructuredLogger)
        logger = logging.getLogger(name)
        
        # Only configure if not already set up
        if not logger.handlers:
            # Determine log level from environment
            debug_mode = os.environ.get('IMAGEN_DEBUG', '').lower() in ('1', 'true')
            log_level = DEBUG_LOG_LEVEL if debug_mode else DEFAULT_LOG_LEVEL
            
            logger.setLevel(log_level)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            console_handler.setLevel(log_level)
            logger.addHandler(console_handler)
            
            # File handler for all logs
            log_dir = LoggerFactory.get_log_dir()
            file_handler = RotatingFileHandler(
                log_dir / 'app.log',
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5
            )
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
            
            # Debug file handler (always at DEBUG level)
            if debug_mode:
                debug_handler = RotatingFileHandler(
                    log_dir / 'debug.log',
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=3
                )
                debug_handler.setFormatter(logging.Formatter(LOG_FORMAT))
                debug_handler.setLevel(DEBUG_LOG_LEVEL)
                logger.addHandler(debug_handler)
        
        return logger

class LogManager:
    """Singleton manager for application logging."""
    _instance = None
    _logger = None
    
    @classmethod
    def get_logger(cls, name: str = APP_NAME) -> StructuredLogger:
        """Get or create the singleton logger instance."""
        if cls._logger is None:
            cls._logger = LoggerFactory.create_logger(name)
        return cls._logger
    
    @classmethod
    def set_log_level(cls, level: int):
        """Change the log level of all handlers."""
        logger = cls.get_logger()
        logger.setLevel(level)
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)

# Create the default logger instance
logger = LogManager.get_logger()