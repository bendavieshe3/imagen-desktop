"""Grid layout for displaying image thumbnails."""
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import List

from .thumbnail import ImageThumbnail
from .context_menu import ThumbnailContextMenu

class ImageGrid(QWidget):
    """Grid layout for displaying thumbnails."""
    
    # Signals
    image_deleted = pyqtSignal(Path)  # Emitted when an image is deleted
    
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
    
    def set_images(self, image_paths: List[Path]):
        """Set the images to display in the grid."""
        # Clear existing thumbnails
        self.clear()
        
        # Add new thumbnails
        row = 0
        col = 0
        max_cols = 3
        
        for image_path in image_paths:
            if image_path.exists():
                thumbnail = ImageThumbnail(image_path)
                thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                thumbnail.customContextMenuRequested.connect(
                    lambda pos, p=image_path: self._show_context_menu(pos, p)
                )
                
                self.grid_layout.addWidget(thumbnail, row, col)
                self.thumbnails.append(thumbnail)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        # Add stretch to bottom
        self.grid_layout.setRowStretch(row + 1, 1)
    
    def clear(self):
        """Remove all thumbnails from the grid."""
        for thumbnail in self.thumbnails:
            thumbnail.deleteLater()
        self.thumbnails.clear()
        
        # Clear grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _show_context_menu(self, pos, image_path: Path):
        """Show context menu for a thumbnail."""
        menu = ThumbnailContextMenu(image_path, self)
        menu.image_deleted.connect(self.image_deleted.emit)
        menu.exec(self.sender().mapToGlobal(pos))