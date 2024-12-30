"""Base repository implementation for SQLAlchemy."""
from typing import TypeVar, Type, Optional, List
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from ...utils.debug_logger import logger

T = TypeVar('T')

class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def _get_session(self) -> Session:
        """Get a new session from the factory."""
        return self.session_factory()
    
    def add(self, model: T) -> Optional[T]:
        """Add a new model instance to the database."""
        try:
            with self._get_session() as session:
                session.add(model)
                session.commit()
                session.refresh(model)
                return model
        except SQLAlchemyError as e:
            logger.error(f"Error adding model: {str(e)}")
            return None
    
    def get_by_id(self, model_class: Type[T], id_value: any) -> Optional[T]:
        """Get a model instance by its ID."""
        try:
            with self._get_session() as session:
                return session.query(model_class).get(id_value)
        except SQLAlchemyError as e:
            logger.error(f"Error getting model by ID: {str(e)}")
            return None
    
    def update(self, model: T) -> bool:
        """Update an existing model instance."""
        try:
            with self._get_session() as session:
                session.merge(model)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating model: {str(e)}")
            return False
    
    def delete(self, model: T) -> bool:
        """Delete a model instance."""
        try:
            with self._get_session() as session:
                session.delete(model)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting model: {str(e)}")
            return False
    
    def list_all(self, model_class: Type[T]) -> List[T]:
        """List all instances of a model."""
        try:
            with self._get_session() as session:
                return session.query(model_class).all()
        except SQLAlchemyError as e:
            logger.error(f"Error listing models: {str(e)}")
            return []