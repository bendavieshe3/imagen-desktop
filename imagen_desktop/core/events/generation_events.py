"""Generation-related events and event handling."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List

from imagen_desktop.core.events.base import BaseEvent, EventPublisher
from imagen_desktop.core.models.generation import Generation
from imagen_desktop.core.models.product import Product
from imagen_desktop.utils.debug_logger import logger

class GenerationEventType(str, Enum):
    """Types of generation events."""
    STARTED = "generation.started"
    PROCESSING = "generation.processing"
    COMPLETED = "generation.completed"
    FAILED = "generation.failed"
    CANCELED = "generation.canceled"
    ERROR = "generation.error"

@dataclass
class GenerationEventData:
    """Data for generation events."""
    generation: Generation
    products: Optional[List[Product]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GenerationEvent(BaseEvent[GenerationEventData]):
    """Event representing a generation operation."""
    
    def __init__(self, 
                event_type: GenerationEventType, 
                generation: Generation, 
                products: Optional[List[Product]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                error: Optional[str] = None):
        super().__init__(
            event_type=event_type,
            entity_id=generation.id,
            entity_type="generation",
            data=GenerationEventData(
                generation=generation,
                products=products,
                metadata=metadata,
                error=error
            )
        )

class GenerationEventPublisher:
    """Publisher for generation events."""
    
    @classmethod
    def publish_generation_event(cls, event: GenerationEvent):
        """Publish a generation event."""
        try:
            logger.debug(
                "Publishing generation event",
                extra={
                    'context': {
                        'event_type': event.event_type,
                        'generation_id': event.entity_id
                    }
                }
            )
            EventPublisher.publish(event)
        except Exception as e:
            logger.error(f"Error publishing generation event: {e}", exc_info=True)
    
    @classmethod
    def subscribe_to_generations(cls, callback):
        """Subscribe to all generation events."""
        for event_type in GenerationEventType:
            cls.subscribe(event_type, callback)
    
    @classmethod
    def subscribe(cls, event_type: GenerationEventType, callback):
        """Subscribe to a specific generation event type."""
        EventPublisher.subscribe(event_type, callback)
    
    @classmethod
    def unsubscribe_from_generations(cls, callback):
        """Unsubscribe from all generation events."""
        for event_type in GenerationEventType:
            cls.unsubscribe(event_type, callback)
            
    @classmethod
    def unsubscribe(cls, event_type: GenerationEventType, callback):
        """Unsubscribe from a specific generation event type."""
        EventPublisher.unsubscribe(event_type, callback)