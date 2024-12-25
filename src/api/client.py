"""Base client for Replicate API interactions."""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import replicate
from ..utils.debug_logger import logger

class ReplicateClient:
    """Base client for interacting with Replicate API."""
    
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
        """List available models, optionally filtered by collection."""
        models = []
        
        try:
            if collection:
                collection_data = replicate.collections.get(collection)
                for model in collection_data.models:
                    models.append({
                        'name': model.name,
                        'owner': model.owner,
                        'description': model.description,
                        'identifier': f"{model.owner}/{model.name}"
                    })
            else:
                for page in replicate.paginate(replicate.models.list):
                    for model in page:
                        models.append({
                            'name': model.name,
                            'owner': model.owner,
                            'description': model.description,
                            'identifier': f"{model.owner}/{model.name}"
                        })
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
        
        return models
    
    def get_model(self, model_identifier: str) -> dict:
        """Get information about a specific model."""
        if '/' not in model_identifier:
            raise ValueError("Invalid model identifier")

        owner, model_name = model_identifier.split('/')
        try:
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
                         **params) -> Any:  # Return type changed to Any
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
    
    def get_prediction(self, prediction_id: str) -> Any:  # Return type changed to Any
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