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
    generation_started = pyqtSignal(str)  # prediction_id
    generation_progress = pyqtSignal(str, int)  # prediction_id, progress
    generation_completed = pyqtSignal(str, list)  # prediction_id, output_urls
    generation_failed = pyqtSignal(str, str)  # prediction_id, error_message
    generation_canceled = pyqtSignal(str)  # prediction_id
    
    def __init__(self, image_model: Optional[ImageGenerationModel] = None):
        super().__init__()
        self.image_model = image_model or ImageGenerationModel()
        self._init_components()
        self._connect_signals()
        self._active_predictions = set()  # Track active predictions
    
    def _init_components(self):
        """Initialize API components."""
        self.client = ReplicateClient()
        self.prediction_manager = PredictionManager(self.client)
        self.output_manager = OutputManager(
            Path.home() / '.replicate-desktop' / 'cache'
        )
    
    def _connect_signals(self):
        """Connect internal signals."""
        # Don't connect generation_started directly anymore
        self.prediction_manager.generation_progress.connect(self.generation_progress)
        self.prediction_manager.generation_completed.connect(self._handle_generation_completed)
        self.prediction_manager.generation_failed.connect(self._handle_generation_failed)
        self.prediction_manager.generation_canceled.connect(self._handle_generation_canceled)
    
    def list_available_models(self, collection: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available models, optionally filtered by collection."""
        return self.client.list_available_models(collection)
    
    def generate_images(self, model: str, params: Dict[str, Any]) -> str:
        """
        Start image generation and initialize tracking.
        Returns prediction ID only, signal will be emitted separately.
        """
        try:
            # First create prediction to get ID
            prediction_id = self.prediction_manager.start_prediction(model, params)
            logger.debug(f"Created prediction {prediction_id}")
            
            # Track the prediction
            self._active_predictions.add(prediction_id)
            
            return prediction_id

        except Exception as e:
            logger.error(f"Failed to start generation: {e}")
            raise
    
    def notify_generation_started(self, prediction_id: str):
        """
        Notify listeners that generation has started.
        Should be called after records are created.
        """
        if prediction_id in self._active_predictions:
            logger.debug(f"Notifying generation started: {prediction_id}")
            self.generation_started.emit(prediction_id)
    
    def save_generation_output(self, prediction_id: str, output_urls: List[str]) -> List[Path]:
        """Save generation outputs to local storage."""
        return self.output_manager.save_outputs(prediction_id, output_urls)
    
    def cancel_generation(self, prediction_id: str):
        """Cancel an ongoing generation."""
        try:
            if prediction_id in self._active_predictions:
                self.prediction_manager.cancel_prediction(prediction_id)
                self._active_predictions.remove(prediction_id)
                self.generation_canceled.emit(prediction_id)
        except Exception as e:
            logger.error(f"Failed to cancel generation {prediction_id}: {e}")
    
    def _handle_generation_completed(self, prediction_id: str, output_urls: List[str]):
        """Handle completed generation."""
        try:
            if prediction_id not in self._active_predictions:
                logger.warning(f"Received completion for unknown generation: {prediction_id}")
                return

            saved_paths = self.output_manager.save_outputs(prediction_id, output_urls)
            self.generation_completed.emit(prediction_id, saved_paths)
            self._active_predictions.remove(prediction_id)
            
        except Exception as e:
            logger.error(f"Failed to save generation outputs: {e}")
            self.generation_failed.emit(
                prediction_id,
                f"Generation completed but failed to save outputs: {str(e)}"
            )
    
    def _handle_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failure."""
        try:
            if prediction_id not in self._active_predictions:
                logger.warning(f"Received failure for unknown generation: {prediction_id}")
                return

            self.generation_failed.emit(prediction_id, error)
            self._active_predictions.remove(prediction_id)

        except Exception as e:
            logger.error(f"Error handling generation failure for {prediction_id}: {e}")
    
    def _handle_generation_canceled(self, prediction_id: str):
        """Handle generation cancellation."""
        try:
            if prediction_id not in self._active_predictions:
                logger.warning(f"Received cancellation for unknown generation: {prediction_id}")
                return

            self.generation_canceled.emit(prediction_id)
            self._active_predictions.remove(prediction_id)

        except Exception as e:
            logger.error(f"Error handling generation cancellation for {prediction_id}: {e}")