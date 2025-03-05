"""Product-related events and event handling."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from imagen_desktop.core.events.base import BaseEvent, EventPublisher
from imagen_desktop.core.models.product import Product
from imagen_desktop.utils.debug_logger import logger

class ProductEventType(str, Enum):
    """Types of product events."""
    CREATED = "product.created"
    UPDATED = "product.updated"
    DELETED = "product.deleted"
    SELECTED = "product.selected"
    ERROR = "product.error"

@dataclass
class ProductEventData:
    """Data for product events."""
    product: Product
    error: Optional[str] = None

class ProductEvent(BaseEvent[ProductEventData]):
    """Event representing a product operation."""
    
    def __init__(self, event_type: ProductEventType, product: Product, error: Optional[str] = None):
        super().__init__(
            event_type=event_type,
            entity_id=product.id,
            entity_type="product",
            data=ProductEventData(product=product, error=error)
        )

class ProductEventPublisher:
    """Publisher for product events."""
    
    @classmethod
    def publish_product_event(cls, event: ProductEvent):
        """Publish a product event."""
        try:
            logger.debug(
                "Publishing product event",
                extra={
                    'context': {
                        'event_type': event.event_type,
                        'product_id': event.entity_id
                    }
                }
            )
            EventPublisher.publish(event)
        except Exception as e:
            logger.error(f"Error publishing product event: {e}", exc_info=True)
    
    @classmethod
    def subscribe_to_products(cls, callback):
        """Subscribe to all product events."""
        for event_type in ProductEventType:
            cls.subscribe(event_type, callback)
    
    @classmethod
    def subscribe(cls, event_type: ProductEventType, callback):
        """Subscribe to a specific product event type."""
        EventPublisher.subscribe(event_type, callback)
    
    @classmethod
    def unsubscribe_from_products(cls, callback):
        """Unsubscribe from all product events."""
        for event_type in ProductEventType:
            cls.unsubscribe(event_type, callback)
            
    @classmethod
    def unsubscribe(cls, event_type: ProductEventType, callback):
        """Unsubscribe from a specific product event type."""
        EventPublisher.unsubscribe(event_type, callback)