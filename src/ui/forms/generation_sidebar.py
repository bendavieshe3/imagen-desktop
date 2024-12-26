"""Sidebar containing generation form elements."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel,
    QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt

from .model_selector import ModelSelector
from .prompt_input import PromptInput
from .parameter_inputs import ParameterInputs

class SectionTitle(QFrame):
    """Section title with horizontal line."""
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 4)
        layout.setSpacing(4)
        
        # Title label
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        # Horizontal line
        line = QFrame()
        line.setFrameStyle(QFrame.Shape.HLine | QFrame.Shadow.Sunken)
        layout.addWidget(line)

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
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        # Model selection section
        content_layout.addWidget(SectionTitle("Model Selection"))
        
        # Model selector and manager button
        self.model_selector = ModelSelector(
            self.api_handler,
            model_repository=self.model_repository
        )
        content_layout.addWidget(self.model_selector)
        
        model_manager_btn = QPushButton("Manage Models...")
        model_manager_btn.clicked.connect(self.model_selector._show_model_manager)
        content_layout.addWidget(model_manager_btn)
        
        # Prompt input section
        content_layout.addWidget(SectionTitle("Prompt"))
        self.prompt_input = PromptInput()
        content_layout.addWidget(self.prompt_input)
        
        # Parameters section
        content_layout.addWidget(SectionTitle("Parameters"))
        
        # All parameters in one section
        self.parameters = ParameterInputs()
        content_layout.addWidget(self.parameters)
        
        content_layout.addStretch()
        
        # Add scrollable content
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Generate button (outside scroll area)
        self.generate_button = QPushButton("Generate")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.clicked.connect(self._on_generate)
        layout.addWidget(self.generate_button)
    
    def _connect_signals(self):
        """Connect internal signals."""
        pass  # Add any needed signal connections
    
    def _on_generate(self):
        """Handle generate button click."""
        model_id = self.model_selector.get_selected_model()
        if not model_id:
            return
        
        # Get parameters
        params = self.parameters.get_parameters()
        
        # Build parameter dictionary
        generation_params = {
            'prompt': self.prompt_input.get_prompt(),
            'num_outputs': params.num_images,
            'width': params.width,
            'height': params.height,
            'disable_safety_checker': True
        }
        
        # Add optional parameters
        if params.seed is not None:
            generation_params['seed'] = params.seed
        if params.guidance_scale != 7.5:
            generation_params['guidance_scale'] = params.guidance_scale
        if params.num_inference_steps != 50:
            generation_params['num_inference_steps'] = params.num_inference_steps
        
        self.generation_requested.emit(model_id, generation_params)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all form elements."""
        self.model_selector.setEnabled(enabled)
        self.prompt_input.setEnabled(enabled)
        self.parameters.set_enabled(enabled)
        self.generate_button.setEnabled(enabled)