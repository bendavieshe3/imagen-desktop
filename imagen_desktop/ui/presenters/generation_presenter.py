"""Presenter for handling image generation lifecycle."""
from typing import Dict, Optional
from pathlib import Path

from imagen_desktop.core.models.image_generation import GenerationStatus
from imagen_desktop.data.repositories.product_repository import ProductRepository
from imagen_desktop.api.api_handler import APIHandler
from imagen_desktop.utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class GenerationPresenter:
    """Handles image generation lifecycle and coordinates with storage."""
    
    def __init__(self,
                 api_handler: APIHandler,
                 product_repository: Optional[ProductRepository] = None,
                 view=None):
        """Initialize the presenter.
        
        Args:
            api_handler: Handler for API interactions
            product_repository: Repository for product storage
            view: Optional view for UI updates
        """
        self.api_handler = api_handler
        self.product_repository = product_repository
        self.view = view
        
        # Track current generations
        self.active_generations = set()
    
    def start_generation(self, model: str, params: dict) -> str:
        """Start a new image generation.
        
        Args:
            model: Model identifier
            params: Generation parameters
            
        Returns:
            Prediction ID string
            
        Raises:
            Exception if generation fails to start
        """
        try:
            # Get prediction ID from API
            prediction_id = self.api_handler.generate_images(model, params)
            logger.info(
                "Created prediction",
                extra={
                    'context': {
                        'prediction_id': prediction_id,
                        'model': model
                    }
                }
            )
            
            # Track active generation
            self.active_generations.add(prediction_id)
            
            # Notify that generation has started
            self.api_handler.notify_generation_started(prediction_id)
            
            if self.view:
                self.view.show_status(f"Generation started: {prediction_id}")
            
            return prediction_id
            
        except Exception as e:
            logger.error(
                "Failed to start generation",
                extra={'context': {'error': str(e)}}
            )
            raise
    
    def cleanup_generation(self, prediction_id: str):
        """Clean up a completed generation.
        
        Args:
            prediction_id: ID of generation to clean up
        """
        if prediction_id in self.active_generations:
            self.active_generations.remove(prediction_id)
            logger.debug(
                "Cleaned up generation",
                extra={'context': {'prediction_id': prediction_id}}
            )