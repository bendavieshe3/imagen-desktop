"""Repository for Replicate model caching."""
from typing import Optional, List
from datetime import datetime

from .base_repository import BaseRepository
from .schema import Model
from ..utils.debug_logger import logger

class ModelRepository(BaseRepository):
    """Repository for caching Replicate model information."""
    
    def add_or_update_model(self,
                           identifier: str,
                           name: str,
                           owner: str,
                           description: Optional[str] = None) -> Optional[Model]:
        """Add or update a model in the cache."""
        try:
            with self._get_session() as session:
                model = session.query(Model).get(identifier)
                if model:
                    model.name = name
                    model.owner = owner
                    model.description = description
                    model.last_updated = datetime.utcnow()
                else:
                    model = Model(
                        identifier=identifier,
                        name=name,
                        owner=owner,
                        description=description
                    )
                    session.add(model)
                session.commit()
                return model
        except Exception as e:
            logger.error(f"Error adding/updating model: {e}")
            return None
    
    def get_model(self, identifier: str) -> Optional[Model]:
        """Get a model by its identifier."""
        return self.get_by_id(Model, identifier)
    
    def list_models(self, collection: Optional[str] = None) -> List[Model]:
        """List all cached models, optionally filtered by collection."""
        try:
            with self._get_session() as session:
                query = session.query(Model)
                if collection:
                    # Add collection filtering logic here when implemented
                    pass
                return query.all()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def cleanup_old_models(self, days: int = 30) -> int:
        """Remove models not updated within specified days."""
        try:
            with self._get_session() as session:
                cutoff = datetime.utcnow() - datetime.timedelta(days=days)
                deleted = session.query(Model)\
                    .filter(Model.last_updated < cutoff)\
                    .delete()
                session.commit()
                return deleted
        except Exception as e:
            logger.error(f"Error cleaning up old models: {e}")
            return 0