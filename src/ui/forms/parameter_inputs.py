"""Combined parameter inputs for image generation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QTextEdit, QLabel
)
from PyQt6.QtCore import pyqtSignal
from dataclasses import dataclass
from typing import Optional

@dataclass
class GenerationParameters:
    """Data class for all generation parameters."""
    num_images: int
    width: int
    height: int
    seed: Optional[int]
    guidance_scale: float
    num_inference_steps: int

class ParameterInputs(QWidget):
    """Combined parameter inputs for image generation."""
    
    params_changed = pyqtSignal(object)  # Emits GenerationParameters
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Number of images
        self.num_images_spin = QSpinBox()
        self.num_images_spin.setRange(1, 10)
        self.num_images_spin.setValue(1)
        layout.addRow("Number of Images:", self.num_images_spin)
        
        # Image size
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
        layout.addRow("Image Size:", size_layout)
        
        # Seed
        self.seed_input = QTextEdit()
        self.seed_input.setPlaceholderText("Random")
        self.seed_input.setMaximumHeight(50)
        layout.addRow("Seed:", self.seed_input)
        
        # Guidance scale
        self.guidance_scale = QDoubleSpinBox()
        self.guidance_scale.setRange(1.0, 20.0)
        self.guidance_scale.setValue(7.5)
        self.guidance_scale.setSingleStep(0.5)
        layout.addRow("Guidance Scale:", self.guidance_scale)
        
        # Inference steps
        self.num_inference_steps = QSpinBox()
        self.num_inference_steps.setRange(1, 100)
        self.num_inference_steps.setValue(50)
        layout.addRow("Inference Steps:", self.num_inference_steps)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.num_images_spin.valueChanged.connect(self._emit_params)
        self.width_spin.valueChanged.connect(self._emit_params)
        self.height_spin.valueChanged.connect(self._emit_params)
        self.seed_input.textChanged.connect(self._emit_params)
        self.guidance_scale.valueChanged.connect(self._emit_params)
        self.num_inference_steps.valueChanged.connect(self._emit_params)
    
    def _emit_params(self):
        """Emit updated parameters."""
        params = self.get_parameters()
        self.params_changed.emit(params)
    
    def get_parameters(self) -> GenerationParameters:
        """Get current parameter values."""
        seed_text = self.seed_input.toPlainText().strip()
        seed = int(seed_text) if seed_text.isdigit() else None
        
        return GenerationParameters(
            num_images=self.num_images_spin.value(),
            width=self.width_spin.value(),
            height=self.height_spin.value(),
            seed=seed,
            guidance_scale=self.guidance_scale.value(),
            num_inference_steps=self.num_inference_steps.value()
        )
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all inputs."""
        self.num_images_spin.setEnabled(enabled)
        self.width_spin.setEnabled(enabled)
        self.height_spin.setEnabled(enabled)
        self.seed_input.setEnabled(enabled)
        self.guidance_scale.setEnabled(enabled)
        self.num_inference_steps.setEnabled(enabled)