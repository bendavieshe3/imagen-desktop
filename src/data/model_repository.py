"""Repository for Replicate model caching."""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import and_, or_, cast, JSON
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast

from .base_repository import BaseRepository
from .schema import Model
from ..utils.debug_logger import logger

class ModelRepository(BaseRepository):
    """Repository for caching Replicate model information."""
    
    def add_or_update_model(self,
                           identifier: str,
                           name: str,
                           owner: str,
                           description: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Optional[Model]:
        """Add or update a model in the cache."""
        try:
            with self._get_session() as session:
                model = session.query(Model).get(identifier)
                if model:
                    model.name = name
                    model.owner = owner
                    model.description = description
                    model.model_metadata = metadata or {}
                    model.last_updated = datetime.utcnow()
                else:
                    model = Model(
                        identifier=identifier,
                        name=name,
                        owner=owner,
                        description=description,
                        model_metadata=metadata or {},
                        last_updated=datetime.utcnow()
                    )
                    session.add(model)
                session.commit()
                session.refresh(model)
                return model
        except Exception as e:
            logger.error(f"Error adding/updating model: {e}")
            return None
    
    def get_model(self, identifier: str) -> Optional[Model]:
        """Get a model by its identifier."""
        try:
            with self._get_session() as session:
                return session.query(Model).get(identifier)
        except Exception as e:
            logger.error(f"Error getting model {identifier}: {e}")
            return None
    
    def list_models(self, 
                    collection: Optional[str] = None,
                    owner: Optional[str] = None,
                    search: Optional[str] = None) -> List[Model]:
        """
        List cached models with optional filters.
        
        Args:
            collection: Filter by collection name
            owner: Filter by model owner
            search: Search term for name/description
        """
        try:
            with self._get_session() as session:
                query = session.query(Model)
                
                filters = []
                if collection:
                    # Use SQLite's json_extract function to access the collection field
                    filters.append(
                        func.json_extract(
                            cast(Model.model_metadata, JSON),
                            '$.collection'
                        ) == collection
                    )
                if owner:
                    filters.append(Model.owner == owner)
                if search:
                    search_term = f"%{search}%"
                    filters.append(or_(
                        Model.name.ilike(search_term),
                        Model.description.ilike(search_term)
                    ))
                
                if filters:
                    query = query.filter(and_(*filters))
                
                return query.order_by(Model.last_updated.desc()).all()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def cleanup_old_models(self, days: int = 30) -> int:
        """Remove models not updated within specified days."""
        try:
            with self._get_session() as session:
                cutoff = datetime.utcnow() - timedelta(days=days)
                deleted = session.query(Model)\
                    .filter(Model.last_updated < cutoff)\
                    .delete()
                session.commit()
                return deleted
        except Exception as e:
            logger.error(f"Error cleaning up old models: {e}")
            return 0
    
    def count_models(self) -> int:
        """Get total count of cached models."""
        try:
            with self._get_session() as session:
                return session.query(func.count(Model.identifier)).scalar() or 0
        except Exception as e:
            logger.error(f"Error counting models: {e}")
            return 0