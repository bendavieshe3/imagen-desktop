"""Adapter between domain events and Qt signals."""
from PyQt6.QtCore import QObject, pyqtSignal
import traceback

from imagen_desktop.core.events.base import BaseEvent
from imagen_desktop.core.events.order_events import OrderEventType, OrderEventPublisher, OrderEvent
from imagen_desktop.core.events.generation_events import GenerationEventType, GenerationEventPublisher, GenerationEvent
from imagen_desktop.core.events.product_events import ProductEventType, ProductEventPublisher, ProductEvent
from imagen_desktop.utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class EventAdapter(QObject):
    """Adapter that converts domain events to Qt signals for UI components."""
    
    # Order signals
    order_created = pyqtSignal(object)  # Order object
    order_updated = pyqtSignal(object)  # Order object
    order_status_changed = pyqtSignal(int, str)  # order_id, status
    order_fulfilled = pyqtSignal(object)  # Order object
    order_failed = pyqtSignal(object, str)  # Order object, error
    order_canceled = pyqtSignal(object)  # Order object
    
    # Generation signals
    generation_started = pyqtSignal(str)  # prediction_id (string)
    generation_processing = pyqtSignal(object)  # Generation object
    generation_completed = pyqtSignal(str, list)  # prediction_id, products
    generation_failed = pyqtSignal(str, str)  # prediction_id, error_message
    generation_canceled = pyqtSignal(str)  # prediction_id
    
    # Product signals
    product_created = pyqtSignal(object)  # Product object
    product_updated = pyqtSignal(object)  # Product object
    product_deleted = pyqtSignal(object)  # Product object
    product_selected = pyqtSignal(object)  # Product object
    
    # Error signal
    error_occurred = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to domain events."""
        # Each handler only subscribes to its own event types
        # Order events
        for event_type in OrderEventType:
            OrderEventPublisher.subscribe(event_type, self._handle_order_event)
        
        # Generation events
        for event_type in GenerationEventType:
            GenerationEventPublisher.subscribe(event_type, self._handle_generation_event)
        
        # Product events
        for event_type in ProductEventType:
            ProductEventPublisher.subscribe(event_type, self._handle_product_event)
        
        logger.debug("EventAdapter subscribed to domain events")
    
    def _handle_order_event(self, event: BaseEvent):
        """Handle order events and emit corresponding Qt signals."""
        try:
            # Validate this is an order event
            if not isinstance(event, OrderEvent):
                logger.warning(f"Non-order event received in _handle_order_event: {type(event)}")
                return
                
            # Process based on event type
            if event.event_type == OrderEventType.CREATED:
                self.order_created.emit(event.data.order)
                logger.debug(f"Order created event emitted for order {event.entity_id}")
            
            elif event.event_type == OrderEventType.UPDATED:
                self.order_updated.emit(event.data.order)
                logger.debug(f"Order updated event emitted for order {event.entity_id}")
            
            elif event.event_type == OrderEventType.STATUS_CHANGED:
                self.order_status_changed.emit(event.entity_id, event.data.order.status.value)
                logger.debug(f"Order status changed event emitted for order {event.entity_id}")
            
            elif event.event_type == OrderEventType.FULFILLED:
                self.order_fulfilled.emit(event.data.order)
                logger.debug(f"Order fulfilled event emitted for order {event.entity_id}")
            
            elif event.event_type == OrderEventType.FAILED:
                error_msg = event.data.error or "Unknown error"
                self.order_failed.emit(event.data.order, error_msg)
                self.error_occurred.emit("Order Failed", error_msg)
                logger.debug(f"Order failed event emitted for order {event.entity_id}")
            
            elif event.event_type == OrderEventType.CANCELED:
                self.order_canceled.emit(event.data.order)
                logger.debug(f"Order canceled event emitted for order {event.entity_id}")
                
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Error handling order event: {e}\n{stack_trace}")
            self.error_occurred.emit("Event Error", f"Error processing order event: {str(e)}")
    
    def _handle_generation_event(self, event: BaseEvent):
        """Handle generation events and emit corresponding Qt signals."""
        try:
            # Validate this is a generation event
            if not isinstance(event, GenerationEvent):
                logger.warning(f"Non-generation event received in _handle_generation_event: {type(event)}")
                return
                
            # Process based on event type
            if event.event_type == GenerationEventType.STARTED:
                # Emit the prediction_id to match what the UI components expect
                self.generation_started.emit(event.data.generation.id)
                logger.debug(f"Generation started event emitted for generation {event.entity_id}")
            
            elif event.event_type == GenerationEventType.PROCESSING:
                self.generation_processing.emit(event.data.generation)
                logger.debug(f"Generation processing event emitted for generation {event.entity_id}")
            
            elif event.event_type == GenerationEventType.COMPLETED:
                # Emit the prediction_id and products list to match what the UI components expect
                self.generation_completed.emit(event.data.generation.id, event.data.products or [])
                logger.debug(f"Generation completed event emitted for generation {event.entity_id}")
            
            elif event.event_type == GenerationEventType.FAILED:
                # Emit the prediction_id and error message to match what the UI components expect
                error_msg = event.data.error or "Unknown error during generation"
                self.generation_failed.emit(event.data.generation.id, error_msg)
                self.error_occurred.emit("Generation Failed", error_msg)
                logger.debug(f"Generation failed event emitted for generation {event.entity_id}")
            
            elif event.event_type == GenerationEventType.CANCELED:
                # Emit the prediction_id to match what the UI components expect
                self.generation_canceled.emit(event.data.generation.id)
                logger.debug(f"Generation canceled event emitted for generation {event.entity_id}")
                
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Error handling generation event: {e}\n{stack_trace}")
            self.error_occurred.emit("Event Error", f"Error processing generation event: {str(e)}")
    
    def _handle_product_event(self, event: BaseEvent):
        """Handle product events and emit corresponding Qt signals."""
        try:
            # Validate this is a product event
            if not isinstance(event, ProductEvent):
                logger.warning(f"Non-product event received in _handle_product_event: {type(event)}")
                return
                
            # Process based on event type
            if event.event_type == ProductEventType.CREATED:
                self.product_created.emit(event.data.product)
                logger.debug(f"Product created event emitted for product {event.entity_id}")
            
            elif event.event_type == ProductEventType.UPDATED:
                self.product_updated.emit(event.data.product)
                logger.debug(f"Product updated event emitted for product {event.entity_id}")
            
            elif event.event_type == ProductEventType.DELETED:
                self.product_deleted.emit(event.data.product)
                logger.debug(f"Product deleted event emitted for product {event.entity_id}")
            
            elif event.event_type == ProductEventType.SELECTED:
                self.product_selected.emit(event.data.product)
                logger.debug(f"Product selected event emitted for product {event.entity_id}")
                
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Error handling product event: {e}\n{stack_trace}")
            self.error_occurred.emit("Event Error", f"Error processing product event: {str(e)}")
    
    def cleanup(self):
        """Clean up event subscriptions when adapter is destroyed."""
        # Order events
        for event_type in OrderEventType:
            OrderEventPublisher.unsubscribe(event_type, self._handle_order_event)
        
        # Generation events    
        for event_type in GenerationEventType:
            GenerationEventPublisher.unsubscribe(event_type, self._handle_generation_event)
        
        # Product events    
        for event_type in ProductEventType:
            ProductEventPublisher.unsubscribe(event_type, self._handle_product_event)
            
        logger.debug("EventAdapter unsubscribed from domain events")