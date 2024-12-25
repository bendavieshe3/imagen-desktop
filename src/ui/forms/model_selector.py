"""Model selection component."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, 
    QComboBox, QLabel, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt

from ...api.api_handler import APIHandler  # Updated import path

class ModelSelector(QWidget):
    model_changed = pyqtSignal(str)  # Emits model identifier
    
    def __init__(self, api_handler: APIHandler):
        super().__init__()
        self.api_handler = api_handler
        self._init_ui()
        self._load_models()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Model Selection")
        form_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        form_layout.addRow("Model:", self.model_combo)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: gray;")
        form_layout.addRow(self.description_label)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
    
    def _load_models(self):
        """Load available models into combo box."""
        try:
            models = self.api_handler.list_available_models('text-to-image')
            
            for model in models:
                identifier = f"{model['owner']}/{model['name']}"
                self.model_combo.addItem(identifier, identifier)
                index = self.model_combo.count() - 1
                self.model_combo.setItemData(
                    index, 
                    model['description'], 
                    Qt.ItemDataRole.UserRole + 1
                )
            
            self._update_description()
            
        except Exception as e:
            self.model_combo.addItem("Error loading models")
            self.description_label.setText(f"Error: {str(e)}")
    
    def _on_model_changed(self, index):
        """Handle model selection change."""
        self._update_description()
        if index >= 0:
            model_id = self.model_combo.itemData(index)
            self.model_changed.emit(model_id)
    
    def _update_description(self):
        """Update the model description text."""
        index = self.model_combo.currentIndex()
        if index >= 0:
            description = self.model_combo.itemData(
                index, 
                Qt.ItemDataRole.UserRole + 1
            )
            self.description_label.setText(description or "")
    
    def get_selected_model(self) -> str:
        """Get the currently selected model identifier."""
        index = self.model_combo.currentIndex()
        return self.model_combo.itemData(index) if index >= 0 else None
    
    def setEnabled(self, enabled: bool):
        """Enable or disable the component."""
        super().setEnabled(enabled)
        self.model_combo.setEnabled(enabled)