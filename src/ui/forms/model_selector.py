"""Model selection component with search and filtering."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QComboBox, QLabel, QGroupBox,
    QLineEdit
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from typing import Optional, List, Dict
import json

from ...api.api_handler import APIHandler
from ...data.model_repository import ModelRepository
from ...utils.debug_logger import logger

# Default models that load instantly
INITIAL_MODELS = [
    {
        'name': 'SDXL Lightning (Fast)',
        'owner': 'bytedance',
        'description': '🚀 Fast generation model. SDXL-Lightning: a fast text-to-image model that makes high-quality images in 4 steps',
        'identifier': 'bytedance/sdxl-lightning-4step',
        'version': '5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637',
        'featured': True
    },
    {
        'name': 'SD 3.5 Large (Quality)',
        'owner': 'stability-ai',
        'description': '✨ High quality model. A text-to-image model that generates high-resolution images with fine details.',
        'identifier': 'stability-ai/stable-diffusion-3.5-large',
        'version': 'e6c4657fe1b3f078fb26d68a1413bc8013e2b085504dd84a33e26e16fb95a593',
        'featured': True
    }
]

class ModelLoaderThread(QThread):
    """Background thread for loading models."""
    models_loaded = pyqtSignal(list)  # Emits list of model data
    
    def __init__(self, api_handler: APIHandler, model_repository: Optional[ModelRepository] = None):
        super().__init__()
        self.api_handler = api_handler
        self.model_repository = model_repository
    
    def run(self):
        try:
            # Get API models
            models = self.api_handler.list_available_models()
            
            # Filter out any models already in initial list
            initial_ids = {m['identifier'] for m in INITIAL_MODELS}
            models = [m for m in models if m['identifier'] not in initial_ids]
            
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
        self.current_models = []  # Track current model list
        
        # Initialize loader thread
        self.loader_thread = ModelLoaderThread(api_handler, model_repository)
        self.loader_thread.models_loaded.connect(self._on_models_loaded)
        
        self._init_ui()
        self._populate_model_list(INITIAL_MODELS)  # Load initial models immediately
        self._start_background_loading()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Model Selection")
        main_layout = QVBoxLayout()
        
        # Model selection
        form_layout = QFormLayout()
        
        combo_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        combo_layout.addWidget(self.model_combo)
        
        # Small refresh indicator
        self.refresh_label = QLabel("Loading more models...")
        self.refresh_label.setVisible(False)
        combo_layout.addWidget(self.refresh_label)
        
        form_layout.addRow("Model:", combo_layout)
        
        # Model description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: gray;")
        form_layout.addRow(self.description_label)
        
        main_layout.addLayout(form_layout)
        
        group.setLayout(main_layout)
        layout.addWidget(group)
    
    def _start_background_loading(self):
        """Start loading full model list in background."""
        self.refresh_label.setVisible(True)
        if not self.loader_thread.isRunning():
            self.loader_thread.start()
    
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
    
    def _on_models_loaded(self, new_models: List[Dict]):
        """Handle loaded model data."""
        self.refresh_label.setVisible(False)
        
        if new_models:  # Only update if we got new models
            # Combine initial and new models
            all_models = INITIAL_MODELS + new_models
            self._populate_model_list(all_models)
    
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