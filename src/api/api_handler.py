"""Main API handler coordinating all API-related operations."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from .client import ReplicateClient
from .prediction_manager import PredictionManager
from .output_manager import OutputManager
from ..models.image_generation import ImageGenerationModel, GenerationStatus
from ..utils.debug_logger import logger

class APIHandler(QObject):
    """Coordinates API operations and manages state."""
    
    # Forward signals from PredictionManager
    generation_started = pyqtSignal(str)
    generation_progress = pyqtSignal(str, int)
    generation_completed = pyqtSignal(str, list)
    generation_failed = pyqtSignal(str, str)
    generation_canceled = pyqtSignal(str)
    
    def __init__(self, image_model: Optional[ImageGenerationModel] = None):
        super().__init__()
        self.image_model = image_model or ImageGenerationModel()
        self._init_components()
        self._connect_signals()
    
    def _init_components(self):
        """Initialize API components."""
        self.client = ReplicateClient()
        self.prediction_manager = PredictionManager(self.client)
        self.output_manager = OutputManager(
            Path.home() / '.replicate-desktop' / 'cache'
        )
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.prediction_manager.generation_started.connect(self._handle_generation_started)
        self.prediction_manager.generation_progress.connect(self.generation_progress)
        self.prediction_manager.generation_completed.connect(self._handle_generation_completed)
        self.prediction_manager.generation_failed.connect(self._handle_generation_failed)
        self.prediction_manager.generation_canceled.connect(self._handle_generation_canceled)
    
    def list_available_models(self, collection: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available models, optionally filtered by collection."""
        return self.client.list_available_models(collection)
    
    def generate_images(self, model: str, params: Dict[str, Any]) -> str:
        """Start image generation and initialize history entry."""
        try:
            # First create prediction to get ID
            prediction_id = self.prediction_manager.start_prediction(model, params)
            logger.debug(f"Created prediction {prediction_id}")

            # Immediately create history entry
            self.image_model.add_generation(
                prediction_id=prediction_id,
                model=model,
                prompt=params.get('prompt', ''),
                parameters=params,
                output_paths=[],
                initial_status=GenerationStatus.STARTING
            )
            logger.debug(f"Added generation {prediction_id} to history")

            return prediction_id

        except Exception as e:
            logger.error(f"Failed to start generation: {e}")
            raise
    
    def cancel_generation(self, prediction_id: str):
        """Cancel an ongoing generation."""
        try:
            self.prediction_manager.cancel_prediction(prediction_id)
            self.image_model.update_generation_status(prediction_id, "cancelled")
        except Exception as e:
            logger.error(f"Failed to cancel generation {prediction_id}: {e}")
    
    def _handle_generation_started(self, prediction_id: str):
        """Handle generation started signal."""
        try:
            self.image_model.update_generation_status(prediction_id, "in_progress")
            self.generation_started.emit(prediction_id)
        except Exception as e:
            logger.error(f"Error handling generation started for {prediction_id}: {e}")
    
    def _handle_generation_completed(self, prediction_id: str, output_urls: List[str]):
        """Handle completed generation by saving outputs."""
        try:
            saved_paths = self.output_manager.save_outputs(prediction_id, output_urls)
            
            # Update the generation with saved paths
            generation = self.image_model.get_generation(prediction_id)
            if generation:
                self.image_model.update_generation(
                    prediction_id=prediction_id,
                    output_paths=saved_paths,
                    status=GenerationStatus.COMPLETED
                )
                logger.debug(f"Updated generation {prediction_id} with output paths")
            
            self.generation_completed.emit(prediction_id, saved_paths)
            
        except Exception as e:
            logger.error(f"Failed to save generation outputs: {e}")
            self.generation_failed.emit(
                prediction_id,
                f"Generation completed but failed to save outputs: {str(e)}"
            )
    
    def _handle_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failure."""
        try:
            self.image_model.handle_failed_generation(prediction_id, error)
            self.generation_failed.emit(prediction_id, error)
        except Exception as e:
            logger.error(f"Error handling generation failure for {prediction_id}: {e}")
    
    def _handle_generation_canceled(self, prediction_id: str):
        """Handle generation cancellation."""
        try:
            self.image_model.update_generation_status(prediction_id, "cancelled")
            self.generation_canceled.emit(prediction_id)
        except Exception as e:
            logger.error(f"Error handling generation cancellation for {prediction_id}: {e}")