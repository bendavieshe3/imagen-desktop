"""Model selection component with search and filtering."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, 
    QComboBox, QLabel, QGroupBox,
    QLineEdit
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from typing import Optional, List, Dict

from ...api.api_handler import APIHandler
from ...data.model_repository import ModelRepository
from ...utils.debug_logger import logger

class ModelLoaderThread(QThread):
    """Background thread for loading models."""
    models_loaded = pyqtSignal(list)  # Emits list of model data
    
    def __init__(self, api_handler: APIHandler, model_repository: Optional[ModelRepository] = None):
        super().__init__()
        self.api_handler = api_handler
        self.model_repository = model_repository
    
    def run(self):
        try:
            models = []
            
            if self.model_repository:
                # Use database if available - only fetch cached models
                cached_models = self.model_repository.list_models()
                models.extend([{
                    'id': model.identifier,
                    'name': model.name,
                    'description': model.description,
                    'owner': model.owner,
                    'version': model.model_metadata.get('version'),
                    'featured': True
                } for model in cached_models])
            
            # Always fetch featured models from API
            api_models = self.api_handler.list_available_models()
            
            # Only add API models that aren't already in the list
            existing_ids = {m['id'] for m in models}
            for model in api_models:
                if model['identifier'] not in existing_ids:
                    models.append({
                        'id': model['identifier'],
                        'name': model['name'],
                        'description': model['description'],
                        'owner': model['owner'],
                        'version': model.get('version'),
                        'featured': model.get('featured', False)
                    })
            
            self.models_loaded.emit(models)
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.models_loaded.emit([])

class ModelSelector(QWidget):
    model_changed = pyqtSignal(str, str)  # Emits (model_id, version_id)
    
    def __init__(self, api_handler: APIHandler, model_repository: Optional[ModelRepository] = None):
        super().__init__()
        self.api_handler = api_handler
        self.model_repository = model_repository
        
        # Initialize loader thread
        self.loader_thread = ModelLoaderThread(api_handler, model_repository)
        self.loader_thread.models_loaded.connect(self._on_models_loaded)
        
        self._init_ui()
        self._start_loading()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Model Selection")
        main_layout = QVBoxLayout()
        
        # Model selection
        form_layout = QFormLayout()
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        
        # Add loading placeholder
        self.model_combo.addItem("Loading models...")
        self.model_combo.setEnabled(False)
        
        form_layout.addRow("Model:", self.model_combo)
        
        # Model description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: gray;")
        form_layout.addRow(self.description_label)
        
        main_layout.addLayout(form_layout)
        
        group.setLayout(main_layout)
        layout.addWidget(group)
    
    def _start_loading(self):
        """Start loading models in background thread."""
        if not self.loader_thread.isRunning():
            self.model_combo.setEnabled(False)
            self.model_combo.clear()
            self.model_combo.addItem("Loading models...")
            self.description_label.clear()
            self.loader_thread.start()
    
    def _on_models_loaded(self, models: List[Dict]):
        """Handle loaded model data."""
        current_id = self.get_selected_model()
        
        self.model_combo.clear()
        
        # Sort models: featured first, then alphabetically
        sorted_models = sorted(models, 
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
        self.model_combo.setEnabled(bool(models))
        
        if not models:
            self.model_combo.addItem("No models available")
            self.model_combo.setEnabled(False)
            self.description_label.setText("Failed to load models. Please try again later.")
        
        # Restore previous selection if possible
        if current_id:
            for i in range(self.model_combo.count()):
                model_data = self.model_combo.itemData(i, Qt.ItemDataRole.UserRole)
                if model_data and model_data['id'] == current_id:
                    self.model_combo.setCurrentIndex(i)
                    break
    
    def _on_model_changed(self, index):
        """Handle model selection change."""
        if index >= 0:
            model_data = self.model_combo.itemData(index, Qt.ItemDataRole.UserRole)
            if model_data:
                self.model_changed.emit(
                    model_data['id'],
                    model_data.get('version', '')
                )
                
                # Update description
                description = model_data.get('description', '')
                if model_data.get('featured'):
                    description = "⭐ Featured Model\n\n" + description
                self.description_label.setText(description)
    
    def get_selected_model(self) -> Optional[str]:
        """Get the currently selected model identifier."""
        index = self.model_combo.currentIndex()
        if index >= 0:
            model_data = self.model_combo.itemData(index, Qt.ItemDataRole.UserRole)
            return model_data['id'] if model_data else None
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
        # Don't enable combo if we're still loading or have no models
        combo_enabled = enabled and not self.loader_thread.isRunning()
        self.model_combo.setEnabled(combo_enabled)