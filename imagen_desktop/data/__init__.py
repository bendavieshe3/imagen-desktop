"""Database package for the application."""
from pathlib import Path
from typing import Optional
import os

from .database import Database
from ..utils.debug_logger import logger

def initialize_database(db_path: Optional[Path] = None) -> Optional[Database]:
    """
    Initialize database module and connection.
    
    Args:
        db_path: Optional path to database file. If not provided, 
                 a default location will be used.
                 
    Returns:
        Database instance or None if initialization failed
    """
    try:
        # Use provided path or default location
        if db_path is None:
            data_dir = Path.home() / '.imagen-desktop'
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / 'imagen.db'
        
        # Create and initialize database
        database = Database(db_path)
        database.initialize()
        
        logger.info(f"Database initialized successfully at {db_path}")
        return database
    
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Return None rather than raising to allow application to 
        # continue with limited functionality
        return None

def get_test_database() -> Database:
    """
    Get a database instance for testing.
    
    Returns:
        Database instance configured for testing
    """
    # Use in-memory database for tests
    db_path = Path(":memory:")
    return Database(db_path)