"""Prompt input component with examples."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLabel, QPushButton, QGroupBox
)
from PyQt6.QtCore import pyqtSignal

class PromptInput(QWidget):
    prompt_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout()
        
        # Example prompts section
        examples_label = QLabel("Example prompts:")
        examples_label.setStyleSheet("color: gray;")
        prompt_layout.addWidget(examples_label)
        
        example_prompts = [
            "a photorealistic landscape of a mountain lake at sunset",
            "a cyberpunk city street at night with neon signs",
            "an oil painting of a cat wearing a renaissance costume"
        ]
        
        for prompt in example_prompts:
            btn = QPushButton(prompt)
            btn.setStyleSheet("text-align: left;")
            btn.clicked.connect(lambda checked, p=prompt: self._use_example(p))
            prompt_layout.addWidget(btn)
        
        # Main prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setMinimumHeight(100)
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        self.prompt_input.textChanged.connect(
            lambda: self.prompt_changed.emit(self.get_prompt())
        )
        prompt_layout.addWidget(self.prompt_input)
        
        group.setLayout(prompt_layout)
        layout.addWidget(group)
    
    def _use_example(self, prompt: str):
        """Set an example prompt as the current prompt."""
        self.prompt_input.setPlainText(prompt)
    
    def get_prompt(self) -> str:
        """Get the current prompt text."""
        return self.prompt_input.toPlainText()
    
    def set_prompt(self, prompt: str):
        """Set the prompt text."""
        self.prompt_input.setPlainText(prompt)
    
    def clear(self):
        """Clear the prompt input."""
        self.prompt_input.clear()