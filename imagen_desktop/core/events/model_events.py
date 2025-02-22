"""Model-related events and event handling."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

from imagen_desktop.core.events.base import BaseEvent, EventPublisher
from imagen_desktop.utils.debug_logger import logger

class ModelEventType(str, Enum):
    """Types of model events."""
    ADDED = "added"
    REMOVED = "removed"
    UPDATED = "updated"
    LIST_CHANGED = "list_changed"
    ERROR = "error"

@dataclass
class ModelEventData:
    """Data for model events."""
    model_id: str
    model_data: Dict[str, Any]
    error: Optional[str] = None

class ModelEvent(BaseEvent[ModelEventData]):
    """Event representing a model operation."""
    
    def __init__(self, event_type: ModelEventType, model_id: str, 
                 model_data: Dict[str, Any], error: Optional[str] = None):
        super().__init__(
            event_type=event_type,
            entity_id=model_id,
            entity_type="model",
            data=ModelEventData(
                model_id=model_id,
                model_data=model_data,
                error=error
            )
        )

class ModelEventPublisher:
    """Publisher for model events."""
    
    @classmethod
    def publish_model_event(cls, event: ModelEvent):
        """Publish a model event."""
        logger.debug(
            "Publishing model event",
            extra={
                'context': {
                    'event_type': event.event_type,
                    'model_id': event.entity_id
                }
            }
        )
        EventPublisher.publish(event)
    
    @classmethod
    def subscribe_to_models(cls, callback):
        """Subscribe to all model events."""
        for event_type in ModelEventType:
            EventPublisher.subscribe(event_type, callback)
    
    @classmethod
    def unsubscribe_from_models(cls, callback):
        """Unsubscribe from all model events."""
        for event_type in ModelEventType:
            EventPublisher.unsubscribe(event_type, callback)