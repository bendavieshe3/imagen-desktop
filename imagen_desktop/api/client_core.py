"""Core Replicate API client functionality."""
import os
import json
from pathlib import Path
import replicate
from typing import Any, Dict, Optional
from ..utils.debug_logger import logger

class ReplicateClientCore:
    """Core client functionality for Replicate API."""
    
    def __init__(self):
        self._load_api_key()
        self._init_client()
    
    def _load_api_key(self):
        """Load API key from environment or config file."""
        self.api_key = os.getenv('REPLICATE_API_TOKEN')
        if not self.api_key:
            config_path = Path.home() / '.replicate-desktop' / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
        
        if not self.api_key:
            logger.error("No API key found")
            raise ValueError("No API key found. Please set REPLICATE_API_TOKEN environment variable.")
    
    def _init_client(self):
        """Initialize the Replicate client."""
        try:
            self.client = replicate.Client(api_token=self.api_key)
            logger.info("Replicate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {e}")
            raise
    
    def create_prediction(self, 
                         model_identifier: str, 
                         version_id: Optional[str] = None, 
                         **params) -> Any:
        """Create a new prediction."""
        try:
            logger.debug(f"Creating prediction for model {model_identifier}")
            model = replicate.models.get(model_identifier)
            version = version_id or model.latest_version
            
            prediction = replicate.predictions.create(
                version=version,
                input=params
            )
            
            logger.info(f"Created prediction {prediction.id} for model {model_identifier}")
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to create prediction: {e}")
            raise
    
    def get_prediction(self, prediction_id: str) -> Any:
        """Get a prediction by ID."""
        try:
            return replicate.predictions.get(prediction_id)
        except Exception as e:
            logger.error(f"Failed to get prediction {prediction_id}: {e}")
            raise
    
    def cancel_prediction(self, prediction_id: str):
        """Cancel a prediction."""
        try:
            prediction = self.get_prediction(prediction_id)
            prediction.cancel()
            logger.info(f"Cancelled prediction {prediction_id}")
        except Exception as e:
            logger.error(f"Failed to cancel prediction {prediction_id}: {e}")
            raise