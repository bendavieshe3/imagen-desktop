"""Sidebar containing generation form elements."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QPushButton
)
from PyQt6.QtCore import pyqtSignal

from .model_selector import ModelSelector
from .prompt_input import PromptInput
from .generation_params import GenerationParams
from .advanced_params import AdvancedParams

class GenerationSidebar(QWidget):
    """Sidebar containing generation controls."""
    
    generation_requested = pyqtSignal(str, dict)  # model_id, parameters
    
    def __init__(self, api_handler, model_repository=None):
        super().__init__()
        self.api_handler = api_handler
        self.model_repository = model_repository
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Model selection
        self.model_selector = ModelSelector(
            self.api_handler,
            model_repository=self.model_repository
        )
        layout.addWidget(self.model_selector)
        
        # Prompt input
        self.prompt_input = PromptInput()
        layout.addWidget(self.prompt_input)
        
        # Parameters tabs
        tabs = QTabWidget()
        
        self.generation_params = GenerationParams()
        tabs.addTab(self.generation_params, "Basic")
        
        self.advanced_params = AdvancedParams()
        tabs.addTab(self.advanced_params, "Advanced")
        
        layout.addWidget(tabs)
        
        # Generate button
        self.generate_button = QPushButton("Generate")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.clicked.connect(self._on_generate)
        layout.addWidget(self.generate_button)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect internal signals."""
        pass  # Add any needed signal connections
    
    def _on_generate(self):
        """Handle generate button click."""
        model_id = self.model_selector.get_selected_model()
        if not model_id:
            return
        
        # Get parameters from components
        basic_params = self.generation_params.get_parameters()
        advanced_params = self.advanced_params.get_parameters()
        
        # Combine parameters
        params = {
            'prompt': self.prompt_input.get_prompt(),
            'num_outputs': basic_params.num_images,
            'width': basic_params.width,
            'height': basic_params.height,
            'disable_safety_checker': True
        }
        
        # Add advanced parameters
        if advanced_params.seed is not None:
            params['seed'] = advanced_params.seed
        if advanced_params.guidance_scale != 7.5:
            params['guidance_scale'] = advanced_params.guidance_scale
        if advanced_params.num_inference_steps != 50:
            params['num_inference_steps'] = advanced_params.num_inference_steps
        
        self.generation_requested.emit(model_id, params)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all form elements."""
        self.model_selector.setEnabled(enabled)
        self.prompt_input.setEnabled(enabled)
        self.generation_params.set_enabled(enabled)
        self.advanced_params.set_enabled(enabled)
        self.generate_button.setEnabled(enabled)