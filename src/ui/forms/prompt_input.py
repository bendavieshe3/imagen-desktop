"""Prompt input component."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLabel
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextOption

class PromptInput(QWidget):
    prompt_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Prompt label
        prompt_label = QLabel("Prompt:")
        layout.addWidget(prompt_label)
        
        # Main prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setMinimumHeight(80)
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        self.prompt_input.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.prompt_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.prompt_input.textChanged.connect(
            lambda: self.prompt_changed.emit(self.get_prompt())
        )
        layout.addWidget(self.prompt_input)
    
    def get_prompt(self) -> str:
        """Get the current prompt text."""
        return self.prompt_input.toPlainText()
    
    def set_prompt(self, prompt: str):
        """Set the prompt text."""
        self.prompt_input.setPlainText(prompt)
    
    def clear(self):
        """Clear the prompt input."""
        self.prompt_input.clear()
    
    def setEnabled(self, enabled: bool):
        """Enable or disable the input."""
        super().setEnabled(enabled)
        self.prompt_input.setEnabled(enabled)