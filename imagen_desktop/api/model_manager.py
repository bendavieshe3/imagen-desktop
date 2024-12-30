"""Model management functionality for Replicate API."""
from typing import List, Dict, Any
import replicate
from .client_core import ReplicateClientCore
from ..utils.debug_logger import logger

class ReplicateModelManager:
    """Handles Replicate model management operations."""
    
    # List of featured text-to-image models (verified Dec 2024)
    FEATURED_MODELS = [
        # Fast Generation Models
        "bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
        "luma/photon-flash:81b0e3ad4acf49cb47143ea63cce47f94cb0bdbecc13d31910654b6282e29ea1",
        "lucataco/ssd-1b:b19e3639452c59ce8295b82aba70a231404cb062f2eb580ea894b31e8ce5bbb6",
        
        # High Quality Models
        "stability-ai/stable-diffusion-3.5-large:e6c4657fe1b3f078fb26d68a1413bc8013e2b085504dd84a33e26e16fb95a593",
        "luma/photon:fe142c037cf359764f2058c3a42ef0dc750d908311d02868cbc7769fe800b648",
        "black-forest-labs/flux-pro:a57823497a8beebcd222c20dd78af15a90c0415c36a5bfc88ee763c67155310e"
    ]
    
    def __init__(self, client: ReplicateClientCore):
        self.client = client
    
    def _categorize_model(self, model_id: str) -> str:
        """Determine model category for description."""
        prefix = ""
        if any(x in model_id.lower() for x in ['flash', 'lightning', 'turbo', 'ssd']):
            prefix = "🚀 Fast generation model. "
        elif any(x in model_id.lower() for x in ['pro', 'large', 'photon']):
            prefix = "✨ High quality model. "
        elif 'ideogram' in model_id.lower():
            prefix = "📝 Excellent text rendering. "
        elif 'aesthetic' in model_id.lower():
            prefix = "🎨 Aesthetic focused. "
        return prefix
    
    def list_available_models(self) -> List[Dict[str, Any]]:
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
                    
                    description = self._categorize_model(model_id) + (model.description or "")
                    
                    models.append({
                        'name': name,
                        'owner': owner,
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
            
            logger.info(f"Successfully loaded {len(models)} models")
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