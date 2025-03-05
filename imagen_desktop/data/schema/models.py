"""SQLAlchemy models for database schema."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON

# Import base class
from imagen_desktop.data.schema import Base

class Order(Base):
    """Model for image generation orders."""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    model = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    base_parameters = Column(JSON, nullable=False)
    status = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="orders")
    generations = relationship("Generation", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order id={self.id}, status={self.status}>"

class Generation(Base):
    """Model for image generation records."""
    __tablename__ = 'generations'
    
    id = Column(String, primary_key=True)  # prediction_id
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    model = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)
    return_parameters = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False)
    error = Column(Text)
    
    # Relationships
    order = relationship("Order", back_populates="generations")
    products = relationship("Product", back_populates="generation", cascade="all, delete-orphan")
    tags = relationship("GenerationTag", back_populates="generation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Generation id={self.id}, status={self.status}>"

class Product(Base):
    """Model for individual generated outputs."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(String, ForeignKey('generations.id'))
    file_path = Column(String, nullable=False)
    product_type = Column(String, nullable=False)  # image, video, etc.
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String)
    file_size = Column(Integer)
    product_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    
    # Relationships
    generation = relationship("Generation", back_populates="products")
    collections = relationship("CollectionProduct", back_populates="product", cascade="all, delete-orphan")
    tags = relationship("ProductTag", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product id={self.id}, type={self.product_type}>"

class Project(Base):
    """Model for organizing orders."""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="project")
    
    def __repr__(self):
        return f"<Project id={self.id}, name={self.name}>"

class Model(Base):
    """Model for caching available Replicate models."""
    __tablename__ = 'models'
    
    identifier = Column(String, primary_key=True)  # owner/name
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    description = Column(Text)
    model_metadata = Column(JSON, nullable=False, default=dict)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Model identifier={self.identifier}>"

class Tag(Base):
    """Model for tags."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    generations = relationship("GenerationTag", back_populates="tag")
    products = relationship("ProductTag", back_populates="tag")
    
    def __repr__(self):
        return f"<Tag id={self.id}, name={self.name}>"

class Collection(Base):
    """Model for user-created collections."""
    __tablename__ = 'collections'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    products = relationship("CollectionProduct", back_populates="collection")
    
    def __repr__(self):
        return f"<Collection id={self.id}, name={self.name}>"

class CollectionProduct(Base):
    """Association table for collections and products."""
    __tablename__ = 'collection_products'
    
    collection_id = Column(Integer, ForeignKey('collections.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    collection = relationship("Collection", back_populates="products")
    product = relationship("Product", back_populates="collections")
    
    def __repr__(self):
        return f"<CollectionProduct collection_id={self.collection_id}, product_id={self.product_id}>"

class GenerationTag(Base):
    """Association table for generations and tags."""
    __tablename__ = 'generation_tags'
    
    generation_id = Column(String, ForeignKey('generations.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    
    # Relationships
    generation = relationship("Generation", back_populates="tags")
    tag = relationship("Tag", back_populates="generations")
    
    def __repr__(self):
        return f"<GenerationTag generation_id={self.generation_id}, tag_id={self.tag_id}>"

class ProductTag(Base):
    """Association table for products and tags."""
    __tablename__ = 'product_tags'
    
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    
    # Relationships
    product = relationship("Product", back_populates="tags")
    tag = relationship("Tag", back_populates="products")
    
    def __repr__(self):
        return f"<ProductTag product_id={self.product_id}, tag_id={self.tag_id}>"