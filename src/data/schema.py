"""SQLAlchemy models and database initialization."""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Generation(Base):
    """Model for image generation records."""
    __tablename__ = 'generations'
    
    id = Column(String, primary_key=True)  # prediction_id
    model = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False)
    error = Column(Text)
    
    # Relationships
    images = relationship("Image", back_populates="generation", cascade="all, delete-orphan")
    tags = relationship("GenerationTag", back_populates="generation", cascade="all, delete-orphan")

class Image(Base):
    """Model for generated images."""
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(String, ForeignKey('generations.id'), nullable=False)
    file_path = Column(String, nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    generation = relationship("Generation", back_populates="images")

class Model(Base):
    """Model for caching available Replicate models."""
    __tablename__ = 'models'
    
    identifier = Column(String, primary_key=True)  # owner/name
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    description = Column(Text)
    model_metadata = Column(JSON, nullable=False, default=dict)  # renamed from metadata
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

class Tag(Base):
    """Model for image tags."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    generations = relationship("GenerationTag", back_populates="tag")

class GenerationTag(Base):
    """Association table for generations and tags."""
    __tablename__ = 'generation_tags'
    
    generation_id = Column(String, ForeignKey('generations.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    
    # Relationships
    generation = relationship("Generation", back_populates="tags")
    tag = relationship("Tag", back_populates="generations")

def init_db(db_path: Path) -> sessionmaker:
    """Initialize the database and return a session factory."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)