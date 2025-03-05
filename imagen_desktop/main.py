#!/usr/bin/env python3
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox

from imagen_desktop.ui.main_window import MainWindow
from imagen_desktop.data import initialize_database
from imagen_desktop.utils.debug_logger import logger

def initialize_app():
    """Initialize application components."""
    try:
        # Initialize database
        logger.info("Initializing database...")
        database = initialize_database()
        
        if database is None:
            logger.warning("Application will start with limited functionality")
            
        return database
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    try:
        # Initialize components
        database = initialize_app()
        
        # Load stylesheet
        try:
            stylesheet_path = Path(__file__).parent.parent / 'resources' / 'styles' / 'main.qss'
            if stylesheet_path.exists():
                with open(stylesheet_path, 'r') as f:
                    app.setStyleSheet(f.read())
        except Exception as e:
            # Skip stylesheet if not found or can't be loaded
            logger.warning(f"Failed to load stylesheet: {e}")
        
        # Create and show main window
        window = MainWindow(database)
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        
        # Show error dialog
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Startup Error")
        error_dialog.setText("Application startup failed")
        error_dialog.setInformativeText(str(e))
        error_dialog.setDetailedText(f"Error details:\n{str(e)}")
        error_dialog.exec()
        
        sys.exit(1)

if __name__ == '__main__':
    main()