"""Manages image generation state and history."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import os
from ..utils.debug_logger import logger
from enum import Enum

class GenerationStatus(Enum):
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class GenerationMetadata:
    """
    Metadata for an image generation.
    
    Args:
        id (str): Unique identifier for the generation
        model (str): Name of the model used
        prompt (str): Generation prompt
        parameters (Dict[str, Any]): Model-specific parameters
        timestamp (datetime): Generation time
        output_paths (List[Path]): Paths to generated images
        status (GenerationStatus): Current generation status
        error (Optional[str]): Error message if failed
    """
    id: str
    model: str
    prompt: str
    parameters: Dict[str, Any]
    timestamp: datetime
    output_paths: List[Path]
    status: GenerationStatus
    error: Optional[str] = None

class ImageGenerationModel:
    """Manages image generation state and history."""
    
    def __init__(self):
        self.history_dir = Path.home() / '.replicate-desktop' / 'history'
        self.history_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized ImageGenerationModel at {self.history_dir}")
        self._load_history()
    
    def _load_history(self):
        """Load generation history from disk."""
        self.history: Dict[str, GenerationMetadata] = {}
        total_entries = 0
        
        try:
            for metadata_file in self.history_dir.glob('*.json'):
                try:
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)
                        metadata = GenerationMetadata(
                            id=data['id'],
                            model=data['model'],
                            prompt=data['prompt'],
                            parameters=data['parameters'],
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            output_paths=[Path(p) for p in data['output_paths']],
                            status=GenerationStatus(data['status']),
                            error=data.get('error')
                        )
                        self.history[metadata.id] = metadata
                        total_entries += 1
                except Exception as e:
                    logger.error(f"Failed to load metadata from {metadata_file}: {e}")
            
            logger.info(f"Loaded {total_entries} history entries successfully")
            
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            raise
    
    def add_generation(self, 
                      prediction_id: str,
                      model: str,
                      prompt: str,
                      parameters: Dict[str, Any],
                      output_paths: List[Path],
                      initial_status: GenerationStatus = GenerationStatus.STARTING) -> GenerationMetadata:
        """
        Add a new generation to history.
        
        Args:
            prediction_id: Unique identifier for the generation
            model: Model identifier used for generation
            prompt: Text prompt used
            parameters: Additional generation parameters
            output_paths: List of paths to generated images
            initial_status: Initial status for the generation
            
        Returns:
            GenerationMetadata: The newly created generation metadata
            
        Raises:
            ValueError: If required parameters are missing
            OSError: If unable to save metadata to disk
        """
        try:
            metadata = GenerationMetadata(
                id=prediction_id,
                model=model,
                prompt=prompt,
                parameters=parameters,
                timestamp=datetime.now(),
                output_paths=output_paths,
                status=initial_status
            )
            
            self.history[prediction_id] = metadata
            self._save_metadata(metadata)
            logger.debug(f"Added generation {prediction_id} with status {initial_status.value}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to add generation {prediction_id}: {e}")
            raise
    
    def update_generation(self,
                         prediction_id: str,
                         output_paths: List[Path],
                         status: GenerationStatus) -> None:
        """
        Update an existing generation with new paths and status.
        
        Args:
            prediction_id: ID of the generation to update
            output_paths: New output paths for the generation
            status: New status for the generation
        """
        if prediction_id in self.history:
            metadata = self.history[prediction_id]
            metadata.output_paths = output_paths
            metadata.status = status
            self._save_metadata(metadata)
            logger.debug(f"Updated generation {prediction_id} with {len(output_paths)} outputs")
        else:
            logger.warning(f"Attempted to update non-existent generation: {prediction_id}")
    
    def update_generation_status(self, prediction_id: str, status: str, error: Optional[str] = None):
        """Update the status of a generation."""
        if prediction_id in self.history:
            metadata = self.history[prediction_id]
            old_status = metadata.status
            metadata.status = GenerationStatus(status)
            metadata.error = error
            self._save_metadata(metadata)
            logger.debug(f"Updated status for {prediction_id}: {old_status.value} -> {status}")
        else:
            logger.warning(f"Attempted to update status for unknown generation: {prediction_id}")
    
    def _save_metadata(self, metadata: GenerationMetadata):
        """
        Save generation metadata to disk.
        
        Args:
            metadata: Generation metadata to save
            
        Raises:
            OSError: If unable to save metadata file
            ValueError: If metadata is invalid
        """
        try:
            metadata_path = self.history_dir / f"{metadata.id}.json"
            
            # Convert paths to strings and ensure they exist
            output_paths = []
            for path in metadata.output_paths:
                if isinstance(path, Path) and path.exists():
                    output_paths.append(str(path))
                elif isinstance(path, str) and Path(path).exists():
                    output_paths.append(path)
            
            data = {
                'id': metadata.id,
                'model': metadata.model,
                'prompt': metadata.prompt,
                'parameters': metadata.parameters,
                'timestamp': metadata.timestamp.isoformat(),
                'output_paths': output_paths,
                'status': metadata.status.value,
                'error': metadata.error
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metadata for {metadata.id}: {e}")
            raise
    
    def get_generation(self, prediction_id: str) -> Optional[GenerationMetadata]:
        """Get metadata for a specific generation."""
        return self.history.get(prediction_id)
    
    def list_generations(self, 
                        limit: Optional[int] = None,
                        status: Optional[str] = None) -> List[GenerationMetadata]:
        """
        List generations, optionally filtered by status.
        
        Args:
            limit: Maximum number of generations to return
            status: Filter by generation status
            
        Returns:
            List of GenerationMetadata objects
        """
        generations = list(self.history.values())
        
        if status:
            generations = [g for g in generations if g.status == status]
        
        generations.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            generations = generations[:limit]
        
        return generations
    
    def clean_history(self, max_age_days: int = 30) -> int:
        """
        Remove history entries older than specified days.
        
        Args:
            max_age_days: Maximum age in days to keep
            
        Returns:
            Number of entries removed
        """
        cutoff = datetime.now() - timedelta(days=max_age_days)
        removed = 0
        
        for id, metadata in list(self.history.items()):
            if metadata.timestamp < cutoff:
                try:
                    path = self.history_dir / f"{id}.json"
                    path.unlink(missing_ok=True)
                    del self.history[id]
                    removed += 1
                except Exception as e:
                    logger.error(f"Failed to remove old history entry {id}: {e}")
        
        if removed > 0:
            logger.info(f"Cleaned {removed} old history entries")
        return removed
    
    def handle_failed_generation(self, prediction_id: str, error: str) -> None:
        """
        Handle a failed generation by updating status and cleaning up.
        
        Args:
            prediction_id: ID of the failed generation
            error: Error message
        """
        if prediction_id in self.history:
            metadata = self.history[prediction_id]
            metadata.status = GenerationStatus.FAILED
            metadata.error = error
            
            # Clean up any partial output files
            for path in metadata.output_paths:
                try:
                    if path.exists():
                        path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to clean up output file {path}: {e}")
            
            metadata.output_paths = []
            self._save_metadata(metadata)
            logger.info(f"Handled failed generation {prediction_id}: {error}")