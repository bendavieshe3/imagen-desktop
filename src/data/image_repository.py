"""Repository for image generation related models."""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from .base_repository import BaseRepository
from .schema import Generation, Image, Model, Tag, GenerationTag
from ..models.image_generation import GenerationStatus
from ..utils.debug_logger import logger

class ImageRepository(BaseRepository):
    """Repository for handling image generation data."""
    
    def add_generation(self, 
                      prediction_id: str,
                      model: str,
                      prompt: str,
                      parameters: Dict[str, Any],
                      status: str = GenerationStatus.STARTING.value,
                      error: Optional[str] = None) -> Optional[Generation]:
        """Add a new generation record."""
        generation = Generation(
            id=prediction_id,
            model=model,
            prompt=prompt,
            parameters=parameters,
            status=status,
            error=error
        )
        return self.add(generation)
    
    def get_generation(self, prediction_id: str) -> Optional[Generation]:
        """Get a generation by ID with related images."""
        try:
            with self._get_session() as session:
                return session.query(Generation)\
                    .options(joinedload(Generation.images))\
                    .filter(Generation.id == prediction_id)\
                    .first()
        except Exception as e:
            logger.error(f"Error getting generation {prediction_id}: {e}")
            return None
    
    def update_generation_status(self, 
                               prediction_id: str,
                               status: str,
                               error: Optional[str] = None) -> bool:
        """Update the status of a generation."""
        try:
            with self._get_session() as session:
                generation = session.query(Generation)\
                    .filter(Generation.id == prediction_id)\
                    .first()
                if generation:
                    generation.status = status
                    generation.error = error
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating generation status: {e}")
            return False
    
    def add_image(self,
                 generation_id: str,
                 file_path: Path,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 format: Optional[str] = None) -> Optional[Image]:
        """Add a new generated image."""
        try:
            file_size = file_path.stat().st_size if file_path.exists() else None
            image = Image(
                generation_id=generation_id,
                file_path=str(file_path),
                width=width,
                height=height,
                format=format,
                file_size=file_size
            )
            return self.add(image)
        except Exception as e:
            logger.error(f"Error adding image: {e}")
            return None
    
    def list_generations(self,
                        limit: Optional[int] = None,
                        status: Optional[str] = None) -> List[Generation]:
        """List generations with optional filtering."""
        try:
            with self._get_session() as session:
                query = session.query(Generation)\
                    .options(joinedload(Generation.images))
                
                if status:
                    query = query.filter(Generation.status == status)
                
                query = query.order_by(desc(Generation.timestamp))
                
                if limit:
                    query = query.limit(limit)
                
                return query.all()
        except Exception as e:
            logger.error(f"Error listing generations: {e}")
            return []