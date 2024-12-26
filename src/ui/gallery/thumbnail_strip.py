"""Horizontal strip of image thumbnails."""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import List

from .thumbnail import ImageThumbnail
from .context_menu import ThumbnailContextMenu

class ThumbnailStrip(QWidget):
    """Horizontal scrolling strip of thumbnails."""
    
    image_clicked = pyqtSignal(Path)  # Emitted when thumbnail is clicked
    image_deleted = pyqtSignal(Path)  # Emitted when image is deleted
    
    def __init__(self):
        super().__init__()
        self.thumbnails = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Create content widget
        self.scroll_content = QWidget()
        self.strip_layout = QHBoxLayout(self.scroll_content)
        self.strip_layout.setSpacing(10)
        self.strip_layout.addStretch()
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
    
    def add_image(self, image_path: Path):
        """Add a new image to the strip."""
        if image_path.exists():
            thumbnail = ImageThumbnail(image_path)
            thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            thumbnail.customContextMenuRequested.connect(
                lambda pos, p=image_path: self._show_context_menu(pos, p)
            )
            thumbnail.mousePressEvent = lambda e, p=image_path: self._handle_click(e, p)
            
            # Insert before the stretch
            self.strip_layout.insertWidget(len(self.thumbnails), thumbnail)
            self.thumbnails.append(thumbnail)
    
    def clear(self):
        """Remove all thumbnails."""
        for thumbnail in self.thumbnails:
            thumbnail.deleteLater()
        self.thumbnails.clear()
        
        # Reset layout (keep the stretch)
        while self.strip_layout.count() > 1:
            item = self.strip_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _show_context_menu(self, pos, image_path: Path):
        """Show context menu for a thumbnail."""
        menu = ThumbnailContextMenu(image_path, self)
        menu.image_deleted.connect(self.image_deleted.emit)
        menu.exec(self.sender().mapToGlobal(pos))
    
    def _handle_click(self, event, image_path: Path):
        """Handle thumbnail click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.image_clicked.emit(image_path)