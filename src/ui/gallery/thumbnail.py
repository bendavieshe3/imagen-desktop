"""Individual image thumbnail widget."""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from pathlib import Path

class ImageThumbnail(QLabel):
    """Widget displaying a thumbnail of a generated image."""
    
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(QSize(200, 200))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f0f0f0;
                border-radius: 4px;
                padding: 2px;
            }
            QLabel:hover {
                border-color: #999;
                background-color: #e5e5e5;
            }
        """)
        self._load_image()
    
    def _load_image(self):
        """Load and display the image."""
        try:
            pixmap = QPixmap(str(self.image_path))
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            
            # Store original dimensions for metadata
            self.original_width = pixmap.width()
            self.original_height = pixmap.height()
            
        except Exception as e:
            self.setText("Error loading image")
            self.setStyleSheet(self.styleSheet() + "QLabel { color: red; }")
            print(f"Error loading thumbnail for {self.image_path}: {e}")

    def get_file_info(self) -> dict:
        """Get information about the image file."""
        return {
            'path': self.image_path,
            'width': getattr(self, 'original_width', 0),
            'height': getattr(self, 'original_height', 0),
            'size': self.image_path.stat().st_size if self.image_path.exists() else 0
        }