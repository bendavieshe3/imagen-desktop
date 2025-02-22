#!/usr/bin/env python3
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from imagen_desktop.ui.main_window import MainWindow
from imagen_desktop.data.database import Database
from imagen_desktop.utils.debug_logger import logger

def initialize_database() -> Database:
    """Initialize application database."""
    try:
        # Set up database path
        data_dir = Path.home() / '.imagen-desktop'
        db_path = data_dir / 'imagen.db'
        
        # Create and initialize database
        database = Database(db_path)
        database.initialize()
        
        logger.info("Database initialization complete")
        return database
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def initialize_app():
    """Initialize application components."""
    try:
        # Initialize database
        logger.info("Initializing database...")
        database = initialize_database()
        
        return database
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

def main():
    app = QApplication(sys.argv)
    
    try:
        # Initialize components
        database = initialize_app()
        
        # Load stylesheet
        try:
            with open('resources/styles/main.qss', 'r') as f:
                app.setStyleSheet(f.read())
        except FileNotFoundError:
            # Skip stylesheet if not found
            pass
        
        # Create and show main window
        window = MainWindow(database)
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

if __name__ == '__main__':
    main()