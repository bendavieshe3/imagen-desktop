"""Context menu for product thumbnails."""
from PyQt6.QtWidgets import QMenu, QMessageBox, QFileDialog
from PyQt6.QtGui import QClipboard, QPixmap
from pathlib import Path

from imagen_desktop.core.models.product import Product
from imagen_desktop.core.events.product_events import (
    ProductEvent, ProductEventType, ProductEventPublisher
)
from imagen_desktop.utils.debug_logger import logger

class ProductContextMenu(QMenu):
    """Context menu for product operations."""
    
    def __init__(self, product: Product, parent=None):
        super().__init__(parent)
        self.product = product
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
        self.delete_action.triggered.connect(self._delete_product)
    
    def _view_full_size(self):
        """Show product in full-size viewer."""
        from imagen_desktop.ui.features.gallery.dialogs.product_viewer import ProductViewer
        viewer = ProductViewer([self.product])
        viewer.exec()
    
    def _copy_to_clipboard(self):
        """Copy product to clipboard."""
        try:
            file_path = Path(self.product.file_path) if isinstance(self.product.file_path, str) else self.product.file_path
            clipboard = QClipboard()
            pixmap = QPixmap(str(file_path))
            clipboard.setPixmap(pixmap)
            logger.debug(f"Copied product {self.product.id} to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to copy image: {str(e)}"
            )
    
    def _save_as(self):
        """Save product to a new location."""
        file_path = Path(self.product.file_path) if isinstance(self.product.file_path, str) else self.product.file_path
        file_name = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(file_path.name),
            "Images (*.png *.jpg *.jpeg *.webp)"
        )[0]
        
        if file_name:
            try:
                import shutil
                shutil.copy2(file_path, file_name)
                logger.debug(f"Saved product {self.product.id} to {file_name}")
            except Exception as e:
                logger.error(f"Failed to save product: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save file: {str(e)}"
                )
    
    def _delete_product(self):
        """Delete product after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Create and emit delete event
                event = ProductEvent(
                    event_type=ProductEventType.DELETED,  
                    product=self.product
                )
                ProductEventPublisher.publish_product_event(event)
                logger.info(f"Deletion requested for product {self.product.id}")
            except Exception as e:
                logger.error(f"Failed to request product deletion: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete product: {str(e)}"
                )