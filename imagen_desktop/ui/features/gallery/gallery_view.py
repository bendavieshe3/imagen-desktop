"""Main gallery view for displaying generated images."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import pyqtSignal

from imagen_desktop.ui.features.gallery.widgets.product_grid import ProductGrid
from imagen_desktop.ui.features.gallery.gallery_presenter import GalleryPresenter
from imagen_desktop.ui.features.gallery.dialogs.product_viewer import ProductViewer
from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.core.events.product_events import ProductEventPublisher, ProductEvent, ProductEventType
from imagen_desktop.data.repositories.product_repository import ProductRepository
from imagen_desktop.utils.debug_logger import logger

class GalleryView(QWidget):
    """Main gallery view combining grid and controls."""
    
    product_selected = pyqtSignal(Product)
    
    def __init__(self, product_repository: ProductRepository):
        super().__init__()
        
        # Initialize presenter
        self.presenter = GalleryPresenter(
            product_repository=product_repository,
            view=self
        )
        
        self._init_ui()
        self._connect_signals()
        self.refresh_gallery()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Controls bar
        controls_layout = QHBoxLayout()
        
        # Sort options
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Most Recent",
            "Oldest First",
            "Largest Files",
            "Smallest Files"
        ])
        controls_layout.addWidget(QLabel("Sort by:"))
        controls_layout.addWidget(self.sort_combo)
        
        # Status label
        self.status_label = QLabel()
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        controls_layout.addWidget(self.refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Product grid
        self.product_grid = ProductGrid()
        layout.addWidget(self.product_grid)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.refresh_button.clicked.connect(self.refresh_gallery)
        self.sort_combo.currentTextChanged.connect(self.refresh_gallery)
        
        # Product grid signals
        self.product_grid.product_clicked.connect(self._show_product_viewer)
        self.product_grid.product_deleted.connect(self._handle_product_deleted)
        
        # Subscribe to product events
        ProductEventPublisher.subscribe_to_products(self._handle_product_event)
    
    def refresh_gallery(self):
        """Refresh the gallery display."""
        # Get current sort option
        sort_by = self.sort_combo.currentText()
        
        # Get products from presenter
        products = self.presenter.list_products(
            product_type=ProductType.IMAGE,
            sort_by=sort_by
        )
        
        # Update grid
        self.product_grid.set_products(products)
        
        # Update status
        self.status_label.setText(f"{len(products)} products")
        logger.debug(f"Refreshed gallery with {len(products)} products")
    
    def _show_product_viewer(self, product: Product):
        """Show the product viewer dialog."""
        viewer = ProductViewer([product], parent=self)
        viewer.exec()
    
    def _handle_product_deleted(self, product: Product):
        """Handle product deletion."""
        if self.presenter.delete_product(product.file_path):
            self.status_label.setText("Product deleted successfully")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Delete Failed",
                f"Failed to delete product {product.id}. Please check logs for details."
            )
    
    def _handle_product_event(self, event: ProductEvent):
        """Handle product-related events."""
        if event.event_type in [ProductEventType.CREATED, ProductEventType.DELETED]:
            self.refresh_gallery()
    
    def closeEvent(self, event):
        """Handle view closure."""
        # Unsubscribe from events
        ProductEventPublisher.unsubscribe_from_products(self._handle_product_event)
        super().closeEvent(event)