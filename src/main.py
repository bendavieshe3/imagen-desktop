#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    try:
        with open('resources/styles/main.qss', 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        # Skip stylesheet if not found
        pass
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()