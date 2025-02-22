"""Main gallery view for displaying generated images."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QMessageBox
)

from imagen_desktop.ui.features.gallery.widgets.product_grid import ProductGrid
from imagen_desktop.ui.features.gallery.gallery_presenter import GalleryPresenter
from imagen_desktop.ui.features.gallery.dialogs.product_viewer import ProductViewer
from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.core.events.product_events import (
    ProductEvent, ProductEventType, ProductEventPublisher
)
from imagen_desktop.data.repositories.product_repository import ProductRepository
from imagen_desktop.utils.debug_logger import logger

class GalleryView(QWidget):
    """Main gallery view combining grid and controls."""
    
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
        """Connect signals and events."""
        self.refresh_button.clicked.connect(self.refresh_gallery)
        self.sort_combo.currentTextChanged.connect(self.refresh_gallery)
        
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
    
    def _handle_product_event(self, event: ProductEvent):
        """Handle product-related events."""
        logger.debug(f"Gallery received product event: {event.event_type}")
        
        if event.event_type == ProductEventType.CREATED:
            # Refresh gallery to show new product
            self.refresh_gallery()
            self.status_label.setText("New product added")
            
        elif event.event_type == ProductEventType.SELECTED:
            self._show_product_viewer(event.data.product)
            
        elif event.event_type == ProductEventType.DELETED:
            self.refresh_gallery()
            self.status_label.setText("Product deleted successfully")
            
        elif event.event_type == ProductEventType.ERROR:
            QMessageBox.warning(
                self,
                "Operation Failed",
                f"Operation failed: {event.data.error}"
            )
    
    def _show_product_viewer(self, product: Product):
        """Show the product viewer dialog."""
        viewer = ProductViewer([product], parent=self)
        viewer.exec()
    
    def showEvent(self, event):
        """Handle view becoming visible."""
        super().showEvent(event)
        # Refresh when view becomes visible
        self.refresh_gallery()
    
    def closeEvent(self, event):
        """Handle view closure."""
        ProductEventPublisher.unsubscribe_from_products(self._handle_product_event)
        super().closeEvent(event)