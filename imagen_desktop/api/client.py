"""Replicate API client."""
from typing import Optional, List, Dict, Any
from .client_core import ReplicateClientCore
from .model_manager import ReplicateModelManager
from ..utils.debug_logger import logger

class ReplicateClient:
    """Client for interacting with Replicate API."""
    
    def __init__(self):
        self.core = ReplicateClientCore()
        self.model_manager = ReplicateModelManager(self.core)
    
    def list_available_models(self, collection: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available text-to-image models."""
        return self.model_manager.list_available_models()
    
    def get_model(self, model_identifier: str) -> dict:
        """Get information about a specific model."""
        return self.model_manager.get_model(model_identifier)
    
    def create_prediction(self, 
                         model_identifier: str, 
                         version_id: Optional[str] = None, 
                         **params) -> Any:
        """Create a new prediction."""
        return self.core.create_prediction(model_identifier, version_id, **params)
    
    def get_prediction(self, prediction_id: str) -> Any:
        """Get a prediction by ID."""
        return self.core.get_prediction(prediction_id)
    
    def cancel_prediction(self, prediction_id: str):
        """Cancel a prediction."""
        return self.core.cancel_prediction(prediction_id)