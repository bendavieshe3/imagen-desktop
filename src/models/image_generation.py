from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
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
        logger.info("Initializing ImageGenerationModel")
        self.history_dir = Path.home() / '.replicate-desktop' / 'history'
        self.history_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"History directory: {self.history_dir}")
        self._load_history()
    
    def _load_history(self):
        """Load generation history from disk."""
        self.history: Dict[str, GenerationMetadata] = {}
        
        logger.info("Loading generation history")
        for metadata_file in self.history_dir.glob('*.json'):
            try:
                logger.debug(f"Loading metadata from {metadata_file}")
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
            except Exception as e:
                logger.error(f"Error loading metadata file {metadata_file}: {e}")
                continue
        
        logger.info(f"Loaded {len(self.history)} history entries")
    
    def add_generation(self, 
                      prediction_id: str,
                      model: str,
                      prompt: str,
                      parameters: Dict[str, Any],
                      output_paths: List[Path]) -> GenerationMetadata:
        """
        Add a new generation to history.
        
        Returns:
            GenerationMetadata: The newly created generation metadata
        """
        logger.info(f"Adding generation {prediction_id}")
        logger.debug(f"Model: {model}")
        logger.debug(f"Output paths: {output_paths}")
        
        try:
            # Ensure the history directory exists
            self.history_dir.mkdir(parents=True, exist_ok=True)
            
            metadata = GenerationMetadata(
                id=prediction_id,
                model=model,
                prompt=prompt,
                parameters=parameters,
                timestamp=datetime.now(),
                output_paths=output_paths,
                status=GenerationStatus.STARTING if not output_paths else GenerationStatus.COMPLETED
            )
            
            # Update in-memory history
            self.history[prediction_id] = metadata
            
            # Force save to disk
            self._save_metadata(metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error adding generation: {e}", exc_info=True)
            raise
    
    def _save_metadata(self, metadata: GenerationMetadata):
        """Save generation metadata to disk."""
        try:
            logger.info(f"Saving metadata for {metadata.id}")
            
            # Ensure directory exists
            self.history_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_path = self.history_dir / f"{metadata.id}.json"
            logger.debug(f"Metadata path: {metadata_path}")
            
            # Convert paths to strings and ensure they exist
            output_paths = []
            for path in metadata.output_paths:
                if isinstance(path, Path) and path.exists():
                    output_paths.append(str(path))
                elif isinstance(path, str):
                    if Path(path).exists():
                        output_paths.append(path)
            
            data = {
                'id': metadata.id,
                'model': metadata.model,
                'prompt': metadata.prompt,
                'parameters': metadata.parameters,
                'timestamp': metadata.timestamp.isoformat(),
                'output_paths': output_paths,
                'status': metadata.status.value if isinstance(metadata.status, GenerationStatus) else str(metadata.status),
                'error': metadata.error
            }
            
            logger.debug(f"Writing metadata: {json.dumps(data, indent=2)}")
            
            with open(metadata_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Successfully saved metadata to {metadata_path}")
            
        except Exception as e:
            logger.error(f"Error saving metadata: {e}", exc_info=True)
            logger.debug(f"Current directory: {os.getcwd()}")
            logger.debug(f"History directory exists: {self.history_dir.exists()}")
            logger.debug(f"History directory is writable: {os.access(self.history_dir, os.W_OK)}")
            raise
    
    def update_generation_status(self, prediction_id: str, status: str, error: Optional[str] = None):
        """Update the status of a generation."""
        logger.info(f"Updating status for {prediction_id} to {status}")
        if prediction_id in self.history:
            metadata = self.history[prediction_id]
            metadata.status = GenerationStatus(status)
            metadata.error = error
            self._save_metadata(metadata)
            logger.info(f"Updated status for {prediction_id}")
        else:
            logger.warning(f"Attempted to update status for unknown generation: {prediction_id}")

    def get_generation(self, prediction_id: str) -> Optional[GenerationMetadata]:
        """Get metadata for a specific generation."""
        return self.history.get(prediction_id)
    
    def list_generations(self, 
                        limit: Optional[int] = None,
                        status: Optional[str] = None) -> List[GenerationMetadata]:
        """List generations, optionally filtered by status."""
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
            max_age_days (int): Maximum age in days to keep
            
        Returns:
            int: Number of entries removed
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
                    logger.error(f"Error removing old history entry {id}: {e}")
        
        return removed

    def handle_failed_generation(self, prediction_id: str, error: str) -> None:
        """
        Handle a failed generation by updating status and cleaning up.
        
        Args:
            prediction_id (str): ID of the failed generation
            error (str): Error message
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