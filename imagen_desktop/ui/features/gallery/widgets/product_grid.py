"""Grid layout for displaying product thumbnails."""
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt

from imagen_desktop.ui.shared.widgets.base_product_display import BaseProductDisplay
from imagen_desktop.ui.shared.widgets.product_thumbnail import ProductThumbnail
from imagen_desktop.utils.debug_logger import logger

class ProductGrid(BaseProductDisplay):
    """Grid layout for product thumbnails."""
    
    def __init__(self):
        super().__init__()
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 3
    
    def _create_layout(self) -> QGridLayout:
        """Create grid layout for thumbnails."""
        layout = QGridLayout()
        layout.setSpacing(10)
        return layout
    
    def _add_to_layout(self, thumbnail: ProductThumbnail, position=None):
        """Add thumbnail to grid layout."""
        if position is not None:
            # Calculate row and column from position
            row = position // self.max_cols
            col = position % self.max_cols
        else:
            row = self.current_row
            col = self.current_col
            
            # Update next position
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1
        
        self.content_layout.addWidget(thumbnail, row, col)
        
        # Add stretch to bottom
        if row > 0:
            self.content_layout.setRowStretch(row + 1, 1)
    
    def _clear_layout(self):
        """Clear the grid layout."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.current_row = 0
        self.current_col = 0
        
        # Reset row stretches
        for i in range(self.content_layout.rowCount()):
            self.content_layout.setRowStretch(i, 0)