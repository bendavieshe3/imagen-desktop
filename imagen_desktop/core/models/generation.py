"""Generation domain model."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class GenerationStatus(str, Enum):
    """Status values for a generation."""
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Generation:
    """
    Domain model for an image generation.
    
    Args:
        id: Unique identifier for the generation (usually prediction_id)
        order_id: ID of the parent order
        model: Name of the model used
        prompt: Generation prompt
        parameters: Generation-specific parameters
        timestamp: Generation time
        status: Current generation status
        return_parameters: Parameters returned by the API
        error: Error message if failed
    """
    id: str
    order_id: int
    model: str
    prompt: str
    parameters: Dict[str, Any]
    timestamp: datetime
    status: GenerationStatus
    return_parameters: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Generation':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            order_id=db_model.order_id,
            model=db_model.model,
            prompt=db_model.prompt,
            parameters=db_model.parameters,
            timestamp=db_model.timestamp,
            status=GenerationStatus(db_model.status),
            return_parameters=db_model.return_parameters,
            error=db_model.error
        )