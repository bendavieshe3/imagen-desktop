"""Component for displaying the current generation output and progress."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar,
    QFrame, QStackedLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
from typing import Optional

class OverlayProgressBar(QWidget):
    """Progress bar with semi-transparent background."""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 4px;
            }
            QProgressBar {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #ccc;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: rgba(100, 149, 237, 180);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(200, 20)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

class OutputDisplay(QWidget):
    """Displays the current generation output and progress."""
    
    def __init__(self):
        super().__init__()
        self.current_product: Optional[Path] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main product display
        self.product_frame = QFrame()
        self.product_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.product_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        
        # Use stacked layout for product and progress overlay
        self.stack = QStackedLayout(self.product_frame)
        
        # Product container
        product_container = QWidget()
        product_layout = QVBoxLayout(product_container)
        self.product_label = QLabel()
        self.product_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        product_layout.addWidget(self.product_label)
        
        # Progress overlay
        self.progress_overlay = OverlayProgressBar()
        self.progress_overlay.hide()
        
        # Add both to stacked layout
        self.stack.addWidget(product_container)
        self.stack.addWidget(self.progress_overlay)
        
        layout.addWidget(self.product_frame)
        
        # Status label at bottom
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def show_progress(self, show: bool = True):
        """Show or hide the progress overlay."""
        if show:
            self.progress_overlay.progress_bar.setRange(0, 0)  # Indeterminate
            self.progress_overlay.show()
            self.stack.setCurrentWidget(self.progress_overlay)
        else:
            self.progress_overlay.hide()
            self.stack.setCurrentWidget(self.stack.widget(0))
    
    def set_status(self, text: str):
        """Update the status text."""
        self.status_label.setText(text)
    
    def display_product(self, product_path: Optional[Path]):
        """Display a product image or clear if None."""
        self.current_product = product_path
        
        if product_path and product_path.exists():
            pixmap = QPixmap(str(product_path))
            scaled_pixmap = pixmap.scaled(
                self.product_frame.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.product_label.setPixmap(scaled_pixmap)
        else:
            self.product_label.clear()
    
    def resizeEvent(self, event):
        """Handle resize events to scale the displayed product."""
        super().resizeEvent(event)
        if self.current_product:
            self.display_product(self.current_product)