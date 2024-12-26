"""Main window for the Replicate Desktop application."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from pathlib import Path
from sqlalchemy.orm import sessionmaker

from .generation_form import GenerationForm
from .gallery_view import GalleryView
from ..models.image_generation import ImageGenerationModel, GenerationStatus
from ..api.api_handler import APIHandler
from ..data.image_repository import ImageRepository
from ..data.model_repository import ModelRepository
from ..utils.debug_logger import logger

class MainWindow(QMainWindow):
    def __init__(self, session_factory: sessionmaker = None):
        super().__init__()
        self.setWindowTitle("Replicate Desktop")
        self.setMinimumSize(800, 600)
        
        # Initialize components
        logger.debug("Initializing MainWindow components")
        
        # Initialize storage mechanisms first
        self.image_model = ImageGenerationModel()  # File-based storage
        self.api_handler = APIHandler(image_model=self.image_model)
        
        if session_factory:
            self.image_repository = ImageRepository(session_factory)
            self.model_repository = ModelRepository(session_factory)
            logger.info("Database repositories initialized")
        else:
            self.image_repository = None
            self.model_repository = None
            logger.warning("Database storage not available")
        
        # Track active generations
        self.active_generations = set()
        
        self._init_ui()
        self._connect_signals()
        
        # Schedule initial model cache update
        # QTimer.singleShot(1000, self._update_model_cache)
        
        # Set up periodic model cache updates (every 12 hours)
        # self.cache_timer = QTimer(self)
        # self.cache_timer.timeout.connect(self._update_model_cache)
        # self.cache_timer.start(12 * 60 * 60 * 1000)  # 12 hours in milliseconds
    
    def _init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self.generation_form = GenerationForm(
            self.api_handler,
            model_repository=self.model_repository
        )
        self.gallery_view = GalleryView(self.image_model)
        
        self.tab_widget.addTab(self.generation_form, "Generate")
        self.tab_widget.addTab(self.gallery_view, "Gallery")
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def _connect_signals(self):
        """Connect signals between components."""
        logger.debug("Connecting MainWindow signals")
        
        # Connect API handler signals
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
        
        # Connect generation form signals
        self.generation_form.generation_requested.connect(self._start_generation)
    
    def _update_model_cache(self):
        """Update the cached model information from the API."""
        if not self.model_repository:
            return
            
        try:
            logger.debug("Updating model cache...")
            self.status_bar.showMessage("Updating model cache...", 3000)
            
            # Get models from API
            models = self.api_handler.list_available_models()
            
            # Update cache
            for model in models:
                try:
                    identifier = f"{model['owner']}/{model['name']}"
                    metadata = {
                        'collection': model.get('collection'),
                        'latest_version': model.get('latest_version'),
                        'version_count': model.get('version_count', 0)
                    }
                    
                    self.model_repository.add_or_update_model(
                        identifier=identifier,
                        name=model['name'],
                        owner=model['owner'],
                        description=model.get('description'),
                        metadata=metadata
                    )
                except Exception as e:
                    logger.error(f"Failed to cache model {identifier}: {e}")
            
            # Clean up old entries
            self.model_repository.cleanup_old_models(days=30)
            
            model_count = self.model_repository.count_models()
            logger.info(f"Model cache updated. Total models: {model_count}")
            self.status_bar.showMessage(f"Model cache updated. {model_count} models available.", 3000)
            
        except Exception as e:
            logger.error(f"Failed to update model cache: {e}")
            self.status_bar.showMessage("Failed to update model cache", 3000)
    
    def _create_generation_record(self, prediction_id: str, model: str, params: dict):
        """Create initial generation record in both storage systems."""
        logger.debug(f"Creating generation record for {prediction_id}")
        
        # Store in file-based system
        self.image_model.add_generation(
            prediction_id=prediction_id,
            model=model,
            prompt=params.get('prompt', ''),
            parameters=params,
            output_paths=[],
            initial_status=GenerationStatus.STARTING
        )
        
        # Store in database if available
        if self.image_repository:
            try:
                self.image_repository.add_generation(
                    prediction_id=prediction_id,
                    model=model,
                    prompt=params.get('prompt', ''),
                    parameters=params,
                    status=GenerationStatus.STARTING.value
                )
                logger.debug(f"Added generation {prediction_id} to database")
            except Exception as e:
                logger.error(f"Failed to add generation to database: {e}")
        
        # Track active generation
        self.active_generations.add(prediction_id)
    
    def _start_generation(self, model: str, params: dict):
        """Start a new image generation."""
        try:
            # First get prediction ID
            prediction_id = self.api_handler.generate_images(model, params)
            logger.debug(f"Created prediction {prediction_id} with model {model}")
            
            # Create initial records before notifying listeners
            self._create_generation_record(prediction_id, model, params)
            
            # Now notify that generation has started
            self.api_handler.notify_generation_started(prediction_id)
            
        except Exception as e:
            logger.error(f"Failed to start generation: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start generation: {str(e)}")
    
    def _on_generation_started(self, prediction_id: str):
        """Handle generation started signal."""
        if prediction_id not in self.active_generations:
            logger.warning(f"Received start signal for unknown generation: {prediction_id}")
            return
            
        logger.debug(f"Generation started: {prediction_id}")
        self.status_bar.showMessage(f"Generation started: {prediction_id}")
        
        # Update file-based storage
        self.image_model.update_generation_status(prediction_id, GenerationStatus.IN_PROGRESS.value)
        
        # Update database if available
        if self.image_repository:
            try:
                self.image_repository.update_generation_status(
                    prediction_id, 
                    GenerationStatus.IN_PROGRESS.value
                )
            except Exception as e:
                logger.error(f"Failed to update generation status in database: {e}")
    
    def _on_generation_completed(self, prediction_id: str, output_files: list):
        """Handle generation completed signal."""
        if prediction_id not in self.active_generations:
            logger.warning(f"Received completion signal for unknown generation: {prediction_id}")
            return
            
        try:
            if output_files and isinstance(output_files[0], Path):
                saved_paths = output_files
            else:
                saved_paths = self.api_handler.save_generation_output(prediction_id, output_files)
            
            # Update file-based storage
            self.image_model.update_generation(
                prediction_id=prediction_id,
                output_paths=saved_paths,
                status=GenerationStatus.COMPLETED
            )
            
            # Update database if available
            if self.image_repository:
                try:
                    for path in saved_paths:
                        self.image_repository.add_image(
                            generation_id=prediction_id,
                            file_path=path
                        )
                except Exception as e:
                    logger.error(f"Failed to add images to database: {e}")
            
            # Switch to gallery tab and refresh
            self.tab_widget.setCurrentWidget(self.gallery_view)
            self.gallery_view.refresh_gallery()
            
            self.status_bar.showMessage(
                f"Generation completed: {prediction_id} - Images saved successfully",
                5000
            )
            logger.debug(f"Generation {prediction_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to handle completed generation: {e}")
            QMessageBox.warning(
                self,
                "Warning",
                f"Generation completed but failed to save outputs: {str(e)}"
            )
        finally:
            self.active_generations.remove(prediction_id)
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failed signal."""
        if prediction_id not in self.active_generations:
            logger.warning(f"Received failure signal for unknown generation: {prediction_id}")
            return
            
        logger.error(f"Generation {prediction_id} failed: {error}")
        self.status_bar.showMessage(f"Generation failed: {error}", 5000)
        
        # Update both storage systems
        self.image_model.update_generation_status(prediction_id, GenerationStatus.FAILED.value, error)
        if self.image_repository:
            try:
                self.image_repository.update_generation_status(prediction_id, "failed", error)
            except Exception as e:
                logger.error(f"Failed to update generation status in database: {e}")
        
        QMessageBox.critical(self, "Error", f"Generation failed: {error}")
        self.active_generations.remove(prediction_id)
    
    def closeEvent(self, event):
        """Handle application close."""
        logger.debug("Application closing")
        # self.cache_timer.stop()
        event.accept()