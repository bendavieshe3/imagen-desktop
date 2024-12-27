"""Main window for the Replicate Desktop application."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMessageBox, QStatusBar, QApplication
)
from sqlalchemy.orm import sessionmaker
from typing import List
from pathlib import Path

from .generation_form import GenerationForm
from .gallery_view import GalleryView
from .main_window_presenter import MainWindowPresenter
from .dialogs.model_manager import ModelManager
from .main_menu_bar import MainMenuBar
from ..utils.debug_logger import logger

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, session_factory: sessionmaker = None):
        super().__init__()
        self.setWindowTitle("Replicate Desktop")
        self.setMinimumSize(1024, 768)
        
        # Initialize presenter
        self.presenter = MainWindowPresenter(session_factory, self)
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Menu bar
        self.menu_bar = MainMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.connect_actions(
            show_models=self._show_model_manager,
            show_generate=lambda: self.tab_widget.setCurrentWidget(self.generation_form),
            show_gallery=lambda: self.tab_widget.setCurrentWidget(self.gallery_view),
            show_about=self._show_about
        )
        
        # Central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Initialize main components
        self.generation_form = GenerationForm(
            self.presenter.api_handler,
            model_repository=self.presenter.model_repository
        )
        self.gallery_view = GalleryView(
            self.presenter.image_model,
            product_repository=self.presenter.product_repository
        )
        
        # Add tabs
        self.tab_widget.addTab(self.generation_form, "Generate")
        self.tab_widget.addTab(self.gallery_view, "Gallery")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def _connect_signals(self):
        """Connect signals between components."""
        logger.debug("Connecting MainWindow signals")
        self.generation_form.generation_requested.connect(self._handle_generation_request)
    
    def _handle_generation_request(self, model: str, params: dict):
        """Handle generation request from the form."""
        try:
            self.presenter.start_generation(model, params)
        except Exception as e:
            self.show_error("Generation Error", str(e))
    
    def _show_model_manager(self):
        """Show the model manager dialog."""
        if self.presenter.model_repository:
            dialog = ModelManager(self.presenter.api_handler, self.presenter.model_repository, self)
            dialog.exec()
        else:
            self.show_error("Not Available", "Model management requires database support.")
    
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Replicate Desktop",
            "A desktop client for Replicate's image generation models.\n\n"
            "Version 0.1.0\n"
            "© 2024 Contributors"
        )
    
    def show_status(self, message: str, timeout: int = 5000):
        """Show a message in the status bar."""
        self.status_bar.showMessage(message, timeout)
    
    def show_error(self, title: str, message: str):
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)
    
    def on_generation_complete(self, prediction_id: str, saved_paths: List[Path]):
        """Handle completed generation."""
        self.show_status(
            f"Generation completed: {prediction_id} - Images saved successfully",
            5000
        )
        self.tab_widget.setCurrentWidget(self.gallery_view)
        self.gallery_view.refresh_gallery()
    
    def on_generation_failed(self, prediction_id: str, error: str):
        """Handle failed generation."""
        self.show_status(f"Generation failed: {error}", 5000)
        self.show_error("Generation Failed", f"Generation failed: {error}")
    
    def closeEvent(self, event):
        """Handle application close."""
        logger.debug("Application closing")
        event.accept()