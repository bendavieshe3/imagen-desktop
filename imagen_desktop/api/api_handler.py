"""Main API handler coordinating all API-related operations."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from .client import ReplicateClient
from .prediction_manager import PredictionManager
from ..core.models.image_generation import ImageGenerationModel
from ..utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class APIHandler(QObject):
    """Coordinates API operations and manages state."""
    
    # Generation signals
    generation_started = pyqtSignal(str)  # prediction_id
    generation_completed = pyqtSignal(str, list)  # prediction_id, raw_outputs
    generation_failed = pyqtSignal(str, str)  # prediction_id, error_message
    generation_canceled = pyqtSignal(str)  # prediction_id
    
    def __init__(self, image_model: Optional[ImageGenerationModel] = None):
        super().__init__()
        self.image_model = image_model or ImageGenerationModel()
        self._init_components()
        self._connect_signals()
        self._active_predictions = set()
    
    def _init_components(self):
        """Initialize API components."""
        self.client = ReplicateClient()
        self.prediction_manager = PredictionManager(self.client)
    
    def _connect_signals(self):
        """Connect internal signals."""
        logger.debug("Connecting APIHandler signals")
        self.prediction_manager.generation_completed.connect(self._handle_generation_completed)
        self.prediction_manager.generation_failed.connect(self._handle_generation_failed)
        self.prediction_manager.generation_canceled.connect(self._handle_generation_canceled)
    
    def generate_images(self, model: str, params: Dict[str, Any]) -> str:
        """Start image generation and return prediction ID."""
        try:
            prediction_id = self.prediction_manager.start_prediction(model, params)
            logger.info(f"Created prediction {prediction_id} for model {model}")
            self._active_predictions.add(prediction_id)
            return prediction_id
        except Exception as e:
            logger.error("Failed to start generation", extra={'context': {'error': str(e)}})
            raise
    
    def notify_generation_started(self, prediction_id: str):
        """Notify listeners that generation has started."""
        if prediction_id in self._active_predictions:
            logger.debug(f"Notifying generation started: {prediction_id}")
            self.generation_started.emit(prediction_id)
    
    def _handle_generation_completed(self, prediction_id: str, raw_outputs: list):
        """Handle completed generation and emit raw outputs."""
        if prediction_id not in self._active_predictions:
            logger.warning(f"Received completion for unknown generation: {prediction_id}")
            return

        logger.info(
            "Generation completed successfully",
            extra={
                'context': {
                    'prediction_id': prediction_id,
                    'output_count': len(raw_outputs)
                }
            }
        )
        
        # Emit raw outputs for processing by appropriate handlers
        self.generation_completed.emit(prediction_id, raw_outputs)
        self._active_predictions.remove(prediction_id)
    
    def _handle_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failure."""
        if prediction_id in self._active_predictions:
            logger.error(
                "Generation failed",
                extra={
                    'context': {
                        'prediction_id': prediction_id,
                        'error': error
                    }
                }
            )
            self.generation_failed.emit(prediction_id, error)
            self._active_predictions.remove(prediction_id)
    
    def _handle_generation_canceled(self, prediction_id: str):
        """Handle generation cancellation."""
        if prediction_id in self._active_predictions:
            logger.info(f"Generation canceled: {prediction_id}")
            self.generation_canceled.emit(prediction_id)
            self._active_predictions.remove(prediction_id)
    
    def cancel_generation(self, prediction_id: str):
        """Cancel an ongoing generation."""
        try:
            if prediction_id in self._active_predictions:
                self.prediction_manager.cancel_prediction(prediction_id)
        except Exception as e:
            logger.error(f"Failed to cancel generation {prediction_id}: {e}")