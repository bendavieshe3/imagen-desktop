"""Core order model."""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

class OrderStatus(str, Enum):
    """Status values for an order."""
    PENDING = "pending"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class Order:
    """Domain model for an image generation order."""
    id: int
    model: str
    prompt: str
    base_parameters: Dict[str, Any]
    status: OrderStatus
    created_at: datetime
    project_id: Optional[int] = None
    
    @classmethod
    def from_db_model(cls, db_model, include_generations: bool = False) -> 'Order':
        """Create domain model from database model."""
        order = cls(
            id=db_model.id,
            model=db_model.model,
            prompt=db_model.prompt,
            base_parameters=db_model.base_parameters,
            status=OrderStatus(db_model.status),
            created_at=db_model.created_at,
            project_id=db_model.project_id
        )
        
        return order
    
    def is_active(self) -> bool:
        """Check if the order is still active (not completed or failed)."""
        return self.status in (OrderStatus.PENDING, OrderStatus.PROCESSING)
    
    def can_be_canceled(self) -> bool:
        """Check if the order can be canceled."""
        return self.is_active()