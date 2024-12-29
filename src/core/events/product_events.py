"""Event system for product-related changes."""
from typing import Callable, List, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from .base import BaseEvent, EventPublisher
from ..models.product import Product, ProductType
from utils.debug_logger import logger

class ProductEventType(str, Enum):
    """Types of product events."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

class ProductEvent(BaseEvent[Product]):
    """Event containing product change information."""
    
    def __init__(self, event_type: ProductEventType, product_id: int, product_type: ProductType):
        super().__init__(
            event_type=event_type,
            entity_id=product_id,
            entity_type="product"
        )
        self.product_type = product_type

class ProductEventPublisher(EventPublisher):
    """Publisher for product-specific events."""
    
    EVENT_TYPE = "product"
    
    @classmethod
    def subscribe_to_products(cls, callback: Callable[[ProductEvent], None]):
        """Subscribe to all product events."""
        cls.subscribe(cls.EVENT_TYPE, callback)
    
    @classmethod
    def unsubscribe_from_products(cls, callback: Callable[[ProductEvent], None]):
        """Unsubscribe from all product events."""
        cls.unsubscribe(cls.EVENT_TYPE, callback)
    
    @classmethod
    def publish_product_event(cls, event: ProductEvent):
        """Publish a product event."""
        cls.publish(event)