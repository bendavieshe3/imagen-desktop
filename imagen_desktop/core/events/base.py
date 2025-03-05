"""Base event system implementation."""
from typing import Callable, Set, TypeVar, Generic, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import traceback

from imagen_desktop.utils.debug_logger import logger

T = TypeVar('T')

@dataclass
class EventData:
    """Base class for event data."""
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class BaseEvent(Generic[T]):
    """Base class for all events."""
    event_type: str
    entity_id: Any
    entity_type: str
    timestamp: datetime = None
    data: Optional[T] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EventPublisher:
    """Base publisher for domain events."""
    
    _instances: Dict[str, 'EventPublisher'] = {}
    _subscribers: Dict[str, Set[Callable]] = {}
    
    def __new__(cls, event_type: str):
        """Create or return publisher for event type."""
        if event_type not in cls._instances:
            cls._instances[event_type] = super().__new__(cls)
            cls._subscribers[event_type] = set()
        return cls._instances[event_type]
    
    @classmethod
    def subscribe(cls, event_type: str, callback: Callable[[BaseEvent], None]):
        """Subscribe to events of a specific type."""
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = set()
        
        cls._subscribers[event_type].add(callback)
        logger.debug(
            "Added event subscriber",
            extra={
                'context': {
                    'event_type': event_type,
                    'subscriber': callback.__qualname__
                }
            }
        )
    
    @classmethod
    def unsubscribe(cls, event_type: str, callback: Callable[[BaseEvent], None]):
        """Unsubscribe from events of a specific type."""
        if event_type in cls._subscribers:
            cls._subscribers[event_type].discard(callback)
            logger.debug(
                "Removed event subscriber",
                extra={
                    'context': {
                        'event_type': event_type,
                        'subscriber': callback.__qualname__
                    }
                }
            )
    
    @classmethod
    def publish(cls, event: BaseEvent):
        """Publish an event to all subscribers."""
        event_type = event.event_type
        if event_type not in cls._subscribers:
            logger.debug(f"No subscribers for event type: {event_type}")
            return
            
        # Get the event class name for filtering
        event_class_name = event.__class__.__name__
        
        logger.debug(
            "Publishing event",
            extra={
                'context': {
                    'event_type': event_type,
                    'event_class': event_class_name,
                    'entity_id': event.entity_id,
                    'entity_type': event.entity_type,
                    'subscriber_count': len(cls._subscribers[event_type])
                }
            }
        )
        
        for subscriber in cls._subscribers[event_type]:
            try:
                # Get the handler name and expected event type
                handler_name = subscriber.__qualname__
                expected_event_type = None
                
                # Check if we're sending to the right type of handler
                if "_handle_order_event" in handler_name and "OrderEvent" not in event_class_name:
                    logger.warning(f"Skipping order handler for non-order event: {event_class_name}")
                    continue
                elif "_handle_generation_event" in handler_name and "GenerationEvent" not in event_class_name:
                    logger.warning(f"Skipping generation handler for non-generation event: {event_class_name}")
                    continue
                elif "_handle_product_event" in handler_name and "ProductEvent" not in event_class_name:
                    logger.warning(f"Skipping product handler for non-product event: {event_class_name}")
                    continue
                
                # Call the subscriber with the event
                subscriber(event)
            except Exception as e:
                stack_trace = traceback.format_exc()
                logger.error(
                    "Error in event subscriber",
                    extra={
                        'context': {
                            'subscriber': subscriber.__qualname__,
                            'error': str(e),
                            'stack_trace': stack_trace
                        }
                    }
                )

    @classmethod
    def clear_subscribers(cls, event_type: str):
        """Clear all subscribers for an event type."""
        if event_type in cls._subscribers:
            cls._subscribers[event_type].clear()
            logger.debug(f"Cleared all subscribers for {event_type}")