"""Thumbnail widget for displaying a product."""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent

from imagen_desktop.core.models.product import Product
from imagen_desktop.utils.debug_logger import logger

class ProductThumbnail(QLabel):
    """Widget displaying a thumbnail of a product."""
    
    clicked = pyqtSignal(Product)
    
    def __init__(self, product: Product, parent=None):
        super().__init__(parent)
        self.product = product
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
        self._load_thumbnail()
    
    def _load_thumbnail(self):
        """Load and display the product thumbnail."""
        try:
            if not self.product.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.product.file_path}")
                
            pixmap = QPixmap(str(self.product.file_path))
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logger.error(
                "Failed to load thumbnail",
                extra={
                    'context': {
                        'product_id': self.product.id,
                        'error': str(e)
                    }
                }
            )
            self.setText("Error loading image")
            self.setStyleSheet(self.styleSheet() + "QLabel { color: red; }")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.product)
        super().mousePressEvent(event)