"""Main gallery view for displaying generated images."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox
)

from ..models.image_generation import ImageGenerationModel
from .gallery.grid_view import ImageGrid
from .gallery.gallery_presenter import GalleryPresenter
from ..utils.debug_logger import logger

class GalleryView(QWidget):
    """Main gallery view combining grid and controls."""
    
    def __init__(self, 
                 image_model: ImageGenerationModel,
                 product_repository=None):
        super().__init__()
        
        # Initialize presenter
        self.presenter = GalleryPresenter(
            image_model=image_model,
            product_repository=product_repository
        )
        
        self._init_ui()
        self._connect_signals()
        self.refresh_gallery()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_gallery)
        controls_layout.addWidget(self.refresh_button)
        
        # Sort options (if using database)
        if self.presenter.product_repository:
            self.sort_combo = QComboBox()
            self.sort_combo.addItems([
                "Most Recent",
                "Oldest First",
                "Largest Files",
                "Smallest Files"
            ])
            self.sort_combo.currentTextChanged.connect(self.refresh_gallery)
            controls_layout.addWidget(QLabel("Sort by:"))
            controls_layout.addWidget(self.sort_combo)
        
        # Status label
        self.status_label = QLabel()
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Image grid
        self.image_grid = ImageGrid()
        layout.addWidget(self.image_grid)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.image_grid.image_deleted.connect(self._handle_image_deleted)
    
    def refresh_gallery(self):
        """Refresh the gallery display."""
        image_paths = self.presenter.list_images()
        
        # Update grid
        self.image_grid.set_images(image_paths)
        
        # Update status
        self.status_label.setText(f"{len(image_paths)} images")
        logger.debug(f"Refreshed gallery with {len(image_paths)} images")
    
    def _handle_image_deleted(self, image_path):
        """Handle image deletion."""
        if self.presenter.delete_image(image_path):
            logger.debug(f"Successfully deleted {image_path}")
            # Refresh the gallery to reflect changes
            self.refresh_gallery()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Delete Failed",
                f"Failed to delete {image_path}. Please check logs for details."
            )