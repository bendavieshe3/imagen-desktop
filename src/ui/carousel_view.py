from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QScrollArea, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QClipboard
from pathlib import Path
from typing import List
import shutil

class CarouselView(QDialog):
    def __init__(self, image_paths: List[Path], current_index: int = 0, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.current_index = current_index
        
        self.setWindowTitle("Image Viewer")
        self.setModal(True)
        self.resize(1024, 768)
        
        self._init_ui()
        self._show_current_image()
    
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
        self._update_info_label()
    
    def _show_current_image(self):
        """Display the current image."""
        if 0 <= self.current_index < len(self.image_paths):
            pixmap = QPixmap(str(self.image_paths[self.current_index]))
            
            # Scale pixmap if larger than screen
            available_size = self.image_label.size()
            scaled_pixmap = pixmap.scaled(
                available_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            self._update_info_label()
    
    def _update_info_label(self):
        """Update the information label."""
        if 0 <= self.current_index < len(self.image_paths):
            current_image = self.image_paths[self.current_index]
            pixmap = QPixmap(str(current_image))
            info_text = f"Image {self.current_index + 1} of {len(self.image_paths)} | "
            info_text += f"Size: {pixmap.width()}x{pixmap.height()} | "
            info_text += f"File: {current_image.name}"
            self.info_label.setText(info_text)
    
    def _show_previous(self):
        """Show the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current_image()
            self._update_button_states()
    
    def _show_next(self):
        """Show the next image."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self._show_current_image()
            self._update_button_states()
    
    def _update_button_states(self):
        """Update the enabled state of navigation buttons."""
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.image_paths) - 1)
    
    def _copy_to_clipboard(self):
        """Copy current image to clipboard."""
        if 0 <= self.current_index < len(self.image_paths):
            clipboard = QClipboard()
            pixmap = QPixmap(str(self.image_paths[self.current_index]))
            clipboard.setPixmap(pixmap)
    
    def _save_as(self):
        """Save current image to a new location."""
        if 0 <= self.current_index < len(self.image_paths):
            current_image = self.image_paths[self.current_index]
            file_name = QFileDialog.getSaveFileName(
                self,
                "Save Image As",
                str(Path.home() / current_image.name),
                "Images (*.png *.jpg *.jpeg)"
            )[0]
            
            if file_name:
                try:
                    shutil.copy2(current_image, file_name)
                except Exception as e:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self._show_current_image()  # Rescale image when window is resized
    
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