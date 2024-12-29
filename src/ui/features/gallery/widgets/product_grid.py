"""Grid layout for displaying product thumbnails."""
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import List

from .product_thumbnail import ProductThumbnail
from .product_context_menu import ProductContextMenu
from core.models.product import Product
from utils.debug_logger import logger

class ProductGrid(QWidget):
    """Grid layout for displaying product thumbnails."""
    
    # Signals
    product_clicked = pyqtSignal(Product)  # Emitted when thumbnail clicked
    product_deleted = pyqtSignal(Product)  # Emitted when product deleted
    
    def __init__(self):
        super().__init__()
        self.thumbnails = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget for scroll area
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(10)
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
    
    def set_products(self, products: List[Product]):
        """Set the products to display in the grid."""
        # Clear existing thumbnails
        self.clear()
        
        # Add new thumbnails
        row = 0
        col = 0
        max_cols = 3
        
        for product in products:
            if product.file_path.exists():
                thumbnail = ProductThumbnail(product)
                thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                thumbnail.customContextMenuRequested.connect(
                    lambda pos, p=product: self._show_context_menu(pos, p)
                )
                thumbnail.clicked.connect(
                    lambda p=product: self.product_clicked.emit(p)
                )
                
                self.grid_layout.addWidget(thumbnail, row, col)
                self.thumbnails.append(thumbnail)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        # Add stretch to bottom
        self.grid_layout.setRowStretch(row + 1, 1)
        logger.debug(f"Added {len(self.thumbnails)} products to grid")
    
    def clear(self):
        """Remove all thumbnails."""
        for thumbnail in self.thumbnails:
            thumbnail.deleteLater()
        self.thumbnails.clear()
        
        # Clear grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _show_context_menu(self, pos, product: Product):
        """Show context menu for a thumbnail."""
        menu = ProductContextMenu(product, self)
        menu.product_deleted.connect(self.product_deleted.emit)
        menu.exec(self.sender().mapToGlobal(pos))