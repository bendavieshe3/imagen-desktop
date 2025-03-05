"""Order-related events and event handling."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

from imagen_desktop.core.events.base import BaseEvent, EventPublisher
from imagen_desktop.core.models.order import Order
from imagen_desktop.utils.debug_logger import logger

class OrderEventType(str, Enum):
    """Types of order events."""
    CREATED = "order.created"
    UPDATED = "order.updated"
    STATUS_CHANGED = "order.status_changed"
    FULFILLED = "order.fulfilled"
    FAILED = "order.failed"
    CANCELED = "order.canceled"
    ERROR = "order.error"

@dataclass
class OrderEventData:
    """Data for order events."""
    order: Order
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class OrderEvent(BaseEvent[OrderEventData]):
    """Event representing an order operation."""
    
    def __init__(self, 
                event_type: OrderEventType, 
                order: Order, 
                metadata: Optional[Dict[str, Any]] = None,
                error: Optional[str] = None):
        super().__init__(
            event_type=event_type,
            entity_id=order.id,
            entity_type="order",
            data=OrderEventData(
                order=order,
                metadata=metadata,
                error=error
            )
        )

class OrderEventPublisher:
    """Publisher for order events."""
    
    @classmethod
    def publish_order_event(cls, event: OrderEvent):
        """Publish an order event."""
        try:
            logger.debug(
                "Publishing order event",
                extra={
                    'context': {
                        'event_type': event.event_type,
                        'order_id': event.entity_id
                    }
                }
            )
            EventPublisher.publish(event)
        except Exception as e:
            logger.error(f"Error publishing order event: {e}", exc_info=True)
    
    @classmethod
    def subscribe_to_orders(cls, callback):
        """Subscribe to all order events."""
        for event_type in OrderEventType:
            cls.subscribe(event_type, callback)
    
    @classmethod
    def subscribe(cls, event_type: OrderEventType, callback):
        """Subscribe to a specific order event type."""
        EventPublisher.subscribe(event_type, callback)
    
    @classmethod
    def unsubscribe_from_orders(cls, callback):
        """Unsubscribe from all order events."""
        for event_type in OrderEventType:
            cls.unsubscribe(event_type, callback)
            
    @classmethod
    def unsubscribe(cls, event_type: OrderEventType, callback):
        """Unsubscribe from a specific order event type."""
        EventPublisher.unsubscribe(event_type, callback)