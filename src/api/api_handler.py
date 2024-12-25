"""Main API handler coordinating all API-related operations."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from .client import ReplicateClient
from .prediction_manager import PredictionManager
from .output_manager import OutputManager
from ..utils.debug_logger import logger

class APIHandler(QObject):
    """Coordinates API operations and manages state."""
    
    # Forward signals from PredictionManager
    generation_started = pyqtSignal(str)
    generation_progress = pyqtSignal(str, int)
    generation_completed = pyqtSignal(str, list)  # Now emits list of Path objects
    generation_failed = pyqtSignal(str, str)
    generation_canceled = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
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
        self.prediction_manager.generation_started.connect(self.generation_started)
        self.prediction_manager.generation_progress.connect(self.generation_progress)
        self.prediction_manager.generation_completed.connect(self._handle_generation_completed)
        self.prediction_manager.generation_failed.connect(self.generation_failed)
        self.prediction_manager.generation_canceled.connect(self.generation_canceled)
    
    def list_available_models(self, collection: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available models, optionally filtered by collection."""
        return self.client.list_available_models(collection)
    
    def generate_images(self, model: str, params: Dict[str, Any]) -> str:
        """
        Start image generation.
        Returns prediction ID.
        """
        return self.prediction_manager.start_prediction(model, params)
    
    def cancel_generation(self, prediction_id: str):
        """Cancel an ongoing generation."""
        self.prediction_manager.cancel_prediction(prediction_id)
    
    def _handle_generation_completed(self, prediction_id: str, output_urls: List[str]):
        """Handle completed generation by saving outputs."""
        try:
            saved_paths = self.save_generation_output(prediction_id, output_urls)
            # Now we emit the saved_paths directly
            self.generation_completed.emit(prediction_id, saved_paths)
        except Exception as e:
            logger.error(f"Failed to save generation outputs: {str(e)}")
            self.generation_failed.emit(
                prediction_id,
                f"Generation completed but failed to save outputs: {str(e)}"
            )
    
    def save_generation_output(self, prediction_id: str, output_urls: List[str]) -> List[Path]:
        """Save generation outputs to local cache."""
        return self.output_manager.save_outputs(prediction_id, output_urls)