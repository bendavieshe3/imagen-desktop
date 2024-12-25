#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .data.db_utils import init_database
from .utils.debug_logger import logger

def initialize_app():
    """Initialize application components."""
    try:
        # Initialize database and get session factory
        logger.info("Initializing database...")
        session_factory = init_database()
        logger.info("Database initialization complete")
        
        return session_factory
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

def main():
    app = QApplication(sys.argv)
    
    try:
        # Initialize components
        session_factory = initialize_app()
        
        # Load stylesheet
        try:
            with open('resources/styles/main.qss', 'r') as f:
                app.setStyleSheet(f.read())
        except FileNotFoundError:
            # Skip stylesheet if not found
            pass
        
        # Create and show main window
        window = MainWindow(session_factory)
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

if __name__ == '__main__':
    main()