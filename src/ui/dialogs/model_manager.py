"""Dialog for browsing and managing available models."""
import replicate
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QLabel, QProgressBar,
    QMessageBox, QLineEdit, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from typing import List, Dict, Any, Set
import json
from pathlib import Path

from ...api.api_handler import APIHandler
from ...data.model_repository import ModelRepository
from ...utils.debug_logger import logger

class ModelLoaderThread(QThread):
    """Background thread for loading models."""
    models_loaded = pyqtSignal(list)  # Emits list of model data
    error_occurred = pyqtSignal(str)  # Emits error message
    
    def __init__(self, api_handler: APIHandler):
        super().__init__()
        self.api_handler = api_handler
    
    def run(self):
        try:
            # Get all text-to-image models from collection
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

class ModelManager(QDialog):
    """Dialog for browsing and managing models."""
    
    models_updated = pyqtSignal()  # Emitted when model list changes
    
    def __init__(self, api_handler: APIHandler, model_repository: ModelRepository, parent=None):
        super().__init__(parent)
        self.api_handler = api_handler
        self.model_repository = model_repository
        self.installed_models = set()  # Track installed models
        self.current_filter = ""
        self._init_ui()
        self._load_installed_models()
        self._load_default_models()  # Show something immediately
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Model Manager")
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Header section with counts
        header_layout = QHBoxLayout()
        self.installed_count_label = QLabel()
        header_layout.addWidget(self.installed_count_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Status section
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Loading models...")
        status_layout.addWidget(self.status_label)
        
        self.refresh_button = QPushButton("Refresh Available Models")
        self.refresh_button.clicked.connect(self._refresh_models)
        status_layout.addWidget(self.refresh_button)
        
        layout.addLayout(status_layout)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter models by name, owner, or description...")
        self.search_input.textChanged.connect(self._filter_models)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Tree widget for model list
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Model", "Owner", "Description", "Added"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 120)
        self.tree.setColumnWidth(2, 500)
        self.tree.setColumnWidth(3, 80)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree.itemClicked.connect(self._handle_item_clicked)
        layout.addWidget(self.tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add to Model List")
        self.add_button.clicked.connect(self._add_selected)
        self.add_button.setEnabled(False)
        button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove from Model List")
        self.remove_button.clicked.connect(self._remove_selected)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Initialize loader thread
        self.loader_thread = ModelLoaderThread(self.api_handler)
        self.loader_thread.models_loaded.connect(self._on_models_loaded)
        self.loader_thread.error_occurred.connect(self._on_load_error)
    
    def _update_counts(self):
        """Update the header counts."""
        total = self.tree.topLevelItemCount()
        self.installed_count_label.setText(
            f"Models on list: {len(self.installed_models)} of {total} available"
        )
    
    def _load_default_models(self):
        """Load the default models list."""
        try:
            paths = [
                Path(__file__).parent.parent.parent.parent / 'resources' / 'models' / 'default_models.json',
                Path.home() / '.replicate-desktop' / 'default_models.json'
            ]
            
            for path in paths:
                if path.exists():
                    with open(path, 'r') as f:
                        data = json.load(f)
                        self._populate_model_list(data.get('models', []))
                        self._update_counts()
                        return
            
            logger.warning("Default models file not found")
            
        except Exception as e:
            logger.error(f"Error loading default models: {e}")
    
    def _load_installed_models(self):
        """Load the list of installed models."""
        try:
            models = self.model_repository.list_models()
            self.installed_models = {model.identifier for model in models}
            self.status_label.setText(f"{len(self.installed_models)} models in list")
        except Exception as e:
            logger.error(f"Error loading installed models: {e}")
            self.status_label.setText("Error loading model list")
    
    def _refresh_models(self):
        """Start loading available models."""
        self.refresh_button.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("Loading available models...")
        self.loader_thread.start()
    
    def _filter_models(self):
        """Filter the model list based on search text."""
        search_text = self.search_input.text().lower()
        visible_count = 0
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            matches = (
                search_text in item.text(0).lower() or
                search_text in item.text(1).lower() or
                search_text in item.text(2).lower()
            )
            item.setHidden(not matches)
            if matches:
                visible_count += 1
        
        if search_text:
            self.status_label.setText(f"Showing {visible_count} matching models")
        else:
            self._update_counts()
    
    def _populate_model_list(self, models: List[Dict[str, Any]], clear_first: bool = True):
        """Populate the tree widget with models."""
        if clear_first:
            self.tree.clear()
        
        # Sort models by name
        sorted_models = sorted(models, key=lambda x: x['name'].lower())
        
        for model in sorted_models:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, model['name'])
            item.setText(1, model['owner'])
            item.setText(2, model.get('description', ''))
            
            # Set installed status with yes/no
            is_installed = model['identifier'] in self.installed_models
            item.setText(3, "Yes" if is_installed else "No")
            
            # Use color to indicate status
            if is_installed:
                item.setForeground(3, QColor('#2E8B57'))  # Sea green
                item.setFont(3, self.font())  # Make it more visible
            
            # Store model data
            item.setData(0, Qt.ItemDataRole.UserRole, model)
        
        self._update_counts()
    
    def _handle_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item selection."""
        if not item:
            return
            
        model_data = item.data(0, Qt.ItemDataRole.UserRole)
        is_installed = model_data['identifier'] in self.installed_models
        
        self.add_button.setEnabled(not is_installed)
        self.remove_button.setEnabled(is_installed)
    
    def _add_selected(self):
        """Add selected model to installed list."""
        item = self.tree.currentItem()
        if not item:
            return
        
        try:
            model_data = item.data(0, Qt.ItemDataRole.UserRole)
            if model_data['identifier'] not in self.installed_models:
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
                
                # Update UI
                item.setText(3, "Yes")
                item.setForeground(3, QColor('#2E8B57'))
                self.add_button.setEnabled(False)
                self.remove_button.setEnabled(True)
                
                self._update_counts()
                self.models_updated.emit()
                
        except Exception as e:
            logger.error(f"Error adding model: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add model: {str(e)}")
    
    def _remove_selected(self):
        """Remove selected model from installed list."""
        item = self.tree.currentItem()
        if not item:
            return
        
        try:
            model_data = item.data(0, Qt.ItemDataRole.UserRole)
            if model_data['identifier'] in self.installed_models:
                if self.model_repository.delete_by_identifier(model_data['identifier']):
                    self.installed_models.remove(model_data['identifier'])
                    
                    # Update UI
                    item.setText(3, "No")
                    item.setForeground(3, self.palette().text().color())
                    self.add_button.setEnabled(True)
                    self.remove_button.setEnabled(False)
                    
                    self._update_counts()
                    self.models_updated.emit()
                
        except Exception as e:
            logger.error(f"Error removing model: {e}")
            QMessageBox.critical(self, "Error", f"Failed to remove model: {str(e)}")
    
    def _on_models_loaded(self, models: List[Dict[str, Any]]):
        """Handle loaded model data."""
        self._populate_model_list(models)
        
        self.refresh_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"Loaded {len(models)} available models")
        
        # Filter if search is active
        if self.search_input.text():
            self._filter_models()
    
    def _on_load_error(self, error: str):
        """Handle model loading error."""
        self.refresh_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("Error loading models")
        QMessageBox.critical(self, "Error", f"Failed to load models: {error}")