"""Main window presenter coordinating other presenters."""
from typing import Optional, Any, List
from pathlib import Path
import requests
from sqlalchemy.orm import sessionmaker
from PIL import Image

from ..core.models.product import Product, ProductType
from ..models.image_generation import ImageGenerationModel
from ..api.api_handler import APIHandler
from ..data.image_repository import ImageRepository
from ..data.repositories.model_repository import ModelRepository
from ..data.repositories.model_query_repository import ModelQueryRepository
from ..data.repositories.product_repository import ProductRepository
from .presenters import GenerationPresenter
from ..utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class MainWindowPresenter:
    """Coordinates functionality between different presenters."""
    
    def __init__(self, 
                 session_factory: Optional[sessionmaker] = None,
                 view = None):
        """Initialize the presenter with optional database support."""
        self.view = view
        
        # Initialize core components
        logger.debug("Initializing MainWindow components")
        self.image_model = ImageGenerationModel()
        self.api_handler = APIHandler(image_model=self.image_model)
        
        # Initialize repositories
        if session_factory:
            self.image_repository = ImageRepository(session_factory)
            self.model_repository = ModelRepository(session_factory)
            self.model_query_repository = ModelQueryRepository(session_factory)
            self.product_repository = ProductRepository(session_factory)
            logger.info("Database repositories initialized")
        else:
            self.image_repository = None
            self.model_repository = None
            self.model_query_repository = None
            self.product_repository = None
            logger.warning("Database storage not available")
        
        # Initialize feature presenters
        self.generation_presenter = GenerationPresenter(
            api_handler=self.api_handler,
            product_repository=self.product_repository,
            view=self.view
        )
        
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect API handler signals."""
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
    
    def start_generation(self, model: str, params: dict) -> str:
        """Start a new image generation."""
        return self.generation_presenter.start_generation(model, params)
    
    def _save_output_and_create_product(self, output: Any, prediction_id: str) -> Optional[Product]:
        """Save generation output to file and create product record."""
        try:
            output_dir = Path.home() / '.replicate-desktop' / 'products'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Handle FileOutput objects from Replicate
            if hasattr(output, 'read'):
                data = output.read()
            elif hasattr(output, 'url'):
                # Download from URL
                response = requests.get(output.url)
                response.raise_for_status()
                data = response.content
            else:
                # Assume string URL
                response = requests.get(str(output))
                response.raise_for_status()
                data = response.content
            
            # Save to unique file
            import uuid
            file_path = output_dir / f"{uuid.uuid4()}.png"
            with open(file_path, 'wb') as f:
                f.write(data)
            
            # Create product if repository available
            if self.product_repository:
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        format = img.format.lower() if img.format else None
                        
                    product = self.product_repository.create_product(
                        file_path=file_path,
                        generation_id=prediction_id,
                        width=width,
                        height=height,
                        format=format,
                        product_type=ProductType.IMAGE
                    )
                    if product:
                        return product
                        
                except Exception as e:
                    logger.error(f"Failed to create product record: {e}")
                    
            return None
            
        except Exception as e:
            logger.error("Failed to save output file", extra={'context': {'error': str(e)}})
            return None
    
    def _on_generation_started(self, prediction_id: str):
        """Handle generation started."""
        logger.info(f"Generation started: {prediction_id}")
        if self.view:
            self.view.show_status("Generation started...")
    
    def _on_generation_completed(self, prediction_id: str, outputs: list):
        """Handle generation completed signal."""
        try:
            products = []
            
            for output in outputs:
                product = self._save_output_and_create_product(output, prediction_id)
                if product:
                    products.append(product)
            
            if self.view:
                # Pass products to generation form
                if hasattr(self.view, 'generation_form'):
                    self.view.generation_form._on_generation_completed(prediction_id, products)
                    
                self.view.show_status(f"Generation completed ({len(products)} products created)")
            
        except Exception as e:
            logger.error("Failed to handle generation completion", extra={'context': {'error': str(e)}})
            if self.view:
                self.view.show_error("Generation Error", str(e))
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failed signal."""
        logger.error("Generation failed", extra={'context': {'error': error}})
        if self.view:
            self.view.show_error("Generation Failed", error)