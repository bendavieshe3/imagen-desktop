"""Repository for Replicate model caching."""
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.sql import func

from .base_repository import BaseRepository
from ..schema import Model
from ...utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

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
                    logger.debug(
                        "Updating existing model", 
                        extra={'context': {'identifier': identifier}}
                    )
                    model.name = name
                    model.owner = owner
                    model.description = description
                    model.model_metadata = metadata or {}
                    model.last_updated = datetime.utcnow()
                else:
                    logger.debug(
                        "Creating new model", 
                        extra={'context': {'identifier': identifier}}
                    )
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
            logger.error(
                "Failed to add/update model",
                extra={
                    'context': {
                        'identifier': identifier,
                        'error': str(e)
                    }
                }
            )
            return None
    
    def get_model(self, identifier: str) -> Optional[Model]:
        """Get a model by its identifier."""
        try:
            with self._get_session() as session:
                model = session.query(Model).get(identifier)
                if model:
                    logger.debug(
                        "Retrieved model",
                        extra={'context': {'identifier': identifier}}
                    )
                return model
        except Exception as e:
            logger.error(
                "Failed to get model",
                extra={
                    'context': {
                        'identifier': identifier,
                        'error': str(e)
                    }
                }
            )
            return None
    
    def delete_by_identifier(self, identifier: str) -> bool:
        """Delete a model by its identifier."""
        try:
            with self._get_session() as session:
                model = session.query(Model).filter(
                    Model.identifier == identifier
                ).first()
                if model:
                    session.delete(model)
                    session.commit()
                    logger.info(
                        "Deleted model",
                        extra={'context': {'identifier': identifier}}
                    )
                    return True
                return False
        except Exception as e:
            logger.error(
                "Failed to delete model",
                extra={
                    'context': {
                        'identifier': identifier,
                        'error': str(e)
                    }
                }
            )
            return False
            
    def list_models(self) -> List[Model]:
        """List all models (For backward compatibility)."""
        try:
            with self._get_session() as session:
                models = session.query(Model).order_by(Model.last_updated.desc()).all()
                logger.debug(
                    "Listed all models",
                    extra={'context': {'count': len(models)}}
                )
                return models
        except Exception as e:
            logger.error(
                "Failed to list models",
                extra={'context': {'error': str(e)}}
            )
            return []