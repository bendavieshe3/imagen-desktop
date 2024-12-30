"""Basic generation parameters component."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QComboBox, QLabel, QGroupBox
)
from PyQt6.QtCore import pyqtSignal
from dataclasses import dataclass

@dataclass
class GenerationParameters:
    """Data class for generation parameters."""
    num_images: int
    width: int
    height: int

class GenerationParams(QWidget):
    params_changed = pyqtSignal(object)  # Emits GenerationParameters
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Basic Parameters")
        params_layout = QFormLayout()
        
        # Number of images
        self.num_images_spin = QSpinBox()
        self.num_images_spin.setRange(1, 10)
        self.num_images_spin.setValue(1)
        params_layout.addRow("Number of Images:", self.num_images_spin)
        
        # Image size presets
        self.size_preset_combo = QComboBox()
        self.size_preset_combo.addItems([
            "Square (512x512)", 
            "Landscape (768x512)", 
            "Portrait (512x768)",
            "HD (1024x768)",
            "Custom"
        ])
        params_layout.addRow("Size Preset:", self.size_preset_combo)
        
        # Custom size inputs
        size_layout = QHBoxLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(256, 1024)
        self.width_spin.setValue(512)
        self.width_spin.setSingleStep(64)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(256, 1024)
        self.height_spin.setValue(512)
        self.height_spin.setSingleStep(64)
        
        size_layout.addWidget(QLabel("Width:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Height:"))
        size_layout.addWidget(self.height_spin)
        params_layout.addRow("Custom Size:", size_layout)
        
        group.setLayout(params_layout)
        layout.addWidget(group)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.size_preset_combo.currentTextChanged.connect(self._handle_size_preset)
        
        # Connect value changes to emit updated parameters
        self.num_images_spin.valueChanged.connect(self._emit_params)
        self.width_spin.valueChanged.connect(self._emit_params)
        self.height_spin.valueChanged.connect(self._emit_params)
    
    def _handle_size_preset(self, preset: str):
        """Handle size preset selection."""
        if preset == "Square (512x512)":
            self.width_spin.setValue(512)
            self.height_spin.setValue(512)
        elif preset == "Landscape (768x512)":
            self.width_spin.setValue(768)
            self.height_spin.setValue(512)
        elif preset == "Portrait (512x768)":
            self.width_spin.setValue(512)
            self.height_spin.setValue(768)
        elif preset == "HD (1024x768)":
            self.width_spin.setValue(1024)
            self.height_spin.setValue(768)
    
    def _emit_params(self):
        """Emit updated parameters."""
        params = GenerationParameters(
            num_images=self.num_images_spin.value(),
            width=self.width_spin.value(),
            height=self.height_spin.value()
        )
        self.params_changed.emit(params)
    
    def get_parameters(self) -> GenerationParameters:
        """Get current parameter values."""
        return GenerationParameters(
            num_images=self.num_images_spin.value(),
            width=self.width_spin.value(),
            height=self.height_spin.value()
        )
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all inputs."""
        self.num_images_spin.setEnabled(enabled)
        self.size_preset_combo.setEnabled(enabled)
        self.width_spin.setEnabled(enabled)
        self.height_spin.setEnabled(enabled)