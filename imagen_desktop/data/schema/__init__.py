"""SQLAlchemy models for database schema."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON

# Create base class for declarative models
Base = declarative_base()

# Import all models to ensure they're registered with the Base metadata
from imagen_desktop.data.schema.models import (
    Order, Generation, Product, Project, Model, Tag, Collection,
    CollectionProduct, GenerationTag, ProductTag
)

__all__ = [
    'Base',
    'Order',
    'Generation',
    'Product',
    'Project',
    'Model',
    'Tag',
    'Collection',
    'CollectionProduct',
    'GenerationTag',
    'ProductTag'
]