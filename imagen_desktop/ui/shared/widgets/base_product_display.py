"""Base widget for displaying product thumbnails."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from typing import List
from pathlib import Path

from imagen_desktop.core.models.product import Product
from imagen_desktop.core.events.product_events import ProductEvent, ProductEventType, ProductEventPublisher
from imagen_desktop.ui.shared.widgets.product_thumbnail import ProductThumbnail
from imagen_desktop.utils.debug_logger import logger

class BaseProductDisplay(QWidget):
    """Base class for product thumbnail displays."""
    
    def __init__(self):
        super().__init__()
        self.thumbnails = []
        self._init_base_ui()
        self._connect_events()
    
    def _init_base_ui(self):
        """Initialize base UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create content widget
        self.scroll_content = QWidget()
        self.content_layout = self._create_layout()
        self.scroll_content.setLayout(self.content_layout)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
    
    def _connect_events(self):
        """Subscribe to product events."""
        ProductEventPublisher.subscribe_to_products(self._handle_product_event)
    
    def _handle_product_event(self, event: ProductEvent):
        """Handle product-related events."""
        if event.event_type == ProductEventType.DELETED:
            self._handle_product_deleted(event.data.product)
        elif event.event_type == ProductEventType.ERROR:
            logger.error(
                f"Product operation failed: {event.data.error}",
                extra={'context': {'product_id': event.data.product.id}}
            )
    
    def _handle_product_deleted(self, product: Product):
        """Handle product deletion."""
        # Find and remove thumbnail
        for thumbnail in self.thumbnails[:]:  # Copy list for safe removal
            if thumbnail.product.id == product.id:
                thumbnail.deleteLater()
                self.thumbnails.remove(thumbnail)
                logger.debug(f"Removed thumbnail for product {product.id}")
                break
    
    def _create_layout(self):
        """Create the layout for thumbnails. Override in subclasses."""
        raise NotImplementedError
    
    def _add_to_layout(self, thumbnail: ProductThumbnail, position=None):
        """Add thumbnail to layout. Override in subclasses."""
        raise NotImplementedError
    
    def _add_thumbnail(self, product: Product, position=None):
        """Add a thumbnail to the layout."""
        thumbnail = ProductThumbnail(product)
        thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        thumbnail.customContextMenuRequested.connect(
            lambda pos, p=product: self._show_context_menu(pos, p)
        )
        
        self._add_to_layout(thumbnail, position)
        self.thumbnails.append(thumbnail)
        
    def _show_context_menu(self, pos, product: Product):
        """Show context menu for a thumbnail."""
        from imagen_desktop.ui.shared.widgets.product_context_menu import ProductContextMenu
        menu = ProductContextMenu(product, self)
        menu.exec(self.sender().mapToGlobal(pos))
    
    def set_products(self, products: List[Product]):
        """Set the products to display."""
        self.clear()
        for product in products:
            file_path = Path(product.file_path)
            if file_path.exists():
                self._add_thumbnail(product)
        logger.debug(f"Added {len(self.thumbnails)} products to display")
    
    def add_product(self, product: Product, position=None):
        """Add a single product."""
        file_path = Path(product.file_path)
        if file_path.exists():
            self._add_thumbnail(product, position)
    
    def clear(self):
        """Remove all thumbnails."""
        for thumbnail in self.thumbnails:
            thumbnail.deleteLater()
        self.thumbnails.clear()
        
        # Clear layout (implementation specific)
        self._clear_layout()
    
    def _clear_layout(self):
        """Clear the layout. Override in subclasses."""
        raise NotImplementedError
        
    def closeEvent(self, event):
        """Clean up event subscriptions."""
        ProductEventPublisher.unsubscribe_from_products(self._handle_product_event)
        super().closeEvent(event)