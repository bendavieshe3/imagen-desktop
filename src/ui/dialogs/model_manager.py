"""Dialog for browsing and managing available models."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QLabel, QProgressBar,
    QMessageBox, QLineEdit, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Dict, Any

from .model_manager_presenter import ModelManagerPresenter
from ...api.api_handler import APIHandler
from ...data.model_repository import ModelRepository
from ...utils.debug_logger import logger

class ModelManager(QDialog):
    """Dialog for browsing and managing models."""
    
    models_updated = pyqtSignal()  # Emitted when model list changes
    
    def __init__(self, api_handler: APIHandler, model_repository: ModelRepository, parent=None):
        super().__init__(parent)
        self.presenter = ModelManagerPresenter(api_handler, model_repository)
        self._init_ui()
        self._load_models()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Model Manager")
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Header section
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
        self.search_input.setPlaceholderText("Filter models...")
        self.search_input.textChanged.connect(self._filter_models)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Progress bar
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
        
        # Action buttons
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
    
    def _connect_signals(self):
        """Connect presenter signals."""
        self.presenter.loader_thread.models_loaded.connect(self._on_models_loaded)
        self.presenter.loader_thread.error_occurred.connect(self._on_load_error)
    
    def _load_models(self):
        """Load and display models."""
        try:
            models = self.presenter.load_models()
            self._populate_model_list(models)
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load models: {str(e)}")
    
    def _refresh_models(self):
        """Start loading available models."""
        self.refresh_button.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("Loading available models...")
        self.presenter.loader_thread.load_models()
    
    def _on_models_loaded(self, models: list):
        """Handle loaded model data."""
        self._populate_model_list(models)
        self.refresh_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"Loaded {len(models)} available models")
        
        if self.search_input.text():
            self._filter_models()
    
    def _on_load_error(self, error: str):
        """Handle model loading error."""
        self.refresh_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("Error loading models")
        QMessageBox.critical(self, "Error", f"Failed to load models: {error}")
    
    def _populate_model_list(self, models: list):
        """Populate the tree widget with models."""
        self.tree.clear()
        
        for model in models:
            item = QTreeWidgetItem(self.tree)
            self._setup_model_item(item, model)
        
        self._update_counts()
    
    def _setup_model_item(self, item: QTreeWidgetItem, model: Dict[str, Any]):
        """Configure a tree widget item for a model."""
        display_name = f"⭐ {model['name']}" if model.get('featured') else model['name']
        
        item.setText(0, display_name)
        item.setText(1, model['owner'])
        item.setText(2, model.get('description', ''))
        
        is_installed = self.presenter.is_installed(model['identifier'])
        item.setText(3, "Yes" if is_installed else "No")
        
        if is_installed:
            item.setForeground(3, QColor('#2E8B57'))
        
        item.setData(0, Qt.ItemDataRole.UserRole, model)
    
    def _handle_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item selection."""
        if not item:
            return
            
        model_data = item.data(0, Qt.ItemDataRole.UserRole)
        is_installed = self.presenter.is_installed(model_data['identifier'])
        
        self.add_button.setEnabled(not is_installed)
        self.remove_button.setEnabled(is_installed)
    
    def _filter_models(self):
        """Filter the model list based on search text."""
        search_text = self.search_input.text().lower()
        visible_count = 0
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            matches = any(
                search_text in item.text(col).lower()
                for col in range(3)
            )
            item.setHidden(not matches)
            if matches:
                visible_count += 1
        
        if search_text:
            self.status_label.setText(f"Showing {visible_count} matching models")
        else:
            self._update_counts()
    
    def _update_counts(self):
        """Update the header counts."""
        total = self.tree.topLevelItemCount()
        installed = len(self.presenter.installed_models)
        self.installed_count_label.setText(
            f"Models on list: {installed} of {total} available"
        )
    
    def _add_selected(self):
        """Add selected model to installed list."""
        item = self.tree.currentItem()
        if not item:
            return
        
        try:
            model_data = item.data(0, Qt.ItemDataRole.UserRole)
            if self.presenter.add_model(model_data):
                self._setup_model_item(item, model_data)
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
            if self.presenter.remove_model(model_data['identifier']):
                self._setup_model_item(item, model_data)
                self._update_counts()
                self.models_updated.emit()
                
        except Exception as e:
            logger.error(f"Error removing model: {e}")
            QMessageBox.critical(self, "Error", f"Failed to remove model: {str(e)}")