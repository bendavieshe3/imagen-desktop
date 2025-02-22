"""Core Replicate API client functionality."""
import os
import json
from pathlib import Path
import replicate
from typing import Any, Dict, Optional
from PyQt6.QtWidgets import QMessageBox
from ..utils.debug_logger import logger

class APIKeyError(Exception):
    """Exception raised for missing or invalid API key."""
    pass

class ReplicateClientCore:
    """Core client functionality for Replicate API."""
    
    def __init__(self, show_ui_errors: bool = True):
        """Initialize the core client.
        
        Args:
            show_ui_errors: Whether to show error dialogs to user
        """
        self.show_ui_errors = show_ui_errors
        self.api_key = None
        self.client = None
        
        try:
            self._load_api_key()
            self._init_client()
        except APIKeyError as e:
            self._handle_startup_error(str(e))
            raise
        except Exception as e:
            self._handle_startup_error(f"Failed to initialize client: {str(e)}")
            raise
    
    def _load_api_key(self):
        """Load API key from environment or config file."""
        # Try environment variable first
        self.api_key = os.getenv('REPLICATE_API_TOKEN')
        
        # Try config file if no environment variable
        if not self.api_key:
            config_path = Path.home() / '.imagen-desktop' / 'config.json'
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        self.api_key = config.get('api_key')
                        # Set environment variable for Replicate client
                        if self.api_key:
                            os.environ['REPLICATE_API_TOKEN'] = self.api_key
                except Exception as e:
                    logger.error(f"Failed to read config file: {e}")
        
        if not self.api_key:
            raise APIKeyError(
                "No API key found. Please set the REPLICATE_API_TOKEN environment variable "
                "or add it to ~/.imagen-desktop/config.json"
            )
    
    def _init_client(self):
        """Initialize the Replicate client."""
        try:
            # Initialize with explicit API token
            self.client = replicate.Client(api_token=self.api_key)
            # Test the client
            self.client.models.get("stability-ai/sdxl")
            logger.info("Replicate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {e}")
            raise
    
    def _handle_startup_error(self, message: str):
        """Handle startup errors appropriately."""
        logger.error(message)
        if self.show_ui_errors:
            QMessageBox.critical(
                None,
                "Initialization Error",
                f"{message}\n\nThe application cannot start without a valid API key."
            )
    
    def create_prediction(self, 
                         model_identifier: str, 
                         version_id: Optional[str] = None, 
                         **params) -> Any:
        """Create a new prediction."""
        if not self.client:
            raise APIKeyError("Client not initialized - API key required")
            
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
        if not self.client:
            raise APIKeyError("Client not initialized - API key required")
            
        try:
            return replicate.predictions.get(prediction_id)
        except Exception as e:
            logger.error(f"Failed to get prediction {prediction_id}: {e}")
            raise
    
    def cancel_prediction(self, prediction_id: str):
        """Cancel a prediction."""
        if not self.client:
            raise APIKeyError("Client not initialized - API key required")
            
        try:
            prediction = self.get_prediction(prediction_id)
            prediction.cancel()
            logger.info(f"Cancelled prediction {prediction_id}")
        except Exception as e:
            logger.error(f"Failed to cancel prediction {prediction_id}: {e}")
            raise