"""Main form for image generation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Any

from imagen_desktop.ui.features.generation.forms.generation_sidebar import GenerationSidebar
from imagen_desktop.ui.features.generation.forms.output_display import OutputDisplay
from imagen_desktop.ui.features.gallery.widgets.product_strip import ProductStrip
from imagen_desktop.core.models.product import Product
from imagen_desktop.core.events.product_events import (
    ProductEvent, ProductEventType, ProductEventPublisher
)
from imagen_desktop.utils.debug_logger import logger

class GenerationForm(QWidget):
    """Main generation interface combining sidebar, output display, and thumbnail strip."""
    
    generation_requested = pyqtSignal(str, dict)  # model_id, parameters
    
    def __init__(self, api_handler, model_repository=None):
        super().__init__()
        self.api_handler = api_handler
        self.model_repository = model_repository
        self.current_prediction_id = None
        self._init_ui()
        self._connect_signals()
        ProductEventPublisher.subscribe_to_products(self._handle_product_event)
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Create splitter for sidebar and output area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left sidebar
        self.sidebar = GenerationSidebar(
            self.api_handler,
            model_repository=self.model_repository
        )
        self.sidebar.setMaximumWidth(400)
        splitter.addWidget(self.sidebar)
        
        # Output display
        self.output_display = OutputDisplay()
        splitter.addWidget(self.output_display)
        
        # Set initial splitter sizes (30% sidebar, 70% output)
        splitter.setSizes([30, 70])
        
        content_layout.addWidget(splitter)
        layout.addLayout(content_layout)
        
        # Product thumbnail strip
        self.product_strip = ProductStrip()
        self.product_strip.setMinimumHeight(220)
        self.product_strip.setMaximumHeight(220)
        layout.addWidget(self.product_strip)
    
    def _connect_signals(self):
        """Connect internal signals."""
        # Connect sidebar signals
        self.sidebar.generation_requested.connect(self.generation_requested.emit)
        
        # Connect API handler signals
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
        self.api_handler.generation_canceled.connect(self._on_generation_canceled)
    
    def _handle_product_event(self, event: ProductEvent):
        """Handle product events."""
        if event.event_type == ProductEventType.SELECTED:
            self._on_product_clicked(event.data.product)
    
    def _on_product_clicked(self, product: Product):
        """Handle product selection."""
        self.output_display.display_image(product.file_path)
    
    def _update_ui_state(self, generating: bool):
        """Update UI elements based on generation state."""
        self.sidebar.set_enabled(not generating)
        self.output_display.show_progress(generating)
    
    def _on_generation_started(self, prediction_id: str):
        """Handle generation started signal."""
        self.current_prediction_id = prediction_id
        self.output_display.set_status("Generating image...")
        self.output_display.show_progress(True)
        self._update_ui_state(True)
    
    def _on_generation_completed(self, prediction_id: str, products: List[Product]):
        """Handle generation completed signal."""
        if prediction_id != self.current_prediction_id:
            return

        self.output_display.set_status("Generation complete!")
        self.output_display.show_progress(False)
        self._update_ui_state(False)
        
        # Update displays with products
        for product in products:
            self.product_strip.add_product(product)
            
        # Show latest product in output display
        if products:
            self.output_display.display_image(products[-1].file_path)
        
        self.current_prediction_id = None
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failure."""
        if prediction_id != self.current_prediction_id:
            return
            
        self.output_display.set_status(f"Generation failed: {error}")
        self.output_display.show_progress(False)
        self._update_ui_state(False)
        self.current_prediction_id = None
    
    def _on_generation_canceled(self, prediction_id: str):
        """Handle generation cancellation."""
        if prediction_id != self.current_prediction_id:
            return
            
        self.output_display.set_status("Generation canceled")
        self.output_display.show_progress(False)
        self._update_ui_state(False)
        self.current_prediction_id = None
    
    def closeEvent(self, event):
        """Handle view closure."""
        ProductEventPublisher.unsubscribe_from_products(self._handle_product_event)
        super().closeEvent(event)