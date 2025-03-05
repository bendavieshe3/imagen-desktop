"""Main window presenter coordinating other presenters."""
from typing import Optional, Any, List, Dict
from pathlib import Path
import requests

# Update imports to use the correct paths
from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.api.api_handler import APIHandler
from imagen_desktop.data.database import Database
from imagen_desktop.data.repositories.order_repository import OrderRepository
from imagen_desktop.data.repositories.generation_repository import GenerationRepository
from imagen_desktop.data.repositories.model_repository import ModelRepository
from imagen_desktop.data.repositories.model_query_repository import ModelQueryRepository
from imagen_desktop.data.repositories.product_repository import ProductRepository
from imagen_desktop.ui.event_adapter import EventAdapter
from imagen_desktop.ui.presenters.generation_presenter import GenerationPresenter
from imagen_desktop.utils.debug_logger import logger

class MainWindowPresenter:
    """Coordinates functionality between different presenters."""
    
    def __init__(self, 
                 database: Optional[Database] = None,
                 view = None):
        """Initialize the presenter with optional database support."""
        self.view = view
        self.database = database
        
        # Initialize repositories
        self.order_repository = None
        self.generation_repository = None
        self.model_repository = None
        self.model_query_repository = None
        self.product_repository = None
        
        if database:
            self._init_repositories()
        
        # Initialize event adapter
        self.event_adapter = EventAdapter()
        
        # Initialize components
        self._init_components()
        self._connect_signals()
    
    def _init_repositories(self):
        """Initialize repositories with database."""
        try:
            self.order_repository = OrderRepository(self.database)
            self.generation_repository = GenerationRepository(self.database)
            self.model_repository = ModelRepository(self.database)
            self.model_query_repository = ModelQueryRepository(self.database)
            self.product_repository = ProductRepository(self.database)
            logger.info("Database repositories initialized")
        except Exception as e:
            logger.error(f"Failed to initialize repositories: {e}")
            raise
    
    def _init_components(self):
        """Initialize core components."""
        logger.debug("Initializing MainWindow components")
        
        # Initialize API handler
        self.api_handler = APIHandler(
            order_repository=self.order_repository,
            generation_repository=self.generation_repository,
            product_repository=self.product_repository
        )
        
        # Initialize feature presenters
        self.generation_presenter = GenerationPresenter(
            api_handler=self.api_handler,
            product_repository=self.product_repository,
            view=self.view
        )
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Connect event adapter signals to view components
        if self.view and hasattr(self.view, 'generation_form'):
            logger.debug("Connecting generation form signals")
            
            # Connect generation events from the event adapter to UI components
            self.event_adapter.generation_started.connect(
                self.view.generation_form._on_generation_started
            )
            
            self.event_adapter.generation_completed.connect(
                self.view.generation_form._on_generation_completed
            )
            
            self.event_adapter.generation_failed.connect(
                self.view.generation_form._on_generation_failed
            )
            
            self.event_adapter.generation_canceled.connect(
                self.view.generation_form._on_generation_canceled
            )
    
    def start_generation(self, model: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Start a new generation for the given model and parameters.
        
        Args:
            model: Model identifier
            params: Generation parameters with prompt included
            
        Returns:
            Prediction ID if successful, None otherwise
        """
        try:
            # Extract prompt from params for readability 
            prompt = params.get("prompt", "")
            if not prompt:
                logger.warning("Empty prompt provided for generation")
                
            # Log the generation request
            logger.info(
                "Starting generation",
                extra={
                    'context': {
                        'model': model,
                        'prompt': prompt
                    }
                }
            )
            
            # Create an order instead of directly starting a generation
            order, prediction_id = self.api_handler.create_order(
                model=model,
                prompt=prompt,
                parameters=params
            )
            
            if order and prediction_id:
                if self.view:
                    self.view.show_status(f"Started generation for order {order.id}")
                return prediction_id
            else:
                error_msg = "Failed to create order or start generation"
                logger.error(error_msg)
                if self.view:
                    self.view.show_error("Generation Error", error_msg)
                return None
                
        except Exception as e:
            logger.error(f"Failed to start generation: {e}")
            if self.view:
                self.view.show_error("Generation Error", str(e))
            return None
    
    def _save_output_and_create_product(self, output: Any, prediction_id: str) -> Optional[Product]:
        """
        Save generation output to file and create product record.
        
        Args:
            output: Raw output from generation
            prediction_id: ID of the generation
            
        Returns:
            Created Product or None if creation failed
        """
        try:
            if not self.product_repository:
                logger.warning("Product repository not available")
                return None
                
            # Save output to file
            output_dir = Path.home() / '.imagen-desktop' / 'products'
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
            
            # Get image dimensions
            width = None
            height = None
            format_name = None
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    width, height = img.size
                    format_name = img.format.lower() if img.format else None
            except Exception as e:
                logger.warning(f"Failed to get image dimensions: {e}")
            
            # Create product record
            product = self.product_repository.create_product(
                file_path=file_path,
                generation_id=prediction_id,
                width=width,
                height=height,
                format=format_name,
                product_type=ProductType.IMAGE
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            return None