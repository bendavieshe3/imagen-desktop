"""Generation progress display component."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QProgressBar,
    QLabel, QGroupBox
)
from PyQt6.QtCore import pyqtSignal

class GenerationProgress(QWidget):
    cancel_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_prediction_id = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Generation Progress")
        progress_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        
        group.setLayout(progress_layout)
        layout.addWidget(group)
    
    def show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        self.progress_bar.setVisible(show)
    
    def set_status(self, text: str):
        """Update the status text."""
        self.status_label.setText(text)
    
    def on_generation_started(self, prediction_id: str):
        """Handle generation started."""
        self.current_prediction_id = prediction_id
        self.set_status(f"Generation in progress... (ID: {prediction_id})")
        self.show_progress(True)
    
    def on_generation_completed(self, prediction_id: str):
        """Handle generation completed."""
        if prediction_id == self.current_prediction_id:
            self.set_status("Generation completed!")
            self.show_progress(False)
            self.current_prediction_id = None
    
    def on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failure."""
        if prediction_id == self.current_prediction_id:
            self.set_status(f"Generation failed: {error}")
            self.show_progress(False)
            self.current_prediction_id = None
    
    def on_generation_canceled(self, prediction_id: str):
        """Handle generation cancellation."""
        if prediction_id == self.current_prediction_id:
            self.set_status("Generation canceled")
            self.show_progress(False)
            self.current_prediction_id = None