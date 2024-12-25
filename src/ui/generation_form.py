"""Main form for image generation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from .forms.model_selector import ModelSelector
from .forms.prompt_input import PromptInput
from .forms.generation_params import GenerationParams
from .forms.advanced_params import AdvancedParams
from .forms.generation_progress import GenerationProgress

class GenerationForm(QWidget):
    generation_requested = pyqtSignal(str, dict)  # model_id, parameters
    
    def __init__(self, api_handler):
        super().__init__()
        self.api_handler = api_handler
        self.current_prediction_id = None
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Tabs for basic and advanced settings
        tab_widget = QTabWidget()
        
        # Basic tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        self.model_selector = ModelSelector(self.api_handler)
        basic_layout.addWidget(self.model_selector)
        
        self.prompt_input = PromptInput()
        basic_layout.addWidget(self.prompt_input)
        
        self.generation_params = GenerationParams()
        basic_layout.addWidget(self.generation_params)
        
        basic_tab.setLayout(basic_layout)
        tab_widget.addTab(basic_tab, "Basic")
        
        # Advanced tab
        self.advanced_params = AdvancedParams()
        tab_widget.addTab(self.advanced_params, "Advanced")
        
        layout.addWidget(tab_widget)
        
        # Progress section
        self.progress = GenerationProgress()
        layout.addWidget(self.progress)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_generation)
        button_layout.addWidget(self.cancel_button)
        
        self.generate_button = QPushButton("Generate")
        self.generate_button.setMinimumWidth(120)
        self.generate_button.clicked.connect(self._on_generate)
        button_layout.addWidget(self.generate_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals between components."""
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
        self.api_handler.generation_canceled.connect(self._on_generation_canceled)
    
    def _on_generate(self):
        """Handle generate button click."""
        model_id = self.model_selector.get_selected_model()
        if not model_id:
            QMessageBox.critical(self, "Error", "Please select a valid model")
            return
        
        # Get parameters from components
        basic_params = self.generation_params.get_parameters()
        advanced_params = self.advanced_params.get_parameters()
        
        # Combine all parameters
        params = {
            'prompt': self.prompt_input.get_prompt(),
            'num_outputs': basic_params.num_images,
            'width': basic_params.width,
            'height': basic_params.height,
            'disable_safety_checker': True
        }
        
        # Add advanced parameters if they differ from defaults
        if advanced_params.seed is not None:
            params['seed'] = advanced_params.seed
        
        if advanced_params.guidance_scale != 7.5:
            params['guidance_scale'] = advanced_params.guidance_scale
        
        if advanced_params.num_inference_steps != 50:
            params['num_inference_steps'] = advanced_params.num_inference_steps
        
        try:
            self.generation_requested.emit(model_id, params)
            self._update_ui_state(generating=True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self._update_ui_state(generating=False)
    
    def _cancel_generation(self):
        """Cancel the current generation."""
        if self.current_prediction_id:
            self.api_handler.cancel_generation(self.current_prediction_id)
            self.progress.set_status("Canceling generation...")
            self.cancel_button.setEnabled(False)
    
    def _update_ui_state(self, generating: bool):
        """Update UI elements based on generation state."""
        self.generate_button.setEnabled(not generating)
        self.cancel_button.setEnabled(generating)
        self.progress.show_progress(generating)
        
        # Enable/disable components
        self.model_selector.setEnabled(not generating)
        self.prompt_input.setEnabled(not generating)
        self.generation_params.set_enabled(not generating)
        self.advanced_params.set_enabled(not generating)
    
    def _on_generation_started(self, prediction_id: str):
        self.current_prediction_id = prediction_id
        self.progress.on_generation_started(prediction_id)
        self._update_ui_state(generating=True)
    
    def _on_generation_completed(self, prediction_id: str, output_urls: list):
        if prediction_id == self.current_prediction_id:
            self.progress.on_generation_completed(prediction_id)
            self._update_ui_state(generating=False)
            self.current_prediction_id = None
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        if prediction_id == self.current_prediction_id:
            self.progress.on_generation_failed(prediction_id, error)
            self._update_ui_state(generating=False)
            self.current_prediction_id = None
            QMessageBox.critical(self, "Error", f"Generation failed: {error}")
    
    def _on_generation_canceled(self, prediction_id: str):
        if prediction_id == self.current_prediction_id:
            self.progress.on_generation_canceled(prediction_id)
            self._update_ui_state(generating=False)
            self.current_prediction_id = None