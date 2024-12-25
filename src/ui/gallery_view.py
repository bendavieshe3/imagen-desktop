"""Main gallery view for displaying generated images."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)

from ..models.image_generation import ImageGenerationModel
from .gallery.grid_view import ImageGrid

class GalleryView(QWidget):
    """Main gallery view combining grid and controls."""
    
    def __init__(self, image_model: ImageGenerationModel):
        super().__init__()
        self.image_model = image_model
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
        generations = self.image_model.list_generations()
        
        # Collect all valid image paths
        image_paths = []
        for generation in generations:
            image_paths.extend([
                path for path in generation.output_paths
                if path.exists()
            ])
        
        # Update grid
        self.image_grid.set_images(image_paths)
        
        # Update status
        self.status_label.setText(f"{len(image_paths)} images")
    
    def _handle_image_deleted(self, image_path):
        """Handle image deletion."""
        # Refresh the gallery to reflect changes
        self.refresh_gallery()