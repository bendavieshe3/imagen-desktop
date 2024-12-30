"""Main menu bar for the application."""
from PyQt6.QtWidgets import QMenuBar, QMenu, QApplication
from PyQt6.QtGui import QAction
from typing import Optional, Callable

class MainMenuBar(QMenuBar):
    """Menu bar for the main application window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_menus()
    
    def _init_menus(self):
        """Initialize all menus."""
        self._create_file_menu()
        self._create_view_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """Create the File menu."""
        file_menu = self.addMenu("&File")
        
        # Models action
        self.models_action = QAction("Manage Models...", self)
        file_menu.addAction(self.models_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)
    
    def _create_view_menu(self):
        """Create the View menu."""
        view_menu = self.addMenu("&View")
        
        # Generate tab action
        self.generate_action = QAction("Generate", self)
        view_menu.addAction(self.generate_action)
        
        # Gallery tab action
        self.gallery_action = QAction("Gallery", self)
        view_menu.addAction(self.gallery_action)
    
    def _create_help_menu(self):
        """Create the Help menu."""
        help_menu = self.addMenu("&Help")
        
        # About action
        self.about_action = QAction("&About", self)
        help_menu.addAction(self.about_action)
    
    def connect_actions(self, 
                       show_models: Optional[Callable] = None,
                       show_generate: Optional[Callable] = None,
                       show_gallery: Optional[Callable] = None,
                       show_about: Optional[Callable] = None):
        """Connect menu actions to callbacks."""
        if show_models:
            self.models_action.triggered.connect(show_models)
        
        if show_generate:
            self.generate_action.triggered.connect(show_generate)
        
        if show_gallery:
            self.gallery_action.triggered.connect(show_gallery)
        
        if show_about:
            self.about_action.triggered.connect(show_about)