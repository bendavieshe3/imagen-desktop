"""Model selection component with search and filtering."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QComboBox, QLabel, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional, List, Dict
import json
from pathlib import Path

from ...api.api_handler import APIHandler
from ...data.model_repository import ModelRepository
from ..dialogs.model_manager import ModelManager
from ...utils.debug_logger import logger

class ModelSelector(QWidget):
    model_changed = pyqtSignal(str, str)  # Emits (model_id, version_id)
    
    def __init__(self, api_handler: APIHandler, model_repository: Optional[ModelRepository] = None):
        super().__init__()
        self.api_handler = api_handler
        self.model_repository = model_repository
        self.current_models = []  # Track current model list
        self._init_ui()
        self._load_models()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Model dropdown
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        layout.addWidget(self.model_combo)
        
        # Model description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: gray;")
        layout.addWidget(self.description_label)
    
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
    
    def _load_models(self):
        """Load models from cache or defaults."""
        models = []
        
        # Try to load from database first
        if self.model_repository:
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
                logger.debug(f"Loaded {len(models)} models from cache")
            except Exception as e:
                logger.error(f"Error loading cached models: {e}")
        
        # If no cached models, load defaults
        if not models:
            models = self._load_default_models()
            logger.debug(f"Loaded {len(models)} default models")
        
        # Update the model list
        self._populate_model_list(models)
    
    def _populate_model_list(self, models: List[Dict]):
        """Populate the combo box with models."""
        # Store current selection
        current_id = self.get_selected_model()
        
        # Update current models list
        self.current_models = models if isinstance(models, list) else []
        
        self.model_combo.clear()
        
        # Sort models: featured first, then alphabetically
        sorted_models = sorted(self.current_models, 
                             key=lambda x: (not x.get('featured', False), x['name'].lower()))
        
        for model in sorted_models:
            # Create display name
            if model.get('featured'):
                display_name = f"⭐ {model['name']}"
            else:
                display_name = model['name']
                
            # Add owner in display name
            display_name += f" ({model['owner']})"
            
            # Store full model data in combo box
            self.model_combo.addItem(display_name, model)
            
            # Store description separately for UI
            index = self.model_combo.count() - 1
            self.model_combo.setItemData(
                index,
                model['description'],
                Qt.ItemDataRole.UserRole + 1
            )
        
        # Enable combo box if we have models
        self.model_combo.setEnabled(bool(self.current_models))
        
        # Restore previous selection if possible
        if current_id:
            for i in range(self.model_combo.count()):
                model_data = self.model_combo.itemData(i, Qt.ItemDataRole.UserRole)
                if model_data and model_data['identifier'] == current_id:
                    self.model_combo.setCurrentIndex(i)
                    break
    
    def _on_model_changed(self, index):
        """Handle model selection change."""
        if index >= 0:
            model_data = self.model_combo.itemData(index, Qt.ItemDataRole.UserRole)
            if model_data:
                self.model_changed.emit(
                    model_data['identifier'],
                    model_data.get('version', '')
                )
                
                # Update description
                description = model_data.get('description', '')
                self.description_label.setText(description)
    
    def _show_model_manager(self):
        """Show the model manager dialog."""
        if not self.model_repository:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Not Available",
                "Model management requires database support which is not available."
            )
            return
            
        dialog = ModelManager(self.api_handler, self.model_repository, self)
        dialog.models_updated.connect(self._load_models)  # Reload when cache changes
        dialog.exec()
    
    def get_selected_model(self) -> Optional[str]:
        """Get the currently selected model identifier."""
        index = self.model_combo.currentIndex()
        if index >= 0:
            model_data = self.model_combo.itemData(index, Qt.ItemDataRole.UserRole)
            return model_data['identifier'] if model_data else None
        return None
    
    def get_selected_version(self) -> Optional[str]:
        """Get the version ID of the selected model."""
        index = self.model_combo.currentIndex()
        if index >= 0:
            model_data = self.model_combo.itemData(index, Qt.ItemDataRole.UserRole)
            return model_data.get('version') if model_data else None
        return None
    
    def setEnabled(self, enabled: bool):
        """Enable or disable the component."""
        super().setEnabled(enabled)
        self.model_combo.setEnabled(enabled)