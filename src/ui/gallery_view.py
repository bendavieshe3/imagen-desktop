from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QGridLayout, QMenu,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QClipboard
from pathlib import Path
from typing import List, Optional
from ..models.image_generation import ImageGenerationModel, GenerationMetadata
import shutil

class ImageThumbnail(QLabel):
    """Widget displaying a thumbnail of a generated image."""
    
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(QSize(200, 200))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f0f0f0;
            }
        """)
        self._load_image()
    
    def _load_image(self):
        """Load and display the image."""
        pixmap = QPixmap(str(self.image_path))
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

class GalleryView(QWidget):
    def __init__(self, image_model: ImageGenerationModel):
        super().__init__()
        self.image_model = image_model
        self._init_ui()
        self.refresh_gallery()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_gallery)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Scroll area for images
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(10)
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
    
    def refresh_gallery(self):
        """Refresh the gallery display."""
        # Clear existing thumbnails
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load generations
        generations = self.image_model.list_generations()
        
        # Add thumbnails to grid
        row = 0
        col = 0
        max_cols = 3
        
        for generation in generations:
            for image_path in generation.output_paths:
                if image_path.exists():
                    thumbnail = ImageThumbnail(image_path)
                    thumbnail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                    thumbnail.customContextMenuRequested.connect(
                        lambda pos, g=generation, p=image_path: self._show_context_menu(pos, g, p)
                    )
                    
                    self.grid_layout.addWidget(thumbnail, row, col)
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
        
        # Add stretch to bottom
        self.grid_layout.setRowStretch(row + 1, 1)
    
    def _show_context_menu(self, pos, generation: GenerationMetadata, image_path: Path):
        """Show context menu for an image."""
        menu = QMenu(self)
        
        # Add menu actions
        view_action = menu.addAction("View Full Size")
        copy_action = menu.addAction("Copy to Clipboard")
        save_action = menu.addAction("Save As...")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Show menu and handle selection
        action = menu.exec(self.sender().mapToGlobal(pos))
        
        if action == view_action:
            self._view_full_size(image_path)
        elif action == copy_action:
            self._copy_to_clipboard(image_path)
        elif action == save_action:
            self._save_as(image_path)
        elif action == delete_action:
            self._delete_image(generation, image_path)
    
    def _view_full_size(self, image_path: Path):
        """Open image in a new window at full size."""
        from .carousel_view import CarouselView
        viewer = CarouselView([image_path])
        viewer.show()
    
    def _copy_to_clipboard(self, image_path: Path):
        """Copy image to clipboard."""
        clipboard = QClipboard()
        pixmap = QPixmap(str(image_path))
        clipboard.setPixmap(pixmap)
    
    def _save_as(self, image_path: Path):
        """Save image to a new location."""
        file_name = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            str(Path.home() / image_path.name),
            "Images (*.png *.jpg *.jpeg)"
        )[0]
        
        if file_name:
            try:
                shutil.copy2(image_path, file_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def _delete_image(self, generation: GenerationMetadata, image_path: Path):
        """Delete an image from the gallery."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this image?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove the image path from generation metadata
                generation.output_paths.remove(image_path)
                
                # If this was the last image, delete the entire generation
                if not generation.output_paths:
                    self.image_model.delete_generation(generation.id)
                else:
                    # Update the generation metadata
                    self.image_model._save_metadata(generation)
                
                # Delete the actual file
                image_path.unlink()
                
                # Refresh the gallery
                self.refresh_gallery()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete image: {str(e)}")