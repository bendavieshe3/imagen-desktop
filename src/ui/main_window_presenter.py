"""Main window presenter coordinating other presenters."""
from typing import Optional, Any, List
from pathlib import Path
import requests
from sqlalchemy.orm import sessionmaker
from PIL import Image

from ..models.image_generation import ImageGenerationModel
from ..api.api_handler import APIHandler
from ..data.image_repository import ImageRepository
from ..data.repositories.model_repository import ModelRepository
from ..data.repositories.model_query_repository import ModelQueryRepository
from ..data.product_repository import ProductRepository
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
    
    def _save_output_to_file(self, output: Any) -> Optional[Path]:
        """Save generation output to file."""
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
            
            return file_path
            
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
            saved_paths = []
            
            for output in outputs:
                file_path = self._save_output_to_file(output)
                if file_path:
                    saved_paths.append(file_path)
                    
                    # Create product if repository available
                    if self.product_repository:
                        try:
                            with Image.open(file_path) as img:
                                width, height = img.size
                                format = img.format.lower() if img.format else None
                                
                            self.product_repository.create_product(
                                file_path=file_path,
                                generation_id=prediction_id,
                                width=width,
                                height=height,
                                format=format,
                                product_type="image"
                            )
                        except Exception as e:
                            logger.error(f"Failed to create product record: {e}")
            
            if self.view:
                # Update thumbnail strip with each image
                for path in saved_paths:
                    self.view.generation_form.thumbnail_strip.add_image(path)
                
                # Display the latest image in the output display
                if saved_paths:
                    self.view.generation_form.output_display.display_image(saved_paths[-1])
                    
                self.view.show_status(f"Generation completed ({len(saved_paths)} images created)")
            
        except Exception as e:
            logger.error("Failed to handle generation completion", extra={'context': {'error': str(e)}})
            if self.view:
                self.view.show_error("Generation Error", str(e))
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failed signal."""
        logger.error("Generation failed", extra={'context': {'error': error}})
        if self.view:
            self.view.show_error("Generation Failed", error)