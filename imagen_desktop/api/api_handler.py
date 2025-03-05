"""Main API handler coordinating all API-related operations."""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import traceback
from PyQt6.QtCore import QObject

from .client import ReplicateClient
from .prediction_manager import PredictionManager
from ..core.models.generation import Generation, GenerationStatus
from ..core.models.order import Order, OrderStatus
from ..core.models.product import Product, ProductType
from ..core.events.order_events import OrderEvent, OrderEventType, OrderEventPublisher
from ..core.events.generation_events import GenerationEvent, GenerationEventType, GenerationEventPublisher
from ..core.events.product_events import ProductEvent, ProductEventType, ProductEventPublisher
from ..data.repositories.order_repository import OrderRepository
from ..data.repositories.generation_repository import GenerationRepository
from ..data.repositories.product_repository import ProductRepository
from ..utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class APIHandler(QObject):
    """Coordinates API operations and manages state."""
    
    def __init__(self, 
                order_repository: Optional[OrderRepository] = None,
                generation_repository: Optional[GenerationRepository] = None,
                product_repository: Optional[ProductRepository] = None):
        super().__init__()
        
        # Set repositories
        self.order_repository = order_repository
        self.generation_repository = generation_repository
        self.product_repository = product_repository
        
        self._init_components()
        self._connect_signals()
        self._active_predictions = set()
    
    def _init_components(self):
        """Initialize API components."""
        self.client = ReplicateClient()
        self.prediction_manager = PredictionManager(self.client)
    
    def _connect_signals(self):
        """Connect internal signals."""
        logger.debug("Connecting APIHandler signals")
        self.prediction_manager.generation_completed.connect(self._handle_generation_completed)
        self.prediction_manager.generation_failed.connect(self._handle_generation_failed)
        self.prediction_manager.generation_canceled.connect(self._handle_generation_canceled)
    
    def create_order(self, 
                    model: str, 
                    prompt: str,
                    parameters: Dict[str, Any],
                    project_id: Optional[int] = None) -> Tuple[Optional[Order], str]:
        """
        Create a new order and start the first generation.
        
        Args:
            model: Model identifier
            prompt: Text prompt
            parameters: Generation parameters
            project_id: Optional project ID
            
        Returns:
            Tuple of (Order, prediction_id) or (None, error_message)
        """
        try:
            # Validate repositories
            if not all([self.order_repository, self.generation_repository]):
                logger.error("Missing required repositories")
                return None, "Database repositories not available"
            
            # Create order
            order = self.order_repository.create_order(
                model=model,
                prompt=prompt,
                base_parameters=parameters,
                project_id=project_id,
                status=OrderStatus.PENDING.value
            )
            
            if not order:
                return None, "Failed to create order record"
            
            logger.info(f"Created order {order.id}")
            
            try:
                # Publish order created event
                order_event = OrderEvent(
                    event_type=OrderEventType.CREATED,
                    order=order
                )
                OrderEventPublisher.publish_order_event(order_event)
            except Exception as e:
                stack_trace = traceback.format_exc()
                logger.error(f"Error publishing order event: {e}\n{stack_trace}")
            
            # Start generation (using same parameters as order)
            prediction_id = self.prediction_manager.start_prediction(model, parameters)
            
            # Create generation record
            generation = self.generation_repository.create_generation(
                prediction_id=prediction_id,
                order_id=order.id,
                model=model,
                prompt=prompt,
                parameters=parameters,
                status=GenerationStatus.STARTING
            )
            
            if not generation:
                logger.error(f"Failed to create generation record for order {order.id}")
            else:
                try:
                    # Publish generation started event
                    generation_event = GenerationEvent(
                        event_type=GenerationEventType.STARTED,
                        generation=generation
                    )
                    GenerationEventPublisher.publish_generation_event(generation_event)
                except Exception as e:
                    stack_trace = traceback.format_exc()
                    logger.error(f"Error publishing generation event: {e}\n{stack_trace}")
            
            # Update order status
            self.order_repository.update_order_status(
                order_id=order.id,
                status=OrderStatus.PROCESSING
            )
            
            try:
                # Publish order status changed event
                order_status_event = OrderEvent(
                    event_type=OrderEventType.STATUS_CHANGED,
                    order=order
                )
                OrderEventPublisher.publish_order_event(order_status_event)
            except Exception as e:
                stack_trace = traceback.format_exc()
                logger.error(f"Error publishing order status event: {e}\n{stack_trace}")
            
            # Track active prediction
            self._active_predictions.add(prediction_id)
            
            logger.info(
                f"Created order {order.id} with generation {prediction_id}",
                extra={'context': {'model': model}}
            )
            
            return order, prediction_id
            
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Failed to create order: {e}\n{stack_trace}")
            return None, str(e)
    
    def notify_generation_started(self, prediction_id: str):
        """Notify listeners that generation has started."""
        if prediction_id in self._active_predictions:
            logger.debug(f"Notifying generation started: {prediction_id}")
            
            if self.generation_repository:
                generation = self.generation_repository.get_generation(prediction_id)
                if generation:
                    try:
                        generation_event = GenerationEvent(
                            event_type=GenerationEventType.STARTED,
                            generation=generation
                        )
                        GenerationEventPublisher.publish_generation_event(generation_event)
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        logger.error(f"Error publishing generation started event: {e}\n{stack_trace}")
    
    def _handle_generation_completed(self, prediction_id: str, raw_outputs: list):
        """Handle completed generation and emit products."""
        if prediction_id not in self._active_predictions:
            logger.warning(f"Received completion for unknown generation: {prediction_id}")
            return

        logger.info(
            "Generation completed successfully",
            extra={
                'context': {
                    'prediction_id': prediction_id,
                    'output_count': len(raw_outputs)
                }
            }
        )
        
        # Get generation details
        generation = None
        if self.generation_repository:
            generation = self.generation_repository.get_generation(prediction_id)
        
        # Process outputs into products
        products = []
        if self.product_repository:
            for output in raw_outputs:
                product = self._create_product_from_output(output, prediction_id)
                if product:
                    products.append(product)
        
        # Update generation status
        if generation and self.generation_repository:
            self.generation_repository.update_generation_status(
                prediction_id=prediction_id,
                status=GenerationStatus.COMPLETED
            )
            
            try:
                # Publish generation completed event
                generation_event = GenerationEvent(
                    event_type=GenerationEventType.COMPLETED,
                    generation=generation,
                    products=products
                )
                GenerationEventPublisher.publish_generation_event(generation_event)
            except Exception as e:
                stack_trace = traceback.format_exc()
                logger.error(f"Error publishing generation completed event: {e}\n{stack_trace}")
            
            # If we have order information, update order too
            if self.order_repository and generation and generation.order_id:
                # Check if all generations for this order are complete
                generations = self.generation_repository.list_generations_by_order(
                    order_id=generation.order_id
                )
                
                all_complete = all(
                    g.status in (GenerationStatus.COMPLETED, GenerationStatus.FAILED)
                    for g in generations
                )
                
                if all_complete:
                    # Get updated order
                    order = self.order_repository.get_order(generation.order_id)
                    if order:
                        self.order_repository.update_order_status(
                            order_id=generation.order_id,
                            status=OrderStatus.FULFILLED
                        )
                        
                        try:
                            # Publish order fulfilled event
                            order_event = OrderEvent(
                                event_type=OrderEventType.FULFILLED,
                                order=order
                            )
                            OrderEventPublisher.publish_order_event(order_event)
                        except Exception as e:
                            stack_trace = traceback.format_exc()
                            logger.error(f"Error publishing order fulfilled event: {e}\n{stack_trace}")
        
        self._active_predictions.remove(prediction_id)
    
    def _create_product_from_output(self, output: Any, generation_id: str) -> Optional[Product]:
        """
        Create a product from generation output.
        
        Args:
            output: Raw output from generation
            generation_id: ID of the generation that produced this output
            
        Returns:
            Product or None if creation failed
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
                import requests
                response = requests.get(output.url)
                response.raise_for_status()
                data = response.content
            else:
                # Assume string URL
                import requests
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
                generation_id=generation_id,
                width=width,
                height=height,
                format=format_name,
                product_type=ProductType.IMAGE
            )
            
            # Note: ProductEventPublisher is already called inside the repository's create_product method
            
            return product
            
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Failed to create product: {e}\n{stack_trace}")
            return None
    
    def _handle_generation_failed(self, prediction_id: str, error: str):
        """Handle generation failure."""
        if prediction_id in self._active_predictions:
            logger.error(
                "Generation failed",
                extra={
                    'context': {
                        'prediction_id': prediction_id,
                        'error': error
                    }
                }
            )
            
            # Update generation status
            if self.generation_repository:
                generation = self.generation_repository.get_generation(prediction_id)
                
                if generation:
                    self.generation_repository.update_generation_status(
                        prediction_id=prediction_id,
                        status=GenerationStatus.FAILED,
                        error=error
                    )
                    
                    try:
                        # Publish generation failed event
                        generation_event = GenerationEvent(
                            event_type=GenerationEventType.FAILED,
                            generation=generation,
                            error=error
                        )
                        GenerationEventPublisher.publish_generation_event(generation_event)
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        logger.error(f"Error publishing generation failed event: {e}\n{stack_trace}")
                    
                    # If we have order information, update order too
                    if self.order_repository and generation.order_id:
                        # Get updated order
                        order = self.order_repository.get_order(generation.order_id)
                        if order:
                            self.order_repository.update_order_status(
                                order_id=generation.order_id,
                                status=OrderStatus.FAILED
                            )
                            
                            try:
                                # Publish order failed event
                                order_event = OrderEvent(
                                    event_type=OrderEventType.FAILED,
                                    order=order,
                                    error=error
                                )
                                OrderEventPublisher.publish_order_event(order_event)
                            except Exception as e:
                                stack_trace = traceback.format_exc()
                                logger.error(f"Error publishing order failed event: {e}\n{stack_trace}")
            
            self._active_predictions.remove(prediction_id)
    
    def _handle_generation_canceled(self, prediction_id: str):
        """Handle generation cancellation."""
        if prediction_id in self._active_predictions:
            logger.info(f"Generation canceled: {prediction_id}")
            
            # Update generation status
            if self.generation_repository:
                generation = self.generation_repository.get_generation(prediction_id)
                
                if generation:
                    self.generation_repository.update_generation_status(
                        prediction_id=prediction_id,
                        status=GenerationStatus.CANCELLED
                    )
                    
                    try:
                        # Publish generation canceled event
                        generation_event = GenerationEvent(
                            event_type=GenerationEventType.CANCELED,
                            generation=generation
                        )
                        GenerationEventPublisher.publish_generation_event(generation_event)
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        logger.error(f"Error publishing generation canceled event: {e}\n{stack_trace}")
                    
                    # If we have order information, update order too
                    if self.order_repository and generation.order_id:
                        # Get updated order
                        order = self.order_repository.get_order(generation.order_id)
                        if order:
                            self.order_repository.update_order_status(
                                order_id=generation.order_id,
                                status=OrderStatus.CANCELED
                            )
                            
                            try:
                                # Publish order canceled event
                                order_event = OrderEvent(
                                    event_type=OrderEventType.CANCELED,
                                    order=order
                                )
                                OrderEventPublisher.publish_order_event(order_event)
                            except Exception as e:
                                stack_trace = traceback.format_exc()
                                logger.error(f"Error publishing order canceled event: {e}\n{stack_trace}")
            
            self._active_predictions.remove(prediction_id)
    
    def cancel_generation(self, prediction_id: str):
        """Cancel an ongoing generation."""
        try:
            if prediction_id in self._active_predictions:
                self.prediction_manager.cancel_prediction(prediction_id)
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Failed to cancel generation {prediction_id}: {e}\n{stack_trace}")