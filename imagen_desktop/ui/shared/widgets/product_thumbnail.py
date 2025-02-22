"""Thumbnail widget for displaying a product."""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QMouseEvent
from pathlib import Path

from imagen_desktop.core.models.product import Product
from imagen_desktop.core.events.product_events import (
    ProductEvent, ProductEventType, ProductEventPublisher
)
from imagen_desktop.utils.debug_logger import logger

class ProductThumbnail(QLabel):
    """Widget displaying a thumbnail of a product."""
    
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
            # Convert string path to Path object if necessary
            file_path = self.product.file_path
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(
                    "Failed to load thumbnail - file not found",
                    extra={
                        'context': {
                            'product_id': self.product.id,
                            'file_path': str(file_path)
                        }
                    }
                )
                self._show_error("File not found")
                return
                
            pixmap = QPixmap(str(file_path))
            if pixmap.isNull():
                logger.error(
                    "Failed to load thumbnail - invalid image data",
                    extra={
                        'context': {
                            'product_id': self.product.id,
                            'file_path': str(file_path)
                        }
                    }
                )
                self._show_error("Invalid image")
                return
            
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            
            # Store original dimensions for tooltip
            self.setToolTip(
                f"Size: {self.product.width}x{self.product.height}\n"
                f"Format: {self.product.format}"
            )
            
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
            self._show_error("Error loading image")
    
    def _show_error(self, message: str):
        """Display error state."""
        self.setText(message)
        self.setStyleSheet(self.styleSheet() + """
            QLabel {
                color: #721c24;
                background-color: #f8d7da;
                border-color: #f5c6cb;
            }
        """)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.product is not None:
                try:
                    # Emit selection event
                    logger.debug(f"Selected product {self.product.id}")
                    event = ProductEvent(
                        event_type=ProductEventType.SELECTED,
                        product=self.product
                    )
                    ProductEventPublisher.publish_product_event(event)
                except Exception as e:
                    logger.error(f"Error handling product selection: {e}")
            else:
                logger.error("Product not available for thumbnail")
        super().mousePressEvent(event)
        
    def resizeEvent(self, event):
        """Handle resize events by rescaling the pixmap."""
        super().resizeEvent(event)
        if self.pixmap() and not self.pixmap().isNull():
            scaled_pixmap = self.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)