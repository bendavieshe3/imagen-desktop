"""Presenter logic for the main application window."""
from pathlib import Path
from typing import Optional, Set, List
from sqlalchemy.orm import sessionmaker
from PIL import Image

from ..models.image_generation import ImageGenerationModel, GenerationStatus
from ..api.api_handler import APIHandler
from ..data.image_repository import ImageRepository
from ..data.repositories.model_repository import ModelRepository
from ..data.repositories.model_query_repository import ModelQueryRepository
from ..data.product_repository import ProductRepository
from ..utils.debug_logger import logger

class MainWindowPresenter:
    """Handles business logic for the main window."""
    
    def __init__(self, 
                 session_factory: Optional[sessionmaker] = None,
                 view = None):
        """Initialize the presenter with optional database support."""
        self.view = view
        self.active_generations: Set[str] = set()
        
        # Initialize components
        logger.debug("Initializing MainWindow components")
        
        # Initialize storage mechanisms
        self.image_model = ImageGenerationModel()
        self.api_handler = APIHandler(image_model=self.image_model)
        
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
        
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect API handler signals."""
        self.api_handler.generation_started.connect(self._on_generation_started)
        self.api_handler.generation_completed.connect(self._on_generation_completed)
        self.api_handler.generation_failed.connect(self._on_generation_failed)
    
    def start_generation(self, model: str, params: dict) -> str:
        """Start a new image generation."""
        try:
            # Get prediction ID
            prediction_id = self.api_handler.generate_images(model, params)
            logger.debug(f"Created prediction {prediction_id} with model {model}")
            
            # Create initial records
            self._create_generation_record(prediction_id, model, params)
            
            # Notify that generation has started
            self.api_handler.notify_generation_started(prediction_id)
            return prediction_id
            
        except Exception as e:
            logger.error(f"Failed to start generation: {e}")
            raise
    
    def _create_generation_record(self, prediction_id: str, model: str, params: dict):
        """Create initial generation record in storage systems."""
        logger.debug(f"Creating generation record for {prediction_id}")
        
        # Store in file-based system
        self.image_model.add_generation(
            prediction_id=prediction_id,
            model=model,
            prompt=params.get('prompt', ''),
            parameters=params,
            output_paths=[],
            initial_status=GenerationStatus.STARTING
        )
        
        # Store in database if available
        if self.image_repository:
            try:
                self.image_repository.add_generation(
                    prediction_id=prediction_id,
                    model=model,
                    prompt=params.get('prompt', ''),
                    parameters=params,
                    status=GenerationStatus.STARTING.value
                )
                logger.debug(f"Added generation {prediction_id} to database")
            except Exception as e:
                logger.error(f"Failed to add generation to database: {e}")
        
        # Track active generation
        self.active_generations.add(prediction_id)
    
    def _on_generation_started(self, prediction_id: str):
        """Handle generation started signal."""
        if prediction_id not in self.active_generations:
            logger.warning(f"Received start signal for unknown generation: {prediction_id}")
            return
            
        logger.debug(f"Generation started: {prediction_id}")
        self.view.show_status(f"Generation started: {prediction_id}")
        
        # Update storage systems
        self.image_model.update_generation_status(
            prediction_id, 
            GenerationStatus.IN_PROGRESS.value
        )
        
        if self.image_repository:
            try:
                self.image_repository.update_generation_status(
                    prediction_id, 
                    GenerationStatus.IN_PROGRESS.value
                )
            except Exception as e:
                logger.error(f"Failed to update generation status in database: {e}")
    
    def _create_product_record(self, generation_id: str, file_path: Path) -> bool:
        """Create a product record for a generated file."""
        try:
            # Get image metadata
            with Image.open(file_path) as img:
                width, height = img.size
                format = img.format.lower() if img.format else None
            
            # Create product record
            if self.product_repository:
                self.product_repository.create_product(
                    file_path=file_path,
                    generation_id=generation_id,
                    width=width,
                    height=height,
                    format=format,
                    product_type="image",
                    metadata={
                        "source": "generation",
                        "imported": False
                    }
                )
                logger.debug(f"Created product record for {file_path}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to create product record for {file_path}: {e}")
            return False
    
    def _on_generation_completed(self, prediction_id: str, output_files: list):
        """Handle generation completed signal."""
        if prediction_id not in self.active_generations:
            logger.warning(f"Received completion for unknown generation: {prediction_id}")
            return
            
        try:
            if output_files and isinstance(output_files[0], Path):
                saved_paths = output_files
            else:
                saved_paths = self.api_handler.save_generation_output(prediction_id, output_files)
            
            # Update legacy storage
            self.image_model.update_generation(
                prediction_id=prediction_id,
                output_paths=saved_paths,
                status=GenerationStatus.COMPLETED
            )
            
            # Create product records
            products_created = False
            if self.product_repository:
                for path in saved_paths:
                    if self._create_product_record(prediction_id, path):
                        products_created = True
                    
                if products_created:
                    logger.info(f"Created product records for generation {prediction_id}")
            
            # Update view status only, don't switch tabs
            self.view.show_status(f"Generation completed: {prediction_id}")
            logger.debug(f"Generation {prediction_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to handle completed generation: {e}")
            self.view.show_error("Generation Error", 
                               f"Generation completed but failed to save outputs: {str(e)}")
        finally:
            self.active_generations.remove(prediction_id)
    
    def _on_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failed signal."""
        if prediction_id not in self.active_generations:
            logger.warning(f"Received failure for unknown generation: {prediction_id}")
            return
            
        logger.error(f"Generation {prediction_id} failed: {error}")
        
        # Update storage
        self.image_model.update_generation_status(
            prediction_id, 
            GenerationStatus.FAILED.value,
            error
        )
        
        if self.image_repository:
            try:
                self.image_repository.update_generation_status(
                    prediction_id, "failed", error
                )
            except Exception as e:
                logger.error(f"Failed to update generation status in database: {e}")
        
        # Update view
        self.view.show_status(f"Generation failed: {error}")
        self.active_generations.remove(prediction_id)