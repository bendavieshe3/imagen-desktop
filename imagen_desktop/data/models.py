"""Domain model representations for data transfer."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

@dataclass
class Generation:
    """Domain representation of a generation."""
    id: str
    model: str
    prompt: str
    parameters: Dict[str, Any]
    timestamp: datetime
    status: str
    order_id: int
    error: Optional[str] = None
    return_parameters: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Generation':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            model=db_model.model,
            prompt=db_model.prompt,
            parameters=db_model.parameters,
            timestamp=db_model.timestamp,
            status=db_model.status,
            order_id=db_model.order_id,
            error=db_model.error,
            return_parameters=db_model.return_parameters
        )

@dataclass
class Product:
    """Domain representation of a product."""
    id: int
    file_path: Path
    product_type: str
    generation_id: Optional[str]
    created_at: datetime
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    is_favorite: bool = False
    metadata: Dict[str, Any] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Product':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            file_path=Path(db_model.file_path),
            product_type=db_model.product_type,
            generation_id=db_model.generation_id,
            created_at=db_model.created_at,
            width=db_model.width,
            height=db_model.height,
            format=db_model.format,
            file_size=db_model.file_size,
            is_favorite=db_model.is_favorite,
            metadata=db_model.product_metadata or {}
        )

@dataclass
class Order:
    """Domain representation of an order."""
    id: int
    model: str
    prompt: str
    base_parameters: Dict[str, Any]
    status: str
    created_at: datetime
    project_id: Optional[int] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Order':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            model=db_model.model,
            prompt=db_model.prompt,
            base_parameters=db_model.base_parameters,
            status=db_model.status,
            created_at=db_model.created_at,
            project_id=db_model.project_id
        )

@dataclass
class Model:
    """Domain representation of a model."""
    identifier: str
    name: str
    owner: str
    description: Optional[str]
    last_updated: datetime
    metadata: Dict[str, Any] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Model':
        """Create domain model from database model."""
        return cls(
            identifier=db_model.identifier,
            name=db_model.name,
            owner=db_model.owner,
            description=db_model.description,
            last_updated=db_model.last_updated,
            metadata=db_model.model_metadata or {}
        )

@dataclass
class Tag:
    """Domain representation of a tag."""
    id: int
    name: str
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Tag':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            name=db_model.name
        )

@dataclass
class Project:
    """Domain representation of a project."""
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Project':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description,
            status=db_model.status,
            created_at=db_model.created_at
        )

@dataclass
class Collection:
    """Domain representation of a collection."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    @classmethod
    def from_db_model(cls, db_model) -> 'Collection':
        """Create domain model from database model."""
        return cls(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description,
            created_at=db_model.created_at
        )