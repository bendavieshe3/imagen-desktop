"""Base client for Replicate API interactions."""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import replicate
from ..utils.debug_logger import logger

class ReplicateClient:
    """Base client for interacting with Replicate API."""
    
    # List of featured text-to-image models verified working and openly available
    # Focusing on Stability AI models which are known to be commercially usable
    FEATURED_MODELS = [
        "stability-ai/sdxl-turbo:d7985af5cdc8e7f9a5ea49fcb6074fccb0e35618f39778dd5476346db3c74285",  # Latest SDXL Turbo fast model
        "stability-ai/sdxl:a00d0b7dcbb9c3fbb34ba87d2d5b46c56969c84a628bf778a7fdaec30b1b99c5",      # Latest SDXL 1.0 high quality
    ]
    
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
            raise ValueError("No API key found. Please set REPLICATE_API_TOKEN environment variable.")
    
    def _init_client(self):
        """Initialize the Replicate client."""
        self.client = replicate.Client(api_token=self.api_key)
    
    def list_available_models(self, collection: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available text-to-image models."""
        try:
            models = []
            
            # Get featured models (with specific versions)
            for model_string in self.FEATURED_MODELS:
                try:
                    model_id, version = model_string.split(':')
                    owner, name = model_id.split('/')
                    model = replicate.models.get(model_id)
                    description = model.description or ""
                    
                    # Add speed indicator and usage info
                    if "turbo" in model_id.lower():
                        description = "🚀 Fast generation model. " + description
                    else:
                        description = "✨ High quality model. " + description
                        
                    models.append({
                        'name': model.name,
                        'owner': model.owner,
                        'description': description,
                        'identifier': model_id,
                        'version': version,
                        'featured': True
                    })
                except Exception as e:
                    logger.error(f"Error loading featured model {model_id}: {e}")
            
            return models
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return []
    
    def get_model(self, model_identifier: str) -> dict:
        """Get information about a specific model."""
        if '/' not in model_identifier:
            raise ValueError("Invalid model identifier")

        try:
            owner, model_name = model_identifier.split('/')
            model = replicate.models.get(owner + "/" + model_name)
            return {
                'name': model.name,
                'owner': model.owner,
                'description': model.description,
                'identifier': model_identifier,
                'latest_version': model.latest_version.id
            }
        except Exception as e:
            logger.error(f"Error getting model {model_identifier}: {str(e)}")
            raise
    
    def create_prediction(self, 
                         model_identifier: str, 
                         version_id: Optional[str] = None, 
                         **params) -> Any:
        """Create a new prediction."""
        try:
            model = replicate.models.get(model_identifier)
            version = version_id or model.latest_version
            
            prediction = replicate.predictions.create(
                version=version,
                input=params
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to create prediction: {str(e)}")
            raise
    
    def get_prediction(self, prediction_id: str) -> Any:
        """Get a prediction by ID."""
        try:
            return replicate.predictions.get(prediction_id)
        except Exception as e:
            logger.error(f"Failed to get prediction {prediction_id}: {str(e)}")
            raise
    
    def cancel_prediction(self, prediction_id: str):
        """Cancel a prediction."""
        try:
            prediction = self.get_prediction(prediction_id)
            prediction.cancel()
        except Exception as e:
            logger.error(f"Failed to cancel prediction {prediction_id}: {str(e)}")
            raise