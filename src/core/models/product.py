"""Core product model and enums."""
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class ProductType(str, Enum):
    """Types of products that can be generated."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

@dataclass
class Product:
    """Domain model for a generated product."""
    id: int
    file_path: Path
    product_type: ProductType
    generation_id: Optional[str]
    created_at: datetime
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Product':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            file_path=Path(db_model.file_path),
            product_type=ProductType(db_model.product_type),
            generation_id=db_model.generation_id,
            created_at=db_model.created_at,
            width=db_model.width,
            height=db_model.height,
            format=db_model.format,
            file_size=db_model.file_size,
            metadata=db_model.product_metadata or {}
        )