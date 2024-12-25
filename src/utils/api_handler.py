import os
import json
import time
import threading
import replicate
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from PyQt6.QtCore import QObject, pyqtSignal

class APIHandler(QObject):
    """Handles interactions with the Replicate API."""
    
    # Signals for async operations
    generation_started = pyqtSignal(str)  # prediction_id
    generation_progress = pyqtSignal(str, int)  # prediction_id, progress
    generation_completed = pyqtSignal(str, list)  # prediction_id, output_urls
    generation_failed = pyqtSignal(str, str)  # prediction_id, error_message
    generation_canceled = pyqtSignal(str)  # prediction_id
    
    def __init__(self):
        super().__init__()
        self._load_api_key()
        self._init_client()
        self._cache_dir = Path.home() / '.replicate-desktop' / 'cache'
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._active_predictions = {}  # Store active prediction threads
    
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
    
    def _normalize_output(self, output: Any) -> List[str]:
        """Normalize prediction output to a list of URLs."""
        if output is None:
            return []
        elif isinstance(output, str):
            return [output]
        elif isinstance(output, list):
            return output
        else:
            return [str(output)]
    
    def _poll_prediction(self, prediction_id: str):
        """Poll prediction status until completion."""
        try:
            while prediction_id in self._active_predictions:
                try:
                    prediction = replicate.predictions.get(prediction_id)
                    
                    if prediction.status == 'succeeded':
                        if prediction.output is not None:
                            normalized_output = self._normalize_output(prediction.output)
                            self.generation_completed.emit(prediction_id, normalized_output)
                        break
                    elif prediction.status == 'failed':
                        self.generation_failed.emit(prediction_id, prediction.error or "Unknown error")
                        break
                    elif prediction.status == 'canceled':
                        self.generation_canceled.emit(prediction_id)
                        break
                    
                    # Wait before next poll
                    time.sleep(1)
                    
                except Exception as e:
                    self.generation_failed.emit(prediction_id, str(e))
                    break
        finally:
            # Always clean up
            if prediction_id in self._active_predictions:
                del self._active_predictions[prediction_id]
    
    def generate_images(self, model_identifier: str, params: Dict[str, Any]) -> str:
        """
        Start an image generation prediction.
        Returns the prediction ID.
        """
        try:
            if '/' not in model_identifier:
                raise ValueError("Invalid model identifier")
            
            owner, model_name = model_identifier.split('/')
            model = replicate.models.get(owner + "/" + model_name)
            prediction = replicate.predictions.create(
                version=model.latest_version,
                input=params
            )
            
            # Store thread for cancellation
            thread = threading.Thread(
                target=self._poll_prediction,
                args=(prediction.id,),
                daemon=True
            )
            self._active_predictions[prediction.id] = {
                'thread': thread,
                'prediction': prediction
            }
            
            # Start polling
            thread.start()
            self.generation_started.emit(prediction.id)
            
            return prediction.id
            
        except Exception as e:
            error_msg = f"Failed to start generation: {str(e)}"
            self.generation_failed.emit("", error_msg)
            raise
    
    def cancel_generation(self, prediction_id: str):
        """Cancel an active generation."""
        if prediction_id in self._active_predictions:
            try:
                # Cancel the prediction with Replicate
                prediction = self._active_predictions[prediction_id]['prediction']
                prediction.cancel()
                
                # Clean up thread
                del self._active_predictions[prediction_id]
                self.generation_canceled.emit(prediction_id)
                
            except Exception as e:
                error_msg = f"Failed to cancel generation: {str(e)}"
                self.generation_failed.emit(prediction_id, error_msg)
    
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
            print(f"Error loading models: {str(e)}")
            raise
        
        return models
    
    def save_generation_output(self, prediction_id: str, output_urls: List[str]) -> List[Path]:
        """Save generation outputs to local cache."""
        prediction_dir = self._cache_dir / prediction_id
        prediction_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        for i, url in enumerate(output_urls):
            file_path = prediction_dir / f"output_{i}.png"
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                saved_paths.append(file_path)
            except Exception as e:
                print(f"Failed to download image {i}: {str(e)}")
                continue
        
        return saved_paths