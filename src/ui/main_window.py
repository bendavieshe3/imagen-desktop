from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt
from .generation_form import GenerationForm
from .gallery_view import GalleryView
from ..models.image_generation import ImageGenerationModel
from ..utils.api_handler import APIHandler
from ..utils.debug_logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Replicate Desktop")
        self.setMinimumSize(800, 600)
        
        # Initialize components
        logger.info("Initializing MainWindow components")
        self.api_handler = APIHandler()
        self.image_model = ImageGenerationModel()
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create and add tabs
        self.generation_form = GenerationForm(self.api_handler)
        self.gallery_view = GalleryView(self.image_model)
        
        self.tab_widget.addTab(self.generation_form, "Generate")
        self.tab_widget.addTab(self.gallery_view, "Gallery")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def _connect_signals(self):
        """Connect signals between components."""
        logger.info("Connecting MainWindow signals")
        
        # Connect API handler signals
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
        
        # Connect generation form signals
        self.generation_form.generation_requested.connect(self._start_generation)
        logger.info("Connected generation_requested signal")
    
    def _start_generation(self, model: str, params: dict):
        """Start a new image generation."""
        logger.info(f"Starting generation with model: {model}")
        try:
            prediction_id = self.api_handler.generate_images(model, params)
            logger.info(f"Got prediction ID: {prediction_id}")
            
            # Create initial metadata
            metadata = self.image_model.add_generation(
                prediction_id=prediction_id,
                model=model,
                prompt=params.get('prompt', ''),
                parameters=params,
                output_paths=[]  # Will be updated when generation completes
            )
            logger.info(f"Created initial metadata for {prediction_id}")
            
        except Exception as e:
            logger.error(f"Failed to start generation: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to start generation: {str(e)}")
    
    def _on_generation_started(self, prediction_id: str):
        """Handle generation started signal."""
        logger.info(f"Generation started: {prediction_id}")
        self.status_bar.showMessage(f"Generation started: {prediction_id}")
        self.image_model.update_generation_status(prediction_id, "running")
    
    def _on_generation_completed(self, prediction_id: str, output_files: list):
        """Handle generation completed signal."""
        logger.info(f"Generation completed: {prediction_id}")
        try:
            # Save output files
            saved_paths = self.api_handler.save_generation_output(prediction_id, output_files)
            logger.info(f"Saved output files: {saved_paths}")
            
            # Update generation metadata
            generation = self.image_model.get_generation(prediction_id)
            if generation:
                logger.info(f"Updating metadata for {prediction_id}")
                self.image_model.add_generation(
                    prediction_id=prediction_id,
                    model=generation.model,
                    prompt=generation.prompt,
                    parameters=generation.parameters,
                    output_paths=saved_paths
                )
            
            # Switch to gallery tab and refresh
            self.tab_widget.setCurrentWidget(self.gallery_view)
            self.gallery_view.refresh_gallery()
            
            self.status_bar.showMessage(
                f"Generation completed: {prediction_id} - Images saved successfully",
                5000
            )
            
        except Exception as e:
            logger.error(f"Failed to handle completed generation: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                "Warning",
                f"Generation completed but failed to save outputs: {str(e)}"
            )
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failed signal."""
        logger.error(f"Generation failed: {prediction_id} - {error}")
        self.status_bar.showMessage(f"Generation failed: {error}", 5000)
        self.image_model.update_generation_status(prediction_id, "failed", error)
        QMessageBox.critical(self, "Error", f"Generation failed: {error}")
    
    def closeEvent(self, event):
        """Handle application close."""
        logger.info("Application closing")
        event.accept()