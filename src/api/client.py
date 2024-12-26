"""Base client for Replicate API interactions."""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import replicate
from ..utils.debug_logger import logger

class ReplicateClient:
    """Base client for interacting with Replicate API."""
    
    # List of featured text-to-image models (verified Dec 2024)
    FEATURED_MODELS = [
        # Fast Generation Models
        f"bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
        f"luma/photon-flash:81b0e3ad4acf49cb47143ea63cce47f94cb0bdbecc13d31910654b6282e29ea1",
        f"lucataco/ssd-1b:b19e3639452c59ce8295b82aba70a231404cb062f2eb580ea894b31e8ce5bbb6",
        
        # High Quality Models
        f"stability-ai/stable-diffusion-3.5-large:e6c4657fe1b3f078fb26d68a1413bc8013e2b085504dd84a33e26e16fb95a593",
        f"luma/photon:fe142c037cf359764f2058c3a42ef0dc750d908311d02868cbc7769fe800b648",
        f"black-forest-labs/flux-pro:a57823497a8beebcd222c20dd78af15a90c0415c36a5bfc88ee763c67155310e",
        
        # Specialized Models
        f"ideogram-ai/ideogram-v2:d07f7f3ad03f2ec100edeaa91e26ac731d7d00ec369e6a475b80c04bd1101d5d",  # Good text rendering
        f"playgroundai/playground-v2.5-1024px-aesthetic:a45f82a1382bed5c7aeb861dac7c7d191b0fdf74d8d57c4a0e6ed7d4d0bf7d24"  # Aesthetic focused
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
            failed_models = []
            
            # Get featured models (with specific versions)
            for model_string in self.FEATURED_MODELS:
                try:
                    model_id, version = model_string.split(':')
                    owner, name = model_id.split('/')
                    model = replicate.models.get(model_id)
                    
                    # Determine model category for description
                    prefix = ""
                    if any(x in model_id.lower() for x in ['flash', 'lightning', 'turbo', 'ssd']):
                        prefix = "🚀 Fast generation model. "
                    elif any(x in model_id.lower() for x in ['pro', 'large', 'photon']):
                        prefix = "✨ High quality model. "
                    elif 'ideogram' in model_id.lower():
                        prefix = "📝 Excellent text rendering. "
                    elif 'aesthetic' in model_id.lower():
                        prefix = "🎨 Aesthetic focused. "
                    
                    description = prefix + (model.description or "")
                    
                    models.append({
                        'name': model.name,
                        'owner': model.owner,
                        'description': description,
                        'identifier': model_id,
                        'version': version,
                        'featured': True
                    })
                except Exception as e:
                    failed_models.append(model_id)
                    logger.error(f"Error loading featured model {model_id}: {e}")
            
            if failed_models:
                logger.warning(f"Failed to load models: {', '.join(failed_models)}")
            
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