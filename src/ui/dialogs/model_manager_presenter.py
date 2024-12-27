"""Presenter for model manager dialog."""
import replicate
from typing import List, Dict, Any, Set, Optional
from pathlib import Path
import json
from PyQt6.QtCore import QObject, pyqtSignal

from ...api.api_handler import APIHandler
from ...data.repositories.model_repository import ModelRepository
from ...utils.debug_logger import logger

class ModelLoaderThread(QObject):
    """Background thread for loading models."""
    models_loaded = pyqtSignal(list)  # Emits list of model data
    error_occurred = pyqtSignal(str)  # Emits error message
    
    def __init__(self):
        super().__init__()
    
    def load_models(self):
        """Load available models from Replicate."""
        try:
            collection = replicate.collections.get("text-to-image")
            models = []
            
            for model in collection.models:
                models.append({
                    'name': model.name,
                    'owner': model.owner,
                    'identifier': f"{model.owner}/{model.name}",
                    'description': model.description,
                    'version': model.latest_version.id if model.latest_version else None,
                    'featured': False
                })
            
            self.models_loaded.emit(models)
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.error_occurred.emit(str(e))

class ModelManagerPresenter:
    """Handles model management business logic."""
    
    def __init__(self, api_handler: APIHandler, model_repository: ModelRepository):
        self.api_handler = api_handler
        self.model_repository = model_repository
        self.installed_models: Set[str] = set()
        self.current_models: List[Dict] = []
        self.loader_thread = ModelLoaderThread()
        
        self._load_installed_models()
    
    def _load_installed_models(self):
        """Load the list of installed models."""
        try:
            models = self.model_repository.list_models()
            self.installed_models = {model.identifier for model in models}
            logger.info(f"Loaded {len(self.installed_models)} installed models")
        except Exception as e:
            logger.error(f"Error loading installed models: {e}")
            raise
    
    def _load_default_models(self) -> List[Dict]:
        """Load the default models list from JSON."""
        try:
            paths = [
                Path(__file__).parent.parent.parent.parent / 'resources' / 'models' / 'default_models.json',
                Path.home() / '.replicate-desktop' / 'default_models.json'
            ]
            
            for path in paths:
                if path.exists():
                    with open(path, 'r') as f:
                        data = json.load(f)
                        logger.debug(f"Loaded default models from {path}")
                        return data.get('models', [])
            
            logger.warning("No default models file found")
            return []
            
        except Exception as e:
            logger.error(f"Error loading default models: {e}")
            return []
    
    def load_models(self) -> List[Dict]:
        """Load and return available models."""
        models = []
        
        try:
            cached_models = self.model_repository.list_models()
            for model in cached_models:
                metadata = model.model_metadata or {}
                models.append({
                    'name': model.name,
                    'owner': model.owner,
                    'description': model.description,
                    'identifier': model.identifier,
                    'version': metadata.get('version', ''),
                    'featured': metadata.get('featured', False)
                })
            logger.debug(f"Loaded {len(models)} cached models")
        except Exception as e:
            logger.error(f"Error loading cached models: {e}")
        
        if not models:
            models = self._load_default_models()
        
        self.current_models = models
        return sorted(models, key=lambda x: (not x.get('featured', False), x['name'].lower()))
    
    def add_model(self, model_data: Dict[str, Any]) -> bool:
        """Add a model to the repository."""
        try:
            self.model_repository.add_or_update_model(
                identifier=model_data['identifier'],
                name=model_data['name'],
                owner=model_data['owner'],
                description=model_data.get('description'),
                metadata={
                    'version': model_data.get('version'),
                    'featured': model_data.get('featured', False)
                }
            )
            self.installed_models.add(model_data['identifier'])
            logger.info(f"Added model {model_data['identifier']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding model: {e}")
            raise
    
    def remove_model(self, model_id: str) -> bool:
        """Remove a model from the repository."""
        try:
            if self.model_repository.delete_by_identifier(model_id):
                self.installed_models.remove(model_id)
                logger.info(f"Removed model {model_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing model: {e}")
            raise
    
    def is_installed(self, model_id: str) -> bool:
        """Check if a model is installed."""
        return model_id in self.installed_models