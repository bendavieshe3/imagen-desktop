"""Horizontal strip layout for displaying product thumbnails."""
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtCore import Qt
from typing import Optional

from .base_product_display import BaseProductDisplay
from .product_thumbnail import ProductThumbnail
from utils.debug_logger import logger

class ProductStrip(BaseProductDisplay):
    """Horizontal strip layout for products."""
    
    def __init__(self, max_thumbnails: int = 50):
        self.max_thumbnails = max_thumbnails
        super().__init__()
        
        # Configure scroll area for horizontal scrolling
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMaximumHeight(220)  # Fixed height for strip
    
    def _create_layout(self) -> QHBoxLayout:
        """Create horizontal layout for thumbnails."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addStretch()  # Keep thumbnails left-aligned
        return layout
    
    def _add_to_layout(self, thumbnail: ProductThumbnail, position: Optional[int] = None):
        """Add thumbnail to strip at position or start."""
        # Remove oldest thumbnail if at limit
        if len(self.thumbnails) >= self.max_thumbnails:
            oldest = self.thumbnails.pop()
            oldest.deleteLater()
        
        # Add at position or start
        insert_pos = position if position is not None else 0
        self.content_layout.insertWidget(insert_pos, thumbnail)
        
        # Scroll to show new thumbnail
        if insert_pos == 0:
            self.scroll.horizontalScrollBar().setValue(0)
    
    def _clear_layout(self):
        """Clear the strip layout."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Re-add the stretch
        self.content_layout.addStretch()