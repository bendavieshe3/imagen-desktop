"""Query operations for model repository."""
from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy import and_, or_, cast, JSON
from sqlalchemy.sql import func

from ..base_repository import BaseRepository
from ..schema import Model
from ...utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class ModelQueryRepository(BaseRepository):
    """Handles query operations for models."""
    
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
                
                logger.debug(
                    "Listing models with filters",
                    extra={
                        'context': {
                            'collection': collection,
                            'owner': owner,
                            'search': search
                        }
                    }
                )
                
                return query.order_by(Model.last_updated.desc()).all()
                
        except Exception as e:
            logger.error(
                "Failed to list models",
                extra={
                    'context': {
                        'error': str(e),
                        'collection': collection,
                        'owner': owner
                    }
                }
            )
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
                
                logger.info(
                    "Cleaned up old models",
                    extra={
                        'context': {
                            'days': days,
                            'deleted_count': deleted
                        }
                    }
                )
                return deleted
                
        except Exception as e:
            logger.error(
                "Failed to cleanup old models",
                extra={
                    'context': {
                        'days': days,
                        'error': str(e)
                    }
                }
            )
            return 0
    
    def count_models(self) -> int:
        """Get total count of cached models."""
        try:
            with self._get_session() as session:
                count = session.query(func.count(Model.identifier)).scalar() or 0
                logger.debug(
                    "Counted models",
                    extra={'context': {'count': count}}
                )
                return count
        except Exception as e:
            logger.error(
                "Failed to count models",
                extra={'context': {'error': str(e)}}
            )
            return 0