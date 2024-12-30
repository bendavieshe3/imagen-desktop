"""Base widget for displaying product thumbnails."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List

from imagen_desktop.core.models.product import Product
from imagen_desktop.ui.features.gallery.widgets.product_thumbnail import ProductThumbnail
from imagen_desktop.utils.debug_logger import logger

class BaseProductDisplay(QWidget):
    """Base class for product thumbnail displays."""
    
    # Signals
    product_clicked = pyqtSignal(Product)
    product_deleted = pyqtSignal(Product)
    
    def __init__(self):
        super().__init__()
        self.thumbnails = []
        self._init_base_ui()
        
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
    
    def _create_layout(self):
        """Create the layout for thumbnails. Override in subclasses."""
        raise NotImplementedError
    
    def _add_thumbnail(self, product: Product, position=None):
        """Add a thumbnail to the layout."""
        thumbnail = ProductThumbnail(product)
        thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        thumbnail.customContextMenuRequested.connect(
            lambda pos, p=product: self._show_context_menu(pos, p)
        )
        thumbnail.clicked.connect(self.product_clicked.emit)
        
        self._add_to_layout(thumbnail, position)
        self.thumbnails.append(thumbnail)
        
    def _add_to_layout(self, thumbnail: ProductThumbnail, position=None):
        """Add thumbnail to layout. Override in subclasses."""
        raise NotImplementedError
    
    def _show_context_menu(self, pos, product: Product):
        """Show context menu for a thumbnail."""
        from .product_context_menu import ProductContextMenu
        menu = ProductContextMenu(product, self)
        menu.product_deleted.connect(self.product_deleted.emit)
        menu.exec(self.sender().mapToGlobal(pos))
    
    def set_products(self, products: List[Product]):
        """Set the products to display."""
        self.clear()
        for product in products:
            self._add_thumbnail(product)
        logger.debug(f"Added {len(self.thumbnails)} products to display")
    
    def add_product(self, product: Product, position=None):
        """Add a single product."""
        if product.file_path.exists():
            self._add_thumbnail(product, position)
    
    def clear(self):
        """Remove all thumbnails."""
        for thumbnail in self.thumbnails:
            thumbnail.deleteLater()
        self.thumbnails.clear()
        
        # Clear layout (implementation specific)
        self._clear_layout()