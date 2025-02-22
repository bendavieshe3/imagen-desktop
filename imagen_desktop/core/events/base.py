"""Base event system implementation."""
from typing import Callable, Set, TypeVar, Generic, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
            return
            
        logger.debug(
            "Publishing event",
            extra={
                'context': {
                    'event_type': event_type,
                    'entity_id': event.entity_id,
                    'entity_type': event.entity_type,
                    'subscriber_count': len(cls._subscribers[event_type])
                }
            }
        )
        
        for subscriber in cls._subscribers[event_type]:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(
                    "Error in event subscriber",
                    extra={
                        'context': {
                            'subscriber': subscriber.__qualname__,
                            'error': str(e)
                        }
                    }
                )

    @classmethod
    def clear_subscribers(cls, event_type: str):
        """Clear all subscribers for an event type."""
        if event_type in cls._subscribers:
            cls._subscribers[event_type].clear()
            logger.debug(f"Cleared all subscribers for {event_type}")