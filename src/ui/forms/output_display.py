"""Component for displaying the current generation output and progress."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
from typing import Optional

class OutputDisplay(QWidget):
    """Displays the current generation output and progress."""
    
    def __init__(self):
        super().__init__()
        self.current_image: Optional[Path] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Main image display
        self.image_frame = QFrame()
        self.image_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.image_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        
        image_layout = QVBoxLayout(self.image_frame)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.image_label)
        
        layout.addWidget(self.image_frame)
        
        # Progress section
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        layout.addLayout(progress_layout)
    
    def show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    def set_status(self, text: str):
        """Update the status text."""
        self.status_label.setText(text)
    
    def display_image(self, image_path: Optional[Path]):
        """Display an image or clear if None."""
        self.current_image = image_path
        
        if image_path and image_path.exists():
            pixmap = QPixmap(str(image_path))
            scaled_pixmap = pixmap.scaled(
                self.image_frame.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.clear()
    
    def resizeEvent(self, event):
        """Handle resize events to scale image."""
        super().resizeEvent(event)
        if self.current_image:
            self.display_image(self.current_image)