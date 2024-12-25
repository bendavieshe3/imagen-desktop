"""Context menu for gallery thumbnails."""
from PyQt6.QtWidgets import QMenu, QMessageBox, QFileDialog
from PyQt6.QtGui import QClipboard, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import shutil

from .carousel_view import CarouselView

class ThumbnailContextMenu(QMenu):
    """Context menu for thumbnail operations."""
    
    # Signals
    image_deleted = pyqtSignal(Path)  # Emitted when image is deleted
    
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._init_actions()
    
    def _init_actions(self):
        """Initialize menu actions."""
        # View action
        self.view_action = self.addAction("View Full Size")
        self.view_action.triggered.connect(self._view_full_size)
        
        # Copy action
        self.copy_action = self.addAction("Copy to Clipboard")
        self.copy_action.triggered.connect(self._copy_to_clipboard)
        
        # Save action
        self.save_action = self.addAction("Save As...")
        self.save_action.triggered.connect(self._save_as)
        
        self.addSeparator()
        
        # Delete action
        self.delete_action = self.addAction("Delete")
        self.delete_action.triggered.connect(self._delete_image)
    
    def _view_full_size(self):
        """Open image in full-size viewer."""
        viewer = CarouselView([self.image_path])
        viewer.exec()  # Use exec() instead of show() for modal dialog
    
    def _copy_to_clipboard(self):
        """Copy image to clipboard."""
        try:
            clipboard = QClipboard()
            pixmap = QPixmap(str(self.image_path))
            clipboard.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to copy image: {str(e)}"
            )
    
    def _save_as(self):
        """Save image to a new location."""
        file_name = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            str(Path.home() / self.image_path.name),
            "Images (*.png *.jpg *.jpeg *.webp)"
        )[0]
        
        if file_name:
            try:
                shutil.copy2(self.image_path, file_name)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save image: {str(e)}"
                )
    
    def _delete_image(self):
        """Delete image after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this image?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.image_path.exists():
                    self.image_path.unlink()
                    self.image_deleted.emit(self.image_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete image: {str(e)}"
                )