from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QSpinBox, QPushButton,
    QFormLayout, QGroupBox, QTextEdit, QDoubleSpinBox,
    QCheckBox, QProgressBar, QTabWidget, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from ..utils.api_handler import APIHandler

class GenerationForm(QWidget):
    generation_requested = pyqtSignal(str, dict)  # model_id, parameters
    
    def __init__(self, api_handler: APIHandler):
        super().__init__()
        self.api_handler = api_handler
        self.current_prediction_id = None
        self._init_ui()
        self._connect_signals()
        self._load_models()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Tabs for basic and advanced settings
        tab_widget = QTabWidget()
        
        # Basic tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Model selection
        model_group = QGroupBox("Model Selection")
        model_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentIndexChanged.connect(self._update_model_description)
        model_layout.addRow("Model:", self.model_combo)
        
        # Model description
        self.model_description = QLabel()
        self.model_description.setWordWrap(True)
        self.model_description.setStyleSheet("color: gray;")
        model_layout.addRow(self.model_description)
        
        model_group.setLayout(model_layout)
        basic_layout.addWidget(model_group)
        
        # Prompt input
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout()
        
        # Example prompts
        examples_label = QLabel("Example prompts:")
        examples_label.setStyleSheet("color: gray;")
        prompt_layout.addWidget(examples_label)
        
        example_prompts = [
            "a photorealistic landscape of a mountain lake at sunset",
            "a cyberpunk city street at night with neon signs",
            "an oil painting of a cat wearing a renaissance costume"
        ]
        
        for prompt in example_prompts:
            example_btn = QPushButton(prompt)
            example_btn.setStyleSheet("text-align: left;")
            example_btn.clicked.connect(lambda checked, p=prompt: self._use_example_prompt(p))
            prompt_layout.addWidget(example_btn)
        
        # Main prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setMinimumHeight(100)
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        prompt_layout.addWidget(self.prompt_input)
        
        prompt_group.setLayout(prompt_layout)
        basic_layout.addWidget(prompt_group)
        
        # Basic parameters
        params_group = QGroupBox("Basic Parameters")
        params_layout = QFormLayout()
        
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
        self.size_preset_combo.currentTextChanged.connect(self._handle_size_preset)
        params_layout.addRow("Size Preset:", self.size_preset_combo)
        
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
        
        params_group.setLayout(params_layout)
        basic_layout.addWidget(params_group)
        
        tab_widget.addTab(basic_tab, "Basic")
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)
        
        # Advanced parameters
        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Random")
        advanced_layout.addRow("Seed:", self.seed_input)
        
        self.guidance_scale = QDoubleSpinBox()
        self.guidance_scale.setRange(1.0, 20.0)
        self.guidance_scale.setValue(7.5)
        self.guidance_scale.setSingleStep(0.5)
        advanced_layout.addRow("Guidance Scale:", self.guidance_scale)
        
        self.num_inference_steps = QSpinBox()
        self.num_inference_steps.setRange(1, 100)
        self.num_inference_steps.setValue(50)
        advanced_layout.addRow("Inference Steps:", self.num_inference_steps)
        
        self.negative_prompt = QTextEdit()
        self.negative_prompt.setPlaceholderText("Enter negative prompt here...")
        self.negative_prompt.setMaximumHeight(100)
        advanced_layout.addRow("Negative Prompt:", self.negative_prompt)
        
        tab_widget.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tab_widget)
        
        # Progress section
        progress_group = QGroupBox("Generation Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
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
        """Connect to API handler signals."""
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
        self.api_handler.generation_canceled.connect(self._on_generation_canceled)
    
    def _load_models(self):
        """Load available models into the combo box."""
        try:
            models = self.api_handler.list_available_models('text-to-image')
            
            for model in models:
                identifier = f"{model['owner']}/{model['name']}"
                self.model_combo.addItem(identifier, identifier)  # Set both display text and data
                # Store description in item data for later use
                index = self.model_combo.count() - 1
                self.model_combo.setItemData(index, model['description'], Qt.ItemDataRole.UserRole + 1)
                
            # Update initial description
            self._update_model_description()

            
        except Exception as e:
            self.model_combo.addItem("Error loading models")
            self.generate_button.setEnabled(False)
            self.model_description.setText(f"Error: {str(e)}")
    
    def _update_model_description(self):
        """Update the model description when selection changes."""
        current_index = self.model_combo.currentIndex()
        if current_index >= 0:
            description = self.model_combo.itemData(current_index, Qt.ItemDataRole.UserRole)
            if description:
                self.model_description.setText(description)
            else:
                self.model_description.setText("")
    
    def _use_example_prompt(self, prompt: str):
        """Set an example prompt as the current prompt."""
        self.prompt_input.setPlainText(prompt)
    
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
    
    def _on_generate(self):
        """Handle generate button click."""
        model_identifier = self.model_combo.currentData()
        if not model_identifier or '/' not in model_identifier:
            QMessageBox.critical(self, "Error", "Please select a valid model")
            return
        
        # Build parameters
        params = {
            'prompt': self.prompt_input.toPlainText(),
            'num_outputs': self.num_images_spin.value(),
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
        }
        
        # Add advanced parameters
        if self.negative_prompt.toPlainText():
            params['negative_prompt'] = self.negative_prompt.toPlainText()
        
        if self.guidance_scale.value() != 7.5:  # Only add if different from default
            params['guidance_scale'] = self.guidance_scale.value()
            
        if self.num_inference_steps.value() != 50:  # Only add if different from default
            params['num_inference_steps'] = self.num_inference_steps.value()
        
        seed = self.seed_input.text().strip()
        if seed and seed.isdigit():
            params['seed'] = int(seed)
        
        try:
            # Emit signal for parent to handle generation
            self.generation_requested.emit(model_identifier, params)
            
            # Update UI state
            self._update_ui_state(generating=True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self._update_ui_state(generating=False)

    def _cancel_generation(self):
        """Cancel the current generation."""
        if self.current_prediction_id:
            self.api_handler.cancel_generation(self.current_prediction_id)
            self.status_label.setText("Canceling generation...")
            self.cancel_button.setEnabled(False)
    
    def _update_ui_state(self, generating: bool):
        """Update UI elements based on generation state."""
        # Update button states
        self.generate_button.setEnabled(not generating)
        self.cancel_button.setEnabled(generating)
        self.generate_button.setText("Generating..." if generating else "Generate")
        
        # Show/hide progress bar
        self.progress_bar.setVisible(generating)
        
        # Enable/disable input fields
        self.model_combo.setEnabled(not generating)
        self.prompt_input.setEnabled(not generating)
        self.num_images_spin.setEnabled(not generating)
        self.width_spin.setEnabled(not generating)
        self.height_spin.setEnabled(not generating)
        self.size_preset_combo.setEnabled(not generating)
        self.seed_input.setEnabled(not generating)
        self.guidance_scale.setEnabled(not generating)
        self.num_inference_steps.setEnabled(not generating)
        self.negative_prompt.setEnabled(not generating)
    
    def _on_generation_started(self, prediction_id: str):
        """Handle generation started signal."""
        self.current_prediction_id = prediction_id
        self.status_label.setText(f"Generation in progress... (ID: {prediction_id})")
        self._update_ui_state(generating=True)
    
    def _on_generation_completed(self, prediction_id: str, output_urls: list):
        """Handle generation completed signal."""
        if prediction_id == self.current_prediction_id:
            self.status_label.setText(f"Generation completed! (ID: {prediction_id})")
            self._update_ui_state(generating=False)
            self.current_prediction_id = None
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failed signal."""
        if prediction_id == self.current_prediction_id or not prediction_id:
            self.status_label.setText(f"Generation failed: {error}")
            self._update_ui_state(generating=False)
            self.current_prediction_id = None
            QMessageBox.critical(self, "Error", f"Generation failed: {error}")
    
    def _on_generation_canceled(self, prediction_id: str):
        """Handle generation canceled signal."""
        if prediction_id == self.current_prediction_id:
            self.status_label.setText("Generation canceled")
            self._update_ui_state(generating=False)
            self.current_prediction_id = None