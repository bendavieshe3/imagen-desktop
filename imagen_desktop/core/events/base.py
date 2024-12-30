"""Base event system implementation."""
from typing import Callable, Set, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from imagen_desktop.utils.debug_logger import logger

T = TypeVar('T')

@dataclass
class BaseEvent(Generic[T]):
    """Base class for all events."""
    event_type: str
    entity_id: any
    entity_type: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EventPublisher:
    """Base publisher for domain events."""
    
    _instances = {}  # One instance per event type
    _subscribers: Set[Callable] = set()
    
    def __new__(cls, event_type: str):
        """Create or return publisher for event type."""
        if event_type not in cls._instances:
            cls._instances[event_type] = super().__new__(cls)
            cls._instances[event_type]._subscribers = set()
            cls._instances[event_type]._event_type = event_type
        return cls._instances[event_type]
    
    @classmethod
    def subscribe(cls, event_type: str, callback: Callable[[BaseEvent], None]):
        """Subscribe to events of a specific type."""
        instance = cls(event_type)
        instance._subscribers.add(callback)
        logger.debug(
            f"Added event subscriber",
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
        if event_type in cls._instances:
            cls._instances[event_type]._subscribers.discard(callback)
            logger.debug(
                f"Removed event subscriber",
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
        instance = cls(event.event_type)
        
        logger.debug(
            f"Publishing event",
            extra={
                'context': {
                    'event_type': event.event_type,
                    'entity_id': event.entity_id,
                    'entity_type': event.entity_type
                }
            }
        )
        
        for subscriber in instance._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(
                    f"Error in event subscriber",
                    extra={
                        'context': {
                            'subscriber': subscriber.__qualname__,
                            'error': str(e)
                        }
                    }
                )