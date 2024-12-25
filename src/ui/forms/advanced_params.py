"""Advanced generation parameters component."""
from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QDoubleSpinBox,
    QSpinBox, QTextEdit
)
from PyQt6.QtCore import pyqtSignal
from dataclasses import dataclass
from typing import Optional

@dataclass
class AdvancedParameters:
    """Data class for advanced parameters."""
    seed: Optional[int]
    guidance_scale: float
    num_inference_steps: int

class AdvancedParams(QWidget):
    params_changed = pyqtSignal(object)  # Emits AdvancedParameters
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QFormLayout(self)
        
        # Seed input
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
        self.seed_input.textChanged.connect(self._emit_params)
        self.guidance_scale.valueChanged.connect(self._emit_params)
        self.num_inference_steps.valueChanged.connect(self._emit_params)
    
    def _emit_params(self):
        """Emit updated parameters."""
        params = self.get_parameters()
        self.params_changed.emit(params)
    
    def get_parameters(self) -> AdvancedParameters:
        """Get current parameter values."""
        seed_text = self.seed_input.toPlainText().strip()
        seed = int(seed_text) if seed_text.isdigit() else None
        
        return AdvancedParameters(
            seed=seed,
            guidance_scale=self.guidance_scale.value(),
            num_inference_steps=self.num_inference_steps.value()
        )
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all inputs."""
        self.seed_input.setEnabled(enabled)
        self.guidance_scale.setEnabled(enabled)
        self.num_inference_steps.setEnabled(enabled)