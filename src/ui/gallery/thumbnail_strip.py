"""Horizontal strip of image thumbnails."""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import List, Optional

from .thumbnail import ImageThumbnail
from .context_menu import ThumbnailContextMenu

class ThumbnailStrip(QWidget):
    """Horizontal scrolling strip of thumbnails."""
    
    image_clicked = pyqtSignal(Path)  # Emitted when thumbnail is clicked
    image_deleted = pyqtSignal(Path)  # Emitted when image is deleted
    
    def __init__(self, max_thumbnails: int = 50):
        super().__init__()
        self.max_thumbnails = max_thumbnails
        self.thumbnails = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Create content widget
        self.scroll_content = QWidget()
        self.strip_layout = QHBoxLayout(self.scroll_content)
        self.strip_layout.setSpacing(10)
        self.strip_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
    
    def add_image(self, image_path: Path):
        """Add a new image to the start of the strip."""
        if image_path.exists():
            thumbnail = ImageThumbnail(image_path)
            thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            thumbnail.customContextMenuRequested.connect(
                lambda pos, p=image_path: self._show_context_menu(pos, p)
            )
            thumbnail.mousePressEvent = lambda e, p=image_path: self._handle_click(e, p)
            
            # Insert at the start, before existing thumbnails
            self.strip_layout.insertWidget(0, thumbnail)
            self.thumbnails.insert(0, thumbnail)
            
            # Remove oldest thumbnails if over limit
            while len(self.thumbnails) > self.max_thumbnails:
                oldest = self.thumbnails.pop()
                oldest.deleteLater()
            
            # Scroll to show new thumbnail
            self.scroll.horizontalScrollBar().setValue(0)
    
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