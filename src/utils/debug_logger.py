import sys
import logging
from datetime import datetime

def setup_logger():
    """Configure debug logger for the application."""
    logger = logging.getLogger('replicate-desktop')
    logger.setLevel(logging.DEBUG)
    
    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Create global logger instance
logger = setup_logger()