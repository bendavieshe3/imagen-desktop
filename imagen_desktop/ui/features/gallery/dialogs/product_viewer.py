"""Dialog for viewing products at full size."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QScrollArea, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from typing import List
from pathlib import Path
import shutil

from imagen_desktop.core.models.product import Product
from imagen_desktop.utils.debug_logger import logger

class ProductViewer(QDialog):
    """Full-size product viewer with navigation."""
    
    def __init__(self, products: List[Product], current_index: int = 0, parent=None):
        super().__init__(parent)
        self.products = products
        self.current_index = current_index
        
        self.setWindowTitle("Product Viewer")
        self.setModal(True)
        self.resize(1024, 768)
        
        self._init_ui()
        self._show_current_product()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Image display area with scroll support
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # Info display
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Navigation and action buttons
        button_layout = QHBoxLayout()
        
        # Navigation
        self.prev_button = QPushButton("← Previous")
        self.prev_button.clicked.connect(self._show_previous)
        button_layout.addWidget(self.prev_button)
        
        button_layout.addStretch()
        
        # Action buttons
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        save_button = QPushButton("Save As...")
        save_button.clicked.connect(self._save_as)
        button_layout.addWidget(save_button)
        
        button_layout.addStretch()
        
        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self._show_next)
        button_layout.addWidget(self.next_button)
        
        layout.addLayout(button_layout)
        
        # Update button states
        self._update_button_states()
    
    def _show_current_product(self):
        """Display the current product."""
        if 0 <= self.current_index < len(self.products):
            product = self.products[self.current_index]
            file_path = Path(product.file_path) if isinstance(product.file_path, str) else product.file_path
            
            if file_path.exists():
                pixmap = QPixmap(str(file_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self._update_info_label(product)
                else:
                    self.image_label.setText("Error loading image")
                    logger.error(f"Failed to load image for product {product.id}")
            else:
                self.image_label.setText("Image file not found")
                logger.error(f"Image file not found: {file_path}")
    
    def _update_info_label(self, product: Product):
        """Update the information label."""
        info_text = f"Product {self.current_index + 1} of {len(self.products)} | "
        if product.width and product.height:
            info_text += f"Size: {product.width}x{product.height} | "
        info_text += f"Format: {product.format or 'Unknown'}"
        self.info_label.setText(info_text)
    
    def _show_previous(self):
        """Show the previous product."""
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current_product()
            self._update_button_states()
    
    def _show_next(self):
        """Show the next product."""
        if self.current_index < len(self.products) - 1:
            self.current_index += 1
            self._show_current_product()
            self._update_button_states()
    
    def _update_button_states(self):
        """Update the enabled state of navigation buttons."""
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.products) - 1)
    
    def _copy_to_clipboard(self):
        """Copy current image to clipboard."""
        if 0 <= self.current_index < len(self.products):
            try:
                from PyQt6.QtGui import QGuiApplication
                clipboard = QGuiApplication.clipboard()
                product = self.products[self.current_index]
                file_path = Path(product.file_path) if isinstance(product.file_path, str) else product.file_path
                pixmap = QPixmap(str(file_path))
                clipboard.setPixmap(pixmap)
                logger.debug(f"Copied product {product.id} to clipboard")
            except Exception as e:
                logger.error(f"Failed to copy to clipboard: {e}")
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Failed to copy image: {str(e)}")
    
    def _save_as(self):
        """Save current image to a new location."""
        if 0 <= self.current_index < len(self.products):
            product = self.products[self.current_index]
            file_path = Path(product.file_path) if isinstance(product.file_path, str) else product.file_path
            
            file_name = QFileDialog.getSaveFileName(
                self,
                "Save Image As",
                str(file_path.name),
                "Images (*.png *.jpg *.jpeg *.webp)"
            )[0]
            
            if file_name:
                try:
                    shutil.copy2(file_path, file_name)
                    logger.debug(f"Saved product {product.id} to {file_name}")
                except Exception as e:
                    logger.error(f"Failed to save image: {e}")
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self._show_current_product()
    
    def keyPressEvent(self, event):
        """Handle keyboard navigation."""
        if event.key() == Qt.Key.Key_Left:
            self._show_previous()
        elif event.key() == Qt.Key.Key_Right:
            self._show_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)